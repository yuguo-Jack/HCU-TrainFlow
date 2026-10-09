# Megatron 原始日志与持续观测

训练启动后，远端观察器持续采集真实迭代和生命周期证据；本地主控恢复在线后再同步事件和接续分析。观察器不启动、终止或重启训练，现有容错仍是恢复动作的唯一负责人。

## 数据流

```text
实际训练 stdout/stderr + 进程身份 + 真实退出回执
    → training_logs：有持久游标的增量解析
    → 私有 normalized.jsonl
    → monitor：启动、进展、数值、显存、退出与恢复判断
    → 持久事件 / 告警与 Agent inbox
```

`src/hcu_trainflow/training_logs.py` 依据 Megatron 的 `training/training.py::training_log` 与 `training/utils/common_utils.py::report_memory` 解析记录，不能将任意包含 `step` 的文字视为训练完成。支持当前常见的时间、iteration/total、消耗样本、迭代毫秒、具名 loss、grad norm、跳过/nan 迭代计数和按 rank 打印的显存字段。上游格式变更后，需要同时检查 parser、fixture、监控策略和运行示例。

源码中的平均 loss 为 NaN 时，`avg >= 0` 条件可能使该项不打印；因此 `number of nan iterations > 0` 同样生成数值异常，而非因缺失 `lm loss` 就认定正常。

## 每次启动建立独立 attempt

在实际训练的启动包装器中记录下列 manifest。PID 必须属于观察器能够查阅的 `/proc` 命名空间；Docker 容器内 PID 不能直接当作宿主 PID。可以在宿主观察真实宿主 launcher PID，也可以在同一容器命名空间内观察，但必须如实记录这种部署的失效范围。

```json
{
  "schema_version": 1,
  "context": "CURRENT_TASK_CONTEXT_HASH",
  "attempt_id": "run-001",
  "log_path": "/private/task/attempts/run-001/training.log",
  "log_start_offset": 0,
  "start_step": 0,
  "expected_final_step": 100,
  "started_at": 1700000000.0,
  "log_timezone": "+08:00",
  "process": {
    "pid": 12345,
    "start_ticks": "123456789",
    "boot_id": "ACTUAL_BOOT_ID",
    "pid_namespace": "pid:[ACTUAL_NAMESPACE_ID]"
  }
}
```

示例数值必须替换为现场事实。`process_identity(pid)` 读取 Linux `/proc/<pid>/stat` 的启动 tick、boot ID 和 PID namespace。PID 相同但启动 tick/boot/namespace 不同，属于其他进程，不能延续旧作业的健康状态。未知进程权限或身份读取失败保留为 unknown。

`started_at` 为 UTC epoch 秒；当前 Megatron 文本时间没有时区，`log_timezone` 必须填写现场明确的 `UTC` 或固定 UTC 偏移。不要默认训练节点与本机处于同一时区。`start_step` 表示 checkpoint 起点，不能算一次新进展。`expected_final_step` 是绝对 iteration 目标。新启动使用新的 attempt ID 和日志文件；确实追加同一个文件时必须记录启动前的 `log_start_offset`。

同一 attempt 的 manifest 固定不变。模型/数据/源代码比较上下文改变时使用新的 task/context 和观察目录；普通故障重启可以保持 context，但必须更换 attempt ID 与进程身份，不能靠日志中的 step 回退自动猜测重启。

context 换代还必须隔离 **monitor Store**，不仅是 parser 的 `state-dir`：前者保留 `watch:TASK_ID` 的 context/epoch/输入路径，后者保留原始字节游标。用 `scripts/manage_training_observer.py prepare-context` 从冻结的新 TaskSpec 准备独立 context+epoch Store，保留旧状态；按 [观察器换代流程](workspace-maintenance.md#观察器换-context保留两层身份边界) 完成旧身份停止/保留、新 once/start-ready、独立 sentinel 与事件 peer 交接。不要删除任一数据库中的 context 字段绕过报错。

## 成功退出必须有独立回执

训练包装器或调度器在确认真实进程结果后原子写入退出回执。不能用观察脚本自身的 exit code、`grep` 成功或“PID 不见了”代替训练退出码。

```json
{
  "attempt_id": "run-001",
  "context": "CURRENT_TASK_CONTEXT_HASH",
  "process": {"pid": 12345, "start_ticks": "123456789", "boot_id": "ACTUAL_BOOT_ID", "pid_namespace": "pid:[ACTUAL_NAMESPACE_ID]"},
  "exit_code": 0,
  "finished_at": 1700000100.0
}
```

完成需要：回执的 attempt/context/进程身份完全一致、真实退出码为零、观察到期望的最终 iteration，且没有该 attempt 的致命或非有限数值证据。monitor 还会独立复核真实迭代、时钟、步数回退与回执时间。`completed` 是受验证的运行完成声明，不能代替阶段 loss 验证、性能验收或 checkpoint 可恢复性证明。

当前启动包装器还会在真实子进程退出、日志 flush/fsync 后封存 `log_evidence`：日志的精确路径、字节数和 SHA-256。观察器核对文件内容、已消费的范围以及回执身份，保留核验事实。无源时间或源时间失效的迭代可能在退出后才被采集：不能把采集时间伪造成训练时间，也不能仅因采集晚于退出就永远拒绝完成；这时必须有核验通过的日志封存才能证明这些迭代来自退出前的内容。旧回执有完整源时钟时保持兼容，缺时钟且缺封存时保留 `completion-unverified`。

同一 attempt 的退出回执一旦被观察，不允许随后悄悄更换退出码、时间或日志封存。冲突会成为持久的致命证据。已核验的终态与封存保留在观察器状态中，后续不能通过复用原日志路径将另一轮内容补进这个 attempt。

退出码为零但少跑了目标步数、PID 消失却没有回执、另一轮运行的旧回执、失败回执、仅有启动心跳，均不能完成。已完成 attempt 之后不再从被复用的日志路径导入新训练进展。

## 远端观察器

`scripts/launch_training.py` 可为已准入的明确命令建立一次 attempt：

```bash
python3 scripts/launch_training.py \
  --attempt-dir /private/task/attempts/run-001 \
  --context CURRENT_TASK_CONTEXT_HASH --attempt-id run-001 \
  --cwd /private/task/source --expected-final-step 100 --log-timezone UTC \
  -- python3 train.py --train-iters 100
```

必须替换为当前工程的真实命令。包装器记录自己的 Linux 进程身份、等待其训练子进程，将 stdout/stderr 写入 `training.log`，实际退出后写 `exit.json`。包装器异常消失时没有完成回执，观察器据此保留未确认状态。它不选择卡、不抢占资源、不自动重启，也不充当远端进程监管服务；运行前仍须履行资源准入。启动目录必须是新的，防止覆盖旧 attempt 或在未知执行后盲目重试。

`argv` 必须是会在前台等待训练结束的实际 launcher，例如当前工程已验证的 torchrun 命令。不要传入仅启动后台作业就立即返回的提交脚本，并把它的返回码当作训练退出码；这类调度器需要自己的真实作业终态适配。包装器被打断而子进程仍在运行时不会伪造退出回执，应先核对现有子进程、调度器与 checkpoint，不能立即再启动一份。

安装包也提供一次性采集接口，用于诊断解析与监控状态：

```bash
hcu-trainflow --workspace /private/task/remote-state observe-training TASK_ID \
  /private/task/attempts/run-001/attempt.json /private/task/monitor-policy.json \
  --exit-receipt /private/task/attempts/run-001/exit.json
```

该命令返回结构化 adapter/monitor 结果；有告警时退出码为 2。不要把观察命令的返回码当作训练退出码。持续运行使用下方独立脚本及现场监管机制。

将已审核的工程包/源码与脚本部署到任务私有目录，先在远端 Store 注册同 context 的 TaskSpec。观察器只依赖标准库及工程自身模块；不需要在远端运行大模型 Agent。

```bash
python3 scripts/observe_training.py \
  --workspace /private/task/remote-state \
  --task TASK_ID \
  --manifest /private/task/current-attempt.json \
  --exit-receipt /private/task/current-exit.json \
  --policy /private/task/monitor-policy.json \
  --interval-seconds 30
```

先以 `--once` 验证一轮解析和事件，再交给现场允许的进程监管机制；一次采集有告警时返回 2。持续观察默认只在 `monitor.completion_verified=true` 后退出，不会仅凭 adapter 的 `completed` 声明停止。持续模式正常完成的退出码表示观察任务已结束，遗留的非致命告警仍在结构化输出和事件中，不能将其当作所有性能/loss 验收通过。需要持续等待新的显式 attempt 可使用 `--continue-after-finish`，完成后的轮询仍不是训练进展。同一观察目录通过 Linux 文件锁限制一个实例，重复启动应检查既有观察器，不能删除锁文件绕过它。

### 观察器启动、状态和停止

可用 `scripts/manage_training_observer.py` 在当前 Linux `/proc` 命名空间启动独立观察进程。它只管理观察器，不管理训练。将它与同版本 `observe_training.py` 一起部署，并使用匹配的已安装工程包。下例中的路径、task 和阈值须替换为现场配置：

```bash
observer_args=(
  --workspace /private/task/remote-state --task TASK_ID
  --manifest /private/task/attempts/run-001/attempt.json
  --exit-receipt /private/task/attempts/run-001/exit.json
  --policy /private/task/monitor-policy.json --interval-seconds 30
)
python3 scripts/manage_training_observer.py start "${observer_args[@]}"
python3 scripts/manage_training_observer.py status "${observer_args[@]}"
python3 scripts/manage_training_observer.py stop "${observer_args[@]}"
```

`start` 等待该次 launch 的首轮采集回执，默认最多 30 秒，可用 `--timeout-seconds` 指定不超过 60 秒的等待。仅看到 PID 存活不会报告启动已就绪；启动超时会保留 `attention` 和进程记录，应先检查现有进程、stderr、锁和首轮回执。它不会为超时再启动一份，也不会自动杀掉尚在读取大日志的观察器。启动错误保留在该 launch 的目录，返回非零状态。

同 state 目录中已存在身份匹配的观察器时，完全相同参数的 `start` 只返回现状；若旧 attempt 仍在运行、新请求的配置不同，拒绝启动。PID 被复用、命名空间不符或身份不明时也拒绝替换。managed 模式固定一份 attempt manifest 和 policy 内容；更换 attempt 或策略应先以原参数停止、保留原件，再用新参数启动。不要原地改写输入文件。独立脚本的 `--continue-after-finish` 用于另行管理的持续观察场景，不与 managed 模式混用。

状态字段分别回答不同的问题：

| 字段 | 含义 |
| --- | --- |
| `process.status` | 精确身份进程当前是否存活；僵尸 `Z` 是 exited |
| `heartbeat_freshness` | 当前 launch 回执是否 fresh、stale、missing 或时钟不符；默认阈值 120 秒，可用 `--freshness-seconds` 修改 |
| `ready` | 当前 launch 是否至少完成一次观测；该次观测也可以正确报告训练失败 |
| `monitor_status` | 最后一次训练观测的结果；观察器存活不代表训练正常 |
| `training_completion_verified` | 最后一次 monitor 对训练完成的证据校验，不代表 loss 或性能验收 |
| `observer_exit` | 观察器自己的退出回执，绝不能替代训练 wrapper 的退出回执 |

`observing` 需要进程存活、首轮已完成、心跳新鲜且 monitor 正常。进程存活但心跳过期、训练失败、观察器异常退出均保留 `attention`。`stopped` 表示明确停止了观察器，原训练告警继续保留；`completed` 需要 monitor 已验证训练完成且观察器因此正常退出，属于终态证据，不是仍在采集的健康心跳。

`stop` 校验原 attempt/context/配置、PID 启动 tick、boot ID、PID namespace 和完整 argv，使用 Linux pidfd 对精确进程发送 SIGTERM。它在打开 pidfd 后再次核对身份，防止数字 PID 复用误杀其他进程。缺少 pidfd 支持时拒绝发送信号，没有普通 `kill PID` 回退，也不会升级到 SIGKILL 或触碰训练进程。停止等待超时仍返回 `attention`，保留现场供人工或 Agent 分析。

### 多节点：训练进展与全部成员健康

一些引擎由 rank0 输出进度，另一些分支用全局最后 rank 或专用 logger。先检查固定版本的打印调用者及真实日志，再把实际来源写入进度配置。把它作为训练进展来源时，应明确采集覆盖范围，并另核对全部必需 member 的 launcher/容器进程身份、观察器 ready 与心跳、异常日志和真实退出结果。指定来源有进展不能证明其余观察器正常；没有 iteration 的非主 rank 也不能被强行伪造进度。当前单个 watcher 的 `completion_verified` 只验证其 manifest/log/receipt 范围，主控还需要集合所有必需成员结果及 checkpoint/阶段契约，才能判整体完成。

独立 sentinel 按各成员的具体 workspace/launch/精确身份监测，不能只检查一个节点能 ping 通。context 或观察 Store 更换后，先使新观察器实际完成首轮采集并验证心跳，再替换 sentinel 目标；保留旧 incident 的解除/替代依据与交接缺口。独立节点、进程存活、心跳新鲜、真实训练推进和最终告警投递分别留证，不能互相代替。

CLI 一次性采集、Python `observe_once`、底层日志采集与 daemon 共用 `observer.lock`；daemon 在整个循环期间持锁，一次性接口在解析、导出和 monitor 入库全部结束后释放。管理操作另有控制锁，避免同时 start/stop。不要删除锁文件绕过锁，也不要通过另建 state 目录启动第二个写者。同一路 task 的 monitor 输入路径固定，更换观察目录需要明确迁移。

默认状态路径为 `WORKSPACE/training-logs/TASK_ID`，包含：

| 文件 | 用途 |
| --- | --- |
| `training-log.sqlite3` | 原始字节记录、输入游标、attempt 状态、不可变规范化样本与输出游标 |
| `normalized.jsonl` | 供现有 monitor 增量消费的派生日志 |
| `observer.lock` | CLI/API/daemon 共享的单写锁；存在并不代表仍被持有 |
| `observer-control.lock` | 生命周期管理操作互斥 |
| `observer-process.json` | 当前 managed launch 的精确身份和输入配置 |
| `observer-launches/LAUNCH_ID/` | 每次启动的 request、process、identity、ready、heartbeat、observer-exit、stdout/stderr 与启动/停止结果，保留历史 |

原始游标与样本先在同一事务内提交，再导出 NDJSON。导出中断后可以从数据库恢复；重复行不会再次计作迭代进展。NDJSON 属于观察器输出，不应手工编辑。保留数据库、原始日志、attempt 和 exit 回执后才能清理任务临时目录。

共享文件系统必须支持所选 SQLite/文件锁语义；每个 state 目录只由一个观察器写入，不可跨节点并行操作同一数据库。部署时验证真实文件系统的掉线与恢复行为。任务日志可以在共享盘，观察器状态也可以放在有可靠锁语义的节点私有目录，并通过既有备份/同步机制保存。

## 三类时钟和策略

- `timestamp`：源 iteration 的时间；用于真实推进、间隔和停滞判断。
- `observed_at`：观察器实际收到这条记录的时间；批量读取或日志缓冲可能使它晚于 iteration。
- heartbeat：观察器本次仍能执行，只刷新采集时钟，保留最后真实 step，`progress_observed=false`。

没有源时间的旧日志保留首次观察时间，并明确标记时间依据不足；不能据此宣称完成准确的墙钟性能对比。正常的延迟到达不应与真正的 iteration 时间回退混为一谈。

真实源时钟、采集 fallback 时钟与 heartbeat 分别检查。带 fallback 时间的窗口不用于墙钟 `sustained-slowdown` 计算，避免把采集排队时延当作训练变慢。可以保留日志自身打印的每迭代耗时用于后续分析，但不能混合两种分母。

```json
{
  "startup_timeout_seconds": 1800,
  "stall_seconds": 180,
  "telemetry_seconds": 120,
  "recovery_seconds": 1800,
  "min_progress_samples": 2,
  "performance_window": 5
}
```

这些数值只示范配置字段。实际阈值由现场的编译、数据构建、checkpoint 恢复和稳态迭代耗时确定。`startup_timeout_seconds` 单独约束首次真实迭代前的初始化/编译阶段；出现真实迭代后使用 `stall_seconds`，不能靠把 phase 改回 startup 避免停滞告警。`telemetry_seconds` 监测采集本身；`recovery_seconds` 仍与既有容错的恢复证据和 checkpoint 校验联动。

## 显存与异常

Megatron 的 `memory (MB)` 实际使用 `1024**2` 分母，转换成字节时按 MiB 处理。allocated/reserved 和各自峰值保留在 `memory_by_rank`，它们不是物理设备的全部用量。只有明确出现 `total device memory used` 时才生成物理显存使用字段，并标明仅覆盖打印该项的 rank。需要持续 headroom 判断时，启用所选版本支持的周期显存日志，或补充 HCU 设备侧采集；不能把前两步的一次 allocator 报告当成长训全设备实时监控。

非有限 loss/grad、nan iteration、RuntimeError/OOM/崩溃线索、PID 复用、原始日志缺失或轮转、权限与解码问题都会进入结构化告警。日志轮转保留旧样本并按原始行哈希去重，但会明确提示连续性需要核对，不能因此宣称未丢行。最终无换行的完整记录只有在匹配退出回执后才会被消费。

## 事件同步与私有观测图表

在远端观察 Store 导出事件，传回本机时保留原始字节并核对 SHA-256，再导入本机 Store。两端使用同一 TaskSpec/context；现场路径和 peer 名称由部署配置提供：

```bash
# 远端：只导出已有事件；增量同步时填写上一次核对过的 last_seq。
hcu-trainflow --workspace /private/task/remote-state events-export /private/task/export/events.json --after 0

# 本地：先注册相同 TaskSpec，再导入从远端完整复制的文件。
hcu-trainflow --workspace /private/task/local-state events-import remote-observer /private/task/export/events.json
hcu-trainflow --workspace /private/task/local-state monitor-report TASK_ID /private/task/reports/observations.html
```

同一 peer 的重复导入不增加事件。导入的 `last_seq` 只是事件游标，不能替代真实训练进展。用于离线分析时，可以创建独立的私有报告 Store，避免与正在运行的主控状态混用；导入后也不能直接发起恢复或重新启动，仍须核对当前作业、attempt 和 checkpoint。

新的观察 Store 从新的序号空间开始，使用 `prepare-context` 返回的 `event_peer_suffix` 组成独立 peer；它同时区分 source/task/context/epoch/目标 Store，不能只用 context 字符串，更不能沿用旧 peer 的 last_seq。多成员独立 Store 各用自己的 peer。共享数据仍按 context/attempt/member 映射归档，而不是将序号相同的事件视作相同观察。

`monitor-report` 输出 HTML/SVG 与同名 `.data.json`，后者包含选中事件的结构化投影、事件 ID、指标点、告警和数据质量说明；HTML 中记录 sidecar SHA-256。它不是原始日志或导出文件的逐字节副本，仍应独立保留原日志、退出回执、事件导出原件及其哈希。Python API 可以限制具体 attempt/context，CLI 默认展示该任务已有记录：

```python
from hcu_trainflow.core import Store
from hcu_trainflow.delivery import monitor_report

monitor_report(
    Store("/private/task/local-state"), "TASK_ID",
    "/private/task/reports/run-001.html",
    attempt="run-001", context="CURRENT_TASK_CONTEXT_HASH",
)
```

图表遵循以下规则：

- loss、梯度范数、已报告迭代耗时及吞吐只使用真实 `iteration` 记录，要求 `progress_observed=true`。heartbeat、memory 和生命周期记录即使携带上次的 loss/step，也不生成新的训练点。
- 旧的规范化样本保持兼容，时钟来源注明未知。现代样本缺少 `timestamp_basis` 时单列未知时钟；collector fallback 单列采集时钟，均不连接成可信训练时间曲线。源时钟回退明确提示，不能据此推导稳态速度。
- 不同 context/attempt 分开；同一个 ID 意外更换进程身份、启动时间或经历 context 重置时，再拆为不同显示段，保留契约异常提示。
- rank 显存使用自身 `observed_at`，重复携带的快照去重。allocator、allocator 峰值和物理设备用量分别展示为散点，不插值；同一次批量采集中相同时间/值只表示一个已知快照，原始 memory 行仍完整保留在事件投影中。
- 布尔、负显存、非有限数值、不可呈现的时间戳和格式错误保留为数据质量缺口，不转成零值。缺少吞吐或物理显存时明确显示未采集，不由 loss/步数或 allocator 推算补齐。
- 报告 `status=complete` 表示图表已生成；没有可绘制指标为 `incomplete`。两者均不表示训练已完成、loss 收敛或优化验收通过。短跑、合成数据和缩模的边界应与报告一同记录。

图表及 sidecar 默认属于私有证据，可能包含日志路径、内部环境和错误信息。发布最佳实践时仍通过显式文件白名单和内容审查导出，不将整份观测 Store 或报告上传公共仓库。

## 本机离线与失效范围

观察器由远端监管进程维持运行。本地 Agent 离线时，它继续产生事件和已有告警通道所需的 evidence；既有容错仍负责恢复。主控重新上线后按事件游标同步，核对当前 attempt/进程/checkpoint，再接续处理。

还需要在不同失效域检查观察器 heartbeat：与训练同容器的观察器无法证明容器被销毁后仍有监控；与训练同节点的观察器无法在节点掉电后告警。独立节点/跳转节点或既有容错应监测观察器失联。仅让 daemon 在运行，不等于飞书发送和 Agent 唤醒已接通；这两种投递必须按部署时的授权分别配置、测试和保留回执。

生命周期管理器使用 detached session 使观察器不依赖当前 SSH 终端，但它不是 systemd、Kubernetes 或容错系统的替代品，不承诺容器/节点失效后自动恢复。Docker 新部署可使用允许的 `--init` 或已验证的监管进程回收孤儿/僵尸；既有容器 PID 1 不回收时，停止后的 `Z` 进程不算仍在工作。上线验收必须单独测试观察器崩溃、节点失联、外部心跳检测、告警投递和本地主控接续。
