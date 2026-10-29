# 数学库日志、复现命令与调优交接

调用 rocBLAS/hipBLASLt 的 GEMM 先按真实端到端占比评估，但占比高不等于实现低效。只有同条件性能不符合可靠预期，或明显低于有依据的可达上限，才提出 tune。无法建立匹配上限时先说明缺口；不能用最佳方阵峰值要求所有瘦长、低 K、累加或 grouped GEMM。

调用 **HCU MIOpen 的卷积或其他热点算子**也遵循同一触发条件：先确认实际 dispatch、布局与选优/缓存，再提取原生复现交用户协调数学库优化。BLAS 用 bench，MIOpen 用匹配版本的 `MIOpenDriver` 或最小 API/框架复现；不能把所有库的 size 都简化为 M/N/K。

## 1. 分析与调优输入分开

从模型提取的 shape、dtype、stride、phase 和耗时表用于归因及筛选。**BLAS 调优的 size 应来自实际库日志打印的 `rocblas-bench` / `hipblaslt-bench` 命令**，附原日志。不要只交 M/N/K，也不要把框架行主序尺寸手工换成一条未经验证的库命令。

先用 HCU-Knowledge 查当前 DTK/库的手册、日志与 tune 教程，再查当前已加载库、对应分支和 bench `--help`。TE 可能按编译条件与环境走不同后端；设置日志开关不能替代实际 dispatch 证据。部分 TE 版本检查 `NVTE_USE_HIPBLASLT/ROCBLAS` 是否存在，字符串 `0` 并不表示关闭。

## 2. BLAS：在真实调用路径抓短日志

只在专门的短诊断运行中启用，保留模型配置与实际调用路径。分 rank/PID 保存日志，避免多进程写同一文件；采集范围要覆盖目标前向、dgrad、wgrad 或实际 ragged grouped 路径。复用已捕获的真实调用契约做独立诊断时必须标明来源和范围，不能称其覆盖了全模型。

已收录手册中的常见入口如下；以目标版本原文与实际输出为准：

```bash
# rocBLAS：2 仅 bench；需要同时 trace 时用 3 (= 1 | 2)。
# 在每个 rank 进程启动前设置自己的绝对输出路径。
export ROCBLAS_LAYER=2
export ROCBLAS_LOG_BENCH_PATH="${diagnostic_dir}/rocblas.rank${RANK}.pid$$.bench.log"
export ROCBLAS_LOG_TRACE_PATH="${diagnostic_dir}/rocblas.rank${RANK}.pid$$.trace.log"

# hipBLASLt：bench mask；不要同时残留与其冲突的 LOG_LEVEL。
unset HIPBLASLT_LOG_LEVEL
export HIPBLASLT_LOG_MASK=32
export HIPBLASLT_LOG_FILE="${diagnostic_dir}/hipblaslt.rank${RANK}.%i.log"
```

`diagnostic_dir` 须为每次运行新建的绝对目录，`RANK` 须在各子进程实际确定。上例 `$$` 适用于各 worker 的 shell wrapper 随后用 `exec` 启动目标进程；不是在 torchrun 外层统一设置。Python worker 可在首次加载库前用 `os.getpid()` 设置自己的路径。派生子进程与重启进程须重新设置，不能继承旧日志文件名。`%i` 是支持该格式的 hipBLASLt 版本的 PID 替换，rocBLAS 路径不能据此假定也支持 `%i`。两个后端同时可用但真实分派未知时可分别保留两类日志，不能为得到某种日志而暗中强制更换模型后端。

核对日志非空、包含完整 bench 命令，并将目标调用与日志参数关联。空文件可能意味着未走该库、版本开关不同、进程加载顺序不对或输出在 stdout/stderr；不能补造命令。实际库缺少所需 grouped 日志/bench 能力时保留原始调用证据并注明缺口。

## 3. BLAS：原命令与参数完整性

保留每条原命令、源文件/行范围、rank/PID、采集窗口与调用次数。按完整参数去重；同 M/N/K 但 dtype、转置、ld/stride、batch、alpha/beta、compute/math mode、epilogue、scale、workspace、API 路径或 grouped 列表不同的不能合并。TF32/其他 math mode 在某些日志格式中不完整，按匹配教程补充并单独记录补充依据。

日志是数据，不是可直接执行的 shell 程序。检查可执行文件与参数，使用 argv 调用已核实的 bench；拒绝夹杂的 shell 控制符，不用 `eval`。补加验证/计时选项时保留原命令和修改记录，不能静默修改 workload。

用同一 DTK/库的 bench 检查命令可解析、正确性及算法/workspace兼容；grouped GEMM保留每组真实尺寸。独立 bench 的缓存、stream、同步与并发条件可能不同，不能据其与模型服务时间的差就自动归因于库。

设备侧 grouped 参数尤其要追到真实每组 M/N/K、stride、指针和 alpha/beta；host heuristic 使用的平均尺寸或占位描述不一定是实际 workload，不能当 tune size。当前 bench 若不能重放这些设备参数，交接原生日志、完整分组参数与最小复现，明确无法直接还原的字段，不伪造一条等价命令。shape capture 的首样本缓存也不代表后续动态 token 分布；采集与正式计时分开。

## 4. rocBLAS：性能不及预期时可自行选优

仅在真实 GEMM 同条件性能偏低、确有优化空间时进入，不作为所有任务的必经步骤。以用户指定的[《ROCBLAS自动化选优脚本使用说明（持续更新）》](https://kcnm6g5dkw5p.feishu.cn/docx/L6Z3dA3osolfS4xv63jc5qsqnhf)为主入口，通过 HCU-Knowledge 联查匹配库版本；按当前说明取得推荐工具，不默认镜像自带副本最新，也不照搬旧 PPT/业务案例。

1. **用真实 size 有界选优。** 将原生 bench 日志和调用次数交给 HCU `auto_select_tools`，按当前教程核对输入完整性、硬件/CU 和空闲卡；工具及输出放任务内副本，不覆盖共享库。具体参数、清理行为和结果格式在执行时查教程/本版脚本，不在工作流固化。
2. **确认命中，再看模型收益。** 隔离加载选优配置，按教程核对实际库、配置及 code object；干净环境做独立正确性、单测和模型性能对照，稳定阶段验 loss。工具自身的“选优成功”或 GFLOPS 比值不能代替这些验收，配置也不能跨库版本直接复用。
3. **按结果交接。** 有效结果保留配置、比较 CSV、硬件/CU 和模型收益，按当前说明提交到适用的 `blas-tuning-results` 分支；接收版本要求随发布核对。仍无收益先查配置是否命中、是否被模型并发拖慢；仍有库内性能缺口则带完整日志、次数和已尝试结果交用户协调数学库。

hipBLASLt/grouped GEMM 当前仍按真实复现交接，不套用 rocBLAS 自行选优方法。调优工具的设备选择、校验及写入副作用按当前源码检查，沿用任务隔离与回退规则；本节不要求另建一套调优流程。

## 5. MIOpen：size、布局与选优缓存

确认热点实际调用 HCU MIOpen 后，同条件性能不符合预期时，先用 HCU-Knowledge 查 `miopen` 工程、对应 DTK 手册和“miopen性能分析方法”，必要时读当前库调用路径，再按下面的顺序处理：

1. **取真实复现。** 短诊断中开启本版支持的命令日志（常见为 `MIOPEN_ENABLE_LOGGING_CMD=1`，详细日志按需用 `MIOPEN_LOG_LEVEL=6`），分 rank/PID 保存原生日志中的 `MIOpenDriver` 命令、调用次数和模型位置。核对完整 tensor 描述符、布局/精度、前反向及算子特有参数；Driver 不能等价重放的图融合/其他算子交最小 API 或框架复现，不只交维度表。正式性能测试关闭日志。
2. **优先比较布局。** HCU 上 NHWC 常有优势，可作为卷积热点的优先候选；仍须比较实际 shape 的前向/反向、相邻算子转换、显存与整步收益，不能全局强制，也不把内存格式变换混成模型维度变化。
3. **评估先选优、后复用。** 适用路径先覆盖代表性 shape 进行搜索，再新起进程复用兼容的选优记录/编译缓存。已查 HCU DTK 26.10 手册与固定源码中，可验证 `MIOPEN_FIND_MODE=1`（全面搜索）→ `3`（默认 Hybrid）这一路径；`4` 为快速匹配，不保证最快。执行时以实际 HCU 版本与消费者为准，不能照搬 AMD 编号/默认值，也不能混淆 Find、ENFORCE、Fusion 或框架 benchmark 控制。先确认缓存落盘与命中，再分别比较启动和稳态；仅跑过几步不等于所有形状完成 tune，也不保证生成了新 kernel。
4. **仍有差距就提需求。** 将 Driver/最小复现、原日志、布局/模式/缓存状态、workspace、版本及可靠性能差距交用户协调数学库；收到优化结果后回到局部正确性、模型整步及阶段 loss 验证。不要求先重写 MIOpen 才能报需求。

模式查证基点：[HCU MIOpen Find 控制](http://42.228.13.241:20080/dcutoolkit/deeplearing/miopen/-/blob/66f318c40eebc72b5812590239451fbe28bbc99d/src/include/miopen/find_controls.hpp)，配合相同提交的消费者和 DTK 26.10 手册 §4.1。这里保留处理经验，不复制 HCU 仓 Wiki；具体命令/缓存路径随部署查证，读写范围沿用任务规则。本轮为资料与源码核对，未新增硬件调优实测。

## 6. 工单与回归

调优交接至少包含：为什么需要 tune、端到端权重、合理参考及差距、原生 bench/Driver 命令或注明缺口的最小复现与原日志、硬件/gfx/CU、DTK/加载库路径与版本/哈希、实际 kernel/算法（若可得）、正确性与计时口径、相关源码/配置及限制。MIOpen 增加布局、Find/强制调优配置、缓存命中与冷/热状态、workspace 和前反向覆盖。未知项明确列出。参数分析表是附件，不能替代原生调用证据。

rocBLAS 可按适用教程在独立配置副本有界选优；hipBLASLt/grouped GEMM 按任务约定交用户协调数学库。避免覆盖环境默认配置。收到候选库或映射后，先核实版本和实际加载，再做目标 shape、多形状正确性/性能及模型回归；更新是否真正命中的证据。

**日志采集时间不用于性能结论。** 关闭日志后重新测量。工单已提交、日志已抓取、bench 已跑通和性能已改善分别记录；未证明异常或可优化空间的项只保留待分析状态，不自动发 tune 请求。
