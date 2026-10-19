---
id: ecosystem/topics/loongforge-ep-offload
title: LoongForge：跨微批 EP 重叠、延迟 wgrad 与细粒度卸载
engine: loongforge
kind: authored
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-20'
coverage: selected source delta and related discussion review; unchanged evidence reused; no HCU runtime validation
sources:
- source: baidu-baige-loongforge
  path: .gitmodules
  commit: 15504e1bb7d948bd3900d17ed35fe5cd4bc50d3c
  sha256: b5aca9eaf884dfde53b152fc6000eff8a8c793339b659411f6e79292bf68b2ed
- source: baidu-baige-loongforge
  path: docs/source/features/moe_all2all_overlap.md
  commit: 15504e1bb7d948bd3900d17ed35fe5cd4bc50d3c
  sha256: bd5b07da7b731f7cc3b3d0259ea4c9153da39fa0da7622e3a6cc493aaa46a615
- source: baidu-loong-megatron
  path: megatron/core/pipeline_parallel/schedules.py
  commit: cfcdede99642303b1dff0464b77a7df50ef6e4ea
  sha256: 97eb33ae369eae12ffc86b76d7c6ab4ce7d3c8fc4536278e6643ad6cd581bb00
- source: baidu-loong-megatron
  path: megatron/core/pipeline_parallel/fine_grained_activation_offload.py
  commit: cfcdede99642303b1dff0464b77a7df50ef6e4ea
  sha256: 2211b10e879f93ebc1abb0289bc6a56094a41483c8172b582c38c0b2bda88491
- source: baidu-loong-megatron
  path: megatron/core/transformer/transformer_config.py
  commit: cfcdede99642303b1dff0464b77a7df50ef6e4ea
  sha256: 1ddc625ba2d9304b535c88279d2db9a47796eaeb3617bad9a6e6674386a69d74
---

# LoongForge：跨微批 EP 重叠、延迟 wgrad 与细粒度卸载

## 性能问题与父子版本

EP all-to-all在关键路径暴露等待时，将不同microbatch的forward/backward和通信交错，可用计算隐藏dispatch/combine。文档入口在父LoongForge，真实schedule/offload由父树锁定。本次父仓 `15504e1bb7d9` 已选 Loong-Megatron `cfcdede99642303b1dff0464b77a7df50ef6e4ea`；与历史 `64c279` 比较，`schedules.py` 和 `fine_grained_activation_offload.py` 原件逐字节相同，所述 EP/卸载生命周期继续适用。不是任意Megatron main都有相同flag和节点。

子仓本次新增的是另一条 [变量长 ChunkPipe](loongforge-chunkpipe-variable-length.md)接入：其 iterator、MLA/MTP、数据广播与 loss 归一化有自己的条件。不能因共享 microbatch/schedule 术语就把变长序列分块、跨微批 EP 和 CPU 激活卸载当成同一个开关或已验证组合。

## 调度与参数组合

`--overlap-moe-expert-parallel-comm --delay-wgrad-compute`依赖interleaved 1F1B。将部分wgrad推迟使dgrad与下一段任务更早推进，但改变活动microbatch/激活生命周期。传统full-layer recompute与该调度不兼容；文档采用selective的a2a_overlap_attn/post_attn/mlp与`--fine-grained-activation-offloading`配套选择tensor。

文档给`CUDA_DEVICE_MAX_CONNECTIONS=32`是NV路径示例，不是HCU`GPU_MAX_HW_QUEUES`的等价值或推荐默认。TP/EP并发争用、现场runtime队列行为应分别验证。

## 固定源码的卸载机制

`PipelineOffloadManager`维护按VPP stage的chunk队列、专用D2H/H2D stream和事件；autograd saved-tensor hooks将需要保存的tensor交`ChunkOffloadHandler`。按组offload到pinned host memory，再按backward消费次序预取/等待。first/last chunk及马上消费的末层会避免无效卸载；不能只看`non_blocking=True`就认为所有传输被隐藏。

每tensor记录原device和CPU副本，FP8使用`Float8Tensor.make_like`保留相关表示；reload等待offload事件，消费者还须等待reload完成。队列归属、tag、buffer释放、TE context和异步copy共同构成正确性。默认threshold用数据项数量检查，估算数据量应乘实际dtype字节，不能把阈值数字直接当bytes。

## 收益、代价和验证

收益是EP暴露等待减少、HBM激活降低；代价为额外活动buffer、host容量、D2H/H2D/PCIe与NUMA、事件/launch及重算计算。`--bindpcie`用于其NV NUMA亲和示例，HCU按真实GPU/CPU拓扑选择。单kernel变慢也可能换来更快step，但必须记录整体与各阶段因果。

在同shape/token distribution/GBS下比普通schedule、overlap、延迟wgrad、再offload/recompute，逐步保持梯度与阶段loss可信。测每并行域代表rank、wgrad/dgrad、活动chunk、显存、PCIe和关键路径。至少检查多个microbatch、VPP首末边界、异步buffer重复使用、FP8与checkpoint恢复，不把文档支持描述升级为HCU通过。

## 回退与更新责任

卡住查schedule/queue/事件与collective顺序；梯度错误查提前释放或FP8元数据，OOM区分HBM激活和通信buffer。按完整机制包恢复可信schedule与缓存，不保留一半新wgrad/一半旧state。更新父gitlink后重新读子schedule/offload/config与测试，联动[案例](../cases/loongforge-ep-offload.md)及[总览](../overview/engineering-guide.md)。

## 固定证据与复核范围

- [.gitmodules](https://github.com/baidu-baige/LoongForge/blob/15504e1bb7d948bd3900d17ed35fe5cd4bc50d3c/.gitmodules)
- [docs/source/features/moe_all2all_overlap.md](https://github.com/baidu-baige/LoongForge/blob/15504e1bb7d948bd3900d17ed35fe5cd4bc50d3c/docs/source/features/moe_all2all_overlap.md)
- [megatron/core/pipeline_parallel/schedules.py](https://github.com/baidu-baige/Loong-Megatron/blob/cfcdede99642303b1dff0464b77a7df50ef6e4ea/megatron/core/pipeline_parallel/schedules.py)
- [megatron/core/pipeline_parallel/fine_grained_activation_offload.py](https://github.com/baidu-baige/Loong-Megatron/blob/cfcdede99642303b1dff0464b77a7df50ef6e4ea/megatron/core/pipeline_parallel/fine_grained_activation_offload.py)
- [megatron/core/transformer/transformer_config.py](https://github.com/baidu-baige/Loong-Megatron/blob/cfcdede99642303b1dff0464b77a7df50ef6e4ea/megatron/core/transformer/transformer_config.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
