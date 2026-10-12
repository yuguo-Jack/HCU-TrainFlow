---
id: ecosystem/topics/primus-compile-overlap
title: Primus：编译区域、参数 gather 与 TE 通信重叠
engine: primus
kind: authored
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected source, official documentation and related PR reading; no HCU runtime
  validation
sources:
- source: amd-agi-primus
  path: primus/backends/megatron/patches/ddp_overlap_compile_patches.py
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 37b37010af2d8580fa8367e3037334388bee85ebfb6e6b11c3e3ba44f5ec86e2
- source: amd-agi-primus
  path: primus/backends/megatron/patches/te_patches/tp_overlap_patches.py
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 29fdfc204fd8e0e24211a2497bc60b761a2a5162c948047d722524cd501dda55
- source: amd-agi-primus
  path: primus/core/patches/patch_runner.py
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 330529f72986ec1d291222b0c3fbf556863ca03b7e72c986cba1f2ac081a645e
- source: amd-agi-primus
  path: primus/core/runtime/train_runtime.py
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 63c969944700b1d63d2393a9e96cb79ff373f25541f6f1e1fef060bdeb57de1c
- source: amd-agi-primus
  path: tests/unit_tests/megatron/cco/test_tp_overlap.py
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 3529ffe5254d81357d5e3e127be876df752486143fa830b22bc9e52687a5b1a9
---

# Primus：编译区域、参数 gather 与 TE 通信重叠

## 问题和选择依据

distributed optimizer 在 forward 前可能发起/等待参数 all-gather。torch.compile 同时追踪子模块 forward pre-hook 时，collective 副作用、Python 控制流与 bucket 状态可能落入编译区，造成 graph break 或依赖错误。此机制面向这三个条件同时存在的路径，不是“开启 compile 必须改所有 DDP”。先有可复现 graph break 或暴露等待，再考虑它。

## 配置到调用链

`megatron.ddp.overlap_param_gather_compile` 在 `before_train` 注册；条件包含 distributed optimizer、overlap_param_gather、torch_compile.enable，并允许 `disable_ddp_compile_patches` 禁用。wrapper 将 Transformer layer 的 hook 放到 compiled forward 外的 eager 边界、递归处理其参数；非 layer 模块则非递归处理。enable/disable hook 生命周期同样被包装，graph capturing 时跳过不适用的 hook。

这改变的是参数 readiness 的触发位置。应继续读实际 Core DDP bucket completion / finish_param_sync，确认开始 forward 时参数已可读，不能只看 wrapper 返回值。共享参数及多个 microbatch 可能重复触发，checkpoint/eval 切换又会改变 hook 启停，都是组合验证点。

## TE 的 TP overlap 是另一条路径

`tp_overlap_patches.py` 根据实际导入 TE 的版本分为 TE>=2 的 `general_gemm`、`CommOverlap` / `CommOverlapP2P` 与 TE<2 的 gemm/fp8_gemm 入口，替换 workspace / userbuffer helpers。基本条件是 `tp_comm_overlap`；FP8 与 `tp_comm_overlap_rs`、bulk dgrad/wgrad 的某些组合会拒绝走该 patch。参数名出现不能证明使用了目标实现，要看 condition、success 日志和库加载。

TP collective 与 GEMM 分块/stream 协作，减少的是暴露 TP 等待；额外 workspace、buffer、launch 和资源竞争可能使 kernel 变慢。它与 DDP gather/compile patch 解决的问题不同，不能把单个开关认作 DP/TP 全开。Primus TE 适配代码有自己依赖，迁到 HCU 要对应 HCU TE/DTK 与实际 CommOverlap 能力。

## 验证、性能判断与数值

先比较 compile/overlap 的 2×2 组合，在相同输入和并行组下核对输出、dgrad/wgrad、optimizer update、hook 次数、bucket 完成时间及多个 microbatch。再检查 graph break 数、CPU launch、TP/DP 暴露等待和稳态 wall-clock 步时；不要把重叠区两条 stream 时间相加当成收益。

TP 单测可从 `tests/unit_tests/megatron/cco/test_tp_overlap.py` 进入，测试依赖 GPU/TE 不能在未加载实现时以 skip 作 pass。进阶组合包括低精度、shared parameter、checkpoint/eval、capture/非 capture、pipeline。阶段 loss 接在数值可信的局部回归之后。

## 失败、回退与更新

patch 函数内部异常会 raise，但通用 runner 默认记录并继续；当前 runtime 没有传 `stop_on_error=True`。因此优化验收必须明确 patch 生效，而非以训练仍在跑证明生效。回退应恢复原 hook 与 TE 入口，分别禁用 compile 或 overlap 定位最小差异，记录步时代价。Core/TE 符号、调用阶段或 patch 条件变化时，联动[总览](../overview/engineering-guide.md)与[案例](../cases/primus-compile-ddp.md)。

## 固定证据与复核范围

- [primus/backends/megatron/patches/ddp_overlap_compile_patches.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/primus/backends/megatron/patches/ddp_overlap_compile_patches.py)
- [primus/backends/megatron/patches/te_patches/tp_overlap_patches.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/primus/backends/megatron/patches/te_patches/tp_overlap_patches.py)
- [primus/core/patches/patch_runner.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/primus/core/patches/patch_runner.py)
- [primus/core/runtime/train_runtime.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/primus/core/runtime/train_runtime.py)
- [tests/unit_tests/megatron/cco/test_tp_overlap.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/tests/unit_tests/megatron/cco/test_tp_overlap.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
