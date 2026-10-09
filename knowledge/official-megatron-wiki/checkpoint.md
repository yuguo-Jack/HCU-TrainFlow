---
id: official-megatron-wiki/checkpoint
title: 分布式 checkpoint、数据游标与恢复验收
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
  path: megatron/core/dist_checkpointing/serialization.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 2f3c6b9f11c3919ce6579ef75dd877e351f09c1fc54b8c025f7c95fc4f2fcf57
- source: nvidia-megatron-lm
  path: megatron/training/checkpointing.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: bc03641fb7232e646088d3ffe0d4421b78f1a9a03a2296ecddd471fba3256b2d
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 9df18e0c6002c0ee7c2f595d32e0bcb04dd4363e35fc0c9b8da206e8a2c1dfe8
---

# 分布式 checkpoint、数据游标与恢复验收

## 两层责任

training/checkpointing 处理训练状态；Core serialization 处理分片和后端。排障从实际格式、异步保存是否完成、metadata 和 shard 完整性入手，再检查模型/优化器布局，而不是看到 checkpoint 目录存在就认定可恢复。

## 恢复记录

保留 checkpoint ID、源提交、并行拓扑、模型与优化器状态、RNG、样本消费位置、学习率 step、写入完成证据。变更 TP/PP/EP 或参数布局时需要受支持的转换策略和恢复小跑；固定目录名不代表布局兼容。

## 长训闭环

远端 watcher 不负责发明另一套重启策略。Cluster Manager 或站点指定工具拥有恢复权；watcher 检测进程退出、进展停滞及恢复超时，记录 incident。恢复成功必须看到 checkpoint 已验证和连续推进样本，不能只以进程重新出现或 first log 为准。

保存期间显存和主存峰值必须列入 headroom，异步保存的后台 worker 也应监测。遇到反复恢复同一步、损坏 shard、步数回退但 attempt 未变化，交由诊断 Skill 收集证据并升级给专家。

## 固定源码与更新范围

- [megatron/core/dist_checkpointing/serialization.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/core/dist_checkpointing/serialization.py)
- [megatron/training/checkpointing.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/training/checkpointing.py)
- [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/training/training.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
