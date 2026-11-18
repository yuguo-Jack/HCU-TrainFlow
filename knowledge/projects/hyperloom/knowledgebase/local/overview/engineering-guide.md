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
reviewed_on: '2026-11-18'
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
- source: yuguo-jack-hyperloom
  path: README.md
  commit: d79d7a70384e3ea6be737d296bdfd476965da471
  sha256: 870be9730e9ede0c81c43c9bbaa21bf5cf2d327249028844f87cb2e03a6e7c9a
- source: yuguo-jack-hyperloom
  path: docs/components/index.md
  commit: d79d7a70384e3ea6be737d296bdfd476965da471
  sha256: d48adb0bca9621a33d52da69557ce1b0e289c00a7df4dc0686e602c15a19ce7c
- source: yuguo-jack-hyperloom
  path: docs/kernelforge/conceptual/architecture.md
  commit: d79d7a70384e3ea6be737d296bdfd476965da471
  sha256: 381331e317b96959f233abf98aa49b4acc3cfc1cb64927079cb0a3d314e72146
- source: yuguo-jack-hyperloom
  path: pyproject.toml
  commit: d79d7a70384e3ea6be737d296bdfd476965da471
  sha256: 8b711ea5ef5c71135ca0e2a04d57922eaab1f439d308fdfe1e1211ff3372c1bf
- source: yuguo-jack-hyperloom
  path: docs/conceptual/optimization-loop.md
  commit: d79d7a70384e3ea6be737d296bdfd476965da471
  sha256: d047538b8312c55143030be66a45b57a3ab88550387d2fd3705ca3595cca88dd
- source: yuguo-jack-hyperloom
  path: src/kernelforge/workflows/forge_loop/policy/analysis_refresh_policy.py
  commit: d79d7a70384e3ea6be737d296bdfd476965da471
  sha256: 5056484adc3778fd00717f777864aa8a7419fa5a364d8360c59ee7d0d40c00b8
- source: yuguo-jack-hyperloom
  path: src/kernelforge/workflows/forge_loop/search/search_policy.py
  commit: d79d7a70384e3ea6be737d296bdfd476965da471
  sha256: 64cdbd9ad07bd3a0b989bc287afb97b479b766abce226f66e53ab73134b4acd5
- source: yuguo-jack-hyperloom
  path: src/hyperloom/orchestrator/trace_analysis/_idle_gate.py
  commit: d79d7a70384e3ea6be737d296bdfd476965da471
  sha256: 7053a00fc9cbc4e3267df56cc1472cde03259b38db4e3599a057a55c235a3bd9
---

# Hyperloom：训练工作流可借鉴的迭代与证据机制

当前按用户指定改用官方 AMD-AGI/Hyperloom，固定 `d79d7a70384e3ea6be737d296bdfd476965da471`。旧 yuguo-Jack fork 已由用户确认删除；`0425bde` 及原来源 ID/证据继续保留历史身份，不改称当前官方实现。TrainFlow 采用方法，不安装或运行该工程。

## 定位与目录

Hyperloom 是 AMD-AGI 维护的 agentic 优化工程；它的 inference optimizer、KernelForge 和 framework/critic 等组件有不同职责。`docs/components/` 提供组件关系，`docs/kernelforge/` 解释 kernel campaign，`src/hyperloom/inference_optimizer/` 是推理端调度/分析/恢复入口，`src/hyperloom/agents/` 提供各角色运行实现。这里记录可迁移机制，不将其推理性能门槛当 HCU 训练验收。

## 配置、安装与调用链

从 README、pyproject、相关组件安装页确定 Python/CLI、模型服务与 profiler 依赖；各子组件不保证一次安装即具备全部外部服务。进入具体 campaign 前，查相应 `--help`、任务配置、driver、backend 与源码锁；任务 snapshot→baseline→profile→plan→edit→validate→benchmark→acceptance→keep/revert 是 KernelForge 的核心链路。

用户的训练任务无需另部署整个 Hyperloom。TrainFlow 复用其方法，实际执行仍按本仓 Skill、HCU 工具和阶段证据；安装 Hyperloom 只适用于明确要运行该组件的独立评估。

## 机制一：保护测量面与双层验收

campaign 固定 kernel、driver、backend、门槛和分支；初始 baseline 要先测，不能无条件接收第一次修改。实现者修改实现，测量 driver 与正确性参考受到保护。完整 correctness 与 canonical benchmark 由 loop/driver 产生；当前额外 task compile/correctness acceptance 专用于 assembly backend，其余 backend 沿 driver 验证与测量。它们均不接受实现者自报摘要，warm start 也不跳过该任务的准入。TrainFlow 的模型回接与阶段 loss 属于自己的训练验收，不能机械复制来源的某一 backend 门槛。

训练中对应为：冻结数据/初态/计时口径和模型语义，候选只能修改授权实现；单算子通过后仍需引擎回接及阶段 loss。不能让优化 Agent 为提高分数更换 shape、减少计算或放宽容差。回滚应指向已验证代码/制品，不只保存“更快”的数字。

## 机制二：有用并行与停滞处理

KernelForge 的只读分析可分计算、内存与算法视角，最终形成一份可执行计划；多个实现 lane 使用独立工作副本。Supervisor 在搜索停滞时读完整轨迹后改方向。训练工作流借鉴证据分工和候选隔离，但不强制每个热点启动多个 Agent。

独立算子可以并行，耦合 ABI、shared buffer、通信协议或同卡测量须协调。每轮重新看实际端到端贡献与剩余空间；已经达到合理上限时说明原因，而不是无预算无限重试。故障、中断恢复要求沿同一 baseline/context 接续。

## 当前证据刷新和搜索策略

`analysis_refresh_policy.py` 已迁到 `src/kernelforge/workflows/forge_loop/policy/`，按 canonical commit、evidence commit、测量基点及尝试状态作确定性决定。相同 iteration 不重复尝试，失败可重试，exhausted 不被当成新证据；partial 可在后续 iteration 升级。累计收益与 supervisor 触发属于来源自身策略，返回的 `evidence_stale` 仍须保留；未要求刷新不等于新实现已经有同版本分析。

`search_policy.py` 位于同一 `forge_loop` 的 `search/`，区分 EXPLOIT 与 DIVERSIFY。重复无改动优先触发换机制，其次结合 mode residence、stall 和有测量的边际收益；空 diff、没有测量与已经达到上限是不同结论。TrainFlow 借鉴状态和原因记录，按实际结构/配方/证据变化刷新及预算停止，不采用来源的统一5%收益、迭代窗口或固定 Agent 数。

`_idle_gate.py` 将 high-idle、low-compute 和 graph-under-recorded 分开。collective spin-wait 可被计为 GPU busy，却没有对应有效计算；先查实际 group、跨 rank 到达和时间误差，不能直接定性链路瓶颈。Graph 漏采时来源会跳过 idle gate 并基于录到的事件排候选，这仍只是样本，TrainFlow 保留缺口、原件与必要补采，不据此宣布完整训练覆盖。

## 测试、诊断与知识维护

查组件自己的 tests 和 CLI 合约；启动失败区分外部服务/凭据、设备工具、backend 编译与任务 driver，不能将 Agent 文本输出当有效 benchmark。知识回写只提炼复用条件与已验证结果，单次失败流水留任务档案。官方代码与组件服务未全部在 HCU 验证；源码/性能方法更新按关联 docs 与 Skill 复核。

TrainFlow 的具体采用位置见 [性能方法来源](../../../../../../docs/practices/performance-methods.md)和[证据驱动迭代](../../../../../../skills/hcu-train-analyze-and-optimize/references/evidence-driven-loop.md)。

## 来源、PR 与更新

- [README.md](https://github.com/AMD-AGI/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/README.md)
- [docs/components/index.md](https://github.com/AMD-AGI/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/components/index.md)
- [docs/kernelforge/conceptual/architecture.md](https://github.com/AMD-AGI/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/kernelforge/conceptual/architecture.md)

维护按登记路径和实际问题检查官方文档及组件入口；普通 PR 通过 `wiki-search-pr` 发现，再按需读原页、固定实现和必要讨论，不默认遍历全仓正文或全部历史评论。正文保留选定源码/官方文档的版本，未在新现场运行。只有影响实际采用方法的 commit、接口、返回 schema 或依赖变化，才联动修订本页和相关工作流。

2026-11-04 再核对固定树及上述 README、组件索引、KernelForge 架构文档：提交仍为 `0425bde3f6e76e1588400c37d056dfd3bb75ac11`，选定文件内容未变。保护测量 driver、独立验收及停滞时重看轨迹的边界仍适用；这只确认所读方法，没有新增 HCU 执行资格。
