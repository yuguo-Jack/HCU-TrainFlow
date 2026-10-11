# 性能分析与非通信热点上限

## 输入契约

保存 PyTorch/Chrome trace、明确 start_us/end_us、实际 process groups、rank、phase、shape/dtype/stride 及 workload 捕获证据。`profile-plan` 要求每个实际非单例组至少两个可用 rank；并不是任意 rank0/rank1 都足够。

跨 rank 判断到达先后或因果链时，保存共同参考时基、校时方法、offset/drift 与误差界，再按实际 group、调用序列及 producer → consumer → join 对应。待解释的时间差不大于误差时保持未知；单 rank 的区间时长仍可独立报告。GPU 空白还可能来自输入/提交、依赖/peer 等待、流水线空泡或缺事件，不能仅凭空白定性 CPU 或链路瓶颈。

```bash
hcu-trainflow profile-plan examples/groups.json
hcu-trainflow profile-analyze examples/trace.json examples/window.json --models examples/models.json --groups examples/process-groups.json --output .work/analysis.json
```

## 分母和重叠

每 rank 的整个训练窗口墙钟为分母。区间扫描求 GPU busy union，并把同一重叠片段等份归因到活跃 kernel，用于透明的初步排序。它不是关键路径算法，也不能把各 rank 时间相加当全局时间。

热点按归因占比排序取累计至少 90%。若 GPU 只占窗口 60%，工具会保留 40% CPU/等待/未归因缺口，不能声称已覆盖 90%。空 trace、无 rank、缺 shape、窗口截断 kernel 或缺模型均不能完成评估。未识别 event 类别显式输出；真实 PyTorch kernel 常不带 shape，需 TraceLens CPU-op 关联或独立 workload capture 补齐。

## 模型

GEMM FLOPs = 2×M×N×K×batch。其他 op 由实际算法定义 FLOPs、有效/实测字节量与延迟下限。理论时间下界：max(FLOPs/匹配算力, bytes/匹配带宽, latency_floor)。eta_bound = 下界/当前 kernel 时间，是在假设下的效率指标，不是硬件计数器利用率。

每项模型必须给 basis；峰值来自匹配硬件/精度/软件/频率条件。shape 的数学最小字节量忽略 cache、重读和中间量，需写清假设。eta>1 表示模型或测量待复核，不截成 100%。建议再给同 shape 独立测试与可达参考，以判断是实现差距还是训练并发干扰。

模型按 operator key 与实际 phase/shape/dtype/stride/算法适用范围核对；同名 kernel 可对应不同工作量，不能把某次 M/N/K 模型沿用于其他调用。确实通用的名字级延迟模型也须说明条件。kernel 的 eta_bound、完整训练 MFU 与 HFU 分别命名：MFU 使用有用模型工作，HFU 使用包含重算的实际执行工作，并注明 FLOPs、设备数、完整窗口和匹配精度峰值；MoE、辅助头或混合精度不能无条件套 `6N × tokens` 或单一矩阵峰值。

纯通信项单列 message/topology/wait/overlap；有计算工作的混合 kernel 用 mixed_compute，仍评估计算部分。attention 的 score/softmax/IO/recompute 与 backward 不能简单视作一个 GEMM。

## 模型内外对照

实际热点中的计算、通信、copy 都应检查；完整调用条件、元数据采集扰动、计时口径及差距归因见 [优化 Skill 的对照方法](../skills/hcu-train-analyze-and-optimize/references/operator-comparison.md)。同 shape 并不自动代表同算法、同布局或同字节量。独立通信保留各 rank 的实际 splits；copy 保留方向、dtype/stride 与 pinned/async 语义；模型内的等待与资源竞争需通过对照定位。

端到端吞吐来自 profiler-off 稳态运行。干净 profile 与额外包装采集分别记录；诊断运行用于定位与建立可重放输入，不把其 CPU wrapper 耗时当 GPU kernel 延迟。先核对实际分发和数值，再比较模型内外耗时分布与匹配的上限，最后回到端到端验证收益。

扩展效率说明基准设备数与工作量：固定完整工作量的强扩展可用 `(T_base / T_N) / (N / N_base)`；弱扩展固定局部负载时，全局 batch、有效 token 数及质量语义可能改变，不能直接沿用强扩展结论。

## TraceLens

Graph、Roofline、原生 Agent、EventReplay、hipprof/pftrace 与 XProf/XCompute 的入口选择、实测范围和失败处理见 [HCU 分析与验证](tracelens-analysis.md)。命中功能时先读该页，再解释自动报告或发起实验。

安装与依赖版本见 [第三方集成](integrations.md)。`tracelens-report TRACE --project PROJECT --rank RANK` 调用锁定版本的 PyTorch report API，输出原生 op/kernel、overlap 等 CSV、输入哈希、日志与报告清单。JSON 和 `.json.gz` 均可读取；不是重新实现一套 TraceLens。

`tracelens-collective 'rank*.json' --project PROJECT --world-size N` 要求完整 `0..N-1` 文件和实际通信上下文。并行域只采两个代表 rank 时，仍可逐 rank 分析，但不足以运行要求完整 ranks 的 collective 报告。RCCL 事件能否识别、collective 映射和分组字段须在目标 trace 上核对；合成单 rank 回归不代表真实 HCU 通信已验证。

`generated` 表示非空报告生成，不表示优化完成。TraceLens 原生百分比的统计窗口/分母不自动等于 TrainFlow 稳态窗口墙钟；Agent 需结合窗口、process groups 和 shape 证据解释，两套结果不能直接相加。缺失 CPU-op 关联、空表、超时与执行失败都会明确保留。

训练 Graph 的一次 launch 不等于一完整训练步：fwd/bwd/重算/更新及梯度累积可能分别捕获或重放。capture 只用于恢复调用映射，正式时间来自真实稳态 replay；核对精确图特化、phase、调用序列、参数/地址与 RNG/状态契约。推理 annotation、最近 batch bucket、CSV 非空或 sanity 日志没有报错均不能证明训练映射完整；根/特化未匹配及事件数/耗时不一致保持缺口。具体支持范围以锁定源码和目标 trace 资格结果为准。

EventReplay 的元数据 IR 或随机输入执行仅证明该范围的合成调用可用；真实数据依赖、梯度、alias 与原地状态需按[独立重放契约](../skills/hcu-train-analyze-and-optimize/references/operator-comparison.md)补齐。原生 Agent 的 top-10、空泡触发门槛及 `SUCCESS` 不替代本仓覆盖、因果和训练验收，见[证据闭环](../skills/hcu-train-analyze-and-optimize/references/evidence-driven-loop.md)。

选窗口时以 CPU `user_annotation` 的完整 `ProfilerStep#` 为依据。HIP trace 还可能在多个 GPU stream 输出同名 `gpu_user_annotation`；这些是同一步的设备区间，不能当成额外训练步。inventory 分别记录 CPU/GPU step annotation 数目，同时保留原总数。必须对照实际训练循环调用 `prof.step()` 的位置和 profiler schedule，不能由命令的起止数字直接推断采了几步。

原生分析的 Python warnings 会保留在 worker 摘要及 stderr。若同一 CPU-op 组含不同数量的 kernel，TraceLens 的逐位置 kernel-detail 汇总可能跳过部分列表；此时报告标记 `incomplete`，不把聚合表误称完整样本。原始区间及独立事件归因仍可用于核对覆盖。没有父 CPU-op 的 runtime 项（例如 `hipLaunchKernel`）不能当作已经建立语义的算子；保持 `unlinked`，再按源码或额外采集定位。CPU 输入 shape 也不能直接充当其中每个 kernel 的 FLOPs 或访存量。

默认不加载其他厂商的架构峰值。确有匹配 HCU 的配置才传 `--gpu-arch-json`；复杂算子仍需补充实际算法和访存模型，不能仅凭自动 FLOPs 宣称达到上限。

kernel 瓶颈升级到 Hygon 算子 Skill，按环境分别使用 XProf/XCompute 或 hipprof。测量吞吐时关闭 profiler；对照 NV 融合粒度和内部精度路径后再验端到端收益。

## 从分析到优化队列

计算占主导时，按真实逻辑算子的端到端贡献优先分析，再结合上限空间和证据选择实现任务。高占比项的模型未知是待解决问题，不能跳过去优先做容易实现的小项。按[热点上限、融合与实现迭代](../skills/hcu-train-analyze-and-optimize/references/operator-ceiling-iteration.md)维护两层排序、融合后复评、HIP迭代和逐项退出依据；保持不同 trace、rank、阶段的分母独立。已有融合仅是新的基线，仍需证明当前效率和继续优化或停止的原因。

## 证据刷新与模型解释

按 [证据驱动闭环](../skills/hcu-train-analyze-and-optimize/references/evidence-driven-loop.md) 区分映射运行、正式稳态 trace、计数器与无 profiler 计时。并行/微批/重算、graph/compile、融合/backend 或布局变化时重建受影响的 rank/shape/源码映射和热点；不能把旧窗口归因用于新候选。方法出处与采用边界见 [性能方法](practices/performance-methods.md)。

`profile-analyze` 的算子评估增加 `bound_terms_us`（compute/memory/latency）、`limiting_terms`（最大模型项，可并列）和 `arithmetic_intensity_flops_per_byte`。流量层级由输入 `basis` 解释；这是模型分解，不是计数器确认的瓶颈。零 FLOPs 的 copy 可用带宽模型；无正值下界仍为 incomplete。工作量、派生值和决策阈值须为有限合法数，`slowdown_threshold >= 1`，`0 < efficiency_target <= 1`，无效输入报错，不静默跳过干扰检查。不同精度/资源、共享带宽和串行依赖须由调用者建立适用模型，简单 max 不能替代依赖分析。
