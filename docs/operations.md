# 长训守护、通知与重新接续

统一主控由 `$hcu-trainflow` 进入，阶段 Skill 为 `$hcu-train-fault-tolerance`。为保持已有 TaskSpec 兼容，独立运行模式仍叫 `operate`；Skill 改名不要求改历史任务。

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

日志游标、观测、incident 和 outbox 同事务提交。部分行不消费、重复观测不重复告警；轮转/坏行明确告警。心跳文件是派生产物，独立 observer 用 heartbeat-check 检查 watcher 失活。watcher 自己不能证明自己一直在线。

## 本机恢复

远端 `events-export` 按 seq 导出；本机 `events-import` 使用稳定 peer ID 重放并去重，遇到缺号拒绝越过。之后查询 inbox，结合当前 attempt/job/checkpoint 决定处理。不要只依据旧告警重启已经恢复的任务。

`inbox --action claim --event ID --owner NAME` 领取，处理后 complete；失败用 retry。agent bridge 可用 `inbox-dispatch ID OWNER CARD LEASE` 执行本地已配置的 launcher，事件文件路径作为最后参数传入。TaskSpec 必须有 execute 和 agent-dispatch。bridge 返回成功仅记录交付，实际 Agent 的接手/完成由 inbox 回执确认。没有已配置且在线的 Agent launcher 就无法自动唤醒它。

飞书优先使用既有容错告警通道；本版本不内置飞书凭据或自动群发。通知成功不等于恢复成功。新增修复上线、重启或隔离权限在具体任务部署时确定，既有容错保持唯一恢复负责人。

## 看板与人类指导

活动主控在关键实验/状态推进前调用 flow-next/flow-board 读取人的意见，等待时按计划轮询。`flow-watch TASK` 可作为本地文件变化采集进程，新增意见进入相同 agent outbox；它不启动模型，也不能单独承诺自动回复。授权 bridge 可在普通执行被待读意见拦住时唤醒主控来处理意见，但训练执行本身仍受检查。

主控将关键曲线/报告路径及阶段结论写入候选报告与看板；人只编辑 GUIDANCE.md，程序不覆盖其内容。具体问题 ID、回复状态、重规划和 review 失效规则见 [协作循环](collaboration.md)。离线期间远端照常记录，恢复后先同步现场事件和人的新意见，避免用旧上下文动作。

bridge 应将事件交给持久队列/宿主接续接口并及时返回，待投递操作结束再由消费者开展任务命令；不要在同任务的 command-run 里面同步阻塞运行整个 Agent。后者会让 Agent 的新命令被仍处于 started 的投递操作阻挡。现场联调要覆盖该时序、重复投递和消费者崩溃，不能仅测试 launcher 退出码。

## 曲线与交付

`monitor-report TASK output.html` 从保留的观测画 step、loss、grad、显存曲线及 incident 时间线；不同 attempt 不连成连续曲线。原始 log 和逐设备细节保留在私有站点存储。曲线平稳不能替代 checkpoint 可恢复性演练或收敛验证。
