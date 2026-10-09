# Workflow overview image source

The README illustration is generated with the built-in imagegen tool. Its technical source is [the editable workflow map](../workflow-map.md); update the illustration when the workflow changes. This is a presentation asset, not a substitute for the contracts and implementation references in that document. For revisions, use the checked-in PNG as a style reference and the editable workflow map as the content authority. The shorter final copy keeps text legible at README image size.

## White technology composition

```text
Use case: infographic-diagram.
Create a NEW polished WHITE-BACKGROUND workflow infographic for the HCU-TrainFlow README, landscape 3:2, highest available resolution.

INPUT ROLES:
Image 1 (the dark HCU-TrainFlow diagram) is the CONTENT AND LOGICAL STRUCTURE reference. Keep its TrainFlow-specific scope, three stages, parallel Agents, validation gate and supporting mechanisms, with the exact copy below.
Image 2 (the white hygonpilot-skills diagram) is ONLY a STYLE / COLOR / TYPOGRAPHY reference. Do not copy its project name, six-stage workflow, named Skills, AOTI/bisect blocks or any capability into TrainFlow.

STYLE:
Pure white canvas. Flat, precise, elegant technology infographic matching Image 2's clean white appearance. Very pale blue, mint and lavender panel fills; thin crisp blue/teal/violet outlines; dark navy body text. Orange is reserved for the verification gate and retry route. Rounded rectangles, numbered circular badges, large sparse line icons, generous whitespace, consistent alignment and text hierarchy. Subtle pastel supporting bands. No dark areas, black panels, neon, glow, sci-fi grid, perspective, mountains, decorative slogans or heavy shadows. Maintain excellent readability at README width. Re-typeset the supplied short copy clearly rather than retaining fuzzy old lettering.

MAIN DESIGN:
Header and local coordinator band; three primary columns (blue adaptation, teal optimization, violet training/monitoring), with the middle column a little wider; cross-cutting evidence/review strip; two foundation panels. Preserve logical arrows exactly: stage 01 → stage 02; the center quality gate is the ONLY route into stage 03; separate orange failure loop back into optimization. Parallel Agent capsules branch independently from a shared dispatch bus.
All supplied Chinese and technical labels below must be accurate. No additional claims or text.

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
Gate YES: a solid BLUE connector from its RIGHT tip labelled “通过”, along the EMPTY gutter between stage 02 and stage 03, into the FIRST card of stage 03. Gate NO: an ORANGE dashed connector from its LEFT tip labelled “未通过”, back up to the optimization work inside stage 02. The pass and fail routes must be separate and clearly connected to the gate. Don't cross text, icons or each other. Reserve actual space for the loop.

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

Important accuracy rules: typeset DTK with K, never DTX. Preserve ≥90% not just >90%. Do not invent benchmark results or claim deployment is already validated. Never replace the required local-correctness wording with “避免”. Do not automatically connect Agent A to B sequentially. Keep all the supplied text exactly but nothing else. An attractive, information-rich and readable Chinese engineering poster, not a decorative illustration. The overall white layout and pastel line-art treatment must match the provided style reference.
```

## Connector refinement

```text
Edit only ONE missing connector in this WHITE HCU-TrainFlow infographic. Everything else must remain unchanged, including all typography, wording, colors, icons, panels and layout.

The blue “通过” arrow from the center bottom diamond currently ends at the panel gutter around (1050,670). The separate blue arrow into the first card of stage 03 is around (1055,310). They must be ONE connected pass path, not two disconnected arrows.

Draw a clearly visible solid blue connector in the white vertical gutter BETWEEN panels 02 and 03: extend the diamond's passed line horizontally to x≈1055 at y≈670, then turn UP along x≈1055 to y≈310, then turn RIGHT into the existing arrow entering the first stage-03 card “完整模型最小 DP 域”. Use an obvious 3–4 pixel medium-blue stroke, right angles, and the single destination arrowhead. Remove the intermediate arrowhead at the bottom bend if necessary so the pass route reads as one continuous line. Do not draw over any text or panel interior. The left orange failure loop stays unchanged.

No changes to any Chinese or English letters. Keep pure white background, pale pastel panels and exact original composition. Do not regenerate or rewrite the diagram.
```
