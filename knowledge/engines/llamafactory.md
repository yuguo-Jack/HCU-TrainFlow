---
id: engines/llamafactory
title: LLaMA-Factory：配置驱动微调与数据语义
engine: llamafactory
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: hiyouga-llama-factory
  path: README.md
  commit: ce9dc9e072f80fa3abe0989d4ab90da25f083438
  sha256: 2d61d3ee9a0b7a099800b17b0be7a8ef034ed9b08f43cb32bdac17642cc823dd
- source: hiyouga-llama-factory
  path: pyproject.toml
  commit: ce9dc9e072f80fa3abe0989d4ab90da25f083438
  sha256: d2d044de25f84d319338de30299437ee882650e2a998af50f617bfbb5964becf
---

# LLaMA-Factory：配置驱动微调与数据语义

## 目录与配置

`src/` 为 Python 实现，`examples/` 为训练配置，`data/` 为数据示例/登记，`tests/` 与 `tests_v1/` 存放不同范围回归，`requirements/` 区分可选依赖。先确定执行的入口/版本与 YAML，而不是只保存一条启动命令。

## 环境与跑通

从目标分支官方 quickstart 选择与任务相同的训练方法，检查实际 `llamafactory-cli` 的 help、解释器和模块路径。使用 HCU 版本的底层 torch/attention/通信能力，单独处理 bitsandbytes 等平台特定依赖。每个可选功能要证明 candidate 真正分发，拒绝无提示 fallback。

## 测试与优化

模板、special token、截断、padding、packing、prompt loss 和 response mask 先对齐；否则速度改变可能来自少算 token。按数据处理、forward/backward、optimizer、保存阶段抓取剖面。全参、LoRA 与量化微调分别保留数值/内存基线，不能跨方法复用 loss 门槛。

本版是入口和数据/性能检查导航，未逐模型验证。针对新模型补配置消费位置、layer/attention backend、梯度与保存恢复专题后，才能称为该模型的完整代码 Wiki。

## 固定源码与更新范围

- [README.md](https://github.com/hiyouga/LLaMA-Factory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/README.md)
- [pyproject.toml](https://github.com/hiyouga/LLaMA-Factory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/pyproject.toml)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
