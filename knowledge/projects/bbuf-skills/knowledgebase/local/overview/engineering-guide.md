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
reviewed_on: '2026-11-18'
sources:
- source: bbuf-ai-infra-auto-driven-skills
  path: README.md
  commit: 371dee04ee30ed918b240823b2a12c139d1a67fa
  sha256: 6fbed4a644aa49cdf360a82489166012d7752917de6a8feb68d351a8da5aef2c
- source: bbuf-ai-infra-auto-driven-skills
  path: skills/model-optimization/README.md
  commit: 371dee04ee30ed918b240823b2a12c139d1a67fa
  sha256: 6b15b88e84baf06ebb67518c87cb614af7bd0d684dac4283ec1911b259544d3d
- source: bbuf-ai-infra-auto-driven-skills
  path: README.md
  commit: 97d0c79da43c4cac6ed417d7f0d5269aeac38010
  sha256: e3d9d26545adafdcd5ebbd075a0211a8c8b52e16dc483d4c5cc10301a31cb548
- source: bbuf-ai-infra-auto-driven-skills
  path: skills/llm-torch-profiler-analysis/SKILL.md
  commit: 97d0c79da43c4cac6ed417d7f0d5269aeac38010
  sha256: 400be657dff6c48c63ceea5d94f2cdb5f0e831c4e27a06939c69fe3fb6b68b34
- source: bbuf-ai-infra-auto-driven-skills
  path: skills/sglang-prod-incident-triage/SKILL.md
  commit: 97d0c79da43c4cac6ed417d7f0d5269aeac38010
  sha256: 39ad6e522426866a1de9eb252b5bba272b7e16e67d865a6b62bc68241a103535
retrieved_on: '2026-11-18'
---

# BBuf AI Infra Skills：按问题组织模型优化与 PR 证据

## 定位、目录和使用方式

该工程是 AI Infra 操作 Skill 和模型优化记录集合。`skills/` 保存具体执行方法，`skills/model-optimization/` 是跨模型共享流程；`model-pr-optimization-history/` 按 sglang、vllm、TensorRT-LLM、tokenspeed 等框架组织模型 PR 历史。Skill 文本、历史记录和真正执行的模型代码不是同一层。

安装/调用先按 README 的目标 Agent 方式选择 Skill，并阅读该 Skill 的依赖、脚本与输入；不能把复制 Markdown 当作 profiler/训练环境已就绪。模型适配或测试命令仍需到目标框架的固定提交执行，保留 backend、数据、模型与设备条件。此 Wiki 用于方法参考，不自动安装或执行外部 Skill 指令。

2026-11-04 固定 README 已指向 v0.1.6，列出的 Skill 从 11 项调整为 10 项，移除了 `sglang-humanize-review` 入口。不要沿用旧安装清单补装已移除的 Skill；需要 PR 证据时仍按当前模型历史、原讨论和最终代码核对。新增解说视频的发布入口不改变训练正确性或性能验收。

## 机制一：优化前检查模型能力和 PR 历史

模型 Day-0 support 路线关注 architecture gap map、并行/kernel 适配、关联 PR DAG 与发布条件。先比较模型语义、缺失算子、并行与 backend，而非从一个启动报错随机打补丁。已有 open watchpoint 可能尚未出现在 merged git history，应读模型历史和相关 PR 的最终代码。

TrainFlow 将这一路线用于真实模型适配：优先当前 HCU 脚本与模型配置，查官方实现确定优化器/层型/精度，按差异有界修复；已支持的模型不重新发明架构。上游推理专用 release gate 不能直接复制为训练 loss/恢复验收。

## 机制二：PR 动机、代码和验证一起记录

工程要求模型 PR 历史读取 diff，解释动机、实现、关键代码和验证/风险。对训练优化同样需把配置项追到实际调用、具体 kernel 与测试，区分 PR 描述、最终 merge 和安装版本，避免仅凭标题采纳一个优化。

源码发生变化后复核实际受影响的总览、机制和案例，open PR 可以提供思路但不成为默认已支持能力。TrainFlow 的 lite 策略以联搜发现普通 PR 入口，正文、固定代码和必要讨论按问题读取；只有形成结论所需的重要证据才正式保留。既有精选与历史原件保留其身份，不据此声称镜像或重新审查全部评论、review 和 diff。

## 输入、性能、数值和诊断边界

不同 Skill 的 benchmark、profile、错误定位各有命令和目标；使用前核对真实工作负载、计时口径、设备工具和可解析结果。服务吞吐、TTFT/TPOT 与训练 step/有效 token/梯度语义不同，迁移方法必须重设合理目标。出现卡住、OOM、错误结果时保留版本/输入/栈与最小复现，再按证据排除假设，不能只调整超时或容差。

当前 `97d0c79da43c4cac6ed417d7f0d5269aeac38010` 的 profiler 方法进一步要求：量化 kernel 与 reference 可能共享同一个 scale-floor 错误，数值 oracle 须对照独立公式；融合后的 normalized rows、量化值/scale、后续系数等缓存，可能在 residual 改写或 row selection 后失效。减少 launch 或两个实现彼此一致不证明语义等价。来源中的 V4.1 Engram/late-layer 是触发这类检查的具体例子，TrainFlow 提炼其状态所有权和 oracle 方法，不将例子固化为所有模型的默认步骤。

## 采集控制与诊断的版本边界

本版本两个 Skill 修订了服务入口的旧断言。这是方法来源对其检查版本的说明，实际使用仍须读取目标镜像/源码的路由和响应：

- SGLang 当前 Rust ingress 已可有 API/admin key 和 profiler、load/metrics、HiCache 等控制路由，旧镜像不同；`/ready` 的鉴权豁免不代表装载了该路由。401/404 先固定 ingress 二进制/提交、请求和响应体，再判断鉴权、条件挂载或版本差异，不能直接套用“Rust 无鉴权/无 profiler”的旧结论。
- vLLM helper 按 `/openapi.json` 广告决定是否向 start 请求传 session prefix、iteration/delay 和 profiler kwargs；旧版或未开放 OpenAPI 的服务保留 bodyless 控制及启动时 schedule。探测步数不保证纯 decode 窗口，也不覆盖 warmup/wait/active 的实际语义；旧 `capture_torch_profiler` 在所述新版本已弃用、无作用。
- TokenSpeed 的新方法入口描述 SMG 加 headless Rust engine，原 Python control sidecar 已移除；控制 URL 不再按 serving port + 1 猜测。Rust forward 线程的全进程采集、固定 wheel 的请求转发和实际产物仍须就地确认，不能把来源中的 AMD/NV 环境变量直接作为 HCU 训练默认。

采集前确认 helper 是否支持实际鉴权；本版本 helper 未提供 auth flag 时改用获权原生控制和离线分析，不绕过服务边界。capture label、正步数、shape/stack 开关、实际 phase 和文件名也要与部署版本核对。上游方法文档更新不证明本机对应服务或所有路由已经执行验证。

训练中采用位置见 [性能方法来源](../../../../../../docs/practices/performance-methods.md)；运行验收使用目标工程单测、shape 对照、模型回接和阶段 loss。本页未宣布所有外部 Skill 都已在 HCU 训练验证。官方目录和模型 PR 历史继续可按问题在线搜索，不以本页代替全部原文。

## 来源、PR 与更新

- [README.md](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/blob/371dee04ee30ed918b240823b2a12c139d1a67fa/README.md)
- [skills/model-optimization/README.md](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/blob/371dee04ee30ed918b240823b2a12c139d1a67fa/skills/model-optimization/README.md)

按实际问题检查登记方法、官方目录及文档入口；通过 `wiki-search-pr` 搜索改动原因，再追当前实现和测试，不为日常维护补采全部历史讨论或逐仓扩写报告。正文是选定源码/官方文档解读，未在新现场运行。新 commit、接口、返回 schema 或依赖变化时，同时复核本页和相关工作流。
