---
id: ecosystem/cases/primus-layer-recompute
title: 案例：精确逐层重算及上游源码指纹约束
engine: primus
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: amd-agi-primus
  path: primus/backends/megatron/patches/recompute_layer_patches.py
  commit: 0f996490ad1bf53f0756dc631e195c94738a6341
  sha256: 5909bb386bf88bdb57d4b0b582db7f218a6fb66365783b2d4b042cb32e996ca4
- source: amd-agi-primus
  path: tests/unit_tests/backends/megatron/test_recompute_layer_patches.py
  commit: 0f996490ad1bf53f0756dc631e195c94738a6341
  sha256: 6c3f9d188b4237b6e2b8954840c2803ff63be090e976ad696fbcceb5e90d22e0
---

# 案例：精确逐层重算及上游源码指纹约束

## 适用问题

当少数层决定激活峰值时，整段重算可能付出不必要计算。此补丁用全局 layer ID 选择重算对象；不设置选择时委托原实现，减少改变上游其他路径的风险。

## 实现边界

`validate_specified_recompute_layers` 限定 ID 范围、full granularity、method 组合及相关并行约束。MTP 的索引接在 decoder 层之后，有独立处理，不能把它遗漏成“只要 TransformerBlock 改了就够”。测试针对上游被包装函数的签名/源码指纹，以暴露依赖变化。

## 迁移实验

按每层激活生命周期和 step 关键路径选择候选 ID，保存 peak reserved/allocated、重算时间和吞吐，逐步减少无效重算。检查 RNG、FP8/FP4 context、MTP、pipeline layer offset、checkpoint 保存及不选择层时完全回退原逻辑。

## 更新责任

签名未变不保证函数语义没变；每次上游 `_checkpointed_forward` 改动都阅读 wrapper 和原函数。若官方加入等价且在目标 HCU 分支验证通过的能力，再移除补丁并用同组回归证明行为保持。

## 固定源码与更新范围

- [primus/backends/megatron/patches/recompute_layer_patches.py](https://github.com/AMD-AGI/Primus/blob/0f996490ad1bf53f0756dc631e195c94738a6341/primus/backends/megatron/patches/recompute_layer_patches.py)
- [tests/unit_tests/backends/megatron/test_recompute_layer_patches.py](https://github.com/AMD-AGI/Primus/blob/0f996490ad1bf53f0756dc631e195c94738a6341/tests/unit_tests/backends/megatron/test_recompute_layer_patches.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
