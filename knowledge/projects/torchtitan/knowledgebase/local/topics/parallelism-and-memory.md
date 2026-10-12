---
id: official-torchtitan-wiki/parallelism-and-memory
title: TorchTitan 并行域、容量、重算与显存生命周期
engine: torchtitan
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: Curated source chains and official evidence at a fixed main commit; not
  all models, backends or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/distributed/PARALLELISM_CONTEXT.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: b3592c4fd1279ec85a188510a3cf13b9dc63ecfc3e10a50270047fff8f044948
- source: pytorch-torchtitan
  path: torchtitan/distributed/parallelism_context.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 36d2ff85f47b79e42d1e69567c9a4466f4573340630a4b5b55479cadb85350f1
- source: pytorch-torchtitan
  path: torchtitan/config/parallelism.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 7fd587ef274963ff8171981b3dee2adde352c4401466044ecc05b39fdf834573
- source: pytorch-torchtitan
  path: torchtitan/distributed/fsdp.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 572effd3ae6d6d0e65c436cac17fbeecbd0927a1c41eaa166bb98884da0b6377
- source: pytorch-torchtitan
  path: torchtitan/distributed/PIPELINE_PARALLEL.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: c7f4d13d05e0c858f586c431c643e8b5478f9145318e7fdc75fe6df79fded44e
- source: pytorch-torchtitan
  path: torchtitan/distributed/pipeline_parallel.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: b2dd65caa89d17c500f9ee4c765a500654e4678d5108e6e5c2fb8581a5476b8b
- source: pytorch-torchtitan
  path: torchtitan/distributed/REMAT.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 330408f54575d08657fae75ece3890f6f5329eeced1b1d07d43d7f1e9868328b
- source: pytorch-torchtitan
  path: torchtitan/distributed/activation_checkpoint.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: d2ecf1a77668b5e1d83c162b067ed47881eb6549ccfa793ec5ea6958a06a6a20
- source: pytorch-torchtitan
  path: torchtitan/config/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: e62e3776a4dd1c2179b3643d9e611f5a6f53fc972ac16de4588ee96a99a06b9b
- source: pytorch-torchtitan
  path: torchtitan/components/optim/ema.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: d41f90389d35aa3ba0d3050fba312772c52d10428e53e7b3dd24aecf8144ea3c
pr_sources:
- pr-pytorch--torchtitan-5101
- pr-pytorch--torchtitan-5280
- pr-pytorch--torchtitan-5266
---
# TorchTitan 并行域、容量、重算与显存生命周期

## 正确计算卡数与 EP

标准 dense mesh 满足：

```text
world_size = pp × dp_replicate × dp_shard × cp × tp
dp = dp_replicate × dp_shard
edp_shard = dp_shard × cp × tp / ep
```

EP 是同一组设备上的 sparse mesh 重解释，**不能再额外乘到 dense world_size 上**。EP 必须满足相应可整除约束；`dp_shard=-1` 可由剩余规模推导。dense 与 sparse 参数/梯度走不同 mesh，通信分析要用保存的真实 group 成员，而不是按连续 rank 猜测。

模型布局由构造时的 ParallelismConfig 决定。改 CP/EP 后需要重新调用模型构造器，不能只替换 Trainer 上的并行字段。更换并行还要检查 batch/token 预算、优化器布局、attention 和 expert shard 条件。

## 容量评估与调参顺序

先统计参数/梯度/优化器常驻、激活与保存张量、FSDP gather、MoE/通信 scratch、graph pool、数据与 checkpoint 暂存的峰值，再测最差 rank 的 headroom。不能仅用参数量估显存，也不能把 allocatable HBM 全部占满视作合理方案。

1. 固定模型语义与 global token 预算，用真实短跑校准容量；可放下全参时优先全参，不先习惯性缩维。
2. 用 DP shard/replicate、TP/CP/EP/PP 匹配节点与互联；增加分片通常省常驻内存但增加通信、重算或调度开销。
3. 在不改变有效 batch 语义下调 microbatch 与 accumulation，观察 GEMM 形状、CPU 调度、PP bubble 与显存峰值。
4. 分别试 reshard、预取、AC、offload 等候选；记录峰值发生在哪个阶段，而不是只比稳态平均 memory。
5. 稳定后继续扩 DP 域；记录吞吐缩放、并行负载、阶段 loss 和 checkpoint/recovery，不能把更多卡本身当作优化通过。

## FSDP2 与 HSDP

FSDP2 以 DTensor 管理分片，配合 meta 初始化后物化，保留参数 FQN。`reshard_after_forward=True` 可降低驻留，但 backward 需要重新 gather；False 则可能跨微批复用权重，代价是更高显存。HSDP 分片域和复制域的梯度通信不同，梯度累积时 replica all-reduce 的时机要核对。

CP 并不意味着每个子模块都按 CP 同样处理。视觉等 CP-invariant 参数可能排除 CP shard 轴；把所有子模块统一切分会造成布局、精度或多余通信问题。混合模型应对照当前 `resolve_fsdp_mesh` / sparse mesh 和测试。

PR #5266 的上游实验也提醒：视觉编码器减少 FSDP 通信后，指定 CP2/CP4 测试的整段 step 仍变慢，峰值显存增加，部分 BF16 归约/clip 数值发生变化；作者未验证完整训练收敛。不能把“通信量减少”摘要成“训练更快且精度不变”。

## PP：驻留、提前 unshard 与在途发送

`pp_max_unsharded_active_stages` 控制可同时保持 unsharded 的 stage 数；`pp_num_unshard_lookahead_factor` 控制何时提前准备后续 stage。后者主要改变通信发起时刻，不代表减少 collective 次数。auto/full 或逐 PP rank 的值应结合 schedule、链路和 headroom 测量。

`pipeline_parallel_max_outstanding_sends` 控制多 stage 调度中的在途发送 action 数，单位不是字节或 microbatch。提前 wait 可降低通信暂存峰值，也可能减少 overlap；必须验证依赖顺序和真实 step time。稳定 ModuleDict/FQN 有利于不同 PP 分割的 checkpoint 对齐；seed checkpoint 可用于跨并行基线，但创建它也受真实容量约束。

## 区域重算：省什么、重新算什么

当前 `torch_remat` 路径按带名称的 region 而非旧的逐 op 开关组织：

- `FullAC` 基本选择全部重算，但保留实现定义的必要区域，不能理解为所有状态都可重复执行。
- `RegionAC` 用 save/recompute pattern 控制；recompute pattern 优先。模型实际标记了哪些 region，应使用 trace 核实，拼错或未匹配 pattern 不能算策略生效。
- `SelectiveAC` 默认保存主要区域并重算如 routed experts 的 w13 路径，减少大激活保留；不是任意 attention/GEMM 都自动采用同样策略。
- routing 决策、统计状态、dropout RNG、跨 region 的 view/消费者和通信 replay 均有边界。重复执行有副作用的区域可能改变路由或计数；DeepEP 重算还需确定性排序/通信一致性。

重算是显存、额外 FLOPs 与通信的交换。上限建模时包含实际重算和量化开销；比较 loss、吞吐及峰值，保留能回到原 recipe 的开关。

## 固定证据与使用边界

本页以官方主线 `65aaaa960698ab5d6e98c874177b41b9c30e9c58` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/distributed/PARALLELISM_CONTEXT.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/distributed/PARALLELISM_CONTEXT.md)
- [torchtitan/distributed/parallelism_context.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/distributed/parallelism_context.py)
- [torchtitan/config/parallelism.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/config/parallelism.py)
- [torchtitan/distributed/fsdp.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/distributed/fsdp.py)
- [torchtitan/distributed/PIPELINE_PARALLEL.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/distributed/PIPELINE_PARALLEL.md)
- [torchtitan/distributed/pipeline_parallel.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/distributed/pipeline_parallel.py)
- [torchtitan/distributed/REMAT.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/distributed/REMAT.md)
- [torchtitan/distributed/activation_checkpoint.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/distributed/activation_checkpoint.py)
- [torchtitan/config/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/config/README.md)

- [PR #5101：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5101.md)
- [PR #5280：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5280.md)
- [PR #5266：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5266.md)

## 当前主线补充：EMA offload 初始化也有峰值

[PR #5282](https://github.com/pytorch/torchtitan/pull/5282) 改变 CPU-offloaded EMA 的创建位置：`_EMAParamOptimizer(..., offload_to_cpu=True)` 直接对 local shard 在 pinned CPU storage 建副本，避免先完整 clone 到 GPU 再搬到 CPU 的初始化峰值。参数与匹配 buffer 都传入同一配置；普通非 offload 路径继续 clone。

`EMA._materialize_dtensor` 在保存/加载时按当前活跃参数的 sharding spec 重建 DTensor，用于 DCP 重分片；不能缓存旧 world size 的 spec。CPU offload 仍有 pinned host 内存、DMA、更新/保存同步和临时 GPU staging 的代价。容量评估需要分别看初始化、稳态 step、EMA更新与保存恢复峰值，而不是只看几个稳定 step 的 allocated。

验证应覆盖 offload 开关、参数和 buffers、多步 EMA 数值、checkpoint round trip 以及并行规模变化；本页仅审查当前源码，没有执行该测试矩阵。不要用这个实现去推断所有 optimizer state 都自动采用同一 offload 策略。

- [torchtitan/components/optim/ema.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/components/optim/ema.py)