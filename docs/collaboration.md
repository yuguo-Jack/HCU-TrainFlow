# 协作循环与文件交互

## 一次任务如何持续推进

`$hcu-trainflow` 是主控入口，三个阶段 Skill 负责领域判断。CLI 保留任务、候选、复核、人的意见与执行证据，向主控返回下一动作。Agent 负责理解目标、选择工具和代码修改；远端负责实际编译、测量、训练和守护。这是一套可更换 Agent 运行时的协作协议。

```text
目标和验收条件 → 实施 / 测量 → 候选快照 → 独立 review
                    ↑                         │
                    └── 发现问题并修正 ←───────┤
                                              ↓
                               程序检查证据 → 推进阶段 / 下一轮
人的意见 → 留存版本 → 回复 / 调整 → 新候选与重新复核
```

用户可以只给环境、模型和目标，主控从已有材料中补全任务；关键资源/权限/数据缺失再询问。后续常规实验在已给范围内推进。不要要求用户手动生成本文 JSON。

## 和参考工程的关系

| 参考 | 采用的机制 | TrainFlow 的处理 |
| --- | --- | --- |
| [PolyArch/humanize](https://github.com/PolyArch/humanize) | RLCR（Ralph-Loop with Codex Review）、目标对齐、持续实施与复核 | 本地持久轮次、定期全目标复核、失败上限；不安装其全局 Stop hooks，不绑定固定模型组合 |
| [humanfia/humanize](https://github.com/humanfia/humanize) | 独立 flow runtime，内置 RLAR 的 actor/reviewer、结构化判断和可接续轮次 | 实施者与 reviewer 分离、明确 accept/revise/blocked；未打包其完整 runtime，不能称两个 Humanize 是同一个插件 |
| [BBuf SKILLS](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS) | 可复现分析、当前源码契约、从真实 review 提炼检查问题 | 检查真实 dispatch、数值和证据；其 humanize-review Skill 不等同于 RLCR 调度器 |
| [Hyperloom](https://github.com/yuguo-Jack/Hyperloom) | 持久运行状态、计划批判、候选和停滞/预算控制 | 保留候选证据和有界迭代；训练额外检查梯度、阶段 loss、实际并行组和扩容 |
| [Multica](https://github.com/multica-ai/multica) | 负责人分工、成员结果回流、运行中消息和投递状态 | 本地依赖图、会话映射、定向消息与处理回执；已发送不等于已处理，已返回不等于验收 |

本项目实现自己的轻量协议，没有调用上面几个工程的完整循环运行时。代码 review 接受不代表 GPU 测试、模型 loss 或扩容验收通过。当前没有全局 Stop hook 强制宿主永不结束；持续执行依赖入口 Skill 和部署的 Agent，关闭会话后的唤醒依赖本地桥接。

## 命令与状态

先创建普通 TaskSpec，随后 `flow-start TASK PLAN.json`；旧任务不会自动挂接循环。所有文件在私有 workspace。主要命令：

| 命令 | 作用 |
| --- | --- |
| `flow-start TASK PLAN` | 固定验收目标和循环预算，初始化人的文件与看板 |
| `flow-next TASK` | 返回 work/repair/coordinate/review/advance/reconcile/human/completed/cancelled |
| `flow-submit TASK CANDIDATE` | 留存不可变候选并请求独立复核 |
| `flow-review TASK REVIEW` | 校验结构、上下文、身份区分、目标覆盖及发现 |
| `flow-review-failed TASK ROUND --reason TEXT` | 记录 reviewer 超时、无法解析或未输出等失败 |
| `flow-advance TASK` | 复核与证据均符合当前阶段才推进 |
| `flow-replan TASK PLAN --reason TEXT` | 记录上下文/目标/预算调整原因，保留旧轮次并使旧复核失效 |
| `flow-board TASK` | 同步人的修改，重新生成看板，返回两个文件路径 |
| `flow-watch TASK [--once]` | 默认每 5 分钟扫描指导；--once 立即采集，不自行调用模型 |
| `flow-question TASK QUESTION` | 增加稳定问题 ID，注明是否阻塞 |
| `flow-guidance-ack TASK HASH --decision DECISION --note TEXT` | 对一版人的原文逐项回应；决定可为 applied/queued/needs-human/not-applicable |
| `flow-question-close TASK ID --guidance HASH --note TEXT` | 依据已读的实际回答关闭问题 |

`flow-next` 的 action 必须检查，命令退出 0 不意味着任务已经完成。`human` 是需要处理新指导或专家判断，不是强制每阶段找人审批。正常 review 由独立 Agent 完成。未配置独立 reviewer 时需要如实登记，不能让实施者改个名字假装独立。

### PLAN.json

```json
{
  "acceptance": {
    "environment": "所有分配设备和相关互联有可比预期与验收证据",
    "quality": "阶段候选相对初始冻结基线通过约定的 loss 与梯度验证",
    "performance": "给出热点覆盖、非通信上限模型及 profiler-off 性能",
    "scale": "恢复完整模型、逐级扩 DP 域验证及约定时长稳定运行"
  },
  "max_rounds": 20,
  "max_stalled_rounds": 3,
  "full_review_every": 4,
  "max_review_failures": 3,
  "poll_seconds": 300
}
```

验收条件按任务具体化，独立分析模式不要套全训练条件。轮数和 reviewer 失败数防止无界循环；计算时长、操作数仍受 TaskSpec budget 限制。连续停滞由 reviewer 基于实际收益/阻塞证据判断，不能通过每轮自报“有进步”来绕过。达到边界后提出具体建议；有新假设和授权才记录重规划。不要自动上调 budget 或降低数值门槛。

`coordinate` 要求主控处理团队可派发工作、结果验收和定向消息，具体见 [多 Agent 协同](multi-agent.md)。团队工作验收完成后，仍要提交整体候选、独立复核并推进阶段。

新任务默认 poll_seconds=300。已有任务保留登记时的配置；需要改为 300 时使用完整原计划 `flow-replan`，只调整采集间隔并说明原因，保留验收目标和预算。自动 `flow-next`/执行/推进检查共享上次扫描时间，间隔内不重复读文件；显式 `flow-board` 或 `flow-watch --once` 立即刷新。采集间隔不是紧急停机信号，紧急操作使用当前会话或站点控制渠道。

### 候选契约

```json
{
  "author": "implementation-session-id",
  "context": "TASK_CURRENT_CONTEXT_HASH",
  "goal": "FLOW_CURRENT_GOAL_HASH",
  "snapshot": "RETAINED_CANDIDATE_MANIFEST_HASH",
  "summary": "问题、证据、改动、收益/代价、剩余风险与本轮结论",
  "reports": {"analysis": "CURRENT_REPORT_HASH"},
  "target": "optimizing",
  "evidence": ["RAW_EVIDENCE_HASH"]
}
```

哈希是 `artifact-add` 或报告写入返回的真实对象 ID，示例占位符不能使用。候选 manifest 保留代码快照、配置、依赖、采样和产物关系；`source-snapshot` 返回的 snapshot_id 是源清单指纹，使用时把其清单保存为 artifact，再将 artifact ID 填入 candidate.snapshot。报告必须写相同的 `candidate_snapshot`，并与当前 context、最新报告 ID 相符。新实验/代码候选需要对应验证；上下文换硬件/数据/验证契约则用 task-context 和 flow-replan。

`reports` 由 `flow-next` 的 required_reports 指定。完整流程依次为环境、基线、分析、阶段质量/性能、扩容、完成报告；进入 profiling 仍引用已验证 baseline。进入 training 所需 environment/stage-quality/scale 必须明确覆盖同一候选；可引用先前原始验收并解释依赖未变化的适用依据，不能只改 snapshot 字段让过期验证“通过”。

优化阶段可设 `target: "iterate"` 保持在当前阶段，不必每次长时验 loss。必须额外提供 `experiment` artifact：内容就是 `iteration-check` 的完整输入，包括 context、correctness 中的 candidate_snapshot、执行/实际 dispatch 证据、profiler-off 测量协议与至少三组成对耗时。阶段晋级仍需 stage-quality 和 performance；保留迭代不等于批准长训默认配置。

初始数值基线始终独立保留；较优候选是后续性能比较的参考，不能替换初始数值基线。逐轮候选、实验及 review 都可重读；主控选择实际正确且有收益的候选，不因最近一轮就覆盖较优版本。

### 独立 REVIEW.json

```json
{
  "round": 1,
  "candidate": "SUBMITTED_CANDIDATE_HASH",
  "goal": "FLOW_CURRENT_GOAL_HASH",
  "context": "TASK_CURRENT_CONTEXT_HASH",
  "reviewer": "separate-review-session-id",
  "verdict": "revise",
  "summary": "已核对当前源码、原始证据和目标；尚缺实际 backward 分发证明",
  "findings": [{"severity": "blocking", "detail": "补采 backward 实际 kernel 与梯度回归"}],
  "acceptance": {"environment": "met", "quality": "pending", "performance": "pending", "scale": "pending"},
  "progress": "advanced",
  "full_alignment": true,
  "evidence": ["REVIEW_EVIDENCE_HASH"]
}
```

验收 key 必须完整对应 PLAN。verdict 为 accept/revise/blocked；progress 为 advanced/stalled/regressed。accept 不允许 blocking 发现，最终 completed 不允许 pending 条件。每隔指定轮次，以及 scale_ready/training/completed 前必须全目标复核。缺失、空 review 及不匹配的候选不能过关。JSON 解析之前就失败、模型超时或空输出由主控调用 flow-review-failed；有效 JSON 但契约错误自动记失败。

程序能验证身份字符串不同、哈希和结构，不能鉴定是否真的由另一个模型读过。部署时由主控保留 reviewer 运行记录，reviewer 从当前源码和原始证据判断，不能只转述实施者总结；底层依赖分支、数值/梯度、收益分母、显存峰值和回退都是适用时的复核内容。

独立 review 的关键问题：是否真的改善当前训练瓶颈；数据、基线和精度契约是否保持；显存/通信代价是否可接受；同 shape 单测和模型内是否一致；候选是否实际分发；底层库版本与当前 HCU 分支是否适用；失败路径和回退是否完整。分析任务复核推理和证据，代码任务还核对实现与回归，不套用只面向推理的评分。

## 人的评论如何处理

BOARD.md 由程序生成，展示目标、当前阶段、问题、处理回执、历史轮次和证据链接；GUIDANCE.md 只在首次创建时写模板，此后程序不覆盖人的文本。人在文件中引用问题 ID 并填写回答，也可直接追加意见。

每次检测到内容变化，保存原文 artifact、待处理状态和 agent outbox 事件。相同内容不反复发事件；恢复到更早版本也作为新动作记录。新意见使正在等待/已通过但尚未推进的 review 失效。主控先读完整原文，记录 applied/queued/needs-human/not-applicable 及理由，再提交受指导的新候选。文件中的指示不自动扩大执行/发布权限。建议追加带日期的评论，避免多人同时覆盖。

阻塞问题只在得到真正的答复后关闭。一般建议可以回应后继续其他工作；外部权限、资源决定、反复数值异常和无法解释的性能问题需要人介入时，给出具体证据、备选项和代价，避免泛泛问“是否继续”。没有用户回复不算授权。

`flow-watch` 单独运行时只是文件事件采集器。默认每 5 分钟读一次交互文件，活动主控在每轮、昂贵实验前和阶段推进前检查已采集指导；用户明确要求立即刷新时可即时采集。Agent 之间的消息走自己的持久收件箱与宿主投递，不受五分钟文件间隔限制。配置好的 bridge 可以消费事件唤醒本地 Agent；送达不等于已读或已解决，主控仍要回执并完成 inbox。无需在远端部署模型 Agent。

queued 的意见需在最终交付前改为实际应用或有理由的不适用，不能一直排队却声称完成。任务完成后的新目标另建任务；完成记录保持原验收范围。

## 中断、并发和长训

- 任务/轮次/事件在 SQLite 持久保存，代码与证据按内容保存。重新打开相同 workspace 后先 flow-next；旧 context、旧目标或被替换报告不能凭旧 review 推进。
- 一个主控拥有阶段推进权；专家通过带依赖、范围与 token 的 assignment 工作，结果验收后下游才能消费。多个控制者提交同一待审轮会被拒绝，硬件执行仍需资源租约。协议不是 OS 沙箱，不能约束绕过它的任意命令。
- 未明归属的 started 或任何 unknown 执行先核对原作业；已绑定到不同当前 assignment 的独立执行可按资源约束并行，不能以“再试一次”启动重复训练。所有执行结束后才可推进阶段。
- 长训主控按实际进展记录实验和问题，不逐 step 触发代码 review。检测到异常先诊断再形成需复核的修复；不能每次 loss 抖动就改实现。
- 本机离线，远端 watcher 和既有容错继续；本机恢复按 seq 接收事件并核对 attempt、checkpoint、节点池。独立 heartbeat observer 检测 watcher 自身失活。
- 本版本提供通用 bridge 契约，没有验证你的实际 Codex launcher、飞书投递或集群恢复。真实环境提供后，要测试 Agent 中断、主机休眠、故障无人恢复、事件重放及人类指导生效。

## 本地协议演示

```bash
hcu-trainflow collaboration-demo .work/collaboration-demo-001
```

示例有“双 lane 领取→问答与回执→结果验收→提交→要求修改→人的评论→恢复工作区→修正→接受→完成”，输出看板路径。Agent、review 和人的回复都是明确标记的合成 fixture，未调用真实模型，也没有 GPU 训练。用于检查协议和阅读体验，不能冒充完整自主运行验收。
