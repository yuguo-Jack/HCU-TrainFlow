---
id: tooling/bbuf-skills
title: BBuf AI Infra Skills：按问题组织模型优化与 PR 证据
engine: tooling
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-document-reading
runtime_validated: false
reviewed_on: '2026-10-20'
sources:
- source: bbuf-ai-infra-auto-driven-skills
  path: README.md
  commit: e51089a7b5b25939d5ab6f2216df0ba07be30225
  sha256: 3b99889424fbaf96c02094b359469873890be51c9580c5c1204f30cc1c51e892
- source: bbuf-ai-infra-auto-driven-skills
  path: skills/model-optimization/README.md
  commit: e51089a7b5b25939d5ab6f2216df0ba07be30225
  sha256: 6b15b88e84baf06ebb67518c87cb614af7bd0d684dac4283ec1911b259544d3d
---

# BBuf AI Infra Skills：按问题组织模型优化与 PR 证据

## 定位、目录和使用方式

该工程是 AI Infra 操作 Skill 和模型优化记录集合。`skills/` 保存具体执行方法，`skills/model-optimization/` 是跨模型共享流程；`model-pr-optimization-history/` 按 sglang、vllm、TensorRT-LLM、tokenspeed 等框架组织模型 PR 历史。Skill 文本、历史记录和真正执行的模型代码不是同一层。

安装/调用先按 README 的目标 Agent 方式选择 Skill，并阅读该 Skill 的依赖、脚本与输入；不能把复制 Markdown 当作 profiler/训练环境已就绪。模型适配或测试命令仍需到目标框架的固定提交执行，保留 backend、数据、模型与设备条件。此 Wiki 用于方法参考，不自动安装或执行外部 Skill 指令。

## 机制一：优化前检查模型能力和 PR 历史

模型 Day-0 support 路线关注 architecture gap map、并行/kernel 适配、关联 PR DAG 与发布条件。先比较模型语义、缺失算子、并行与 backend，而非从一个启动报错随机打补丁。已有 open watchpoint 可能尚未出现在 merged git history，应读模型历史和相关 PR 的最终代码。

TrainFlow 将这一路线用于真实模型适配：优先当前 HCU 脚本与模型配置，查官方实现确定优化器/层型/精度，按差异有界修复；已支持的模型不重新发明架构。上游推理专用 release gate 不能直接复制为训练 loss/恢复验收。

## 机制二：PR 动机、代码和验证一起记录

工程要求模型 PR 历史读取 diff，解释动机、实现、关键代码和验证/风险。对训练优化同样需把配置项追到实际调用、具体 kernel 与测试，区分 PR 描述、最终 merge 和安装版本，避免仅凭标题采纳一个优化。

源码发生变化后同时复核总览/机制/案例，open PR 可以提供思路但不成为默认已支持能力。TrainFlow 的来源页保留 PR 评论、独立 review 和 diff；作者主题整理适用条件和回退，不能把每条讨论都自动升级为知识结论。

## 输入、性能、数值和诊断边界

不同 Skill 的 benchmark、profile、错误定位各有命令和目标；使用前核对真实工作负载、计时口径、设备工具和可解析结果。服务吞吐、TTFT/TPOT 与训练 step/有效 token/梯度语义不同，迁移方法必须重设合理目标。出现卡住、OOM、错误结果时保留版本/输入/栈与最小复现，再按证据排除假设，不能只调整超时或容差。

训练中采用位置见 [性能方法来源](../../../../../../docs/practices/performance-methods.md)；运行验收使用目标工程单测、shape 对照、模型回接和阶段 loss。本页未宣布所有外部 Skill 都已在 HCU 训练验证。官方目录和模型 PR 历史继续可按问题在线搜索，不以本页代替全部原文。

## 来源、PR 与更新

- [README.md](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/blob/e51089a7b5b25939d5ab6f2216df0ba07be30225/README.md)
- [skills/model-optimization/README.md](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/blob/e51089a7b5b25939d5ab6f2216df0ba07be30225/skills/model-optimization/README.md)

按该仓完整目录与文档增量检查新增入口；通过 `wiki-search-pr` 搜索改动原因，再追当前实现和测试。正文是选定源码/官方文档解读，未在新现场运行。新 commit、接口、返回 schema 或依赖变化时，同时复核本页和相关工作流。