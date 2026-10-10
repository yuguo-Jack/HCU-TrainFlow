# Workflow overview image source

Version: **0.5.0**. Generated with the built-in imagegen tool using the previous white technology-style overview as the visual reference. The [project introduction](../project-overview.md) explains the method; the [editable workflow map](../workflow-map.md) gives the precise branches and acceptance rules. The illustration does not expand the [hardware validation scope](../capabilities.md).

## Reproduction prompt

```text
Redesign the supplied HCU-TrainFlow README workflow infographic for version 0.5.0. Use the old image as a STYLE reference: white background, refined flat technical infographic, pale blue/teal/lavender panels, dark navy Chinese typography, thin connectors, small orange feedback arrows. Maintain its attractive three-column composition but REPLACE ALL CONTENT with the wording below. It is a precise technical workflow, not promotional artwork. Wide landscape 3:2, highest available resolution; readable Chinese, no 3D, no dark background, no fake dashboards. Make the center column slightly wider. Preserve generous margins, hierarchy and straight unambiguous arrow routing. No additional text or claims.

TITLE: HCU-TrainFlow
SUBTITLE: 面向 HCU 大模型训练的全流程智能体协同工作流
small scope: 预训练 · SFT · RL · Torch 原生训练

Top full-width orchestration band:
本地主控 Agent
任务拆解 · 并行协作 · 证据验收 · 独立复核
Three parallel boxes connected by branching lines, never serial: 任务 A / 任务 B / 更多任务
small: 按实际热点分工 · 隔离资源测量

THREE STAGE PANELS:

LEFT 01 pale blue title 环境验收与模型适配
four stacked cards:
环境与硬件基线
健康 · GEMM / HBM · 互联 / 通信
资源占用 · 实际版本 · 可达性能

核对 HCU 启动配方
环境脚本 · 活跃分支 · 用户 patch
模型结构 · 数据 · 优化器语义

完整模型容量评估
并行布局 · 显存余量 · 短跑校准
放不下才缩层，其他变更按授权

跑通与初始数值基线
前向 / 反向 · 更新 · checkpoint
冻结源码、配置和比较条件
bottom note: 代理结果保留适用范围

CENTER 02 pale teal title 性能分析与优化
five stacked cards:
并行切分与显存权衡
TP / PP / DP / CP / EP · 微批 / 重算

端到端 profile + TraceLens
实际并行组 · 代表 rank · 稳态窗口
空泡 / 通信 / 计算：按主要占比推进

系统与通信优化
输入流水 · compile · 调度
overlap · 通算融合 · 资源竞争

重点算子：两条并行分析线
同 shape 独立实测 ↔ 上限建模
≥90% 端到端热点中的非通信算子

复用与迭代实现
HCU TE / Flash-Train / Primus Turbo
Baseline → HIP · Triton 优化
按收益排序 · 局部回归 · 停止有依据

Bottom orange validation gate:
阶段验收：同初态 A/B
loss · 性能 · 显存 · 原始证据
A failure loop labelled 修正 back to center implementation card. A pass connector labelled 通过 must lead to top first card of RIGHT panel, not straight to long-training.

RIGHT 03 pale lavender title 扩 DP 域与持续容错
four stacked cards:
验收目标配置，再扩 DP
必要时恢复完整模型
健康池 · 扩展效率 · 显存 / 通信

接入既有容错
唯一恢复负责人 · 按部署授权
故障识别 → 清理 → 恢复 → 推进

持续观测与曲线
step · loss · 吞吐 · 显存
checkpoint · 全部成员 · 观察器

已部署的远端守护持续运行
事件持久化 · 重放与去重
本机恢复后接续，唤醒需部署
bottom: 达到约定条件后完成或交接

Arrows: left to center. Center gate passed to right FIRST card. Subtle orange arrow from RIGHT down and back into CENTER labelled 新瓶颈返回优化. No arrow text overlay.

Full-width review band below:
实施 → 测量 → 独立复核 → 修正 / 推进
BOARD / GUIDANCE / QUESTIONS · 每 5 分钟采集指导

Two bottom support boxes:
本地协同 · 远端执行
固定源码快照 → 编译 / 训练 / 采集
SSH / Docker / Conda / Slurm / K8s
超时或断线：先核查原作业

HCU-Knowledge 贯穿三个阶段
联查官方 Wiki / PR / 对应分支源码
共享 Wiki：官方资料 · 通用经验 · 最终里程碑
局部 Wiki 按需更新，大知识库独立维护

FOOTNOTE:
0.5.0 · 流程方法与实际验收范围分别记录 · 详见工程介绍与工作流全景
```

## Final targeted edit

Keep the generated layout and all other wording unchanged. In the fourth card of the right column, use the heading `已部署的远端守护持续运行`, retaining the event-replay and wake-up deployment notes. Make `新瓶颈返回优化` a one-way orange feedback arrow toward the center optimization loop; remove the arrowhead pointing into the right column. Preserve the blue acceptance path into the first scaling card.
