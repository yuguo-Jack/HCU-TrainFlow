# Workflow overview image source

Generated with built-in imagegen. The content authority is [the editable workflow map](../workflow-map.md). The previous white overview is the style/composition reference. Workflow requirements do not imply completed HCU hardware validation.

## Reproduction prompt

```text
Redesign the attached HCU-TrainFlow README workflow infographic. Use the attached image ONLY as the established visual style and general three-column composition; replace its content with the EXACT updated wording below. White background, elegant technological flat-vector appearance, pale blue/teal/lavender panels, dark navy sharp Chinese typography, thin blue outlines, orange validation feedback. High legibility, crisp Chinese text. Landscape 3:2, highest available resolution. No dark background, no neon or 3D. Do not retain old obsolete text “最小 DP 域”. Balance density with generous margins. Make center optimization panel wider than side panels. No logos from other projects.

TITLE: “HCU-TrainFlow”
SUBTITLE: “面向 HCU 训练的全流程智能体协同工作流”
Scope small text: “预训练 · SFT · RL · 视频生成 · VLA · 世界模型”

TOP full-width coordinator band:
“本地主控 Agent”
“任务拆解 · 并行派发 · 消息交互 · 证据验收”
Three independent small boxes “任务 A” “任务 B” “更多任务” connected from a shared horizontal bus, NOT sequential.
Right note “独立优化并行 · 共享测量协调”

MAIN PANEL 01 pale blue: “环境验收与模型适配”
4 cards, stacked:
“环境与全节点验收”
“Cluster Manager / run nhc / DTK”
“GEMM · HBM · 互联 · 通信”

“优先复用 HCU 配方”
“当前分支 · 环境变量 · 用户 patch”

“跑通与初始数值基线”
“输出 · 梯度 · optimizer · checkpoint”

“核对实际训练语义”
“数据 / shape / mask / loss”
“SFT · RL · Torch 原生训练”
Bottom small orange note:
“资源不足可仅缩 layer 跑通或筛机”
“代理结果不代替完整模型验证”

Panel 01 arrow right into Panel02 (normal sequential progression).

MAIN PANEL02 wider pale teal: “性能分析与优化”
5 compact cards stacked, each readable:
“并行切分 × 显存预算”
“布局 · 微批 · 累积 · 重算 · 余量”

“端到端 profile + TraceLens”
“每个实际非单例组至少 2 个代表 rank”
“空泡 · 慢 rank · 显存 · 调度”

“Torch 原生训练专项”
“输入流水 · compile · 断图 / 重编译”
“前向 / 反向 · DDP / FSDP”

“通信 overlap 与通算融合”
“暴露时间 · bucket / chunk · 预取”
“依赖同步 · 资源竞争 · 整步净收益”

“热点建模与实现优化”
“≥90% 端到端热点中的非通信算子”
“上限 / 效率 · HCU TE / Flash-Train”
“优先复用 · HIP / Triton Skills”
Under cards small line: “按收益与风险排序 · 每轮局部回归”
At panel bottom an orange outlined validation diamond:
“稳定阶段：loss 与性能通过？”
small note under: “对照初始基线；不逐轮长时验 loss”
Diamond failure arrow labeled “未通过” loops back UP along left gutter within center panel to optimization.
Diamond pass arrow labeled “通过” must be a CONTINUOUS solid BLUE line leading along gutter between panels02/03 up to the FIRST card of panel03. Do not let it float/disconnect or point straight into long-training. Do not draw over text.

MAIN PANEL03 pale lavender: “扩 DP 域与长训守护”
4 cards stacked:
“恢复完整模型，再扩 DP”
“可行布局验证 → 逐级扩 DP”
“健康池 · 显存 / 通信 / 扩展效率”

“持续监测与曲线”
“step · loss · 吞吐 · 显存”
“checkpoint · watcher 心跳”

“故障诊断与既有容错”
“唯一恢复负责人 · 按部署授权”

“本机离线，远端守护继续”
“本机恢复 → 事件重放 → Agent 接续”
Bottom strip:
“达到约定条件后完成 / 交接”

Below3panels full-width slim review loop:
“全程证据与独立复核”
“实施 → 测量 → 独立复核 → 修正 / 推进”
“BOARD / GUIDANCE：每 5 分钟采集指导”

BOTTOM two support boxes:
Left title “本地协同 · 远端执行”
“独立 checkout → 固定快照 → 远端编译与测量”
“SSH / Docker / Conda / Slurm / K8s”
“超时或断线：先核查原作业”
Right title “HCU-Knowledge 贯穿三个阶段”
“完整安装必需 · 支持复用已有知识库”
“联查官方 Wiki / PR / 源码 · 私有经验沉淀”
“局部 Wiki 按需更新；大知识库单独维护”

FOOTNOTE:
“工作流机制示意 · 真实 HCU 环境与站点接续仍需逐项验证”

Do not add any new claims or mandatory special agent roster. All labels must be grammatically precise Chinese. Avoid extra decorative text. Retain the clean attractive white technology style, large stage numbers 01/02/03, sparse outlined icons, strictly aligned cards.
```
