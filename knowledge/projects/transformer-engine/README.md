---
id: project-transformer-engine
title: transformer-engine 官方工程 Wiki 导航
kind: source-map
review_level: navigation-only
runtime_validated: false
sources: []
generated_body_sha256: 2551be64eea436b17efa7781333b0915ea22908ca348e3c477ac9a99e335f06a
---

# transformer-engine

从[工程总览：Transformer Engine 官方工程：定位、目录与训练调用链](knowledgebase/local/overview/overview.md)进入。

## 整理后的知识

### 定位与代码地图

- [Transformer Engine 官方工程：定位、目录与训练调用链](knowledgebase/local/overview/overview.md)

### 安装、运行与测试

- [TE 安装、运行、单测与 HCU 环境接入](knowledgebase/local/guides/build-run-test.md)

### 机制专题

- [TE Attention：后端选择、cuDNN 调用与训练精度契约](knowledgebase/local/topics/attention.md)
- [TE 融合与形状级分析：OperationFuser 和 GEMM 教程](knowledgebase/local/topics/fusion-and-profiling.md)
- [TE 并行与显存：Userbuffers、CP、Graph 和 Offload](knowledgebase/local/topics/overlap-and-memory.md)
- [TE 低精度训练：recipe、amax、权重缓存与反向状态](knowledgebase/local/topics/precision-and-cache.md)

### 优化案例

- [案例：单 group NVFP4 MLP 的权重视图为什么不能照搬 MXFP8](knowledgebase/local/cases/grouped-mlp-weight-layout.md)
- [案例：RMSNorm 与 MXFP8 量化融合的调用、布局和数值边界](knowledgebase/local/cases/rmsnorm-mxfp8-fusion.md)

### 版本与更新

- [TE 官方教程索引与版本更新方法](knowledgebase/local/changes/tutorials-and-update.md)

## 上游资料

- [nvidia-transformerengine](https://github.com/NVIDIA/TransformerEngine)
- [nvidia-transformerengine-docs](https://docs.nvidia.com/deeplearning/transformer-engine/)
- [选定官方文档原文](knowledgebase/upstream/docs/)
- [已选定 PR 与固定证据](knowledgebase/upstream/prs/)
- [固定源码阅读入口](knowledgebase/upstream/source-map/)

普通 PR 通过官方原页联搜，正文、代码和讨论按需读取；已选定页面链接固定原件，历史材料由既有固定 Git 基线按需恢复。局部 Wiki 不重复维护 HCU 仓，参见[知识分工](../../../docs/knowledge-architecture.md#hcu-仓库知识的分工)。
