# 私有缓存维护与观察器上下文换代

维护默认生成可审阅计划。自动删除仅对已明确登记、可重新生成的缓存开放；任务原始证据、源码工作树、模型权重、checkpoint、对象库和数据库各自保留。

## 可清理的范围

工作流的缓存生产者可以把临时下载包、可重复解压结果或构建缓存写到：

```text
PRIVATE_WORKSPACE/
├── cache/recreatable/FAMILY/GENERATION/   # 显式登记后才受本策略管理
└── .maintenance/
    ├── cache-registry.json               # 登记、重建依据、使用 pin、删除历史
    ├── plans/PLAN_HASH.json              # 只读检查产生的完整计划
    ├── receipts/PLAN_HASH.json           # 实际执行和失败回执
    └── quarantine/                      # 部分失败/中断后的隔离内容
```

`FAMILY` 表示同类缓存，`GENERATION` 使用新的唯一标识。只有这个精确的四层路径格式可登记。不扫描 `research/`、`runtime/`、`checkouts/`、`evidence/` 等目录推测哪些东西“看起来临时”。现有任务不用迁移全部目录；后续缓存生产步骤可以逐步采用这个专用目录。

登记时必须提供重建的源/方法说明。说明仅作为事实记录，不会执行其中的命令。不要把唯一原件、未保存修改的源码、训练日志原件、临时尚未回传的结果或待核销的作业文件登记为缓存。源码快照清单、Git 目录、数据库、checkpoint/常见权重扩展名等有额外拒绝规则，这些规则不能替代登记者确认数据的可重建性。

默认每族保留**最近登记的 3 代**，并至少 7 天未使用/修改才可删除；只能增加保留代数。年龄取登记时间、最近使用时间和树中最新修改时间的最大值。未来时间或时钟回退不会加速淘汰。未登记目录永远不进入计划。

## 安装与命令

使用同版本 TrainFlow 安装包和仓库中的脚本。下面都是通用示例，路径、家族和生成标识应由实际任务配置提供。

```bash
# 登记已有、独立的可重建缓存目录。重建说明应含固定来源或版本。
python scripts/maintain_workspace.py --workspace /private/task \
  register cache/recreatable/compiler-build/build-001 \
  --rebuild 'Rebuild from the retained source snapshot and recorded compiler version'

# 消费者/写者打开缓存前登记 pin；结束且核销后由同一 owner 释放。
python scripts/maintain_workspace.py --workspace /private/task \
  pin cache/recreatable/compiler-build/build-001 --owner compile-worker
python scripts/maintain_workspace.py --workspace /private/task \
  pin cache/recreatable/compiler-build/build-001 --owner compile-worker --release

# 默认 dry-run。策略参数放在子命令之前。
python scripts/maintain_workspace.py --workspace /private/task plan
python scripts/maintain_workspace.py --workspace /private/task \
  --keep-last 4 --min-age-days 14 plan

# 查看计划后显式允许执行；用上一条输出的真实哈希替换。
python scripts/maintain_workspace.py --workspace /private/task \
  apply PLAN_SHA256 --enable-delete
```

`plan` 输出计划路径、拟回收字节数、每一代的处理决定和保留理由；完整文件包含登记快照、目录根身份及拟删除树的逐文件 SHA-256/修改时间。已经因最近3代、pin、年龄或运行状态需要保留的条目只做廉价身份检查，标明 `tree=null`，不会每五分钟重读其全部内容。后续真正符合淘汰条件时才重新深扫。未加 `--enable-delete` 的 apply 会拒绝。计划最多有效一小时，过期重新检查。注册重复路径不会悄悄覆盖历史；重新生成使用新的 generation 名称。

Python API 可复用 `register_cache`、`pin_cache`、`plan_retention`、`apply_retention`。所有缓存使用者必须参与 pin 约定，包括自主 Agent 以及单独运行的缓存生产工具；无法确认外部使用者时保留 pin，不启用删除。

## 定期维护入口

以下命令可由已有工作流轮询或现场调度机制调用，不额外安装常驻服务：

```bash
# 默认仅检查一次；每5分钟触发它即可。
python scripts/maintain_workspace.py --workspace /private/task tick

# 一个有界会话内最多12轮，每轮间隔300秒。
python scripts/maintain_workspace.py --workspace /private/task \
  tick --iterations 12 --interval-seconds 300

# 只有部署时明确启用，才会对本轮检查后仍合格的缓存执行删除。
python scripts/maintain_workspace.py --workspace /private/task \
  tick --enable-delete
```

默认扫描预算 60 秒，可设置 `--max-scan-seconds`，上限 300 秒；单棵树另有限制，超过预算会停止本轮。计时预算用于限制扫描工作，不能把它当成底层文件系统故障时的强制 I/O 超时。计划/回执仍可能占少量空间；当前没有递归清理这些维护证据。

任何未完成/未知操作、未到期资源 lease 都保护整个工作空间的缓存。这刻意比按路径猜测作业依赖更保守。远程 SSH 超时后即便 lease 过期，只要 operation 仍 unknown，仍不能清理。正常任务中可以周期检查，等作业核销且资源释放后再执行合格计划。该检查只覆盖当前 Store 已知状态；外部进程、其他 Store 和远端使用者仍必须登记使用 pin，不能仅凭一个 Store 没有活跃行推断所有消费者都已停止。

## 执行一致性与中断

执行时取得维护独占锁，再持有 Store 的写事务检查操作/lease；期间新的 TrainFlow 命令意图与 lease 不能插入。随后复核计划哈希、登记内容、pin、当前 TaskSpec 的源码路径引用、所有代次的根身份，以及**全部拟删除条目的树内容**。拟删除条目的缺失、变更、链接、junction、挂载点、hardlink、特殊文件或预算超限都会拒绝继续。没有深扫的保留项不会在 apply 中临时升级为删除项；旧版计划结构须重新生成。

合格目标先原子重命名到私有隔离目录，再次复核其完整内容，最后只删除该明确隔离树。回执在重命名前写入，逐项记录 `rename-intent → quarantined → removed`。原始证据不会因为脚本退出码为零就自动获得其他任务的验收状态。

如果删除中断、文件仍被占用、内容发生变化或磁盘故障：

1. 读取 `.maintenance/receipts/PLAN_HASH.json`，区分已删除项和仍隔离项。
2. 保留隔离内容、登记表和计划。不要自动重新执行旧计划，也不要递归删除整个 quarantine。
3. 核对原路径是否被重新建立、是否还有消费者、所需原件与重建依据是否完整。
4. 明确恢复或再次清理方案后，再由人工或 Agent 进行范围明确的维护。当前模块故意不自动猜测部分失败应恢复哪一代。

这是配合 pin 与工作流锁使用的维护工具，不是隔离恶意本机进程的安全沙箱。检查会拒绝已发现的并发修改；不遵守 pin、持续篡改目录结构的外部写者必须先停止或隔离。不能在这种目录上声称普通跨平台文件 API 消除了所有检查后替换竞态。共享文件系统也必须先验证锁、重命名和 SQLite 语义；验证前保持 dry-run。

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

统一 Skill 的 `references/maintenance.md` 在既有五分钟交互循环触发维护，adapt/optimize/fault-tolerance 的 `references/workflow.md` 分别规定缓存生产、候选保留和长训交接责任。没有新增独立 Skill，也不把 `flow-watch` 的文件采集误称为已经运行维护命令。

标准 `setup_trainflow.py` 以 checkout 做 editable 安装，`install_skills.py` 复制 Skill 自带 references；项目 `scripts/`、`docs/` 继续从 `TRAINFLOW_PROJECT` 定位。`retention.py` 是 wheel 中的 Python 模块，但 wheel 不包含整个项目脚本/文档/Wiki。远端只装 wheel 时，另同步同版本 `observe_training.py`、`manage_training_observer.py`，需要维护时同步 `maintain_workspace.py`，核对模块/脚本版本及哈希。本机 Skill 升级不代表远端脚本已更新。

### 不可变证据的并发写入

证据对象按内容哈希保存；并发登记相同内容只复用并核验，不替换已有对象。Windows 使用不覆盖目标的原子重命名，POSIX 的对象目录须支持同目录硬链接。临时读取共享冲突有界重试；损坏哈希、权限或文件系统错误继续返回失败，不退回部分写入或覆盖。重建缓存清理规则不适用于这些原始证据。
