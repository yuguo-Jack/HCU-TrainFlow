---
name: hcu-train-analyze-and-optimize
description: 分析 HCU 训练引擎及 Torch 原生训练瓶颈，推进系统、通信与算子优化、局部回归及阶段 loss 验证；支持仅模型性能分析。
---

# hcu-train-analyze-and-optimize

## 开始前定位与阅读

先定位 HCU-TrainFlow checkout：用户明确指定的路径优先，其次 `TRAINFLOW_PROJECT`，再读本 Skill 安装目录的 `workspace.json` 中 `project_root`；验证该目录的项目标识、docs/skills 与版本，失效时重新安装绑定，不猜路径。私有 `TRAINFLOW_WORKSPACE` 由当前任务另行确定，不从项目绑定推断。先读项目 `docs/skill-reading-map.md` 的当前模式行，再按其中的开始/条件入口读正文。首次使用或工程升级后核对安装副本；文件缺失或绑定过期先修复，不能直接跳过指南。

默认只在当前任务工作空间及已核实的远端/容器映射目录内创建、修改、移动或删除；外部资料可按需读取。首次写入、映射变化或涉及外部路径时先读项目 `docs/workspace-boundaries.md`，复用已记录范围与授权；必要例外写清路径和影响，未获授权再询问，不逐条命令重复确认。

支持 `analyze` 只交付性能分析，也支持 `optimize/full` 迭代。分析任务不自动改实现或长时验 loss。

快速线与稳定线共用下面的完整优化闭环，区别仅在源码/依赖基线与交付形式。不能以“已跑通、已对齐初步融合或 patch 已导出”跳过端到端分析、原生调参、热点上限/同 shape 对照、必要的系统/通信/算子迭代及阶段精度验收。额外移植 HCU 独有机制或未合入 PR 可以按需求选择，原有优化验收不因此变为可选；确无优化必要需给出证据。

涉及 Graph、Roofline/算子效率、EventReplay、TraceLens 原生 Agent 或 hipprof/XProf/XCompute 时，读取工程 `docs/tracelens-analysis.md`，使用锁定 fork 的统一入口和实际资格边界。自动模型未知项仍须纳入热点任务；计数器、回放与 profiler-off 时间不可混用；原生 Agent metrics 完成后继续查证、撰写及复核，不把自动表格当成最终结论。

先识别实际训练执行路径：大型引擎按既有并行与融合路线；Torch 原生训练（包括视频生成、VLA、世界模型）按 [Torch 训练专项](references/torch-native-training.md) 补查输入流水、eager/compile、断图/重编译、autograd、DDP/FSDP 和实际 backend。引擎内部模块也可采用该专项，不另建一套流程。环境适配和扩 DP/容错继续复用另外两个阶段。

## 优化闭环

实验粒度按项目 `docs/collaboration.md`：先低成本淘汰，再为可保留候选做正式对照和独立复核；同一假设下的试参不逐次进入 RLCR。引擎原生选项与并行配置先按适用条件、容量、拓扑和已知瓶颈筛出少量方案，不全组合扫描。首要热点证据充足即可实施，其余建模并行补齐；≥90% 处置仍是完整阶段的要求。局部迭代复用未变化的模型、oracle 和其他算子资格，按影响补采 profile，稳定阶段才验 loss。

开始性能判断及每次切换优化方向时，按 [证据驱动的优化闭环](references/evidence-driven-loop.md) 核对：初始/最佳/候选身份，profile 是否仍适用，热点源码/重叠/融合三张关联表，预期收益可否证伪，以及组合和停滞后的处置。用映射运行定位源码、正式稳态 trace 判断调度、针对性计数器解释瓶颈、profiler-off 配对确认收益；不互换这几种证据。它补充下面的工作顺序，不新增阶段或固定 Agent。

沿适配阶段固定的执行工作分支推进。`full` 任务中，本轮优化完成不等于完整训练工作流完成；扩 DP、容错和持续监测尚未验证时，不宣告完整任务交付完成。按项目 `docs/practices/engine-delivery-tracks.md` 分路线交付：快速线保留指定 commit 的 example/patch，稳定线维护发布组合；只有约定的主仓整合项才保持 deferred，不强制把快速方案移到稳定主仓。独立 optimize/adapt/diagnose 任务按其已授权目标完成验证后交付，不增加扩容/长训义务；仅 analyze 不擅自修改或提交实现。可参考最新主仓/第三方源码并移植必要修复，不为交付目标提前替换执行基线。执行基线与交付目标的顺序见 adapt Skill 的 `references/workflow.md`。

**先复用已有验证。** 开始候选前检查已有数值、dispatch、性能和阶段 loss 证据，记录源码/库/配置差异究竟影响哪层。固定实现、ABI、shape/dtype 和数值契约未变的独立算子测试直接引用；换训练分支通常先补集成与端到端对照，不重跑整套底层资格测试。确有调用/梯度生命周期、依赖版本或覆盖缺口时只补受影响用例，写明重测原因。稳定候选再做一次阶段 loss 验收；不要以反复资格测试代替推进新优化。

**并行组织热点工作。** 获取固定模型 profile 和真实调用契约后，“同 shape 独立实测与模型内对照”和“上限评估、融合挖掘与实现优化”是可并行的两条工作线，不以全部单测完成作为启动分析的前提。按实际热点把不同算子或实现独立的算子族分给不同成员；上限初估可先基于源码、FLOPs/字节量和匹配硬件参考，实测返回后修正效率、剩余空间及优先级。分析发现新的 shape/数值/dispatch 条件，应反向补充重放契约。模型内外差距指向竞争或等待时，与系统/通信负责人共享证据，避免只重写 kernel。共享 GPU/NIC/带宽上的性能测量串行，有可核验隔离资源才并行测；开发与 CPU 分析不必等待测量资源。每个可用候选独立验收并及时交流，最终在同一固定模型实例验证组合收益与数值，稳定阶段统一验 loss。任务依赖、编辑范围和结果验收遵循主控 Skill 的团队协议，不能为满足并行形式机械增加 Agent。

1. **固定比较对象。** 初始基线不可覆盖；锁定源码、数据、环境、shape、拓扑、precision、sample/token 聚合和预算。未完成环境验收须标明对性能解释的限制。
2. **先检查并调优引擎原生能力，同时评估并行与显存。** 按 [原生能力调优与实现迭代](references/native-engine-tuning.md) 系统梳理当前训练/推理引擎的配置与实际生效路径，覆盖官方已合入、候选 PR 和 HCU 特有优化；区分当前支持、未命中、依赖缺口与不适用。除并行切分/显存外，同等检查后端与融合、编译/图执行、通信调度、缓存/状态及输入流水；RL 同时检查推理与训推协同。结合已有或短时 profile，优先试与主要瓶颈相关的可用机制，不穷举参数、不等全部试完才实施关键优化。已有显著收益仍须解释热点和完成阶段验证。

   延续完整模型容量判断，资源足够优先完整配置；容量条件变化时参考 HCU Train Sim 并短跑校准，不因调参随意缩层。比较 TP/PP/DP/CP/EP/SP、微批/累积、重算和状态分片，以最吃紧 rank 的峰值与必要余量、通信/空泡及 profiler-off 吞吐取舍；保持模型、有效全局 batch/token、精度与优化器语义可比。参考项目 `knowledge/projects/megatron/knowledgebase/local/topics/parallelism.md`。只分析模式核对能力并给建议，不擅自试跑。

   **调参与后续优化是循环。** 高价值选项因 HCU 缺依赖而不可用时，追消费者与库/算子条件，按后续融合/通信/底层实现流程补齐；先复用再开发，完成后返回参数与必要组合验证。反过来，配置改变调用、rank 分组、shape、调度或资源竞争后，更新 profile、上限与优化优先级。候选 PR 是隔离验证的实现候选，不当成已支持开关，也不自动替换执行基线。
3. **抓训练端到端剖面。** 优先使用实际 HCU 启动链已有的 torch profiler 支持，必要时对照官方实现接入；保留已验收的环境与 launcher，并记录采集所需改动。每个实际非单例并行组至少两个有代表性的 rank。保留完整稳态步和 phase，区分 fwd/bwd/optimizer/通信/数据/checkpoint；跨 rank 先校时。warmup、编译和 profiling 开销不能混进性能对照。
4. **按主要占比选择优化主线。** 空泡大先追数据、CPU launch、同步、PP 调度；通信大先与同条件预期核对，异常先排查，已符合单测预期的固有开销重点做 overlap/通算融合；负载不均用并行、路由、调度等框架措施，按需借鉴第三方引擎；计算占主导时按计算算子占比逐项推进；其他主导瓶颈仍存在时，可并行做独立计算分析。通信按 [通信优化专项](references/communication-optimization.md) 分 process group、消息量、拓扑、依赖、暴露尾部与最慢 rank。联合分析计算被并发拖慢、bucket/chunk/prefetch、通算融合及其同步协议；不能只凭 stream 重叠判定有效。关注显存 reserved/allocated、图池、临时/通信 buffer，以及保存恢复峰值。`GPU_MAX_HW_QUEUES` 按目标 runtime 和对照实测调节，没有通用最佳值。

   解释profile前先明确实际完整CPU步标记、步数、窗口总长、单步分布和profiler开关；排除同名GPU重复标记，不能把多步总GPU时间与关profiler的单步中位数直接比较。CPU op时长可含设备等待，通信驻留可含等peer；仅见GPU空白不能直接归因为CPU计算。非通信热点90%不等于端到端墙钟90%，分母与缺口必须同时报告。形状/模型范围改变后重建热点模型，不继承旧效率结论。
5. **复用 TraceLens。** 按项目 docs/integrations.md 安装锁定依赖，用 `tracelens-report TRACE --project PROJECT --rank RANK` 做 op/kernel、overlap 分析；完整 ranks 才用 `tracelens-collective`。需要切分稳定训练窗口、按实际 rank 合并展示、前后比较、Graph 归因、硬件校准 Roofline、原生 Agent 准备、hipprof 或 counters 时，按项目 `docs/tracelens-analysis.md` 使用 `tracelens-analyze` 的对应模式；EventReplay 按其原生路径和副作用约束另行执行。检查日志、非空表、单位、统计分母及 unsupported 情形。原生表保留在私有 workspace，`generated` 不代表训练评估通过，`review-pending` 还需查证与独立复核。TrainFlow 补充稳态窗口、实际 rank 分组、shape 与热点建模；不默认套用 AMD/NV 峰值，轻量归因不冒充跨 rank 关键路径。

   以下融合检查、上限评估、同条件复测和实现迭代按第 3–5 项的证据安排，不要求先对全模型做一轮融合才能建模。每个热点先明确调用契约、当前性能和实施理由；其依赖满足即可优化，其他热点继续分析。仅分析模式在报告与建议处交付，不执行后续修改或测量。
6. **融合粒度与数值对齐。** 先核对第 2 项已支持融合的配置、命中条件和依赖缺口，避免把未启用能力误判为缺实现；补齐后返回该选项及相关组合验证。 对照 NV 实际调用、接口、fwd/bwd、saved tensors、cast/accumulation。先查当前 HCU TE、Flash-Train、HCU Primus Turbo 已支持实现，核对与 AMD Primus/Primus-LM patch 的调用关系。TE 能力交 HCU TE，通用编译/cuDNN frontend 训练融合优先 Flash-Train，Primus Turbo 后端/模块问题交其 HCU 分支；依实际归属复用或修复。优先复用，不重复开发。
7. **评估累计 ≥90% 端到端占比的热点集合。** 墙钟为分母，重叠不能重复累计，CPU/等待缺口不能删掉。其中每个非通信 op 按 shape/dtype/布局/phase 建立 FLOPs、HBM/其他有效流量或延迟模型，给理论/可达上限、当前效率、独立实测与优化决策。先按端到端贡献排序，再按可兑现收益与约束安排实施；跳过高占比项说明原因。混合通算 kernel 仍评估计算部分；纯通信单列消息/拓扑/等待。缺模型或覆盖不足须明确补证据，不能报全覆盖。具体按 [热点上限、融合与实现迭代](references/operator-ceiling-iteration.md) 建表并随新 profile 更新。
8. **同条件复测与库调优交接。** 提取真实热点中的计算、通信及 copy，按 [模型内外同条件对照](references/operator-comparison.md) 保留 shape/dtype/stride、实际实现、前后向/累积语义、通信各 rank 收发量及 copy 方向，再独立实测与模型内比较。先区分实现效率、提交等待和并发干扰；不以总耗时相近代替逐项检查。数学库 GEMM 先判断是否低于可靠预期或明显偏离合理上限；确需 tune 时按 [数学库日志与调优交接](references/math-library-tuning.md) 抓取实际 rocBLAS/hipBLASLt 日志中的完整 bench 命令，框架 shape 表仅作分析附件。rocBLAS 可按当前教程自行有界选优并回归，hipBLASLt/grouped GEMM 交用户协调。MIOpen conv/其他热点按同指南检查布局和选优/缓存，仍有差距提 Driver/最小复现交数学库；不因占比高就提调优。必要时看编译器/runtime/数学库/通信库对应分支源码；rocSHMEM 通算融合按瓶颈证据决定。
HCU 算子/通信候选和底层构建按 [工程联动](references/hcu-library-integration.md)：联查 HCU Primus Turbo、AITER、UCCL、UltraEP、MoonEP，以及现有 RCCL/rocSHMEM/DeepEP/MORI/Flux；按瓶颈和真实消费者的固定依赖、数值协议及完成语义选用，不默认同名接口可替换。必要时在独立开发树改库、远端隔离重编，证明实际加载新制品并完成分层回归后按目标仓规范PR。

9. **按优先级持续迭代算子实现。** 计算占主导时，以计算热点为主线；其他情况下按其端到端影响安排独立计算分析；先按真实逻辑 op 聚合占比，再拆 phase/shape，完成高占比项初查、上限/未知和选择裁决后派发。高占比但上限不清的先补分析，不能因易写或已有 benchmark 随便选较小项。初步融合不是结束：重新评估融合后的工作量、瓶颈与可达上限，仍有显著空间就继续实施和测量。必要时将受编译/布局/指令限制的实现转 HIP：缺正确基线调用 `$hygon-hip-baseline-generator`，再用 `$hygon-hip-kernel-optimizer`；适合 Triton 的调用 `$hygon-triton-kernel-optimizer`。先确认可用；缺失时按 docs/integrations.md 获取 thirdparty/cuda-optimized-skill 并安装，也可读取其 skills/<name>/SKILL.md 及配套资源。kernel 遇到优化瓶颈必须做性能分析；hipprof 与 XProf/XCompute 的命令和产物分别使用，不混写。指令/反汇编问题按目标 ISA 和技能中的编译产物方法处理。达到目标、近可达上限、多轮无收益或受阻均需逐项给出证据和原因；显著空间未解决要汇报并保留缺口，不能以“已有融合”或预算耗尽视为达标。
10. **验证。** 每轮候选做实际 dispatch、局部输出/梯度/参数更新与多 shape 回归，随后 profiler-off 重复测量，按预先确定的稳定性标准处理噪声。阶段候选稳定后按项目 `docs/training-state-validation.md` 的阶段 A/B 段，从同一初始模型/优化器/RNG/数据状态对照，固定配方、样本与容差并登记状态/配方指纹；不频繁长训，也不省略阶段验收。RL 加查 policy version、logprob、reward 和数据年龄。

独立 GEMM/HBM/通信实测不及近期适用参考，或模型内性能异常时，沿项目 `docs/environment-discovery.md` 第 6 节推进差距闭环：查原件口径、配置/链路、所加载库与对应源码，按需搜 HCU-Knowledge，做授权内的单变量有界 A/B/A，核对正确性和实际作用路径，再回归保留或回退。不能把现场低值直接当可达上限，也不能因参考条件不全就停止排查；未解决用 `performance_discrepancy` / 当前 flow 问题保留，带已尝试证据升级专家。`analyze` 仅分析时不扩大执行权限，明确待执行步骤。

选择候选变量前先还原现场已验证配方与环境脚本的加载顺序、各 rank 生效参数和实际库；整套配方收益不能直接归因于其中一个开关。基本尝试后剩余显著可信差距需要按 `docs/collaboration.md`“问题升级与用户决定”明确向用户报告，附推荐下一步和备选项，由主控登记阻塞问题，等待答复后再扩展该调查；不能只写未来建议便结束。用户已有具体下一步指导时直接依其范围处理；只分析模式保持只分析。

融合、compile、低精度或布局改动的数值回归按项目 `docs/practices/model-accuracy-diagnosis.md` 执行：先确认对照语义，再按有 NV/无 NV 路线用 Probe 或等价采集定位首差，必要时交现有算子 Skill 补独立参考与修复。局部正确性失败阻止该候选晋级，不能靠更快或相近 loss 放行；长窗口 loss 仍在稳定里程碑验。

## 异常与证据不足

按 [优化验证与异常诊断](references/validation-diagnostics.md) 处理候选未生效、缺采集、收益不稳定、数值偏差、内存和恢复问题。先确认比较与调用契约，再找首次分歧，必要时转规模长稳 Skill 共用诊断；故障证据、context 和 owner 连续保留。不能用诊断模式计时报告加速，也不能用空报告或未知上限关闭优化。

## 重要参考

TraceLens 使用 thirdparty 清单锁定的 HCU fork，保留上游完整模块和原生 CLI。TrainFlow 的报告、collective 与统一分析入口之外，按任务需要通过统一分析调用 compare/split/merge，并复用原生 trace 索引、源码定位及 EventReplay，具体依赖和入口见 docs/integrations.md 与 docs/tracelens-analysis.md。原生命令仍要遵循任务执行权限并记录私有输入/产物；缺少架构模型或事件映射时先标注缺口，优先用现有扩展点，必要的核心修改在独立 fork 开发 checkout 中完成并补回归。

TE 精度、权重缓存、attention backend、userbuffers 和融合查 `knowledge/projects/transformer-engine/README.md`；cuDNN graph/plan、SDPA fwd/bwd、open-kernel 融合和 host 缓存查 `knowledge/projects/cudnn-frontend/README.md`。先读 Wiki 再定位目标版本源码与教程，保留 NV/HCU 实现边界和实际 dispatch 证据。

按项目 [优化参考选择表](../../docs/optimization-reference-map.md)联查 Megatron、TorchTitan、DeepSpeed、Primus、MindSpeed/MindSpeed-LLM、LoongForge 与相关 SFT/RL/推理依赖，不按厂商或引擎名称固定排序；各入口都可追官方教程、PR 和源码。先比较补丁基线/gitlink、触发条件、测试和回退；官方能力真正进入当前 HCU 分支且回归等价后再退役旧 patch。

## 可并行的分析与实施

卡数充足且有独立优化假设时，可在互不争用的多个完整模型最小可行 DP 实例上并行开展模型级优化。每个实例分配独立 checkout/快照、端口、输出、checkpoint、设备租约和观察身份，共用冻结基线与质量契约；核对 EP/状态分片等约束，不强制 DP=1。按实际收益分工，及时用 agent-send/inbox 交流新结果、接口影响和失败边界；不在运行中静默合并他人的代码。共享 NIC/CFS/功率域可能污染测量，必要时串行；主控在共同参考实例配对复验兼容组合，稳定后统一阶段 loss。详细方法见项目 `docs/practices/capacity-and-parallel-experiments.md`。

固定 trace 后，可并行分析 CPU/空泡、计算/shape/上限、通信/并行域、显存/生命周期，各自保留原始证据并及时交流互相影响（如 overlap 下的 GEMM 变慢、重算与峰值显存）。所有 lane 使用同一窗口、rank 映射和墙钟分母；不能分别删去各自不擅长的时间再相加。

Agent 分工由实际模型调用和 profile 决定，不预设固定名称、算子类别或人数。先得到足以派发的热点清单，再按真实算子/源码位置、shape、dtype、前后向和实现路径动态拆分或合并任务；对应 `profile-analyze` 的 operator key 与原始 trace，补足其未覆盖的调用与 shape 信息。逐项覆盖应建模的非通信热点，不局限于少数常见算子。

**不同算子的详细分析与优化均可并行推进。** 本算子的分析有依据后即可进入局部优化，其他算子可仍在分析或优化，不设置全体分析结束的统一等待点。按不重叠代码区域或独立候选 checkout 分工，接口、数值契约与保存状态先约定；耦合的 kernel body 和 launch 参数由同一 owner 负责。独立 GPU 可并行测量，共享 GPU 只将实际占用设备的验证排队，开发/编译仍可继续；完整优化任务可选 `resource_scope: operation`，仅在命令执行时领取/释放租约。按 `docs/multi-agent.md` 登记实际依赖、peer、资源和验收。

单个 kernel 内部沿用原 Hygon Skill 的实测迭代，不强制再拆多 Agent 讨论。结论有疑问就定向提问/共享证据；主控选择兼容组合，集成后重新做局部正确性、隔离性能和阶段 loss 验证。新 profile 出现新热点时动态调整分工，不能沿用过时任务名单。

## 候选维护与观察范围

按 [候选缓存与观察交接](references/workflow.md#候选缓存与观察交接) 管理可重建缓存及临时大文件。一批实验结束后，由实施者核销并显式退役无用 dump、重复解析物和临时保存点，主控按阶段/低频策略维护，不随每轮调参或五分钟交互扫盘。原 trace、数值基线、最好候选与验收证据持续保留；大规模采集/回放前只查容量和预计写入量。真实比较 context 变化时交接新观察 Store/peer/sentinel，不用旧 watcher 游标解释新候选；已核实的实际进度源与所有必需 member 健康分别检查，不固定假定 rank0 输出进度。

## 阶段产物

按预期整步收益范围、证据置信度、显存/编译成本、数值风险和依赖排序候选，允许独立方向并行；估计收益不得重复相加。沿用当前 flow/experience 保存已验收最佳版本、保留/拒绝原因和回退；不用最后一次尝试替代最好结果，不新建一套独立总账。

分析模式交付可复查的瓶颈报告、覆盖缺口、shape/效率表、优先级和建议实验。优化模式另交付候选源快照、成对实验、阶段 quality、回退和目标仓 PR。证据不足、收益平台期、反复数值异常或底层库缺能力时向用户报告最小证据包，方便专家介入。

## 与统一主控衔接

由 `$hcu-trainflow` 调用时，沿用当前任务、目标和私有工作区；本阶段负责实际领域工作，主控负责 `flow-next`、独立复核和推进。交付候选源/配置清单、原始证据和绑定 candidate_snapshot 的报告；不要另起无关联任务，也不要绕开复核直接推进状态。人的 GUIDANCE.md 默认每 5 分钟由主控采集，成员检查已采集指导并回应，不各自频繁读文件；明确记录收益、数值/显存代价、未完成项和需要专家判断的问题。完整契约见项目 `docs/collaboration.md`。本 Skill 仍可按用户指定独立使用，不强制开展全流程。

遇到 HCU 相关适配、性能或故障问题，先用 `$hcu-knowledge-search` 搜索大知识库（按工程、错误/符号、shape、gfx/DTK 和机制组合），再核对当前分支源码。已有适用证据可复用；不是每条命令重复搜，也不自动更新大知识库。

## Wiki 维护衔接

独立调用本阶段也按 `docs/knowledge-architecture.md` 的“任务中的维护时机”执行：确认实际模型/环境/分支后检查相关官方资料，必要时调用 `$hcu-trainflow-wiki-skill-update` 定向更新；阶段验收与最终交付前筛选本阶段可复用的通用环境经验或合格的最终模型总结。没有最终优化与数值验收就不写最终优化总结，没有可共享知识则记录原因。复用任务已有处理记录，不反复刷新、不把私有 experience 自动记录当作共享 Wiki 已更新。

## 运行约定

仅跨项目可复用的通用环境经验和模型最终优化里程碑总结/关键数据按收录规则写入本仓 `knowledge/`；完整任务档案留 workspace，凭据/私钥/token 永不入仓。CLI 用 `hcu-trainflow --workspace <private-path>`；源码环境可用 `python -m hcu_trainflow`。先读项目 `docs/quickstart.md` 和当前任务上下文，再按需读相关章节。

主 Agent 在本地主控，专家分工记录 owner、scope、允许修改路径、预算与验收证据。运行代码使用独立开发 checkout 和不可变源快照；远端只执行明确命令/守护，不要求部署模型 Agent。TaskSpec 的 execute/sync/notify 权限是任务约定，不是 OS 安全沙箱。实际节点、容器、Pod UID、Slurm allocation 由部署任务确认。

HCU-Knowledge 随完整安装提供，贯穿环境适配、性能优化和扩 DP/容错；需要 HCU 事实、历史案例或底层实现时使用 `$hcu-knowledge-search`；也可以读当前对应分支源码和公开官方文档。知识检索不自动更新 HCU 大知识库。本工作流维护官方资料、可复用环境经验和模型最终优化总结，工作流方法在 docs/skills；具体依赖命令升级时同步复核 Skill/适配器，不能仅改 Wiki。

产物归属本 Skill：按项目 `docs/change-delivery.md` 核对原始修改、基点/目标、上游等价实现和受影响验证，准备符合目标仓规范的改动、测试、PR 说明和回退方式。用户只委托交付已有修改时直接复用这部分，不重走无关训练阶段；原任务未完成目标仍保留。外部目标仓 PR/Cookbook 按目标发布要求处理；TrainFlow 自带 Wiki 按本仓知识归属规则保留通用环境经验、模型最终优化总结与必要证据，二者不要混同。遵循当前会话已给出的提交/发布授权。

## 局部知识的使用与里程碑记录

开始任务或出现新问题、证据冲突、版本差异时，按需跨引擎 wiki-search 检索官方资料、可复用环境经验及模型最终总结；工作流方法按需读 docs/practices，已有实验用 experience-search 查本任务记录并核对 context、条件和 loss 状态。相同问题已有适用证据时直接引用，不在每个重要实验前重复检索。需要机制依据时调用 hcu-trainflow-wiki-search；本地不足必须主动搜线上 PR，再读完整讨论、最终 diff、固定源码、调用者和测试，不能只停在已有入口页。HCU-TrainFlow-Wiki 中的资料或经验发现版本漂移时，按需调用更新入口复核；HCU 大知识库不随本任务更新。

report 和 flow-advance 自动把原上下文与报告沉淀到私有 experience。到达环境验收、初始基线、重要候选、阶段 loss、扩容/恢复或结束里程碑后，确认写入成功；失败用 experience-sync 重放。按 docs/experience-knowledge.md 补充结构化解释记录，包括实际性能/显存口径、适用/失败条件和回退，不伪造测量，不把局部通过当成长训 loss 通过。只分析或诊断的任务同样记录已知与待验证项。 工程 Wiki 仅收录官方资料、跨项目可复用的通用环境经验，以及模型最终优化里程碑的总结和关键数据。按 docs/knowledge-architecture.md 筛选：环境经验进入 `knowledge/sites/`；完成当前优化阶段且数值验收清楚的最终总结才进入 `knowledge/experiments/`。临时排查、单次调参、逐算子中间报告和未定候选只留 workspace/看板，不因已测量就入库。必要证据采用仓内相对链接和清单，入库后从新 Store 验证可读可搜。

形成 Cookbook 最佳实践时，先关联基线/候选/验证经验 ID，再记录草稿、目标 PR、提交/合入/替代状态；外部 Cookbook 按目标仓要求审核；TrainFlow 自带 Wiki 保存符合收录规则的环境经验与模型最终总结；草稿、候选及完整过程留任务档案。该阶段负责自己成果的交付，不新增独立交付 Skill。
