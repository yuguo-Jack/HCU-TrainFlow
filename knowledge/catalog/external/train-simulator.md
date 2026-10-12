---
id: tooling/train-simulator
title: HCU Train Simulator 容量与并行估算
kind: external-reference
engine: tooling
stages:
- adapt
- optimize
- fault-tolerance
owner: external
hcu_project: train-simulator
search_skill: hcu-knowledge-search
runtime_validated: false
sources: []
---

# HCU Train Simulator 容量与并行估算

源码、模型注册、构建、命令与 PR 由 **HCU-Knowledge 的 `train-simulator` 项目**维护。使用 `$hcu-knowledge-search` 查询 `hcu-train-simulator capacity memory search solve`，确认实际版本、模型与硬件配置。

TrainFlow 的[容量规划与并行实验](../../../docs/practices/capacity-and-parallel-experiments.md)说明何时估算、如何用最差 rank 显存和真实短跑校准，以及何时允许缩层；这里只保留流程方法。

## 后续维护

更新时读取[外部知识与用法关联](../external-knowledge.json)，核对大库结论和实际依赖；接口、输出、单位或副作用变化时复核其 `targets` 对应文档、Skill 和解析器。普通查询仅留任务缓存，TrainFlow 更新不自动更新 HCU-Knowledge，也不将 HCU 仓加入本地官方来源。
