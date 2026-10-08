---
id: official-megatron-wiki/training-and-loss
title: 训练循环、loss 和优化器更新的证据链
engine: megatron
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-megatron-lm
  path: pretrain_gpt.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: a21cb1d38e5aa722ccdf51d5885e077681e30f02c4699dd279127695c6ab1fa0
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 9df18e0c6002c0ee7c2f595d32e0bcb04dd4363e35fc0c9b8da206e8a2c1dfe8
- source: nvidia-megatron-lm
  path: megatron/core/pipeline_parallel/schedules.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 3719d850b8822e221f30472881b8802b8f88ce02167856130fae97849d1d91ee
---

# 训练循环、loss 和优化器更新的证据链

## 阅读链路

`pretrain_gpt.py` 提供 batch、forward 和 loss 回调；training 层驱动循环，Core schedule 组织微批的 forward/backward。报告中区分 token 加权 loss、微批 mean、跨 rank reduce 后指标和日志平滑值。聚合不同会产生看似精度偏差。

## 阶段验证契约

初始可信基线保持不可覆盖。冻结样本顺序/tokenization、loss mask、seed、优化器/LR/精度路径、梯度累积以及比较窗口。每个优化小迭代做局部输出、梯度、dispatch 和短性能回归；到一个稳定阶段再做较长 loss 比较，无需每次改动长训。

`quality-check` 对齐步骤与样本指纹，拒绝空执行、必需测试跳过、候选未调用、非有限 loss 和过短窗口。容差由模型和数值路径给出，工具不内置“所有模型通用”的容差。比较通过只覆盖冻结窗口，不自动证明长期收敛。

## 低精度与失败恢复

检查 cast/accumulate/reduce dtype、动态 scaling、溢出跳步、FP8 缓存和重算时 RNG。优化器更新应与参数版本、梯度同步完成状态对应。恢复后除了 step 增长，还需证明模型、优化器、RNG 与数据游标来自一致 checkpoint。

## 固定源码与更新范围

- [pretrain_gpt.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/pretrain_gpt.py)
- [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/training/training.py)
- [megatron/core/pipeline_parallel/schedules.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/core/pipeline_parallel/schedules.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
