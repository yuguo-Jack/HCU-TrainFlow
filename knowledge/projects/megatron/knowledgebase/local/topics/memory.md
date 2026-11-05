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
reviewed_on: '2026-11-04'
coverage: frozen source delta and consumer review; unchanged files rechecked; no HCU runtime validation
sources:
- source: nvidia-megatron-lm
  path: docs/user-guide/features/dist_optimizer.md
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 3b1c2ea7abaa7a6ce3dec095b736f23b936e8ad6cb013d6582c0992ae9c6a5e5
- source: nvidia-megatron-lm
  path: docs/user-guide/features/fine_grained_activation_offloading.md
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 7aad62c9a0199bb95783d058410d79399d7d61f98bf6b98e2fa96415852f675b
- source: nvidia-megatron-lm
  path: megatron/core/pipeline_parallel/fine_grained_activation_offload.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 3c3ada00034a77c55fd632c67593b37a6bb99e92928231775521446b76ab4cb3
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/cpu_offloading/README.md
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 58bb8c15943166199d3066361742f2718536d4792b81cd0d22007e20e984571d
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/distrib_optimizer.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 748f6f665109a99ae9b13cd90c6cb179afb855906bdf75f1442064a0c11e20a9
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 39f34cb0f9005ad53b4d318346a7b6bbb88931a19d5f868805a42e83dd1eece6
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/paged_stash.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: c120b2e7ce96baf76be69b5a3a7944a584c406fd4c093c56e71b5be6e0313e53
- source: nvidia-megatron-lm
  path: docs/user-guide/features/paged_stash.md
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: c290e8e9a72f9b0a0b864651dc28e692279d5389e547dbef5ea3f56f622a5a7d
- source: nvidia-megatron-lm
  path: tests/unit_tests/pipeline_parallel/test_fine_grained_activation_offloading.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: ba362d34fd0efddb2c6f58f52a115970f134a79fcc2fed925d5a552583f01413
- source: nvidia-megatron-lm
  path: megatron/core/pipeline_parallel/pinned_activation_buffer.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 4dd4a48f954c366ff4d2cdd3e56820ee81f6f5f495f69110ca6e0e86c2be6e82
- source: nvidia-megatron-lm
  path: megatron/core/full_cuda_graph.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 8859a7946d168298e36af1f0ccb02d99c32e8b69a1055aaf155a5d31e628d78f
- source: nvidia-megatron-lm
  path: megatron/core/transformer/multi_token_prediction.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 567b6e3f2a63d9488fdb02780af47dcd26c81a654701c9a5bad4d9d76a266638
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 1cfba3a404c97febc4c2e40895467372e6ab540006dc6a6e22fbc547087a5b75
retrieved_on: '2026-11-04'
---

# Megatron 显存生命周期：状态分片、重算、offload与Paged Stash

## 先按 owner 和阶段分账

参数/低精度缓存、FP32主权重、optimizer状态、梯度、saved activations、通信/gatherbuffer、graphpool、kernel workspace和allocatorreserved分别记录；每rank/每pipeline stage不一定相同。峰值覆盖初始化、首次fwd/bwd、optimizer、save/restore和图capture，不能只拿稳态截图定可运行容量。

DP/状态分片、microbatch/accumulation、TP/PP/CP/EP与重算共同影响显存/吞吐，见[并行](parallelism.md)。先确认全模型可行和worst-rank余量，再选机制；卡快满不证明利用率最好。

## 分布式 optimizer 的真实存储

当前官方dist-optimizer文档给Adam类示例的理论bytes/param：BF16模型参数、FP32main grad下非分片18B，对DP大小d分片为`6+12/d`；FP16/FP16和FP32/FP32另有公式。它假设相应state dtype与算法，不可推广Muon、FSDP、optimizer offload或特殊权重缓存。

实现用连续parameter/main-grad buffers：backward梯度写入main-grad，reduce-scatter后各DP rank更新自己的FP32master slice，再cast并allgather供forward。参数tensor可为buffer views；物理存储、padding和临时gather计入实测，不能把view数量相加当真实字节。

## 注册通信缓冲区的卸载生命周期

当前 NCCL UBR 的 gradient-buffer offload 要在构造时选择可替换梯度池，参数池保持存活。先注销全部相关梯度池，再释放 storage 和池 owner；reload 创建、填充并重新注册新池。MXFP8 参数与梯度共享 storage 的布局显式拒绝该卸载，不能把它与所有低精度存储复用相加计算节省。

注销中途失败会保留 storage，但早先的注销不会回滚；调用方必须终止该次运行，不能在可能部分注册的模型上直接重试 offload。reload 的失败清理是另一条路径，不能推成前述注销失败也可安全重试。HCU 使用实际 RCCL/allocator consumer 验证，不把这份 NVIDIA pool 实现当作现成 HIP 能力。

## 重算与细粒度激活 offload

重算减少saved tensor、增加计算与RNG/低精度状态重放；选择light模块或昂贵模块的offload需依据shape/实际代价。细粒度offload由`PipelineOffloadManager`→per-microbatch`ChunkOffloadHandler`→module接口管理，group_start/saved-tensor hooks捕获，D2H到pinned-host，backward前H2D重载与event等待。

`activation_offload_fraction` 的 steady-state 是过滤后 eligible **groups 比例**，按 forward 顺序跨配置 module 选择，不是 bytes 比例。暖机已改为每 chunk、每 module 名独立在线配额：第 k 次出现的 ceil(k×fraction) 增量决定是否拷贝，空/不合格组也推进计数；0.5 选择各 module 的第1/3/5…次。暖机只收集候选字节而不必全量 CPU copy，之后再按 margin、PP delta、fraction 形成稳态策略，两阶段不可混算。驻留组仍占 reload 队列的 no-op 槽；post-warmup margin 组排除该槽，保留其 backward marker 触发预取，避免部分 offload 提前堆积已重载张量。

`attn_proj` 需与 `core_attn` 配合；`fused_group_mlp` 与 `expert_fc1`+`moe_act` 是 grouped MLP 两条实现上的等价请求，由每个实例映射到其 fused/unfused 路径，配置不可重复列；选择性residual replay、Paged Stash等可能已有owner，不能双重释放。CPU offload的host内存/NUMA、PCIe和通信争用也需预算。

## 教程和当前代码的图模式差异

官方offload教程主要推荐TE graph；当前TransformerConfig代码还允许受限local partial-MoE（只expert_fc1/moe_act/fused_group_mlp且未捕获完整MoE）及full_iteration路径。full_iteration要求非负`fine_grained_offloading_max_inflight_offloads`，以显式event joins约束生存期；不能从教程的一句compatible推到任意图scope。

max-inflight为0时每次offload后join，较大值可重叠但扩大生存期；None不做该类join，在上述full-iteration路径不允许。delay-offload只对实际wired delayed expert commit生效，graph replay后flush利用可隐藏的host空闲窗口；不是所有attention或图内offload都被延后。

优化要比较内存、D2H/H2D、CPU launch/event与step。NV/TE图API存在不等于HCU所有graph/backend已支持；执行前读部署分支，禁用候选offload/graph保留回退。

新 `fine_grained_offloading_buffer_size_gib` 默认0关闭，可把各 chunk 的备份打包进每 rank 一个固定 pinned buffer；正容量须为256B倍数、首次使用前配置、永不自动增长。实际 allocator 直接依赖 cuda-python 的 `cudaHostAlloc`，并非通用 HIP allocator。所有备份 H2D reader 完成后才允许复用；graph 捕获区保留地址，即使 reset/clear 也不收回，eager 只能用其余尾部，观察 live/peak 与 graph_reserved_bytes。一般 PP/VPP/EP overlap 可能要容纳整 iteration 的备份，不能按一微批预算，也不能把它当所有 host 内存上限。

FGO 和 Paged Stash 现在都先排除 CheckpointWithoutOutput 所拥有的 storage，避免接管待重算恢复的 view；core_attn offload 对共享 storage 的非连续 packed Q/K/V 仍显式拒绝，不能把 contiguous copy 当作无害替代。

full_iteration 的 eager optimizer 新增独立 gradient-conversion graph 复用 F/B scratch，地址签名变动报错、训练图重建时失效；optimizer_cuda_graph、CPU offload、Megatron FSDP 与 precision-aware alias 路径不套用同一省内存结论。MTP 的逐 head early backward 另减少同时驻留 logits，捕获/暖机退回 deferred，见[训练/loss](training-and-loss.md)。原 Adam 18B/6+12/d 公式与 UBR 失败终止边界仍由未改对应机制支持，继续作为有条件估算。

## Optimizer CPU offload

官方CPU-offloadREADME给`optimizer-cpu-offload`、fraction与precision-aware optimizer组合，D2H梯度→CPUstep→H2D参数可用相应overlap路径。先核对实际算法/状态dtype、hostRAM/NUMA与CPU算力；释放device state可能由PCIe和CPUstep成为新瓶颈。

clip/masterweight、overflow跳步、param-gather与checkpoint期间副本是否一致，必须沿optimizer代码和测试验证。不能因为宿主剩余内存大就默认offload对吞吐有利，更不能把copy异步提交当更新已完成。

## Paged Stash 与 capacity 不是通用开关

Paged Stash保存路由专家backward所需activations到分页设备buffer，可选pinned-host spill；它与sync-free capacity预留结合，减少动态尺寸同步/碎片，未启用stash时仍可能走capacity-runner。over-budget或overflow由runner按全rank状态触发无capacity/stash重跑，吞吐需计rerun成本。

当前 paged-stash 教程已补充 HybridEP 的 TE fuser 与 GroupedTensor 两条专家路径；非 fuser 要求支持 saved-buffer 标记的 TE、fused SwiGLU/QuickGeGLU、无 GLU interleaving，单独 launches 仍可能有 CPU 开销。配置对 rank capacity 的 backend 检查仍包含 `hybridep`/`ncclep`，不能将 HybridEP 教程当作所有 backend 的完整资格矩阵。stash仍要求capacity，禁止层级cpu_offloading和冲突expert offload；[MoE专题](moe.md)与[历史launch案例](../cases/paged-stash-launch.md)有完整调用/优化边界。

这里区分的是教程描述与配置检查范围。配置被接受不等于每种 backend、专家实现和 stash 组合都已完成运行验证，也不代表 HCU 分支支持；实际任务继续核对 dispatcher、runner、保存/恢复调用链及对应测试。

## 数值、泄漏和恢复诊断

增长趋势按allocated/reserved/deviceused与各owner统计，分析微批引用、saved tensors、event最后使用、图池和checkpoint后台。一次empty_cache下降不能证明所有泄漏已解决。backward/recompute、optimizer、save/reload与低精度cache共同做局部回归，稳定配置阶段再验loss。

offload单测覆盖生命周期和选择规则，缺HCU设备/平台项明示待验。保留不启用该机制的配置，失败先恢复可信state并定位最早非法释放/重复restore，而不是同时改多个内存参数。

## 固定源码与维护边界

- [docs/user-guide/features/dist_optimizer.md](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/docs/user-guide/features/dist_optimizer.md)
- [docs/user-guide/features/fine_grained_activation_offloading.md](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/docs/user-guide/features/fine_grained_activation_offloading.md)
- [megatron/core/pipeline_parallel/fine_grained_activation_offload.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/pipeline_parallel/fine_grained_activation_offload.py)
- [megatron/core/optimizer/cpu_offloading/README.md](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/optimizer/cpu_offloading/README.md)
- [megatron/core/optimizer/distrib_optimizer.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/optimizer/distrib_optimizer.py)
- [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/transformer/transformer_config.py)
- [megatron/core/transformer/moe/paged_stash.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/transformer/moe/paged_stash.py)
- [docs/user-guide/features/paged_stash.md](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/docs/user-guide/features/paged_stash.md)
- [tests/unit_tests/pipeline_parallel/test_fine_grained_activation_offloading.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/tests/unit_tests/pipeline_parallel/test_fine_grained_activation_offloading.py)

2026-11-04按上述固定源码、实际消费者与官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。