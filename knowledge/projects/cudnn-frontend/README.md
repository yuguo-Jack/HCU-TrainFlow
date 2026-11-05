---
id: project-cudnn-frontend
title: cudnn-frontend 官方工程 Wiki 导航
kind: source-map
review_level: navigation-only
runtime_validated: false
sources: []
generated_body_sha256: acdcff8b39d5fad37b5a86c08bd9e9cbd3ac673646e6151d23817a0c8fe9aa6a
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
- [选定官方文档原文](knowledgebase/upstream/docs/)
- [已选定 PR 与固定证据](knowledgebase/upstream/prs/)
- [固定源码阅读入口](knowledgebase/upstream/source-map/)

普通 PR 通过官方原页联搜，正文、代码和讨论按需读取；已选定页面链接固定原件，历史材料由既有固定 Git 基线按需恢复。局部 Wiki 不重复维护 HCU 仓，参见[知识分工](../../../docs/knowledge-architecture.md#hcu-仓库知识的分工)。
