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
- [按项目进入：整理后的知识、官方文档、PR 与源码地图](projects/README.md)
- [全库来源游标与文档清单](catalog/) / [外部 HCU 知识与用法关联](catalog/external-knowledge.json)
- [搜索与持续更新](../docs/wiki.md) / [私有训练经验与 Cookbook 记录](../docs/experience-knowledge.md)
- [Megatron LM/Core 工程地图](projects/megatron/knowledgebase/local/overview/engineering-guide.md)
- [Paged Stash launch 与 PR 描述漂移案例](projects/megatron/knowledgebase/local/cases/paged-stash-launch.md)
- [DeepSpeed offload 梯度生命周期案例](projects/deepspeed/knowledgebase/local/cases/deepspeed-offload-lifetime.md)

## 官方工程与优化参考

各行采用同一套内容维度；从总览进入源码结构、运行测试、机制专题及 PR。完整分项路线见 [覆盖导航](COVERAGE.md)，不以页数或来源数量衡量实现质量。

| 工程 | 阅读入口与核心问题 |
| --- | --- |
| [Megatron LM/Core](projects/megatron/knowledgebase/local/overview/overview.md) | 并行与调度、训练 loss、MoE、offload/Paged Stash、checkpoint |
| [Megatron Bridge](projects/bridge/knowledgebase/local/overview/bridge.md) | 配方配置、模型转换、训练接入与状态归属 |
| [Energon](projects/energon/knowledgebase/local/overview/energon.md) | 数据管线、packing、多 worker 分片与精确恢复 |
| [TorchTitan](projects/torchtitan/knowledgebase/local/overview/overview.md) | Torch 原生分布式训练、compile/融合、MoE、TitanRL |
| [DeepSpeed](projects/deepspeed/knowledgebase/local/overview/engineering-guide.md) | ZeRO 状态/内存、offload 流生命周期、流水及恢复 |
| [MS-SWIFT](projects/swift/knowledgebase/local/overview/engineering-guide.md) | SFT packing/loss、Megatron 与 GRPO 权重生命周期 |
| [LLaMA-Factory](projects/llamafactory/knowledgebase/local/overview/engineering-guide.md) | 多模态 SFT、LoRA、两代入口、CP 与 chunk loss |
| [verl](projects/verl/knowledgebase/local/overview/engineering-guide.md) | 动态批次、策略 loss、训推权重/KV 与 checkpoint |
| [slime](projects/slime/knowledgebase/local/overview/engineering-guide.md) | packed CP、策略更新、增量权重与训练恢复 |
| [AReaL](projects/areal/knowledgebase/local/overview/engineering-guide.md) | 异步 rollout、策略版本、更新与恢复一致性 |
| [SGLang](projects/sglang/knowledgebase/local/overview/engineering-guide.md) | rollout 调度/显存、权重更新与 cache 边界 |
| [vLLM](projects/vllm/knowledgebase/local/overview/engineering-guide.md) | sleep/wake、分布式权重物化、replica 与 KV 生命周期 |
| [AMD Primus](projects/primus/knowledgebase/local/overview/engineering-guide.md) | 后端、版本锁、重算、编译与通信 overlap |
| [MindSpeed / MindSpeed-LLM](projects/mindspeed/knowledgebase/local/overview/engineering-guide.md) | 核心机制与模型 recipe、MoE/流水、精度与约束 |
| [百度 LoongForge](projects/loongforge/knowledgebase/local/overview/engineering-guide.md) | 模型适配、EP overlap、offload 与固定子仓 |
| [Transformer Engine](projects/transformer-engine/knowledgebase/local/overview/overview.md) | 低精度/缓存、attention、融合、权重布局及前后向 |
| [cuDNN Frontend](projects/cudnn-frontend/knowledgebase/local/overview/overview.md) | Graph/plan、开放 kernel、稀疏 attention 与 autograd |

HCU 实际仓库、分支和修改归属通过 [HCU 库联动](../skills/hcu-train-analyze-and-optimize/references/hcu-library-integration.md)与大知识库查证；上述官方能力不自动等于 HCU 分支已适配。

## 分析工具与流程参考

| 工程 | 核心内容 |
| --- | --- |
| [TraceLens](projects/tracelens/knowledgebase/local/overview/engineering-guide.md) | 调用树、Graph、通信、Roofline、Replay 与 Agent 分析 |
| [Hyperloom](projects/hyperloom/knowledgebase/local/overview/engineering-guide.md) | 证据更新、dispatch/oracle、优化与知识沉淀 |
| [BBuf Skills](projects/bbuf-skills/knowledgebase/local/overview/engineering-guide.md) | 性能分析、诊断与有界实验的方法参考 |

工具输入/输出与数值、实际执行和上游方法的适用范围分别说明；不套用不存在的模型训练能力。

## HCU 知识联查

HCU 仓库的目录、构建、源码、PR 和案例由 HCU-Knowledge 维护。本库不复制其项目 Wiki：[Cluster Manager](catalog/external/cluster-manager.md)、[Train Simulator](catalog/external/train-simulator.md)提供大库入口；[HCU TraceLens](catalog/external/hcu-tracelens.md)连接实际工具与本仓集成契约。其他 HCU 工程按问题调用 `$hcu-knowledge-search`。通用工具方法和已验证站点经验仍分别归 docs 与 sites。

## 目录规则

每个官方项目位于 `projects/<project>/`，`README.md` 统一导航。项目内 `knowledgebase/upstream/{docs,prs,source-map}` 保存来源，`knowledgebase/local/{overview,guides,topics,cases,changes}` 保存解释。跨项目原始 PR JSON 集中放 `evidence/prs/`，每篇 PR 页链接其固定原件。`catalog/` 维护游标与关联。Release/roadmap 通过官方链接和相关版本解释查证，不另建发布页全量快照库。

## 更新方法

`wiki-update` 检查全仓目录、文档与 PR 增量、登记源码，生成受影响页面和工作流清单；用 Wiki update Skill 深读差异、PR 顶层 review/评论/代码后修订所有关联结论，最后 `wiki-review` 写复核回执、`wiki-apply` 写来源锁、`wiki-index` 重建搜索。运行中的任务继续使用原锁定快照，升级需重新建立 context。

收录前先按[内容筛选规则](../docs/knowledge-architecture.md)检查相关性和复用价值。来源配置的 `document_scope` 说明范围，`document_exclusions` 保存排除路径及理由；增量同步不会恢复已排除页，保留页与排除规则冲突时先明确整理。完整源码导航和线上 PR 检索仍保留。更新时同时复核同仓总览、专题、案例与受影响用法，验证后按[本机同步步骤](../docs/integrations.md#skills账号与升级)更新安装；普通查询不做正式收录。
