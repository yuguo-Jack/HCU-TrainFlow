# 性能分析与非通信热点上限

## 输入契约

保存 PyTorch/Chrome trace、明确 start_us/end_us、实际 process groups、rank、phase、shape/dtype/stride 及 workload 捕获证据。`profile-plan` 要求每个实际非单例组至少两个可用 rank；并不是任意 rank0/rank1 都足够。

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

纯通信项单列 message/topology/wait/overlap；有计算工作的混合 kernel 用 mixed_compute，仍评估计算部分。attention 的 score/softmax/IO/recompute 与 backward 不能简单视作一个 GEMM。

## 模型内外对照

实际热点中的计算、通信、copy 都应检查；完整调用条件、元数据采集扰动、计时口径及差距归因见 [优化 Skill 的对照方法](../skills/hcu-train-optimize/references/operator-comparison.md)。同 shape 并不自动代表同算法、同布局或同字节量。独立通信保留各 rank 的实际 splits；copy 保留方向、dtype/stride 与 pinned/async 语义；模型内的等待与资源竞争需通过对照定位。

端到端吞吐来自 profiler-off 稳态运行。干净 profile 与额外包装采集分别记录；诊断运行用于定位与建立可重放输入，不把其 CPU wrapper 耗时当 GPU kernel 延迟。先核对实际分发和数值，再比较模型内外耗时分布与匹配的上限，最后回到端到端验证收益。

## TraceLens

安装与依赖版本见 [第三方集成](integrations.md)。`tracelens-report TRACE --project PROJECT --rank RANK` 调用锁定版本的 PyTorch report API，输出原生 op/kernel、overlap 等 CSV、输入哈希、日志与报告清单。JSON 和 `.json.gz` 均可读取；不是重新实现一套 TraceLens。

`tracelens-collective 'rank*.json' --project PROJECT --world-size N` 要求完整 `0..N-1` 文件和实际通信上下文。并行域只采两个代表 rank 时，仍可逐 rank 分析，但不足以运行要求完整 ranks 的 collective 报告。RCCL 事件能否识别、collective 映射和分组字段须在目标 trace 上核对；合成单 rank 回归不代表真实 HCU 通信已验证。

`generated` 表示非空报告生成，不表示优化完成。TraceLens 原生百分比的统计窗口/分母不自动等于 TrainFlow 稳态窗口墙钟；Agent 需结合窗口、process groups 和 shape 证据解释，两套结果不能直接相加。缺失 CPU-op 关联、空表、超时与执行失败都会明确保留。

选窗口时以 CPU `user_annotation` 的完整 `ProfilerStep#` 为依据。HIP trace 还可能在多个 GPU stream 输出同名 `gpu_user_annotation`；这些是同一步的设备区间，不能当成额外训练步。inventory 分别记录 CPU/GPU step annotation 数目，同时保留原总数。必须对照实际训练循环调用 `prof.step()` 的位置和 profiler schedule，不能由命令的起止数字直接推断采了几步。

原生分析的 Python warnings 会保留在 worker 摘要及 stderr。若同一 CPU-op 组含不同数量的 kernel，TraceLens 的逐位置 kernel-detail 汇总可能跳过部分列表；此时报告标记 `incomplete`，不把聚合表误称完整样本。原始区间及独立事件归因仍可用于核对覆盖。没有父 CPU-op 的 runtime 项（例如 `hipLaunchKernel`）不能当作已经建立语义的算子；保持 `unlinked`，再按源码或额外采集定位。CPU 输入 shape 也不能直接充当其中每个 kernel 的 FLOPs 或访存量。

默认不加载其他厂商的架构峰值。确有匹配 HCU 的配置才传 `--gpu-arch-json`；复杂算子仍需补充实际算法和访存模型，不能仅凭自动 FLOPs 宣称达到上限。

kernel 瓶颈升级到 Hygon 算子 Skill，按环境分别使用 XProf/XCompute 或 hipprof。测量吞吐时关闭 profiler；对照 NV 融合粒度和内部精度路径后再验端到端收益。

## 从分析到优化队列

计算占主导时，按真实逻辑算子的端到端贡献优先分析，再结合上限空间和证据选择实现任务。高占比项的模型未知是待解决问题，不能跳过去优先做容易实现的小项。按[热点上限、融合与实现迭代](../skills/hcu-train-optimize/references/operator-ceiling-iteration.md)维护两层排序、融合后复评、HIP迭代和逐项退出依据；保持不同 trace、rank、阶段的分母独立。已有融合仅是新的基线，仍需证明当前效率和继续优化或停止的原因。
