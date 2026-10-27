# 工作流总览图生成说明

- 内容基准：HCU-TrainFlow 当前主线；所有流程图均不写工程版本号。
- 输出：[workflow-overview-native-tuning.png](workflow-overview-native-tuning.png)。首页使用摘要图，精确分支与验收门槛以[可编辑流程图](../workflow-map.md)和[能力边界](../capabilities.md)为准。
- 生成方式：内置 `imagegen`，以此前的总览图为编辑输入，采用白底、低饱和蓝灰 / 青灰 / 淡紫灰、细线边框与箭头，保留分阶段科技信息图结构及文字对比度。
- 维护：图面不印版本号；流程、状态或边界变更时一起复核 README、工程介绍和细图。重新生成后检查文字、箭头及验证声明。

## 本次完整提示词

```text
Edit the attached HCU-TrainFlow README overview infographic to reflect the current workflow. The existing image is the edit target and layout reference. Refine the design substantially: pure white canvas, nearly white panels, very pale desaturated blue-gray / teal-gray / lavender-gray accents, dark slate Chinese typography, fine hairline borders and arrows, small restrained thin-stroke icons. Make lines approximately HALF as thick as in the reference; remove the heavy saturated outlines and large vivid icons. The orange feedback accents must be muted warm gray-ochre, subtle but legible. Keep text dark and clearly readable: soften panel colors and lines, not the text. Use spacious margins, consistent subtle rounded corners, precise typographic hierarchy, clean technical editorial design. No gradients, glow, heavy shadows, thick arrows, saturated electric blue or violet. High resolution wide landscape 3:2 composition, ideally 2304 x 1536 or higher, with fully readable accurate Chinese. This is a technical workflow, not promotional art. Re-layout text cleanly as needed. No false dashboards or extra features. All panels inside safe margins. Never obscure text with arrows. Replace all wording with the following exact content, organized hierarchically. Do not add a project version number anywhere in the diagram.

TITLE: HCU-TrainFlow
SUBTITLE: 面向 HCU 大模型训练的全流程智能体协同工作流
scope: 预训练 · SFT · RL · Torch 原生训练
small mode line: 完整流程或独立阶段 · 仅环境 / 仅分析 / 仅诊断 / 仅交付

Top orchestration band:
本地主控 Agent
按证据拆解任务 · 动态并行协作 · 结果验收 · 独立复核
Show three boxes branching in parallel: 任务 A / 任务 B / 更多任务
small note: 依赖与资源决定并行，不固定算子名单

Three stage columns, center slightly wider, linked LEFT to CENTER then CENTER acceptance gate to RIGHT first card.

LEFT 01 title 环境检查与模型适配
card 1 环境与硬件基线
健康 · GEMM / HBM · 互联 / 通信
占用与权限 · 实际版本 · 可达性能
card 2 准确核对模型与 HCU 配方
活跃分支 · 环境脚本 · 用户 patch
结构 · 数据 · 精度 · 优化器语义
card 3 完整模型容量评估
并行布局 · 显存余量 · 短跑校准
放不下才缩层，其他变更按授权
card 4 跑通与初始数值基线
前向 / 反向 · 更新 · checkpoint
冻结源码、配置和比较条件
bottom note: 环境差距先排查 · 代理结果限定范围

CENTER 02 title 性能分析与优化
card 1 引擎原生能力与配置调优
官方 / 候选 PR / HCU 优化项
并行 · 显存 · 融合 · 编译 · 通信
card 2 稳态 profile + TraceLens
时间线 / Graph · 多 rank · 真实 shape
指标 → Agent 查证 → 瓶颈排序
card 3 优先解决主要耗时
空泡 / 通信 / 负载不均 / 计算
compile · overlap · 通算融合
card 4 重点算子：并行评估与验证
同 shape / EventReplay ↔ Roofline / 效率
≥90% 端到端热点中的非通信项逐项建模
未知项补证据，条件上限不等于整步收益
card 5 复用与实现迭代
优先复用现有算子库 / 通信库能力
能力或性能不足：基于对应库实现
算子 Skill · 迭代回归 · 无 profiler 实测
优化停止有依据

Orange outlined stage gate below center cards:
稳定阶段验收：同初态 A/B
loss · 整步净收益 · 显存 · 原始证据
Orange feedback arrow from this gate back to the first configuration card labeled 补齐依赖 / 回调配置
Blue pass arrow labeled 通过 from gate to RIGHT FIRST CARD (not directly long training).

RIGHT 03 title 规模扩展与长稳运行
card 1 验收目标配置，再扩 DP
必要时恢复完整模型
精度 / loss · 健康池 · 扩展效率
显存 / 通信 · 保存与恢复
card 2 既有容错与故障诊断
唯一恢复负责人 · 按部署授权
定位 → 修复验证 → 恢复 → 持续推进
恢复后复核训练状态与精度
card 3 持续观测与曲线
精度 / loss / 梯度 · 吞吐 · 显存
step / checkpoint · 训练进展
全部成员 · 观察器健康
card 4 已部署的远端守护持续运行
事件持久化 · 重放与去重
本机恢复后接续，告警 / 唤醒分别验收
bottom note: 达到约定条件后完成或交接
A separate orange ONE-WAY arrow from right panel back into center analysis area labeled 新瓶颈返回优化. It must not point toward the right panel.

Full-width feedback band:
实施 → 测量 → 独立复核 → 修正 / 推进
BOARD / GUIDANCE / QUESTIONS · 每 5 分钟采集指导与问题

Three bottom support panels of similar height, with concise exact text:
本地协同 · 远端执行
固定源码快照 → 编译 / 训练 / 采集
SSH / Docker / Conda / Slurm / K8s
超时或断线：先核查原作业

知识贯穿三个阶段
必装 HCU-Knowledge · 联查官方 Wiki / PR / 源码
共享 Wiki：官方资料 · 通用环境 · 最终模型总结
过程留任务档案 · 大知识库独立更新

交付与交接
训练引擎 · 算子库 · 通信库 · 相关工具
按改动归属提交 PR，关联依赖与验证
配方 · 精度 / 性能证据 · 回退 / 运行交接

Footer:
流程概览 · 具体分支、证据门槛与实测边界见工程文档

Aim for elegant clear readable technical documentation quality. Keep arrows sparse and precise. Do not insert logos, additional statistics, fabricated screenshots, checkmarks implying all capabilities passed, or any platform-wide validation claim.
```

本次使用内置 imagegen 精确编辑原概览图：仅扩展中间阶段首卡的上述三行，并将左侧反馈标注改为“补齐依赖 / 回调配置”，其余信息和风格保持。原生调优包括并行与显存，完整分支与失败回退以可编辑流程图为准。
