---
id: tooling/tracelens
title: TraceLens 复用接口与训练补充信息
engine: tooling
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-11'
sources:
- source: amd-agi-tracelens
  path: setup.py
  commit: c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3
  sha256: 29d8f29499f4a8f4a5fc2c0aa6407d6f400a7c5bfdfb3ba2be274aff493fc253
- source: amd-agi-tracelens
  path: TraceLens/Reporting/generate_perf_report_pytorch.py
  commit: c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3
  sha256: 1027bf63be0cbd1dc053c905256639e5cc870a61b0278a0669aaf7ede414ead0
- source: amd-agi-tracelens
  path: docs/how-to/collective-report.md
  commit: c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3
  sha256: 5e593b974ec752c8b43b4f5babd2edc86e3eed19cefcbcb63b05ca55de0d36ce
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

## HCU 消费方与更新

上游 rocprof、架构预测、回放或 Graph 能力不自动等于 HCU 可用。HCU fork 的部署、API 适配、真实验证和故障处理统一见[工作流集成契约](../../../../../../docs/tracelens-analysis.md)及[外部入口](../../../../../catalog/external/hcu-tracelens.md)，本页不重复维护该 fork 的代码知识。

上游更新时同时检查调用树语义、报告列与单位、shape 处理、回放约束、性能模型和 Agent 输入。通过固定 PR/head/base 追实现，再在集成层核对是否影响现用 HCU fork；不可直接用 upstream HEAD 替换运行依赖。源码阅读和工具资格测试不构成完整训练精度/收敛通过。
