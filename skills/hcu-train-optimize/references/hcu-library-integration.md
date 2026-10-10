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

## 2. HCU 分支与能力边界的检索入口

下列为 **2026-10-10 读取 HCU-Knowledge 保留报告的来源**，不是本轮新编译或新硬件验证。实际使用前核对当前仓和部署版本；当 GitHub HYGON 同用途仓与内部等价时优先公开，内部实质领先用其活跃分支。

- `primus-turbo`：内部 `dcutoolkit/deeplearing/Primus-Turbo`，通用 HCU 线 `wyf-main@717671bc4597f4f0850324b1dca37589b0b06195`；`perf/hygon-megamoe-asm-final` 为专项线，不能因名字新就替代通用线。先读 `tools/hygon_setup_utils.py`、`primus_turbo/common/hygon_runtime_utils.py`、`pytorch/core/backend.py`、`ops/grouped_gemm.py` 和实际 MoE dispatcher。现有构建识别有 DTK 版本限制、AICC/CK/外部 DeepEP 要求；升级镜像后须复核。shape profile 是采样/调试功能，与正式计时分开。
- `uccl`：内部 `dcutoolkit/deeplearing/uccl`，`main@c84261ae83158e307decfc18b290212f3fcd1b37`。区分 `collective/`、`p2p/Makefile.dtk` 与 `ep/setup.py` 三条路径；核实 provider、rail、CPU proxy、真实gfx及Torch ABI。DeepEP接口风格相近不代表handle可互换。
- `ultraep`：内部 `dcutoolkit/deeplearing/ultraep`，`develop@876af49045f36608ebe1743f070786959de83c3f`。当前入口 `docs/hcu.md`、`build_hcu_shca.sh`、`tests/hcu/`；按所需路径追 `weight_sync`、`reroute`、`grad_reduce`、runtime/provider。旧 `dcu_*` 路径需对版本，DTK/HCU同义不代表历史命令原封可用。
- `moonep`：内部 `dcutoolkit/deeplearing/MoonEP`，`develop@d913e0088c11966dcdcf45d059e3955ec6c3bccb`；`master` 仅初始化。保留报告描述的是节点内 BF16、同步、单 inflight、`zero_copy=True` 的候选，不能假定跨节点、FP8、graph、公共异步event或Megatron集成已支持。读 `README_CN.md`、`RELEASE_COMPATIBILITY.md`、`moonep/api.py`、`tests/TEST_MATRIX.md`，再追 native 实现。

统一知识入口为 HCU-Knowledge `knowledge/projects/<project>/knowledgebase/local/overview/engineering-guide.md`；搜索结果提供固定源码与原件。不写死别人的本机知识库路径。没有权限或内容落后时如实记录，并在当前授权范围读取上游/内部新源码，不能换成 AMD/NVIDIA 同名仓假装 HCU 已支持。

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
