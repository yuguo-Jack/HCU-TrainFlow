# TraceLens 的 HCU 分析与验证

本页是性能 Skill 的条件阅读入口。先按 [性能采集](profiling.md) 冻结 trace、训练窗口、rank/并行域、版本和调用契约，再选择工具。使用 `thirdparty/manifest.json` 锁定的 HCU fork；原始 trace、张量、计数器文件留在任务 workspace。

## 选择入口

按当前问题选用表中路径，不将全功能资格测试作为每个模型的必做清单。相同 trace/窗口/工具身份的有效报告直接复用；调用归属不清才补 Graph，模型与独立性能有疑问才回放，需要解释硬件瓶颈才采相应计数器。已有充分分析时无需再启动原生 Agent 重复一遍。原生 Agent 的适用推理/复核可纳入同一候选审查并引用其回执，避免多轮相同内容的独立审核；各自的证据契约仍需通过。

| 问题 | 路径 | 后续动作 |
| --- | --- | --- |
| 时间花在哪里，CPU 怎样启动 kernel？ | `tracelens-report`；完整通信组用 `tracelens-collective` | `profile-analyze` 用显式墙钟窗口核对覆盖，区分空泡、通信、计算、copy 和未归因项 |
| 原 trace 混有启动、预热和多步？ | `split` 模式，显式指定训练步范围 | 核对原生检测的 annotation 和实际截取范围；不套推理稳态规则 |
| 多 rank 时序需要一起查看？ | `merge` 模式，提供实际 rank→文件映射 | 保留独立 trace；合并只用于展示，不自动校时或推导跨机因果 |
| 修改后调用、次数和耗时如何变化？ | `compare` 模式，TraceDiff 加报告表比较 | 对齐比较 context，查看新增/消失/变慢调用，再用 profiler-off 整步验证 |
| Graph replay 看不到原算子和 shape？ | `tracelens-analyze` 的 `graph` 模式 | capture 恢复调用，replay 提供 GPU 时间 |
| 热点距离带宽/算力参考有多远？ | `roofline` 模式与原生性能模型 | 核算实际 shape/dtype/算法；未知高占比项继续建模 |
| 需要原生 Agent 分析方法？ | `agent` 模式准备类别、指标与条件优先级 | 活跃 Agent 读指令、查证、写 findings/analysis，再独立复核 |
| 训练中被拖慢，还是实现本身慢？ | EventReplay 或专用同调用测试 | 对齐输入值、stride、dispatch、状态和计时范围，解释并发干扰 |
| 只有 DTK hipprof JSON / pftrace？ | `hipprof` 模式 | 分析 API、dispatch、copy、memset；缺 ATen shape 时补采，不按名字猜 |
| 需要计数器和指令停顿？ | XProf → XCompute → `counters` 模式 | 联合 ISA、同 shape 基准与模型解释差距，再交 Hygon kernel Skill 迭代 |

普通分析在本机 CPU 离线运行。EventReplay、采集、微基准属于远程实验，仍须资源准入、固定任务快照、超时与残留作业核对。`analysis-only` 不自动获得运行实验或修改训练的权限。

## 统一离线命令

```bash
hcu-trainflow --workspace /private/task/analysis tracelens-analyze request.json --project /path/to/HCU-TrainFlow --timeout 1800
```

路径相对于 request 文件，各模式分别提供以下字段，不接受任意 shell 命令：

```json
{"mode":"hipprof","trace":"hipprof.json"}
```

```json
{"mode":"hipprof","trace":"hipprof.pftrace","traceconv_path":"/tools/perfetto/traceconv"}
```

```json
{"mode":"graph","manifest":"graph-manifest.json","capture_folder":"graph-captures","gpu_arch_json":"hcu-arch.json"}
```

```json
{"mode":"roofline","perf_csv":"native/unified_perf_summary.csv","gpu_arch_json":"hcu-arch.json","wallclock_time_us":10000}
```

```json
{"mode":"agent","trace":"rank0.json","gpu_arch_json":"hcu-arch.json"}
```

```json
{"mode":"counters","manifest":"xcompute-manifest.json"}
```

```json
{"mode":"split","trace":"rank0.json","iterations":"10:20"}
```

```json
{"mode":"merge","traces":{"0":"rank0.json","4":"rank4.json"}}
```

```json
{"mode":"compare","trace":"before.json","comparison_trace":"after.json","gpu_arch_json":"hcu-arch.json"}
```

`iterations` 是检测到的迭代序列的零基序号，结束位置不包含在内；不必等于训练日志的全局 step ID。缺步骤或范围被原生工具截短时标为 incomplete。合并的 rank ID 必须来自实际采集，不把抽样 rank 重新编号为完整 world；未采样 rank 仍是覆盖缺口。

每次生成独立目录，保留请求、输入/输出 SHA256、锁定源码提交、原生表、日志和 `report.json`。`generated` 仅表示该范围产物完成；`incomplete` 保留未知项；`needs-agent-review` 表示指标已准备、推理复核尚未完成，后两者返回退出码 2。残留 CSV 不能将失败/超时改判成功。这些状态都不替代训练阶段的数值、性能或独立 review 门槛。

## Roofline 与优化队列

HCU 架构 JSON 必须含实际设备身份和参数来源。实测 sustained envelope、厂商理论峰值、同 shape 可达基准分开记录。大 GEMM 的实测吞吐仅是条件参考，不是小矩阵、其他精度或 memory-bound 算子的可达上限。HCU 模型显式验证工作量映射；未知项保留 unknown，不套 AMD/NVIDIA 规格。

保留 `observed_kernel_time_sum_us`、墙钟窗口及 `kernel_time_sum_is_wallclock=false`。重叠 kernel 的时间之和不是端到端占比。`conditional_kernel_time_headroom_us` 是条件模型的筛查差距，`achievable_e2e_savings_pct` 保持未知；只有依赖/关键路径证据和 profiler-off 实验能支持端到端收益。

先处理最大的实际端到端问题。计算主导时按热点贡献排队，再结合模型空间、融合机会、已有实现和风险选任务；不能按自动模型跳过高占比未知项。`profile-analyze` 优先使用精确 operator key；名字级模型必须提供 `applies_to` 的匹配 shape/dtype/phase，已采集 stride 时也须匹配，避免同名 kernel 串用工作量。

待优化热点交给适用的 Hygon HIP/Triton Skill；缺初版时先用 baseline Skill。交接必须含调用、固定数值参考、上限假设、当前效率、真实 profile 和下一轮验证条件。已有融合也要复评；离上限较远时用计数器/SQTT/ISA解释，不能展示图表后就关闭任务。累计 ≥90% 集合中的非通信热点及未知项仍逐一处置。

## 从分析走到源码和候选实现

借鉴 Hyperloom 的原生分析交接、源码定位，以及 GEAK 对 baseline 分析先验的复用方式，接入现有优化队列，不另起一套调度器。源码审阅依据见 [参考方法](practices/performance-methods.md#tracelens-调用链核对)。

1. 将原生报告的热点映射到 `operator key + phase + shape/dtype/layout + backend`，保留原 trace/event/rank。CPU dispatcher、实际 GPU kernel、逻辑融合链分别记载，父调用与其子 kernel 不重复累加。报告中的 shape 回查原 trace 或捕获输入，不能只从分析文章提取。
2. 需要寻找实现时运行 `TraceLens_resolve_kernel_source --kernel NAME --search-path CHECKOUT`，读取其定位方法、置信度和 `patchable`，再核对实际加载制品与源码提交。HIP/C++、Triton 和 DTK 数学库制品使用各自定位路径。只有二进制线索时继续查底层库对应分支，不能按符号猜一个函数就修改。
3. 同一源码函数的多个特化可合并为一个实现任务，但保留每个 shape、dtype、phase 的频次/耗时与正确性回归，不能把它们合成一个虚构的平均调用。仅有相同 kernel 名称不构成同一实现的证据。
4. 源码不可直接修改的高占比项仍须处置：数学库核对实际 bench/tune 输入，已有库复用或向所属库准备修复；继续按 HCU 大库和实际分支找实现。原生工具的 `patchable=false` 只说明该定位结果不能直接编辑，不表示无需优化。
5. 旧报告仅在源码/制品、输入、配方、并行组和采集窗口一致时复用。参数、融合或实现改变后采新 trace，用 compare 检查调用变化，重新计算覆盖与优先级。性能提升以局部数值通过、profiler-off 配对和模型集成结果为准。

大量 trace 的跨实验定位可用原生 `TraceLens_trace_index`，数据库放任务缓存，保留输入哈希和查询条件；它只帮助寻找报告，不替代 HCU-Knowledge 的领域知识检索。源码定位和索引不强制每轮运行。

## 训练 Graph

使用 fork `TraceLens.Trace2Tree.training_graph`，不直接套推理 bucket。详细格式见 fork `docs/how-to/hcu-graph-replay.md`。

- 显式 capture/replay annotation、文件哈希、输入 signature、phase 和 segment。
- 当前可信契约为 `serialized_single_stream`。多 stream/并发 Graph、缺 capture 或名称/数量/耗时不一致，拒绝猜配。
- 原 GPU event 恰好计一次；恢复的 CPU 节点只表达 capture 调用，CPU duration 为零，不能拿来推断 replay CPU 瓶颈。
- fwd/bwd/重算/更新可能分段捕获；一个 Graph launch 不等于完整训练步。地址、参数值、RNG/训练状态另验。
- 专用函数保留增强树，不重新按 replay 时间戳构树；`graph_attribution` 保存原始索引，供任务绑定和复核。

## EventReplay

在采集点保存实际张量值及期望输出，以 `write_replay_bundle()` 生成源事件/原件 SHA 绑定的 bundle，保持 shape/dtype/stride/参数/schema。API 与拒绝条件见 fork `docs/how-to/hcu-graph-replay.md`。

```bash
python -m TraceLens.EventReplay.hcu_replay --bundle /private/task/replay.json --device hcu --warmup 3 --steps 10 --max-seconds 30 --report /private/task/replay-report.json
```

执行层还须外部进程 deadline；Python 时间预算不能中断已经卡死的 GPU kernel。随机输入只记 synthetic。变异、别名、随机数、通信和训练状态调用缺少完整专用契约时拒绝通用回放；一次 ATen 成功不证明完整 backward/optimizer 等价。

同步 device-event 计时可能包括 launch/dispatch 间隙，与 trace 单个 kernel interval 不同。对照要同调用、同范围、多样本和同环境，不能拿不同范围的两列直接算“拖慢倍数”。每轮局部正确性和 profiler-off 性能，稳定阶段才长窗口验 loss。

## 原生 Agent

`agent` 模式调用原生报告、`orchestrator_prepare` 和 HCU category runner，不暗启其他 LLM 服务。当前宿主 Agent 接着：

1. 读输出 manifest、HCU Roofline 和实际出现类别的原生 instruction，检查采集代码是否刻意同步/缩形状。
2. 查原 trace/计数器/源码，写 findings 与 `analysis.md`，分清事实、假设、条件空间和下一实验。CPU duration 减 GPU 时间最多是筛查线索，不证明同步因果。
3. 核对当前输入和结论后，运行 `python -m TraceLens.Agent.Analysis.utils.hcu_analysis review --output-dir <分析目录> --include-report`，将已审阅的 findings/报告绑定到当前原件、指标和代码。再运行同模块 `aggregate --output-dir <分析目录>`，分别检查类别 metrics、findings、最终报告状态，并独立审核结论。输入、指标或分析文件变化后旧回执失效；不要为了通过聚合直接重签旧结论。
4. 回到 TrainFlow 的覆盖、并行域、显存和数值约束。原生 top-N 不替代 ≥90% 集合，不按类别数量机械增加 Agent。

结构校验不能证明结论正确。已用当前活跃 Agent 验证“指标→源码→findings→聚合”链路；其他宿主仍需活跃 Agent 或配置的推理服务，离线脚本不会自行推理。

## HCU profiler 格式与权限

hipprof 解析实际 DTK `HIP/HIPOPS/HIPCOPY`，按 pid+index 关联；autograd worker 的 procId 不能当主 pid。保留纳秒原字段；pftrace begin/end 显示时间受精度影响时核对原始整数值。memset/copy 分开，D2D 不凭名字猜两端设备。派生 JSON 写缓存，不覆盖源文件旁同名 JSON。Perfetto 工具按实际系统指定路径。

XProf `.perf` 属另一种输入，先由匹配 XCompute 转计数器/SQTT CSV，再用 manifest 记录工具、设备、原件哈希、采样和命令。格式见 fork `docs/how-to/hcu-xprof-xcompute.md`。N/A 非 0；未标单位的 SQTT 列不猜周期/纳秒；不同 `.perf` 中相同 dispatch id 不合并。关联训练 trace 需真实调用/shape 证据，不只凭 kernel 名称。

这里的 XProf 是 HCU 工具包的 `xprof` 可执行程序，与 TraceLens `jax` extra 中同名 PyPI `xprof` 包不是同一安装来源；不要通过 `pip install xprof` 代替 HCU 工具安装。hipprof timeline、XProf counter/SQTT、XCompute 解析各自按版本和输入格式核对。

counter replay 会多次运行 kernel；SQTT 通常仅采指定 SE/CU/dispatch。其时间不是 profiler-off 基线，也不代表全芯片所有 wave。权限随工具/驱动版本而定：本轮 XProf 需要 `/dev/mem` 及对应权限，缺失时初始化失败。按现场文档核对后在授权的专用诊断容器补齐，不无条件提高普通训练容器权限。

## 实测覆盖与边界

本轮在 BW1000_H/gfx936、DTK 26.10、Torch 2.11.0/HIP 7.2.26365 空闲设备上执行有界资格测试，原件/命令留私有任务证据。这是工具能力验证，不是 Kimi K3 优化或完整训练质量验证。

| 能力 | 真实验证 | 边界 |
| --- | --- | --- |
| Graph | 前向+反向捕获、4 次 replay；loss/grad 对 eager 一致；44 GPU 事件一次计数、3 种 GEMM shape 恢复 | 多 stream/复杂训练图未放宽契约 |
| EventReplay | 实际 mm 输入/输出；HCU 执行、10 样本与数值校验通过 | 状态/RNG/通信用专用测试 |
| Roofline | FP32/BF16 GEMM、device-copy 校准；真实 trace 的支持/未知项输出 | 复杂算子继续建模；实测 envelope 不是厂商峰值 |
| Agent | 原生类别指标、活跃 Agent findings/报告及聚合 | 不将刻意同步的微基准空泡推广为生产瓶颈 |
| hipprof JSON/pftrace | 同次采集两路径表逐项一致：92 kernel、18 copy、26 memset | 其他 DTK 格式就地核对 |
| XProf/XCompute | XProf 3.16.0+aqlprofile 3.6.2 counter/SQTT 实采；XCompute Light 4.8.0 解析 | GUI、其他 gfx/DTK、完整训练采样未覆盖 |

2026-10-13 对同栈另做全路径复核：原生报告、Graph、Roofline、捕获值回放及六类 Agent 指标重跑；两 rank RCCL 的 8 条记录匹配成 4 次 collective；同一次 hipprof 采集的 JSON/pftrace 六张表逐项一致；XProf counter 和选定 dispatch 的 SQTT 均重新采集解析。本次还用真实 trace 验证切分、索引、HIP 源码定位、TraceDiff、报告自比较和多 rank 合并；自比较只验证工具，不能声称加速。Agent 最终推理报告的既有资格与本次指标复测分别记录，不把 metrics_complete 当作本轮完整推理已完成。

保留上游 rocprofv3、TraceDiff、JAX 等入口。HCU 替代路径以实际格式适配及执行证据说明，不能把保留入口称作所有平台/格式均已实测。
