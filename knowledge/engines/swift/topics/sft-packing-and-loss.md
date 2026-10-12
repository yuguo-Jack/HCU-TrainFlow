---
id: engines/swift/topics/sft-packing-and-loss
title: ms-swift SFT：packing、序列并行与 loss 归一化
engine: swift
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
- source: modelscope-ms-swift
  path: swift/pipelines/train/sft.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 744ceb388ae51f3f50f95f9ceb208980696ba95eaa1f01aaabb0584bd78515b6
- source: modelscope-ms-swift
  path: swift/template/base.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 212b92b190bed8c2c987864ffa93a1cd3a9e45ffa6ba19736e42b7bd88d9c4e4
- source: modelscope-ms-swift
  path: swift/trainers/seq2seq_trainer.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 4bb65c60321cd619dd44a530e1b228ce470c625a9134666758c21d1337f79163
- source: modelscope-ms-swift
  path: swift/sequence_parallel/utils.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 063c86a51d702286bd809533c90c1e44f2538bbe7d55f88d8d20b95bec3945a9
- source: modelscope-ms-swift
  path: swift/megatron/trainers/trainer.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: b7efa15ead7a4f049495c4a0639c27edf6b99bddf9795c47c178a555cbcbf6dc
- source: modelscope-ms-swift
  path: tests/train/test_chunked_cross_entropy.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: dfca2f2e3787ecbdaa555129d59dc2cb03e70c0f704432fa34f4af86fd8288a5
- source: modelscope-ms-swift
  path: tests/train/test_trainer_partial_accumulation.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: dfeaa1943e3d70e1ffe458b547b11ce8d92d1fab2a08e033cde47f825ceccbe4
- source: modelscope-ms-swift
  path: examples/train/packing/llm.sh
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 083d2d8ec9e7a8e6746335040b70b8cb01855f9ff1f72e54935f8039ea6da087
---

# ms-swift SFT：packing、序列并行与 loss 归一化

## 问题与使用条件

短样本 padding 比例大或长序列激活超出单卡容量时，可考虑 packing、padding-free 与 SP。它们改变 tensor 排列、通信和分批方式，目标是保留原有训练 token/权重/样本隔离后减少浪费。本文精读普通 SFT、模板及 Megatron loss 的相关代码；两类 backend 的归一化位置不同。

入口为 [工程总览](../../swift.md)。固定代码 `409170095f24b45b8945715341504d99b70a2bc0`；本页是代码契约解释，没有 HCU 性能或阶段 loss 实测。

## 数据到 trainer 的真实调用链

1. `SwiftSft._prepare_template` 取对应 model/template，设置 train mode，检查 `support_padding_free`。未声明时多模态模板与文本模板的默认支持不同，不能给所有 VLM 强开 packing。
2. `_prepare_dataset/_encode_dataset` 载入/编码；GRPO/GKD 延后，cached dataset 禁止 streaming，预训练 split 有独立限制。
3. `_post_process_datasets` 对普通 map-style 使用 `LazyLLMDataset`，packing 选择 `PackingDataset`，streaming packing 选择 `IterablePackingDataset`。`packing_length`、strategy、worker 数和严格编码条件都影响实际 batch。
4. `Template.packing_row` 合并 input IDs、labels、loss_scale 等，缺 position IDs 时按各样本长度分别从零生成；channel 保留为每段列表，多模态额外字段由 `_data_collator_mm_data` 合并。
5. `Template._data_collator` 的 padding-free 路径再合并 batch；Megatron/SP 的非 padding-free 路径要求 right padding。实际 attention 如何接收分段信息继续追模型/template hook 和 backend，position reset 本身不是所有 attention 实现都自动隔离的保证。
6. `Seq2SeqTrainer._prepare_inputs/compute_loss` 或 `MegatronTrainer.forward_step/loss_func` 消费这些字段，形成训练与日志的分子/分母。

源码：[SwiftSft](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/swift/pipelines/train/sft.py)、[Template](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/swift/template/base.py)、[Seq2SeqTrainer](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/swift/trainers/seq2seq_trainer.py)。

## 普通 SFT 的分母与梯度累积

`Template.compute_sft_loss` 默认调用 model；若给出 `num_items_in_batch`，把模型按本 microbatch 平均的 loss 乘以 `有效 shifted labels 数 / num_items_in_batch`。这使一个累积窗口内不同长度 microbatch 的贡献按 token 归一，避免对每个 microbatch 等权平均。

在自定义 loss、loss_scale、DFT/channel loss 或 SP 路径，trainer 会取走 labels，计算 per-token loss，再处理分母。`loss_scale` 随预测目标 shift 后逐 token 加权；不能把 fractional weight 想当然改成 fractional token 个数。`num_items_in_batch` 的来源和汇总域应与 numerator 对齐。

SP 下 `GatherLoss.forward` 将本 shard 的 loss/labels 收集；backward 再 split，并乘 `sequence_parallel.world_size`，补偿后续梯度语义。当前 trainer 的 fallback 分母在 SP 条件下还有 all-reduce；必须核对实际 process group 与 caller 提供的 num-items，不能通过观察一个 rank 的 loss 标量确认正确。

`average_tokens_across_devices`、model 是否接受 loss kwargs、SP train/eval 的额外比例，以及 MoE router aux loss 都参与最终值。调整 microbatch 或梯度累积后，使用同一完整 batch 比较参数梯度/更新，尤其覆盖最后一个不足设置累积步数的窗口。

## Megatron 的 sum/count 与日志同步

`MegatronTrainer.loss_func` 对 output float 转换，用 `labels != -100` 构造 mask，可选 DFT/`loss_scale` 改分子，然后返回 `(lm_loss_sum, local_num_tokens, metrics)`。Core schedule/配置消费该计数；不要再在 adapter 中任意除一次 batch/token 数。

日志 stats 保存 sum/count，普通 logging loss 的 DP/CP reduce 延后至 `_log_callback`。所有相应 last-stage rank 必须参与；全掩码 rank 用零贡献，而非略过 collective。channel loss 同步 keys/values 的路径仍存在，因此“日志 reduce 减少”需按具体启用项分析。

## Chunked CE 能减少什么、不能减少什么

[ChunkedCrossEntropyLoss](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/swift/sequence_parallel/utils.py)在 token 维分块，forward 逐块执行 CE 后拼 loss，backward 逐块重建局部 autograd，梯度写入独立 `grad_logits`。它保存完整 logits/labels，**不是** fused linear+CE，也不自动消除 `T×V` logits 张量；收益主要是限制 CE 中间工作空间，代价是循环/更多 launch 和重建 CE。

当前实现不把梯度写回输入 logits，避免 logits 被 aux loss 或 retained graph 再使用时遭破坏。不能为了减一次分配改成就地覆盖。大 vocabulary、长序列或 SP gather 场景应实际比较工作空间和 kernel 时间，模型融合后可考虑更下层的 linear-CE 实现，但需保留输出/反向契约。

## 验证、诊断与回退

| 检查 | 用来排除什么 |
| --- | --- |
| 逐样本/pack 的 token、labels、position 与有效目标计数 | 样本泄漏、跨段预测、模板丢目标、padding 参与 loss |
| packing 开关下固定 batch logits/loss/梯度对照 | attention 分段或 label shift 语义变化 |
| SP=1 与目标 SP 的梯度、sum/count 对照 | gather/backward 比例、分母 group 错位 |
| 完整/部分累积窗口对合并 batch | 尾窗口重复除梯度累积步数 |
| CE forward、加权反向、aux loss 及重复 backward | 别名、输入覆盖、反向只部分正确 |
| step 吞吐、有效 token、峰值显存和通信 | 减 padding 的收益是否超过新同步与 launch |

官方 [chunked CE 测试](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/tests/train/test_chunked_cross_entropy.py)覆盖多 chunk size、FP32/FP64、leaf/non-leaf、ignore index、任意外部权重、共享 logits 的 aux loss 和 retained-graph 二次反向。[部分累积测试](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/tests/train/test_trainer_partial_accumulation.py)针对 trainer/reranker，以窗口 1/2/4 和合并 batch 比较梯度。测试设计是参考证据，本轮未执行这些上游测试。

发现数值差异时保留原样本与配置，先回退 packing/SP/chunk-loss 对照到已验基线，定位分段/分母后再重开。真实 HCU backend 不能执行支持的 varlen attention 时，不仅改 flag，还要确认实际 fallback 和内存/吞吐影响。

## 更新联动

联动 Template、dataset packing、Seq2SeqTrainer、SP autograd、Megatron loss 和对应测试；Transformers 对 num-items/梯度累积的接口变化也属于依赖影响。问题检索关键词：`packing loss denominator`、`partial accumulation`、`chunked CE logits reuse`、`GatherLoss`。版本兼容、官方 PR 与 HCU 运行状态分别核验。
