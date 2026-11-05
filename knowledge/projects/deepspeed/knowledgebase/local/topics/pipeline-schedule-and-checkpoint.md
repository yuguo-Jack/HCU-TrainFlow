---
id: engines/deepspeed/topics/pipeline-schedule-and-checkpoint
title: DeepSpeed Pipeline：1F1B、batch、activation 与 checkpoint
engine: deepspeed
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-11-04'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime execution
sources:
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/pipe/engine.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 74fe2ff16f84ad51ac3f85be5a85938c9fa482c076df29f4edb22e7d24be7cc8
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/pipe/schedule.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 52aae5310aa18183d093149dd12cb20b02e6a8143e906bd32cf4fcdb96542a6b
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/engine.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: cd28c8d864e789c07cbcb80c6275e885fd8f409d90497084e0376935fcb10204
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/config.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 982bc8974c4a70665f1450dd96f843454626eb95aeebe5887305ac6e48548743
- source: deepspeedai-deepspeed
  path: docs/_tutorials/pipeline.md
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: da381a5d2a222855c15adbdc3d2fc3b5f6f35fb0af19799b9ccb4b7e4e5a89ba
- source: deepspeedai-deepspeed
  path: docs/_tutorials/universal-checkpointing.md
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 61d4c532cc607d6d9283d36ffa83ea35da606ff4de9d7a9bc59625a88c5fe0ce
- source: deepspeedai-deepspeed
  path: docs/_tutorials/getting-started.md
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: c5df6860cecad9a8f1840e921ea460570d5c37bd140d39542760bc9d4e1bad01
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage_1_and_2.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 0dd8a8c856a90e2aa0dae70d8d03f961d1b346800fdcabbf8e29ed149aec8bd8
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage3.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 64f3afdbacb757b0d8c0a9c08a4b6b6958b0bcbf597fd2eebd5a5c47821701cd
- source: deepspeedai-deepspeed
  path: tests/unit/checkpoint/test_fp32_master_only.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: a34af0cfe6a58b63d750cdd9931bd742444b3bede860817c61dfc1395f4a9c28
---

# DeepSpeed Pipeline：1F1B、batch、activation 与 checkpoint

## 入口和重要限制

`deepspeed.initialize(model=PipelineModule(...))` 返回 [`PipelineEngine`](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/deepspeed/runtime/pipe/engine.py)，使用 `train_batch(data_iter=...)` 推进一个 optimizer batch。普通 `forward/backward/step` 在该 engine 中有明确限制，不能保留外部 Trainer 的普通循环再加 pipeline schedule。

当前初始化断言 **ZeRO stage 必须小于 2**，即官方 PipelineEngine 不支持 ZeRO-2/3。别的训练引擎能够组合 PP 和分片，不代表这里也支持。它主动关闭父类 backward allreduce，由 pipeline schedule 在合适位置执行归约。

`micro_batches = gradient_accumulation_steps`，并要求：

`train_batch_size = train_micro_batch_size_per_gpu × micro_batches × pipeline grid 的 DP size`。

PP/TP rank 不增加独立训练样本，不用总 world size 代替 DP。改变 global batch 可能改变优化器行为和 loss 曲线；若只调执行粒度，用允许的 microbatch/accumulation 组合保持样本契约。

## 1F1B 调度如何执行

[`TrainSchedule.steps`](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/deepspeed/runtime/pipe/schedule.py)采用同步 1F1B，`total_steps = 2 × (micro_batches + stages − 1)`；stage 奇偶与 step 奇偶映射到不同 microbatch 的 forward/backward。一个调度步由原子命令序列组成，调度注释的契约是各 step 之间允许插入 barrier 而不死锁。

- 首/末 stage 在需要时 `LoadMicroBatch`。
- forward slot 安排 `SendGrad`/`RecvActivation` 和 `ForwardPass`；backward slot 安排 `RecvGrad`/`SendActivation` 和 `BackwardPass`。
- 启动与排空阶段会有无效 microbatch slot，不能把它们当作 CPU 瓶颈。
- 最后一调度步执行 `ReduceTiedGrads`、`ReduceGrads`、`OptimizerStep`，保证 tied parameters 和 DP 更新的位置一致。

实际命令由 engine 对应 `_exec_*` 执行。PP 卡住需要看两端命令序列、tensor shape/dtype 与各 rank schedule，而不仅是最后一条通信 API。

## activation 驻留与吞吐权衡

`TrainSchedule.num_pipe_buffers` 返回 `max(2, min(stages − stage_id, micro_batches))`，反映 1F1B 中尚未完成 backward 的 forward activation 数；它不是“每层固定两个 activation”或“完整模型显存公式”。输入输出 buffer、模型中间结果、重算、通信 staging 和 allocator 保留也占空间。

增加 micro_batches 可降低 pipeline 启动/排空占比，增加微批内工作量可能改善 GEMM，但各自受 stage 内 activation、序列长度、负载均衡、全局 batch 和 step 延迟约束。比较至少一对同 global batch 的配置，记录各 stage 最长计算、send/recv、idle 和 peak，而不是只看平均 kernel 时间。

`set_train_batch_size` 可在相同 micro batch 与 DP 条件下重算 gradient accumulation，要求整除。可变序列 shape 需要检查 `reset_activation_shape` 清除通信/activation 缓存；不能把第一次形状的 buffer 沿用到新形状。激活重算应与模型分段和 RNG 契约一同验证。

## 保存、导出与改变拓扑

三类产物职责不同：

1. **engine checkpoint**：续训所需的分片模型、optimizer、scheduler 与计数等，所有需要参与的 rank 同步保存/加载；数据 cursor/RNG 的完整范围还要查调用方。
2. **完整模型权重导出**：为推理或迁移收集 state_dict；它可能提高保存峰值，也可能不包含训练状态。
3. **Universal Checkpoint 转换**：将受支持布局转换后，在限定条件下改变并行配置，不是任意模型/权重名称翻译器。

[Universal 教程](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/docs/_tutorials/universal-checkpointing.md)的路径是先 `save_checkpoint`，用 `deepspeed/checkpoint/ds_to_universal.py --input_folder ... --output_folder ...` 转换，再设置 `checkpoint.load_universal=true` 后加载。遵循所用版本对优化器、TP/PP/DP 与模型 metadata 的要求，恢复后比较下一步 loss、梯度和参数更新。

当前教程还解释 AutoTP/AutoEP：row/column/replicated、fused/QKV 子参数等要提供对应布局元数据。AutoEP stage 1/2 的 routed expert 权重与 stage 3 的 partition-native 格式不同；**partition-native AutoEP 不能用 `zero_to_fp32.py` 当作通用导出路径，应按教程用 `ds_to_universal.py`**。跨 DP/EP 恢复仍要求兼容的 expert 数量、权重名称/布局和恢复模式，不推断支持任意结构变更。

### 恢复模式与 FP32 master 来源

2026-11-04 复核 `d8241a9ba266405e1a58fadf19e24b2370f6d7fa` 的 `DeepSpeedEngine.load_checkpoint`、stage1/2和stage3消费者，模式应明确记录：

| 模式 | 当前权重/状态来源 |
| --- | --- |
| 完整ZeRO，加载optimizer | 必须读取保存的FP32 master与optimizer状态 |
| 完整ZeRO，`load_optimizer_states=False` | 仍读保存的FP32 master，optimizer moments等保持新建状态；scheduler开关另行控制 |
| `load_module_only=True`，native ZeRO-1/2 | 从已载模型权重重建FP32 master；不是完整续训 |
| module-only，Universal ZeRO-1/2 | 先从Universal FP32读模型，再刷新master |
| module-only，ZeRO-3 | 模型文件没有全部partition参数，仍读保存FP32分片 |

`zero_optimization.load_from_fp32_weights`现已deprecated，Engine忽略该值并在需要ZeRO分片时传True。缺失native分片或Universal FP32文件硬失败，不再静默从低精度回填。NVMe恢复且不载optimizer时仅拷各master的FP32 swap文件，避免把旧optimizer状态一起带回；恢复前也核对所有swap路径、空间与参与rank。

native DP数变化仅允许elastic ZeRO-1/2、checkpoint本身非rigid且不加载optimizer状态，读取所有保存分片后重分配FP32权重；ZeRO-3和带optimizer的native resize被拒绝。Universal仍受模型/布局metadata约束。相同step、相同输入的恢复对照要区分这些模式，关闭optimizer后下一步更新自然可能不同，不能宣称无损续训。

已阅读新增 [`test_fp32_master_only.py`](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/tests/unit/checkpoint/test_fp32_master_only.py)：用 ZeRO-2/BF16 和 CPU/Gloo，将保存 master 改为不落在 BF16 网格的值，分别断言完整 no-optimizer 保留精确 FP32、module-only 使用低精度模型值、缺分片完整加载报错；另覆盖 DP2→DP1 的 Universal 与 native elastic 限制。它验证的设计边界不是所有 ZeRO-3/NVMe/模型布局的运行结论，本轮没有执行这些上游测试。

PP的 `TrainSchedule.steps/num_pipe_buffers` 和ZeRO<2兼容断言未变；本轮pipe engine只把吞吐timer换成 `elapsed_total(reset=True)`。历史吞吐对照需核对累计窗口，不能把计时口径变化误判成1F1B调度优化。

## 验证、诊断和更新

验证执行入口、两 stage 以上的真实通信、tied grads、多个 microbatch、变序列形状、保存恢复继续一 batch。PP 空泡先分辨调度固有成本与 stage 不均；卡住先核对 rank 配方一致、发送接收的顺序/shape，不盲目调更大的通信 timeout。

本页阅读官方[Pipeline 教程](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/docs/_tutorials/pipeline.md)、当前 engine/schedule 和恢复文档，未执行 HCU PP 测试。schedule/ZeRO 兼容或 checkpoint metadata 改动时，联动[总览](../overview/engineering-guide.md)、[ZeRO 专题](zero-state-lifecycle.md)和调用方启动配置。
