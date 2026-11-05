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
reviewed_on: '2026-11-04'
coverage: frozen source delta and consumer review; unchanged files rechecked; no HCU runtime validation
sources:
- source: amd-agi-primus
  path: primus/backends/megatron/patches/recompute_layer_patches.py
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 5909bb386bf88bdb57d4b0b582db7f218a6fb66365783b2d4b042cb32e996ca4
- source: amd-agi-primus
  path: tests/unit_tests/backends/megatron/test_recompute_layer_patches.py
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 6c3f9d188b4237b6e2b8954840c2803ff63be090e976ad696fbcceb5e90d22e0
- source: amd-agi-primus
  path: primus/backends/megatron/patches/recompute_layer_patches.py
  commit: bab82720d72cadbdfbedcc050c9fb49de3b353be
  sha256: 689372168818ec24bc9147b611aac22b99a45b6e183a1dd5492b5337cb9332c5
- source: amd-agi-primus
  path: tests/unit_tests/backends/megatron/test_recompute_layer_patches.py
  commit: bab82720d72cadbdfbedcc050c9fb49de3b353be
  sha256: 1896030ea03bfcca9811065e63738f4fe828638192dca7a2ae912e2b222e1ebb
- source: amd-agi-primus
  path: primus/backends/megatron/patches/_source_patch_utils.py
  commit: bab82720d72cadbdfbedcc050c9fb49de3b353be
  sha256: b8d4d892ee84b7c24577cc47ddfba6cbea0f571eeafd9d2916b41affa1b548cb
retrieved_on: '2026-11-04'
---

# 案例：精确逐层重算及上游源码指纹约束

## 问题与瓶颈

少数层决定激活峰值时，统一整段重算可能多付计算。当前 Primus patch 仍按全局 layer ID 选择重算；不指定集合时保留原实现控制流。2026-11-04 核对 `bab82720d72cadbdfbedcc050c9fb49de3b353be`：相对历史 `ab8735564c4cc3bb7c0475146057eee8dae4c650`，实现与单测均已变化，新增 Core 模块级重算和新 MTP 签名支持，不能继续只套用旧类方法 wrapper。

## 实现、依赖与适用条件

`validate_specified_recompute_layers` 检查 ID、full granularity、method 组合与并行条件。wrapper 同时处理 TransformerBlock 与 MTP，decoder 之后的 MTP 层不是同一 local 索引；PP/VPP offset 需按真实模型布局解释。decoder 和 MTP 对低精度 checkpoint 的选择并不完全相同；MTP 的 FP4 覆盖不能由 decoder 分支推导。tensor 参数与非 tensor kwargs 的包装不能破坏 autograd/RNG。[机制专题](../topics/primus-recompute-memory.md)展开实际分派与显存代价。

旧 Core 仍包装 `TransformerBlock._checkpointed_forward`；新路径替换 `megatron.core.recompute.checkpointed_forward` 并重绑 `transformer_block` 的导入引用，选层分支使用 `chunk_runner`，FP8/FP4 且输入不需梯度时不 checkpoint。MTP 按原签名有无 `forward_func` 分派。新增单测检查源码 anchor、两个引用与幂等性；旧方法消失时旧签名测试可 skip。运行时源码替换仅检查 anchor 存在，不能由测试存在推导严格唯一性或全部组合支持。签名或指纹通过不表示所有模型、FP8/FP4、MTP 和 checkpoint 组合已在 HCU 验证。

## 应做的迁移验证

先验证不选层的完整回退，再逐层、跨 PP/VPP 和 MTP 选择；保存 worst-rank peak allocated/reserved、重算时间、活动微批与吞吐。检查输出、梯度、optimizer step、RNG、低精度缓存、checkpoint 恢复和阶段 loss。选择必须由激活生命周期/峰值证据驱动。

## 回退与更新

还原选择集合或恢复官方方法；配置和 wrapper 一起回退。每次 Core 原函数变化同时重读原方法、wrapper 和测试。如果已采用分支具备等价官方能力并在目标 HCU 验证，再移除补丁。未记录新的实测收益，历史案例保持代码阅读的边界。

当前实现与测试的固定证据为父仓 `bab82720d72cadbdfbedcc050c9fb49de3b353be`，检索于 2026-11-04；下列 `ab8735564c4cc3bb7c0475146057eee8dae4c650` 链接保留案例起源，当前完整文件与哈希见页首。收益和迁移验证仍没有新增实测。

## 固定证据与复核范围

- [primus/backends/megatron/patches/recompute_layer_patches.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/primus/backends/megatron/patches/recompute_layer_patches.py)
- [tests/unit_tests/backends/megatron/test_recompute_layer_patches.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/tests/unit_tests/backends/megatron/test_recompute_layer_patches.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
