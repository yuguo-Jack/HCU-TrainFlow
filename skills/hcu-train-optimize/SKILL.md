---
name: hcu-train-optimize
description: 分析 HCU 大模型训练瓶颈，或推进系统与算子优化、局部回归及阶段 loss 验证；支持仅模型性能分析。
---

# HCU 训练性能分析与优化

支持 `analyze` 只交付性能分析，也支持 `optimize/full` 迭代。分析任务不自动改实现或长时验 loss。

## 优化闭环

1. **固定比较对象。** 初始基线不可覆盖；锁定源码、数据、环境、shape、拓扑、precision、sample/token 聚合和预算。未完成环境验收须标明对性能解释的限制。
2. **先评估并行切分与显存预算。** 结合模型、卡数、机内/机间拓扑和实际 HCU 配方，参考局部 Wiki 的 `official-megatron-wiki/parallelism.md` 及官方并行/性能教程，比较 TP/PP/DP/CP/EP、SP、微批/梯度累积、重算与状态分片。先估最吃紧 rank 的峰值和必要余量，再以短跑实测吞吐、通信、PP 空泡和显存校准；不把显存填满作为目标。保持模型、有效全局 batch/token、精度与优化器语义可比；记录候选矩阵，选定布局后更新 rank 分组与算子 shape，再深入优化。只分析模式给建议，不擅自试跑。详见项目 `docs/workflows.md`。
3. **抓训练端到端剖面。** 优先使用实际 HCU 启动链已有的 torch profiler 支持，必要时对照官方实现接入；保留已验收的环境与 launcher，并记录采集所需改动。每个实际非单例并行组至少两个有代表性的 rank。保留完整稳态步和 phase，区分 fwd/bwd/optimizer/通信/数据/checkpoint；跨 rank 先校时。warmup、编译和 profiling 开销不能混进性能对照。
4. **先系统分析。** 空泡分数据、CPU launch、同步、PP 调度；通信分真实消息量、拓扑、wait、overlap 和最慢 rank。关注显存 reserved/allocated、图池、临时/通信 buffer，以及保存恢复峰值。`GPU_MAX_HW_QUEUES` 按目标 runtime 和对照实测调节，没有通用最佳值。
5. **复用 TraceLens。** 按项目 docs/integrations.md 安装锁定依赖，用 `tracelens-report TRACE --project PROJECT --rank RANK` 做 op/kernel、overlap 分析；完整 ranks 才用 `tracelens-collective`。检查日志、非空表、单位、统计分母及 unsupported 情形。原生表保留在私有 workspace，`generated` 不代表训练评估通过。TrainFlow 补充稳态窗口、实际 rank 分组、shape 与热点建模；不默认套用 AMD/NV 峰值，轻量归因不冒充跨 rank 关键路径。
6. **融合粒度与数值对齐。** 对照 NV 实际调用、接口、fwd/bwd、saved tensors、cast/accumulation。先查最新 Flash-Train 已支持算子；TE 能力提交 HCU TE，通用编译/cuDNN frontend 训练融合优先 Flash-Train。优先复用，不重复开发。
7. **评估累计 ≥90% 端到端占比的热点集合。** 墙钟为分母，重叠不能重复累计，CPU/等待缺口不能删掉。其中每个非通信 op 按 shape/dtype/布局/phase 建立 FLOPs、HBM/其他有效流量或延迟模型，给理论/可达上限、当前效率、独立实测与优化决策。混合通算 kernel 仍评估计算部分；纯通信单列消息/拓扑/等待。缺模型或覆盖不足须明确补证据，不能报全覆盖。
8. **分发实施。** shape 相同的 attention/GEMM/通信独立测量与模型内比较，先解决干扰。rocBLAS 可按匹配教程 tune，hipBLASLt/grouped GEMM 提完整 size 工单给人。必要时看编译器/runtime/数学库/通信库对应分支源码；rocSHMEM 通算融合按瓶颈证据决定。
9. **算子流程。** 需要时调用 `$hygon-hip-baseline-generator`、`$hygon-hip-kernel-optimizer`、`$hygon-triton-kernel-optimizer`。先确认可用；缺失时按 docs/integrations.md 获取 thirdparty/cuda-optimized-skill 并安装，也可读取其 skills/<name>/SKILL.md 及配套资源。kernel 遇到优化瓶颈必须做性能分析；hipprof 与 XProf/XCompute 的命令和产物分别使用，不混写。指令/反汇编问题按目标 ISA 和技能中的编译产物方法处理。
10. **验证。** 每轮候选做实际 dispatch、局部输出/梯度/参数更新与多 shape 回归，随后 profiler-off 重复测量。阶段候选稳定后再做冻结样本和容差的较长 loss 验收；不频繁长训，也不省略阶段验收。RL 加查 policy version、logprob、reward 和数据年龄。

## 重要参考

TraceLens 使用 thirdparty 清单锁定的 HCU fork，保留上游完整模块和原生 CLI。两个 TrainFlow 报告入口之外，按任务需要复用 TraceDiff、graph 报告、trace 分段/索引、源码定位及 EventReplay，具体依赖和入口见 docs/integrations.md。原生命令仍要遵循任务执行权限并记录私有输入/产物；缺少架构模型或事件映射时先标注缺口，优先用现有扩展点，必要的核心修改在独立 fork 开发 checkout 中完成并补回归。

TE 精度、权重缓存、attention backend、userbuffers 和融合查 `knowledge/official-transformer-engine-wiki/`；cuDNN graph/plan、SDPA fwd/bwd、open-kernel 融合和 host 缓存查 `knowledge/official-cudnn-frontend-wiki/`。先读 Wiki 再定位目标版本源码与教程，保留 NV/HCU 实现边界和实际 dispatch 证据。

AMD Primus、华为 MindSpeed/MindSpeed-LLM、百度 LoongForge 与官方开发分支都是一级机制参考。先比较补丁基线/gitlink、触发条件、测试和回退；官方能力真正进入当前 HCU 分支且回归等价后再退役旧 patch。

## 可并行的分析与实施

固定 trace 后，可并行分析 CPU/空泡、计算/shape/上限、通信/并行域、显存/生命周期，各自保留原始证据并及时交流互相影响（如 overlap 下的 GEMM 变慢、重算与峰值显存）。所有 lane 使用同一窗口、rank 映射和墙钟分母；不能分别删去各自不擅长的时间再相加。

Agent 分工由实际模型调用和 profile 决定，不预设固定名称、算子类别或人数。先得到足以派发的热点清单，再按真实算子/源码位置、shape、dtype、前后向和实现路径动态拆分或合并任务；对应 `profile-analyze` 的 operator key 与原始 trace，补足其未覆盖的调用与 shape 信息。逐项覆盖应建模的非通信热点，不局限于少数常见算子。

**不同算子的详细分析与优化均可并行推进。** 本算子的分析有依据后即可进入局部优化，其他算子可仍在分析或优化，不设置全体分析结束的统一等待点。按不重叠代码区域或独立候选 checkout 分工，接口、数值契约与保存状态先约定；耦合的 kernel body 和 launch 参数由同一 owner 负责。独立 GPU 可并行测量，共享 GPU 只将实际占用设备的验证排队，开发/编译仍可继续；完整优化任务可选 `resource_scope: operation`，仅在命令执行时领取/释放租约。按 `docs/multi-agent.md` 登记实际依赖、peer、资源和验收。

单个 kernel 内部沿用原 Hygon Skill 的实测迭代，不强制再拆多 Agent 讨论。结论有疑问就定向提问/共享证据；主控选择兼容组合，集成后重新做局部正确性、隔离性能和阶段 loss 验证。新 profile 出现新热点时动态调整分工，不能沿用过时任务名单。

## 阶段产物

分析模式交付可复查的瓶颈报告、覆盖缺口、shape/效率表、优先级和建议实验。优化模式另交付候选源快照、成对实验、阶段 quality、回退和目标仓 PR。证据不足、收益平台期、反复数值异常或底层库缺能力时向用户报告最小证据包，方便专家介入。

## 与统一主控衔接

由 `$hcu-trainflow` 调用时，沿用当前任务、目标和私有工作区；本阶段负责实际领域工作，主控负责 `flow-next`、独立复核和推进。交付候选源/配置清单、原始证据和绑定 candidate_snapshot 的报告；不要另起无关联任务，也不要绕开复核直接推进状态。人的 GUIDANCE.md 默认每 5 分钟由主控采集，成员检查已采集指导并回应，不各自频繁读文件；明确记录收益、数值/显存代价、未完成项和需要专家判断的问题。完整契约见项目 `docs/collaboration.md`。本 Skill 仍可按用户指定独立使用，不强制开展全流程。

## 运行约定

先定位 HCU-TrainFlow checkout（用户给定路径或 `TRAINFLOW_PROJECT`）和私有 `TRAINFLOW_WORKSPACE`。不要把 site、数据、模型、日志或凭据写进公共仓。CLI 用 `hcu-trainflow --workspace <private-path>`；源码环境可用 `python -m hcu_trainflow`。先读项目 `docs/quickstart.md` 和当前任务上下文，再按需读相关章节。

主 Agent 在本地主控，专家分工记录 owner、scope、允许修改路径、预算与验收证据。运行代码使用独立开发 checkout 和不可变源快照；远端只执行明确命令/守护，不要求部署模型 Agent。TaskSpec 的 execute/sync/notify 权限是任务约定，不是 OS 安全沙箱。实际节点、容器、Pod UID、Slurm allocation 由部署任务确认。

需要 HCU 事实、历史案例或底层实现时使用可用的 `$hcu-knowledge-search`；也可以读当前对应分支源码和公开官方文档。知识检索不自动更新 HCU 大知识库。本工作流只维护自己的局部官方 Wiki；具体依赖命令升级时同步复核 Skill/适配器，不能仅改 Wiki。

产物归属本 Skill：按目标仓规范准备集中、通用的改动、测试、PR 说明和回退方式。公开 PR/Cookbook 只含脱敏的可公开方法与必要代码，不上传任务数据。遵循当前会话已给出的提交/发布授权。

## 局部知识的使用与里程碑记录

开始任务、重要实验或排障前，按模型/环境/机制用 experience-search 检索私有经验，检查 context、测量条件、失败原因和 loss 状态。需要机制依据时调用 hcu-engine-wiki-search；本地不足必须主动搜线上 PR，再读完整讨论、最终 diff、固定源码、调用者和测试，不能只停在已有入口页。局部官方 Wiki 发现版本漂移可按需自主更新；HCU 大知识库不随本任务更新。

report 和 flow-advance 自动把原上下文与报告沉淀到私有 experience。到达环境验收、初始基线、重要候选、阶段 loss、扩容/恢复或结束里程碑后，确认写入成功；失败用 experience-sync 重放。按 docs/experience-knowledge.md 补充结构化解释记录，包括实际性能/显存口径、适用/失败条件和回退，不伪造测量，不把局部通过当成长训 loss 通过。只分析或诊断的任务同样记录已知与待验证项。

形成 Cookbook 最佳实践时，先关联基线/候选/验证经验 ID，再记录草稿、目标 PR、提交/合入/替代状态；公开内容单独审核脱敏，经验、日志、数据和内部链接留在私有工作区。该阶段负责自己成果的交付，不新增独立交付 Skill。
