---
id: knowledge-index
title: 训练引擎官方 Wiki 与生态机制索引
visibility: public
---

# 训练引擎官方 Wiki 与生态机制索引

本库以公开官方源码为基准，保存固定提交的阅读说明、工程导航和优化机制。HCU 私有补丁、现场材料和训练数据保存在任务工作区，通过可选 HCU-Knowledge 检索补充。

首版深度主要在 Megatron 生态与 AMD/华为/百度的代表性机制；其他引擎提供明确入口和任务检查路线，未宣称完成逐模型 Wiki。`review_level` 与 `runtime_validated` 显式表示阅读和验证状态。source-lock 记录采集内容，不代表所有文件逐行复核。

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

`wiki-refresh` 采集注册文件并生成受影响页面和工作流清单；用 Wiki update Skill 深读差异、PR 顶层 review/评论/代码后修订所有关联结论，最后 `wiki-review` 写复核回执和 `wiki-index` 重建搜索。运行中的任务继续使用原锁定快照，升级需重新建立 context。
