---
id: project-deepspeed
title: deepspeed 官方工程 Wiki 导航
kind: source-map
review_level: navigation-only
runtime_validated: false
sources: []
generated_body_sha256: d7b104462a9bbf000a3740cc4641014a6a0e8e686e145a9aa1b8841c719263d7
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
- [官方文档原文](knowledgebase/upstream/docs/)
- [PR 描述、review 与固定代码](knowledgebase/upstream/prs/)
- [完整源码路径](knowledgebase/upstream/source-map/)

原始 PR JSON 集中保存在 [evidence/prs](../../evidence/prs/)；每篇 PR 原文页链接其固定原件。局部 Wiki 不重复维护 HCU 仓，参见[知识分工](../../../docs/knowledge-architecture.md#hcu-仓库知识的分工)。
