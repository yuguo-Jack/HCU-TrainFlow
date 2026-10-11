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
- source: hcu-tracelens
  path: README.md
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: a6624439b1ab85f4e6cf216da384883e5b4e9c1a18f733362394d72bb750851e
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/category_analyses/analysis_utils.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: f539e231ca20da216506091a9b5f6c0952ebb8d5fefa285a24ee294f49428321
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/category_analyses/cpu_idle_analysis.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 478a5d857c5c32aaecf8591d0789ddd4ce5370ec291a07343ae0f48f897c8e07
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/category_analyses/kernel_fusion_analysis.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: e96847adaeee88eb407021966901350273b21451f5dd5e0ca402d4dc74dd341a
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/skills/analysis-orchestrator/agents/kernel-fusion-analyzer.md
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: ec0c96b54943df67d4cc52f3c6d49ee183aa960f214d6c4042160a999474638d
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/skills/analysis-orchestrator/reference.md
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: c4c148a26a4d38f12bb6987a0b78fdd17465cb0a5fa4d483e302996d38d012ca
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/utils/arch_utils.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: aa963ed5f17c01bf4fce4d1718cb7c02e5658c10f7ac21d5d1d1e62aed24ef3e
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/utils/artifact_bindings.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 7c29807ad0f5452598d9f6ce029aae80903f80fbd89bd423f3705e549f5d5a9f
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/utils/deterministic_fallback.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 8fa877065e24b81512ee67f8d57d5424a95ddcfc0851a501828713e44c536935
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/utils/hcu_analysis.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 90e30f678f53d0be4a328f5ff7692c0ee5c8ffe04447639bfb249fb2ac0904e1
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/utils/orchestrator_prepare.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: b1499c00c3ee48ff52e4437401f6b996449532eb21aa2f4844df5d6d94064950
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/utils/report_utils.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: de4ba36ecd20d80e8c43be2d2c0592e027e3f1c3e3e8c7193690b84789c49a7b
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/utils/validation_utils.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 88a383c3041e5570b602b9d8e7d5b384674f009f9bbade6e06a4eb5545aeab47
- source: hcu-tracelens
  path: TraceLens/EventReplay/batched_replay.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 9d1008a52143659c1f1ad65be21281ca1552ae7e351e465cadbca876a79b9592
- source: hcu-tracelens
  path: TraceLens/EventReplay/event_replay.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 57e2b4c576c8786cdcc904dbb20d2d984bae66a14981029c2b29a31ede784b23
- source: hcu-tracelens
  path: TraceLens/EventReplay/hcu_replay.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 1bf047cbcaf7363cc1901e90763b73c554f5b15de951d2ee148f7b3709e60f3c
- source: hcu-tracelens
  path: TraceLens/EventReplay/safety.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: e8ed4659e39beb4e9d6635ec4f7758d8514e9bd874c1d71f95f2d6fa6658bb46
- source: hcu-tracelens
  path: TraceLens/EventReplay/utils.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 3dd2c1593d74898b561137c2c7a3153dad0dc64e53db8b6c8421ad9c41e46c19
- source: hcu-tracelens
  path: TraceLens/PerfModel/hcu_roofline.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 5dca9f9203c7978920c7a3b550fdf519f5f10a332f117de21a1c8edf9d21a5fc
- source: hcu-tracelens
  path: TraceLens/Reporting/generate_multi_rank_collective_report_pytorch.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 0566e1ecf0606f7f39e22e99d1c264ea104ebee65f8e574b48d98f178338adf3
- source: hcu-tracelens
  path: TraceLens/Reporting/generate_perf_report_pytorch.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 1027bf63be0cbd1dc053c905256639e5cc870a61b0278a0669aaf7ede414ead0
- source: hcu-tracelens
  path: TraceLens/Reporting/generate_perf_report_pytorch_inference.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: a3c0214030e876e68d6333e61ee740b03c78dd5799bd4c36fe7e6177b8dffdeb
- source: hcu-tracelens
  path: TraceLens/Reporting/hipprof.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: d98377d7ce70820c70c96b056366fa11e0a45b013d7ccaf9302c5042b4888147
- source: hcu-tracelens
  path: TraceLens/Reporting/pftrace_utils.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 3f9c8911f4257b82904491691578eb43a8b123c89689dc008ddcf6f9116acbcc
- source: hcu-tracelens
  path: TraceLens/Reporting/reporting_utils.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 611d84a8e8fa0c3ec23e83cd80cd84cda80471059749bbd806843edfbda92e76
- source: hcu-tracelens
  path: TraceLens/Reporting/xcompute.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 7e94a700ed7b30764f970e11479838f512b40220425b3a8d762047adc182a2d1
- source: hcu-tracelens
  path: TraceLens/Trace2Tree/trace_capture_merge_experimental.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: fb648f3102d343d5abdeaf89146b8ebb48ae4d0d81aa176ba087252a0767730a
- source: hcu-tracelens
  path: TraceLens/Trace2Tree/training_graph.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: d04f4709cb67accd1173295a8349079db0fc55bb10ed99c0d095863d9cfdc26a
- source: hcu-tracelens
  path: TraceLens/util.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: bca3b6f6c47f81c280df6f10befd52cad965ad9ef5c49dfd7c1e06a90ae4700f
- source: hcu-tracelens
  path: docs/hcu-integration.md
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: d8ef02421a13654ac7c6d87cb76d5c007c4b2ffbdcd7eb2e6b7d7f45ffc2d74c
- source: hcu-tracelens
  path: docs/how-to/hcu-graph-replay.md
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 26e52400eb7aeb07902d9b05a862ad20f1170b1c340e2b4d59da924a5489b1c1
- source: hcu-tracelens
  path: docs/how-to/hcu-roofline-agent.md
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 6bd1d5d18d84512755a2aa192bf02df13d1d96b49442ec1f16e31eae77489928
- source: hcu-tracelens
  path: docs/how-to/hcu-xprof-xcompute.md
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 4dec462f3efce61148f2283fca02ab924e6bcf30f4289867db46dd8cb1ec3dec
- source: hcu-tracelens
  path: setup.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 29d8f29499f4a8f4a5fc2c0aa6407d6f400a7c5bfdfb3ba2be274aff493fc253
- source: hcu-tracelens
  path: tests/platform/test_portability.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: eb580b92dedaa3675a67db14538bad7e631dfa8652b24e55354d3709963d01ad
- source: hcu-tracelens
  path: TraceLens/Trace2Tree/trace_to_tree.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 94eafd161d869c99c71d555248e47dd90207f13631374306f9b94b559729b5f8
- source: hcu-tracelens
  path: TraceLens/TreePerf/tree_perf.py
  commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
  sha256: 4234bf731724742d9c480ca909f8fc8b6ae905f9c37c8a0df4e746744af329c9
---

# TraceLens：HCU 训练分析与算子验证

## 定位与代码结构

TrainFlow 锁定 `yuguo-Jack/TraceLens` 的 HCU fork，同时保留 AMD 上游基线。`Reporting/` 提供原生报告和输入适配；`Trace2Tree/` 负责调用树和训练 Graph 归因；`TreePerf/` 汇总 op/kernel/overlap；`PerfModel/` 提供工作量及条件模型；`EventReplay/` 重放有明确输入契约的 ATen 调用；`Agent/Analysis/` 准备类别、计算指标、校验 findings 和分析报告。上游 `TraceDiff`、通信、JAX、rocprofv3 等模块仍保留。

安装和日常使用见[依赖集成](../../docs/integrations.md)；功能选择、真实验证范围和完整命令见[HCU 分析契约](../../docs/tracelens-analysis.md)。运行代码来自固定依赖 checkout，修改在独立开发目录，不能把知识库源码缓存当开发分支。

## 已接入能力

| 能力 | 当前接口与关键实现 | 使用边界 |
| --- | --- | --- |
| 原生 Torch / collective 报告 | `tracelens-report`、`tracelens-collective`；原 report API | 完整通信组、真实 metadata、显式训练窗口；GPU 时间和不等于墙钟 |
| HCU Roofline | `tracelens-analyze` roofline；`PerfModel/hcu_roofline.py` | 实际设备与校准来源；逐 shape/dtype 模型；unknown 保留；条件 gap 不宣称 E2E speedup |
| 训练 Graph | graph 模式；`Trace2Tree/training_graph.py` | 哈希绑定、显式 annotation、serialized single stream；前反向调用可恢复，GPU 时间来自 replay |
| EventReplay | `EventReplay/hcu_replay.py` | 实际张量/schema/trace 绑定与数值比较；复杂训练状态、通信和 RNG 使用专用测试 |
| 原生 Agent | agent 模式；`Agent/Analysis/utils/hcu_analysis.py` | 指标生成后由活跃 Agent 查证和写报告；缺 metrics/findings/实际推理不能叫分析完成 |
| hipprof / pftrace | hipprof 模式；`Reporting/hipprof.py` | DTK 格式适配，精确 ns、pid/index、copy/memset；未知 ATen shape 不补造 |
| XProf / XCompute | counters 模式；`Reporting/xcompute.py` | 保存计数器和 SQTT 原语义/N/A/单位；同 perf 内绑定 dispatch，额外 replay 不当正式性能 |

## 分析如何进入优化流程

先按实际端到端主耗时分流。TraceLens 提供细节证据，TrainFlow 保留当前窗口、并行域、显存、数值状态、90% 热点集合及后续责任人。自动 HCU 模型的未知高占比项继续建模；已经融合的算子也继续评估当前效率。

实际需要优化时，按源码/backend 选择已有 HCU 实现、数学库 tune 或 HIP/Triton Skill；缺初版用 baseline Skill。EventReplay 与同调用实验区分模型内干扰和实现差距，XProf/XCompute/ISA 解释算子瓶颈；最后用 profiler-off 配对及阶段 loss 验收益。不能将同步微基准的空泡直接解释成生产训练 CPU 瓶颈。

## 实测与未验证范围

在 BW1000_H/gfx936、DTK26.10、Torch2.11.0/HIP7.2.26365 上完成了有界工具验证：真实前反向 Graph、captured-value mm Replay、FP32/BF16/copy 校准、原生类别分析与 Agent findings、hipprof JSON/pftrace 同源表一致、XProf3.16.0+aqlprofile3.6.2 counter/SQTT 及 XComputeLight4.8.0 解析。原件在任务私有证据中，方法与范围在上述分析契约中。

这不覆盖所有 gfx/DTK、复杂并发 Graph、任意有状态 replay、GUI、Origami 硬件预测或所有原生 JAX/rocprof 格式，更不等于完整训练 loss/收敛通过。整页保留 `runtime_validated: false`，避免把部分实测泛化为全部接口验证。

## 更新与维护

HCU fork 的改动已超过最初 Windows CSV 修复，包括 HIP 类别、训练 Graph、回放契约、HCU 模型与 Agent、DTK 输入解析。维护时核对 fork 和 upstream，检查函数签名/输出列/单位/缺失项语义，重跑固定原件和失败路径；上游有等价实现时经回归再移除本地补丁。

`thirdparty/manifest.json` 的 `dependency_sources` 将当前 TraceLens commit 关联到本页、来源基线、目录清单和固定文件证据。校验器可阻止依赖已升级而当前 Wiki 留旧基线；历史页仍可保留旧提交。结构校验不证明正文语义正确，工具升级仍须一起复核总览、专题、案例、Skill、解析器及安装副本。
