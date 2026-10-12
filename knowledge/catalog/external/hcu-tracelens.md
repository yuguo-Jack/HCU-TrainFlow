---
id: tooling/hcu-tracelens
title: HCU TraceLens 集成与使用边界
kind: external-reference
engine: tooling
stages:
- adapt
- optimize
- fault-tolerance
owner: external
hcu_project: null
search_skill: hcu-knowledge-search
runtime_validated: false
sources: []
---

# HCU TraceLens 集成与使用边界

[官方 AMD TraceLens Wiki](../../projects/tracelens/README.md)维护上游分析机制。HCU 定制工具的使用契约、命令、适用范围与已验证边界由 [TrainFlow 分析接口](../../../docs/tracelens-analysis.md)和[依赖安装](../../../docs/integrations.md)维护，固定实现见 `thirdparty/manifest.json` 指向的 fork。

HCU 硬件、profiler 和底层库问题交给 `$hcu-knowledge-search`。目前不假定大库已有该定制 fork 的完整仓库 Wiki；必要时直接阅读实际锁定的工具源码和 fork 文档，不在这里再采集一套 HCU 源码/PR 知识库。

## 后续维护

更新时读取[外部知识与用法关联](../external-knowledge.json)，核对大库结论和实际依赖；接口、输出、单位或副作用变化时复核其 `targets` 对应文档、Skill 和解析器。普通查询仅留任务缓存，TrainFlow 更新不自动更新 HCU-Knowledge，也不将 HCU 仓加入本地官方来源。
