# 离线训练图表

`scripts/render_training_dashboard.py` 将已有 `training_logs` 规范化日志生成一个运行 attempt 的静态 SVG / HTML 看板。用于查看进度和已报告指标，不启动训练、不改变容错规则，也不根据曲线判定质量、性能或恢复通过。无需绘图库、浏览器服务或联网资源。

## 与 Store 的 monitor-report 的区别

| 工具 | 输入与用途 | 来源核验与范围 |
|---|---|---|
| `python -m hcu_trainflow --workspace /private/store monitor-report TASK /private/report.html` | 已登记在 TrainFlow Store 的 observation / incident 事件；查看任务历史、事件、告警和观察指标 | 保留所选事件及数据 sidecar 哈希；不同 attempt/context 分线，不合成一条训练曲线 |
| `scripts/render_training_dashboard.py` | 已收集的 `normalized.jsonl` 文件；无需 Store，制作单 attempt 的离线证据快照 | 固定 NDJSON 原字节与哈希，可进一步核验对应 raw log 的字节范围；混合流必须显式选择 attempt+context |

已有任务事件历史优先用 `monitor-report`；拿到独立规范化日志文件，或需要核对 raw log 字节与归档单次实验时用本工具。两者都只呈现观察证据，不据图形作质量、性能或容错通过判断。本工具没有新增 Store 事件、修改 Store 或接管其告警逻辑。

## 使用

先运行原有训练观察器，或把其 `normalized.jsonl` 与需要核对的原始训练日志收集到私有 workspace。输出目录必须新建或为空，以保留旧里程碑。

```bash
python scripts/render_training_dashboard.py /private/normalized.jsonl \
  --output-dir /private/reports/attempt-01 \
  --measurement-mode functional
```

打开输出目录的 `index.html`。图包括报告的 loss、每步耗时、已有的各 rank 内存指标；缺失项显示缺口，不能补零。`dashboard.json` 保存可复用的指标与来源，`normalized.snapshot.jsonl` 保留读取到的原字节。

### 轮转日志包含多个 attempt

默认拒绝混合 context、attempt 或进程身份。确实需要从一个轮转流中选择某次运行时，必须同时指定身份：

```bash
python scripts/render_training_dashboard.py /private/normalized.jsonl \
  --attempt-id attempt-01 --context CONTEXT_HASH \
  --output-dir /private/reports/attempt-01 \
  --measurement-mode performance \
  --raw-log /private/attempt-01/training.log
```

其他身份的记录只计入排除清单，不参与图表。原始规范化快照仍保留完整输入；其中可能含其他私有 attempt，不能直接发布到公开仓库。重复或倒退的 iteration step、同一所选 attempt 的进程身份变化仍拒绝，以免把多个 rank 或重启过程拼接成一条曲线。

`--raw-log` 可选：提供时核对所选记录中每条 `source.offset / bytes / sha256` 对应的原始字节，并保存 `raw.snapshot.log`。文件本地路径可与远程原路径不同。未提供时，规范化输入本身的哈希会验证和保存，原始训练行哈希仅保留为未独立核实的引用；图中不会声称原件已经验证。

### 测量口径与吞吐

`--measurement-mode` 可选值为 `unspecified`、`performance`、`profile`、`stage-quality-audit`、`functional`、`monitor-drill`。这是调用者声明，绘图器不会据此认证运行模式。所有已报告 step 都绘制，**不自动删除冷编译、热身、慢步，也不计算平均性能或 A/B 收益**。正式性能比较应使用另外固定并验证的实验窗口与条件。

当前适配器没有通用的吞吐派生规则。只有 `iteration.metrics` 中确实存在数值字段，并且知道其单位时才加入吞吐图：

```bash
python scripts/render_training_dashboard.py /private/normalized.jsonl \
  --output-dir /private/reports/with-throughput \
  --throughput-metric "tokens per second" --throughput-unit "tokens/s"
```

字段不存在时该位置保留 missing；不能由 GBS、序列长度或一条旧状态推算实际有效 token 吞吐。

## 读取与异常处理

- 只从 `observation_kind=iteration` 的该次 `metrics` 读取 loss 与耗时。heartbeat 中的 loss、`step_seconds_reported` 等可能是上次状态，不能当成新测量。即使新 iteration 缺字段，也不能用旧状态补齐。
- `memory_by_rank` 是累计快照。仅在 memory 事件内选取真正改变的 rank 快照，不重复画 heartbeat 或其他 rank 的旧值。只有一个 rank 时，新的 memory 事件即使值相同也保留测点；多个 rank 的所有快照都相同、无法判断本次来自哪个 rank 时，列出歧义记录，不编造 rank。横轴为规范化记录序号，另存当时已观测的训练 step；不把采集时间伪装成设备事件时间。
- 内存规范化单位已是 bytes，图中显示 GiB。allocator allocated/reserved/peak 和已明确报告的整卡用量分别命名；allocator 不能代表整卡安全余量，缺失 rank 不补零。
- 数值零是有效值；missing、字符串 `nan/inf`、非数值和无效耗时形成断线并记录原因。完整坏 JSON 行、非法 UTF-8、非标准 JSON `NaN/Infinity` 一律报错。原始字节保持不变，观察器已有的 warning/fatal 也显示在页面。
- 极大或极小的有限数值先按量级归一化，再计算轴范围和留白，防止例如 `+1e308 - (-1e308)` 溢出；轴标明 `tick × scale`。图表数据与原始字节仍保留原值，不把极值剪裁为普通值，也不把它转成缺失。
- 输入最多 256 MiB。打开文件后按初始大小读取，并在同一句柄上重新核对该前缀。读取期间追加的内容不进入本次快照；记录追加/路径替换状态。截断或前缀变化报错。这个有限快照检查不替代文件锁，建议对已收集或已封存文件生成正式报告。
- 最后一行没有换行时默认拒绝，即使它看起来是完整 JSON。对正在追加的流，可显式给 `--allow-partial-final-line`：仅排除这一未终止尾行，并记录其长度/哈希、保留全部原字节；不会静默跳过其他坏行。

## 输出与边界

| 文件 | 内容 |
|---|---|
| `index.html` | 无脚本、无外部资源的入口；身份、模式、缺口、原观察告警与各图 |
| `loss.svg` | iteration 内实际报告的 loss 系列；保留原始 loss 类型 |
| `step-time.svg` | 所有报告的 step 时长，单位秒；不作性能门槛 |
| `memory.svg` | 实际报告的 rank 内存快照，GiB |
| `throughput.svg` | 仅显式选择字段/单位时生成 |
| `dashboard.json` | 原件与快照哈希、身份筛选统计、绘图点、缺失原因、来源引用与限制 |
| `normalized.snapshot.jsonl` | 有限读取快照，包含被显式排除的尾行和其他 attempt 原字节 |
| `raw.snapshot.log` | 仅提供 `--raw-log` 时生成 |

HTML 和 SVG 对所有来自日志的文字转义；没有图表点击执行命令等功能。绘图不能代替并行域覆盖、loss 控制变量复核、profiler 关键路径分析或容错恢复验收。真实记录保留在私有目录，公开测试仅使用合成数据。
