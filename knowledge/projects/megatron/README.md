---
id: project-megatron
title: megatron 官方工程 Wiki 导航
kind: source-map
review_level: navigation-only
runtime_validated: false
sources: []
generated_body_sha256: dcfd78ffe73d47d5bd815b9d9b4c45739ba10c89e074dd4d80d4b57ea1ab2ff1
---

# megatron

从[工程总览：Megatron 官方生态：职责、完整阅读路线与版本边界](knowledgebase/local/overview/overview.md)进入。

## 整理后的知识

### 定位与代码地图

- [Megatron LM/Core：从训练入口到并行、MoE 与内存的工程地图](knowledgebase/local/overview/engineering-guide.md)
- [Megatron 官方生态：职责、完整阅读路线与版本边界](knowledgebase/local/overview/overview.md)
- [Megatron 代码目录：从配置、训练步到计算和恢复](knowledgebase/local/overview/source-map.md)

### 安装、运行与测试

- [Megatron 安装、模型配置、数据、运行与分层测试](knowledgebase/local/guides/build-run-test.md)

### 机制专题

- [Megatron checkpoint：分片、异步完成、数值状态与恢复](knowledgebase/local/topics/checkpoint.md)
- [Megatron 显存生命周期：状态分片、重算、offload与Paged Stash](knowledgebase/local/topics/memory.md)
- [Megatron MoE：路由、dispatcher、grouped GEMM与容量控制](knowledgebase/local/topics/moe.md)
- [Megatron 通信重叠：DP bucket、TP、PP与EP的依赖和限制](knowledgebase/local/topics/overlap.md)
- [并行域、微批与 rank 采样](knowledgebase/local/topics/parallelism.md)
- [训练 profiler 采样与 TraceLens 联动](knowledgebase/local/topics/profiling.md)
- [Megatron 训练步：数据、loss 归一化、optimizer与数值诊断](knowledgebase/local/topics/training-and-loss.md)
- [Megatron Core→Transformer Engine：配置、融合、低精度与HCU接口](knowledgebase/local/topics/transformer-engine.md)

### 优化案例

- [案例：MLA 融合分支遗漏 residual 声明，导致反向少一层融合](knowledgebase/local/cases/mla-residual-norm.md)
- [Paged Stash copy/pop：launch 粒度、带宽与 PR 描述漂移](knowledgebase/local/cases/paged-stash-launch.md)

## 上游资料

- [nvidia-megatron-lm](https://github.com/NVIDIA/Megatron-LM)
- [选定官方文档原文](knowledgebase/upstream/docs/)
- [已选定 PR 与固定证据](knowledgebase/upstream/prs/)
- [固定源码阅读入口](knowledgebase/upstream/source-map/)

普通 PR 通过官方原页联搜，正文、代码和讨论按需读取；已选定页面链接固定原件，历史材料由既有固定 Git 基线按需恢复。局部 Wiki 不重复维护 HCU 仓，参见[知识分工](../../../docs/knowledge-architecture.md#hcu-仓库知识的分工)。
