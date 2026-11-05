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
reviewed_on: '2026-11-04'
coverage: frozen source delta and consumer review; unchanged files rechecked; no HCU runtime validation
sources:
- source: nvidia-megatron-lm
  path: docs/user-guide/features/moe.md
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 004d1c2bc849bb6a96e77099872a1cb282907e28be774953c2ae40aa39b094c6
- source: nvidia-megatron-lm
  path: docs/user-guide/features/paged_stash.md
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: c290e8e9a72f9b0a0b864651dc28e692279d5389e547dbef5ea3f56f622a5a7d
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/moe_layer.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 3672b8c10b5758ec920eb44480220e5bbe4189108de059fea863259546c8d37c
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/token_dispatcher.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: ca4155cb32939839a14219cb14c38fa0abd0b28bdfe9546a383d5f3039c5608b
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/paged_stash.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: c120b2e7ce96baf76be69b5a3a7944a584c406fd4c093c56e71b5be6e0313e53
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 39f34cb0f9005ad53b4d318346a7b6bbb88931a19d5f868805a42e83dd1eece6
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/virtual_expert_load_balancer.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: d4ea965c28c26e37386a76a1c1453386abef2e1dab8bbb4947594fc7be67dd91
- source: nvidia-megatron-lm
  path: tests/unit_tests/transformer/moe/test_virtual_experts.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 3a56ef29ac6b286ef881603b1d480e5fcf9a43eb7d47ed42368ac8f8e7bb4a8f
- source: nvidia-megatron-lm
  path: megatron/core/extensions/transformer_engine.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: ab48dd0b062fa44b816205ae9e8491a8785e1c934d2b88cefb3ee0768b6df7b1
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/router.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 19222feee0fca608353117cca63ba9b51160d720bb3f58ede7f2a25843ce3f4f
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/training_matches_inference.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 3f3cec992fafc6f189f360af5679cbcbbdf303cf65169c23c8922dc8a3e3db7d
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/megakernel/factory.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: b57ba0c2d1ef7a57a6e9972d3b19ce5401093f16d4e5647ba7197eb2fac4e3ee
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/megakernel/mok/runtime.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 1e6b1b65f1203ddf40e5ea6f5135091903adb4385416fd217d5a5b244468607a
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/megakernel/mok/backend.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 63326a8898483e2b31a00b190004d7b8a470da350e4658e71282fadea3c541fd
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/megakernel/parameter_bridge.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: dacb759b3cca519cb5fb521ef048d7ed3a9d73a5020897272bffb465c691b01f
- source: nvidia-megatron-lm
  path: megatron/core/distributed/finalize_model_grads.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 6dac52af3f531447c4dfd96bca03b0607cb0fe509c5108890e90812c3bdf190a
retrieved_on: '2026-11-04'
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

当前 `ncclep` 的 packed THD bootstrap 不再盲用第一微批 tokens：优先以 max_seqlen_per_dp_cp_rank（按 SP/TP 切片）或 max_seq_length_per_sample（按 CP/TP 切片）形成同 rank 上界，再按64对齐；缺上界或输入超过边界报错。fixed-length/BSHD 仍依赖首次 shape，不保证后来更大的微批可用。padding mask 必须从 [b,s] 转成 sequence-first token 顺序，填充路由 ID=-1、weight=0；GroupedTensor zero-copy 旧 buffer 仅在量化 zero-copy 分支传入。alltoall combine_postprocess 清除 router probs，避免保留重算图。

## 负载偏斜和计算效率分开

每层记录token/expert和token/rank直方图、padding/被drop量、dispatch/combine消息量、最慢rank与对齐窗口。rank算子都快但工作量偏斜时，先研究routing/capacity/框架分配；不要用改一个expert GEMM掩盖step由最重rank决定。

对groupedGEMM提每group的M/N/K、dtype、transpose、stride/leadingdim和scale，从实际rocBLAS/hipBLASLt log/bench命令形成tune请求；用户/HCU数学库团队处理hipBLASLt/grouped未支持的自动tune。孤立shape性能和模型内争用比较后才判断库实现是否需改。

## 两种 capacity 和 Paged Stash

`moe_expert_capacity_factor`限制每expert并支持相应padding/drop策略；`moe_expert_rank_capacity_factor`是rank级dispatch/grouped缓冲预留，两者不是同一个预算。当前rank capacity允许hybridep/ncclep，HybridEP 需 fuser 或 GroupedTensor；当前教程已补后者的 TE 标记、fused activation 和无 interleaving 条件，backend/runner 仍以部署源码核对。

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

新增 MOK 路径在 `MoELayer` 中跳过原生 dispatcher，整体替换 dispatch/expert/combine；原生 expert module 仍持有参数、DDP、optimizer 和 checkpoint。配置仅允许受限 BF16 或带 fp8_param 的 MXFP8、TP=ETP=1、指定 EP、shared expert/SwiGLU，并拒绝 MoonEP、EP-overlap、delayed wgrad、latent MoE 和若干 graph scopes。实际 factory 延迟导入指定的 mixture-of-kittens MCore integration fork；原生专家参数通过 alias 参与 param-gather hook，MOK 的 state_dict/sharded_state_dict 不重复保存。autograd runtime 调外部 functional forward/backward，将数值 wgrad 写入同 device、连续 FP32/BF16 main_grad，再返回只触发 DDP hook 的参数 storage alias sentinel，其值不可读取或当作真实梯度。backend 还要求 routed/shared intermediate size 一致、无 GLU interleaving/外层 pad-to-capacity；外部 fork 自身与 HCU 资格未验证，不能把它映射成某个 flex backend。

QB 新增 global_batch histogram 配置，与默认 micro_batch 精确估计不同；当前检查要求 sigmoid、EMA=0、aux coeff=0、无 group/replay/per-expert dropping，rank capacity 还要求 Paged Stash dropless retry。runner 会在失败重放前清 histogram。当前 router 用 grad-enabled 的训练 forward 累积 int32 histogram；finalize 将每层 histogram 跨 TP×DP×CP 归并（GTP remat 路径分域归并），调用 quantile helper 更新 expert_bias/bin_bounds，然后清临时统计。histogram 不持久化，expert_bias 与 bin_bounds 持久化；改变 scope/bin 数须重建对应状态，不能随意借用旧 checkpoint。QB routing 仍拒绝 padding_mask。

补查还发现一个静态组合缺口：global_batch 初始化 qb_beta=None，但训练且观察 router_diagnostics 时，routing 仅按“是否 QB”计算 `-self.qb_beta`，没有按 scope 选择 expert_bias，会进入对 None 的负号运算。即使 TP=CP=1、完整本地序列满足诊断前置条件仍可达；本轮未执行复现，应先修正并回归该组合，不能把 tensor metrics 采集默认视为所有 QB 安全。新增 `moe_training_matches_inference` 也是带 FlashInfer/MXFP8或NVFP4、batch-invariant、selective-MoE-recompute 等严格门禁的独立 value-pass 路径；value pass 的输出用 generation kernel、反向由 checkpoint 重算的 training forward 提供；另缓存派生 kernel weights，因此增加驻留。缓存随参数版本、全局 optimizer-step post-hook、state_dict/load hook 或显式 release 失效，绕过这些入口的外部权重写入须先 release。DTensor expert 和非 Megatron-DDP param-gather pre-hook 被拒绝；MXFP8 value-pass 还将小 expert 批补到大于128行/专家的 launch。bitwise 等价是上游设计目标，本轮没有执行比较。MoonEP planner/transport 原件与测试未变，保留此前 plan/gradient ownership 和 release-before-group-destroy 边界。

## 精度、失败与维护

局部校验覆盖outputs、dgrad/wgrad、auxloss、专家空token/不均shape、padding尾部、lowprecision scales、drop/overflow和重跑；阶段loss检查完整route→expert→optimizer状态。FP8缓存/GroupedTensor不是普通BF16tensor，stash/offload与shape推断须追特殊路径。

hang先定位哪层/哪阶段/哪rank及collective split顺序；OOM看received/routed padding、stash与workspace重叠；loss异常看routing semantics、scale、auxloss/gradient和实际fallback。保留baseline dispatcher/无候选融合配置，未验backend不作可用声明。

PR #7897与#7534为已登记机制入口；进一步搜索`wiki-search-pr "MoE grouped tensor paged stash" --engine megatron`读最终实现、目标branch及测试。open/development优化只记候选，官方已merge后仍确认当前HCU运行分支是否包含。

## 固定源码与维护边界

- [docs/user-guide/features/moe.md](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/docs/user-guide/features/moe.md)
- [docs/user-guide/features/paged_stash.md](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/docs/user-guide/features/paged_stash.md)
- [megatron/core/transformer/moe/moe_layer.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/transformer/moe/moe_layer.py)
- [megatron/core/transformer/moe/token_dispatcher.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/transformer/moe/token_dispatcher.py)
- [megatron/core/transformer/moe/paged_stash.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/transformer/moe/paged_stash.py)
- [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/transformer/transformer_config.py)

2026-11-04按上述固定源码、实际消费者与官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。