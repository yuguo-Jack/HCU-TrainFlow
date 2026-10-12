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
reviewed_on: '2026-10-12'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime
  execution
sources:
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/pipe/engine.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 211edb569ad0dc1c1b830c818a0ea15b64e22986c4840468af73304d825c8ae3
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/pipe/schedule.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 52aae5310aa18183d093149dd12cb20b02e6a8143e906bd32cf4fcdb96542a6b
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/engine.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 2ff52b1d128f42e49b9a01d2b95b18bd83285af60db4ce01baaa5c078c5920ca
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/config.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: cf8beb53835f192afdf5a0c8a4b5bbf3fb09d1fdc767a0f46f66b1cdf38c650a
- source: deepspeedai-deepspeed
  path: docs/_tutorials/pipeline.md
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: da381a5d2a222855c15adbdc3d2fc3b5f6f35fb0af19799b9ccb4b7e4e5a89ba
- source: deepspeedai-deepspeed
  path: docs/_tutorials/universal-checkpointing.md
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 61d4c532cc607d6d9283d36ffa83ea35da606ff4de9d7a9bc59625a88c5fe0ce
- source: deepspeedai-deepspeed
  path: docs/_tutorials/getting-started.md
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 8494b298115871b4d5d2b0e72132123bcfb703768678ca726d51cc62b6c4c05e
---

# DeepSpeed Pipeline：1F1B、batch、activation 与 checkpoint

## 入口和重要限制

`deepspeed.initialize(model=PipelineModule(...))` 返回 [`PipelineEngine`](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/deepspeed/runtime/pipe/engine.py)，使用 `train_batch(data_iter=...)` 推进一个 optimizer batch。普通 `forward/backward/step` 在该 engine 中有明确限制，不能保留外部 Trainer 的普通循环再加 pipeline schedule。

当前初始化断言 **ZeRO stage 必须小于 2**，即官方 PipelineEngine 不支持 ZeRO-2/3。别的训练引擎能够组合 PP 和分片，不代表这里也支持。它主动关闭父类 backward allreduce，由 pipeline schedule 在合适位置执行归约。

`micro_batches = gradient_accumulation_steps`，并要求：

`train_batch_size = train_micro_batch_size_per_gpu × micro_batches × pipeline grid 的 DP size`。

PP/TP rank 不增加独立训练样本，不用总 world size 代替 DP。改变 global batch 可能改变优化器行为和 loss 曲线；若只调执行粒度，用允许的 microbatch/accumulation 组合保持样本契约。

## 1F1B 调度如何执行

[`TrainSchedule.steps`](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/deepspeed/runtime/pipe/schedule.py)采用同步 1F1B，`total_steps = 2 × (micro_batches + stages − 1)`；stage 奇偶与 step 奇偶映射到不同 microbatch 的 forward/backward。一个调度步由原子命令序列组成，调度注释的契约是各 step 之间允许插入 barrier 而不死锁。

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

[Universal 教程](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/docs/_tutorials/universal-checkpointing.md)的路径是先 `save_checkpoint`，用 `deepspeed/checkpoint/ds_to_universal.py --input_folder ... --output_folder ...` 转换，再设置 `checkpoint.load_universal=true` 后加载。遵循所用版本对优化器、TP/PP/DP 与模型 metadata 的要求，恢复后比较下一步 loss、梯度和参数更新。

当前教程还解释 AutoTP/AutoEP：row/column/replicated、fused/QKV 子参数等要提供对应布局元数据。AutoEP stage 1/2 的 routed expert 权重与 stage 3 的 partition-native 格式不同；**partition-native AutoEP 不能用 `zero_to_fp32.py` 当作通用导出路径，应按教程用 `ds_to_universal.py`**。跨 DP/EP 恢复仍要求兼容的 expert 数量、权重名称/布局和恢复模式，不推断支持任意结构变更。

## 验证、诊断和更新

验证执行入口、两 stage 以上的真实通信、tied grads、多个 microbatch、变序列形状、保存恢复继续一 batch。PP 空泡先分辨调度固有成本与 stage 不均；卡住先核对 rank 配方一致、发送接收的顺序/shape，不盲目调更大的通信 timeout。

本页阅读官方[Pipeline 教程](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/docs/_tutorials/pipeline.md)、当前 engine/schedule 和恢复文档，未执行 HCU PP 测试。schedule/ZeRO 兼容或 checkpoint metadata 改动时，联动[总览](../overview/engineering-guide.md)、[ZeRO 专题](zero-state-lifecycle.md)和调用方启动配置。
