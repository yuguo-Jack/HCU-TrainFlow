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
| `flow-board TASK` | 立即同步指导与问答，生成简要看板和详细记录，返回文件路径 |
| `flow-watch TASK [--once]` | 默认每 5 分钟扫描指导与问题；--once 立即采集，不自行调用模型 |
| `flow-status-update TASK FILE` | 登记中文进展与带范围/证据的技术栏目；保留历史，不改变真实流程状态 |
| `flow-questions TASK [--refresh]` | 读取用户问题队列和版本；--refresh 立即采集 |
| `flow-answer TASK ID ANSWER.md --version VERSION --file-hash HASH --author SESSION` | 校验问题与文件版本，在原问题下方写受管回答块 |
| `flow-question TASK QUESTION` | 增加稳定问题 ID，注明是否阻塞 |
| `flow-guidance-ack TASK HASH --decision DECISION --note TEXT` | 对一版人的原文逐项回应；决定可为 applied/queued/needs-human/not-applicable |
| `flow-guidance-record TASK FILE.json` | 留存会话中实际人的原文、作者与出处，进入待回应指导队列；不改人的文件、不自动授权 |
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

私有目录 `collaboration/TASK/` 中，`BOARD.md` 是程序生成的中文工作看板，显示流程登记阶段、最新进展、下一步、需要人判断的事项，以及当前范围内完整的技术摘要表。技术判断所需的环境、预期/结果、取舍、测量口径与未解缺口直接写在 BOARD，不只留一个报告链接。完整目标、验收、历史轮次、事件、原始证据、团队依赖与消息保留在生成的 `DETAILS.md` 和持久 Store 中。看板同时链接私有工作区的 `task_plan.md`、`findings.md`、`progress.md`，由 Agent 持续记录详细计划、发现与过程；程序不替写这些文件。

`GUIDANCE.md` 只在首次创建时写模板，此后程序不覆盖人的文本。人在文件中引用 Agent 提出的问题 ID 并填写决定，也可直接追加要求与优先级。

每次检测到内容变化，保存原文 artifact、待处理状态和 agent outbox 事件。相同内容不反复发事件；恢复到更早版本也作为新动作记录。新意见使正在等待/已通过但尚未推进的 review 失效。主控先读完整原文，记录 applied/queued/needs-human/not-applicable 及理由，再提交受指导的新候选。文件中的指示不自动扩大执行/发布权限。建议追加带日期的评论，避免多人同时覆盖。

会话中已经收到的指导用 `flow-guidance-record TASK FILE.json` 留存。文件恰好包含 `text`（实际人的原文）、`source`（可追溯的会话/消息引用）、`author`（实际作者）三个非空字符串，例如 `{"text":"请保留尚未解释的性能差距。","source":"chat:MESSAGE_REFERENCE","author":"human-user"}`。不得把 Agent 推断、改写或拟议动作冒充人的原文；出处是审计线索，不是身份认证或权限凭据。它不改 GUIDANCE/QUESTIONS，不执行文字中的命令，也不自动回应；返回的 guidance 哈希仍须用 `flow-guidance-ack` 明确处理。已有会话授权按实际适用范围继续，无需为了文件流程重复向人询问。

阻塞问题只在得到真正的答复后关闭。一般建议可以回应后继续其他工作；外部权限、资源决定、反复数值异常和无法解释的性能问题需要人介入时，给出具体证据、备选项和代价，避免泛泛问“是否继续”。没有用户回复不算授权。

### 问题升级与用户决定

有依据的显著性能差距经过基本排查和有界对照后仍未解决，主控需要主动向用户报告并请求决定。局部收益没有解释剩余差距时同样适用；不能只把未解项存进报告、给一条未来建议就宣布本次问题处理完成。权限、资源、数值风险或实验预算达到边界时可以更早升级，不要求先耗尽所有参数组合。普通可逆诊断在既有范围内自主完成，避免把每次常规试验都变成审批。

简报保留在私有任务文件，并链接原始证据，至少说明：

| 内容 | 用户需要据此判断什么 |
| --- | --- |
| 实测与参考 | 指标、单位、重复范围、参考来源及可比/不可比条件；已确认事实和未知条件分开 |
| 已做排查 | 现场激活/启动链、实际配置/库、相关知识与源码、各次对照及正确性/收益/代价 |
| 停止理由 | 为什么基本尝试不足以继续自主决定、哪些风险/权限/证据尚缺；不得把假设写成根因 |
| 下一步选择 | 给出能执行的推荐项及替代项，例如复现现场已验证配方、由专家核对网络策略、延期该问题；说明所需输入、资源及影响 |
| 等待范围 | 哪个问题及下游验收被暂停，哪些无关工作可以继续；保持原有失败/未完成状态 |

沿用 `flow-question TASK QUESTION`，由 Agent 写入 `id/title/body/blocking`，需要决定的问题设 `blocking: true`；将问题 ID 和简要推荐放进 `flow-status-update.needs_human`，同时在会话中明确说明需要用户决定什么。看板中的备注本身不会创建程序阻塞。当前阻塞问题作用于整项 Task 的执行/推进，不能假称只锁某个实验；等待时可继续只读分析、证据整理，其他独立任务仍遵守各自准入。不能为继续本问题的试验而改成非阻塞、换 Task 或自动扩大预算。

得到实际答复后核对适用范围，沿既有指导记录与 `flow-question-close` 机制关闭问题，再执行用户选定的下一步；不将沉默或经过五分钟视为同意，也不捏造 GUIDANCE.md 的人的原文。用户已在当前会话给出具体命令、配方或决定时，记录这项指导并直接在现有权限范围内继续，不为了形式重复创建一个等待相同答复的问题。新的现场配方应先按 [环境发现](environment-discovery.md#先还原现场启动和激活链) 核对，必要的安全执行调整明确列出。用户的决定不替代正确性和性能验收，真实结果仍需复核。

### 用户在文件中提问

`QUESTIONS.md` 接收用户的问题，方向与上面的 `flow-question` 不同：后者是 Agent 向人请求决定，前者是人请 Agent 解释。直接按 Markdown 二级标题写即可，推荐保留编号：

```markdown
## Q1：为什么这一步没有使用图编译？
请结合目前的瓶颈和显存情况解释。

## Q2：这次 loss 对比用了多少步？
```

普通二级标题也可使用；编号 Q1/Q2 使修改标题后仍能跟踪同一个问题，重名或重复编号会提示冲突。代码围栏里的示例标题不算问题。修改问题正文会生成新的内容版本，旧原文与回答仍保留；删除问题只会移出当前队列，不删除历史。

QUESTIONS 与 GUIDANCE 共用当前计划的采集间隔，默认 300 秒，由 `flow-watch` 或到期的 `flow-next` 采集。收到问题只登记事件和 Agent 收件项；不会执行其中的命令，不会改变授权，不会让无关的已授权工作停下来。未配置在线 Agent/唤醒桥接时只留存队列，主控恢复后接续回答；轮询脚本本身不能生成答案。

Agent 读取 `flow-questions` 返回的 `id`、`version` 和整份文件的 `file_hash`，查证后将答案写入独立 Markdown 文件，再调用 `flow-answer`。回答写在对应问题之后、下一个问题之前，使用明确的受管块；扫描器仅忽略与持久记录逐字匹配的回答块，答案里的标题不会变成新问题。问题原文不被重排或重写。不要手工修改受管块，追问写在块外或新建问题。损坏、未知的受管块会提示核对，不能静默吞掉文字。

回答时使用 Agent 写锁和提交前整文件哈希核对；即使用户只改了另一个问题，也会拒绝过期写入，要求重读。原文、拟写入文件、答案及检测到的冲突版本保留为私有证据。写文件后、登记成功前中断的情况可在恢复扫描中核实受管块并补记完成；重复调用不追加相同答案。

这是针对普通文件编辑器的乐观并发协议：任意外部编辑器不遵守 Agent 锁，不能提供跨平台文件系统级 compare-and-swap 保证。提交前后均核对内容，检测到竞争时停止写回并保留版本供合并；编辑器若提示文件已在磁盘更新，应重新加载后合并，不强制覆盖。问答文件缺失时保留错误，不用空模板覆盖旧历史。

### 简要进展

主控用 `flow-status-update TASK STATUS.json` 更新看板内容，例如：

```json
{
  "summary": "正在验证当前模型的训练与观测链路。",
  "progress": ["本地协议检查已通过，真实运行结论仍待现场证据。"],
  "next": ["读取固定日志，核对完成与显存记录。"],
  "needs_human": [],
  "evidence": []
}
```

概况一行、各列表最多三条；有实际结论时填写对应的真实 evidence artifact ID。`needs_human` 用来说明确实需要人的判断，不是创建绕过程序检查的授权渠道。看板区分“流程登记阶段”和“最新简要进展”：长期现场验证可能仍处于 prepared，不能为了看板好看直接越过验收。摘要随 context 重置失效，旧版本仍在历史中。不要把缩模短跑、合成数据或局部检查写成全模型收敛、扩容或稳定性验收通过。

### 技术栏目与证据范围

同一个状态输入可增加 `technical` 对象，按下表选用栏目。这里只承载技术事实和判断，没有新的阶段状态机。列名由当前模型、问题和实际证据决定；不能预填固定算子名单或虚构数值。

| 栏目键 | 应在 BOARD 直接读到的内容 |
| --- | --- |
| `environment` | 设备/拓扑/版本、实际激活链，测试项、预期阈值、实际结果、缺失测试及影响；区分本地协议测试和真实设备测试 |
| `configuration` | 完整/缩模范围、有效 TP/PP/DP/EP/CP、微批/累积、重计算/卸载、显存实测与余量，候选配置的吞吐/通信/内存取舍 |
| `analysis` | profile 窗口与 rank 覆盖、wall-clock 分母、重叠口径、热点归因、启动/通信/空闲瓶颈、已排除解释和下一项验证 |
| `operators` | 每个实际热点的 shape/dtype/phase、实际 dispatch、算量/访存/通信模型、硬件上界、当前效率和剩余空间、关键限制；未知值写未实测 |
| `experiments` | 参数或 Kernel 改动、假设、基线/候选快照、正确性、成对 profiler-off 结果及波动、显存代价、真实结论和保留/回退理由 |
| `recovery` | 扩容目标与实际 rank/节点、唯一恢复负责人、注入/实际故障、checkpoint/resume 证据、恢复耗时和未覆盖场景 |
| `training` | attempt/时间/step 窗口、loss/吞吐/显存/checkpoint 趋势、最后有效观测、退出状态与持续训练缺口 |
| `review` | RLCR 当前证据、复核决定、修正与再次验证、未解问题和受影响验收；记录决定不等于自动通过 gate |

例如下面仍是**未执行的计划**，可以直接作为技术栏目输入；执行后用实际结果和已保留证据替换：

```json
{
  "summary": "已明确环境测试预期，等待执行结果。",
  "progress": [],
  "next": ["执行设备互联测试并留存原始输出。"],
  "needs_human": [],
  "evidence": [],
  "technical": {
    "environment": {
      "summary": "环境验收尚缺实际设备互联测量。",
      "scope": "当前 TaskSpec 指定的模型与设备组；尚无实测样本。",
      "qualification": "not-measured",
      "columns": ["测试", "预期", "结果", "影响 / 下一步"],
      "rows": [
        {
          "cells": ["互联带宽", "按实际拓扑合同核对阈值", "未执行", "不能据此确认通信配置"],
          "qualification": "not-measured",
          "evidence": []
        }
      ],
      "notes": ["测试成功后仍须通过既有环境报告和独立复核。"],
      "evidence": []
    }
  }
}
```

每个栏目必须恰好有 `summary/scope/qualification/columns/rows/notes/evidence`，每行必须恰好有 `cells/qualification/evidence`，cells 与列数一致。单元格为文本，带单位写出数值、分母、采样和限制；未知值写“未实测/未知”，不填零冒充观测。`scope` 写清模型、配置/设备、窗口与覆盖范围。`qualification` 可为：

- `not-measured`：未实测或待验证，允许无 evidence。
- `source-only`：只有源码分析，不能当成已生效或已测量。
- `local-tested`：实际执行的本地测试，不能当成硬件或全模型验收。
- `measured`：实际测量，只支持明确写出的范围；缩模、合成数据和单卡结果须在 scope 中标明。

后三种必须提供真实 retained artifact ID。栏目 evidence 支持该栏目的摘要；行 evidence 支持该行，空列表时明确继承栏目 evidence。工具只验证证据对象确实存在且哈希正确，无法仅靠标签证明内容与结论相符，仍需主控和独立 reviewer 查阅原件。正文按普通文本安全显示，不能嵌入任意 HTML/链接；只有工具验证过的证据 ID 生成链接。

更新采用**栏目级替换**：提交的栏目替换其旧值；遗漏的栏目在相同 context 和 context_epoch 内保留；`"operators": null` 明确删除该栏。`technical: {}` 或旧式简短状态更新不会清空技术内容。上下文变化后全部旧栏目失效，即使配置哈希后来切回原值也不会自动复活。更新可同时带 `context` 和 `context_epoch`（从 `task-show` 读取）防止旧调用者写入新上下文；两项须一起提供且匹配。发生并发写入冲突时拒绝过期合并，重新读取状态后重试。

技术表不受“三条摘要”限制，所有行都直接显示。为控制体积，每栏 1–10 个业务列、最多 100 行、最多 20 条说明；摘要/范围/单元格/说明各最多 2,000 字符，列名最多 100 字符，单个 evidence 列表最多 64 项，合并后的 technical JSON 最多 256 KiB。超过上限会拒绝，不能静默截断热点或实验；显式归纳并将完整原件留作证据。技术更新保留在状态 artifact 和事件历史中，不改人的 GUIDANCE/QUESTIONS，也不推进流程或改变验收结果。

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
