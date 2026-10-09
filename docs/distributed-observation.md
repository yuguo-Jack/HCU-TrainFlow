# 分布式训练的成员观测

`scripts/observe_distributed_training.py` 在指定进度源的日志监控旁补充全部必需节点的证据。它仅使用 CPU 读取进程身份、日志与退出回执；不连接远端、不查询或占用 GPU、不重启训练，也不替代现有容错负责人。

## 三种结论分开

| 证据 | 证明什么 | 不能据此证明什么 |
| --- | --- | --- |
| 实际训练日志源的 iteration/loss | 该日志记录的训练进展；现有 watcher 检查启动、停滞、数值、吞吐和显存 | 全部节点或其观察器都健康 |
| 每个 member 的新鲜观测 | 对应 wrapper 的 boot/PID namespace/PID/start ticks、日志异常和退出情况 | 每个 torchrun worker、设备、网络或 checkpoint 都健康 |
| 全部 member 成功退出且进度源记录最终步数 | 此固定分布式 attempt 的退出与最终步数契约完成 | loss 验收通过、checkpoint 正确、长训可靠性或完整模型能力验证通过 |

这里的 member 是**每节点一个受监督 launcher**，不是每个 GPU rank。训练包装器等待本节点 torchrun，保留真实子进程退出码。某个 worker 卡住而 wrapper 仍存活时，还需要 进度源的 stall 监控、独立 sentinel 和既有故障诊断；不能只靠 launcher 存活判断训练正常。

## 先确定哪一份日志真正记录进度

不能把协调节点、node0 或 rank0 固定当作 iteration/loss 来源。应阅读当前冻结引擎的训练日志调用者和打印 helper，再核对最初几步真实日志及 global-rank→member 映射。例如有些 Megatron 分支在 `training_log` 调用 `print_rank_last`，其 `is_last_rank()` 判断全局 rank=`world_size-1`；这与“每个 PP 组的最后 stage”不是同一选择条件。模型、引擎分支和 logger 行为改变后重新确认。

将实际节点写入显式 `progress_member`，并让单源训练 watcher 指向该节点的 manifest/log。若选错，保留误选导致的 attention/缺步证据；不要将其他节点的 memory/heartbeat 改写成 iteration。切换进度来源时优先按成员建立独立 parser 和 observer Store；若改变 normalized log 路径，必须同时换 Store，否则会触发 `Watcher log path changed`。同 context、同 normalized 路径可以在原 writer 确认停止后串行接收不同 attempt，但须满足原 adapter 的身份、时序和新 attempt 检查，不能让两个节点并发共用游标。使用 prepare-context 时可把新的 member 来源加入 context_root 的独立目录，保留旧 Store，并为新 sentinel/event peer 重新绑定。更换来源本身不证明训练恢复，也不要改写历史 manifest。

## 1. 冻结全部启动成员

主控完成资源准入后，用现有 `launch_training.py` 为每个成员生成独立 `attempt.json`、日志与 `exit.json`。所有初始 manifest 出现后，保存以下私有 `group.json`。哈希取 **attempt.json 原始字节 SHA256**，不是重新序列化后的对象指纹。

```json
{
  "schema_version": 1,
  "task": "training-task",
  "context": "CURRENT_CONTEXT",
  "context_epoch": 0,
  "group_attempt": "distributed-attempt-001",
  "progress_member": "node1",
  "start_step": 0,
  "expected_final_step": 100,
  "members": [
    {"id": "node0", "node": "compute-a", "manifest_sha256": "EXACT_FIRST_MANIFEST_SHA256"},
    {"id": "node1", "node": "compute-b", "manifest_sha256": "EXACT_SECOND_MANIFEST_SHA256"}
  ],
  "policy": {"heartbeat_max_age_seconds": 120, "clock_skew_seconds": 30}
}
```

成员全部必需，不能因为连接失败而删掉一个；一个节点一个唯一 manifest。`start_step` 是恢复起点，`expected_final_step` 是绝对目标步数，不是额外步数。换 context、epoch、group attempt、成员集合或 manifest 时保留旧契约，使用新的状态目录。A→B→A 也必须体现新 epoch。

主控还须关联已冻结的 CommandGroup、源码/配置/数据快照和各节点启动命令。manifest/退出回执证明指定 wrapper 的运行事实，本身不能证明它执行的是正确模型、并行拓扑或相同训练配方；这些启动前契约沿用现有准入与代码快照验证，不能因本工具返回 completed 而省略。

若某成员启动前失败而没有 manifest，保持组级启动缺口并检查 CommandGroup 的各成员回执。不能制造 manifest 或缩减 members 来使该组通过。现有 CommandGroup 的 unknown/部分超时仍须逐成员核销；本工具不会代为释放租约。

## 2. 在各成员原 namespace 采集

每个节点的原训练容器中运行对应命令；原生部署则在相同 Linux PID namespace 运行。collector 会核对自身的 boot_id/PID namespace 与 manifest，而不是在主节点读取共享日志便假定其他节点存活。

```bash
python scripts/observe_distributed_training.py member \
  --group /private/observation/group.json --member node1 \
  --manifest /private/attempt-node1/attempt.json \
  --exit-receipt /private/attempt-node1/exit.json \
  --state-dir /private/observation/attempt-001/node1-state \
  --output /private/observation/attempt-001/node1.json \
  --iterations 120 --interval-seconds 30
```

`exit.json` 尚未出现是正常运行状态；进程消失且没有有效退出证明则是 attention。非进度源 rank 不需要伪造 iteration，也不会因为不输出进度而被套用稳态 stall 阈值。所有成员的异常、nonfinite、step 回退、日志替换和退出问题都会保留。

每次最多解析 16 MiB 新日志，超长记录或未消费 backlog 不当作已审完。退出验证要求真实 receipt 的 context/attempt/process/时间和完整日志长度/SHA256 相符；无源时钟的最终 iteration 必须能定位到封存中的原始字节。第一次封存验证可能读取整份日志；相同 receipt 和文件元数据后续可复用验证缓存。保留原始日志及退出回执，元数据缓存不是防止恶意篡改的安全边界。

状态目录含单写锁、持续游标和不可变 `observations/` 快照；`--output` 是在同一锁内原子替换的最新副本。重复启动不能删锁绕过，输出/状态路径应归此 collector 独占，不能指向训练日志或其他成员的目录。重启复用该目录，继续序号和哈希链；新 attempt/epoch 另建目录。

## 3. 聚合所有成员

主控可把成员快照复制到本地再聚合，也可在明确配置的独立 CPU 观察节点读取共享文件。聚合器不拿远端 PID 去查本机 `/proc`。

```bash
python scripts/observe_distributed_training.py aggregate \
  --group /private/observation/group.json \
  --member-file node0=/private/observation/attempt-001/node0.json \
  --member-file node1=/private/observation/attempt-001/node1.json \
  --state-dir /private/observation/attempt-001/group-state \
  --output /private/observation/attempt-001/group-status.json \
  --iterations 120 --interval-seconds 30
```

API 为 `collect_member(group, member_id, manifest_path, state_dir, exit_path=..., output_path=...)` 与 `aggregate_members(group, {member_id: snapshot}, state_dir, output_path=...)`。API 的 `now/process_status/collector_identity` 仅供受审的现场适配器或 CPU 测试注入，不能据此制造真实运行证据。

| 输出 | 含义 |
| --- | --- |
| `status=observing` | 所有必需成员当前观测无已知错误，但还未满足全组结束；不是训练总体 PASS |
| `status=attention` | 缺失、过期、错身份、回退、异常、未封存、非零退出或最终步数缺口；查看逐成员 `issues` |
| `status=completed` / `completion_verified=true` | 此次检查全部成员真实 exit0、日志封存已核验，且指定进度源达到最终步数 |
| `all_members_observed_healthy` | 仅表示该有限观测范围未发现问题；仍须结合 进度源 watcher、设备/网络检查和独立 sentinel |

每个结果保留 group 指纹、context/epoch、成员快照哈希、采样/检查时间与输出范围。不能把 CLI exit0 当作模型完成：正常 observing 也返回0；attention 返回2。JSON 源无效、manifest 漂移或状态目录冲突会退出2。失效结果不能被指定来源的训练进度掩盖。

同序号重复输入可重试但不会刷新采样时间；旧序号、同序号不同内容、时间回退及相邻哈希链断开会保留异常。聚合轮询可以跳过若干成员序号，不能据此假定所有中间记录都已导入。member 发现的 fatal/非零退出保留为本组粘性失败，避免后续正常快照掩盖它；恢复须新 attempt，不能清掉 DB/JSON 假装故障没发生。

终态快照同样检查新鲜度。结束前收齐每个节点的最终观测，再保存聚合的不可变报告；该报告证明 `checked_at` 时刻的完成事实。若很久以后重新评估旧快照会报过期，不能把这个新检查当作当前节点健康证明，也无需持续改写已经封存的历史报告。

## 持续运行、交接与故障边界

- 默认仅采一次；`--iterations` 明确有界（1..2880），间隔1..300秒。部署方负责启动、监督和续接 collector/aggregator，本工具不偷偷创建后台服务。没有远端监管时，SSH/本机退出也可能中断采集，不能承诺离线持续监测。
- 所有节点和聚合器需有可信时钟；允许的少量正向偏差通过 `clock_skew_seconds` 明示，超差或时钟倒退保留 attention。此机制没有测量或校准跨节点时钟。
- 文件读取可能因共享存储故障阻塞。有界轮询次数**不等于**文件系统调用硬超时；部署应给采集进程设置独立超时/监管，并让不同故障域的 sentinel 用既有有界 reader 检查 collector 和 group 输出的新鲜度。只读到同一个 CFS 不能覆盖 CFS/节点共同失效。
- 原 进度源 watcher 继续负责训练进展。更换上下文按 `docs/training-observation.md` 准备独立 context+epoch Store，重新绑定其 sentinel 身份。成员 collector/聚合器各自用新契约和目录，独立 sentinel 也必须跟进新的 peer/输出，不能继承旧 Store 的增量游标。
- 本工具写私有快照，不直接向 TrainFlow Store 注入事件。主控可将原始快照与聚合报告 `artifact-add` 后纳入阶段报告；若转成事件，每个 group/member/状态空间使用独立 peer 和原始来源哈希，不能混用 进度源 watcher 的 `last_seq`。
- 原始日志、回执、观测历史和 SQLite/JSON 状态都不是可自动删除的再生缓存。整个机制不修改训练参数、不发信号、不隔离节点，不与 ClusterManager 等既有恢复负责人争夺操作权。

CPU 反例测试覆盖空/缺失/陈旧成员、PID/namespace 混用、部分失败、无最终步数、nonfinite、日志/回执变化、时间与序号回退等。真实 SSH+Docker、多节点训练和独立观察故障演练须在实际环境另行验收，合成测试不等于该现场已经接通。
