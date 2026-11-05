---
id: tooling/tracelens
title: TraceLens 复用接口与训练补充信息
engine: tooling
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-11-04'
retrieved_on: '2026-11-04'
sources:
- source: amd-agi-tracelens
  path: setup.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: dfb945fa7f3de359e711a05ebcaa6757d814af61963e89126409c227a6320505
- source: amd-agi-tracelens
  path: TraceLens/Reporting/generate_perf_report_pytorch.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: 5811e3b4d77f75c9ebc8d823d8ff5e644fc9837ed687e0a83a0f22a7075a9b74
- source: amd-agi-tracelens
  path: docs/how-to/collective-report.md
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: 5e593b974ec752c8b43b4f5babd2edc86e3eed19cefcbcb63b05ca55de0d36ce
- source: amd-agi-tracelens
  path: TraceLens/PerfModel/benchmarking/fp4fp6_helpers.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: 26853c27b4d3f8f6a79fd28724358e80a7ed1281222adad996220f0865a565f7
- source: amd-agi-tracelens
  path: TraceLens/PerfModel/benchmarking/microbench.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: ba2e720e8741fd96784a9b0c166f000b980b3331605a0ceb719f366bc9ad0c3b
- source: amd-agi-tracelens
  path: TraceLens/PerfModel/benchmarking/microbench_utils.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: d9469794e4fea032d8c72e5cc4d5c5708a8c1bbac3cb3d556149dce4802c808d
- source: amd-agi-tracelens
  path: TraceLens/PerfModel/extensions/moe_perf_model_extensions.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: c9ca3842a2c39f1fabe282b46a65dd652a98696df7fc95b530f77297c5c45240
- source: amd-agi-tracelens
  path: TraceLens/Reporting/compare_perf_reports_pytorch.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: db66408515d249574ececabcc6a219f70f48d77a916d40150228a75ad3827ff6
- source: amd-agi-tracelens
  path: TraceLens/TraceUtils/utils/trace_extraction.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: c6a6d7048e96a43fef58317ca2a1d052e04e87aabc80b875d26abb767c97945b
- source: amd-agi-tracelens
  path: tests/test_compare_perf_reports.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: 91cce7a4a15680a1f3223929fdb09bf503112fdae109b268165076ba90669dc9
- source: amd-agi-tracelens
  path: tests/test_perfmodel_benchmarking.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: 058582281f1086ce14b19918114ecbf3dc1ad6ae08e58b56e191241be0a5f77c
- source: amd-agi-tracelens
  path: tests/test_perfmodel_extensions.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: f6a6b243fe6866a826725d932f08ed323665d65bf5888e029fff28c6e722cd9b
- source: amd-agi-tracelens
  path: README.md
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: 2dc0c8abdfdc4c6bcdff7df203b6000ea4995a1450a5e7539c7152b1e45009f0
- source: amd-agi-tracelens
  path: TraceLens/Agent/Analysis/utils/deterministic_fallback.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: 101c7faccd755c0b5aad5cb50cbf583f3f9ab1e97993e9df0de8d3bf4c8d1143
- source: amd-agi-tracelens
  path: TraceLens/Trace2Tree/trace_capture_merge_experimental.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: 61a0b517c4be6782df98230bca6183b6eee9e948c31ea5f9f31ae4e19a75a777
- source: amd-agi-tracelens
  path: TraceLens/TraceUtils/split_trace/main.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: 835cd090be6ebe29185414e3ece0519137474e0cde1e3bbf6e5509e3ae0eaa7b
- source: amd-agi-tracelens
  path: TraceLens/Trace2Tree/trace_to_tree.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: 2e4553a9c116e5516bf11c4f896b2f1408c46ef2159d8c89918d6e39d01cb245
- source: amd-agi-tracelens
  path: TraceLens/Reporting/generate_multi_rank_collective_report_pytorch.py
  commit: 90f2f6f58210d1828c5eca6949b1dce7d2525fa7
  sha256: 0566e1ecf0606f7f39e22e99d1c264ea104ebee65f8e574b48d98f178338adf3
---

# TraceLens 官方分析机制与阅读路线

## 定位和源码组织

本项目维护 **AMD-AGI/TraceLens 官方上游**，用于理解 profile 的报告、归因、比较与性能模型。`Reporting/` 组织报告入口，`Trace2Tree/` 关联调用与 GPU 事件，`TreePerf/` 汇总算子和 kernel，`PerfModel/` 提供条件性能模型，`EventReplay/` 处理支持的事件回放，`Agent/Analysis/` 提供分析材料与约束。完整文件路径见[固定源码地图](../../upstream/source-map/amd-agi-tracelens.md)，不要把目录存在视为所有硬件都支持。

## 安装、报告和测试入口

从[官方 README](../../upstream/docs/amd-agi-tracelens/README.md.md)和固定 `setup.py` 核对依赖与 entry points；原生 PyTorch 报告入口是 `TraceLens/Reporting/generate_perf_report_pytorch.py`。输入类型、输出选项和当前签名以[PyTorch 报告教程](../../upstream/docs/amd-agi-tracelens/docs/how-to/generate-perf-report-pytorch.md.md)及对应源码为准。先用完整、有限的已知 trace 核对事件数、单位、时间窗口及缺失关联，再使用报告解释训练性能。

多 rank 通信使用[collective 教程](../../upstream/docs/amd-agi-tracelens/docs/how-to/collective-report.md.md)：保留 group/rank、消息量及同步等待，不能把不同通信域直接合并。训练步、optimizer、数据/保存活动是否在窗口内必须明示，GPU 时长和不能作为端到端墙钟。

## 本固定上游的接口变化

本次阅读固定在官方 `90f2f6f58210d1828c5eca6949b1dce7d2525fa7`，采集/复核日期为 2026-11-04。PyTorch `generate_perf_report_pytorch` 已移除 `python_path` 与旧 `enable_origami`，改为两个默认 False 的 `enable_origami_gemm` / `enable_origami_sdpa_tile`；CLI 分别为 `--enable-origami-gemm` / `--enable-origami-sdpa-tile`，仍要求合适的 GPU arch。GEMM 预测列和按 tile GEMM 建模的 SDPA 预测不同，不能把预测时间当作实测或混合使用旧参数。

extension loader 新增 `external_op_projection`，以及必须为 dict 的 `op_projections` / `kernel_filters`，逐 label 注册；原有 tree postprocess、perf model 和类别 hook 仍有各自作用。extension 是可执行 Python，固定来源和适用版本，不能把动态注册结果当作所有算子的默认模型。

`setup.py` 新增 config-driven report、model explorer visualizer 和 model roofline projection entry points，以及单独的 `Visualizer` extra。entry point 存在只证明注册；其依赖、配置 schema、静态模型预测与目标硬件能力还需沿具体实现核实，本轮没有安装或运行。现用 HCU fork `22786b16d429783927981bd592a47ad0f79db3ba` 仍使用自己的固定签名，不能把这些新参数直接透传，也不据官方上游变化升级依赖锁。

## 机制与性能判读

| 问题 | 官方阅读入口 | 判断边界 |
| --- | --- | --- |
| op 到 GPU kernel 的归因 | [Trace2Tree](../../upstream/docs/amd-agi-tracelens/docs/conceptual/trace2tree.md.md)、[shape metadata](../../upstream/docs/amd-agi-tracelens/docs/conceptual/shape-metadata.md.md) | 缺失关联、shape 或调用栈要保留未知，不能凭 kernel 名填造输入 |
| 候选前后变化 | [TraceDiff](../../upstream/docs/amd-agi-tracelens/docs/how-to/compare-traces.md.md) | 配对相同窗口、配置和 profiler 设置；分布式关键路径需要独立证据 |
| GEMM / 条件上限 | [GEMM 分析](../../upstream/docs/amd-agi-tracelens/docs/conceptual/gemm-analysis.md.md)、[Triton 性能模型](../../upstream/docs/amd-agi-tracelens/docs/conceptual/triton-perf-model-walkthrough.md.md) | dtype、shape、布局、读写流量和硬件峰值决定条件；模型差距不是端到端可得加速 |
| 模型内干扰与孤立执行 | [EventReplay](../../upstream/docs/amd-agi-tracelens/docs/how-to/event-replay.md.md) | 检查参数与状态能否复现；同步单测和异步训练时间需对齐范围 |
| Agent 分析 | [官方 Agent 教程](../../upstream/docs/amd-agi-tracelens/docs/how-to/agent.md.md) | 脚本输出是分析输入；结论仍需查证原件、未知项和数值边界 |

## 当前分析与微基准的细化边界

MoE performance model 必须按具体类确认计算精度：W4A16 GPTQ/AWQ 用激活 dtype，FlyDSL A4W4 与新 OPUS A8W4 stage1 有自身 MXFP4 建模规则，不能把“存储4 bit”或“取两输入较宽者”推广为所有 kernel 的统一上限。microbench 的 MXFP4/6 会在可整除 shape 的有限 tile 中取最佳值，编译/launch 失败的 tile 被跳过，全部适用 tile 失败会报错；保存实际 shape、配置和失败项，不能把最佳 tile 视为任何 shape 的通用吞吐。

官方 `NATIVE_MX_GFX_ARCHS` 当前只列 gfx950，其他非空 gfx 会在生成 arch JSON 时采用 FP16/BF16 peak 作为 MX 上限；这是一条上游建模规则。HCU 必须核对目标 ISA、实际计算精度和设备实测，不按同名 gfx 字符串或低精度存储宽度自动套用该规则。arch JSON 的峰值、带宽和容量也已保留一位小数，消费者应按有限有效数值读取，不要求整数或把 0.0 哨兵作为有效性能基准。

当前官方 compare 的 `--sheets all` 可跳过未生成的 kernel_summary；显式要求该表仍报错并提示生成时启用。split 输出增加 `busy_ratio=GPU忙区间/所选GPU跨度`，合并范围文件名改用连字符；这不是完整训练墙钟占比，调用者应读取返回的实际 output_path，不能拼旧文件名或据 busy_ratio 推断分布式利用率。对应报告/模型单测是阅读与回归入口，本轮未执行 GPU 微基准。

新增 `moe_opus_stage1_a8w4` 从 packed FP4 权重、scale 与输出形状推导工作量，shape/dtype 不足返回无性能值；活跃专家数仍使用均匀路由的期望估计。`SglangMoeSortingSmall` 区分 compact/distributed 整数排序，`moe_sorting_opus_fwd` 只计实际可能写入的 padded slots、可选 moe buffer/workspace；非 dense 或无法识别的 tensor/布局保留 None。logical batch、捕获 padding、实际 routing 和整数操作不同于 dense GEMM FLOPs，报表比较要固定模型类与这些假设。

## 多节点降级报告与 split/merge

deterministic fallback 的 Graph coverage gate 现在逐 `node` 计算并采用最差节点，避免一个完整 trace 掩盖另一个节点的缺失。多 trace 报告按 node/op 聚合，门限和 heuristic impact 以各节点时间总和为分母，表内显示本节点占比；Executive Summary 的 Total 是 **node times 的和，非分布式 wall time**。它依赖相邻 `gpu_timeline.csv` 获取每节点时间，对不等长窗口尤其要核对。降级报告只恢复 kernel name/time 等有限项，不能补造 shape、分类或效率，更不能把 heuristic impact 当作实测收益。

官方 split 新增进程内 `split_and_enumerate(...)` / `run(Namespace)`，返回与 execution_details 文件同形的列表，没有提取结果返回空列表；仍会写输出。iteration extraction 同时认可 preferred annotation pattern。现用 HCU fork 是否具有同样 API 需按固定接口确认，不能由函数名相似假定兼容。

experimental capture merge 现在按 target/draft 等 role、batch size、FULL/PIECEWISE 和可用 replay rank 选择 capture；同 key 可有多个文件，SGLang request batch 与 tensor batch 可带 multiplier。先尝试单源位置配对，再按 dispatch count 精确或最近匹配，并按 dominant count 推断 mode。最近匹配是启发式恢复，不能保证 capture 与 replay 真实语义一致；缺 role/batch/源文件、跳过 root、数量差异和 warning/日志必须留作不完整证据。合并后的关联不是原 profiler 已记录的事实，应保存原 trace、capture metadata、匹配方式与失败项。

## 未变机制与验证范围

本轮复核的 collective report/tutorial、compare report/回归、FP4/6 microbench helpers/回归与 `trace_to_tree.py` 固定对象未变；其 rank/group、缺表显式请求、tile 失败与事件关联门禁继续成立。报告接口、MoE 模型、fallback 和 merge 的变化分别按当前源码解释，没有运行上游测试、GPU replay、微基准或真实多节点训练。PR 讨论覆盖以独立采集回执为准，不由本页源码阅读代替。

## HCU 消费方与更新

上游 rocprof、架构预测、回放或 Graph 能力不自动等于 HCU 可用。HCU fork 的部署、API 适配、真实验证和故障处理统一见[工作流集成契约](../../../../../../docs/tracelens-analysis.md)及[外部入口](../../../../../catalog/external/hcu-tracelens.md)，本页不重复维护该 fork 的代码知识。

上游更新时同时检查调用树语义、报告列与单位、shape 处理、回放约束、性能模型和 Agent 输入。通过固定 PR/head/base 追实现，再在集成层核对是否影响现用 HCU fork；不可直接用 upstream HEAD 替换运行依赖。源码阅读和工具资格测试不构成完整训练精度/收敛通过。

- [README.md](https://github.com/AMD-AGI/TraceLens/blob/90f2f6f58210d1828c5eca6949b1dce7d2525fa7/README.md)

- [TraceLens/Agent/Analysis/utils/deterministic_fallback.py](https://github.com/AMD-AGI/TraceLens/blob/90f2f6f58210d1828c5eca6949b1dce7d2525fa7/TraceLens/Agent/Analysis/utils/deterministic_fallback.py)

- [TraceLens/Trace2Tree/trace_capture_merge_experimental.py](https://github.com/AMD-AGI/TraceLens/blob/90f2f6f58210d1828c5eca6949b1dce7d2525fa7/TraceLens/Trace2Tree/trace_capture_merge_experimental.py)

- [TraceLens/TraceUtils/split_trace/main.py](https://github.com/AMD-AGI/TraceLens/blob/90f2f6f58210d1828c5eca6949b1dce7d2525fa7/TraceLens/TraceUtils/split_trace/main.py)

- [TraceLens/Trace2Tree/trace_to_tree.py](https://github.com/AMD-AGI/TraceLens/blob/90f2f6f58210d1828c5eca6949b1dce7d2525fa7/TraceLens/Trace2Tree/trace_to_tree.py)

- [TraceLens/Reporting/generate_multi_rank_collective_report_pytorch.py](https://github.com/AMD-AGI/TraceLens/blob/90f2f6f58210d1828c5eca6949b1dce7d2525fa7/TraceLens/Reporting/generate_multi_rank_collective_report_pytorch.py)
