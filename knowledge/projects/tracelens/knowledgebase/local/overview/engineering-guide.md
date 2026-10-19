---
id: tooling/tracelens
title: TraceLens 复用接口与训练补充信息
engine: tooling
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-20'
sources:
- source: amd-agi-tracelens
  path: setup.py
  commit: c34d16c58983e83023643d8578ff4e6f7a1b2744
  sha256: 29d8f29499f4a8f4a5fc2c0aa6407d6f400a7c5bfdfb3ba2be274aff493fc253
- source: amd-agi-tracelens
  path: TraceLens/Reporting/generate_perf_report_pytorch.py
  commit: c34d16c58983e83023643d8578ff4e6f7a1b2744
  sha256: 1027bf63be0cbd1dc053c905256639e5cc870a61b0278a0669aaf7ede414ead0
- source: amd-agi-tracelens
  path: docs/how-to/collective-report.md
  commit: c34d16c58983e83023643d8578ff4e6f7a1b2744
  sha256: 5e593b974ec752c8b43b4f5babd2edc86e3eed19cefcbcb63b05ca55de0d36ce
- source: amd-agi-tracelens
  path: TraceLens/PerfModel/benchmarking/fp4fp6_helpers.py
  commit: c34d16c58983e83023643d8578ff4e6f7a1b2744
  sha256: 26853c27b4d3f8f6a79fd28724358e80a7ed1281222adad996220f0865a565f7
- source: amd-agi-tracelens
  path: TraceLens/PerfModel/benchmarking/microbench.py
  commit: c34d16c58983e83023643d8578ff4e6f7a1b2744
  sha256: ba2e720e8741fd96784a9b0c166f000b980b3331605a0ceb719f366bc9ad0c3b
- source: amd-agi-tracelens
  path: TraceLens/PerfModel/benchmarking/microbench_utils.py
  commit: c34d16c58983e83023643d8578ff4e6f7a1b2744
  sha256: d9469794e4fea032d8c72e5cc4d5c5708a8c1bbac3cb3d556149dce4802c808d
- source: amd-agi-tracelens
  path: TraceLens/PerfModel/extensions/moe_perf_model_extensions.py
  commit: c34d16c58983e83023643d8578ff4e6f7a1b2744
  sha256: 9712ca63569be3c94798fcfc0bbba5c090472c69b9aa449cf2fc6e972c4fd765
- source: amd-agi-tracelens
  path: TraceLens/Reporting/compare_perf_reports_pytorch.py
  commit: c34d16c58983e83023643d8578ff4e6f7a1b2744
  sha256: db66408515d249574ececabcc6a219f70f48d77a916d40150228a75ad3827ff6
- source: amd-agi-tracelens
  path: TraceLens/TraceUtils/utils/trace_extraction.py
  commit: c34d16c58983e83023643d8578ff4e6f7a1b2744
  sha256: 2d3b57a111857edc53de396a8f734458d8d505240a1b8d6639f64208fc1506f9
- source: amd-agi-tracelens
  path: tests/test_compare_perf_reports.py
  commit: c34d16c58983e83023643d8578ff4e6f7a1b2744
  sha256: 91cce7a4a15680a1f3223929fdb09bf503112fdae109b268165076ba90669dc9
- source: amd-agi-tracelens
  path: tests/test_perfmodel_benchmarking.py
  commit: c34d16c58983e83023643d8578ff4e6f7a1b2744
  sha256: 058582281f1086ce14b19918114ecbf3dc1ad6ae08e58b56e191241be0a5f77c
- source: amd-agi-tracelens
  path: tests/test_perfmodel_extensions.py
  commit: c34d16c58983e83023643d8578ff4e6f7a1b2744
  sha256: dfd880d24e8d48ac201e3912a12c6b82ff816f2b72efeed036788a7609c56d88
---

# TraceLens 官方分析机制与阅读路线

## 定位和源码组织

本项目维护 **AMD-AGI/TraceLens 官方上游**，用于理解 profile 的报告、归因、比较与性能模型。`Reporting/` 组织报告入口，`Trace2Tree/` 关联调用与 GPU 事件，`TreePerf/` 汇总算子和 kernel，`PerfModel/` 提供条件性能模型，`EventReplay/` 处理支持的事件回放，`Agent/Analysis/` 提供分析材料与约束。完整文件路径见[固定源码地图](../../upstream/source-map/amd-agi-tracelens.md)，不要把目录存在视为所有硬件都支持。

## 安装、报告和测试入口

从[官方 README](../../upstream/docs/amd-agi-tracelens/README.md.md)和固定 `setup.py` 核对依赖与 entry points；原生 PyTorch 报告入口是 `TraceLens/Reporting/generate_perf_report_pytorch.py`。输入类型、输出选项和当前签名以[PyTorch 报告教程](../../upstream/docs/amd-agi-tracelens/docs/how-to/generate-perf-report-pytorch.md.md)及对应源码为准。先用完整、有限的已知 trace 核对事件数、单位、时间窗口及缺失关联，再使用报告解释训练性能。

多 rank 通信使用[collective 教程](../../upstream/docs/amd-agi-tracelens/docs/how-to/collective-report.md.md)：保留 group/rank、消息量及同步等待，不能把不同通信域直接合并。训练步、optimizer、数据/保存活动是否在窗口内必须明示，GPU 时长和不能作为端到端墙钟。

## 机制与性能判读

| 问题 | 官方阅读入口 | 判断边界 |
| --- | --- | --- |
| op 到 GPU kernel 的归因 | [Trace2Tree](../../upstream/docs/amd-agi-tracelens/docs/conceptual/trace2tree.md.md)、[shape metadata](../../upstream/docs/amd-agi-tracelens/docs/conceptual/shape-metadata.md.md) | 缺失关联、shape 或调用栈要保留未知，不能凭 kernel 名填造输入 |
| 候选前后变化 | [TraceDiff](../../upstream/docs/amd-agi-tracelens/docs/how-to/compare-traces.md.md) | 配对相同窗口、配置和 profiler 设置；分布式关键路径需要独立证据 |
| GEMM / 条件上限 | [GEMM 分析](../../upstream/docs/amd-agi-tracelens/docs/conceptual/gemm-analysis.md.md)、[Triton 性能模型](../../upstream/docs/amd-agi-tracelens/docs/conceptual/triton-perf-model-walkthrough.md.md) | dtype、shape、布局、读写流量和硬件峰值决定条件；模型差距不是端到端可得加速 |
| 模型内干扰与孤立执行 | [EventReplay](../../upstream/docs/amd-agi-tracelens/docs/how-to/event-replay.md.md) | 检查参数与状态能否复现；同步单测和异步训练时间需对齐范围 |
| Agent 分析 | [官方 Agent 教程](../../upstream/docs/amd-agi-tracelens/docs/how-to/agent.md.md) | 脚本输出是分析输入；结论仍需查证原件、未知项和数值边界 |

## 当前分析与微基准的细化边界

MoE performance model 现按激活/权重中较宽的计算精度选择矩阵上限，例如 BF16 激活配 MXFP4 权重不直接使用 FP4 peak。microbench 的 MXFP4/6 会在可整除 shape 的有限 tile 中取最佳值，编译/launch 失败的 tile 被跳过，全部适用 tile 失败会报错；保存实际 shape、配置和失败项，不能把最佳 tile 视为任何 shape 的通用吞吐。

官方 `NATIVE_MX_GFX_ARCHS` 当前只列 gfx950，其他非空 gfx 会在生成 arch JSON 时采用 FP16/BF16 peak 作为 MX 上限；这是一条上游建模规则。HCU 必须核对目标 ISA、实际计算精度和设备实测，不按同名 gfx 字符串或低精度存储宽度自动套用该规则。arch JSON 的峰值、带宽和容量也已保留一位小数，消费者应按有限有效数值读取，不要求整数或把 0.0 哨兵作为有效性能基准。

当前官方 compare 的 `--sheets all` 可跳过未生成的 kernel_summary；显式要求该表仍报错并提示生成时启用。split 输出增加 `busy_ratio=GPU忙区间/所选GPU跨度`，合并范围文件名改用连字符；这不是完整训练墙钟占比，调用者应读取返回的实际 output_path，不能拼旧文件名或据 busy_ratio 推断分布式利用率。对应报告/模型单测是阅读与回归入口，本轮未执行 GPU 微基准。

## HCU 消费方与更新

上游 rocprof、架构预测、回放或 Graph 能力不自动等于 HCU 可用。HCU fork 的部署、API 适配、真实验证和故障处理统一见[工作流集成契约](../../../../../../docs/tracelens-analysis.md)及[外部入口](../../../../../catalog/external/hcu-tracelens.md)，本页不重复维护该 fork 的代码知识。

上游更新时同时检查调用树语义、报告列与单位、shape 处理、回放约束、性能模型和 Agent 输入。通过固定 PR/head/base 追实现，再在集成层核对是否影响现用 HCU fork；不可直接用 upstream HEAD 替换运行依赖。源码阅读和工具资格测试不构成完整训练精度/收敛通过。