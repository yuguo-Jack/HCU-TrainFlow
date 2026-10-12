# 工作区容量、临时产物清理与观察器上下文换代

先确认[工作空间与写入边界](workspace-boundaries.md)中的真实根及映射。写入范围不等于删除范围：本页登记、保护和核销规则继续生效。不能为省空间清空共享数据、其他任务、全局 Docker/包缓存；不要沿链接或把共享挂载父目录登记成任务清理根。

清理接在实验批次收尾、阶段交接、恢复核销和任务结束处。长时间停留在同一阶段时，默认每 **6 小时**才允许扫描一次；与五分钟人类交互轮询分开。维护默认 dry-run；部署中明确启用的自动清理策略可执行已登记且满足条件的项目，无需逐个重新询问。

## 清理范围与生命周期

```text
PRIVATE_WORKSPACE/
├── cache/recreatable/FAMILY/GENERATION/  # 可重建缓存：至少保留最近3代，默认7天未使用
├── scratch/disposable/FAMILY/GENERATION/ # 临时产物：显式退役、默认静置1小时
└── .maintenance/
    ├── cache-registry.json              # 两类登记、生命周期、使用 pin、删除历史
    ├── tick-state.json                  # 最近扫描时间、触发原因、未完成状态
    ├── plans/PLAN_HASH.json             # 候选、保留理由及身份快照
    ├── receipts/PLAN_HASH.json          # 实际删除或隔离回执
    └── quarantine/                     # 中断后的隔离内容，禁止整目录清空
```

`FAMILY/GENERATION` 使用明确且唯一的目录标识；一个 generation 对应一个独立、可整体处置的产物。文件也放在自己的 generation 目录中，不把整个实验目录登记为可删除。未登记的旧目录不自动进入删除计划；不依据名称包含 `tmp`、`failed`、`core` 或年龄推断可丢弃。

| 类型 | 如何进入回收候选 | 继续保护什么 |
|---|---|---|
| 可重建缓存 | 登记固定来源/重建方法；最近3代之外且超过使用/修改保留期 | 使用 pin、源码引用、当前及近期缓存 |
| `temporary-checkpoint` | 已确认失败、无效或明确废弃的**临时保存点**；写者及异步上传已结束，没有恢复消费者，保留失败/废弃依据后显式退役 | 正在写入、最新有效、最佳、基线、回退/恢复所需保存点及其分片；不能只看某个 rank 结束或保存目录名字 |
| `debug-output` | 已结束调试的 core dump、张量/内存转储等；必要原始证据与定位结论已留存 | 未定位故障唯一原件、仍在分析的 dump、未回传结果 |
| `profiler-intermediate` | 已保留原 trace、采集配置和报告，重复解析/解压的中间副本不再使用 | 原 trace、shape/计时证据、待分析采集 |
| `temporary-output` | 已核销实验的无用临时输出，责任人明确说明处置依据 | 源码/未提交改动、原始材料、正式模型权重、日志、Store objects/snapshots/数据库 |

临时产物有 `active → retired → removed` 生命周期。登记即自动设置生产者 pin；仅释放 pin **不等于**退役。由登记 owner 确认写者停止、其他消费者均已释放 pin，先把不超过1 MiB的处置记录保存为 Store artifact（引用已保留的必要原始证据），再 `retire`。该命令不会探测/终止进程，也不会判断任意文字说明是否足以证明废弃；这些判断由阶段责任 Agent 根据作业、消费者和数据用途完成。关键原件不能以一份摘要替代。

生产者从创建时就选好上述目录；有价值的产物继续保留并设置用途明确的 pin；确需独立归档时先保存并验证正式副本及引用，再决定是否退役旧副本，不直接搬走仍登记使用的目录。旧产物需要纳管时，先确认所有者、根目录边界、依赖和停止状态；不要为满足路径格式自动搬动正在使用的目录。普通 checkpoint 目录不由本工具滚动删除，正式保存点保留策略继续由训练引擎/站点负责。临时保存点例外仅放开 checkpoint 文件后缀和目录名，数据库、证据、Git、链接等保护仍然生效。

## 命令与生产者责任

使用当前 checkout 的脚本，路径替换为任务真实值。策略选项放在子命令之前。

```bash
# 可重建缓存：使用前 pin，操作核销后由各自 owner 释放。
python scripts/maintain_workspace.py --workspace /private/task \
  register cache/recreatable/compiler-build/build-001 \
  --rebuild 'Rebuild from retained source revision and recorded compiler'
python scripts/maintain_workspace.py --workspace /private/task \
  pin cache/recreatable/compiler-build/build-001 --owner compiler
python scripts/maintain_workspace.py --workspace /private/task \
  pin cache/recreatable/compiler-build/build-001 --owner compiler --release

# 已创建的独立临时输出目录，在生产前登记；owner 自动持有 pin。
python scripts/maintain_workspace.py --workspace /private/task \
  register-temporary scratch/disposable/save/attempt-001 \
  --kind temporary-checkpoint --owner checkpoint-writer

# 写者、消费者和异步任务均核销；保存失败/废弃依据、保留点和必要原件的位置。
# 此处保存的是小型处置记录，不是把数十 GB checkpoint 复制进 objects。
hcu-trainflow --workspace /private/task artifact-add /private/task/retirement-record.md
python scripts/maintain_workspace.py --workspace /private/task \
  retire scratch/disposable/save/attempt-001 --owner checkpoint-writer \
  --reason 'Incomplete save; writer exited, no recovery references; evidence retained' \
  --evidence RETAINED_ARTIFACT_SHA256 --producer-stopped

# 其他消费者使用同一 pin API；即使已退役，新 pin 仍阻止删除。
python scripts/maintain_workspace.py --workspace /private/task \
  pin scratch/disposable/save/attempt-001 --owner diagnostic-reader

# 显式人工/Agent 检查不受自动 tick 的冷却时间限制；plan 不删除。
python scripts/maintain_workspace.py --workspace /private/task plan
python scripts/maintain_workspace.py --workspace /private/task \
  apply PLAN_SHA256 --enable-delete
```

默认缓存保留最近3代且至少7天未使用，`--keep-last` 只能设为3或更多；缓存 `--min-age-days` 可调整但不得短于1小时。临时产物不套用“3代”，仅明确退役者可清理；`--temporary-min-age-hours` 默认1；任务收尾已确认全部写者/消费者终结且必要证据已留存时，可在部署策略中明确设0立即处理，不绕过退役、pin、作业和身份检查。年龄取登记/使用/退役时间与树中最新修改时间的最大值；时钟回退拒绝，未来时间继续保留。退役后文件变化会标记 `changed-after-retirement`，不会因再等一段时间自动变成可删除；由原 owner 重新核对写者、用途和证据，再显式 retire；程序保留前次退役记录并重算宽限期。根目录身份变化则停止核销，不自动覆盖登记。

所有消费者，包括其他 Agent、进程、节点和 Store，都要在访问前 pin，并在核销后由原 owner 释放。保留点、基线、最好候选、未结故障设置用途明确的长期 pin，不能靠心跳过期自动解除。普通源码 checkout、关键证据和数据库放在清理根之外。

## 触发时机与空间压力

| 时机 | 动作 |
|---|---|
| 一批实验/调参结束、阶段交接、故障恢复全部核销、任务收尾 | 阶段 Agent 标明本批废弃产物；主控调用对应 `--trigger` 的 tick。不是每个 step、kernel 或 Agent 消息触发 |
| 同阶段长时间运行 | 已部署调用者按6小时或更长周期调用 periodic tick；无需新增常驻服务 |
| 大 checkpoint、core dump、profile/回放采集、构建/同步前 | 只做 `capacity` 与站点配额检查，核对预计新增字节数和余量；不递归扫盘 |
| 低空间 | 在保护规则内尝试提前回收；仍不足时暂停**新的大写入**并报告保留项/空间缺口，不擅自删除恢复点或终止训练 |

```bash
# 实验批次收尾；默认只生成计划，部署启用后加 --enable-delete。
python scripts/maintain_workspace.py --workspace /private/task \
  tick --trigger experiment-batch --enable-delete

# 同阶段长时间运行，默认6小时扫描间隔；配置为更长也可以。
python scripts/maintain_workspace.py --workspace /private/task \
  tick --trigger periodic --scan-interval-hours 6 --enable-delete

# 无文件树扫描；默认低于20 GiB或文件系统10%剩余时报告 low-space。
# 按任务保存规模、站点配额和共享盘大小设置阈值，不能把默认值当充足证明。
python scripts/maintain_workspace.py --workspace /private/task \
  --min-free-gib 100 --min-free-percent 5 capacity
```

trigger 还有 `stage-transition`、`recovery-reconciled`、`task-close`、`space-pressure`。`tick-state.json` 持久保存上次扫描；periodic 默认6小时，阶段/空间触发也至少间隔1小时，防止密集实验或空间告警重复扫盘。`not-due` 只查容量、不遍历产物、不生成新计划。退役宽限期使本轮新废弃的大文件可能留到下一次合格时机。手动 `plan/apply` 可以在明确需要时重新检查；收尾策略如需零宽限，使用 `--temporary-min-age-hours 0`，其余保护与核销条件不变。

CLI 退出码：0 表示命令正常结束（也可能是 dry-run/not-due 或全部保留），1 是错误/需要核销，2 是容量检查仍低于阈值。`--iterations` 的兼容有界轮询不会绕过扫描冷却，不建议用高频轮询替代阶段触发。发生部分失败/中断后 tick 停止自动重试；先核对计划、原路径、隔离内容和作业，再显式 `--resume-after-review`。该参数只重置本次调度资格，不跳过任何删除保护。

默认扫描预算60秒、上限300秒，最多20000个目录项；超出时停止。缓存拟删除候选维持逐文件内容哈希及10 GiB单树预算。临时产物候选采用**文件身份、大小、mtime/ctime 的元数据快照**，不重读 checkpoint/dump 的全部字节，也没有该10 GiB内容扫描限制；它依赖已停止写者和 pin 协议，不能用于证明数值一致或 checkpoint 完整。已保护条目只检查根身份。扫描时间预算不是文件系统卡死时的强制 I/O 超时，也不是大目录删除的硬超时；避开训练关键 I/O 和性能计时窗口。

回执中的 `remove_bytes` / `removed_logical_bytes` 为文件逻辑大小，不是承诺的磁盘释放量（稀疏、压缩、快照、已打开文件和共享盘其他写者都会影响）。看板 environment/recovery 简要记录触发点、前后实际可用空间、删除逻辑量、保留原因和未完成项，并链接计划/回执；无变化不刷屏。`capacity` 不包含用户/组配额，也不会自动阻断训练提交；主控和现场启动适配器须据退出码与保存估算作决定。

## 本地、远端与共享文件系统

各个**实际写盘根**单独登记容量和维护责任：本地任务空间、远端任务目录、容器写层/节点本地 scratch 可能属于不同磁盘。默认只操作授权任务根；不会清理整机 `/tmp`、Docker 镜像、其他用户目录或整个共享 `/cfs`。尽量把容器大文件显式映射到任务自己的远端目录。需要其他文件系统时先建立独立任务维护根，不能通过软链接跨出去。

同一 CFS 目录在多节点或容器中可见时，只配置一个清理者，在真实挂载侧执行同版本脚本，不对每个挂载别名重复登记/计数；先验证共享盘锁、原子重命名与 SQLite 语义，未验证保持 dry-run。所有消费者共同使用该维护根/pin，不能用一个空白 Store 代替真实作业状态。本地主控离线时，仅已部署的远端调用者会执行低频 tick；本地恢复后先读远端 tick-state/回执再接续，避免重复清理。`flow-watch` 仍只采集交互文件，不会自动运行维护脚本。

活跃/unknown operation 或有效 lease 保守地保护当前 Store 的**全部**缓存/临时产物；即使某个候选已退役，仍等到作业核销和资源释放后才删除。长训中可查容量和登记废弃项，必要清理安排在安全空档；空间不足不能删作业记录来解锁。外部运行者和其他 Store 仍需遵守 pin，本工具不会自动发现全部进程引用。

## 执行一致性与中断

`apply` 重查计划哈希（最长有效1小时）、登记/pin、Store 活动、源码引用、根身份及全部候选；临时产物还验证保留的处置 artifact。执行持维护锁与 Store 写事务；目标先原子移动到私有 quarantine，再复核，最后只删除隔离树。回执按 `rename-intent → quarantined → removed` 保存。链接、junction、跨设备/挂载点、hardlink、特殊文件、身份变化、缺失证据均拒绝；没有扫描的保留项不会临时升级成删除项。

中断时保留 `.maintenance/receipts/PLAN_HASH.json` 和 quarantine。核对真实已删/未删项、原路径是否被重新创建、消费者及原件，再制定范围明确的恢复/清理方案；不能递归清空 quarantine 或自动重试旧计划。最后才重新允许 tick。计划/回执本身体积小，本模块不递归清理这些维护证据。

本工具是合作进程的生命周期管理，不是抵抗恶意目录替换的沙箱；不遵守 pin 的写者须先停止或隔离。不能声称普通跨平台文件 API 消除了所有检查后替换竞态。

## 观察器换 context：保留两层身份边界

日志观察包含两套独立状态：

1. `training-log.sqlite3` 固定 parser 的 context、attempt 与原始字节游标；旧目录遇到新 context 会报 `Observer context changed`。
2. 观察 Store 的 `meta['watch:TASK_ID']` 固定 monitor 的 context、context epoch、归一化日志路径和事件游标；只换 parser 的 state-dir 仍会报 `Watcher context changed`。

这些检查防止把旧模型/源码范围的进展、loss、退出回执混入新范围。不要删除这些字段或原地改写旧数据库。默认 parser state-dir 也保持原样，使 CLI once、daemon 与管理脚本继续使用同一单写锁。

`manage_training_observer.py prepare-context` 可以为新范围准备独立观察 Store：

```bash
python scripts/manage_training_observer.py prepare-context \
  --workspace /private/task/controller-state --task TASK_ID \
  --context-root /private/task/observation-contexts
```

它读取已经注册的当前 TaskSpec/context，输出：

```text
observation-contexts/TASK_ID/CONTEXT_HASH-eSOURCE_CONTEXT_EPOCH/
├── state.sqlite3
├── observer-scope.json
└── training-logs/TASK_ID/   # 第一次观察时建立
```

观察 TaskSpec 移除执行权限，保留 context；辅助命令不启动/停止进程，不运行训练，也不自动修改旧 Store。context epoch 纳入目录和事件 peer 后缀，A→B→A 不会复用最初 A 的游标。已有不明目录、范围标记不符、观察 task 被原地改写、准备期间源 context 变化均拒绝覆盖。

完整换代步骤：

1. 用旧 workspace、旧 manifest、旧 policy 查验旧观察器状态。若仍应停止，仅按原始参数和精确进程身份停止它；不能拿新 manifest 去停止旧进程，也不能因此停止训练。
2. 保留旧数据库、manifest、真实退出回执、日志、观察器生命周期回执和事件导出。旧训练未结束但确需切换观察来源时，先明确唯一观察责任及重叠/缺口，不通过新目录启动重复写者。
3. 在可信源 Store 冻结新 TaskSpec/context，调用 `prepare-context`，检查其 `prepared-only` 输出。这个状态不表示已有观察器健康。
4. 把匹配新 context 的原始 attempt manifest 与 policy 交给新 workspace。先 `observe-training` 或 `observe_training.py --once` 检查，再用 `manage_training_observer.py start`，核对 ready、心跳新鲜度和实际 monitor 状态。
5. 更新独立 sentinel 所监控的 workspace/launch/精确进程身份；旧 launch 的失联告警不会凭新进程存在自动解决。用新 scope 的 status/stop 管理新观察器。
6. 每个新观察 Store 用 helper 返回的 `event_peer_suffix` 组成独立事件 peer，例如 `observer-SCOPE_SHA256`。该后缀覆盖源 Store/task/context/epoch 和目标 Store 身份，不仅使用 context；不同任务或目标根即便 context 相同也不冲突。不同 Store 的 seq 都可能从1开始，不能沿用旧 peer 的 last_seq；主控图表按 context/attempt 过滤，历史继续可追溯。

相同 context 下的普通训练重启仍使用新 attempt ID 和进程身份；不需要为每个 attempt 另建 Store。对照模型、源码、数据或实验范围变更则走上述换代。监控恢复成功只说明观察链条恢复，不代表模型 loss、性能或 checkpoint 已通过验收。

更多日志和进程回执语义见 [训练观察说明](training-observation.md)。

## 安装与 Skill 引用链

统一 Skill 的 `references/maintenance.md` 规定阶段收尾、低频维护与容量预检，三个阶段的 `references/workflow.md` 分别负责产物登记/退役、候选保留和长训交接。五分钟交互轮询不触发目录扫描，没有新增独立 Skill，也不把 `flow-watch` 的文件采集误称为已经运行维护命令。

标准 `setup_trainflow.py` 以 checkout 做 editable 安装，`install_skills.py` 复制 Skill 自带 references；项目 `scripts/`、`docs/` 继续从 `TRAINFLOW_PROJECT` 定位。`retention.py` 是 wheel 中的 Python 模块，但 wheel 不包含整个项目脚本/文档/Wiki。远端只装 wheel 时，另同步同版本 `observe_training.py`、`manage_training_observer.py`，需要维护时同步 `maintain_workspace.py`，核对模块/脚本版本及哈希。本机 Skill 升级不代表远端脚本已更新。

### 不可变证据的并发写入

证据对象按内容哈希保存；并发登记相同内容只复用并核验，不替换已有对象。Windows 使用不覆盖目标的原子重命名，POSIX 的对象目录须支持同目录硬链接。临时读取共享冲突有界重试；损坏哈希、权限或文件系统错误继续返回失败，不退回部分写入或覆盖。重建缓存清理规则不适用于这些原始证据。
