---
id: project-primus
title: primus 官方工程 Wiki 导航
kind: source-map
review_level: navigation-only
runtime_validated: false
sources: []
generated_body_sha256: b2a92a46c9929d650e544004080dd6d0fc3e25f19a4baa65d6861b35fcd2f2a4
---

# primus

从[工程总览：AMD Primus：配置、后端补丁、并行与恢复](knowledgebase/local/overview/engineering-guide.md)进入。

## 整理后的知识

### 定位与代码地图

- [AMD Primus：配置、后端补丁、并行与恢复](knowledgebase/local/overview/engineering-guide.md)

### 机制专题

- [Primus：编译区域、参数 gather 与 TE 通信重叠](knowledgebase/local/topics/primus-compile-overlap.md)
- [Primus：按全局层选择重算、MTP 与低精度状态](knowledgebase/local/topics/primus-recompute-memory.md)

### 优化案例

- [案例：参数 gather overlap 与编译区域的 hook 边界](knowledgebase/local/cases/primus-compile-ddp.md)
- [案例：精确逐层重算及上游源码指纹约束](knowledgebase/local/cases/primus-layer-recompute.md)

## 上游资料

- [amd-agi-primus](https://github.com/AMD-AGI/Primus)
- [官方文档原文](knowledgebase/upstream/docs/)
- [PR 描述、review 与固定代码](knowledgebase/upstream/prs/)
- [完整源码路径](knowledgebase/upstream/source-map/)

原始 PR JSON 集中保存在 [evidence/prs](../../evidence/prs/)；每篇 PR 原文页链接其固定原件。局部 Wiki 不重复维护 HCU 仓，参见[知识分工](../../../docs/knowledge-architecture.md#hcu-仓库知识的分工)。
