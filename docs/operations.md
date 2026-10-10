# 长训守护、通知与重新接续

统一主控由 `$hcu-trainflow` 进入，阶段 Skill 为 `$hcu-train-scale-and-stability`。为保持已有 TaskSpec 兼容，独立运行模式仍叫 `operate`；Skill 改名不要求改历史任务。

排障步骤见 [故障诊断与恢复验收](../skills/hcu-train-scale-and-stability/references/diagnosis.md)，来源与在线查证见 [证据入口](../skills/hcu-train-scale-and-stability/references/evidence-sources.md)。按实际症状进入，不以重启成功代替根因和长稳验收。

## 部署结构

训练节点或可靠管理节点运行日志归一化器、TrainFlow watcher 和原有容错工具。它们不依赖本机 Agent 在线。归一化器针对当前引擎版本适配，把已验证的全局训练进展写为追加 JSONL；不能把不同 rank 的零散同名 step 混成一条进展流。

每行至少含 UTC epoch timestamp、attempt_id、step；可含 loss、grad_norm、device_memory_bytes、job_alive、checkpoint_verified、recovery_state 和 completed。新进程恢复使用新 attempt_id。显存可记录任务要求的最大设备值，逐设备全量数据另存原始证据。系统不从一条 rank0 日志推断所有设备都健康。

```bash
hcu-trainflow --workspace /private/remote task-create /private/task.json
hcu-trainflow --workspace /private/remote watch TASK /private/normalized.jsonl /private/policy.json --interval 10
```

生产使用站点 systemd/容器 supervisor/调度器托管；`examples/trainflow-watch.service` 是待填模板，不能原样部署。没有现场部署时，工程仅提供运行能力和接入契约。

## 检测与记录

检测无 telemetry、telemetry 过期、step 停滞、同 attempt 步数回退、恢复超时、非有限 loss/grad、显存余量及持续吞吐下降。阈值按模型/步长/checkpoint/网络和历史基线制定，不使用通用生产默认。

日志游标、观测、incident 和 outbox 同事务提交。部分行不消费、重复观测不重复告警；轮转/坏行明确告警。心跳文件是派生产物。`heartbeat-check` 是只检查时间年龄的基础工具；需要校验任务、attempt、launch、进程身份和正常结束时，使用下文的独立观察器。watcher 自己不能证明自己一直在线。

每个 attempt 的开始时间、最高 step 和上次真实推进时间独立持久化，不随最近 1000 条观测窗口滑动；高频心跳不能掩盖停滞或恢复超时。旧游标首次升级时从已保留事件恢复这些时钟。日志轮转同时检查文件身份及已读前缀，小文件也参与检查，正常追加不会被误判为轮转。

## 独立节点观察 watcher 健康

`scripts/observe_remote_health.py` 补上训练节点、容器或 watcher 自身失联后的证据检测。它在另一个节点读取 watcher 的文件证据，写入自己的 **节点本地 Store**。不读取、打开或共享训练 watcher 的实时 SQLite；两边通过文件证据和 `events-export/import` 交换记录。

它复用 `heartbeat-check` 对已保留、不可变心跳快照检查年龄，并额外核对：

- 固定 task/context/context_epoch、attempt、observer launch和spec哈希。
- watcher与训练进程各自的PID、start_ticks、boot_id、PID namespace；不会在观察节点用同号PID猜测另一节点进程是否存活。
- manifest哈希、期望step、开始时间、正常训练退出收据与 watcher退出收据。
- 启动超时、心跳过期、时间倒退或未来时间、文件读取错误、错误退出，以及 watcher自身返回的训练告警。

判为 `completed` 必须同时具有匹配的训练exit0、达到期望step的已验证monitor结果、匹配的watcher正常结束原因和有序时间戳。旧attempt、旧launch、旧epoch或同号PID的新进程不能套用旧完成证据。完成后仍继续读证据；文件消失或换了新launch会重新进入attention，不因曾经完成而永久忽略现场。

**心跳过期表示“当前无法证明观察器继续工作”，不直接断言节点死亡。** 共享存储缓存、网络故障、时钟偏差也可能造成类似现象。跨主机时间在未校准时保持 `observer-source-clock-invalid`，不擅自加一个宽松skew阈值标为健康。现场应确认时钟或接入有依据的时间映射，不能用时钟异常自动触发重启。

### 部署位置和启动

1. 保持原训练watcher及其manager运行方式。选另一物理节点或可靠管理节点，使用本任务独占的容器或进程空间。
2. 将新脚本、对应TrainFlow包和固定contract复制到观察节点**本地文件系统**；例如任务自有容器的 `/var/tmp/trainflow/<task>-health/`。不能只把代码和Python依赖留在同一共享CFS上，否则CFS故障时新reader也可能无法启动。
3. 为观察器建独立本地Store，明确source_domain和observer_domain。脚本要求两者不同，且观察器当前kernel boot_id不能与被观察进程相同；这只能排除明显同机部署，物理故障域仍由部署方确认。Store绑定观察节点domain和boot_id，不允许另一节点悄悄复用同一个库。
4. 首次用 `--once` 验证路径、身份、时钟及退出证明，然后以显式supervisor或脱离本地SSH的进程运行。重复启动会被该Store的独占锁拒绝。更换attempt/launch/策略应注册新的observer_id和contract，先核实旧观察器状态，不能原地替换文件使其无声转向。

```bash
# 示例路径；源码包或PYTHONPATH也应位于观察节点本地。
python -B /local/trainflow/scripts/observe_remote_health.py \
  --workspace /local/task-health/store --contract /local/task-health/contract.json --once

# 交给部署现场的supervisor，或先进行有限次数CPU观测。
python -B /local/trainflow/scripts/observe_remote_health.py \
  --workspace /local/task-health/store --contract /local/task-health/contract.json \
  --interval-seconds 30 --max-polls 4
```

不指定 `--max-polls` 时持续观察；间隔默认30秒，可按watcher周期和站点要求调整。启动、heartbeat年龄、读文件超时必须在contract中分别给定，不把这些示例值当作通用生产阈值。`--once`/达到poll数量后exit0只表示有界观察已执行，健康结果需查看输出中的status/issues。

contract是部署者从真实文件提取的JSON，字段如下；process对象直接沿用原文件中的完整身份：

| 字段 | 来源/含义 |
| --- | --- |
| schema_version、observer_id | 1；本次独立观察范围的唯一ID |
| task_id、context、context_epoch | 被观察任务当前值；epoch取当前monitor证据，不猜默认值 |
| source_domain、observer_domain | 部署确认的不同故障域 |
| source_root | 只读任务证据根路径，限制读取范围 |
| source_workspace | 被观察watcher的Store根路径，仅用于身份和隔离检查，程序不打开其SQLite |
| record_path、manifest_path、training_exit_path、lifecycle_dir | 当前observer-process.json、attempt manifest、真实训练exit、launch证据目录 |
| expected.launch_id、spec_hash、observer_process、observer_started_at | 原manager的observer record |
| expected.attempt_id、manifest_hash、training_process、attempt_started_at、start_step、expected_final_step | 固定attempt manifest及其规范JSON fingerprint |
| policy.heartbeat_max_age_seconds、startup_timeout_seconds、source_read_timeout_seconds | 明确的新鲜度、启动和单次源读取时间限制 |

### 共享存储故障和事件交付

读取共享证据在独立子进程完成，主循环通过单调时钟限制时间。超时只向自己创建的reader发送终止；不阻塞等待内核D状态任务，也不连续派生更多reader。仍未退出的reader会留下身份记录并报告不确定状态，供主控核实。该机制不修复存储，也不保证内核能及时杀掉不可中断I/O。

发生异常时在观察器自己的Store中持久化 `incident-opened`；同一异常不重复打开。只有重新获得匹配、健康的观察证据或完整完成证明才写 `incident-cleared`。源不可读不会清除已有失联事件。open/clear进入自己的agent outbox，后续由明确配置的消费者导出并处理。

这里**没有配置飞书发送、Agent唤醒或训练自动恢复**。没有在线消费者时，事件只留在本地；不能把写入outbox称为已通知人或Agent已接手。持续失联需另一个可靠的通知/监控系统观察sentinel自身的 `observer-health/<id>-heartbeat.json` 和独立进程身份。

CFS故障时，本地Store仍有机会记录读超时；但共享CFS上的源数据和备份可能都不可用。观察节点/本地盘同时故障也会失去此层记录。容器可写层中的Store会随容器删除而丢失，应在存储可用时通过事件/证据导出备份，而非跨节点共享运行中的SQLite或直接复制WAL中的数据库。生产容错不能只依赖两个共享同一故障域的观察器相互宣称存活。

## 本机恢复

远端 `events-export` 按 seq 导出；本机 `events-import` 使用稳定 peer ID 重放并去重，遇到缺号拒绝越过。之后查询 inbox，结合当前 attempt/job/checkpoint 决定处理。不要只依据旧告警重启已经恢复的任务。

派发本地事件时，程序拒绝早于当前 context epoch 的记录，并把领取时的 context/epoch 绑定到执行事务；配置改成 B 后再改回 A，也不能复用原 A 事件启动新的处理。远端事件的本地 seq 是导入顺序，不能证明远端产生时的 epoch：迟到事件仍须核对实际 attempt、进程/作业、checkpoint 和最新观测，必要时只保留为历史。bridge 被唤醒是处理证据的入口，不授予按旧事件直接重启训练的权限。

`inbox --action claim --event ID --owner NAME` 领取，处理后 complete；失败用 retry。agent bridge 可用 `inbox-dispatch ID OWNER CARD LEASE` 执行本地已配置的 launcher，事件文件路径作为最后参数传入。TaskSpec 必须有 execute 和 agent-dispatch。bridge 返回成功仅记录交付，实际 Agent 的接手/完成由 inbox 回执确认。没有已配置且在线的 Agent launcher 就无法自动唤醒它。

飞书优先使用既有容错告警通道；本版本不内置飞书凭据或自动群发。通知成功不等于恢复成功。新增修复上线、重启或隔离权限在具体任务部署时确定，既有容错保持唯一恢复负责人。

## 看板与人类指导

活动主控在关键实验/状态推进前调用 flow-next/flow-board 读取人的意见，等待时按计划轮询。`flow-watch TASK` 可作为本地文件变化采集进程，新增意见进入相同 agent outbox；它不启动模型，也不能单独承诺自动回复。授权 bridge 可在普通执行被待读意见拦住时唤醒主控来处理意见，但训练执行本身仍受检查。

主控将关键曲线/报告路径及阶段结论写入候选报告与看板；人只编辑 GUIDANCE.md，程序不覆盖其内容。具体问题 ID、回复状态、重规划和 review 失效规则见 [协作循环](collaboration.md)。离线期间远端照常记录，恢复后先同步现场事件和人的新意见，避免用旧上下文动作。

bridge 应将事件交给持久队列/宿主接续接口并及时返回，待投递操作结束再由消费者开展任务命令；不要在同任务的 command-run 里面同步阻塞运行整个 Agent。后者会让 Agent 的新命令被仍处于 started 的投递操作阻挡。现场联调要覆盖该时序、重复投递和消费者崩溃，不能仅测试 launcher 退出码。

## 曲线与交付

`monitor-report TASK output.html` 从保留的观测画 step、loss、grad、显存曲线及 incident 时间线；不同 attempt 不连成连续曲线。原始 log 和逐设备细节保留在私有站点存储。曲线平稳不能替代 checkpoint 可恢复性演练或收敛验证。
