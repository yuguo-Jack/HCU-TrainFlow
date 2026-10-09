---
id: official-megatron-wiki/overlap
title: TP、DP、PP、EP overlap 的适用条件
engine: megatron
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-megatron-lm
  path: megatron/core/distributed/distributed_data_parallel.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: a19f8e1300dd8c7b294d1d52defe22ecb6e9c79fbcbae61a41dc5bf0de460f67
- source: nvidia-megatron-lm
  path: megatron/core/pipeline_parallel/schedules.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 3719d850b8822e221f30472881b8802b8f88ce02167856130fae97849d1d91ee
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 7fc7af4f3f6fe67a6a1d7f9a7df63c5eaf245bc2cb686ff09a0adc58292daa6a
---

# TP、DP、PP、EP overlap 的适用条件

## 分开评估四种问题

DP 关注梯度桶 ready 时机、reduce-scatter 和下步参数 all-gather；TP 关注 layer 内部 collective 与 GEMM 分块；PP 关注 P2P、微批和交错 schedule；EP 关注 token dispatch/combine 及 expert 工作量。总通信 kernel 耗时不是暴露在关键路径上的通信开销。

源码入口分别是 DDP bucket/hooks、Core schedule、TransformerConfig 与 MoE layer。当前 schedules 对一些非交错/交错组合有显式断言，例如 P2P overlap 与其他批处理模式的约束，应跟随选定分支读取，不做全版本常量。

## HCU 实验设计

先关候选 overlap 建立可运行基线，再一次改变一个机制，记录流、event 等待、通信 buffer、设备队列与显存峰值。`GPU_MAX_HW_QUEUES` 是需要记录的 HCU/HIP runtime 变量；取值基于当前 runtime 实现和实测，不把 CUDA 的连接数变量数值直接搬过来。

并发通信可能争用 CU、HBM 和调度资源，使 GEMM 单次更慢。应同时报告端到端改善、模型内与独立 shape 实测差距、最长 rank 和内存余量。通算融合或 rocSHMEM 只有在瓶颈及生命周期证据支持时引入。

## 固定源码与更新范围

- [megatron/core/distributed/distributed_data_parallel.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/core/distributed/distributed_data_parallel.py)
- [megatron/core/pipeline_parallel/schedules.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/core/pipeline_parallel/schedules.py)
- [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/core/transformer/transformer_config.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
