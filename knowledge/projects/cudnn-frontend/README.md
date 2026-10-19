---
id: project-cudnn-frontend
title: cudnn-frontend 官方工程 Wiki 导航
kind: source-map
review_level: navigation-only
runtime_validated: false
sources: []
generated_body_sha256: d93bad190e593b54a89e7f76bcdcfb34eabcbb0b9c3ab2d08d4fb27c311cde00
---

# cudnn-frontend

从[工程总览：cuDNN Frontend 官方工程：Graph、开放 Kernel 与训练调用链](knowledgebase/local/overview/overview.md)进入。

## 整理后的知识

### 定位与代码地图

- [cuDNN Frontend 官方工程：Graph、开放 Kernel 与训练调用链](knowledgebase/local/overview/overview.md)

### 安装、运行与测试

- [cuDNN Frontend 编译安装、运行示例与测试路线](knowledgebase/local/guides/build-run-test.md)

### 机制专题

- [cuDNN SDPA 训练：Forward、Backward、Stats 与布局](knowledgebase/local/topics/attention.md)
- [cuDNN Flex Attention：区间 MaskPlan、反向和复用成本](knowledgebase/local/topics/flex-attention-plans.md)
- [cuDNN Graph、执行计划、Workspace 与动态形状缓存](knowledgebase/local/topics/graph-and-plans.md)
- [cuDNN 开放 Kernel：MoE 融合、FROST 与稀疏 Attention](knowledgebase/local/topics/open-kernel-fusions.md)

### 优化案例

- [案例：cuDNN Kernel 不慢，模型却被构图和 Host 调度拖慢](knowledgebase/local/cases/host-dispatch-and-cache.md)

### 版本与更新

- [cuDNN Frontend 官方教程、源码实例与更新索引](knowledgebase/local/changes/tutorials-and-update.md)

## 上游资料

- [nvidia-cudnn-frontend](https://github.com/NVIDIA/cudnn-frontend)
- [nvidia-cudnn-frontend-docs](https://docs.nvidia.com/cudnn/)
- [官方文档原文](knowledgebase/upstream/docs/)
- [PR 描述、review 与固定代码](knowledgebase/upstream/prs/)
- [完整源码路径](knowledgebase/upstream/source-map/)

原始 PR JSON 集中保存在 [evidence/prs](../../evidence/prs/)；每篇 PR 原文页链接其固定原件。局部 Wiki 不重复维护 HCU 仓，参见[知识分工](../../../docs/knowledge-architecture.md#hcu-仓库知识的分工)。
