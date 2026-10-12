---
id: official-megatron-wiki/memory
title: Megatron 显存生命周期：状态分片、重算、offload与Paged Stash
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
  path: docs/user-guide/features/dist_optimizer.md
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 9f1f0ad18cd89a8730a9d9a6bbf91e05f96b1d6e62ccc7c6c93d8cafbe5ffeca
- source: nvidia-megatron-lm
  path: docs/user-guide/features/fine_grained_activation_offloading.md
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 20fd1e02cecb27d05b18ae672ca761583a93471420edd8f3bb3133b100c95a3e
- source: nvidia-megatron-lm
  path: megatron/core/pipeline_parallel/fine_grained_activation_offload.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 96ebb98249d5d60e8c16df56f4876420146d841e3c1c4b4c9e83557d5fe2ac38
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/cpu_offloading/README.md
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 58bb8c15943166199d3066361742f2718536d4792b81cd0d22007e20e984571d
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/distrib_optimizer.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 892589f868b77a8f209bbcc8861521e7e71ddd46665b3dee38871aa580523389
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 36ebc84d850af5653d6f17aa2147f61b79f82b7a05422b8d0eba8943bafb0f87
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/paged_stash.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 950b8c72253b90e8b6936a5aa8532120bd8e056f6cc88807efa4c818d88d4efc
- source: nvidia-megatron-lm
  path: docs/user-guide/features/paged_stash.md
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 053fecb7a457408c19a5c44322c2dfd6a50a3d27e49786ddc6192b503c6d96a1
- source: nvidia-megatron-lm
  path: tests/unit_tests/pipeline_parallel/test_fine_grained_activation_offloading.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: db30edc4c97846d8a7bef0316b8900fc8c296e8dbb5c04cc28b621821c29e676
---

# Megatron 显存生命周期：状态分片、重算、offload与Paged Stash

## 先按 owner 和阶段分账

参数/低精度缓存、FP32主权重、optimizer状态、梯度、saved activations、通信/gatherbuffer、graphpool、kernel workspace和allocatorreserved分别记录；每rank/每pipeline stage不一定相同。峰值覆盖初始化、首次fwd/bwd、optimizer、save/restore和图capture，不能只拿稳态截图定可运行容量。

DP/状态分片、microbatch/accumulation、TP/PP/CP/EP与重算共同影响显存/吞吐，见[并行](parallelism.md)。先确认全模型可行和worst-rank余量，再选机制；卡快满不证明利用率最好。

## 分布式 optimizer 的真实存储

当前官方dist-optimizer文档给Adam类示例的理论bytes/param：BF16模型参数、FP32main grad下非分片18B，对DP大小d分片为`6+12/d`；FP16/FP16和FP32/FP32另有公式。它假设相应state dtype与算法，不可推广Muon、FSDP、optimizer offload或特殊权重缓存。

实现用连续parameter/main-grad buffers：backward梯度写入main-grad，reduce-scatter后各DP rank更新自己的FP32master slice，再cast并allgather供forward。参数tensor可为buffer views；物理存储、padding和临时gather计入实测，不能把view数量相加当真实字节。

## 重算与细粒度激活 offload

重算减少saved tensor、增加计算与RNG/低精度状态重放；选择light模块或昂贵模块的offload需依据shape/实际代价。细粒度offload由`PipelineOffloadManager`→per-microbatch`ChunkOffloadHandler`→module接口管理，group_start/saved-tensor hooks捕获，D2H到pinned-host，backward前H2D重载与event等待。

`activation_offload_fraction`是过滤后eligible **groups比例**，按forward顺序跨所有配置module选择，不是bytes比例，也不是module名列表比例。min tensor、末尾margin、PP-rank delta先改变候选；同0.5在不同模型可能释放完全不同字节。pool按shape/dtype复用host buffer，暖机和steady-state分开计。

`attn_proj`需与`core_attn`配合，fused_group_mlp不能再和expert_fc1/moe_act重叠offload；选择性residual replay、Paged Stash等可能已有owner，不能双重释放。CPU offload的host内存/NUMA、PCIe和通信争用也需预算。

## 教程和当前代码的图模式差异

官方offload教程主要推荐TE graph；当前TransformerConfig代码还允许受限local partial-MoE（只expert_fc1/moe_act/fused_group_mlp且未捕获完整MoE）及full_iteration路径。full_iteration要求非负`fine_grained_offloading_max_inflight_offloads`，以显式event joins约束生存期；不能从教程的一句compatible推到任意图scope。

max-inflight为0时每次offload后join，较大值可重叠但扩大生存期；None不做该类join，在上述full-iteration路径不允许。delay-offload只对实际wired delayed expert commit生效，graph replay后flush利用可隐藏的host空闲窗口；不是所有attention或图内offload都被延后。

优化要比较内存、D2H/H2D、CPU launch/event与step。NV/TE图API存在不等于HCU所有graph/backend已支持；执行前读部署分支，禁用候选offload/graph保留回退。

## Optimizer CPU offload

官方CPU-offloadREADME给`optimizer-cpu-offload`、fraction与precision-aware optimizer组合，D2H梯度→CPUstep→H2D参数可用相应overlap路径。先核对实际算法/状态dtype、hostRAM/NUMA与CPU算力；释放device state可能由PCIe和CPUstep成为新瓶颈。

clip/masterweight、overflow跳步、param-gather与checkpoint期间副本是否一致，必须沿optimizer代码和测试验证。不能因为宿主剩余内存大就默认offload对吞吐有利，更不能把copy异步提交当更新已完成。

## Paged Stash 与 capacity 不是通用开关

Paged Stash保存路由专家backward所需activations到分页设备buffer，可选pinned-host spill；它与sync-free capacity预留结合，减少动态尺寸同步/碎片，未启用stash时仍可能走capacity-runner。over-budget或overflow由runner按全rank状态触发无capacity/stash重跑，吞吐需计rerun成本。

本轮发现paged-stash教程仍写HybridEP+TEfuser，但实际config允许capacity backend `hybridep`或`ncclep`；HybridEP可用TEfuser或grouped-tensor路径。源码约束不能被旧教程替换。stash仍要求capacity，禁止层级cpu_offloading和冲突expert offload；[MoE专题](moe.md)与[历史launch案例](cases/paged-stash-launch.md)有完整调用/优化边界。

这里区分的是教程描述与配置检查范围。配置被接受不等于每种 backend、专家实现和 stash 组合都已完成运行验证，也不代表 HCU 分支支持；实际任务继续核对 dispatcher、runner、保存/恢复调用链及对应测试。

## 数值、泄漏和恢复诊断

增长趋势按allocated/reserved/deviceused与各owner统计，分析微批引用、saved tensors、event最后使用、图池和checkpoint后台。一次empty_cache下降不能证明所有泄漏已解决。backward/recompute、optimizer、save/reload与低精度cache共同做局部回归，稳定配置阶段再验loss。

offload单测覆盖生命周期和选择规则，缺HCU设备/平台项明示待验。保留不启用该机制的配置，失败先恢复可信state并定位最早非法释放/重复restore，而不是同时改多个内存参数。

## 固定源码与维护边界

- [docs/user-guide/features/dist_optimizer.md](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/docs/user-guide/features/dist_optimizer.md)
- [docs/user-guide/features/fine_grained_activation_offloading.md](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/docs/user-guide/features/fine_grained_activation_offloading.md)
- [megatron/core/pipeline_parallel/fine_grained_activation_offload.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/pipeline_parallel/fine_grained_activation_offload.py)
- [megatron/core/optimizer/cpu_offloading/README.md](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/optimizer/cpu_offloading/README.md)
- [megatron/core/optimizer/distrib_optimizer.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/optimizer/distrib_optimizer.py)
- [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/transformer/transformer_config.py)
- [megatron/core/transformer/moe/paged_stash.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/transformer/moe/paged_stash.py)
- [docs/user-guide/features/paged_stash.md](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/docs/user-guide/features/paged_stash.md)
- [tests/unit_tests/pipeline_parallel/test_fine_grained_activation_offloading.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/tests/unit_tests/pipeline_parallel/test_fine_grained_activation_offloading.py)

2026-10-12按上述固定源码/官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。
