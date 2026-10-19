---
id: official-megatron-wiki/moe
title: Megatron MoE：路由、dispatcher、grouped GEMM与容量控制
engine: megatron
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-20'
coverage: reviewed training, parallel, state and backend implementation chains; not
  all models or runtime combinations
sources:
- source: nvidia-megatron-lm
  path: docs/user-guide/features/moe.md
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 004d1c2bc849bb6a96e77099872a1cb282907e28be774953c2ae40aa39b094c6
- source: nvidia-megatron-lm
  path: docs/user-guide/features/paged_stash.md
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 053fecb7a457408c19a5c44322c2dfd6a50a3d27e49786ddc6192b503c6d96a1
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/moe_layer.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: bfe309cdb8d30fbbde4a202a047f30e343c0b3e08c3f89e822ed15780f369a7c
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/token_dispatcher.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 7f3e33027136df240426614ee65a3c149d7a2c4361eda3b62cc6123af1bd9c6e
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/paged_stash.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 950b8c72253b90e8b6936a5aa8532120bd8e056f6cc88807efa4c818d88d4efc
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: ec8de7059bf8d6c78663384a489794d0712eaa1b81685ad0339e2c77cb9e32e3
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/virtual_expert_load_balancer.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: d4ea965c28c26e37386a76a1c1453386abef2e1dab8bbb4947594fc7be67dd91
- source: nvidia-megatron-lm
  path: tests/unit_tests/transformer/moe/test_virtual_experts.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 3a56ef29ac6b286ef881603b1d480e5fcf9a43eb7d47ed42368ac8f8e7bb4a8f
---

# Megatron MoE：路由、dispatcher、grouped GEMM与容量控制

## 从路由到梯度的工作负载

`MoELayer`连接router→permutation/preprocess→token_dispatch→expert GEMM/activation→combine→shared-expert与辅助loss。route top-k、expert数、capacity/padding、expert tensor/EP与真实每专家token分布共同决定shape；总tokens和hidden不能充分描述grouped GEMM。

layer forward仅是一半，dispatch/combine反向、wgrad/dgrad、auxloss scaling、recompute与optimizer都受布局/生命周期影响。先从实际layer spec和config确认MoE层频率、sharedexpert/激活/scale，再读dispatcher和expert backend，不以名字推断实现。

## Dispatcher 的范围与代价

| 实现 | 主要思路 | 调参/平台条件 |
| --- | --- | --- |
| allgather | 收集路由/激活后本地选择 | 通信/驻留代价随域增长；当前变长序列有实现约束 |
| alltoall | 按expert owner分发/合并 | split-size、token偏斜和permute/copy开销 |
| flex | 接入DeepEP/DeepEPv2/HybridEP/NCCL-EP等实际backend | 可选依赖、精度/通信API、capability和fork支持不同 |

当前`token_dispatcher.py`包含preprocess/dispatch/postprocess与combine对应阶段；仅开启flex不证明底层全部优化有效。保存实际provider、load路径、process-group和consumer调用，HCU已有DeepEP/UCCL等需按真实版本确认，NV backend并不自动迁移。

## 负载偏斜和计算效率分开

每层记录token/expert和token/rank直方图、padding/被drop量、dispatch/combine消息量、最慢rank与对齐窗口。rank算子都快但工作量偏斜时，先研究routing/capacity/框架分配；不要用改一个expert GEMM掩盖step由最重rank决定。

对groupedGEMM提每group的M/N/K、dtype、transpose、stride/leadingdim和scale，从实际rocBLAS/hipBLASLt log/bench命令形成tune请求；用户/HCU数学库团队处理hipBLASLt/grouped未支持的自动tune。孤立shape性能和模型内争用比较后才判断库实现是否需改。

## 两种 capacity 和 Paged Stash

`moe_expert_capacity_factor`限制每expert并支持相应padding/drop策略；`moe_expert_rank_capacity_factor`是rank级dispatch/grouped缓冲预留，两者不是同一个预算。当前rank capacity允许hybridep/ncclep，HybridEP需fuser或grouped-tensor；这比paged-stash教程的旧约束更广，以部署源码为准。

`moe_paged_stash`为saved routed-expert activation分配page，copy到设备stash、backward pop/reload，必要时hostspill；page/free-list/metadata、stream和saved tensor ownership一起决定正确性。spill/overflow或overbudget的rerun、page大小和buffer factors都要计代价，不把capacity预留当永久不会溢出的保证。

给更大headroom可减少rerun却占更多显存；更小page不一定降低time，可能增加metadata/launch。优化因素应由真实skew/peak与copy/pop profile决定，见[memory](memory.md)和[launch案例](../cases/paged-stash-launch.md)。

## MoonEP：把负载搬到虚拟专家的训练契约

当前 `moe_virtual_expert_load_balance` 通过 HybridEP 接入：规划 runtime expert IDs，向额外 slot 推送 FC1/FC2 权重，再将虚拟 slot 的梯度回并到真实 owner。TE 的额外 runtime GEMM slot 不注册为可初始化/保存的模型权重，checkpoint 只枚举 owned experts；slot 内容每微批可变，不能沿用 owned 权重的 first-microbatch 量化缓存标记。

该路径限制 flex+hybridep、indices routing、BF16 参数、grouped-tensor、FP32 router、已分配 main_grad 和固定 token 数；原生 MXFP8 还要求 param gather 与相应 grad-buffer 复用。EP/top-k/对齐及激活等检查以固定 TransformerConfig 为准。Paged Stash、delay-wgrad、跨微批 EP-overlap、shared-expert-overlap 等组合在当前检查中被拒绝，不能把各自可用能力直接叠加。

规划先在独立 stream 启动，shared expert 等独立计算可覆盖其时间；消费 dispatch 前等待 planning event。forward 结束保存本次 plan，backward 先重新推权重并 wait，FC2/FC1 梯度各启动一次回并，最后在计算 stream 等完成、清 slot 并交接真实梯度。重复 push、遗留 plan、token 数漂移或未完成两路规约都有显式失败；释放对称内存必须早于销毁其 EP group。

`plan_dispatch` 显式退出 Dynamo tracing，TE 图 scope 也有 whole-MoE 与 router/preprocess 的不同限制；compile 支持不等于全部规划过程 Graph-safe。上游虚拟专家测试覆盖路由/peer transport/训练对照，并区分 Blackwell MXFP8 与其他设备 skip。本轮只审阅源码和测试设计，没有运行这些多 GPU 测试。评估时分别测 planning、权重搬运、专家偏斜改善、梯度回并和额外峰值，再验证完整微批累积及阶段 loss；失败回退常规已验证 dispatcher。

## 融合与 1F1B overlap 的真实契约

核对NV实际granularity：permute/pad、scale/quantize、expertlinear/activation、combine/sharedexpert、残差与backward缓存。HCU优先已有TE/Flash-Train/PrimusTurbo实现，再按backend责任补HIP/Triton等；初版融合仍按高占比、同shape效率和上限继续优化。

EPoverlap改变微批与wgrad时序，当前config对fullrecompute、shared-expert-overlap、图scope、MTP与backend有组合限制，见[overlap](overlap.md)。不要把其他引擎的同名sharedexpert flag映射为同语义。

## 精度、失败与维护

局部校验覆盖outputs、dgrad/wgrad、auxloss、专家空token/不均shape、padding尾部、lowprecision scales、drop/overflow和重跑；阶段loss检查完整route→expert→optimizer状态。FP8缓存/GroupedTensor不是普通BF16tensor，stash/offload与shape推断须追特殊路径。

hang先定位哪层/哪阶段/哪rank及collective split顺序；OOM看received/routed padding、stash与workspace重叠；loss异常看routing semantics、scale、auxloss/gradient和实际fallback。保留baseline dispatcher/无候选融合配置，未验backend不作可用声明。

PR #7897与#7534为已登记机制入口；进一步搜索`wiki-search-pr "MoE grouped tensor paged stash" --engine megatron`读最终实现、目标branch及测试。open/development优化只记候选，官方已merge后仍确认当前HCU运行分支是否包含。

## 固定源码与维护边界

- [docs/user-guide/features/moe.md](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/docs/user-guide/features/moe.md)
- [docs/user-guide/features/paged_stash.md](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/docs/user-guide/features/paged_stash.md)
- [megatron/core/transformer/moe/moe_layer.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/core/transformer/moe/moe_layer.py)
- [megatron/core/transformer/moe/token_dispatcher.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/core/transformer/moe/token_dispatcher.py)
- [megatron/core/transformer/moe/paged_stash.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/core/transformer/moe/paged_stash.py)
- [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/core/transformer/transformer_config.py)

2026-10-20按上述固定源码/官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。