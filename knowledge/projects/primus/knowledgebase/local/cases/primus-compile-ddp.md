---
id: ecosystem/cases/primus-compile-ddp
title: 案例：参数 gather overlap 与编译区域的 hook 边界
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
  path: primus/core/patches/patch_runner.py
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 330529f72986ec1d291222b0c3fbf556863ca03b7e72c986cba1f2ac081a645e
- source: amd-agi-primus
  path: primus/core/runtime/train_runtime.py
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 63c969944700b1d63d2393a9e96cb79ff373f25541f6f1e1fef060bdeb57de1c
---

# 案例：参数 gather overlap 与编译区域的 hook 边界

## 问题与瓶颈

本轮固定源码仍包含 distributed optimizer、parameter gather overlap、torch.compile 联用时的 DDP hook 补丁。子模块 pre-hook 的 collective 与 Python/bucket 状态被编译追踪，可能造成 graph break 或错误同步边界。案例对“已证实这类问题”的目标路径有效，不是所有 compile 训练的默认步骤。

## 为什么这样改与实现位置

`ddp_overlap_compile_patches.py` 在 `before_train` 放置两层 hook：Transformer layer 在 compiled forward 外的 eager 包装触发并递归处理参数；其他模块非递归处理。启停 hook、graph capture 跳过和参数所属 bucket 一并考虑。它在编译边界外维持参数可读依赖，从而让 forward 中的计算更适合编译。

上一版“失败会抛错，避免无声继续”的表述不够完整：patch 函数会 raise，**通用 runner 默认记录异常，本轮 runtime 未要求传播**。因此训练继续不证明补丁已成功；必须检查成功日志/实际 hook 与性能 trace。[机制专题](../topics/primus-compile-overlap.md)说明 TE TP overlap 与此补丁的区别。

## 条件、验证与证据

检查实际 HCU 分支有同类问题、DDP API 匹配、condition 命中，保留最终配置。按 compile/overlap 2×2、多个 microbatch、共享参数、checkpoint/eval、capture 验证 forward、dgrad/wgrad、参数更新与 gather 完成时机。性能指标为 graph break、CPU launch、暴露通信和稳态步时；单纯编译成功不够。

本次为源码复核，没有新增 HCU 性能或 loss 数据。新的 Primus main 仍保留机制，案例继续适用但需按部署 Core/TE 重新确认，不将历史说明套到任意新版本。

## 失败与回退

恢复原 hook，分别禁用 compile/overlap 缩小差异；不要混合半个新生命周期与旧 bucket 方法。官方加入等价能力后先完成同矩阵回归再移除 HCU patch。更新联动[总览](../overview/engineering-guide.md)、专题和受影响的测试/Skill。

## 固定证据与复核范围

- [primus/backends/megatron/patches/ddp_overlap_compile_patches.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/primus/backends/megatron/patches/ddp_overlap_compile_patches.py)
- [primus/core/patches/patch_runner.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/primus/core/patches/patch_runner.py)
- [primus/core/runtime/train_runtime.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/primus/core/runtime/train_runtime.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
