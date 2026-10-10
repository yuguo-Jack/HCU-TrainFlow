# 训练状态、保存与续训验证

适配新引擎、修改优化器/权重缓存、改变分片，或准备长训恢复时阅读本页。保存成功、加载成功和恢复后训练等价是三个独立结论。原始证据与具体模型补丁放私有工作区。

## 从局部验证到完整训练

1. 固定模型、数据/tokenizer、软件二进制、源码快照、并行布局及随机种子。区分模型初始化、首次编译、实际 iteration、验证集计算和 checkpoint 写盘；不同阶段使用匹配的超时。
2. 先验证受影响的输出、输入梯度、参数梯度及参数更新。优化器按实际实现核对 step、moment、weight decay、clip、None/zero gradient 和溢出行为。多个参数组执行到一半失败可能已部分更新，不能在这个状态上直接重试；使用重新初始化或已验证 checkpoint。
3. 随机输入只验运行链路。真实文本需固定 tokenizer 文件及特殊 token，核对本机预处理与实际训练镜像的 token ID 一致，保存独立训练/验证 split、索引内容哈希和读回结果。禁止因 tokenizer 软件版本不同而静默重新编码。
4. 资格审计可能逐参数同步或保留大量中间状态。审计通过后关闭这些额外负载，单独测 profiler-off 性能；受审计拖慢的步长不作为优化基线。

## 优化里程碑的阶段 A/B loss

局部正确性每轮做，较长 loss 在稳定里程碑做。阶段对照应从同一份已验证的初始状态分别启动基线与候选，不是在两个连续的训练区间比较 loss：

1. 保存初始模型、优化器各参数组与状态、scheduler、RNG、数据游标/consumed samples 的身份。可使用同一个不可变 checkpoint；从随机初始化开始时须核验实际初始张量/状态，只有相同 seed 不足以保证不同实现消费随机数的顺序一致。
2. 固定实际 token/样本次序、tokenizer、mask/packing、有效 batch、精度、clip/weight decay 和完整调度 horizon。保存输入指纹；重新跑时不能悄悄重编码、改变数据游标或沿用上次候选已更新的参数。
3. 先按基线重复运行的自身差异、算法和任务要求确定窗口/容差，再开始候选对照。不能看到候选差异后放宽门槛。非确定性或布局变化无法建立逐 step 等价时，预先设计相应验证，保留不确定性；短窗口误差小不等于统计非劣或长期收敛。
4. 新任务的 QualityContract 除 samples/aggregation 之外，写入 `initial_state_fingerprint` 和 `training_recipe_fingerprint`，分别引用上述状态清单和可比配方的内容指纹；两组记录必须重复相同值。候选的实现快照仍各自保存，不能把实现差异混入要求相同的配方指纹。`quality-check` 会比较已声明身份，但不会自动读取 checkpoint 来鉴定作者是否写对；负责 Agent 与独立 reviewer 要核对原件。
5. 确认候选实际生效，记录前后向/参数更新、溢出/跳步和有效 token 聚合口径；对齐同一 step 序列。性能另在关闭 profiler 和重型审计后测，不把 loss 审计开销计为性能回退。
6. 报告区分局部数值、阶段窗口、统计结论、完整模型和长训验证。初态/输入缺少可追溯证据时仅记录观察值，不给阶段等价结论。历史契约未声明新增身份字段时程序保留窗口比较能力，但返回 `stage_eligible=false`。正式 `stage-quality` 报告按[质量契约](contracts.md#qualitycontract-与记录)留存 `quality_inputs`，程序重算并绑定候选后才可用于新阶段晋级；不能只把比较结果的 pass 抄进报告。

## 有界续训对照

使用短窗口即可验证恢复机制，无需每次进行长时 loss 验证：

- 连续组从固定初始状态运行到总目标 N，在中间 K 保存。
- 恢复组从连续组同一份 K 的不可变 checkpoint 恢复，目标仍为总步数 N。确认引擎的参数含义是总步数还是新增步数。
- 区分本次停止步数与优化器调度长度。延长 `train_iters` 可能同时改变 LR decay / weight decay 的总长度并在加载时冲突；若目标是原样续训，应采用该版本支持的 checkpoint scheduler 恢复策略，核对恢复的 num_steps、LR/WD 全部参数。不要用跳过优化器/RNG、覆盖断言或重新初始化来换取退出码 0。确需改变调度配方则单独记录并验证，不作为原样恢复。
- 不能修改原运行目录中的 latest 指针。为读取旧迭代建立任务自己的只读选择目录或使用引擎原生迭代选择参数；确保所有分片、metadata 和版本一致。
- 核对加载日志、模型 key 覆盖、优化器/调度器、RNG、数据游标/consumed samples、并行布局以及后续更新。某些实现会在 strict 加载失败后重试非 strict；退出码 0 不能证明没有 missing/unexpected keys。
- 比较 K+1…N 的 loss、grad、学习率、样本数和最终模型/优化器状态。打印的小数相同不代表原始 tensor 相同；需要时按 checkpoint storage chunk 分批在 CPU 比较，避免一次加载整个大模型。
- 固定确定性配置可要求精确相等；存在非确定性 kernel 时，先建立重复运行自身差异，再使用预先声明的容差。不得观察到差异后任意放宽阈值。记录哪些 RNG/调度器/数据状态能直接比较、哪些只有行为证据。

没有覆盖的异步保存、跨拓扑 reshard、故障中断、不同优化器和持久化后端继续列为待验证。短窗口恢复通过不代表长时 loss/收敛验收通过。

## 恢复演练的保存预算与时序

先根据当前保存格式估算**整个 checkpoint** 的模型、优化器 master/moment、RNG/数据状态、分片 padding 和临时文件。分布式优化器减少每卡状态，不代表整个保存点的总磁盘占用按卡数同比减少。核对任务挂载的实际可用空间、用户/组配额及站点限制；`df` 有余量不能代替配额检查。估算与实际 shard 总大小分别记录，保留安全余量，遇到空间不足不跳过 optimizer/RNG 凑恢复成功。

按实际引擎源码核对周期保存、正常退出补存和异步写入完成条件。短演练也可能因小保存间隔产生多代大文件。若只需验证一次恢复，可使用原生的提前退出机制生成一个完整恢复点，保持原训练总目标与调度长度不变；后续恢复仍加载完整状态，在本次演练明确不验证再次保存时关闭新增保存。这个做法只适用于引擎允许将保存与加载独立配置的情况，不能替代生产任务的持续 checkpoint 策略，也不自动删除历史原件。

保存/加载日志和 iteration/loss 可能由不同 rank 输出，分别核实来源。完整校验和计算可能产生大量共享存储读流量，应安排在源保存点已静止且相关 writer 终结后；不要把全量哈希放进短暂的故障注入窗口或正常性能计时中。后续复用校验记录时绑定完整路径、文件集合、内容哈希与不可变/写权限约束；metadata 未变本身不是内容未变的证明。

故障注入、模型启动/编译、checkpoint 写入、无进展检测和恢复完成分别设定有依据的有界时间。受控暂停只作用于已确认身份的任务进程；跨节点恢复前核销所有成员的 wrapper、worker 与退出回执，再重新检查资源并交由同一个容错负责人启动。恢复后需要实际加载来源和连续推进证据；只看到最后一个成功 step 或单节点退出不足以验收。

## Checkpoint 临时目录与进程通信预检

部分 checkpoint writer 会启动 Python `spawn` / `SyncManager`，即使训练采用同步保存，也可能通过 AF_UNIX socket 交换状态。源快照或 attempt 名很长时，直接把同样长的 scratch 路径用作 `TMPDIR`，可能在训练结束后的首次保存才出现 `AF_UNIX path too long`。它限制的是**完整 socket 路径的字节数**，还包括 Python 自动添加的 `pymp-*` / `listener-*` 后缀；仅检查目录存在或能写普通文件不够。

先在真实 Linux 容器或训练环境中，显式准备一个本任务已有授权范围内、由当前 UID 拥有的短临时目录。编译缓存可以继续使用独立的较长目录，不必跟随 IPC 临时目录改名。在训练之前执行 stdlib 检查，示例变量应替换为本任务的真实路径：

```bash
python -B scripts/probe_training_tempdir.py \
  --task-root "$TASK_ROOT" --tempdir "$TASK_ROOT/tmp/$SHORT_RUN_ID" \
  --timeout-seconds 15 > "$TASK_ROOT/evidence/tempdir-probe.json"
```

父目录、临时目录和 evidence 目录应由任务部署步骤预先建立；探针不会自动选择系统 `/tmp`，不会创建缺失的用户路径。目录必须位于 `--task-root` 下，且具有当前所有者的写入/搜索权限。它实际执行 AF_UNIX Listener 双向通信、`spawn` Manager Queue 往返和正常退出，记录实际路径、字节数、子进程身份与清理结果。成功返回0；失败返回2；非 Linux 返回3和 `unsupported`，不能用 Windows 单测代替现场 Linux 验证。

探针固定本次进程的 `tempfile.tempdir`，因此不可写或缺失目录不会触发 Python 默认目录搜索的静默回退。超时只终止本次独立进程组；清理仅移除自己的随机 `pymp-*` 目录及遗留 listener socket，发现身份变化或未知文件则保留并报错。测试期间不应有其他清理者修改该目录。探针不保存模型 checkpoint，也不能代替真实保存/加载验证。

通过后，训练命令应明确使用**同一 Linux 环境和选定目录**的 `TMPDIR`（必要时同时设置 `TEMP`、`TMP`），不要把探针自己的临时 `pymp-*` 子目录作为训练配置。长训期间目录可能被删除、权限或挂载变化，仍须保留真实 writer 的原始日志。训练中出现 `EOFError` 时，向前追溯 Manager 子进程的第一条错误：socket 路径、权限、spawn import、资源耗尽等都可能使父进程只看到 EOF；不要直接按数据损坏或 GPU OOM 处理。

## 保存或优化器阶段的资源错误

报错中的 “GPU out of memory” 或 “probable leak” 是线索，不是根因。先定位实际失败调用及资源域：

| 发生位置 | 要保存的证据 | 验证方式 |
| --- | --- | --- |
| 模型前后向 | allocator allocated/reserved/peak、device 可用量、张量生命周期、rank 差异 | 固定 shape 与并行配置，区分容量、碎片及临时 buffer |
| 原生 multi-tensor 优化器 | tensor 数量、每组列表、dtype、descriptor/元数据池限制、失败前更新范围 | 相同原生算子的有界批次对照；核对 step/scalar 与所有状态，不能静默替换优化器 |
| 混合精度 checkpoint 映射 | 实际 optimizer 参数组顺序、原生 FP32 参数、FP16/BF16 master 参数、分片 key/shape/offset | 按真实参数 ID 核对 moment 与 master 的归属；同形状也可能错配，不能只验 shape。保留形状断言，覆盖混合及单一 dtype、保存/加载和恢复后的下一次更新 |
| GPU→CPU checkpoint staging | CPU RSS/可用内存、锁页限额、进程 VMA 数/上限、pinned tensor 数、逐步分配轨迹 | 用匹配 dtype/layout 的最小复现比较当前搬运路径；保留最后成功样本 |
| checkpoint worker / Manager IPC | 第一条子进程异常、实际 TMPDIR、完整 socket 路径字节数、spawn 启动与退出 | 在相同 Linux 环境先做有界 IPC 预检；父进程 EOFError 可能只是后续症状，禁止默默回退到任务范围外的目录 |
| checkpoint 写盘 | 实际保存格式/分片数、metadata、共享盘延迟、可用容量、结束标记 | 核对全部 rank 完成、回执和实际加载；不能只看到保存开始日志 |

大量很小的张量可能先耗尽描述符或主机映射额度，而非 GPU 容量。失败时错误记录自身也可能无法再分配内存，应提前流式保留关键指标。不要把提高系统限额当作默认修复；先查对应 HCU/上游版本已有实现及同步要求，局部修复需保留原生数值和格式契约。

对 CPU 搬运方式的改变，应检查 dtype、stride、空 tensor、metadata、同步完成和后续 writer/load。只验证同步保存，不得顺带宣布异步/NVRx 等路径可用。补丁进入目标仓之前检查最新上游是否已修复，并附受影响路径的单测、环境、正确性及性能成本。
