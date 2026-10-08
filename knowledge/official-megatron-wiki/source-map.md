---
id: official-megatron-wiki/source-map
title: Megatron 代码目录与问题定位地图
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
  path: megatron/core/parallel_state.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 414ecaf3b1891e8d621e5ec86a80af9d2d313d4393ac11e83832ff4bf7257dd2
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 7fc7af4f3f6fe67a6a1d7f9a7df63c5eaf245bc2cb686ff09a0adc58292daa6a
- source: nvidia-megatron-lm
  path: megatron/training/initialize.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 15c038fdd92d57923389ef8cf004231cad73c21d0fbfb658fa73293ce9dd8ea1
---

# Megatron 代码目录与问题定位地图

## 代码目录

| 入口/目录 | 阅读目的 | 典型问题 |
|---|---|---|
| `pretrain_gpt.py` | batch、forward、loss、数据集构造 | loss mask、packing、样本读取不一致 |
| `megatron/training/` | 参数、初始化、训练循环、日志、保存加载 | 配置未生效、跳步、恢复后样本偏移 |
| `megatron/core/parallel_state.py` | rank 到通信组映射 | TP/PP/CP/EP/DP 组错误、collective 不匹配 |
| `core/pipeline_parallel/` | fwd/bwd schedule 与 P2P | PP 空泡、微批调度和等待 |
| `core/transformer/` | layer 配置及模块组合 | attention/MLP/MoE 分发、重算与融合 |
| `core/extensions/` | 外部库适配 | TE API/数值路径差异 |
| `core/distributed/`、`core/optimizer/` | 梯度/参数通信与状态 | overlap、显存、优化器更新 |
| `core/dist_checkpointing/` | 分片序列化 | checkpoint 不完整、布局转换 |

## 定位方法

先用实际启动日志确认解析后的配置，再搜索字段的消费位置，沿调用到真实实现；仅找到 argparse 定义不证明被使用。保存调用符号、文件、行附近上下文与 SHA。遇到框架 wrapper 时记录包的实际 import 路径，避免看着源码 A 却运行 wheel B。

模块图还应附本任务的替换表：官方模块 → HCU 实现 → dispatch 条件 → 正确性基线。任一分支改变时复核表中引用。调试中可以拉取运行版本对应底层库源码，不能仅凭库名判断行为。

## 固定源码与更新范围

- [pretrain_gpt.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/pretrain_gpt.py)
- [megatron/core/parallel_state.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/core/parallel_state.py)
- [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/core/transformer/transformer_config.py)
- [megatron/training/initialize.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/training/initialize.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
