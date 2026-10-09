---
id: official-megatron-wiki/memory
title: 显存生命周期、重算、offload 与 checkpoint 峰值
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
  path: docs/user-guide/features/fine_grained_activation_offloading.md
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 20fd1e02cecb27d05b18ae672ca761583a93471420edd8f3bb3133b100c95a3e
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/distrib_optimizer.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 892589f868b77a8f209bbcc8861521e7e71ddd46665b3dee38871aa580523389
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 9df18e0c6002c0ee7c2f595d32e0bcb04dd4363e35fc0c9b8da206e8a2c1dfe8
---

# 显存生命周期、重算、offload 与 checkpoint 峰值

## 分账

将参数、主权重/优化器状态、梯度、激活、通信 buffer、图池、临时 workspace 与 allocator reserved 分开。观测 steady-state 之外的初始化、第一次 backward、optimizer、保存 checkpoint 和恢复峰值。空闲很少不是优化成功的充分条件。

## 当前实现的阅读重点

官方细粒度 offload 文档把激活输入按模块组管理；offload fraction 是符合条件的组比例，不是字节比例。其图捕获、流事件与可选模块有版本限制，文档内不同图实现的描述需继续到当前代码验证，不能概括成任意图模式均兼容。

training 中参数 gather hooks 会在保存、评估和训练之间切换。若缓存低精度权重或复用梯度 buffer，检查 optimizer step 后是否失效、保存前是否同步、恢复后是否重建。paged stash 一类 overflow/回退机制应追踪实际 runner 和容量参数，不将其当成无条件显存节省开关。

## 优化选择

轻量模块重算可能划算；昂贵模块 offload 则取决于 H2D/D2H、NUMA、主存和并行通信争用。保存张量的 ownership、引用释放、流上的最后使用和重载位置比一张峰值截图更有解释力。每项实验要保留不启用该机制的回退配置，并在阶段 loss 中覆盖 backward、参数更新和 checkpoint 恢复。

## 固定源码与更新范围

- [docs/user-guide/features/fine_grained_activation_offloading.md](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/docs/user-guide/features/fine_grained_activation_offloading.md)
- [megatron/core/optimizer/distrib_optimizer.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/core/optimizer/distrib_optimizer.py)
- [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/training/training.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
