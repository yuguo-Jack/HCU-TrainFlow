---
name: hcu-train-optimize
description: 分析 HCU 大模型训练瓶颈，或推进系统与算子优化、局部回归及阶段 loss 验证；支持仅模型性能分析。
---

# HCU 训练性能分析与优化

支持 `analyze` 只交付性能分析，也支持 `optimize/full` 迭代。分析任务不自动改实现或长时验 loss。

## 优化闭环

1. **固定比较对象。** 初始基线不可覆盖；锁定源码、数据、环境、shape、拓扑、precision、sample/token 聚合和预算。未完成环境验收须标明对性能解释的限制。
2. **抓训练端到端剖面。** 优先使用实际 HCU 启动链已有的 torch profiler 支持，必要时对照官方实现接入；保留已验收的环境与 launcher，并记录采集所需改动。每个实际非单例并行组至少两个有代表性的 rank。保留完整稳态步和 phase，区分 fwd/bwd/optimizer/通信/数据/checkpoint；跨 rank 先校时。warmup、编译和 profiling 开销不能混进性能对照。
3. **先系统分析。** 空泡分数据、CPU launch、同步、PP 调度；通信分真实消息量、拓扑、wait、overlap 和最慢 rank。关注显存 reserved/allocated、图池、临时/通信 buffer，以及保存恢复峰值。`GPU_MAX_HW_QUEUES` 按目标 runtime 和对照实测调节，没有通用最佳值。
4. **复用 TraceLens。** 先用其已安装 CLI/API 做 op/kernel、overlap、collective 分析，核对输出单位/字段与 unsupported 情形。TrainFlow 补充训练契约、rank 覆盖和热点建模；轻量归因不冒充跨 rank 关键路径。
5. **融合粒度与数值对齐。** 对照 NV 实际调用、接口、fwd/bwd、saved tensors、cast/accumulation。先查最新 Flash-Train 已支持算子；TE 能力提交 HCU TE，通用编译/cuDNN frontend 训练融合优先 Flash-Train。优先复用，不重复开发。
6. **评估累计 ≥90% 端到端占比的热点集合。** 墙钟为分母，重叠不能重复累计，CPU/等待缺口不能删掉。其中每个非通信 op 按 shape/dtype/布局/phase 建立 FLOPs、HBM/其他有效流量或延迟模型，给理论/可达上限、当前效率、独立实测与优化决策。混合通算 kernel 仍评估计算部分；纯通信单列消息/拓扑/等待。缺模型或覆盖不足须明确补证据，不能报全覆盖。
7. **分发实施。** shape 相同的 attention/GEMM/通信独立测量与模型内比较，先解决干扰。rocBLAS 可按匹配教程 tune，hipBLASLt/grouped GEMM 提完整 size 工单给人。必要时看编译器/runtime/数学库/通信库对应分支源码；rocSHMEM 通算融合按瓶颈证据决定。
8. **算子流程。** 需要时调用 `$hygon-hip-baseline-generator`、`$hygon-hip-kernel-optimizer`、`$hygon-triton-kernel-optimizer`。kernel 遇到优化瓶颈必须做性能分析；hipprof 与 XProf/XCompute 的命令和产物分别使用，不混写。指令/反汇编问题按目标 ISA 和技能中的编译产物方法处理。
9. **验证。** 每轮候选做实际 dispatch、局部输出/梯度/参数更新与多 shape 回归，随后 profiler-off 重复测量。阶段候选稳定后再做冻结样本和容差的较长 loss 验收；不频繁长训，也不省略阶段验收。RL 加查 policy version、logprob、reward 和数据年龄。

## 重要参考

AMD Primus、华为 MindSpeed/MindSpeed-LLM、百度 LoongForge 与官方开发分支都是一级机制参考。先比较补丁基线/gitlink、触发条件、测试和回退；官方能力真正进入当前 HCU 分支且回归等价后再退役旧 patch。

## 输出

分析模式交付可复查的瓶颈报告、覆盖缺口、shape/效率表、优先级和建议实验。优化模式另交付候选源快照、成对实验、阶段 quality、回退和目标仓 PR。证据不足、收益平台期、反复数值异常或底层库缺能力时向用户报告最小证据包，方便专家介入。

## 运行约定

先定位 HCU-TrainFlow checkout（用户给定路径或 `TRAINFLOW_PROJECT`）和私有 `TRAINFLOW_WORKSPACE`。不要把 site、数据、模型、日志或凭据写进公共仓。CLI 用 `hcu-trainflow --workspace <private-path>`；源码环境可用 `python -m hcu_trainflow`。先读项目 `docs/quickstart.md` 和当前任务上下文，再按需读相关章节。

主 Agent 在本地主控，专家分工记录 owner、scope、允许修改路径、预算与验收证据。运行代码使用独立开发 checkout 和不可变源快照；远端只执行明确命令/守护，不要求部署模型 Agent。TaskSpec 的 execute/sync/notify 权限是任务约定，不是 OS 安全沙箱。实际节点、容器、Pod UID、Slurm allocation 由部署任务确认。

需要 HCU 事实、历史案例或底层实现时使用可用的 `$hcu-knowledge-search`；也可以读当前对应分支源码和公开官方文档。知识检索不自动更新 HCU 大知识库。本工作流只维护自己的局部官方 Wiki；具体依赖命令升级时同步复核 Skill/适配器，不能仅改 Wiki。

产物归属本 Skill：按目标仓规范准备集中、通用的改动、测试、PR 说明和回退方式。公开 PR/Cookbook 只含脱敏的可公开方法与必要代码，不上传任务数据。遵循当前会话已给出的提交/发布授权。
