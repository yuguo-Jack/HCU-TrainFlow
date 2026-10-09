# 私有工作区维护与观察交接入口

先定位 `TRAINFLOW_PROJECT` 和 `TRAINFLOW_WORKSPACE`；命令从真实 checkout 的 `scripts/` 取，不从安装后的 Skill 相对路径推测。详细契约以项目 `docs/workspace-maintenance.md`、`docs/training-observation.md` 为准。三个阶段继续负责各自范围，不新增维护 Skill。

## 接入既有五分钟轮询

主控在私有部署配置/计划中记录维护 policy：默认 dry-run；保持至少最近3代和默认7天未使用；只有部署已经明确允许自动清理时才启用删除。人类交互轮询到期后，由主控至多运行一次维护 tick；若没有登记的缓存，跳过。`flow-watch` 只收文件变化，不会自动执行这个脚本；离线自动维护需要现场已经配置的调用者，不能承诺写了 policy 就会后台运行。

```bash
python /path/to/HCU-TrainFlow/scripts/maintain_workspace.py --workspace /private/task tick
```

已批准并记录的自动策略使用 `tick --enable-delete`；保留期参数放在子命令前。脚本首先做廉价保护判断，只有拟删除条目才深扫。活跃/unknown operation 或 lease 时保留，未知远端进程不因 lease 过期而解除保护。每次处理结果进入私有计划/回执；attention 时核对具体项并暂停自动重试，不替代原任务作业核销。

## 三个阶段如何参与

| 阶段 | 生产者责任 | 观察交接 |
|---|---|---|
| adapt | 新建可重建传输/构建缓存才登记 `cache/recreatable/FAMILY/GENERATION`，保存重建源，使用前 pin，远端接收校验和操作核销后释放 | 首次训练先建立匹配 context 的观察 Store、真实 manifest 和 ready；初始化进度与真实 iteration 分开 |
| optimize | 候选编译、传输、重复解析的可重建中间件可按策略登记；原 trace、数值基线、最好候选、源码快照和验收报告不归缓存 | 比较 context 确实改变时交接新观察范围；只改 attempt 时用新 attempt ID，不无故拆分 Store |
| fault-tolerance | 训练/恢复中的文件持续 pin；故障、checkpoint、恢复证据不自动清理；只有作业终态和责任核销后释放缓存使用 | 旧观察器原参数精确停止/保留，新 Store及每个 member 观察器就绪，独立 sentinel 和事件 peer 同步换代 |

普通老目录、未知临时文件、尚未回传结果不因名字含 tmp/cache 就自动登记。不要移动正在使用的目录以满足清理格式。缓存只要跨进程/节点/Store 使用，相关消费者就必须共同履行 pin；当前 Store 的 operation/lease 检查看不到所有外部使用者。

## context 交接检查

1. 保留旧 Store、原始日志、manifest/exit、observer 生命周期和最后事件序号。按旧 workspace/manifest/policy 验证旧进程，必要时仅停止精确旧观察器；不停止训练，不删数据库解除报错。
2. 在冻结了新 TaskSpec 的源 Store 上运行 `scripts/manage_training_observer.py prepare-context --workspace SOURCE --task TASK --context-root PRIVATE_ROOT`。新路径由完整 context+source epoch 区分，输出只代表 prepared-only。
3. 使用返回的 workspace/state-dir，先 once 检查，再启动匹配新 attempt 的观察器；记录 launch、PID/start/boot/namespace、ready、心跳和 monitor 状态。unknown/启动超时不能当接管成功。
4. 对多节点全部必需 member 做上述检查。由源码与实际日志核对唯一或指定的 iteration/loss 来源，可能是 rank0、全局最后 rank 或专用 logger；不能据它有进展就忽略其他节点；其他成员的进程/容器、launcher退出、异常日志和观察心跳分别核对。整体完成还需全部必需成员成功及有效 checkpoint/阶段验收。
5. 重连故障域独立的 sentinel，匹配每个新 Store/launch 身份，保留旧 incident 的解除或替代依据。事件导出使用 helper 返回的唯一 `event_peer_suffix`（例如 `observer-SUFFIX`），不要沿用旧 peer 的 last_seq；不同 Store 的序号都可能从1开始。

## 安装资源核对

完整安装从已 clone 的 checkout 运行 `scripts/setup_trainflow.py`，Python 包采用 editable 安装，Skill 复制自身 references，项目脚本和文档保留在 checkout。检查 `TRAINFLOW_PROJECT` 下的 `scripts/maintain_workspace.py`、`scripts/manage_training_observer.py`、`scripts/observe_training.py` 与相关 docs 均存在，再调用当前版本 `--help`。

仅 pip 安装 wheel 不会自动提供整个 checkout 的 scripts/docs/Wiki，也不等于完整11个Skill安装。远端若只安装 wheel，需要另同步同一修订的实际使用脚本，并验证 hash/版本；不要在本机升级 Skill 后默认远端脚本也已升级。缺资源先报告明确缺项或补部署，不能悄悄降级为猜命令。
