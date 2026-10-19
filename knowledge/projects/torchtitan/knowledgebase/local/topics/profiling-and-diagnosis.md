---
id: official-torchtitan-wiki/profiling-and-diagnosis
title: TorchTitan 性能采集、TraceLens 联动与问题定位
engine: torchtitan
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-20'
coverage: Curated source chains and official evidence at a fixed main commit; not all models, backends
  or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/observability/profiler.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 6132d3da9f53a8aa5d8ca389dd65dcb59bf12c44bb5b1ad71a54fc52dc97646a
- source: pytorch-torchtitan
  path: torchtitan/observability/METRICS.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: b65315a4ad2ca68234e7b84bf5a6f4628fa993097830e462cb65176adbf089a8
- source: pytorch-torchtitan
  path: torchtitan/observability/structured_logger/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 3fd386d188a8ba3245c1ac763c806ae5fa1d44e0b524382a8bca7e129dca0e23
- source: pytorch-torchtitan
  path: torchtitan/trainer.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: c49922cf3d47918901135fc0b798141479cb16b24fb1004b19b255a663c13288
- source: pytorch-torchtitan
  path: torchtitan/distributed/PARALLELISM_CONTEXT.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 7df6f250d92b8a4bf37557a330a571cd4273062fce08a2f3268abfce7ee58916
- source: pytorch-torchtitan
  path: docs/debugging.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 0938badc6722b624d4c07d6e2a620c02fa9cf4bb0e7b26b9d5de77c8b0586b0a
- source: pytorch-torchtitan
  path: tests/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 0872f733f18e85e085802fff3813cd1ee359ec1cc10b8d5929642e62d4c4e712
- source: pytorch-torchtitan
  path: torchtitan/distributed/cuda_graph.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 29822760e2d35f6e816ae0b9655483b0ac366ff2a111bfc208bf6440e0b326b7
- source: pytorch-torchtitan
  path: torchtitan/components/optim/optim.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 6303e04a5cac5781d3b9ac76fafb9ceaf509824b84e189d2aa1362f3cf3ffe24
---
# TorchTitan 性能采集、TraceLens 联动与问题定位

## 建立可解释的测量窗口

先保存固定源码、有效 recipe、设备/互联、各并行域与 rank 成员、microbatch/accumulation/global token、精度、checkpoint 和 validation 周期。冷启动、编译/调优、首步内存分配与真实稳态分开统计。

Trainer 的 metrics 窗口会绕开一些 checkpoint/validation 开销；因此日志中的 tokens/s 不等于包含保存、验证、故障与重启的任务总吞吐。性能报告同时记录定义明确的稳态 step time 和任务有效训练进度，比较时不能换分母。

## Profiler 的实际参数

当前 `Profiler.Config` 中主要字段：

| 字段 | 含义/当前默认 |
| --- | --- |
| `enable_profiling` | 默认 False；显式开启 |
| `profile_freq` | 默认 10；必须覆盖 warmup + active |
| `profiler_warmup` / `profiler_active` | 默认 3 / 1 |
| `profiler_repeat`、`profiler_skip_first`、`profiler_skip_first_wait` | 控制重复采样与跳过阶段，按版本核对 |
| `save_traces_folder` | 默认 `profiling/traces` |
| `enable_memory_snapshot` | 另行开启显存历史/快照 |
| `memory_snapshot_freq`、`memory_snapshot_max_entries` | 控制快照周期与历史容量，不宜无界记录 |

在 Python recipe 中配置这些字段，不把旧版 CLI 名称机械加到启动命令。输出通常为 `<dump_folder>/profiling/traces/iteration_<step>/rank<rank>_trace.json.gz`。`LOG_RANK` 是 stdout 过滤，不能当作 profiler rank 采样开关。

每个实际存在的并行域选择至少两个具有代表性的 rank，并覆盖可能慢的 stage、专家和节点；资源只有一个成员时注明不可比较。保持同一迭代窗口、真实 rank map 与采样负载，避免把不同轮次的 trace 直接叠加。

## 与 TraceLens 和算子流程衔接

1. 保存原始 trace 与环境上下文；由 TrainFlow 的 Torch trace / TraceLens 入口解析，保留压缩原件。若具体工具只接收解压 JSON，解压到任务缓存，不重复登记共享 Wiki。
2. 先建立 CPU 发起、GPU kernel/copy、通信、同步与跨 rank 依赖时间线，识别关键路径和负载不均。不能把所有 kernel duration 简单相加当作端到端墙钟。
3. 空泡最大先查数据、Python/编译、同步和 CPU；通信最大先比同拓扑/数据量单测，再分析 overlap、通算融合或不均衡；计算最大按贡献排序。
4. 对累计覆盖主要 GPU 工作量的热点建立 shape、dtype、布局、FLOPs、实际字节与 ceiling，明确是设备理论上限还是现场实测可达值。非通信计算热点的覆盖目标与端到端 wall-clock 口径同时保留。
5. 用同 shape 基准判断模型内是否显著拖慢；调用次数、warm/cold cache、并发、量化/重算与复制必须可比。kernel 上限不由 aggregate MFU 直接得出。
6. 查官方 PR/源码和 HCU-Knowledge 中可复用实现；迭代后以同基线重采，做局部正确性和阶段 loss 验收。

TorchTitan 自带 MFU/峰值表面向它支持的卡型；HCU 应使用已核实型号、精度算力、HBM/互联的现场参数，不能借相近 NVIDIA/AMD 型号代填。

## 诊断表

| 现象 | 核查步骤 |
| --- | --- |
| 偶发长 step | 对齐数据读取、编译、GC、checkpoint、validation、网络与磁盘时间戳，再看慢 rank |
| 某 rank 不前进 | 栈/collective 序列、实际 group、Flight Recorder、异常退出和超时；先定位首个事件 |
| OOM 或内存持续增长 | allocated/reserved、FSDP/quant cache、PP 在途发送、保存张量、graph pool、checkpoint staging；用快照比生命周期 |
| fake 跑通而真多卡失败 | 对照真实 reduction、tensor aliasing、collective 顺序；fake 不替代精度和网络验证 |
| 配置已开但无预期 kernel | 查 transform、backend selector、硬件条件、实际 trace 和 fallback |

`pdb` 断点落在被 LOG_RANK 过滤的进程可能表现为卡住却无提示。显存 snapshot 和 trace 会较大，只在有效窗口采集，并按工作流阶段清理失效缓存；保留支撑结论和恢复的证据。

## 当前启动/捕获窗口的额外事件

首次optimizer update有一次CUDA等待和empty_cache；每个Graph wrapper首次capture前也释放未使用缓存。它们保留live tensor与Graph pool，不能据reserved短时下降推导模型常驻量减少。Graph的DEBUG memory日志按wrapper name与boundary记录allocated/reserved/active/inactive_split、peak和设备free；这些字段的层次不同，采样需对应同一阶段。wrapper命名可区分forward_backward、optimizer、validation，annotation由profiler导出路径消费。

共享eval pool可能使warmup阶段额外执行validation并延后训练capture；性能窗口同时保存capture/warmup状态与validation次数。当前profiler另为Neuron加入PrivateUse1活动和with_stack，不能把该分支误当作HCU已获得新的profiler后端；HCU证据仍按现场Torch/DTK采集链确认。

## 固定证据与使用边界

本页以官方主线 `a242475253433725f10f39c18f5ccbfdf188e097` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/observability/profiler.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/observability/profiler.py)
- [torchtitan/observability/METRICS.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/observability/METRICS.md)
- [torchtitan/observability/structured_logger/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/observability/structured_logger/README.md)
- [torchtitan/trainer.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/trainer.py)
- [torchtitan/distributed/PARALLELISM_CONTEXT.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/PARALLELISM_CONTEXT.md)
- [docs/debugging.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/docs/debugging.md)
- [tests/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/README.md)

## 本次补充的实现与测试依据

- [torchtitan/distributed/cuda_graph.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/cuda_graph.py)
- [torchtitan/components/optim/optim.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/components/optim/optim.py)
