---
name: hcu-train-optimize
description: 分析 HCU 训练引擎及 Torch 原生训练瓶颈，推进系统、通信与算子优化、局部回归及阶段 loss 验证；支持仅模型性能分析。
---

# HCU 训练性能分析与优化

支持 `analyze` 只交付性能分析，也支持 `optimize/full` 迭代。分析任务不自动改实现或长时验 loss。

先识别实际训练执行路径：大型引擎按既有并行与融合路线；Torch 原生训练（包括视频生成、VLA、世界模型）按 [Torch 训练专项](references/torch-native-training.md) 补查输入流水、eager/compile、断图/重编译、autograd、DDP/FSDP 和实际 backend。引擎内部模块也可采用该专项，不另建一套流程。环境适配和扩 DP/容错继续复用另外两个阶段。

## 优化闭环

沿适配阶段固定的执行工作分支推进。本轮优化完成不等于完整训练工作流完成；扩 DP、容错和持续监测尚未验证时，保持最终主仓整合 deferred。可参考最新主仓/第三方源码并移植必要修复，不为交付目标提前替换执行基线。执行基线与交付目标的顺序见 adapt Skill 的 `references/workflow.md`。

**先复用已有验证。** 开始候选前检查已有数值、dispatch、性能和阶段 loss 证据，记录源码/库/配置差异究竟影响哪层。固定实现、ABI、shape/dtype 和数值契约未变的独立算子测试直接引用；换训练分支通常先补集成与端到端对照，不重跑整套底层资格测试。确有调用/梯度生命周期、依赖版本或覆盖缺口时只补受影响用例，写明重测原因。稳定候选再做一次阶段 loss 验收；不要以反复资格测试代替推进新优化。

**并行组织热点工作。** 获取固定模型 profile 和真实调用契约后，“同 shape 独立实测与模型内对照”和“上限评估、融合挖掘与实现优化”是可并行的两条工作线，不以全部单测完成作为启动分析的前提。按实际热点把不同算子或实现独立的算子族分给不同成员；上限初估可先基于源码、FLOPs/字节量和匹配硬件参考，实测返回后修正效率、剩余空间及优先级。分析发现新的 shape/数值/dispatch 条件，应反向补充重放契约。模型内外差距指向竞争或等待时，与系统/通信负责人共享证据，避免只重写 kernel。共享 GPU/NIC/带宽上的性能测量串行，有可核验隔离资源才并行测；开发与 CPU 分析不必等待测量资源。每个可用候选独立验收并及时交流，最终在同一固定模型实例验证组合收益与数值，稳定阶段统一验 loss。任务依赖、编辑范围和结果验收遵循主控 Skill 的团队协议，不能为满足并行形式机械增加 Agent。

1. **固定比较对象。** 初始基线不可覆盖；锁定源码、数据、环境、shape、拓扑、precision、sample/token 聚合和预算。未完成环境验收须标明对性能解释的限制。
2. **先评估并行切分与显存预算。** 延续适配阶段容量判断，资源足够时优先完整参数配置，必要时参考 HCU Train Sim 并以实际短跑校准，不能习惯性缩层。 结合模型、卡数、机内/机间拓扑和实际 HCU 配方，参考局部 Wiki 的 `official-megatron-wiki/parallelism.md` 及官方并行/性能教程，比较 TP/PP/DP/CP/EP、SP、微批/梯度累积、重算与状态分片。先估最吃紧 rank 的峰值和必要余量，再以短跑实测吞吐、通信、PP 空泡和显存校准；不把显存填满作为目标。保持模型、有效全局 batch/token、精度与优化器语义可比；记录候选矩阵，选定布局后更新 rank 分组与算子 shape，再深入优化。只分析模式给建议，不擅自试跑。详见项目 `docs/workflows.md`。
3. **抓训练端到端剖面。** 优先使用实际 HCU 启动链已有的 torch profiler 支持，必要时对照官方实现接入；保留已验收的环境与 launcher，并记录采集所需改动。每个实际非单例并行组至少两个有代表性的 rank。保留完整稳态步和 phase，区分 fwd/bwd/optimizer/通信/数据/checkpoint；跨 rank 先校时。warmup、编译和 profiling 开销不能混进性能对照。
4. **按主要占比选择优化主线。** 空泡大先追数据、CPU launch、同步、PP 调度；通信大先与同条件预期核对，异常先排查，已符合单测预期的固有开销重点做 overlap/通算融合；负载不均用并行、路由、调度等框架措施，按需借鉴第三方引擎；计算占主导时按计算算子占比逐项推进；其他主导瓶颈仍存在时，可并行做独立计算分析。通信按 [通信优化专项](references/communication-optimization.md) 分 process group、消息量、拓扑、依赖、暴露尾部与最慢 rank。联合分析计算被并发拖慢、bucket/chunk/prefetch、通算融合及其同步协议；不能只凭 stream 重叠判定有效。关注显存 reserved/allocated、图池、临时/通信 buffer，以及保存恢复峰值。`GPU_MAX_HW_QUEUES` 按目标 runtime 和对照实测调节，没有通用最佳值。

   解释profile前先明确实际完整CPU步标记、步数、窗口总长、单步分布和profiler开关；排除同名GPU重复标记，不能把多步总GPU时间与关profiler的单步中位数直接比较。CPU op时长可含设备等待，通信驻留可含等peer；仅见GPU空白不能直接归因为CPU计算。非通信热点90%不等于端到端墙钟90%，分母与缺口必须同时报告。形状/模型范围改变后重建热点模型，不继承旧效率结论。
5. **复用 TraceLens。** 按项目 docs/integrations.md 安装锁定依赖，用 `tracelens-report TRACE --project PROJECT --rank RANK` 做 op/kernel、overlap 分析；完整 ranks 才用 `tracelens-collective`。检查日志、非空表、单位、统计分母及 unsupported 情形。原生表保留在私有 workspace，`generated` 不代表训练评估通过。TrainFlow 补充稳态窗口、实际 rank 分组、shape 与热点建模；不默认套用 AMD/NV 峰值，轻量归因不冒充跨 rank 关键路径。
6. **融合粒度与数值对齐。** 对照 NV 实际调用、接口、fwd/bwd、saved tensors、cast/accumulation。先查当前 HCU TE、Flash-Train、HCU Primus Turbo 已支持实现，核对与 AMD Primus/Primus-LM patch 的调用关系。TE 能力交 HCU TE，通用编译/cuDNN frontend 训练融合优先 Flash-Train，Primus Turbo 后端/模块问题交其 HCU 分支；依实际归属复用或修复。优先复用，不重复开发。
7. **评估累计 ≥90% 端到端占比的热点集合。** 墙钟为分母，重叠不能重复累计，CPU/等待缺口不能删掉。其中每个非通信 op 按 shape/dtype/布局/phase 建立 FLOPs、HBM/其他有效流量或延迟模型，给理论/可达上限、当前效率、独立实测与优化决策。先按端到端贡献排序，再按可兑现收益与约束安排实施；跳过高占比项说明原因。混合通算 kernel 仍评估计算部分；纯通信单列消息/拓扑/等待。缺模型或覆盖不足须明确补证据，不能报全覆盖。具体按 [热点上限、融合与实现迭代](references/operator-ceiling-iteration.md) 建表并随新 profile 更新。
8. **分发实施。** 提取真实热点中的计算、通信及 copy，按 [模型内外同条件对照](references/operator-comparison.md) 保留 shape/dtype/stride、实际实现、前后向/累积语义、通信各 rank 收发量及 copy 方向，再独立实测与模型内比较。先区分实现效率、提交等待和并发干扰；不以总耗时相近代替逐项检查。数学库 GEMM 先判断是否低于可靠预期或明显偏离合理上限；确需 tune 时按 [数学库日志与调优交接](references/math-library-tuning.md) 抓取实际 rocBLAS/hipBLASLt 日志中的完整 bench 命令，框架 shape 表仅作分析附件。rocBLAS 可按匹配教程有界 tune，hipBLASLt/grouped GEMM 交用户协调；不能仅因占比高就提调优。必要时看编译器/runtime/数学库/通信库对应分支源码；rocSHMEM 通算融合按瓶颈证据决定。
HCU 算子/通信候选和底层构建按 [工程联动](references/hcu-library-integration.md)：联查 HCU Primus Turbo、UCCL、UltraEP、MoonEP，以及现有 RCCL/rocSHMEM/DeepEP/MORI/Flux；按瓶颈和真实能力选用，不默认同名接口可替换。必要时在独立开发树改库、远端隔离重编，证明实际加载新制品并完成分层回归后按目标仓规范PR。

9. **按优先级持续迭代算子实现。** 计算占主导时，以计算热点为主线；其他情况下按其端到端影响安排独立计算分析；先按真实逻辑 op 聚合占比，再拆 phase/shape，完成高占比项初查、上限/未知和选择裁决后派发。高占比但上限不清的先补分析，不能因易写或已有 benchmark 随便选较小项。初步融合不是结束：重新评估融合后的工作量、瓶颈与可达上限，仍有显著空间就继续实施和测量。必要时将受编译/布局/指令限制的实现转 HIP：缺正确基线调用 `$hygon-hip-baseline-generator`，再用 `$hygon-hip-kernel-optimizer`；适合 Triton 的调用 `$hygon-triton-kernel-optimizer`。先确认可用；缺失时按 docs/integrations.md 获取 thirdparty/cuda-optimized-skill 并安装，也可读取其 skills/<name>/SKILL.md 及配套资源。kernel 遇到优化瓶颈必须做性能分析；hipprof 与 XProf/XCompute 的命令和产物分别使用，不混写。指令/反汇编问题按目标 ISA 和技能中的编译产物方法处理。达到目标、近可达上限、多轮无收益或受阻均需逐项给出证据和原因；显著空间未解决要汇报并保留缺口，不能以“已有融合”或预算耗尽视为达标。
10. **验证。** 每轮候选做实际 dispatch、局部输出/梯度/参数更新与多 shape 回归，随后 profiler-off 重复测量。阶段候选稳定后再做冻结样本和容差的较长 loss 验收；不频繁长训，也不省略阶段验收。RL 加查 policy version、logprob、reward 和数据年龄。

独立 GEMM/HBM/通信实测不及近期适用参考，或模型内性能异常时，沿项目 `docs/environment-discovery.md` 第 6 节推进差距闭环：查原件口径、配置/链路、所加载库与对应源码，按需搜 HCU-Knowledge，做授权内的单变量有界 A/B/A，核对正确性和实际作用路径，再回归保留或回退。不能把现场低值直接当可达上限，也不能因参考条件不全就停止排查；未解决用 `performance_discrepancy` / 当前 flow 问题保留，带已尝试证据升级专家。`analyze` 仅分析时不扩大执行权限，明确待执行步骤。

选择候选变量前先还原现场已验证配方与环境脚本的加载顺序、各 rank 生效参数和实际库；整套配方收益不能直接归因于其中一个开关。基本尝试后剩余显著可信差距需要按 `docs/collaboration.md`“问题升级与用户决定”明确向用户报告，附推荐下一步和备选项，由主控登记阻塞问题，等待答复后再扩展该调查；不能只写未来建议便结束。用户已有具体下一步指导时直接依其范围处理；只分析模式保持只分析。

## 重要参考

TraceLens 使用 thirdparty 清单锁定的 HCU fork，保留上游完整模块和原生 CLI。两个 TrainFlow 报告入口之外，按任务需要复用 TraceDiff、graph 报告、trace 分段/索引、源码定位及 EventReplay，具体依赖和入口见 docs/integrations.md。原生命令仍要遵循任务执行权限并记录私有输入/产物；缺少架构模型或事件映射时先标注缺口，优先用现有扩展点，必要的核心修改在独立 fork 开发 checkout 中完成并补回归。

TE 精度、权重缓存、attention backend、userbuffers 和融合查 `knowledge/official-transformer-engine-wiki/`；cuDNN graph/plan、SDPA fwd/bwd、open-kernel 融合和 host 缓存查 `knowledge/official-cudnn-frontend-wiki/`。先读 Wiki 再定位目标版本源码与教程，保留 NV/HCU 实现边界和实际 dispatch 证据。

AMD Primus、华为 MindSpeed/MindSpeed-LLM、百度 LoongForge 与官方开发分支都是一级机制参考。先比较补丁基线/gitlink、触发条件、测试和回退；官方能力真正进入当前 HCU 分支且回归等价后再退役旧 patch。

## 可并行的分析与实施

卡数充足且有独立优化假设时，可在互不争用的多个完整模型最小可行 DP 实例上并行开展模型级优化。每个实例分配独立 checkout/快照、端口、输出、checkpoint、设备租约和观察身份，共用冻结基线与质量契约；核对 EP/状态分片等约束，不强制 DP=1。按实际收益分工，及时用 agent-send/inbox 交流新结果、接口影响和失败边界；不在运行中静默合并他人的代码。共享 NIC/CFS/功率域可能污染测量，必要时串行；主控在共同参考实例配对复验兼容组合，稳定后统一阶段 loss。详细方法见项目 `docs/practices/capacity-and-parallel-experiments.md`。

固定 trace 后，可并行分析 CPU/空泡、计算/shape/上限、通信/并行域、显存/生命周期，各自保留原始证据并及时交流互相影响（如 overlap 下的 GEMM 变慢、重算与峰值显存）。所有 lane 使用同一窗口、rank 映射和墙钟分母；不能分别删去各自不擅长的时间再相加。

Agent 分工由实际模型调用和 profile 决定，不预设固定名称、算子类别或人数。先得到足以派发的热点清单，再按真实算子/源码位置、shape、dtype、前后向和实现路径动态拆分或合并任务；对应 `profile-analyze` 的 operator key 与原始 trace，补足其未覆盖的调用与 shape 信息。逐项覆盖应建模的非通信热点，不局限于少数常见算子。

**不同算子的详细分析与优化均可并行推进。** 本算子的分析有依据后即可进入局部优化，其他算子可仍在分析或优化，不设置全体分析结束的统一等待点。按不重叠代码区域或独立候选 checkout 分工，接口、数值契约与保存状态先约定；耦合的 kernel body 和 launch 参数由同一 owner 负责。独立 GPU 可并行测量，共享 GPU 只将实际占用设备的验证排队，开发/编译仍可继续；完整优化任务可选 `resource_scope: operation`，仅在命令执行时领取/释放租约。按 `docs/multi-agent.md` 登记实际依赖、peer、资源和验收。

单个 kernel 内部沿用原 Hygon Skill 的实测迭代，不强制再拆多 Agent 讨论。结论有疑问就定向提问/共享证据；主控选择兼容组合，集成后重新做局部正确性、隔离性能和阶段 loss 验证。新 profile 出现新热点时动态调整分工，不能沿用过时任务名单。

## 候选维护与观察范围

按 [候选缓存与观察交接](references/workflow.md#候选缓存与观察交接) 管理可重建编译/传输缓存。主控按既有五分钟周期维护，实施者负责使用前 pin、核销后释放；原 trace、数值基线、最好候选与验收证据持续保留。真实比较 context 变化时交接新观察 Store/peer/sentinel，不用旧 watcher 游标解释新候选；已核实的实际进度源与所有必需 member 健康分别检查，不固定假定 rank0 输出进度。

## 阶段产物

按预期整步收益范围、证据置信度、显存/编译成本、数值风险和依赖排序候选，允许独立方向并行；估计收益不得重复相加。沿用当前 flow/experience 保存已验收最佳版本、保留/拒绝原因和回退；不用最后一次尝试替代最好结果，不新建一套独立总账。

分析模式交付可复查的瓶颈报告、覆盖缺口、shape/效率表、优先级和建议实验。优化模式另交付候选源快照、成对实验、阶段 quality、回退和目标仓 PR。证据不足、收益平台期、反复数值异常或底层库缺能力时向用户报告最小证据包，方便专家介入。

## 与统一主控衔接

由 `$hcu-trainflow` 调用时，沿用当前任务、目标和私有工作区；本阶段负责实际领域工作，主控负责 `flow-next`、独立复核和推进。交付候选源/配置清单、原始证据和绑定 candidate_snapshot 的报告；不要另起无关联任务，也不要绕开复核直接推进状态。人的 GUIDANCE.md 默认每 5 分钟由主控采集，成员检查已采集指导并回应，不各自频繁读文件；明确记录收益、数值/显存代价、未完成项和需要专家判断的问题。完整契约见项目 `docs/collaboration.md`。本 Skill 仍可按用户指定独立使用，不强制开展全流程。

遇到 HCU 相关适配、性能或故障问题，先用 `$hcu-knowledge-search` 搜索大知识库（按工程、错误/符号、shape、gfx/DTK 和机制组合），再核对当前分支源码。已有适用证据可复用；不是每条命令重复搜，也不自动更新大知识库。

## 运行约定

先定位 HCU-TrainFlow checkout（用户给定路径或 `TRAINFLOW_PROJECT`）和私有 `TRAINFLOW_WORKSPACE`。仅跨项目可复用的通用环境经验和模型最终优化里程碑总结/关键数据按收录规则写入本仓 `knowledge/`；完整任务档案留 workspace，凭据/私钥/token 永不入仓。CLI 用 `hcu-trainflow --workspace <private-path>`；源码环境可用 `python -m hcu_trainflow`。先读项目 `docs/quickstart.md` 和当前任务上下文，再按需读相关章节。

主 Agent 在本地主控，专家分工记录 owner、scope、允许修改路径、预算与验收证据。运行代码使用独立开发 checkout 和不可变源快照；远端只执行明确命令/守护，不要求部署模型 Agent。TaskSpec 的 execute/sync/notify 权限是任务约定，不是 OS 安全沙箱。实际节点、容器、Pod UID、Slurm allocation 由部署任务确认。

HCU-Knowledge 随完整安装提供，贯穿环境适配、性能优化和扩 DP/容错；需要 HCU 事实、历史案例或底层实现时使用 `$hcu-knowledge-search`；也可以读当前对应分支源码和公开官方文档。知识检索不自动更新 HCU 大知识库。本工作流维护官方资料、可复用环境经验和模型最终优化总结，工作流方法在 docs/skills；具体依赖命令升级时同步复核 Skill/适配器，不能仅改 Wiki。

产物归属本 Skill：按目标仓规范准备集中、通用的改动、测试、PR 说明和回退方式。外部目标仓 PR/Cookbook 按目标发布要求处理；TrainFlow 自带 Wiki 按本仓知识归属规则保留通用环境经验、模型最终优化总结与必要证据，二者不要混同。遵循当前会话已给出的提交/发布授权。

## 局部知识的使用与里程碑记录

开始任务、重要实验或排障前，先跨引擎 wiki-search 检索官方资料、可复用环境经验及模型最终总结；工作流方法按需读 docs/practices，再按模型/环境/机制用 experience-search 检索本任务记录，检查 context、测量条件、失败原因和 loss 状态。需要机制依据时调用 hcu-engine-wiki-search；本地不足必须主动搜线上 PR，再读完整讨论、最终 diff、固定源码、调用者和测试，不能只停在已有入口页。局部官方 Wiki 发现版本漂移可按需自主更新；HCU 大知识库不随本任务更新。

report 和 flow-advance 自动把原上下文与报告沉淀到私有 experience。到达环境验收、初始基线、重要候选、阶段 loss、扩容/恢复或结束里程碑后，确认写入成功；失败用 experience-sync 重放。按 docs/experience-knowledge.md 补充结构化解释记录，包括实际性能/显存口径、适用/失败条件和回退，不伪造测量，不把局部通过当成长训 loss 通过。只分析或诊断的任务同样记录已知与待验证项。 工程 Wiki 仅收录官方资料、跨项目可复用的通用环境经验，以及模型最终优化里程碑的总结和关键数据。按 docs/knowledge-architecture.md 筛选：环境经验进入 `knowledge/sites/`；完成当前优化阶段且数值验收清楚的最终总结才进入 `knowledge/experiments/`。临时排查、单次调参、逐算子中间报告和未定候选只留 workspace/看板，不因已测量就入库。必要证据采用仓内相对链接和清单，入库后从新 Store 验证可读可搜。

形成 Cookbook 最佳实践时，先关联基线/候选/验证经验 ID，再记录草稿、目标 PR、提交/合入/替代状态；外部 Cookbook 按目标仓要求审核；TrainFlow 自带 Wiki 保存符合收录规则的环境经验与模型最终总结；草稿、候选及完整过程留任务档案。该阶段负责自己成果的交付，不新增独立交付 Skill。
