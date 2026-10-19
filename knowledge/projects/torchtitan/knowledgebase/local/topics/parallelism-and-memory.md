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
reviewed_on: '2026-10-20'
coverage: Curated source chains and official evidence at a fixed main commit; not all models, backends
  or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/distributed/PARALLELISM_CONTEXT.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 7df6f250d92b8a4bf37557a330a571cd4273062fce08a2f3268abfce7ee58916
- source: pytorch-torchtitan
  path: torchtitan/distributed/parallelism_context.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 36d2ff85f47b79e42d1e69567c9a4466f4573340630a4b5b55479cadb85350f1
- source: pytorch-torchtitan
  path: torchtitan/config/parallelism.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 7fd587ef274963ff8171981b3dee2adde352c4401466044ecc05b39fdf834573
- source: pytorch-torchtitan
  path: torchtitan/distributed/fsdp.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 397ee700761af56345048cb0e7ba5b120bbc2b57a94e02aebb1c4c8499b8846a
- source: pytorch-torchtitan
  path: torchtitan/distributed/PIPELINE_PARALLEL.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: c7f4d13d05e0c858f586c431c643e8b5478f9145318e7fdc75fe6df79fded44e
- source: pytorch-torchtitan
  path: torchtitan/distributed/pipeline_parallel.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 1da335028a5e6360ecdcbe554ea0711b43cba0949c10ac912ebd22a7534ec751
- source: pytorch-torchtitan
  path: torchtitan/distributed/REMAT.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 7b419c4cb3e396ad1f6015130afdacf229264b214a18e0610b7bc9ac91097f99
- source: pytorch-torchtitan
  path: torchtitan/distributed/activation_remat.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 4e935605e29f904ad5c5bef1036e265021f42c334a7a17c6d01083040dffc5a7
- source: pytorch-torchtitan
  path: torchtitan/config/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: e62e3776a4dd1c2179b3643d9e611f5a6f53fc972ac16de4588ee96a99a06b9b
- source: pytorch-torchtitan
  path: torchtitan/components/optim/ema.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 8cfa06a39eb1c7d84fbea7d283fc856a485054e599a7168e3c6f1b9e522fe8ff
- source: pytorch-torchtitan
  path: torchtitan/config/configs.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: aaf73beb7efb044ac1978b3edb43b48db256ccd708660880d947bc70e9be3a2c
- source: pytorch-torchtitan
  path: tests/unit_tests/cpu/test_trainer.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 1882d21356427492dcfc7c160f842e6f18fe813fa565066e8b420741139d9d6b
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

- `FullActivationRematConfig` 选择全量重算策略，但仍保留模型以 `recompute=False` 标记的区域，不能理解为所有状态都可重复执行。
- `ActivationRematConfig` 用 save/recompute pattern 控制；recompute pattern 优先。它直接 `apply(model)`，不再 `Config.build()`。模型实际标记了哪些 region，应使用 trace 核实，拼错或未匹配 pattern 不能算策略生效。
- `DefaultActivationRematConfig` 当前保存主要region并重算 `*routed_experts.w13.*`，减少大激活保留；默认pattern可随上游测量变化，需要固定策略时显式列出 `ActivationRematConfig` 的pattern。没有声明region的模型仍会全量重算。
- routing 决策、统计状态、dropout RNG、跨 region 的 view/消费者和通信 replay 均有边界。重复执行有副作用的区域可能改变路由或计数；DeepEP 重算还需确定性排序/通信一致性。

重算是显存、额外 FLOPs 与通信的交换。上限建模时包含实际重算和量化开销；比较 loss、吞吐及峰值，保留能回到原 recipe 的开关。

## 新配置与惰性物化的容量边界

`activation_remat=None` 禁用该策略；当前 dataclass的 `preserve_rng_state` 和 `debug` 必须为False，随机状态通过明确的 RecomputeStateHook管理。saved-tensor offload hook 现在由 `config.apply(model, saved_tensors_hooks=...)` 按block/FQN提供，而非继承旧RegionAC。hook看到checkpoint输入与保存region等不同类型，不能在仍需被forward读取时破坏原张量；该hook组合还受torch_remat编译限制。

`preprocess_microbatch_groups_lazily` 避免一步开始就把所有group搬入设备和构造掩码；PP中每组包含本schedule step的所有microbatch。它要求关闭CUDA graphs且无SDC replay；pageable输入和varlen host同步可能增加等待，收益取决于输入和实际重叠，不能把注释中的某个H100百分比写成通用结论。全局token分母保持原步的值。

当前decoder统一将MoE挂在 `feed_forward`，FSDP按模块真实类型判断稀疏路径，不再按旧 `moe_enabled` 属性；symm-mem dense scope、expert参数和prefetch必须核对新模块树。EMA DTensor初始化新增显式global shape/stride，局部分片的empty_like大小不能替代全局元数据。

## 固定证据与使用边界

本页以官方主线 `a242475253433725f10f39c18f5ccbfdf188e097` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/distributed/PARALLELISM_CONTEXT.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/PARALLELISM_CONTEXT.md)
- [torchtitan/distributed/parallelism_context.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/parallelism_context.py)
- [torchtitan/config/parallelism.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/config/parallelism.py)
- [torchtitan/distributed/fsdp.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/fsdp.py)
- [torchtitan/distributed/PIPELINE_PARALLEL.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/PIPELINE_PARALLEL.md)
- [torchtitan/distributed/pipeline_parallel.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/pipeline_parallel.py)
- [torchtitan/distributed/REMAT.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/REMAT.md)
- [torchtitan/distributed/activation_remat.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/activation_remat.py)
- [torchtitan/config/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/config/README.md)

- [PR #5101：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5101.md)
- [PR #5280：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5280.md)
- [PR #5266：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5266.md)

## 当前主线补充：EMA offload 初始化也有峰值

[PR #5282](https://github.com/pytorch/torchtitan/pull/5282) 改变 CPU-offloaded EMA 的创建位置：`_EMAParamOptimizer(..., offload_to_cpu=True)` 直接对 local shard 在 pinned CPU storage 建副本，避免先完整 clone 到 GPU 再搬到 CPU 的初始化峰值。参数与匹配 buffer 都传入同一配置；普通非 offload 路径继续 clone。

`EMA._materialize_dtensor` 在保存/加载时按当前活跃参数的 sharding spec 重建 DTensor，用于 DCP 重分片；不能缓存旧 world size 的 spec。CPU offload 仍有 pinned host 内存、DMA、更新/保存同步和临时 GPU staging 的代价。容量评估需要分别看初始化、稳态 step、EMA更新与保存恢复峰值，而不是只看几个稳定 step 的 allocated。

验证应覆盖 offload 开关、参数和 buffers、多步 EMA 数值、checkpoint round trip 以及并行规模变化；本页仅审查当前源码，没有执行该测试矩阵。不要用这个实现去推断所有 optimizer state 都自动采用同一 offload 策略。

- [torchtitan/components/optim/ema.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/components/optim/ema.py)

## 本次补充的实现与测试依据

- [torchtitan/config/configs.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/config/configs.py)
- [tests/unit_tests/cpu/test_trainer.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/unit_tests/cpu/test_trainer.py)
