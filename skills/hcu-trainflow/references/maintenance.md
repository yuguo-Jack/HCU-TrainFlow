# 私有工作区维护与观察交接入口

先定位 `TRAINFLOW_PROJECT` 和 `TRAINFLOW_WORKSPACE`；命令从真实 checkout 的 `scripts/` 取，不从安装后的 Skill 相对路径推测。详细契约以项目 `docs/workspace-maintenance.md`、`docs/training-observation.md` 为准。三个阶段继续负责各自范围，不新增维护 Skill。

## 按阶段和低频时机维护

维护与默认五分钟人类交互采集分开：一批实验结束、阶段交接、故障恢复核销、任务收尾时触发；同阶段长训默认每6小时一次，阶段/空间触发也有1小时冷却。不要在每个参数点、kernel、Agent 消息或交互轮询中扫目录。先确认上一轮操作回执和本批产物生命周期，未到期的 tick 返回 not-due，不遍历文件树。

```bash
python /path/to/HCU-TrainFlow/scripts/maintain_workspace.py --workspace /private/task \
  tick --trigger experiment-batch
```

部署 policy 明确允许自动清理后加 `--enable-delete`，不需重复询问；默认 dry-run。缓存保留最近3代/默认7天未使用；临时大文件通过 `register-temporary` 登记，确认写者与消费者结束、必要证据保留后 `retire`，默认静置1小时；最终收尾的零宽限策略及条件见详细文档。释放 pin 不等于允许删除。完整命令、生命周期及保护条件见项目 `docs/workspace-maintenance.md`。

大 checkpoint 保存或大规模采集/构建前只用 `capacity` 检查磁盘剩余量，另查站点配额，与估计写入量和余量比较。低空间先回收合格项，仍不足就报告空间缺口并暂停新的大写入，不擅自终止训练或删除恢复点。看板只在发生清理、空间告警或 attention 时记录前后可用空间、逻辑删除量、保留原因和回执。

本地、远端、容器节点盘分别确定真实维护根和唯一调用者；同一 CFS 挂载只管理一次。`flow-watch` 仍只收交互文件，离线维护需已有远端调用者显式部署同版本脚本。活跃/unknown operation 或 lease 保守阻止整个 Store 的删除；pin 还覆盖跨进程/节点/Store 使用者。attention 后先核对计划和隔离回执，核销后才用 `--resume-after-review`；不循环重试。

## 三个阶段如何参与

| 阶段 | 生产者责任 | 观察交接 |
|---|---|---|
| 检查与适配 | 建立本地/远端容量阈值、维护根与负责人；缓存登记重建方法，临时输出登记 owner/pin，适配批次收尾明确废弃项 | 首次训练建立匹配 context 的观察 Store、真实 manifest 和 ready；初始化进度与真实 iteration 分开 |
| 分析与优化 | 一批候选核销后退役无用调试 dump、重复 profiler 中间物或临时保存点；保留原 trace、基线、最好候选及可复现证据 | 比较 context 确实改变时交接新观察范围；只改 attempt 时用新 attempt ID，不无故拆分 Store |
| 扩规模与长稳 | 保存前查空间，恢复核销后处置无效临时保存点；最新有效、best、基线、回退/恢复 checkpoint 和故障唯一原件继续保护 | 旧观察器原参数精确停止/保留，新 Store及每个 member 观察器就绪，独立 sentinel 和事件 peer 同步换代 |

不扫描整机猜哪些文件可删，不移动正在使用的目录来满足清理格式。正式模型、源码 checkout、原始材料、日志、证据与数据库在清理根之外；不因已经出图就丢弃原 trace。部署和数据用途未确认的旧目录保留。保留点用途、writer 停止和证据充分性由阶段 Agent 判断，不能误称维护脚本自动证明了这些事实。

## context 交接检查

1. 保留旧 Store、原始日志、manifest/exit、observer 生命周期和最后事件序号。按旧 workspace/manifest/policy 验证旧进程，必要时仅停止精确旧观察器；不停止训练，不删数据库解除报错。
2. 在冻结了新 TaskSpec 的源 Store 上运行 `scripts/manage_training_observer.py prepare-context --workspace SOURCE --task TASK --context-root PRIVATE_ROOT`。新路径由完整 context+source epoch 区分，输出只代表 prepared-only。
3. 使用返回的 workspace/state-dir，先 once 检查，再启动匹配新 attempt 的观察器；记录 launch、PID/start/boot/namespace、ready、心跳和 monitor 状态。unknown/启动超时不能当接管成功。
4. 对多节点全部必需 member 做上述检查。由源码与实际日志核对唯一或指定的 iteration/loss 来源，可能是 rank0、全局最后 rank 或专用 logger；不能据它有进展就忽略其他节点；其他成员的进程/容器、launcher退出、异常日志和观察心跳分别核对。整体完成还需全部必需成员成功及有效 checkpoint/阶段验收。
5. 重连故障域独立的 sentinel，匹配每个新 Store/launch 身份，保留旧 incident 的解除或替代依据。事件导出使用 helper 返回的唯一 `event_peer_suffix`（例如 `observer-SUFFIX`），不要沿用旧 peer 的 last_seq；不同 Store 的序号都可能从1开始。

## 安装资源核对

完整安装从已 clone 的 checkout 运行 `scripts/setup_trainflow.py`，Python 包采用 editable 安装，Skill 复制自身 references，项目脚本和文档保留在 checkout。检查 `TRAINFLOW_PROJECT` 下的 `scripts/maintain_workspace.py`、`scripts/manage_training_observer.py`、`scripts/observe_training.py` 与相关 docs 均存在，再调用当前版本 `--help`。

仅 pip 安装 wheel 不会自动提供整个 checkout 的 scripts/docs/Wiki，也不等于完整11个Skill安装。远端若只安装 wheel，需要另同步同一修订的实际使用脚本，并验证 hash/版本；不要在本机升级 Skill 后默认远端脚本也已升级。缺资源先报告明确缺项或补部署，不能悄悄降级为猜命令。
