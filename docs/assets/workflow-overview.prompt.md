# Workflow overview image source

The README illustration is generated with the built-in imagegen tool. Its technical source is [the editable workflow map](../workflow-map.md); update the illustration when the workflow changes. This is a presentation asset, not a substitute for the contracts and implementation references in that document. For revisions, use the checked-in PNG as a style reference and the editable workflow map as the content authority. The shorter final copy keeps text legible at README image size.

## Final readable composition

```text
Use case: infographic-diagram.
Create the final README workflow poster for HCU-TrainFlow. Use the attached image ONLY as a style reference: midnight navy technical grid, cyan/teal/indigo glowing panels, elegant engineering typography and small line icons. REDESIGN THE TEXT with the shorter exact copy below so every word is LARGE, CRISP and correct. Do not copy any old small text from the reference. This is a new clean typesetting pass, not a pixel patch. Highest resolution available, landscape 3:2. Professional, futuristic, beautiful, clear. No decorative slogans, tiny filler text or invented labels. No dense paragraphs. Use bright near-white body text with ample line spacing.

TOP:
Title “HCU-TrainFlow”
Subtitle “面向 HCU 大模型训练的全流程智能体协同工作流”
Badge “预训练 · SFT · RL”
Coordinator bar: “本地主控 Agent”
Second line “任务拆解 · 并行派发 · 消息交互 · 证据验收”
Three generic capsules connected independently to ONE dispatch bus, NOT sequentially:
“任务 A” “任务 B” “更多任务”
Small caption “独立算子并行 · 共享测量排队”

MAIN CONTENT:
Three tall adjacent panels with generous gutters. Stage 02 slightly wider. First panel connects rightward to second panel. Third panel can only be reached through the pass branch of the bottom gate of panel 02. Do not add any other 02→03 arrow. Numbering and arrows convey sequence.

PANEL 01 exact heading:
“01  环境验收与模型适配”
Card 1 title “环境与全节点验收”
Card 1 body “Cluster Manager / run nhc / DTK”
Card 1 body “GEMM · HBM · 互联 · 通信”
Card 2 title “复用当前 HCU 启动配方”
Card 2 body “分支 · 环境变量 · 依赖 · 用户 patch”
Card 3 title “最小跑通与初始数值基线”
Card 3 body “输出 · 梯度 · 优化器 · checkpoint”
Card 4 title “任务语义核对”
Card 4 body “SFT：模板 / loss mask”
Card 4 body “RL：rollout / 权重同步”
At bottom concise note “缺失或失败：补证据、修复后重验”

PANEL 02 exact heading:
“02  性能分析与优化”
Card 1 title “并行切分 × 显存预算”
Card 1 body “TP / PP / DP / CP / EP / SP”
Card 1 body “微批 · 重算 · 余量 · 通信与吞吐”
Card 2 title “端到端 profile + TraceLens”
Card 2 body “每个实际非单例组至少 2 个代表 rank”
Card 2 body “空泡 · overlap · 显存 · HW Queues”
Card 3 title “热点上限与当前效率”
Card 3 body “≥90% 端到端热点中的非通信算子建模”
Card 3 body “真实 shape · FLOPs / Bytes · 独立实测”
Card 4 title “融合对齐，优先复用”
Card 4 body “HCU TE / Flash-Train”
Card 4 body “HIP / Triton Skill · 局部正确性与性能”
Bottom gate, with very clear larger text:
“稳定阶段：loss 与性能通过？”
Small note directly under gate:
“对照初始基线；不逐轮长时验 loss”
Gate YES: a solid CYAN connector from its RIGHT tip labelled “通过”, along the EMPTY gutter between stage 02 and stage 03, into the FIRST card of stage 03. Gate NO: an AMBER dashed connector from its LEFT tip labelled “未通过”, back up to the optimization work inside stage 02. The pass and fail routes must be separate and clearly connected to the gate. Don't cross text, icons or each other. Reserve actual space for the loop.

PANEL 03 heading:
“03  扩容验证与长训守护”
Card 1 title “完整模型最小 DP 域”
Card 1 body “筛机 → 健康池 → 扩容验收”
Card 2 title “持续监测与曲线”
Card 2 body “step · loss · 吞吐 · 显存”
Card 2 body “checkpoint · watcher 心跳”
Card 3 title “故障诊断与既有容错”
Card 3 body “唯一恢复负责人 · 按部署授权”
Card 4 title “本机离线，远端守护继续”
Card 4 body “本机恢复 → 事件重放 → Agent 接续”
Panel footer:
“达到约定条件后完成 / 交接”

SHARED LOOP BAR BELOW ALL THREE PANELS:
Heading “全程证据与独立复核”
Connected labeled arrows “实施 → 测量 → 独立复核 → 修正 / 推进”
Second line “BOARD / GUIDANCE：每 5 分钟采集指导”
Make dashed links from shared bar to all three panels.

BOTTOM TWO FOUNDATION BOXES, equally weighted:
LEFT title “本地协同 · 远端执行”
line “独立 checkout → 固定快照 → 远端编译与测量”
line “SSH / Docker / Conda / Slurm / K8s”
line “超时或断线：先核查原作业”
RIGHT title “知识检索 · 经验沉淀”
line “官方 Wiki / PR / 源码 · 按需 HCU-Knowledge”
line “局部 Wiki 按需更新；大知识库单独维护”
line “性能 / loss / 故障 → 私有经验与交付记录”

FOOTER, clearly legible:
“工作流机制示意 · 真实 HCU 环境与站点接续仍需联调”

Important accuracy rules: typeset DTK with K, never DTX. Preserve ≥90% not just >90%. Do not invent benchmark results or claim deployment is already validated. Never replace the required local-correctness wording with “避免”. Do not automatically connect Agent A to B sequentially. Keep all the supplied text exactly but nothing else. An attractive, information-rich and readable Chinese engineering poster, not a decorative sci-fi scene.
```
