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

## TraceLens

可用其 `TraceLens_generate_perf_report_pytorch --profile_json_path ... --output_csvs_dir ...` 做细节报告，先看已安装 `--help`。multi-rank collective 报告需要真实 rank 及通信上下文。TrainFlow 不内置或重写完整 TraceLens，也不把其内置其他厂商架构表当 HCU 峰值。

kernel 瓶颈升级到 Hygon 算子 Skill，按环境分别使用 XProf/XCompute 或 hipprof。测量吞吐时关闭 profiler；对照 NV 融合粒度和内部精度路径后再验端到端收益。
