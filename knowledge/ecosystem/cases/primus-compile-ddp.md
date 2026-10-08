---
id: ecosystem/cases/primus-compile-ddp
title: 案例：参数 gather overlap 与编译区域的 hook 边界
engine: primus
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: amd-agi-primus
  path: primus/backends/megatron/patches/ddp_overlap_compile_patches.py
  commit: 0f996490ad1bf53f0756dc631e195c94738a6341
  sha256: 37b37010af2d8580fa8367e3037334388bee85ebfb6e6b11c3e3ba44f5ec86e2
---

# 案例：参数 gather overlap 与编译区域的 hook 边界

## 问题与机制

本提交 Primus 的补丁针对 distributed optimizer、parameter gather overlap 和 torch.compile 同时启用的组合。原本子模块 pre-hook 可能把带 collective 副作用的逻辑带入编译追踪。

补丁将 hook 分两层：Transformer layer 在编译 forward 外部 eager 包装处触发，递归处理其参数；其余模块仍使用非递归 hook。它还覆盖启停 hook 生命周期，并跳过 graph capturing 情形。失败会抛错，避免无声继续执行未正确改写的路径。

## HCU 复用判断

先证明实际 HCU 分支有同类 graph break 或错误，而且当前 DDP API 仍匹配。不能无条件 monkey-patch 所有版本；应尽量在目标工程的可维护扩展点实现。记录参数所属 bucket、同步完成时机、启停循环和模块共享参数。

## 验证与回退

比较无 compile/无 overlap、compile only、overlap only、两者同时启用四种情况。检查 forward/backward、参数更新、不同 microbatch、checkpoint/eval 切换以及真实分发。性能看 graph break 数、CPU launch、暴露通信和步时间，不能只看编译成功。

回退为撤销这一补丁并恢复原路径；若禁用 compile 才能恢复正确性，记录其性能代价。当前页是源码机制案例，没有 HCU 加速数字。

## 固定源码与更新范围

- [primus/backends/megatron/patches/ddp_overlap_compile_patches.py](https://github.com/AMD-AGI/Primus/blob/0f996490ad1bf53f0756dc631e195c94738a6341/primus/backends/megatron/patches/ddp_overlap_compile_patches.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
