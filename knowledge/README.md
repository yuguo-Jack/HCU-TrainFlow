---
id: knowledge-index
title: HCU-TrainFlow-Wiki：官方资料、环境经验与模型总结
visibility: public
---

# HCU-TrainFlow-Wiki：官方资料、环境经验与模型总结

本库只收录官方资料、跨项目可复用的通用环境经验，以及模型最终优化里程碑的总结和关键数据。临时排查、未定候选和逐次实验留在 workspace/看板，不纳入共享检索。HCU-Knowledge 是完整安装的必需依赖，按问题联查，普通任务不更新它。

各官方仓库按同一套[内容标准](../docs/wiki-authoring-standard.md)组织：定位、目录、安装、运行测试、数值/状态契约、调用链、性能显存、诊断恢复、版本与 PR。通过[覆盖导航](COVERAGE.md)按仓查找这些入口；通过[优化参考图谱](../docs/optimization-reference-map.md)按问题联查 Megatron、TorchTitan、DeepSpeed、SFT/RL、推理后端和第三方实现。TE/cuDNN 同时登记官方源码与网站教程。`review_level` 与 `runtime_validated` 分开表示阅读和验证状态；source-lock 与目录完整不代表所有文件逐行复核或完成每个模型实测。

入口为 `$hcu-trainflow-wiki-search` 与 `$hcu-trainflow-wiki-skill-update`。任务初期核对相关官方知识，阶段和最终收尾整理可复用经验，具体见 [知识维护时机](../docs/knowledge-architecture.md#任务中的维护时机)。

## 共享知识与工作流文档

- [工作流方法说明](../docs/practices/README.md)：通信配方、执行基线与验证/交付顺序。
- [站点环境、配方与实测](sites/README.md)：含真实配置和结果，可脱离旧 workspace 使用。
- [模型最终优化里程碑](experiments/README.md)：最终选择、性能/显存/loss 和适用边界；中间候选留在任务档案。
- [知识归属与维护](../docs/knowledge-architecture.md)：共享 Wiki 收录条件、工作流文档和任务档案的关系。
- [全仓内容覆盖导航](COVERAGE.md)：各仓九项阅读维度、机制专题及明确边界。

## 搜索与来源层

- [PR 描述、review、diff 与固定源码索引](PR-INDEX.md)
- [全仓源码路径](source-maps/) / [官方教程原文](upstream-docs/) / [来源游标与文档清单](catalog/)
- [搜索与持续更新](../docs/wiki.md) / [私有训练经验与 Cookbook 记录](../docs/experience-knowledge.md)
- [Megatron LM/Core 工程地图](official-megatron-wiki/engineering-guide.md)
- [Paged Stash launch 与 PR 描述漂移案例](official-megatron-wiki/cases/paged-stash-launch.md)
- [DeepSpeed offload 梯度生命周期案例](engines/deepspeed-offload-lifetime.md)

## 官方工程与优化参考

各行采用同一套内容维度；从总览进入源码结构、运行测试、机制专题及 PR。完整分项路线见 [覆盖导航](COVERAGE.md)，不以页数或来源数量衡量实现质量。

| 工程 | 阅读入口与核心问题 |
| --- | --- |
| [Megatron LM/Core](official-megatron-wiki/overview.md) | 并行与调度、训练 loss、MoE、offload/Paged Stash、checkpoint |
| [Megatron Bridge](official-megatron-wiki/bridge.md) | 配方配置、模型转换、训练接入与状态归属 |
| [Energon](official-megatron-wiki/energon.md) | 数据管线、packing、多 worker 分片与精确恢复 |
| [TorchTitan](official-torchtitan-wiki/overview.md) | Torch 原生分布式训练、compile/融合、MoE、TitanRL |
| [DeepSpeed](engines/deepspeed.md) | ZeRO 状态/内存、offload 流生命周期、流水及恢复 |
| [MS-SWIFT](engines/swift.md) | SFT packing/loss、Megatron 与 GRPO 权重生命周期 |
| [LLaMA-Factory](engines/llamafactory.md) | 多模态 SFT、LoRA、两代入口、CP 与 chunk loss |
| [verl](engines/verl.md) | 动态批次、策略 loss、训推权重/KV 与 checkpoint |
| [slime](engines/slime.md) | packed CP、策略更新、增量权重与训练恢复 |
| [AReaL](engines/areal.md) | 异步 rollout、策略版本、更新与恢复一致性 |
| [SGLang](engines/sglang.md) | rollout 调度/显存、权重更新与 cache 边界 |
| [vLLM](engines/vllm.md) | sleep/wake、分布式权重物化、replica 与 KV 生命周期 |
| [AMD Primus](ecosystem/primus.md) | 后端、版本锁、重算、编译与通信 overlap |
| [MindSpeed / MindSpeed-LLM](ecosystem/mindspeed.md) | 核心机制与模型 recipe、MoE/流水、精度与约束 |
| [百度 LoongForge](ecosystem/loongforge.md) | 模型适配、EP overlap、offload 与固定子仓 |
| [Transformer Engine](official-transformer-engine-wiki/overview.md) | 低精度/缓存、attention、融合、权重布局及前后向 |
| [cuDNN Frontend](official-cudnn-frontend-wiki/overview.md) | Graph/plan、开放 kernel、稀疏 attention 与 autograd |

HCU 实际仓库、分支和修改归属通过 [HCU 库联动](../skills/hcu-train-analyze-and-optimize/references/hcu-library-integration.md)与大知识库查证；上述官方能力不自动等于 HCU 分支已适配。

## 分析工具与流程参考

| 工程 | 核心内容 |
| --- | --- |
| [TraceLens](tooling/tracelens.md) | 调用树、Graph、通信、Roofline、Replay 与 Agent 分析 |
| [HCU Cluster Manager](tooling/cluster-manager.md) | 当前环境检查入口、结果判读、作业控制和恢复 |
| [HCU Train Simulator](tooling/train-simulator.md) | 模型容量、并行方案及实测校准 |
| [Hyperloom](tooling/hyperloom.md) | 证据更新、dispatch/oracle、优化与知识沉淀 |
| [BBuf Skills](tooling/bbuf-skills.md) | 性能分析、诊断与有界实验的方法参考 |

工具输入/输出与数值、实际执行和上游方法的适用范围分别说明；不套用不存在的模型训练能力。

## 更新方法

`wiki-update` 检查全仓目录、文档与 PR 增量、登记源码，生成受影响页面和工作流清单；用 Wiki update Skill 深读差异、PR 顶层 review/评论/代码后修订所有关联结论，最后 `wiki-review` 写复核回执、`wiki-apply` 写来源锁、`wiki-index` 重建搜索。运行中的任务继续使用原锁定快照，升级需重新建立 context。

收录前先按[内容筛选规则](../docs/knowledge-architecture.md)检查相关性和复用价值。来源配置的 `document_scope` 说明范围，`document_exclusions` 保存排除路径及理由；增量同步不会恢复已排除页，保留页与排除规则冲突时先明确整理。完整源码导航和线上 PR 检索仍保留。更新时同时复核同仓总览、专题、案例与受影响用法，验证后按[本机同步步骤](../docs/integrations.md#skills账号与升级)更新安装；普通查询不做正式收录。
