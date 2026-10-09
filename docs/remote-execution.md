# 本地编辑与远程执行

## 私有目录建议

```text
private-workspace/
  sites/                连接及命令卡，不存入 public Git
  development/          实际 fork/分支/worktree，保留用户 patch
  references/           官方和第三方只读源码
  tasks/<task>/         任务状态、objects、runs、events、watch
  transfer/             不可变代码 bundle
```

HCU-Knowledge 的缓存目录不用于开发或 PR。先 fetch 所选真实活跃分支，记录 `git status`、origin/upstream、SHA 与子模块，绝不为更新删除用户改动。

## 快照与同步

```bash
hcu-trainflow --workspace /private/controller source-snapshot /private/development/model train.py src
hcu-trainflow --workspace /private/controller source-bundle SNAPSHOT_SHA /private/transfer/code.zip
scp /private/transfer/code.zip site:/private/transfer/code.zip
```

远端安装本包轻量运行依赖后：

```bash
hcu-trainflow --workspace /private/remote source-receive /private/transfer/code.zip /private/runs/SNAPSHOT_SHA
```

receiver 验证 manifest、文件集、路径、大小和每个 SHA，再建立新目录；不覆盖运行中的目录。bundle 只选源码，模型/数据/凭据不要加入。git HEAD 不能代表有未提交改动的工作树，实际快照以选中文件字节为准。

## 命令卡

`command-plan` 仅生成计划；`command-run task operation card lease` 执行。backend 为 local、ssh、ssh-docker、ssh-slurm 或 k8s。Docker 使用已存在的容器；Slurm 使用现有 allocation；K8s 使用明确 namespace/pod/container。它们是通用传输适配，部署前仍需核对 job、Pod UID、容器镜像和设备绑定。

Conda/裸机可直接给绝对解释器；需要 activation 时仅用已核实的绝对 POSIX 脚本。远端命令在快照目录执行，日志保留私有证据。不要把本地路径当远端路径。

### 跳转节点持有第二跳凭据

先区分两种连接方式。SSH config 的 `ProxyJump` 只转发网络连接，计算节点仍使用本机 SSH 客户端的身份认证。若现场已经配置的是“本机免密到跳转节点、跳转节点免密到计算节点”，命令卡可显式选择 `ssh_jump.mode=exec`：第二个 SSH 客户端实际在跳转节点运行，复用该节点已有凭据。无需复制私钥，也不默认转发 SSH Agent。

```json
{
  "schema_version": 1,
  "backend": "ssh-docker",
  "ssh_target": "compute-alias",
  "ssh_jump": {"mode": "exec", "target": "jump-alias"},
  "container": "task-container",
  "cwd": "/workspace/source-snapshot",
  "activation": "/opt/dtk/env.sh",
  "argv": ["python", "tools/verify_environment.py"],
  "env": {"PYTHONUNBUFFERED": "1"},
  "timeout_seconds": 120,
  "basis": "已核对镜像、挂载、目标容器与脚本快照"
}
```

`ssh_jump` 也适用于 `ssh`、`ssh-slurm`。别名、端口及身份文件由对应机器上的 SSH config 管理；本机的 compute alias 不会自动出现在跳转节点。两跳都使用非交互认证、关闭 Agent forwarding、严格检查已登记主机密钥和 15 秒连接超时。首次主机密钥登记按现场流程验证；命令卡不会自动相信陌生密钥或打开密码提示。SSH/容器操作失败依旧视为远端结果待核销，不自动重发。

现场 SSH config 若将 `UserKnownHostsFile` 指向 `/dev/null`，之前连接成功不代表主机密钥已经保存。可用命令卡顶层 `ssh_known_hosts` 指定最终目标连接的独立文件；`mode=exec` 时该路径位于跳转节点，必须为 POSIX 绝对路径。需要覆盖外层时用 `ssh_jump.known_hosts` 指定本机文件（支持 Windows 绝对路径）。例如：

```json
{
  "ssh_known_hosts": "/shared/task/ssh/known_hosts",
  "ssh_jump": {"mode": "exec", "target": "jump-alias", "known_hosts": "D:/private/task/ssh/known_hosts"}
}
```

这些字段叠加到完整命令卡，不能单独执行。先通过现场信任链核对主机公钥及指纹，再保存公钥记录；单独 `ssh-keyscan` 的结果未经验证不能建立信任。路径选项不改变严格检查策略，不复制私钥，不自动写入其他目录。路径不允许展开 token、换行或 `/dev/null`。复核失败前是否已派发任务；确认未派发并核销后，才能用新的 operation ID 重新尝试。

SSH 目标需要 Bash，Docker/Slurm/K8s 内也使用 Bash。先加载 activation，再进入指定工作目录，最后应用命令卡的显式环境变量并执行参数数组；这避免环境脚本切换目录或覆盖任务变量。参数按每层 shell 单独引用，空字符串、空格、换行、引号和 `$()` 都作为原始参数传递。`argv` 不是供 Agent 拼接任意 shell 的字符串。确实需要管道等逻辑时，把已审核脚本保存在本地、随源码快照同步，再执行该脚本。

## 占用检查与执行准入

设备健康、当前空闲、现场预约是三个不同的条件。健康基准通过不代表可以占卡；零利用率也不代表无人使用。`hcu_trainflow.admission.assess_occupancy` 只评估保留的占用证据，不会连接机器、终止进程、预约硬件或启动训练。

现场 collector 应结合 HCU 管理工具/驱动 sysfs、宿主机 KFD/render 设备持有者、调度器/人工预约记录和容器设备绑定，将原始输出归一化。进程查询权限不足、管理工具看不到宿主进程、只有 Docker 内的局部视图、解析失败或 GPU 与进程的对应关系不明，都应标记覆盖不完整。发现未知 KFD 持有者时不能因为利用率为零忽略它；无法证明其设备范围时，对所有可能受影响的设备保守阻止准入。

契约示例（数值仅表示结构，不能作为真实 HCU 空闲阈值）：

```json
{
  "schema_version": 1,
  "context": "CURRENT_TASK_CONTEXT",
  "devices": [{
    "node": "compute-alias", "device": "0", "identity": "pci:0000:01:00.0",
    "idle_memory_bytes": 0, "memory_tolerance_bytes": 0,
    "max_utilization_pct": 0,
    "basis": "替换成该驱动/设备已核实的空闲显存基线及容差依据"
  }],
  "max_age_seconds": 30, "min_observations": 2,
  "quiet_period_seconds": 10, "max_sample_gap_seconds": 15,
  "shared_resources": []
}
```

每次观察包含 `context`、带时区的 `observed_at` 和 `devices`。设备记录必须含 node/device/identity、`memory_used_bytes`、`utilization_pct`、`pids`、`reservations`、`evidence`（保留原始证据的 SHA256 数组），以及 `coverage: {device: true, processes: true, reservations: true}`。字段缺失不等于零或空列表。驱动常驻显存需按实测空闲基线处理，不能为获得准入任意扩大容差。无调度器的站点也要明确核实人工占用/预约范围；“未查询”不能填写 reservations 覆盖完成。

至少两次观察覆盖安静窗口，全部足够新鲜、间隔受限、设备标识和 context 一致、所有选中设备的 PID/预约为空且显存/利用率符合约定，才返回 `observed-idle`。任一次仍忙返回 `busy`；缺项、过期、重复时间、未来时间或不足观察次数返回 `incomplete`。`observed-idle` 不标记健康通过，也不等于资源已预约。

远端时钟与主控不一致时，可在一次**即时执行**的 collector 请求前后记录主控 UTC 时间及单调时钟耗时，使用 `bound_remote_observation` 保留完整 `collection_window`；不可给缓存或历史样本补上新请求时间。远端原时刻和原始证据保持不变。请求开始只是采样时刻的下界：新鲜度按开始时间保守计算，静默时长按最后请求开始减去最早请求结束计算，最大相邻采样间隔按后一次请求结束减去前一次请求开始计算。重叠、未来或自相矛盾的请求包络不能准入。原有确定在同一时钟上的精确样本按零宽区间处理。旧记录只有保留了原始请求包络才能重新核验这部分结论，不能靠作业退出零反推准入有效。

通信测试还需在契约 `shared_resources` 中声明共享 NIC/通信域。每次观察的同名记录含 `id`、`active`、`coverage_complete` 和 `evidence`。另一张卡上的作业可能占同一 NIC、功耗或链路，不能只隔离 GPU 就并行测通信。

主控保留并验证这些原始证据，在同一现场协调者/调度器下预约资源，启动前立即复查，运行中持续观察干扰；发现他人使用即按已约定策略避让或等待。TrainFlow 的 SQLite lease 只协调遵守协议的客户端，无法阻止其他用户在两次采样之间启动作业。没有现场排他机制时，这一限制要出现在实验记录中，不能宣称取得了真正的硬件锁。

### Linux 宿主只读采集脚本

`scripts/collect_node_occupancy.py` 只依赖 Python 标准库，可以随已审核源码快照复制到工作目录，在 Linux 宿主运行：

```bash
python3 scripts/collect_node_occupancy.py --context CONTEXT_HASH --node COMPUTE_ALIAS --host-scope-confirmed --reservations /private/task/reservations.json
```

脚本读取 DRM sysfs 的显存/利用率、设备 PCI 标识，以及宿主 `/proc/*/fd` 的字符设备号，识别 KFD、render 和 card 的持有者；不调用 Docker、不分配 GPU、不执行性能测试、不改设备设置。`--host-scope-confirmed` 是部署者核实宿主 PID/设备视图后的声明，脚本仍拒绝把非 root、可识别容器、无法读取的进程视图算作完整覆盖。GPU `device` 使用 `cardN`，**不能直接当成 HIP/ROCR 序号**；部署时还要按 PCI/UUID 核实实际可见设备映射。

单个全局 KFD fd 不能证明只占某一张 GPU，因此该 PID 保守地列入所有可能涉及的卡。未映射 render/card 节点的持有者也按同样规则处理；没有精确设备归因时优先选择整个空闲节点，不能猜测空卡。缺失计数器、权限失败、未知进程所有者、空 `/proc` 视图或采集耗时过长都保留为覆盖缺口。

reservations 文件必须明确声明当前 context、node、观察时间、覆盖完整性、依据和证据，按 card 名称列出占用。例如：

```json
{
  "schema_version": 1, "context": "CONTEXT_HASH", "node": "COMPUTE_ALIAS",
  "observed_at": "2026-01-01T00:00:00+00:00", "coverage_complete": true,
  "basis": "替换为当前现场调度器/人工预约核对依据",
  "evidence": ["RETAINED_SHA256"],
  "devices": {"card0": [], "card1": [{"owner": "existing-job"}]}
}
```

示例中的时间、哈希和依据都必须替换。缺少文件、观察过期（默认 30 秒）、设备未列出、无正文依据或未保留证据时，reservation coverage 为 false；脚本不会把无进程推断成无预约。无统一调度器的环境也要由现场协调者记录明确的核对范围与局限。

stdout 为可交给 `assess_occupancy` 的 observation，附带 `raw_evidence: {sha256, utf8}`。主控将 `utf8` 字符串的 UTF-8 **原始字节**登记为 artifact，核对返回哈希与 `sha256` 完全相同，之后才使用 observation。另行采集共享 NIC/通信域数据；当前脚本不会凭零 GPU 利用率生成 NIC 空闲结论。不要把脚本 exit 0 当作准入通过，必须读取各项 coverage 并完成两次观察和现场预约。

## 中断与重试

### 一个多节点作业：显式 CommandGroup

多个节点上的 `torchrun` 需要同时进入 rendezvous。不要用多个虚构的 Agent owner 绕过普通 `command-run` 的并发限制，也不要依次等待每个节点退出。`CommandGroup` 把一项分布式作业登记成一个固定计划、一个 operation 和一个协调 owner，再启动各节点传输进程，最后收集结果。

组卡示例（只是结构示例，目标、GPU 域、网络和 argv 必须现场核实）：

```json
{
  "schema_version": 1,
  "basis": "同一分布式作业；已经核对节点、设备绑定、通信域、快照、前台启动脚本及当前占用",
  "timeout_seconds": 600,
  "shared_resources": ["site-network-domain"],
  "members": [
    {
      "id": "node-rank-0",
      "node": "compute-a",
      "resources": ["compute-a-selected-gpu-domain"],
      "card": {
        "schema_version": 1, "backend": "ssh-docker", "ssh_target": "compute-a",
        "container": "task-container", "cwd": "/private/task/source-snapshot",
        "argv": ["bash", "launch_node.sh", "--node-rank", "0"],
        "timeout_seconds": 600, "basis": "已审核的前台节点 launcher；等待该节点所有训练 rank 结束"
      }
    },
    {
      "id": "node-rank-1",
      "node": "compute-b",
      "resources": ["compute-b-selected-gpu-domain"],
      "card": {
        "schema_version": 1, "backend": "ssh-docker", "ssh_target": "compute-b",
        "container": "task-container", "cwd": "/private/task/source-snapshot",
        "argv": ["bash", "launch_node.sh", "--node-rank", "1"],
        "timeout_seconds": 600, "basis": "相同 rendezvous、world size 与作业身份；明确 node rank"
      }
    }
  ]
}
```

每个成员继续使用原有命令卡和逐层 quoting；SSH jump、Docker、现有 Slurm allocation、K8s 或 local 后端都不另造一套命令解析。每个 member ID、物理 node 域须唯一；同一节点通常由一条前台 launcher 启动它的所有本地 rank。节点私有资源不重叠，共享 NIC/通信域等放入 `shared_resources`；多节点必须声明共享通信资源。字段不是自动硬件发现，命令实际绑定哪些卡仍须按前述准入流程验证。

先按正常流程取得每个节点 GPU 域和共享域的 lease，将返回的 fencing 回执原样放入数组文件 `group-leases.json`。所有 lease 必须属于同一个真实 owner，资源集合与组计划**精确一致**，不能少网络域或随意添加未使用域。若在 assignment 中执行，同一个 assignment 必须已预约整个集合，并传入它的真实 owner/token。

```bash
hcu-trainflow --workspace /private/controller command-group-plan group.json
hcu-trainflow --workspace /private/controller command-group-run TASK_ID GROUP_OPERATION_ID group.json group-leases.json
hcu-trainflow --workspace /private/controller command-group-status GROUP_OPERATION_ID
```

执行前在同一个 SQLite 写事务中核对全部 lease、context epoch、task/assignment 状态、已有未知作业、其他 assignment 预约和预算；任何一项失败都不启动节点。`command-group-run` 可使用 `--assignment ID --owner OWNER --token TOKEN`，但不会为每个节点创建假 Agent 身份。节点传输启动后才进入整体等待，因此不会因等待第一个 torchrun 而阻塞第二个节点启动。

超时分两层：成员命令的 `timeout_seconds` 从该节点启动前开始计时；组的 `timeout_seconds` 从组调度开始计时，不能被逐节点串行等待延长，成员超时不能大于组上限。预算按一个 operation 和组墙钟耗时计算，不按节点数或 lease 数重复累加；未决/核销后的预算至少保留一份组超时预约。

每个 operation 的 `runs/TASK_ID/GROUP_OPERATION_ID/` 保留：

```text
group-plan.json
MEMBER_ID/
  plan.json       # 固定节点命令计划
  state.json      # 启动意图、启动/退出事实、节点耗时和超时类型
  process.json    # 本地 SSH/kubectl/命令子进程 PID，绝非远端训练 PID
  stdout.log
  stderr.log
result.json       # 完整收集后才产生；主控崩溃可能没有
```

部分 Popen 失败后不继续派发尚未启动的节点；已经启动的成员继续在原超时范围内收集。成员到期时仅终止当前主控持有的本地传输子进程，不向任意远端 PID 发信号，不宣称远端 torchrun/rank 已经结束。SSH/K8s/Slurm 非零返回、部分启动、超时或主控中断均使整组 `unknown`，全部节点和共享资源保持未决占用。只有所有成员正常返回零，才记录命令层面的 `complete`；它不证明 loss、性能或 checkpoint 通过。所有命令必须在前台等待真实工作结束，后台提交脚本需要自己的作业终态适配，不能把提交成功当训练结束。

活跃主控持有该 operation 的进程级锁，禁止另一个主控同时执行或提前核销；进程真正崩溃后操作系统释放锁，数据库中的 started 和节点回执仍保留。不要删除锁文件。锁所在文件系统仍需验证跨进程语义；TrainFlow 锁不能替代现场排他调度。

`command-group-status` 对尚未生成完整结果的组保留 unknown，并展示已有节点事实；它不能仅凭本地 PID 或日志文件猜测远端是否仍在工作。先核对每个节点的实际 launcher、所有 rank、容器/Pod/job 身份和输出，收集证据，再统一核销：

```json
{
  "request": "EXACT_GROUP_REQUEST_HASH",
  "context": "ORIGINAL_CONTEXT_HASH",
  "status": "failed",
  "note": "逐节点核对真实终态、残留进程和通信资源，允许结束本组占用",
  "members": [
    {"id": "node-rank-0", "outcome": "failed", "processes_reconciled": true, "evidence": ["RETAINED_SHA256"], "note": "实际节点及 rank 的终态与进程核对依据"},
    {"id": "node-rank-1", "outcome": "not-started", "processes_reconciled": true, "evidence": ["RETAINED_SHA256"], "note": "确认没有成功派发，也没有该次作业遗留进程"}
  ]
}
```

```bash
hcu-trainflow --workspace /private/controller command-group-reconcile GROUP_OPERATION_ID reconciliation.json
```

每个原成员必须出现一次，`outcome` 为 complete/failed/not-started；必须保留逐节点证据并明确核对残留进程和资源，示例里的 true 不能未经核实照抄。全组 complete 只接受全部成员 complete。所有成员通过结构、身份和 artifact 校验后，在一个事务内结束整组未决占用；这仍是基于所提交证据的核销，不是程序自动连接远端完成了核实。旧 `operation-reconcile` 明确拒绝命令组，不能只核销一端就释放另一端和网络域。需要再次运行时使用新的明确 operation ID，并重新检查实际占用与授权。

operation ID 不重复执行已完成请求。超时、SSH 断线或 started 状态残留需核对远端进程、job 和输出，上传证据后 `operation-reconcile`。不能只换一个 operation ID 就重发训练。Python fencing 防止本工作区的过期拥有者发新动作；跨机器的真实运行隔离还依赖站点调度器。

单命令的执行和核销也使用与命令组相同的 operation 进程锁，锁覆盖登记意图、启动子进程、等待和写入终态的整个范围。主控仍活跃时，即便暂时没有发现子进程，也不能提前核销：主控可能正在启动前等待，随后仍会派发。主控退出后锁由操作系统释放；这只允许开始基于证据的核销，不证明远端子进程已经退出。不要删除工作区的 `command-group-locks` 锁文件；历史目录名同时承载单命令与命令组锁，两个 API 不得各自使用不同锁域。

核销未知操作后仍保留其超时预算占用，记为 `budget_seconds`；不会因为缺少本地主控的耗时结果就按零计费。这是保守预算核算，不是伪造的远程实测耗时。任务总预算和 assignment 预算都遵循此规则。资源被领取中的 assignment 整体预约时，无 assignment 身份的主控命令也不能绕过预约。
