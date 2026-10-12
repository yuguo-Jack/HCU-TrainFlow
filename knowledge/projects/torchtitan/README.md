---
id: project-torchtitan
title: torchtitan 官方工程 Wiki 导航
kind: source-map
review_level: navigation-only
runtime_validated: false
sources: []
generated_body_sha256: 13233cb61f9e2ff7d903131902897b87022209823673af89d4a42cd8ed73b483
---

# torchtitan

从[工程总览：TorchTitan 官方工程：定位、能力边界与阅读路线](knowledgebase/local/overview/overview.md)进入。

## 整理后的知识

### 定位与代码地图

- [TorchTitan 官方工程：定位、能力边界与阅读路线](knowledgebase/local/overview/overview.md)
- [TorchTitan 代码目录与问题定位地图](knowledgebase/local/overview/source-map.md)

### 安装、运行与测试

- [TorchTitan 安装、Python 配方、启动与分层测试](knowledgebase/local/guides/build-run-test.md)

### 机制专题

- [TorchTitan Checkpoint、恢复语义与长稳训练](knowledgebase/local/topics/checkpoint-and-stability.md)
- [TorchTitan 局部编译、融合、异步 TP 与 GraphTrainer](knowledgebase/local/topics/compile-fusion-and-communication.md)
- [TorchTitan 模型配方、数据语义与 Kimi/FLUX 适配边界](knowledgebase/local/topics/models-and-data.md)
- [TorchTitan MoE 路由、通信内存与低精度权重生命周期](knowledgebase/local/topics/moe-and-low-precision.md)
- [TorchTitan 并行域、容量、重算与显存生命周期](knowledgebase/local/topics/parallelism-and-memory.md)
- [TorchTitan 性能采集、TraceLens 联动与问题定位](knowledgebase/local/topics/profiling-and-diagnosis.md)
- [TitanRL：训练生成协同、权重同步与精度边界](knowledgebase/local/topics/titanrl.md)
- [TorchTitan 训练循环、有效 token、优化器与数值诊断](knowledgebase/local/topics/training-and-numerics.md)

### 优化案例

- [案例：TorchTitan WGRAD 原地累积的显存收益与梯度所有权](knowledgebase/local/cases/inplace-wgrad-accumulation.md)
- [案例：Kimi Attention Residual 融合很快，模型却未必更快](knowledgebase/local/cases/kimi-attnres-fusion.md)
- [案例：TitanRL 权重同步的训练侧暂存与生成侧峰值](knowledgebase/local/cases/rl-weight-sync-memory.md)

### 版本与更新

- [TorchTitan 官方教程、Release、特性 PR 与持续更新](knowledgebase/local/changes/releases-prs-and-update.md)

## 上游资料

- [pytorch-torchtitan](https://github.com/pytorch/torchtitan)
- [官方文档原文](knowledgebase/upstream/docs/)
- [PR 描述、review 与固定代码](knowledgebase/upstream/prs/)
- [完整源码路径](knowledgebase/upstream/source-map/)

原始 PR JSON 集中保存在 [evidence/prs](../../evidence/prs/)；每篇 PR 原文页链接其固定原件。局部 Wiki 不重复维护 HCU 仓，参见[知识分工](../../../docs/knowledge-architecture.md#hcu-仓库知识的分工)。
