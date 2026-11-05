---
id: official-megatron-wiki/overview
title: Megatron 官方生态：职责、完整阅读路线与版本边界
engine: megatron
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-11-04'
coverage: frozen source delta and consumer review; unchanged files rechecked; no HCU runtime validation
sources:
- source: nvidia-megatron-lm
  path: README.md
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 241f860a314ba3790d0161a52fe423be2779d6854829488b7fb8dbf15954ee14
- source: nvidia-megatron-lm
  path: pyproject.toml
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 5eb07103781cbe8ad94d53331dace3c963f0f40c8ff98c1af467217b21086930
- source: nvidia-megatron-lm
  path: pretrain_gpt.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 37bff81772b4cff0548d94876e9699a66276af578b3902c5bef13fbb5b7af612
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 1cfba3a404c97febc4c2e40895467372e6ab540006dc6a6e22fbc547087a5b75
- source: nvidia-megatron-lm
  path: docs/get-started/releasenotes.md
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 17defec4cce9926d3fc43aecaab98c8364d44e0cc3ec1d19cde7a91c53684243
- source: nvidia-megatron-lm
  path: megatron/training/config/container.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 4965eeb1ad25b950348a29557799fd920f1c2207544c83992eb22e537a8758b2
- source: nvidia-megatron-lm
  path: megatron/training/config/dataset_config.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: ad183c58c35e91b065577d0f3fdb5ef89fbf6282a4e6de1fad1950926c8b030d
- source: nvidia-megatron-lm
  path: megatron/training/datasets/providers.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: a28174f91d974d5ac17d577ed53da2a71af8df16988edca006cc4ccac2c10938
retrieved_on: '2026-11-04'
---

# Megatron 官方生态：职责、完整阅读路线与版本边界

## 工程组成与训练职责

Megatron-LM仓包含应用训练入口、`megatron/training`和`megatron/core`。Core提供模型、并行、optimizer和分片checkpoint，LM入口提供数据/forward/loss及运行配方，不能把同一仓的LM/Core变化登记成两个独立上游。Bridge是独立配方、模型provider与权重转换工程，Energon是可恢复数据加载；TE及cuDNN/编译实现继续承担底层计算。

运行组合以消费者实际依赖锁为准；LM、Bridge、TE各自最新HEAD拼在一起不是已验证组合。官方机制用于核对语义与参考优化，HCU任务实际选HCU仓、分支、模型脚本和平台依赖。

## 按统一粒度浏览

| 问题 | 主入口 | 继续阅读 |
| --- | --- | --- |
| 工程组织/一个开关如何生效 | [目录地图](source-map.md)、[工程指南](engineering-guide.md) | config→provider→模块→backend→测试 |
| 安装、模型跑通、数据/单测 | [安装运行测试](../guides/build-run-test.md) | README、pyproject、quickstart、模型脚本 |
| batch/loss/optimizer数值 | [训练与loss](../topics/training-and-loss.md) | data mask→schedule归一化→grad sync→step→logging |
| 卡显存容量、并行布局与PP偏斜 | [并行策略](../topics/parallelism.md) | 实际groups、层分配、microbatch和状态分片 |
| TP/DP/PP/EP重叠 | [overlap](../topics/overlap.md) | hooks/buckets、P2P、token dispatcher与限制 |
| MoE负载/grouped GEMM/容量 | [MoE](../topics/moe.md) | routing→dispatch→expert→combine及Paged Stash |
| 重算、offload、临时峰值 | [显存生命周期](../topics/memory.md) | autograd saved-tensor、streams、checkpoint峰值 |
| profiler/高占比算子/上限 | [profiling](../topics/profiling.md) | 原生采样、TraceLens与实际kernel分发 |
| 保存、并行变化恢复、长训故障 | [checkpoint](../topics/checkpoint.md) | async finalize、metadata、optimizer/RNG/data游标 |
| TE精度/融合接入 | [Core→TE契约](../topics/transformer-engine.md) | [独立TE Wiki](../../../../transformer-engine/knowledgebase/local/overview/overview.md) |
| HF/Megatron转换与配方 | [Bridge](../../../../bridge/knowledgebase/local/overview/bridge.md) | 模型provider、转换/roundtrip、checkpoint |
| 数据loader恢复 | [Energon](../../../../energon/knowledgebase/local/overview/energon.md) | worker与编码器、savable loader、样本游标 |
| 具体优化改因与反向契约 | [Paged Stash launch案例](../cases/paged-stash-launch.md)、[MLA residual案例](../cases/mla-residual-norm.md) | PR描述/review、最终diff和测试 |

每个入口解释不同实现维度；全仓清单与原文不会替代专题。尚未精读的模型、后端和PR按问题继续查[全仓来源地图](../../upstream/source-map/nvidia-megatron-lm.md)与线上PR。

## 一次训练的源码路线

recipe/`pretrain_gpt.py`读取模型、tokenizer、batch和loss回调；`gpt_builders.py`/model-provider构造实际模型spec；training初始化groups、模型、optimizer和数据，`train_step`驱动Core schedule；层内部进入attention/MLP/MoE、TE与真实kernel；最后沿DDP/optimizer、checkpoint和loader检查状态所有权。

当前训练入口由 typed 配置容器与历史 argparse 衔接，`get_run_config()` 是实际运行配置入口。训练 batch/horizon、optimizer/scheduler 和数据分别由 `cfg.train`、`cfg.optimizer`/`cfg.scheduler`、`cfg.data` 消费；GPT provider 已移到 `training/datasets/providers.py`。只在 CLI 或 dataclass 找到字段不证明已消费，例如 DataLoader 的三个字段仍只声明，详见[构建运行](../guides/build-run-test.md)。诊断还需确认 Python import 和动态扩展真实加载位置。

## 基准与模型契约

保存官方/HCU/用户patch身份、依赖版本、模型参数、真实argv、数据/tokenizer指纹、并行group和checkpoint来源。先查实际HCU同模型支持脚本，用官方配置检查attention、MoE/MTP、optimizer与mask语义；不同名称但参数相似不代表同模型。

容量评估允许时直接完整模型，资源不足优先仅缩layer，保留其余dim、heads、seq、专家、optimizer与数据语义；代理验证与完整模型/大DP结论分开。loss先建立可信基线，局部优化小回归，稳定阶段再做较长数值比较。

## 发布、roadmap 与当前证据

本轮固定 main 为 `21334a44ede0b8497d1770d0b80bc115e777bd00`，与发行版分开。2026-11-04 固定观测 GitHub 最近 10 条 release，包含 2026-10-29 发布的 [`core_v0.20.0`](https://github.com/NVIDIA/Megatron-LM/releases/tag/core_v0.20.0)，以及此前 `26.09-lambda.rc1`、`26.09-alpha/beta.rc*` 和 `core_v0.19.2`。候选名称中的 rc、API 的 prerelease 标记、tag 指向与当前 main 是不同事实；本轮未据此证明 main 新功能均包含于 0.20.0，也未遍历全部 release 历史。当前安装教程已与 main metadata 对齐 Python≥3.12，详见安装页。

[官方开发指南](https://docs.nvidia.com/megatron-core/developer-guide/latest/index.html)、[Releases](https://github.com/NVIDIA/Megatron-LM/releases)、[源码release notes](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/docs/get-started/releasenotes.md)、README 所链[Core roadmap #4003](https://github.com/NVIDIA/Megatron-LM/issues/4003)、[2026 Q2 roadmap #4997](https://github.com/NVIDIA/Megatron-LM/issues/4997)、[MoE roadmap #4815](https://github.com/NVIDIA/Megatron-LM/issues/4815)、[Issues](https://github.com/NVIDIA/Megatron-LM/issues)和[PR](https://github.com/NVIDIA/Megatron-LM/pulls)分别检查。某期roadmap是计划证据，不永远代表最新路线。

旧 2026-10-20 观测曾记录 Q1 #4003、Q2 #4997 和 MoE #4815 的关闭状态；这是历史状态。当前固定 README 改链 [Q3 Core #5676](https://github.com/NVIDIA/Megatron-LM/issues/5676)、[MoE #6757](https://github.com/NVIDIA/Megatron-LM/issues/6757) 和 [FSDPv2 #6812](https://github.com/NVIDIA/Megatron-LM/issues/6812)，并将后两者分别说明为 dev 优先、experimental。README 链接与计划内容不证明 issue 当前状态、发布包含或端到端资格；PR/讨论的最新审阅另按来源页记录。

重点保留[PR #7897](../../upstream/prs/NVIDIA--Megatron-LM/PR-7897.md)、[#7942](../../upstream/prs/NVIDIA--Megatron-LM/PR-7942.md)、[1F1B文档#7534](../../upstream/prs/NVIDIA--Megatron-LM/PR-7534.md)与[MXFP8内存#6878](../../upstream/prs/NVIDIA--Megatron-LM/PR-6878.md)的来源入口。open/dev PR继续按head/base阅读，不标成main已实现；已有等价官方优化合入部署分支后，经回归退役本地patch。

`wiki-update PROJECT nvidia-megatron-lm`覆盖本仓登记来源；Bridge/Energon/TE各自更新源。普通查询可`wiki-search-pr "mechanism error symbol" --engine megatron`再`wiki-code OWNER/REPO FULL_SHA PATH`，训练开发checkout与知识源码缓存分开。

当前 README 性能表已改为特定 `26.08.01` NeMo 容器/代码与 B200、GB200、GB300 等硬件的报告，MoE 数据注明强制均衡路由、无 token dropping。旧 H100 47% MFU 概述不能作当前任意模型基线，更不能迁移为 HCU 目标；保持容器、模型 shape、精度、并行和路由条件才能讨论复现。本页的职责划分与缩层代理边界继续保留，因为入口、Core、Bridge、Energon 的实际所有者未因此合并。

## 固定源码与维护边界

- [README.md](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/README.md)
- [pyproject.toml](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/pyproject.toml)
- [pretrain_gpt.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/pretrain_gpt.py)
- [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/training/training.py)
- [docs/get-started/releasenotes.md](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/docs/get-started/releasenotes.md)

2026-11-04按上述固定源码、实际消费者与官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。