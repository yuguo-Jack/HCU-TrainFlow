---
id: project-deepspeed
title: deepspeed 官方工程 Wiki 导航
kind: source-map
review_level: navigation-only
runtime_validated: false
sources: []
generated_body_sha256: e75ac95d9edbaf8e5c991221621bd81361342368103be4fd63d894fa173ed391
---

# deepspeed

从[工程总览：DeepSpeed：训练引擎、ZeRO、流水线与恢复工程指南](knowledgebase/local/overview/engineering-guide.md)进入。

## 整理后的知识

### 定位与代码地图

- [DeepSpeed：训练引擎、ZeRO、流水线与恢复工程指南](knowledgebase/local/overview/engineering-guide.md)

### 机制专题

- [DeepSpeed Pipeline：1F1B、batch、activation 与 checkpoint](knowledgebase/local/topics/pipeline-schedule-and-checkpoint.md)
- [DeepSpeed ZeRO：分片、参数预取与 offload 生命周期](knowledgebase/local/topics/zero-state-lifecycle.md)

### 优化案例

- [DeepSpeed ZeRO-1/2 offload：梯度所有权与流顺序](knowledgebase/local/cases/deepspeed-offload-lifetime.md)

## 上游资料

- [deepspeedai-deepspeed](https://github.com/deepspeedai/DeepSpeed)
- [选定官方文档原文](knowledgebase/upstream/docs/)
- [已选定 PR 与固定证据](knowledgebase/upstream/prs/)
- [固定源码阅读入口](knowledgebase/upstream/source-map/)

普通 PR 通过官方原页联搜，正文、代码和讨论按需读取；已选定页面链接固定原件，历史材料由既有固定 Git 基线按需恢复。局部 Wiki 不重复维护 HCU 仓，参见[知识分工](../../../docs/knowledge-architecture.md#hcu-仓库知识的分工)。
