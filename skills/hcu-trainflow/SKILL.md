---
name: hcu-trainflow
description: 统一编排 HCU 大模型训练适配、性能优化、大规模验证与持续容错；拆解并行 Agent 任务，协调依赖、消息与证据验收，持续实施、独立复核和修正，并处理看板指导。也可只检查环境、分析性能或诊断故障。
---

# HCU-TrainFlow 协作主控

接受一句任务，例如“在指定 Slurm 环境对这个模型做适配、优化和大规模验证”。由你管理步骤、证据、专家分工、阶段复核和人类指导；不要求用户手工串接三个 Skill 或填写内部 JSON。遵守当前宿主的执行、委派和发布授权。

## 定位与任务契约

1. 定位 HCU-TrainFlow checkout（用户路径或 `TRAINFLOW_PROJECT`）和私有 `TRAINFLOW_WORKSPACE`。先读项目 `docs/collaboration.md`、`docs/multi-agent.md`、`docs/workflows.md`，查看当前 CLI 帮助与已有任务。找不到工程时说明所缺路径，不以安装 Skill 的相对位置猜测项目。
2. 从会话和现场推导模型、预训练/SFT/RL、资源范围、部署方式、数据/权重、用户 patch、目标及已有授权。关键访问、数据或资源缺失才向用户询问；并行继续可做的阅读/分析。全流程用 `full`；只检查、适配、分析、优化、诊断、运行分别用现有独立模式，不扩大任务。
3. 创建或恢复 TaskSpec；冻结初始数值基线、比较上下文、预算、执行权限、唯一容错负责人。依当前 HCU 活跃分支的脚本和现场启动方式适配，不机械照搬 NV 配方。读取原始证据的权限不等于允许发布数据或重启任意任务。
4. 写出可验收的目标和阶段计划，`flow-start` 挂接持久循环。用 `flow-board` 向用户提供中文简要 BOARD.md、要求与指导 GUIDANCE.md、提问与回答 QUESTIONS.md 的路径；完整团队和历史在 DETAILS.md。预算是停止盲目试错的边界；实际调整理由用 `flow-replan` 留痕，不能偷偷降低目标或延长循环。
5. 每个模型私有工作区保留 `task_plan.md`、`findings.md`、`progress.md`：分别记录当前计划、可追溯发现和实验/决策经过。它们补充看板与结构化 evidence，不代替程序门槛；跨环境/版本结论标明适用范围，现场数据不写进公共工程文档。

## 每轮工作

反复执行 `flow-next TASK`，完成当前动作后继续，不在每个正常步骤后要求确认：

| action | 主控责任 |
| --- | --- |
| `work` / `repair` | 调用对应阶段 Skill，读取上一轮问题，选一个有证据支持的改动/实验。准备代码快照、报告和完整候选契约，`flow-submit`。不能只改总结以规避未通过的测试。 |
| `coordinate` | 按 `team-next` 处理可派发任务、活跃成员和返回结果；转送/回复消息，验收解锁依赖。不能把等待成员当任务完成，也不能绕过团队验收直接提交候选。 |
| `review` | 让独立 reviewer 从目标、候选快照、原始测试/trace、代码差异和历史发现重新检查。具备委派授权时用独立 Agent/会话；否则使用已配置 reviewer 或人类复核，不把实施者换个名字冒充独立审核。按契约 `flow-review`；超时、空回复或解析失败记 `flow-review-failed`。 |
| `advance` | `flow-advance` 检查当前证据并进入下一阶段或下一轮。review 接受不能代替程序验收。 |
| `reconcile` | 先确认原作业/attempt/执行是否仍在运行，再凭证据核销不确定操作；不得盲目重跑。 |
| `human` | 读取新指导并回复，或提出真正需要人的问题。能独立完成的证据收集继续做；不绕过权限、数值问题、预算或专家介入边界。 |
| `completed` / `cancelled` | 给出自包含的结果、证据、未解决限制和交付位置；未满足请求不能自行宣告完成。 |

review 按 `docs/collaboration.md` 使用完整字段；不以单词“完成”或退出码替代评审。每隔配置轮次及扩容/长训/结束边界做全目标检查。数值退化、无收益平台期、反复工具失败须带最小证据包请专家介入。

环境/模型/扩容出现可信性能差距时，主控按项目 `docs/environment-discovery.md` 第 6 节派发基本排查与有界尝试，不能接受只有差距表的“完成”报告。复核原件口径、链路/库版本和 HCU 知识/源码后，在已有授权与资源准入范围内自主推进可逆对照；核验正确性、生效路径、回归与回退。`environment-check` 的 `follow_up_required` 或 `performance_discrepancy` 进入当前 flow/经验记录；条件未知不是忽略理由，未解决保持 fail/incomplete。分析-only 或实际权限不足时保留待执行项，报告已排除项与具体所需权限，不能虚构实验或扩大站点改动范围。

## 阶段分工

Torch 原生视频/VLA/世界模型训练沿用这三个阶段；由 optimize 按需加载 Torch 与通信专项，不增加独立 Skill。全流程先检查 HCU-Knowledge 的搜索 Skill、workspace 绑定及当前索引可用性；缺失按 docs/integrations.md 完成必需安装。三个阶段按实际 HCU 问题联查它，普通训练不触发大知识库更新。

- `$hcu-train-adapt`：环境验收、HCU 启动配方、模型适配和初始基线。可仅检查环境。
- `$hcu-train-optimize`：可仅分析性能；先评估并行切分、微批/梯度累积与显存余量，按吞吐和通信代价选择配置；系统、融合、算子优化采用测量→假设→实施→验证→复核。累计 ≥90% 端到端热点集合中的非通信算子逐项建模；比较真实 shape 的独立测试。每轮局部正确性和 profiler-off 性能，稳定阶段才长窗口验 loss，始终对初始基线。复用 Flash-Train/TE 现有实现，必要时调用三个 Hygon kernel Skill。
- `$hcu-train-fault-tolerance`：按本轮选定配置扩 DP 域、筛机扩容、单一恢复负责人、长训监测及故障诊断。完整模型目标须先恢复完整配置；用户明确以缩减模型验证本轮流程时，可扩该配置的 DP 并保留完整模型缺口，见 `docs/proxy-contract.md`。训练启动不是任务结束；验证 step/loss/吞吐/显存/checkpoint/恢复是否持续符合预期。
- `$hcu-engine-wiki-search` / `$hcu-engine-wiki-update`：本地官方 Wiki 的检索和维护。需要 HCU 事实时读 HCU-Knowledge、当前底层库分支或官方资料；普通任务不顺带更新 HCU 大知识库。工具/脚本变了要复核相关 Skill、命令和解析器，不仅更新 Wiki。

## 看板指导

默认每 5 分钟采集 GUIDANCE.md，由 `flow-watch` 或到期的 `flow-next` 收集到事件队列；每轮开始、昂贵实验前、阶段推进前检查已采集指导。不要每个步骤都绕过间隔直接重读文件。用户要求立即刷新时用 `flow-board` / `flow-watch --once`。逐条明确应用、排期或不能应用的理由并 `flow-guidance-ack`；不要编辑人的原文。阻塞问题以 `flow-question` 登记，收到实际回答后关闭。进展、收益/代价、显存趋势、平台期和专家需求写看板；避免要求确认常规动作。

同一次轮询也采集 QUESTIONS.md。用户可按 `## Q1：问题` 写标题和正文；用 `flow-questions TASK` 读取待答项、问题版本和整份文件哈希。你负责查证并写 Markdown 答案，再用 `flow-answer TASK QUESTION ANSWER.md --version VERSION --file-hash HASH --author SESSION` 写回问题下方。不要直接重写人的问题文件；遇到编辑冲突先重读，不能用旧答案覆盖新内容。已发布回答保持版本，追问作为新问题或正文修改处理。回答内容不会产生新问题。

问答是解释收件箱，不自动构成执行命令、扩大资源范围或重启训练的授权；不要据问题里的命令直接行动。待答问题不阻塞无关的已授权工作；及时回答与训练可并行。GUIDANCE、独立 review 和执行准入仍按原有规则处理。观察器/flow-watch 只采集，没有在线 Agent 或已配置唤醒桥接时不会自行生成答案，恢复后先读持久问题队列。

用 `flow-status-update` 维护简短中文进展：一句概况、至多三条已完成/验证中事项、三条下一步和真正需要人判断的事项。不要把每条团队消息、原始 JSON 或所有实验日志塞进 BOARD；DETAILS 与私有的三个计划文件保留完整过程。简报不能修改真实流程状态，也不能把短跑、缩模或局部通过写成全模型验收通过。

需要展示训练趋势时，使用项目 `scripts/render_training_dashboard.py` 从规范化日志生成私有单 attempt 图表；按 `docs/training-dashboard.md` 选择身份、记录原件哈希并保留历史输出。绘图只是观察，不能替代阶段质量、性能或容错验收；未采集的指标明确留空。

## 工作区维护与观察交接

由主控在同一个默认五分钟交互轮询中检查维护是否到期；有已登记缓存时调用一次 `scripts/maintain_workspace.py ... tick`，默认 dry-run。已明确配置自动清理的部署可按该 policy 加 `--enable-delete`，正常执行无需反复询问。只处理登记的可重建代次；老目录不自动迁移或删除，活跃/未知作业、lease、使用 pin 和原件引用继续保护。不要并行派多个清理者，也不要在每条 Agent 消息后扫工作空间。触发方式、缓存生产者与安装资源核对见 [维护与观察交接](references/maintenance.md)。

实际 TaskSpec context 改变时，沿该参考完成**独立观察 Store、事件 peer 和 sentinel**的交接，保留旧游标和证据；不能只换 parser state-dir 或删 watcher 状态。多节点分别核对所有必需 member 的身份、ready、心跳和退出回执；先核对固定引擎源码和真实日志中的进度输出节点（可能是 rank0、全局最后一个 rank 或专用 logger）；该节点的 iteration/loss 只代表该日志覆盖范围。主控离线期间仅由已部署守护继续监测，不能把轮询脚本视为自动运行 Agent。

## 多 Agent 拆解、交流与集成

1. 每个阶段依据真实证据动态拆任务，写出输入/输出与依赖图，不预设固定 Agent 名字、算子名单或数量。环境核对、配方阅读、系统分析可并行。先从模型调用/profile 得到算子热点，再按真实实现、shape/dtype/phase 拆分或合并，覆盖应评估的热点与未归因缺口。不同算子的详细分析和优化均可并行；本算子具备实施条件就可优化，不等所有算子分析结束。实施按独立文件/函数/机制划分，单个算子耦合的 kernel body 与 launch 配置由同一人负责。并发上限不是人数配额，新 profile 后重新判断优先级与分工。
2. `team-plan` 登记 owner、scope、allowed_paths、checkout、mode、resources、depends_on、peers、预算和验收。共享 context 和固定证据，依赖报告须先验收。真正独立的 checkout/设备才用不同 ID；同一 GPU/网络测量域串行或确认隔离。完整算子优化任务宜用 `resource_scope: operation`，仅在实际测量时领取/释放资源租约；也可拆开发与测试任务。其他算子继续开发，有独立设备时可并行测量，不把所有算子优化强制串行。
3. 依据 `team-next` 逐个 `assignment-claim`，再在宿主允许的范围内用原生多 Agent 工具派发，并 `assignment-bind` 实际 session ID。交给成员当前 token、输入哈希、允许范围、输出契约与收件规则。没有可用/获授权委派能力就顺序处理并说明，不能伪造会话或把领取叫作启动。
4. 主动发现接口问题、相互影响或新瓶颈就 `agent-send` 留存，再用宿主消息工具提示已绑定会话。被动方每次恢复、实验/提交前读 `agent-inbox`，先 seen、处理后 handled；回答由提问方确认。相关成员可直接交流，重要阻塞和跨范围变更交主控。运行中投递依赖宿主能力，不能假定写入收件箱就会唤醒 Agent，也不要为每条消息重启会话。
5. 等回答占着并发名额时，先确认执行结束和停止修改，`assignment-yield` 释放占用，恢复重新领取。不能向依赖自己完成的下游提出阻塞问题。成员失败保留其他结果；旧 context/token、未知远端作业先核对，不能自动超时重发。
6. `assignment-return --token` 给出准确输入哈希、结论、原始证据、限制和跨域影响；主控/另一 reviewer 通过 `assignment-review` 验收才解锁下游。统一计算/通信的分母、内存生命周期和数值约束，挑选兼容方案。主控集成后再做局部回归、profiler-off 测量、阶段 loss 及独立整体复核；不能将几个分别有效的改动视为组合后必然有效。

同一私有工作区内，显式 checkout/resource ID 跨任务共享预约；无 assignment 的主控命令也不能绕过已领取的资源范围。context 重置后即使切回原配置，仍需 flow-replan 和新验收。晚到的上游阻塞要重新检查整条依赖链。必做任务取消按 team-next 的 replan_required 明确重规划替代，不能仅追加新任务便把旧义务算完成。

命令与 JSON 以 `docs/multi-agent.md` 为准。团队消息事件及时处理，不受人的五分钟文件采集周期限制。成果由所属阶段交付，无需再增加细碎的独立 Skill。

本地会话在线才有主控推理。`flow-watch` 只记文件变化，不会凭空启动 Agent；离线唤醒需已配置的本地 bridge/宿主服务。远端 watcher 和既有容错独立运行，本机恢复后重放事件、核对现场再续接。没有配置时如实说明接续方式，不能承诺全天自动接管。

## 交付与边界

源码在独立开发 checkout 修改并同步远端，不能混用知识库缓存。成果由对应阶段负责：目标仓规范的改动、测试、回退与 PR，公开 Cookbook 只放可公开方法。原始日志、trace、数据和任务看板均留在私有工作区。整体 workflow 仍需真实 HCU 环境逐项验收，不把合成演示叫训练通过。

## 局部知识的使用与里程碑记录

开始任务、重要实验或排障前，按模型/环境/机制用 experience-search 检索私有经验，检查 context、测量条件、失败原因和 loss 状态。需要机制依据时调用 hcu-engine-wiki-search；本地不足必须主动搜线上 PR，再读完整讨论、最终 diff、固定源码、调用者和测试，不能只停在已有入口页。局部官方 Wiki 发现版本漂移可按需自主更新；HCU 大知识库不随本任务更新。

report 和 flow-advance 自动把原上下文与报告沉淀到私有 experience。到达环境验收、初始基线、重要候选、阶段 loss、扩容/恢复或结束里程碑后，确认写入成功；失败用 experience-sync 重放。按 docs/experience-knowledge.md 补充结构化解释记录，包括实际性能/显存口径、适用/失败条件和回退，不伪造测量，不把局部通过当成长训 loss 通过。只分析或诊断的任务同样记录已知与待验证项。

形成 Cookbook 最佳实践时，先关联基线/候选/验证经验 ID，再记录草稿、目标 PR、提交/合入/替代状态；公开内容单独审核脱敏，经验、日志、数据和内部链接留在私有工作区。该阶段负责自己成果的交付，不新增独立交付 Skill。
