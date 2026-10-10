# 工作目录与阅读入口

筛机和健康复核按 `docs/cluster-health-and-screening.md`：复用现场 `run_nhc`、`clush` 与当前 ClusterManager，核对主动负载、超时、逐节点结果、健康重入规则与精确停止范围。没有失败节点交集不等于没有组级故障；先复核原始结果再更新节点池。

安装本 Skill 不会复制整个 Wiki。设置 `TRAINFLOW_PROJECT` 指向已 clone 的 HCU-TrainFlow；`TRAINFLOW_WORKSPACE` 指向任务私有目录。

按需阅读项目：

- `docs/collaboration.md`：统一入口、候选复核、人的文件指导与断点接续。
- `docs/quickstart.md`：安装、任务、证据及 CLI。
- `docs/workflows.md`：三个工作流与验证门槛。
- `docs/environment-discovery.md` 第 6 节：持续退化/扩容差距的分层排查、隔离对照与未解决事项升级。
- `docs/profiling.md`：时间分母、热点建模和 TraceLens。
- `docs/operations.md`：远程 watcher、事件重放与恢复边界。
- `docs/training-observation.md`：真实进度、生命周期与守护的失效范围。
- `docs/distributed-observation.md`：实际进度源与全部必需节点的独立观测、退出封存和聚合完成验证。
- `docs/workspace-maintenance.md`：维护 policy、缓存 pin、context/epoch 观察 Store 与独立事件 peer。
- `docs/training-state-validation.md`：保存/加载/恢复等价的区别，以及优化器与 checkpoint 资源错误排查。
- `docs/wiki.md`：固定来源、更新复核和工作流维护。
- `knowledge/README.md`：官方引擎与生态章节。

不要读取安装目录相对路径猜测仓库位置；先使用明确项目路径。执行前检查 `hcu-trainflow --help` 和相关子命令帮助，不猜不存在的 flag。

## 观察器换代与缓存保护

扩 DP、完整模型恢复或配置变更造成实际 TaskSpec context 变化时，保留旧日志、parser DB、monitor Store、manifest/exit 和生命周期回执。用旧参数检查并精确停止旧观察器，再运行 `scripts/manage_training_observer.py prepare-context` 创建独立 context+epoch Store；它只准备，不启动训练或宣告监控恢复。不能删除 `watch:TASK_ID` 或只换 parser state-dir 绕过两层检查。相同 context 的普通重启保留 Store，使用新的 attempt/进程身份。

新 scope 先 once 检查，再验证全部必需观察器的 ready、心跳新鲜度、进程身份和 monitor 状态；启动超时/unknown 保留 attention。训练日志可能由 rank0、最后一个全局 rank 或显式 logger 输出；先核对固定引擎源码和真实日志，配置实际进度来源，其正常推进只证明该日志覆盖的训练进展，不能代替其他节点进程、成员 launcher 退出、首个错误和资源健康。全组结束必须核全部必需 member 的真实退出结果及训练/checkpoint 契约，不以单个日志源 exit0 或一次 heartbeat 作为整体完成。

多节点任务按 `docs/distributed-observation.md` 冻结全部 wrapper manifest，在各原节点/PID namespace 用 `scripts/observe_distributed_training.py member` 采集，另用 `aggregate` 汇总。明确配置轮询与监督；默认一次采集不代表持续监控。非进度源 rank 不输出 iteration 时只核身份、日志异常和真实退出，不伪造进度。全体 exit0+日志封存+进度源最终步数只证明该 attempt 结束；仍需原 watcher 的 stall/loss、checkpoint/阶段验证，以及独立 sentinel 对采集自身失联的检查。所有 member 缺失/过期/失败均不可被单个进度源正常推进覆盖。

独立 sentinel 改为监测新 Store/launch 的精确身份，覆盖所有必需 member 与监控自身失联；控制节点连通不代表训练容器还健康。新 Store 使用 helper 返回的唯一 `event_peer_suffix` 组成事件 peer；不沿用旧 peer 的增量游标。保留旧 incident 的解除依据、重放/去重记录和交接缺口，必要时让既有恢复负责人处理，不另起第二套自动恢复。

维护沿用主控五分钟循环与已配置 policy，默认 dry-run。有明确自动清理策略时可执行合格登记缓存，运行/恢复涉及的文件必须保持 pin，unknown 进程先核销。checkpoint、故障原始证据、现场日志与数据库不属于自动清理目标；旧目录不因为看似临时就搬移或清除。结束后由各使用者释放自己的 pin；不因心跳过期自动解锁。详细操作见 `docs/workspace-maintenance.md`。

## 复用私有参考基准

筛机、扩容或故障排查时，按 `docs/experience-knowledge.md` 的 `reference-query` 查适用的硬件、软件、拓扑和单测历史。有效的精确匹配减少重复查询；换架构/构建、久未更新、缺项或矛盾则补核对。用 `reference-record` 保留更新后的来源和测量时间，不能把历史正常值当作当前节点健康，更不能据此跳过 `run_nhc`、资源占用确认或真实恢复证据；不顺带更新 HCU-Knowledge。

模型已适配跑通时，后续扩容和恢复验证可以沿用冻结的用户 patch/donor/HCU 适配版本，不必等待差异较大的主仓移植。记录该版本的完整来源和验证边界；最终整合到 HCU 当前活跃出口仍是未完成交付项，整合后需重新验证受影响的正确性、性能、保存恢复和规模条件，不能直接继承另一工作树的通过结论。
