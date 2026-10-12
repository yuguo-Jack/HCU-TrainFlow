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
reviewed_on: '2026-10-12'
coverage: reviewed training, parallel, state and backend implementation chains; not
  all models or runtime combinations
sources:
- source: nvidia-megatron-lm
  path: megatron/core/distributed/distributed_data_parallel.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: a19f8e1300dd8c7b294d1d52defe22ecb6e9c79fbcbae61a41dc5bf0de460f67
- source: nvidia-megatron-lm
  path: megatron/core/distributed/param_and_grad_buffer.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: ac2b7c8a3ae6bfc307886ca0d84f72b06e47874aa0c9170c8a11662912c48ff3
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/distrib_optimizer.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 892589f868b77a8f209bbcc8861521e7e71ddd46665b3dee38871aa580523389
- source: nvidia-megatron-lm
  path: megatron/core/pipeline_parallel/schedules.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 3719d850b8822e221f30472881b8802b8f88ce02167856130fae97849d1d91ee
- source: nvidia-megatron-lm
  path: megatron/core/extensions/transformer_engine.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 6ee4807baa38389691e5ecf19472ee933f2ac5b6fe51b3e3cf26539388b77bf4
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 36ebc84d850af5653d6f17aa2147f61b79f82b7a05422b8d0eba8943bafb0f87
- source: nvidia-megatron-lm
  path: megatron/training/arguments.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: eca958faeab77e1df81073998ea07aa3cc8a5884f96f6182782d620942139bd2
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

## 以端到端和余量检验

固定模型/数据/有效batch、拓扑和数值baseline，先无候选overlap短跑，再比较耦合设置。采实际group中代表rank的同一稳态窗口，记录通信启动/完成、计算争用、最长rank、wait/event与buffer峰值；吞吐另用profiler-off。

`GPU_MAX_HW_QUEUES`按实际HCU runtime版本与测量调整；CUDA connection变量和其数值不替代此变量。更强并发可能把GEMM/attention拖慢或压缩显存headroom，所以同时比较模型内kernel与同shape单测，按最终step收益而不是“重叠面积更大”选择。

训练/通信库已有功能优先复用；仍有关键路径瓶颈才考虑HCU RCCL、rocSHMEM、DeepEP/UCCL等通算实现，保持同步、buffer ownership、dtype和梯度契约。改底层库须任务独立构建安装、确认实际加载与可回退，不覆盖其他训练共用库。

## 正确性、失败与参考PR

检查更新前后的fwd/bwd、梯度累积、optimizer/masterweights、低精度scale/cache和阶段loss；多个rank成功启动不足以证明匹配collective/同policy。hang按ready→launch→wait与最早出错rank定位，OOM按通信buffers、gather副本和重叠引起的生存期定位。

保留[1F1B文档PR #7534](../../upstream/prs/NVIDIA--Megatron-LM/PR-7534.md)讨论与目标分支，阅读最终schedule/测试再采用。AMD Primus、MindSpeed/LoongForge或DeepSpeed的机制可供比较，须明确依赖、限制与采用/退役条件；其他工程的同名flag不直接映射当前Core。

## 固定源码与维护边界

- [megatron/core/distributed/distributed_data_parallel.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/distributed/distributed_data_parallel.py)
- [megatron/core/distributed/param_and_grad_buffer.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/distributed/param_and_grad_buffer.py)
- [megatron/core/optimizer/distrib_optimizer.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/optimizer/distrib_optimizer.py)
- [megatron/core/pipeline_parallel/schedules.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/pipeline_parallel/schedules.py)
- [megatron/core/extensions/transformer_engine.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/extensions/transformer_engine.py)
- [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/transformer/transformer_config.py)
- [megatron/training/arguments.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/training/arguments.py)

2026-10-12按上述固定源码/官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。
