# HCU 算子、通信与底层依赖联动

遇到 HCU 模型适配、性能异常或故障问题，先通过 `$hcu-knowledge-search` 检索大知识库的工程报告、案例、现场资料，再读当前部署或候选分支的源码。不仅按库名搜，还要按实际 shape、错误、调用符号、gfx、DTK、并行域和机制拆问题；同一问题已取回的适用证据可复用，不需每条命令重复查询。普通任务不触发大知识库更新。

本表是候选实现与问题入口，不是所有任务必须安装、切换或全部测一遍的清单。训练引擎与容错工程沿用现有范围。

## 1. 从瓶颈定位到对应工程

| 证据指向 | 优先联查与复用 | 集成时核对 |
| --- | --- | --- |
| 训练融合、attention/linear/低精度、权重与梯度生命周期 | HCU Transformer Engine、Flash-Train、Primus Turbo；原引擎已有实现 | 公共接口、fwd/bwd/dgrad/wgrad、cast/累加精度、实际 dispatcher、主梯度标记、saved tensors、graph/动态 shape |
| Primus/Primus-LM patch 使用的 GEMM/GroupedGEMM、MoE、融合后端 | **HCU Primus Turbo**；AMD Primus/Primus-LM 的调用与优化动机 | HCU 分支与对应 patch/子模块版本，CK/hipBLASLt/AICC/DTK依赖、gfx能力、低精度门禁、空专家/偏斜/容量、后端实际命中；AMD安装说明不直接等于HCU构建方法 |
| 通用集合通信及模型同步 | HCU RCCL及实际插件；需要时比较UCCL collective | process group、实际加载so/plugin、网络/RDMA/NUMA与CPU推进、消息量、异步完成、暴露等待；不能把UCCL整个仓当单一RCCL替换库 |
| MoE dispatch/combine 或 EP 低效 | HCU DeepEP、UCCL EP、MoonEP；按实际能力选择 | 单机/跨机、吞吐/低延迟、sync/async、dtype、handle/plan、token排列、padding/drop与路由权重、前后向、重算、多microbatch、buffer生命周期 |
| 专家负载偏斜、复制与权重/梯度流转 | HCU UltraEP 与引擎专家计算/dispatcher；联查实际rocSHMEM provider | 副本placement/reroute、权重版本、梯度归并与更新归属、异步顺序、拓扑域和额外显存；不能把它当简单dispatch替换后就认为训练语义正确 |
| 设备侧通信、通算融合与推进瓶颈 | HCU rocSHMEM、MORI、Flux及上述库现有路径 | provider/SHCA、symmetric heap、fence/可见性、progress、资源预留与消费者；遵守[通信专项](communication-optimization.md) |
| GEMM或编译/runtime本身成为限制 | HCU rocBLAS/hipBLASLt、CK、AICC/DCC、Galaxy及真实依赖 | 当前分支、编译/链接参数、ABI、实际加载路径、architecture和数值；按证据选择调参、调优请求或局部修复 |

先选择与热点直接相关的一两条候选路径，说明收益假设与排除理由。可以复用实现，也可以移植局部机制；不为“联动”重装全栈。不把某后端 `import` 成功、接口同名、README 上的速度或某个 gfx code object 存在视作目标训练通过。

融合候选还需区分 forward-only 与完整反向、逻辑 shape 与量化/预排布后的物理 shape、写入范围与调用方初始化责任。用非零/非有限哨兵检查未写区域和尾部，核对概率/中间张量的舍入点；不能仅凭 dtype 相同宣称数值等价。新例程或源码中的理论优化不等于生产 dispatcher 已采用，测试默认关闭参考校验或 CI allow-failure 也不构成正确性通过。

编译器升级时核对实际 intrinsic 累加精度、低精度 packing/scale ABI 和最终代码的等待/同步。源码 load 数量可能因向量化而不同于机器事务数；`vmcnt` 非零不能单独证明有效重叠，目标资源上限也不等于实际 VGPR 用量或 occupancy。按当前 HCU 知识和 kernel Skill 继续查 IR/ISA/性能计数器，不复制另一 gfx 的指令门禁或把 no-NaN 假设当通用加速开关。

**新增实现的归属：** 当前 HCU 各库均无适用实现的通用训练 HIP 算子，默认放 HCU Flash-Train；增强 TE 既有算子、接口或优化器实现则交 HCU TE，Primus Turbo 自有模块交其 HCU 仓。引擎保留调用接入、配置和集成测试，不复制通用 kernel。先在独立开发树完成验证，整合/PR 沿用任务的完整工作流交付顺序，不中途切换执行基线。

## 2. HCU 分支与能力边界的检索入口

下表由 **2026-10-12 的 HCU-Knowledge 工程报告**核对，提供仓库身份和分支选择起点，不固定未来任务依赖，也不宣称本轮编译验证。实际操作先用 `$hcu-knowledge-search` 查工程报告和最新来源决策，再确认现场版本与当前源码；同用途公开 HYGON 仓实质同步时优先公开，内部领先则用内部适用分支。DTK `:20080` 与 DAS `:10068` 是两个权限域。

| HCU 工程 / 源码入口 | 已登记分支与修改归属 |
| --- | --- |
| [RCCL](http://42.228.13.241:20080/dcutoolkit/deeplearing/rccl) | `develop` 为集成线；collective 调度、拓扑、transport、设备侧通信归此仓。directRS/XDP/p2p 专项须单独确认是否合入 |
| [rccl-test](http://42.228.13.241:20080/dcutoolkit/driverruntime/rccl-test) | `dtk-26.04.2` 测试集成线；负责复现与计时/正确性测试，不是通信算法库。AMD RCCL 仅作上游参考 |
| [Transformer Engine](http://42.228.13.241:10068/dcutoolkit/deeplearing/TransformerEngine) | HCU `release_v2.16` 配套线与 `main`；模块、低精度状态、融合及接口归此仓。公开同名仓须确认确有 HCU 后端 |
| [Flash-Train](https://github.com/HYGON-AI/flash-train) | `develop` 综合入口；优先复用训练融合算子，没有适用实现的通用 HIP 算子默认交这里 |
| [Primus Turbo](http://42.228.13.241:10068/dcutoolkit/deeplearing/Primus-Turbo) | `wyf-main` 为综合 HCU 线，`perf/hygon-megamoe-asm-final` 是专项；自有算子/backend 归这里，并核对 Primus patch、CK/hipBLASLt/AICC 依赖 |
| [rocSHMEM](https://github.com/HYGON-AI/rocSHMEM-das) | `develop`；设备侧单边通信、heap、provider/SHCA 与内存可见性。消费者实际 gitlink 优先于该分支 HEAD |
| [DeepEP](http://42.228.13.241:10068/dcutoolkit/deeplearing/DeepEP) | `ci-release` 当前内部集成线；[公开仓](https://github.com/HYGON-AI/DeepEP-das)落后能力需按当前决策比较，不直接替代 |
| [UCCL](http://42.228.13.241:10068/dcutoolkit/deeplearing/uccl) | `main`；分别确认 `collective/`、`p2p/`、`ep/`。不能把整个仓当单一 RCCL 替换库 |
| [UltraEP](https://github.com/HYGON-AI/UltraEP-das) | `main` 已为公开主来源；专家复制、reroute、weight sync、grad reduce，内部 `develop` 保留配套参考 |
| [MoonEP](http://42.228.13.241:10068/dcutoolkit/deeplearing/MoonEP) | `develop`，`master` 仅历史初始化；按实际版本检查 dispatch/combine、G1、同步和单/多节点支持 |
| [MORI](http://42.228.13.241:10068/dcutoolkit/deeplearing/mori) | `dcu-mori-ep-internodev1ll`；MORI EP、MORI-SHMEM 和独立 morishmem 源不能互相代替 |
| [rocBLAS](http://42.228.13.241:20080/dcutoolkit/mathlibs/rocblas) / [hipBLASLt](http://42.228.13.241:20080/dcutoolkit/mathlibs/hipblaslt) | 前者 `dtk-26.10.1`，后者 `chitu-develop-bw-nmz` 与对应发版线；先分析真实 bench 命令和 tune 需求，再决定算法/dispatch 修复 |
| [DCC](http://42.228.13.241:20080/dcutoolkit/driverruntime/llvm-project) / [AICC](http://42.228.13.241:10068/dcutoolkit/deeplearing/aicc/llvm-project) | DCC `develop-6.0.0` 是 DTK HIP 编译器体系；AICC `dtk-llvm-6.3.3` / `dtk-llvm-7.2.1` 是独立 AI 编译器，不因同名 llvm-project 混用 |
| [Galaxy](http://42.228.13.241:20080/dcutoolkit/driverruntime/galaxy) | `develop-merge-rock714` 为已选集成线；runtime、stream/event、调度/内存问题先做最小复现，再查对应运行版本 |

CK、Flux、MIOpen、PyTorch/Inductor 等未在表中逐一列出的真实依赖也可按根因修改：从大知识库的对应项目取仓库身份，再沿引擎 build/lock/gitlink 和已加载制品确定目标，不能凭包名拼仓库 URL。权限不足保留缺口，不拿 NVIDIA/AMD 同名源码当作 HCU 实现。

统一知识入口为 HCU-Knowledge `knowledge/projects/<project>/knowledgebase/local/overview/engineering-guide.md`；搜索结果提供固定源码、PR/MR 与原件。这里仅登记引用与归属，内部实现仍在其受控来源，不复制到公开 Wiki。库调用、架构/ABI、provider、精度与完成语义必须与本次任务相符。

## 3. 必要时修改和重编底层库

1. **确定根因层。** 用 profile、最小重现和当前调用链区分引擎调度、接口适配、库实现、编译、runtime或环境。保留原装库对照；收益不清晰时先量化，不直接改多层。
2. **独立工作树与锁定依赖。** 从选定 HCU 活跃分支建立本地开发 checkout，保留用户patch；不能修改知识库源码缓存。记录原基点、子模块/gitlink、DTK/Torch/Python/编译器、构建选项及目标gfx。依赖补丁和引擎适配作为可分别回退的变更组。
3. **本地改、远端构建。** 同步不可变源快照，在任务授权容器和任务目录构建。先读实际构建脚本和帮助，固定ABI与arch、限定编译CPU/内存。产物用任务隔离的wheel/so前缀或独立测试容器；不能覆盖共享 `/opt/dtk`、别人的镜像/容器或系统库来做对照。
4. **证明跑到新实现。** 记录wheel/so/code-object哈希、build-id、实际import路径、动态链接/已加载库、dispatch/backend与相关编译日志。清理或另设候选JIT缓存，避免旧二进制/符号冲突掩盖结果；“编译成功”不是实际加载证明。
5. **分层验证。** 库单元和边界 → 同shape/同消息量实测 → 引擎fwd/bwd/optimizer/多步集成 → profiler-off配对性能与显存 → 稳定阶段loss。通信增加多rank排列/归约、重复调用、异步完成、空token/偏斜/拓扑及保存恢复；低精度变更单独审查数值契约。已验证且未受影响部分引用既有证据。
6. **整合与PR。** 证据支持时保留候选，否则回退原制品。按各目标 HCU 仓规范提交集中、通用的修复和测试，写根因、支持范围、精度/性能、依赖顺序及回退；多个库有关系的PR交叉关联，避免仅以本机安装完成作为交付。训练引擎仍沿用“完整工作流验证后整合目标主仓”的顺序。

极致优化允许深入底层，修改范围由证据和任务权限决定。独立库可并行开发，ABI/通信协议/共享buffer的耦合改动由共同owner协调；新依赖须通知消费者Agent，集成复验前不自动替换其运行中的版本。

## 4. 知识与维护闭环

选库、构建、dispatch、候选收益/回退和失败过程先写任务 experience/看板。仅可跨项目复用的环境经验或模型最终优化里程碑，按 docs/knowledge-architecture.md 筛选必要结论与证据进入共享 Wiki。通用选库和验证方法留本指南，不写入单项目参数、地址或临时补丁。外部目标PR/Cookbook遵循各自发布规范，与本仓知识归属分开。

HCU-Knowledge、官方Wiki或实际工程发现分支/ABI/脚本/后端能力变化时，同步复核本页、通信专项、adapt/optimize/fault-tolerance与相关命令卡。只更新文档不代表活动镜像已升级，也不自动触发大知识库更新。
