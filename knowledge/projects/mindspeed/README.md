---
id: project-mindspeed
title: mindspeed 官方工程 Wiki 导航
kind: source-map
review_level: navigation-only
runtime_validated: false
sources: []
generated_body_sha256: 4bbddd12b3e0f9b4cb2cf5ad4fe3f30194be4adf3c83a0a4c0c52d49d4eb76ac
---

# mindspeed

从[工程总览：MindSpeed 与 MindSpeed-LLM：特性底座、模型训练和恢复](knowledgebase/local/overview/engineering-guide.md)进入。

## 整理后的知识

### 定位与代码地图

- [MindSpeed 与 MindSpeed-LLM：特性底座、模型训练和恢复](knowledgebase/local/overview/engineering-guide.md)

### 机制专题

- [MindSpeed：Ring、Hybrid 与 KV All-Gather 上下文并行](knowledgebase/local/topics/mindspeed-context-parallel.md)
- [MindSpeed-LLM：ChunkLoss 的 Logit 显存、梯度与入口区别](knowledgebase/local/topics/mindspeed-llm-chunk-loss.md)
- [MindSpeed-LLM：Replica Optimizer、高可用与弹性恢复](knowledgebase/local/topics/mindspeed-llm-high-availability.md)
- [MindSpeed：MoE all-to-all 重叠、共享专家与 Zero Memory](knowledgebase/local/topics/mindspeed-moe-overlap-memory.md)

### 优化案例

- [案例：MoE overlap 的参数约束就是正确性契约](knowledgebase/local/cases/mindspeed-ep-constraints.md)

## 上游资料

- [ascend-mindspeed](https://github.com/Ascend/MindSpeed)
- [ascend-mindspeed-llm](https://github.com/Ascend/MindSpeed-LLM)
- [官方文档原文](knowledgebase/upstream/docs/)
- [完整源码路径](knowledgebase/upstream/source-map/)

原始 PR JSON 集中保存在 [evidence/prs](../../evidence/prs/)；每篇 PR 原文页链接其固定原件。局部 Wiki 不重复维护 HCU 仓，参见[知识分工](../../../docs/knowledge-architecture.md#hcu-仓库知识的分工)。
