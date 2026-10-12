---
id: ecosystem/cases/primus-layer-recompute
title: 案例：精确逐层重算及上游源码指纹约束
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
  path: primus/backends/megatron/patches/recompute_layer_patches.py
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 5909bb386bf88bdb57d4b0b582db7f218a6fb66365783b2d4b042cb32e996ca4
- source: amd-agi-primus
  path: tests/unit_tests/backends/megatron/test_recompute_layer_patches.py
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 6c3f9d188b4237b6e2b8954840c2803ff63be090e976ad696fbcceb5e90d22e0
---

# 案例：精确逐层重算及上游源码指纹约束

## 问题与瓶颈

少数层决定激活峰值时，统一整段重算可能多付计算。当前 Primus patch 仍按全局 layer ID 选择重算；不指定集合时调用原实现，保留上游已有功能。本轮重读源码及相邻单测，机制继续存在，案例仍有效。

## 实现、依赖与适用条件

`validate_specified_recompute_layers` 检查 ID、full granularity、method 组合与并行条件。wrapper 同时处理 TransformerBlock 与 MTP，decoder 之后的 MTP 层不是同一 local 索引；PP/VPP offset 需按真实模型布局解释。低精度用相应 TE checkpoint/context，普通路径用 tensor-parallel checkpoint，tensor 参数与非 tensor kwargs 的包装不能破坏 autograd/RNG。[机制专题](../topics/primus-recompute-memory.md)展开调用链与显存代价。

单测对上游被包装方法签名/源码指纹的约束用来暴露依赖变化。签名或指纹通过不表示所有模型、FP8/FP4、MTP 和 checkpoint 组合已在 HCU 验证。

## 应做的迁移验证

先验证不选层的完整回退，再逐层、跨 PP/VPP 和 MTP 选择；保存 worst-rank peak allocated/reserved、重算时间、活动微批与吞吐。检查输出、梯度、optimizer step、RNG、低精度缓存、checkpoint 恢复和阶段 loss。选择必须由激活生命周期/峰值证据驱动。

## 回退与更新

还原选择集合或恢复官方方法；配置和 wrapper 一起回退。每次 Core 原函数变化同时重读原方法、wrapper 和测试。如果已采用分支具备等价官方能力并在目标 HCU 验证，再移除补丁。未记录新的实测收益，历史案例保持代码阅读的边界。

## 固定证据与复核范围

- [primus/backends/megatron/patches/recompute_layer_patches.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/primus/backends/megatron/patches/recompute_layer_patches.py)
- [tests/unit_tests/backends/megatron/test_recompute_layer_patches.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/tests/unit_tests/backends/megatron/test_recompute_layer_patches.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
