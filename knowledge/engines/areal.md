---
id: engines/areal
title: AReaL：异步 RL 的版本与恢复状态
engine: areal
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: inclusionai-areal
  path: README.md
  commit: ab56dfc317a87b59ce07c8d7fdfb7292fbcefc94
  sha256: bfa381a165d6bacd068f027bf3b66761cf549c3a40f9e7098e68e0ec382b66c8
- source: inclusionai-areal
  path: docs/en/tutorial/quickstart.md
  commit: ab56dfc317a87b59ce07c8d7fdfb7292fbcefc94
  sha256: f92e909bff175a2589618286cb1bd6b88ddec754ac8f5d4041ad5d696c6a04c0
- source: inclusionai-areal
  path: areal/v2/cli/cli.py
  commit: ab56dfc317a87b59ce07c8d7fdfb7292fbcefc94
  sha256: f8e7609425659b31dc39c6d59e45b1fdfacbe6ad2a8d593fdee5f4dfd0a95894
---

# AReaL：异步 RL 的版本与恢复状态

## 工程入口

`areal/` 是实现，`examples/` 和 `docs/` 提供算法/模型配方，`tests/`、`benchmark/` 分别承接回归与性能。当前源码有 v2 CLI；应从所选 example 的启动入口一路确认真实执行路径，不能以旧教程参数解释新 CLI。

## 环境适配

README 的官方安装示例包含 CUDA 专用依赖以及不同推理后端的配置组合，HCU 必须使用匹配替代栈，并固定训练/推理引擎和网络传输版本。先做最小合法数据流和梯度更新，再放开异步并发。

## 优化与质量

异步训练记录采样时 policy version、权重传播延迟、队列深度、样本年龄和丢弃/重试策略。吞吐提升不能靠无意放宽 staleness 或改变有效样本集合获得。性能报告分训练、生成、reward、同步、等待，并保留与质量指标的关系。

## 恢复

检查训练 checkpoint、在途样本、队列 ack、rollout session、policy 版本的共同恢复边界。重复采样和重复更新都应被识别。此版为 quickstart/CLI 层的可追溯导航；具体算法和分布式调度源码需按任务继续扩展。

## 固定源码与更新范围

- [README.md](https://github.com/inclusionAI/AReaL/blob/ab56dfc317a87b59ce07c8d7fdfb7292fbcefc94/README.md)
- [docs/en/tutorial/quickstart.md](https://github.com/inclusionAI/AReaL/blob/ab56dfc317a87b59ce07c8d7fdfb7292fbcefc94/docs/en/tutorial/quickstart.md)
- [areal/v2/cli/cli.py](https://github.com/inclusionAI/AReaL/blob/ab56dfc317a87b59ce07c8d7fdfb7292fbcefc94/areal/v2/cli/cli.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
