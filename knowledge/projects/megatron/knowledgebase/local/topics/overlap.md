---
id: official-megatron-wiki/overlap
title: Megatron 通信重叠：DP bucket、TP、PP与EP的依赖和限制
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
  path: megatron/core/distributed/distributed_data_parallel.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 26a06023687b3ab6a9d89fc2d1776997e619dc9d34649d38b90c2b85cb3f7b07
- source: nvidia-megatron-lm
  path: megatron/core/distributed/param_and_grad_buffer.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 4cf9cf4c1e8cdd4ae9c2e8f190486f39cdaa6b6a9405ce57a46acbb94ba49024
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/distrib_optimizer.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 5e0edba9f82b504a1785959824f03b8ea5c13799049c29a579ce0cc3b9a26e7b
- source: nvidia-megatron-lm
  path: megatron/core/pipeline_parallel/schedules.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 4d1c5904df165b8917029602466ebb0f5409db591b912e6969f4561ecc385171
- source: nvidia-megatron-lm
  path: megatron/core/extensions/transformer_engine.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 402dd8cf540b17fac15f0f77fba603acaa5fb4f6d9493536ff6550719f0bda47
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: ec8de7059bf8d6c78663384a489794d0712eaa1b81685ad0339e2c77cb9e32e3
- source: nvidia-megatron-lm
  path: megatron/training/arguments.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: fa0df51942af46de4af237397c81dc5200f86de11078334aaf19709c95a684fb
---

# Megatron 通信重叠：DP bucket、TP、PP与EP的依赖和限制

## 先判断通信是哪种问题

trace中collective总时长不等于暴露端到端开销。先与环境/同shape单测确认链路和库调用是否达预期，再区分不可避免的数据搬运、launch/同步空泡、慢rank偏斜和可隐藏时间。固有通信优先overlap或有依据的通算融合；真实链路异常先解决底层，不能用overlap掩盖。

## 四域实现与生效条件

| 域 | 代码/触发 | 收益来源 | 代价与核验 |
| --- | --- | --- | --- |
| DP gradient | DDP grad hooks→bucket ready→start/finish_grad_sync | backward尚未结束时归并ready桶 | 桶小增加消息；仍须最终wait，padding与rank顺序一致 |
| DP parameter | distributed/layerwise optimizer→param-sync→forward prehook | 下一层计算前预取allgather | buffer/低精度缓存、首层等待、optimizer/保存切换 |
| TP | TE linears/user-buffer及实际backend | GEMM分块与allgather/reduce-scatter重叠 | 是否真正进入TE/HCU对应路径、额外工作区与CU/HBM竞争 |
| PP | Core schedule→P2PCommunicator | P2P与其他microbatch/chunk计算并行 | stage分配、microbatch/VPP、send/recv配对和tensor最后使用 |
| EP | MoE dispatcher与combined schedule | dispatch/combine与其他计算隐藏 | token skew、专家/weight-gradient生命周期、实现限制 |

当前DDP在overlap关闭时不分bucket；PP rank>0或disable_bucketing可合成单bucket。配置了bucket_size并不保证每rank都用该粒度。`no_sync`管理非末微批累积，ready hook与final sync缺一不可，不能把去wait当优化。

`start_param_sync`默认可发异步allgather，prehook在消费参数前等待；某些schedule/optimizer-step显式dispatch。保存/eval/训练切换会改变hooks，需要检查是否正确禁用/启用与first iteration，防止读旧权重或重复gather。当前args对`overlap_param_gather`要求相应optimizer/FSDP及grad-overlap，具体以部署分支校验为准。

## PP 和 EP 的当前限制

交错schedule明确拒绝`overlap_p2p_comm`与`batch_p2p_comm`同时启用；VPP的group-size/微批约束也影响调度，不只开一个overlap flag。非交错与交错路径分开分析，stage不均先查层/embedding/MTP/loss分配，不能先优化某个随手挑的kernel。

当前`overlap_moe_expert_parallel_comm`要求EP>1、alltoall/flex、支持的PyTorch、BF16/FP16模型；PP>1需VPP，禁止full recompute/某些MoE重算，禁止同用shared-expert-overlap，MTP最多一层等约束。`ncclep`另限制expert_fc1 offload与特定释放路径；TE图不能包含被该路径禁止的完整MoE/MLP scope。以上是固定main条件，不写成全版本的永久规则。

若用了DeepEP/HybridEP/NCCL-EP等后端，查实际源码和consumer接入，不将同名capability视为HCU已实现。更多见[MoE](moe.md)与[memory](memory.md)。

## 新机制的组合边界

MoonEP 在 preprocess 启动规划，再与共享专家或配对计算重叠；它复用 HybridEP transport，却不等同已有跨微批 EP-overlap。当前 config 拒绝同时开启这些调度，也拒绝 shared-expert-overlap 等冲突项，详见[虚拟专家生命周期](moe.md#moonep把负载搬到虚拟专家的训练契约)。配置互斥、stream/event 完成和反向梯度 owner 要一起验证。

TP user-buffer 的容量由实际 batch 长度与 microbatch 推导；VLM 的 decoder 长度和模型位置容量是不同输入。恢复、换 shape 或重建 communicator 后核对实际 buffer，不能以旧一次 init 成功证明新布局仍匹配。

## 以端到端和余量检验

固定模型/数据/有效batch、拓扑和数值baseline，先无候选overlap短跑，再比较耦合设置。采实际group中代表rank的同一稳态窗口，记录通信启动/完成、计算争用、最长rank、wait/event与buffer峰值；吞吐另用profiler-off。

`GPU_MAX_HW_QUEUES`按实际HCU runtime版本与测量调整；CUDA connection变量和其数值不替代此变量。更强并发可能把GEMM/attention拖慢或压缩显存headroom，所以同时比较模型内kernel与同shape单测，按最终step收益而不是“重叠面积更大”选择。

训练/通信库已有功能优先复用；仍有关键路径瓶颈才考虑HCU RCCL、rocSHMEM、DeepEP/UCCL等通算实现，保持同步、buffer ownership、dtype和梯度契约。改底层库须任务独立构建安装、确认实际加载与可回退，不覆盖其他训练共用库。

## 正确性、失败与参考PR

检查更新前后的fwd/bwd、梯度累积、optimizer/masterweights、低精度scale/cache和阶段loss；多个rank成功启动不足以证明匹配collective/同policy。hang按ready→launch→wait与最早出错rank定位，OOM按通信buffers、gather副本和重叠引起的生存期定位。

保留[1F1B文档PR #7534](../../upstream/prs/NVIDIA--Megatron-LM/PR-7534.md)讨论与目标分支，阅读最终schedule/测试再采用。AMD Primus、MindSpeed/LoongForge或DeepSpeed的机制可供比较，须明确依赖、限制与采用/退役条件；其他工程的同名flag不直接映射当前Core。

## 固定源码与维护边界

- [megatron/core/distributed/distributed_data_parallel.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/core/distributed/distributed_data_parallel.py)
- [megatron/core/distributed/param_and_grad_buffer.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/core/distributed/param_and_grad_buffer.py)
- [megatron/core/optimizer/distrib_optimizer.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/core/optimizer/distrib_optimizer.py)
- [megatron/core/pipeline_parallel/schedules.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/core/pipeline_parallel/schedules.py)
- [megatron/core/extensions/transformer_engine.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/core/extensions/transformer_engine.py)
- [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/core/transformer/transformer_config.py)
- [megatron/training/arguments.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/training/arguments.py)

2026-10-20按上述固定源码/官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。