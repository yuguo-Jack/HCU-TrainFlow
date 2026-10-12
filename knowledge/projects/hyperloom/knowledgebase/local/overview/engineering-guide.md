---
id: tooling/hyperloom
title: Hyperloom：训练工作流可借鉴的迭代与证据机制
engine: hyperloom
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-document-reading
runtime_validated: false
reviewed_on: '2026-10-12'
sources:
- source: yuguo-jack-hyperloom
  path: README.md
  commit: 0425bde3f6e76e1588400c37d056dfd3bb75ac11
  sha256: 33b46e91746f3dff5ba197e11e8dec6f709b128d2f8843cdfe8b34a2d83e77c7
- source: yuguo-jack-hyperloom
  path: docs/components/index.md
  commit: 0425bde3f6e76e1588400c37d056dfd3bb75ac11
  sha256: b09b9f503e24391f95f28e1d7cbb076fa8b5b296d461d337bfb4b87cf99c1a47
- source: yuguo-jack-hyperloom
  path: docs/kernelforge/conceptual/architecture.md
  commit: 0425bde3f6e76e1588400c37d056dfd3bb75ac11
  sha256: 60343709a5b4902f24dd51b6d961e78a9a04616b746e51d6df3d9dc57425e839
---

# Hyperloom：训练工作流可借鉴的迭代与证据机制

## 定位与目录

Hyperloom 是面向 AMD 工作负载的 agentic 优化工程；它的 inference optimizer、KernelForge 和 framework/critic 等组件有不同职责。`docs/components/` 提供组件关系，`docs/kernelforge/` 解释 kernel campaign，`src/hyperloom/inference_optimizer/` 是推理端调度/分析/恢复入口，`src/hyperloom/agents/` 提供各角色运行实现。这里记录可迁移机制，不将其推理性能门槛当 HCU 训练验收。

## 配置、安装与调用链

从 README、pyproject、相关组件安装页确定 Python/CLI、模型服务与 profiler 依赖；各子组件不保证一次安装即具备全部外部服务。进入具体 campaign 前，查相应 `--help`、任务配置、driver、backend 与源码锁；任务 snapshot→baseline→profile→plan→edit→validate→benchmark→acceptance→keep/revert 是 KernelForge 的核心链路。

用户的训练任务无需另部署整个 Hyperloom。TrainFlow 复用其方法，实际执行仍按本仓 Skill、HCU 工具和阶段证据；安装 Hyperloom 只适用于明确要运行该组件的独立评估。

## 机制一：保护测量面与双层验收

campaign 固定 kernel、driver、backend、门槛和分支；初始 baseline 要先测，不能无条件接收第一次修改。实现者修改实现，测量 driver 与正确性参考受到保护。完整 correctness、canonical benchmark 和任务自己的 acceptance 不是一份自报摘要；warm start 也不能跳过任务验收。

训练中对应为：冻结数据/初态/计时口径和模型语义，候选只能修改授权实现；单算子通过后仍需引擎回接及阶段 loss。不能让优化 Agent 为提高分数更换 shape、减少计算或放宽容差。回滚应指向已验证代码/制品，不只保存“更快”的数字。

## 机制二：有用并行与停滞处理

KernelForge 的只读分析可分计算、内存与算法视角，最终形成一份可执行计划；多个实现 lane 使用独立工作副本。Supervisor 在搜索停滞时读完整轨迹后改方向。训练工作流借鉴证据分工和候选隔离，但不强制每个热点启动多个 Agent。

独立算子可以并行，耦合 ABI、shared buffer、通信协议或同卡测量须协调。每轮重新看实际端到端贡献与剩余空间；已经达到合理上限时说明原因，而不是无预算无限重试。故障、中断恢复要求沿同一 baseline/context 接续。

## 测试、诊断与知识维护

查组件自己的 tests 和 CLI 合约；启动失败区分外部服务/凭据、设备工具、backend 编译与任务 driver，不能将 Agent 文本输出当有效 benchmark。知识回写只提炼复用条件与已验证结果，单次失败流水留任务档案。官方代码与组件服务未全部在 HCU 验证；源码/性能方法更新按关联 docs 与 Skill 复核。

TrainFlow 的具体采用位置见 [性能方法来源](../../../../../../docs/practices/performance-methods.md)和[证据驱动迭代](../../../../../../skills/hcu-train-analyze-and-optimize/references/evidence-driven-loop.md)。

## 来源、PR 与更新

- [README.md](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/README.md)
- [docs/components/index.md](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/components/index.md)
- [docs/kernelforge/conceptual/architecture.md](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/kernelforge/conceptual/architecture.md)

按该仓完整目录与文档增量检查新增入口；通过 `wiki-search-pr` 搜索改动原因，再追当前实现和测试。正文是选定源码/官方文档解读，未在新现场运行。新 commit、接口、返回 schema 或依赖变化时，同时复核本页和相关工作流。
