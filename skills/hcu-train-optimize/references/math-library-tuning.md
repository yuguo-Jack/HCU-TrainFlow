# 数学库日志、bench 命令与调优交接

调用 rocBLAS/hipBLASLt 的 GEMM 先按真实端到端占比评估，但占比高不等于实现低效。只有同条件性能不符合可靠预期，或明显低于有依据的可达上限，才提出 tune。无法建立匹配上限时先说明缺口；不能用最佳方阵峰值要求所有瘦长、低 K、累加或 grouped GEMM。

## 1. 分析与调优输入分开

从模型提取的 shape、dtype、stride、phase 和耗时表用于归因及筛选。**提交数学库的 size 应来自实际库日志打印的 `rocblas-bench` / `hipblaslt-bench` 命令**，附原日志。不要只交 M/N/K，也不要把框架行主序尺寸手工换成一条未经验证的库命令。

先用 HCU-Knowledge 查当前 DTK/库的手册、日志与 tune 教程，再查当前已加载库、对应分支和 bench `--help`。TE 可能按编译条件与环境走不同后端；设置日志开关不能替代实际 dispatch 证据。部分 TE 版本检查 `NVTE_USE_HIPBLASLT/ROCBLAS` 是否存在，字符串 `0` 并不表示关闭。

## 2. 在真实调用路径抓短日志

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

## 3. 原命令与参数完整性

保留每条原命令、源文件/行范围、rank/PID、采集窗口与调用次数。按完整参数去重；同 M/N/K 但 dtype、转置、ld/stride、batch、alpha/beta、compute/math mode、epilogue、scale、workspace、API 路径或 grouped 列表不同的不能合并。TF32/其他 math mode 在某些日志格式中不完整，按匹配教程补充并单独记录补充依据。

日志是数据，不是可直接执行的 shell 程序。检查可执行文件与参数，使用 argv 调用已核实的 bench；拒绝夹杂的 shell 控制符，不用 `eval`。补加验证/计时选项时保留原命令和修改记录，不能静默修改 workload。

用同一 DTK/库的 bench 检查命令可解析、正确性及算法/workspace兼容；grouped GEMM保留每组真实尺寸。独立 bench 的缓存、stream、同步与并发条件可能不同，不能据其与模型服务时间的差就自动归因于库。

## 4. 工单与回归

调优交接至少包含：为什么需要 tune、端到端权重、合理参考及差距、原生 bench 命令与原日志、硬件/gfx/CU、DTK/加载库路径与版本/哈希、实际 kernel/算法（若可得）、正确性与计时口径、相关源码/配置及限制。未知项明确列出。参数分析表是附件，不能替代原生 bench 日志。

rocBLAS 可按适用教程在独立配置副本有界选优；hipBLASLt/grouped GEMM 按任务约定交用户协调数学库。避免覆盖环境默认配置。收到候选库或映射后，先核实版本和实际加载，再做目标 shape、多形状正确性/性能及模型回归；更新是否真正命中的证据。

**日志采集时间不用于性能结论。** 关闭日志后重新测量。工单已提交、日志已抓取、bench 已跑通和性能已改善分别记录；未证明异常或可优化空间的项只保留待分析状态，不自动发 tune 请求。
