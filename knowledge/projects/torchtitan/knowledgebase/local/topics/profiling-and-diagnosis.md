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
reviewed_on: '2026-11-18'
retrieved_on: '2026-11-18'
coverage: Curated source chains and official evidence at a fixed main commit; not
  all models, backends or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/observability/profiler.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 190e2e3b42af426de9f89c35f5ab0a38e05ac501da3c41f17bea953e15644ebc
- source: pytorch-torchtitan
  path: torchtitan/observability/METRICS.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: ab58719b87a55a08bc9de86cdd1620905f9bcb99d74fca5260fa68c2a8038f69
- source: pytorch-torchtitan
  path: torchtitan/observability/structured_logger/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 3fd386d188a8ba3245c1ac763c806ae5fa1d44e0b524382a8bca7e129dca0e23
- source: pytorch-torchtitan
  path: torchtitan/trainer.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 1e03e753238c07818a9b238b9264001cd3223528e5d18e4316eb88be14175135
- source: pytorch-torchtitan
  path: torchtitan/distributed/PARALLELISM_CONTEXT.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 7df6f250d92b8a4bf37557a330a571cd4273062fce08a2f3268abfce7ee58916
- source: pytorch-torchtitan
  path: docs/debugging.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 523e0d62eca05f837e9ec4da6530a60e4cd95a8f8f55d7f2a8a0f8b1d542fd49
- source: pytorch-torchtitan
  path: tests/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 73f9a9597a0aaeef657c103ec1cc544375c0e9229f49a9a50abcd8d3a02af248
- source: pytorch-torchtitan
  path: torchtitan/distributed/accelerator_graph.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: dec500ca70df82c8c8388b41e49970cd9dbbdd2a1c287217c4783827b576e9d5
- source: pytorch-torchtitan
  path: torchtitan/components/optim/optim.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: b93bb590ff7c7eec2d1bd9c2668ad668bf3bee1e944fbe6b0e0415b2474e154b
- source: pytorch-torchtitan
  path: torchtitan/models/README.md
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: 898429009818d47980f01d6da03989b6583caac574002b839b4d8a87ed272b2e
- source: pytorch-torchtitan
  path: torchtitan/training_engine.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: ecbe72af3cdf4eba9d8093eb07c6178b2046063e87e574ed0d43f5861ab982ab
- source: pytorch-torchtitan
  path: torchtitan/trainer.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: dea5f4c0c83494e39ca87bfc93b07e125f57b6df31af9802d5fb429cc8d5b011
- source: pytorch-torchtitan
  path: torchtitan/components/optim/optim.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: 30a1535bf4b634d2ed78ed6d57494fcce796322ab15be68e90c3ad22ea5bbf54
- source: pytorch-torchtitan
  path: torchtitan/distributed/accelerator_graph.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: e9d6abb0abcb8d857ba73549d48371107c1b43cfd40c5685fc52d0ef7fe205a6
- source: pytorch-torchtitan
  path: torchtitan/distributed/ACCELERATOR_GRAPH.md
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: 963bae7feb7b5ff0c5e69ed73206e1694fa603fca8002e3d14863531a21a2ee9
- source: pytorch-torchtitan
  path: torchtitan/observability/METRICS.md
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: 34586f9f6e3485b2abd95907db856e69ee897e30e79a3eec31b302d1382909d3
- source: pytorch-torchtitan
  path: tests/unit_tests/cpu/test_trainer.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: 7321283e603f94e5a9df8788a9f4f11d7ed83904aa2054c816e9cddef60bc9be
- source: pytorch-torchtitan
  path: torchtitan/rl/controller/controller.py
  commit: 361ae5df6280e578614026b206d801d6ea1baf98
  sha256: e7111207a551e02c27b80dc4059b354353204dcbfb1d1af6ab54f423212c941b
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

## Cuspy、输出格式与缺失标注

新增 `profiler.cuspy: CuspyProfilerConfig | None`，默认 None 继续 Kineto。启用 Cuspy 要求该 Torch 暴露 CuspyConfig、可用 CUDA/CUPTI 及相应 encoder；不满足会报具体原因。可采 CUDA sync、environment counters、Graph dependency/event node ID 和 PM sampling，均不是 HCU 已支持的采集路径。

`trace_format="json"` 默认输出 `rank<rank>_trace.json.gz`；`"pftrace"` 输出二进制 `rank<rank>_trace.pftrace.gz`，还要求 native Perfetto encoder。TrainFlow 当前 Torch trace/固定 TraceLens 消费者按 JSON 契约工作，不能改扩展名后直接解析 pftrace。PM 指标名需按实机枚举，lookback 要覆盖 warmup+active，否则早期样本丢失；采样间隔/窗口还受配置检查。

`record_py_stacks` 把 capture 时的 kernel Python launch stacks 写为独立 `rank<rank>_cuda_graph_py_stacks.json.gz`，键为 `(graph id << 32) | graph node id`。没有 CUDA graph 或 annotation 能力会警告，缺标注不能解释为没有 kernel；sidecar 不是训练 trace 或调用耗时本身。

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

首次 optimizer update 的已初始化设备等待和 empty_cache 当前排除 XPU；Graph wrapper 不再额外调用 empty_cache，捕获 API 自己执行同步/清理。它们保留live tensor与Graph pool，不能据reserved短时下降推导模型常驻量减少。Graph 的 DEBUG memory 日志按当前仍保留的 wrapper boundary 记录allocated/reserved/active/inactive_split、peak和设备free；这些字段的层次不同，采样需对应同一阶段。wrapper命名可区分forward_backward、optimizer、validation，annotation由profiler导出路径消费。

共享eval pool可能使warmup阶段额外执行validation并延后训练capture；性能窗口同时保存capture/warmup状态与validation次数。当前profiler另为Neuron加入PrivateUse1活动和with_stack，不能把该分支误当作HCU已获得新的profiler后端；HCU证据仍按现场Torch/DTK采集链确认。

## 固定证据与使用边界

本页保留官方 `485c065cb248863bf2e2c65588becd6d7a8bcf83` 的固定历史证据；2026-11-18 新实现按 `361ae5df6280e578614026b206d801d6ea1baf98` 逐项复核，见本页增量。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/observability/profiler.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/observability/profiler.py)
- [torchtitan/observability/METRICS.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/observability/METRICS.md)
- [torchtitan/observability/structured_logger/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/observability/structured_logger/README.md)
- [torchtitan/trainer.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/trainer.py)
- [torchtitan/distributed/PARALLELISM_CONTEXT.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/PARALLELISM_CONTEXT.md)
- [docs/debugging.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/docs/debugging.md)
- [tests/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/README.md)

## 本次补充的实现与测试依据

- [torchtitan/distributed/accelerator_graph.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/accelerator_graph.py)
- [torchtitan/components/optim/optim.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/components/optim/optim.py)


## 2026-11-18 固定主线复核

按 `361ae5df6280e578614026b206d801d6ea1baf98` 的实际消费者和来源测试设计复核：

MFU 改为基于实际原始 microbatch 的逻辑 FLOPs，取完整模型、在 DP mesh 平均而不重复 CP；不包含 causal sparsity、重算与 elementwise。未知硬件峰值时不再强行格式化为一个数，不能借相似型号补值或把统计变化当 kernel 加速。loss/validation metrics 也按当前 sum/max 与有效 token 口径归约，比较历史日志先对齐定义。

首次 Optim.step 现跳过 XPU 的 sync/empty_cache；Graph wrapper 删除捕获前重复显式 empty_cache，由 capture API 自己同步/清未用缓存。Trainer.train 异常将原异常传给 close_profiler，OOM 及 PP 包装的 OOM 可生成退出内存快照；正常关闭不伪造 OOM。已读 CPU 回归设计，未执行该上游测试或设备采集。

W&B 横轴使用 `trainer/step`，其 `_step` 只计 log calls；同一训练 step 的训练/validation 可以占多行。`WANDB_RESUME_FROM/FORK_FROM` 的 `_step=N` 是日志行号，不能直接填训练步号。RL 的并行 validation 还记录 `validation/started_at_step`，完成时才记日志且期间权重可变，需保留策略范围与额外生成负载。

固定入口：[torchtitan/models/README.md](https://github.com/pytorch/torchtitan/blob/361ae5df6280e578614026b206d801d6ea1baf98/torchtitan/models/README.md)；[torchtitan/training_engine.py](https://github.com/pytorch/torchtitan/blob/361ae5df6280e578614026b206d801d6ea1baf98/torchtitan/training_engine.py)；[torchtitan/trainer.py](https://github.com/pytorch/torchtitan/blob/361ae5df6280e578614026b206d801d6ea1baf98/torchtitan/trainer.py)。本次未安装或运行上游测试/训练，没有 HCU 设备实测结论。
