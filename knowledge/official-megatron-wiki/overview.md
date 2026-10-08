---
id: official-megatron-wiki/overview
title: Megatron 官方生态：责任边界与阅读路线
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
  path: README.md
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 9da0af3c6ccb7fb9dae98930e369293d5872dce1ca9fc22e506d302a83d5f91f
- source: nvidia-megatron-lm
  path: pretrain_gpt.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: a21cb1d38e5aa722ccdf51d5885e077681e30f02c4699dd279127695c6ab1fa0
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 9df18e0c6002c0ee7c2f595d32e0bcb04dd4363e35fc0c9b8da206e8a2c1dfe8
---

# Megatron 官方生态：责任边界与阅读路线

## 组成和使用边界

Megatron-LM 仓同时包含训练入口及 `megatron/core` 库。不能将 LM 与 Core 的同一次改动登记成两个独立上游。Bridge 是独立仓，负责配方、模型接入和权重转换等集成；Transformer Engine 提供底层模块及低精度实现；Energon 负责可恢复的数据加载。各组件必须锁定兼容版本，不能把每个仓各自最新 HEAD 拼成已验证组合。

## 一次训练的阅读顺序

1. 从任务使用的 recipe 或 `pretrain_gpt.py` 读取模型、数据和 loss 回调。
2. 进入 `megatron/training/training.py` 的初始化、训练循环和 `train_step`，确认优化器、学习率、微批及跳步行为。
3. 进入 Core pipeline schedule，确认实际 fwd/bwd 调度以及损失缩放。
4. 沿模型 layer specification 进入 attention、MLP/MoE、TE 包装与实际 kernel。
5. 最后结合 DDP/optimizer、checkpoint 和数据 loader，检查参数、梯度、样本游标的生命周期。

## 适配任务必须保存

官方基准 SHA、HCU 分支 SHA、用户 patch 哈希、依赖版本、启动参数、环境变量、拓扑、数据指纹及 checkpoint 来源。先跑官方配置可解释的基线，再做 HCU 修改。缩层代理只减少 `num_layers`；代理通过不能代替完整模型的显存和 loss 验证。

## 文档入口

- [Megatron Core 官方开发指南](https://docs.nvidia.com/megatron-core/developer-guide/latest/index.html)：用于查询 API、特性和约束；实际任务仍核对相应版本源码。
- [Megatron-LM releases](https://github.com/NVIDIA/Megatron-LM/releases)：区分已发版、主干及实验分支。
- Roadmap/issue 是意图，合并 PR 是实现候选，实际 HCU 分支已接入且回归通过才是可用能力。不能直接用 roadmap 替代兼容性结论。

## 固定源码与更新范围

- [README.md](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/README.md)
- [pretrain_gpt.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/pretrain_gpt.py)
- [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/training/training.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
