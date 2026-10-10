---
id: knowledge-index
title: TrainFlow 官方资料、环境经验与模型里程碑
visibility: public
---

# TrainFlow 官方资料、环境经验与模型里程碑

本库只收录官方资料、跨项目可复用的通用环境经验，以及模型最终优化里程碑的总结和关键数据。临时排查、未定候选和逐次实验留在 workspace/看板，不纳入共享检索。HCU-Knowledge 是完整安装的必需依赖，按问题联查，普通任务不更新它。

重点覆盖 Megatron 生态、Transformer Engine、cuDNN Frontend 与 AMD/华为/百度的代表性机制；主要 SFT/RL 引擎按目录、调用链、安装运行测试、优化和故障诊断组织，仍不宣称完成逐模型 Wiki。TE/cuDNN 同时登记官方源码与网站教程。`review_level` 与 `runtime_validated` 显式表示阅读和验证状态。source-lock 记录采集内容，不代表所有文件逐行复核。

## 共享知识与工作流文档

- [工作流方法说明](../docs/practices/README.md)：通信配方、执行基线与验证/交付顺序。
- [站点环境、配方与实测](sites/README.md)：含真实配置和结果，可脱离旧 workspace 使用。
- [模型最终优化里程碑](experiments/README.md)：最终选择、性能/显存/loss 和适用边界；中间候选留在任务档案。
- [知识归属与维护](../docs/knowledge-architecture.md)：共享 Wiki 收录条件、工作流文档和任务档案的关系。

## 搜索与来源层

- [PR 描述、review、diff 与固定源码索引](PR-INDEX.md)
- [全仓源码路径](source-maps/) / [官方教程原文](upstream-docs/) / [来源游标与文档清单](catalog/)
- [搜索与持续更新](../docs/wiki.md) / [私有训练经验与 Cookbook 记录](../docs/experience-knowledge.md)
- [Megatron LM/Core 工程地图](official-megatron-wiki/engineering-guide.md)
- [Paged Stash launch 与 PR 描述漂移案例](official-megatron-wiki/cases/paged-stash-launch.md)
- [DeepSpeed offload 梯度生命周期案例](engines/deepspeed-offload-lifetime.md)

## 章节

- [Megatron 官方生态：责任边界与阅读路线](official-megatron-wiki/overview.md)
- [Megatron 代码目录与问题定位地图](official-megatron-wiki/source-map.md)
- [Megatron 安装、启动、测试与 HCU 接入](official-megatron-wiki/build-run-test.md)
- [并行域、微批与 rank 采样](official-megatron-wiki/parallelism.md)
- [训练循环、loss 和优化器更新的证据链](official-megatron-wiki/training-and-loss.md)
- [训练 profiler 采样与 TraceLens 联动](official-megatron-wiki/profiling.md)
- [TP、DP、PP、EP overlap 的适用条件](official-megatron-wiki/overlap.md)
- [显存生命周期、重算、offload 与 checkpoint 峰值](official-megatron-wiki/memory.md)
- [MoE：路由、负载、通信与 grouped GEMM](official-megatron-wiki/moe.md)
- [分布式 checkpoint、数据游标与恢复验收](official-megatron-wiki/checkpoint.md)
- [Megatron Bridge：配方、模型转换与训练配置](official-megatron-wiki/bridge.md)
- [Transformer Engine：精度、融合与 HCU 承接边界](official-megatron-wiki/transformer-engine.md)
- [Energon：数据吞吐与可恢复样本顺序](official-megatron-wiki/energon.md)
- [AMD Primus：后端组织、版本锁与迁移路线](ecosystem/primus.md)
- [案例：参数 gather overlap 与编译区域的 hook 边界](ecosystem/cases/primus-compile-ddp.md)
- [案例：精确逐层重算及上游源码指纹约束](ecosystem/cases/primus-layer-recompute.md)
- [华为 MindSpeed / MindSpeed-LLM：机制级参考](ecosystem/mindspeed.md)
- [案例：MoE overlap 的参数约束就是正确性契约](ecosystem/cases/mindspeed-ep-constraints.md)
- [百度 LoongForge：调度、offload 和模型适配参考](ecosystem/loongforge.md)
- [案例：跨微批 EP overlap 与细粒度激活策略](ecosystem/cases/loongforge-ep-offload.md)
- [TraceLens 复用接口与训练补充信息](tooling/tracelens.md)
- [MS-SWIFT：SFT、Megatron 接口与 RL 阅读入口](engines/swift.md)
- [LLaMA-Factory：配置驱动微调与数据语义](engines/llamafactory.md)
- [DeepSpeed：ZeRO、扩展构建与训练阶段定位](engines/deepspeed.md)
- [verl：PPO 训练、rollout 与权重一致性](engines/verl.md)
- [slime：Megatron 训练与 SGLang rollout 的联动](engines/slime.md)
- [AReaL：异步 RL 的版本与恢复状态](engines/areal.md)
- [SGLang：RL rollout 的推理侧检查](engines/sglang.md)
- [vLLM：RL rollout 的推理侧检查](engines/vllm.md)
- [HCU Cluster Manager：环境检查与单一恢复负责人](tooling/cluster-manager.md)
- [案例：MLA 融合分支遗漏 residual 声明，导致反向少一层融合](official-megatron-wiki/cases/mla-residual-norm.md)

## 更新方法

`wiki-update` 检查全仓目录、文档与 PR 增量、登记源码，生成受影响页面和工作流清单；用 Wiki update Skill 深读差异、PR 顶层 review/评论/代码后修订所有关联结论，最后 `wiki-review` 写复核回执、`wiki-apply` 写来源锁、`wiki-index` 重建搜索。运行中的任务继续使用原锁定快照，升级需重新建立 context。

## 官方底层训练库

- [Transformer Engine 官方工程：定位、目录与训练调用链](official-transformer-engine-wiki/overview.md)
- [TE 安装、运行、单测与 HCU 环境接入](official-transformer-engine-wiki/build-run-test.md)
- [TE 低精度训练：recipe、amax、权重缓存与反向状态](official-transformer-engine-wiki/precision-and-cache.md)
- [TE Attention：后端选择、cuDNN 调用与训练精度契约](official-transformer-engine-wiki/attention.md)
- [TE 并行与显存：Userbuffers、CP、Graph 和 Offload](official-transformer-engine-wiki/overlap-and-memory.md)
- [TE 融合与形状级分析：OperationFuser 和 GEMM 教程](official-transformer-engine-wiki/fusion-and-profiling.md)
- [TE 官方教程索引与版本更新方法](official-transformer-engine-wiki/tutorials-and-update.md)
- [cuDNN Frontend 官方工程：Graph、开放 Kernel 与训练调用链](official-cudnn-frontend-wiki/overview.md)
- [cuDNN Frontend 编译安装、运行示例与测试路线](official-cudnn-frontend-wiki/build-run-test.md)
- [cuDNN Graph、执行计划、Workspace 与动态形状缓存](official-cudnn-frontend-wiki/graph-and-plans.md)
- [cuDNN SDPA 训练：Forward、Backward、Stats 与布局](official-cudnn-frontend-wiki/attention.md)
- [cuDNN 开放 Kernel：MoE 融合、FROST 与稀疏 Attention](official-cudnn-frontend-wiki/open-kernel-fusions.md)
- [案例：cuDNN Kernel 不慢，模型却被构图和 Host 调度拖慢](official-cudnn-frontend-wiki/cases/host-dispatch-and-cache.md)
- [cuDNN Frontend 官方教程、源码实例与更新索引](official-cudnn-frontend-wiki/tutorials-and-update.md)
