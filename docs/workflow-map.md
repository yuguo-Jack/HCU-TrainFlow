# HCU-TrainFlow 工作流全景

本文与 `0.4.0.dev0` 的实现和 Skill 约定对应。先看总览，再按问题进入阶段细图；所有图均为可编辑的 Mermaid，GitHub 可直接显示。

**读图约定：**实线表示推进、反馈或数据传递，虚线表示按需查询、指导或配套能力。方框是工作，菱形是判断，圆柱是持久资料。同一张图中的并行分支表示可拆工作，不表示每次必须启动同样数量的 Agent。

**执行边界：**主控与专家 Agent 负责判断和实施；TrainFlow CLI 负责记录、协调及证据检查；现场负责真实编译、训练、测量和既有容错。图中的训练动作是工作流要求，不能理解为都已在真实 HCU 环境验收。当前实现和现场验证范围见 [能力说明](capabilities.md)。

## 1. 全流程总览

```mermaid
flowchart TD
    U["模型、环境、数据与目标<br/>预训练 / SFT / RL / Torch 原生训练"] --> C["本地主控 hcu-trainflow<br/>明确范围、预算、验收与现场权限"]
    C --> A["① 环境验收与模型适配<br/>hcu-train-adapt · 详见图 2"]
    A --> AG{"环境与初始数值基线通过？"}
    AG -->|缺失或失败| AR["补证据 / 修环境 / 修适配"]
    AR --> A
    AG -->|通过| O["② 性能分析与优化<br/>先并行切分和显存预算 · 详见图 3"]
    O --> Q["稳定候选：阶段 loss 与性能验收<br/>每轮仍做局部正确性及性能回归"]
    Q --> QG{"达到约定目标且数值通过？"}
    QG -->|未达到| OR["定位问题、修正或回退<br/>无新证据 / 达到预算边界时请专家介入"]
    OR --> O
    QG -->|通过| S["③ 恢复完整模型 → 扩 DP 域<br/>筛机、健康池与逐级扩容验证"]
    S --> SG{"环境、质量与扩容验收通过？"}
    SG -->|失败| SR["按原因回到环境、适配或优化<br/>修复后重新验收受影响证据"]
    SR --> C
    SG -->|通过| T["长训：持续监测、既有容错与诊断<br/>hcu-train-fault-tolerance · 详见图 6"]
    T --> TG{"达到任务约定的完成 / 交接条件？"}
    TG -->|否| T
    TG -->|是| Z["完成复核与交付<br/>代码 / 配方 / 证据 / 经验 / 运行交接"]
    LOOP["所有阶段共用<br/>实施 → 测量 → 独立复核 → 修正 / 推进<br/>详见图 4"] -.-> C
    H["BOARD.md 进展与问题<br/>GUIDANCE.md 指导 · 默认每 5 分钟采集"] -.-> C
    K[("必装 HCU-Knowledge 贯穿三个阶段<br/>联查官方 Wiki / 私有经验 / PR / 底层源码<br/>详见图 7")] -.-> C
    C -.-> TEAM["按依赖动态拆解多 Agent 任务<br/>独立工作并行，集成与共享测量协调<br/>详见图 5"]
```

- **全流程入口：**`hcu-trainflow` 协调三个阶段 Skill，保留循环状态、证据和人的指导。
- **独立入口：**`hcu-train-adapt` 可仅检查环境；`hcu-train-optimize` 可仅分析性能；`hcu-train-fault-tolerance` 可仅诊断故障。独立任务按自己的目标交付，不强行经过后续训练阶段。
- **持续运行：**启动训练不等于完成任务；尚在约定监测范围内就继续观测和处理异常。完成或交接须有明确条件、责任人和证据。

## 2. 环境验收与模型适配

```mermaid
flowchart TD
    I["确认模型 / 数据 / 用户 patch<br/>节点、设备、拓扑、调度方式和权限"] --> D["发现当前环境与工程实际工具<br/>Cluster Manager / run nhc / check 脚本 / DTK 命令"]
    D --> E["逐节点与设备采集<br/>GEMM、HBM、机内互联、机间网络和集合通信"]
    X["匹配硬件、精度、shape、拓扑、软件的预期<br/>官方资料 / HCU 知识 / 飞书记录"] -.-> E
    E --> EG{"必需项齐全且结果符合预期？"}
    EG -->|否| FIX["区分权限缺口、未测项与真实故障<br/>诊断修复 / 补测 / 必要时请专家"]
    FIX --> D
    EG -->|是| ONLY{"是否仅环境检查？"}
    ONLY -->|是| ER["交付环境报告、适用范围与证据"]
    ONLY -->|否| R["选择当前 HCU 工程适用分支及启动配方<br/>核对已有脚本、环境变量、依赖和用户 patch"]
    W["官方引擎 Wiki + 对应依赖源码<br/>核对模型、精度及训练语义"] -.-> R
    R --> L["本地独立开发 checkout<br/>固定源码与配置 → 同步远端 → 编译运行"]
    L --> M["最小可运行任务<br/>资源不足时可仅缩 layer，保留其他模型参数"]
    M --> TYPE{"任务类型"}
    TYPE -->|预训练| P["输出、梯度、优化器步与 checkpoint"]
    TYPE -->|SFT| F["另核模板、packing、loss mask"]
    TYPE -->|RL| RL["另核 actor / critic / ref / reward / rollout<br/>权重同步、policy version、logprob 和异步语义"]
    TYPE -->|Torch 原生训练| N["视频 / VLA / 世界模型等<br/>数据与时空 shape、mask、autograd、EMA"]
    P --> B["冻结初始正确性 / 数值基线<br/>有 NV 环境时补跨平台对照"]
    F --> B
    RL --> B
    N --> B
    B --> BG{"基线可用且验证通过？"}
    BG -->|否| BF["追到当前引擎和底层库源码<br/>修正适配，重跑受影响验证"]
    BF --> R
    BG -->|是| OUT["进入性能分析或按适配任务范围交付"]
```

启动配方优先级是：**当前 HCU 分支同模型配方 → 同引擎相近模型的 HCU 配方 → 结合官方语义与 HCU 实现构建配方**。每一种都要核对实际生效参数，不能直接照搬 NV 的环境变量或旧 HCU 脚本。缩 layer 可用于适配/分析和筛机代理，不证明完整模型的显存、收敛和扩容能力。图中任务分支可组合，例如 Torch 原生 SFT；按实际语义核查，不是互斥类别。

工具发现和预期查证由 Agent 按现场完成；当前工程没有为所有 HCU 型号内置一套恒定验收命令和阈值。仅环境检查也可交付明确的失败或不充分报告，这不等于通过训练准入。详见 [适配 Skill](../skills/hcu-train-adapt/SKILL.md)。

## 3. 性能分析、优化与验证

### 3.1 系统调参与瓶颈定位

```mermaid
flowchart TD
    B["固定比较条件与初始数值基线<br/>模型 / 数据 / 精度 / 有效 batch-token / 版本"] --> P["优先评估并行切分与显存预算<br/>TP / PP / DP / CP / EP / SP<br/>微批、累积、重算、状态分片与 offload"]
    P --> M["筛选布局候选<br/>最吃紧 rank 峰值 + 必要余量<br/>短跑校准吞吐、通信与流水空泡"]
    M --> T["稳态端到端采样：torchprof<br/>覆盖各实际非单例并行组至少 2 个代表 rank"]
    T --> TL["TraceLens + TrainFlow 窗口分析<br/>补 CPU-op 对应的 shape / dtype / layout / phase"]
    TL --> A["按证据并行分析<br/>CPU / 数据 / launch 空泡"]
    TL --> C["通信依赖、暴露时间与 overlap<br/>bucket / chunk / 预取 / 通算融合<br/>慢 rank、拓扑及计算竞争 · 详见图 3.5"]
    TL --> V["显存生命周期与峰值<br/>激活 / 状态 / workspace / 通信 / graph"]
    TL --> O["真实算子调用与热点表<br/>前后向、融合粒度与时间归因"]
    TL --> TORCH["Torch 原生 / 引擎局部模块<br/>输入、断图、重编译、前后向、DDP/FSDP<br/>详见图 3.4"]
    A --> H["主控合并证据和瓶颈优先级<br/>区分系统问题与实现差距"]
    C --> H
    V --> H
    O --> H
    TORCH --> H
    H --> RANK["候选排序：预计整步收益、置信度<br/>显存 / 编译成本、数值风险、依赖与回退"]
    RANK --> MODE{"是否仅性能分析？"}
    MODE -->|是| REPORT["交付瓶颈、上限评估、证据缺口与实验建议<br/>不擅自修改配置或启动优化实验"]
    MODE -->|否| SYS["系统调参候选<br/>并行布局 / overlap / GPU_MAX_HW_QUEUES<br/>必要位置 compile / 显存与重算权衡"]
    MODE -->|否| K["融合对齐与热点实现优化<br/>进入图 3.2，可与独立系统分析并行"]
    SYS --> VERIFY["局部正确性 + profiler-off 对照测量<br/>依赖变化同步更新 ranks 和 shapes"]
    VERIFY -->|重采验证与重新归因| T
    K -->|集成候选后重评系统效果| VERIFY
    H -.-> REF["Megatron / Bridge 官方指南与 dev PR<br/>AMD Primus、MindSpeed 系列、LoongForge<br/>HCU 工程及底层库对应分支"]
```

并行布局须在显存、通信、流水空泡和吞吐之间权衡，不以“占满显存”为目标。改变微批、累积或并行度时保持训练语义可比；布局变化会改变热点与 shape，需要重新分析。具体指南见 [并行切分与显存调参](../knowledge/official-megatron-wiki/parallelism.md)。

TraceLens 的逐 rank 分析可用代表样本；其完整 collective 报告要求全部 `0..N-1` rank 文件及实际通信上下文。时间对齐、RCCL 识别和统计口径要在现场核对。TrainFlow 的重叠时间归因是初步排序方法，不是自动关键路径证明。

### 3.2 融合粒度、非通信热点与优化空间

```mermaid
flowchart TD
    H["来自同一稳态窗口的热点和调用证据"] --> F["对照 NV 融合粒度与数值契约<br/>接口、前后向、保存值、累加和 cast"]
    H --> C["累计至少 90% 端到端墙钟热点覆盖<br/>重叠不重复累计；空泡与未归因缺口仍保留"]
    F --> R{"当前 HCU TE / Flash-Train 已支持？"}
    R -->|是| USE["优先复用<br/>进入图 3.3 验证实际 dispatch"]
    R -->|否| NEW["补融合实现<br/>TE 能力归 HCU TE<br/>编译 / cuDNN Frontend 等融合归 Flash-Train"]
    C --> TYPE{"热点类型"}
    TYPE -->|纯通信| COMM["按消息量、拓扑、等待和 overlap 评估<br/>同数据量独立通信测试"]
    TYPE -->|非通信或含计算的混合 kernel| MODEL["逐项建模<br/>真实 shape / dtype / phase<br/>FLOPs、字节量、延迟下限与可达参考"]
    MODEL --> EFF["评估当前效率和改进空间<br/>同 shape 独立实测 vs 模型内耗时"]
    EFF --> WHY{"评估结论"}
    WHY -->|系统并发 / 资源干扰| SYS["返回图 3.1<br/>检查 runtime、overlap、队列和显存"]
    WHY -->|实现差距| TASK["形成优化任务<br/>进入图 3.3"]
    WHY -->|已接近合理上限| KEEP["保留当前实现与评估依据<br/>纳入整体候选验收"]
    WHY -->|模型或测量不足| MORE["补源码、计数器或 shape 证据<br/>修正假设与上限模型"]
    MORE --> MODEL
    NEW --> TASK
    COMM -->|系统调参 / overlap 问题| SYS
    COMM -->|已满足目标| KEEP
    COMM -->|需要通算融合时| SH["核对 rocSHMEM 等当前能力<br/>明确同步、生命周期和正确性"]
    SH --> TASK
```

### 3.3 实现、局部回归与阶段验收

```mermaid
flowchart TD
    IN["已就绪的实现优化 / 融合任务<br/>同一轮可有多个独立任务"] --> TASK["动态分配 Agent 与独立 checkout<br/>按各自依赖进入实现和局部验证"]
    TASK -->|自定义实现| SK["按需使用三个 Hygon 算子 Skill<br/>HIP 基线 / HIP 优化 / Triton 优化<br/>瓶颈时使用实际可用的性能分析工具"]
    TASK -->|数学库路径| LIB["提取 rocBLAS / hipBLASLt 的 size<br/>rocBLAS 按教程 tune<br/>其他提交调优需求，保留已验证路径"]
    SK --> TEST["逐轮局部验证<br/>实际分发、输出 / 梯度 / 优化器影响、多 shape<br/>profiler-off 配对重复测量"]
    LIB -->|获得可测候选后| TEST
    USE["复用已有 HCU 能力"] --> TEST
    TEST --> LOCAL{"局部正确且有收益？"}
    LOCAL -->|否| RETRY["修复、回退或更换假设<br/>重新进入本任务；无新方向时请专家"]
    LOCAL -->|是| MERGE["集成兼容候选<br/>隔离测量，重抓模型 profile"]
    MERGE --> STABLE{"是否到稳定阶段验收点？"}
    STABLE -->|继续迭代| H["回到图 3.1 / 3.2<br/>更新模型 profile、热点及优化优先级"]
    STABLE -->|是| LOSS["相对初始冻结基线验证阶段 loss<br/>同时核对性能、显存和任务特有质量指标"]
    LOSS --> OK{"质量与性能目标通过？"}
    OK -->|否| BACK["定位 / 回退 / 修正<br/>必要时给专家证据包"]
    BACK --> H
    OK -->|是| REVIEW["独立复核当前候选与证据<br/>通过后进入扩容准备或交付"]
    KEEP["已接近上限的当前实现<br/>保留原验证与适用依据"] --> MERGE
```

- **覆盖率分母：**每 rank 的整个训练窗口墙钟；若 GPU busy 只有 60%，剩余空泡/等待不能从分母删掉以制造 90% 覆盖。不同 rank 的时长也不相加作全局时间。
- **效率模型：**时间下界为 `max(FLOPs/匹配算力, bytes/匹配带宽, latency_floor)`；下界除以实测耗时是带假设的效率指标，不是硬件利用率。超过 1 要复核模型和测量。Attention 等复杂算子须用实际算法、IO 和重算路径建模。
- **优化节奏：**融合对齐、其他热点分析和独立算子优化可以交错推进。不是等全部融合完成后才分析剩余热点，也不是每次 kernel 改动都长时验 loss。
- **工具与归属：**XProf/XCompute 与 hipprof 按实际环境分别使用；必要时查底层库对应分支，不能用不匹配的软件栈解释现场行为。hipBLASLt/groupGEMM 当前不承诺自动 tune，记录可复现 size 和需求。

详细约束见 [性能分析](profiling.md)、[优化 Skill](../skills/hcu-train-optimize/SKILL.md) 与 [三个阶段工作流](workflows.md)。

### 3.4 Torch 原生训练专项（沿用同一优化闭环）

```mermaid
flowchart TD
    IN["适配已建立基线 / 优化采样证据"] --> PATH["识别 eager / compile / 混合路径<br/>视频生成、VLA、世界模型或引擎局部模块"]
    PATH --> CONTRACT["固定数据、时空 shape、mask 和 loss<br/>autograd、optimizer、EMA、随机性与有效 batch"]
    CONTRACT --> TIME["分开启动 / 编译 / 稳态整步<br/>forward + backward + optimizer + 数据与通信"]
    TIME --> DATA["输入 / host / 同步<br/>解码、预取、H2D、日志与隐式等待"]
    TIME --> GRAPH["图与运行时<br/>断图、guard、重编译、动态 shape、capture"]
    TIME --> TRAIN["训练状态与分布式<br/>saved tensors、重算、DDP / FSDP"]
    DATA --> SELECT["按整步收益与代价排序<br/>明确证据缺口与候选实验"]
    GRAPH --> SELECT
    TRAIN --> SELECT
    SELECT --> MODE{"是否仅分析？"}
    MODE -->|是| REPORT["交付分析报告与建议<br/>不启动优化实验或修改实现"]
    MODE -->|否| IMPL["选定模块 / 调度 / layout / 库实现<br/>编译生成 kernel 按需交 Hygon Triton Skill"]
    IMPL --> VERIFY["输出 / 梯度 / 参数更新 / 多 shape 回归<br/>profiler-off 整步性能 + 显存"]
    VERIFY -->|改进保留，失败回退与重定位| TIME
    VERIFY -->|候选稳定| LOSS["回共同阶段 loss / 质量验收<br/>沿用 flow 复核与私有经验"]
```

它补充 PyTorch 路径特有分析，不重复环境验收、热点上限建模、算子实现、扩 DP 和容错。AOTI/export 仅在真实使用该路径且训练/子模块契约明确时评估，不能默认替代训练编译。详见 [Torch 原生训练指引](../skills/hcu-train-optimize/references/torch-native-training.md)。

### 3.5 通信调度、overlap 与通算融合

```mermaid
flowchart TD
    IN["实际 groups / 消息 / 拓扑 / stream / buffer"] --> BASE["同条件测纯通信、纯计算、训练并发窗口<br/>校时，定位最慢 rank 与关键依赖"]
    BASE --> WHY{"暴露时间来自哪里？"}
    WHY -->|触发或等待不当| SCHED["bucket / chunk / prefetch / 早发晚等<br/>DP、FSDP、TP、PP、CP、EP 对应调度"]
    WHY -->|资源竞争| RESOURCE["计算退化、SM / HBM / NIC / 队列<br/>GPU_MAX_HW_QUEUES 按当前 runtime 对照"]
    WHY -->|计算通信边界可优化| REUSE["先查 HCU Flux / TE / MORI / rocSHMEM<br/>AG-GEMM、GEMM-RS、dispatch-combine"]
    REUSE --> PROTOCOL["定义 chunk ready / 可见性 / progress<br/>buffer 复用、尾块、反向与梯度同步"]
    SCHED --> TEST["多 rank 局部正确性与并发压力<br/>消息 / shape / 空块 / 累积 / 保存恢复"]
    RESOURCE --> TEST
    PROTOCOL --> TEST
    TEST --> E2E["整步对照：暴露时间、吞吐、计算退化<br/>显存峰值与最差 rank / 尾延迟"]
    E2E --> PASS{"净收益成立且数值通过？"}
    PASS -->|否| BACK["回退或调整，重新归因"]
    BACK --> BASE
    PASS -->|是| OUT["纳入共同候选与阶段 loss<br/>混合通算 kernel 仍建计算效率模型"]
```

时间线相交只是观察；不等于通信已隐藏，也不保证训练更快。不同 Agent 共享同一 process-group/协议版本；耦合的同步与 buffer 生命周期由同一 owner 负责，设备/网络测量按资源协调。详见 [通信优化指引](../skills/hcu-train-optimize/references/communication-optimization.md)。

## 4. 每阶段共用：实施、独立复核、修正

```mermaid
flowchart TD
    START["task-create + flow-start<br/>保存目标、上下文、验收与预算"] --> NEXT["flow-next<br/>读取当前事实、工作状态和已采集指导"]
    NEXT --> ACT{"返回的 action"}
    ACT -->|work / repair| WORK["阶段 Skill 实施与测量<br/>本地修改、远端验证、保存证据"]
    ACT -->|coordinate| TEAM["派发 / 消息 / 结果验收<br/>图 5"]
    TEAM --> NEXT
    WORK --> SUB["flow-submit<br/>固定候选 manifest、代码、配置和报告哈希"]
    SUB --> REV["独立 Agent 复核<br/>核对当前目标、context、候选与原始证据"]
    ACT -->|review| REV
    REV --> VER{"accept / revise / blocked"}
    VER -->|revise| WORK
    VER -->|blocked 或 reviewer 失败| ISSUE["记录原因和缺口<br/>修复、重试或按预算请专家介入"]
    ISSUE --> NEXT
    VER -->|accept| GATE["程序核对当前复核与报告门槛<br/>必做任务、阻塞消息、指导、上下文与快照"]
    ACT -->|advance| GATE
    GATE -->|条件不齐 / 已过期| NEXT
    GATE -->|通过| ADV["flow-advance<br/>下一阶段 / optimizing 内 iterate / 完成"]
    ADV -->|继续| NEXT
    ADV -->|完成| DONE["完成与交付记录"]
    ACT -->|reconcile| REC["核查原操作、远端进程与产物<br/>明确结局后才允许后续执行"]
    REC --> NEXT
    ACT -->|human| HUMAN["回应指导 / 补关键条件 / 专家介入<br/>需要调整目标时显式 replan"]
    HUMAN --> NEXT
    ACT -->|completed / cancelled| ENDSTATE["停止本次流程并保留最终状态"]
    GD["GUIDANCE.md<br/>默认每 300 秒采集，显式刷新可立即读取"] -.-> NEXT
    NEXT -.-> BD["BOARD.md<br/>进展、证据、待决问题、Agent 状态与回复"]
```

`accept` 不是 GPU 测试通过的替代物。`target: iterate` 保持在 optimizing，仍须具备局部正确性、真实 dispatch 和至少三组 profiler-off 配对测量；进入扩容准备仍须阶段质量与性能报告。

环境、模型、数据或验证契约变化时重置比较上下文，旧报告保留但不可直接过当前门槛；改回旧配置也不能让旧验收自动复活。新的人的指导、依赖阻塞或候选修改会使未推进的旧复核失效。详见 [协作契约](collaboration.md)。

## 5. 本地多 Agent 与远端执行

### 5.1 动态任务拆解与交互

```mermaid
flowchart TD
    C["本地主控<br/>根据实测热点、依赖、修改范围和资源拆任务"] --> PLAN["team-plan → team-next<br/>只派发输入已就绪、范围不冲突的工作"]
    PLAN --> CLAIM["assignment-claim<br/>原子领取 token、范围和预算"]
    CLAIM --> HOST["宿主原生工具启动实际 Agent<br/>assignment-bind 保存真实 session"]
    HOST --> A["任务 A<br/>本项分析 → 实现 → 局部验证"]
    HOST --> B["任务 B<br/>本项分析 → 实现 → 局部验证"]
    HOST --> N["其余任务<br/>按当前热点动态拆分 / 合并"]
    A <--> MSG["定向持久消息 + 宿主转送<br/>问题 / 答案 / 发现 / 阻塞 / 交接<br/>seen 与 handled 分开"]
    B <--> MSG
    N <--> MSG
    MSG <--> C
    A --> RET["分别返回报告与证据<br/>绑定领取时的依赖结果哈希"]
    B --> RET
    N --> RET
    RET --> CHECK{"主控或其他 reviewer 验收本项结果"}
    CHECK -->|返工| PLAN
    CHECK -->|通过| READY["本项下游可领取<br/>不等待无依赖的其他算子"]
    READY -->|存在后续任务| PLAN
    READY -->|本轮必要结果齐全| JOIN["主控处理交叉约束并集成<br/>验证组合后的正确性和实际收益"]
    JOIN --> FULL["整体候选独立复核<br/>回到图 4"]
```

任务 A/B 是示意身份，**没有固定 Attention、GEMM、MoE Agent 名单**。只对真正的依赖建立等待关系。一个算子准备好了即可优化，其他算子继续分析或优化。

共享 GPU/NIC/测量域的实验排队；设备和干扰域确实隔离时才可并行测量。`resource_scope: operation` 允许开发任务持续并行，仅在执行时租用设备；耦合修改和最终集成由主控协调。CLI 只保存调度契约，不自行启动模型，也不是操作系统隔离沙箱。详见 [多 Agent 协同](multi-agent.md)。

### 5.2 本地代码、远程测量与执行不确定性

```mermaid
flowchart LR
    subgraph LOCAL["本地：主控与专家"]
        DEV["独立开发 checkout<br/>不同于知识库源码缓存"] --> SNAP["source-snapshot<br/>固定选定代码和未提交修改"]
        CARD["CommandCard<br/>argv / cwd / env / timeout / 来源"]
        LEASE["权限、预算、资源租约<br/>持久化执行意图"]
        EV[("私有 objects / 报告 / 事件")]
    end
    subgraph REMOTE["远端：按实际部署适配"]
        RECEIVE["传输并校验 bundle<br/>隔离运行目录"] --> RUN["SSH 裸机 / Conda / Docker<br/>Slurm 已有分配 / K8s 既有 Pod<br/>编译、训练、分析工具和单测"]
        LOG["退出状态、日志、trace、测量产物"]
        UNKNOWN["超时 / 断线 / 控制器中断<br/>不能假定远端进程已停止"]
    end
    SNAP --> RECEIVE
    CARD --> LEASE
    LEASE --> RUN
    RUN -->|明确结束| LOG
    LOG --> EV
    RUN -->|结局不明| UNKNOWN
    UNKNOWN --> REC["reconcile 原操作<br/>查询作业 / 进程 / 输出，保留核查证据"]
    REC -->|结局确定后恢复调度| LEASE
    EV --> JUDGE["Agent 解释证据并决定下一轮"]
```

权重和数据集留在站点存储，不加入代码 bundle。未明结局先核查，不重复启动训练。跨工作区的资源互斥还须依赖站点调度器或统一协调者；本地 SQLite 不能隔离其他程序。详见 [远程执行](remote-execution.md)。

## 6. 扩容、长训、故障与离线接续

```mermaid
flowchart TD
    Q["优化阶段质量 / 性能通过"] --> FULL["恢复完整模型，在可行模型并行规模验证<br/>复核数值、显存和保存恢复"]
    PROXY["资源不足时仅缩 layer 跑通或提前筛机<br/>保留代理范围，不替代完整模型证据"] -.-> FULL
    FULL --> POOL["Cluster Manager 为主筛机<br/>适用时结合 Primus Safe<br/>动态维护健康节点池"]
    POOL --> DP["逐级扩 DP 域<br/>明确强 / 弱扩展与有效全局 batch 策略"]
    DP --> SCALE["每级扩容验收<br/>吞吐效率 / 通信尾部 / 显存 / checkpoint<br/>当前环境 + 阶段质量 + scale 证据"]
    SCALE --> SG{"当前级验收通过？"}
    SG -->|否| FIXS["按问题返回环境 / 适配 / 优化<br/>修复后重新验收当前上下文"]
    FIXS --> FULL
    SG -->|是| MORE{"还需继续扩 DP？"}
    MORE -->|是| POOL
    MORE -->|否| START["按部署授权启动长训<br/>明确唯一 recovery_owner、阈值和监测范围"]
    START --> JOB["训练与 checkpoint 持续运行"]
    JOB --> LOG["现场归一化器<br/>全局进展 JSONL：attempt / step / 时间<br/>loss / grad / 显存 / 恢复状态等"]
    LOG --> WATCH["远端 watcher 持久采集<br/>游标、真实推进时钟、incident 与 outbox"]
    WATCH --> HEALTH{"进展和指标符合预期？"}
    HEALTH -->|是| CURVE["持续记录与分 attempt 曲线<br/>step / loss / grad / 显存 / 事件<br/>吞吐与 checkpoint 结合原始证据"]
    CURVE --> END{"达到约定的完成 / 交接条件？"}
    END -->|否| JOB
    END -->|是| COMPLETE["完成报告、独立复核和运行交接"]
    HEALTH -->|异常| OUT[("持久异常事件<br/>停滞 / 失联 / 恢复超时 / 非有限值 / 性能下降")]
    OUT --> ALERT["站点通知接口<br/>优先既有容错的飞书告警通道"]
    JOB -->|故障由既有规则处理| FT["现场既有容错负责人<br/>按授权隔离 / 重启 / 恢复"]
    OUT --> LOCAL{"本地 Agent 是否可接续？"}
    LOCAL -->|在线且桥接已配置| IN["本地 inbox / Agent bridge<br/>派发并确认接手"]
    LOCAL -->|离线或未配置| KEEP["远端继续监测、通知和既有容错<br/>事件保留，等待本机恢复"]
    KEEP -->|本机恢复| REPLAY["按 seq 导出 / 导入、去重与缺号检查<br/>核对当前 job / attempt / checkpoint / 节点池"]
    REPLAY --> IN
    IN --> AGENT["故障诊断<br/>卡住、core dump、内存 / 显存增长、通信等<br/>日志 / 栈 / 源码 / 最小复现"]
    AGENT --> FIX["准备修复与验证<br/>新代码、参数和重启动作遵守部署授权"]
    FIX --> FT
    FT --> REC{"checkpoint 可恢复且 step 真实推进？"}
    REC -->|是| JOB
    REC -->|否 / 恢复超时| OUT
    SUP["站点 supervisor 托管 watcher<br/>独立 observer 检查其心跳"] -.-> WATCH
    SUP -->|watcher 失活| ALERT
```

本机休眠时远端不临时启动 LLM Agent；继续工作的是 watcher、站点告警和既有容错。通知送达、bridge 返回成功、Agent 接手、故障解决是四种不同状态，不能互相代替。

恢复完整模型或扩 DP 改变比较上下文时，通过 `task-context` 更新并重新规划，取得当前环境/模型对应的基线与质量证据；缩层旧报告不能直接放行完整模型。全参新瓶颈回到适配/优化阶段处理。上图概括推进关系，不绕过 context 重置后的程序门槛。

TrainFlow 提供 watcher、事件重放、inbox、bridge 接口和报告能力；日志归一化、常驻托管、飞书实际通道、宿主接续及站点恢复规则仍要在部署时接好并实测。故障修复不建立第二套抢着重启的控制者。仅诊断任务可直接进入诊断分支，不需要启动训练或取得重启权限。详见 [长训守护](operations.md)。

## 7. 知识检索、更新与成果沉淀

```mermaid
flowchart TD
    PROB["任意阶段的问题<br/>环境 / 适配 / 性能 / 精度 / 故障"] --> EXP["先查私有环境与模型经验<br/>核对实际版本、shape、数据和适用条件"]
    EXP --> LOCAL["官方 Wiki 检索与原文阅读<br/>专题、案例、官方文档、PR、全仓目录"]
    LOCAL --> ANSWER{"已有证据足以回答当前问题？"}
    ANSWER -->|是| USE["应用到当前假设<br/>实施前核对现场条件，之后实际验证"]
    ANSWER -->|否| PR["按问题在线搜已收录 / 未收录 PR<br/>描述、普通评论、行内评论、顶层 review"]
    PR --> CODE["追到固定 head / base 源码<br/>完整函数、调用者、对应底层依赖和测试"]
    CODE --> USE
    PROB -.-> HCU["必装 HCU-Knowledge，三个阶段按问题检索<br/>硬件、工具、patch、配方、优化与故障案例<br/>飞书在线访问另行授权"]
    HCU -.-> USE
    USE --> RESULT["实际里程碑结果<br/>基线、候选、阶段 loss、扩容、异常与恢复"]
    RESULT --> PRIVATE[("私有经验 Wiki<br/>自动保留报告 / 阶段事件<br/>Agent 补充解释、指标口径、失败条件和回退")]
    PRIVATE --> EXP
    PRIVATE --> DELIVERY["所属阶段负责交付<br/>对应工程 PR / Cookbook 最佳实践"]
    DELIVERY --> PUBLIC["公开前按目标仓规则审阅<br/>只交付可公开方法 / 代码 / 获准示例"]
    DELIVERY --> TRACK["经验中记录交付关联<br/>draft / submitted / merged / rejected / superseded"]
    REFRESH["局部官方 Wiki 按需自主更新<br/>问题驱动 / 里程碑 / 版本漂移"] --> FETCH["目录、文档、源码和 PR 讨论增量采集<br/>失败 / 分页未完成保留待办"]
    FETCH --> IMPACT["联动复核总览、专题、案例<br/>相关 Skill / 命令 / 解析器用法"]
    IMPACT --> APPLY["绑定当前页与来源哈希的回执<br/>apply 版本锁 → 重建检索索引"]
    APPLY --> LOCAL
    IMPACT -->|现场暂不能验证| PENDING["用法保持待现场验证<br/>不冒称 Skill 已在 HCU 通过"]
```

- **两个局部 Wiki Skill：**`hcu-engine-wiki-search` 负责检索、PR 和源码追查；`hcu-engine-wiki-update` 负责增量采集、知识复核及关联用法检查。普通查询写私有缓存，正式收录才进入公共知识目录。
- **大知识库边界：**HCU-Knowledge 是完整安装的必需组件，可复用独立 checkout，三个阶段按问题查询；普通 TrainFlow 工作不附带更新它，更新走单独明确的维护任务。本地索引恢复不等于刷新上游内容。
- **版本边界：**局部官方 Wiki 更新不会自动替换当前训练任务的依赖或运行源码。采用新实现要形成新候选并重新验证；官方已吸收的功能应复核本地 patch 是否可以退场。
- **经验边界：**性能、loss、环境和事故的完整档案留 workspace；可复用的实际站点与模型结论、失败经验及精选证据整理进随工程提交的 Wiki。公开 Cookbook 的方法与其私有验证记录建立关联，记录交付不等于自动发送 PR。

详见 [官方 Wiki 检索与维护](wiki.md)、[私有训练经验](experience-knowledge.md) 和 [公开边界](../CONTRIBUTING.md)。

## 8. 图与程序状态的准确对应

以下是 `full` 模式主路径的**报告门槛**，不等于 Agent 阶段内的所有判断。程序还校验报告实际执行、必需覆盖、当前上下文/候选和协作状态。

| 进入状态 | 必需报告 | 对应工作 |
| --- | --- | --- |
| `prepared` | 任务与 flow 计划 | 固定目标、预算、上下文和范围 |
| `environment_checked` | `environment` | 现场环境验收 |
| `baseline_validated` | `baseline` | 初始正确性与数值基线 |
| `profiling` | `baseline` | 以已验证基线开展采样分析 |
| `optimizing` | `analysis` | 形成瓶颈证据，开始候选迭代 |
| `scale_ready` | `stage-quality`、`performance` | 阶段质量与性能通过 |
| `training` | `environment`、`stage-quality`、`scale` | 当前候选满足训练准入 |
| `completed` | `completion` | 达到约定范围的完成条件 |

独立任务另按模式的交付契约判断，不能照搬全流程门槛。图中“先并行切分和显存预算”属于 Skill 的分析顺序，不是新增状态；图中“原生 Agent 派发”和“现场告警”也不意味着 CLI 自带模型服务或飞书机器人。

| 图中机制 | 实现 / 规则入口 |
| --- | --- |
| 任务状态、报告、证据、资源租约 | [core.py](../src/hcu_trainflow/core.py) |
| 候选、独立复核、指导与阶段推进 | [flow.py](../src/hcu_trainflow/flow.py)、[主控 Skill](../skills/hcu-trainflow/SKILL.md) |
| 任务拆解、领取、依赖、会话与消息 | [team.py](../src/hcu_trainflow/team.py) |
| 代码快照、命令卡、远端执行与核查 | [execution.py](../src/hcu_trainflow/execution.py) |
| 覆盖率、时间模型、数值检查、TraceLens | [analysis.py](../src/hcu_trainflow/analysis.py)、[quality.py](../src/hcu_trainflow/quality.py)、[tracelens.py](../src/hcu_trainflow/tracelens.py) |
| watcher、事件同步与 Agent bridge | [monitor.py](../src/hcu_trainflow/monitor.py)、[coordination.py](../src/hcu_trainflow/coordination.py) |
| 官方知识、源码 / PR、来源更新 | [wiki.py](../src/hcu_trainflow/wiki.py)、[official.py](../src/hcu_trainflow/official.py) |
| 私有经验及交付边界 | [experience.py](../src/hcu_trainflow/experience.py)、[delivery.py](../src/hcu_trainflow/delivery.py) |

修改状态、证据门槛、Skill 顺序、协作协议或监测接管规则时，应同时复核本图及 README 总览；只改图不代表实现已经具备相应能力。
