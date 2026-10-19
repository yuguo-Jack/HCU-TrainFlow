---
id: ecosystem/cases/loongforge-ep-offload
title: 案例：跨微批 EP overlap 与细粒度激活策略
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
  path: docs/source/features/moe_all2all_overlap.md
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: bd5b07da7b731f7cc3b3d0259ea4c9153da39fa0da7622e3a6cc493aaa46a615
- source: baidu-baige-loongforge
  path: .gitmodules
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: b5aca9eaf884dfde53b152fc6000eff8a8c793339b659411f6e79292bf68b2ed
- source: baidu-loong-megatron
  path: megatron/core/pipeline_parallel/schedules.py
  commit: 64c279afb879229cff12fb293624e3691990403f
  sha256: 97eb33ae369eae12ffc86b76d7c6ab4ce7d3c8fc4536278e6643ad6cd581bb00
- source: baidu-loong-megatron
  path: megatron/core/pipeline_parallel/fine_grained_activation_offload.py
  commit: 64c279afb879229cff12fb293624e3691990403f
  sha256: 2211b10e879f93ebc1abb0289bc6a56094a41483c8172b582c38c0b2bda88491
- source: baidu-baige-loongforge
  path: docs/source/features/moe_all2all_overlap.md
  commit: 15504e1bb7d948bd3900d17ed35fe5cd4bc50d3c
  sha256: bd5b07da7b731f7cc3b3d0259ea4c9153da39fa0da7622e3a6cc493aaa46a615
- source: baidu-baige-loongforge
  path: .gitmodules
  commit: 15504e1bb7d948bd3900d17ed35fe5cd4bc50d3c
  sha256: b5aca9eaf884dfde53b152fc6000eff8a8c793339b659411f6e79292bf68b2ed
- source: baidu-loong-megatron
  path: megatron/core/pipeline_parallel/schedules.py
  commit: cfcdede99642303b1dff0464b77a7df50ef6e4ea
  sha256: 97eb33ae369eae12ffc86b76d7c6ab4ce7d3c8fc4536278e6643ad6cd581bb00
- source: baidu-loong-megatron
  path: megatron/core/pipeline_parallel/fine_grained_activation_offload.py
  commit: cfcdede99642303b1dff0464b77a7df50ef6e4ea
  sha256: 2211b10e879f93ebc1abb0289bc6a56094a41483c8172b582c38c0b2bda88491
---

# 案例：跨微批 EP overlap 与细粒度激活策略

## 问题、版本及本次复核

EP通信等待与活动激活限制同时存在时，交错不同microbatch的F/B/A2A，再将部分wgrad推迟，需要重新组织重算和卸载。历史案例固定 Loong-Megatron `64c279afb879229cff12fb293624e3691990403f`。2026-10-20 复核父仓 `15504e1bb7d9` 时，实际 gitlink 已改为 `cfcdede99642303b1dff0464b77a7df50ef6e4ea`；所引用 schedule/offload 两文件逐字节相同，因此保留此案例的机制范围，而不再宣称子仓未变。新 ChunkPipe 消费者变化另见[专题](../topics/loongforge-chunkpipe-variable-length.md)，不把历史 EP 分析升级成全部新组合已验证。仍未做HCU性能验证。

## 为什么这样改与实现位置

interleaved1F1B的EP重叠不能直接搭full-layer recompute；其文档用模块级selective recompute和指定tensor卸载配套。`PipelineOffloadManager→ChunkOffloadHandler`管理VPP chunk、autograd保存tensor、pinned host副本、D2H/H2D stream/event与backward消费队列，跳过马上消费的边界tensor，FP8另保留相应表示。[机制专题](../topics/loongforge-ep-offload.md)提供完整路径。

## 适用条件和证据

必须确认真实采用分支具有相同schedule/dispatcher、层/VPP布局与梯度同步契约。NV文档的CUDA连接数和NUMAflag不是HCU默认。比较各rank EP暴露等待、dgrad/wgrad、活动microbatch、HBM/host内存、D2H/H2D与CPU拓扑；按普通路径→overlap→延迟wgrad→卸载逐步验证数值，再测稳态step和阶段loss。

## 失败条件与回退

检查队列/事件、重复buffer、梯度累计、RNG、低精度scale/cache与checkpoint恢复。回退以调度+state+内存策略完整机制包处理；阶段loss异常回可信基线找首差。新父提交不改变子源码也不能自动声明所有HCU组合通过，后续更新同时查[总览](../overview/engineering-guide.md)、专题、子gitlink及对应测试。

## 固定证据与复核范围

- [docs/source/features/moe_all2all_overlap.md](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source/features/moe_all2all_overlap.md)
- [.gitmodules](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/.gitmodules)
- [megatron/core/pipeline_parallel/schedules.py](https://github.com/baidu-baige/Loong-Megatron/blob/64c279afb879229cff12fb293624e3691990403f/megatron/core/pipeline_parallel/schedules.py)
- [megatron/core/pipeline_parallel/fine_grained_activation_offload.py](https://github.com/baidu-baige/Loong-Megatron/blob/64c279afb879229cff12fb293624e3691990403f/megatron/core/pipeline_parallel/fine_grained_activation_offload.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
