---
id: engines/areal/topics/loss-aggregation-and-packing
title: AReaL：token/response/prompt 聚合、packing 与梯度归一化
engine: areal
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected mechanisms, recipes and tests at pinned official source; not every
  model/backend and no HCU runtime execution
sources:
- source: inclusionai-areal
  path: areal/trainer/ppo/actor.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 0c0a0a4c29a125395c67be4b7cc20b3bd947ad3b5bbd65840d69994039f4dbe1
- source: inclusionai-areal
  path: areal/trainer/ppo/loss_reduction.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: ec6332da715249fb9dd985962536578222fd611268044c96ab72668fd16c306f
- source: inclusionai-areal
  path: areal/utils/functional/loss_aggregation.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 030f9089f557d837bac5301f267f9685857b7e29c08a682d45f460e130313ed3
- source: inclusionai-areal
  path: areal/engine/core/train_engine.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 426e1725004f5108153e19ead99a1b7c75ae39ebdc8224ec5b18269378b6b087
- source: inclusionai-areal
  path: areal/engine/megatron_engine.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: ab46124b83574848f55b1dc80f2c15262c6b4832d0dc558c04207709af952935
- source: inclusionai-areal
  path: areal/engine/fsdp_engine.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 390adcf379c6bde7788170927cff91143ffa87071ce7af9269c1e9560295314b
- source: inclusionai-areal
  path: areal/api/cli_args.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 28fe088a2ef371c79da84884beafdfea90e1d8a1d5dc2ab039cea181c4605191
- source: inclusionai-areal
  path: docs/en/algorithms/sequence_packing.md
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: d0bf74ba82d8ac45dcb2f7cb0ca1ff4f25831ef9742e4f5ff273a3d5e4705ef8
- source: inclusionai-areal
  path: tests/test_prompt_mean_actor.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 389c047c5e005ed26649f199430e94a5bc15fa00391a09baaa84c836e19cddac
- source: inclusionai-areal
  path: tests/test_prompt_mean_loss.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: e03e00914dd8b04c26387b6f3402ed01775605a4de965620f06424b38f298e26
- source: inclusionai-areal
  path: tests/test_train_engine.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 6b1d232555b51025c6be87b366e2a96fca44ed7c5cad6d4dcf8e8579e87a767c
pr_sources:
- pr-areal-project--areal-1546
---

# Loss 聚合、packing 与梯度归一化

## 问题：相同 rollout 换个 batch 划分，训练目标是否变了

RL 回答长短不一；把每个 microbatch 的平均 loss 直接再平均，会让长度/有效 token 不同的 microbatch 获得不同权重。固定官方 `aedc21ec` 的 #1546 把 reduction 与 engine normalization 配对，支持四种目标。优化 packing、token budget、PPO minibatch 和 DP 时，应先明确哪种目标是模型配方的一部分。

## 配置与实现入口

`PPOActorConfig.loss_aggregation` 可选 `token_mean`、`seq_mean`、`prompt_mean`、`constant`，最后一种还要求正且有限的 `loss_aggregation_divisor`。不要把 `seq_mean` 与 prompt mean 混淆：一个 prompt 可以包含多个回答和多轮 trajectory。

入口为[`PPOActor._ppo_update`](https://github.com/areal-project/AReaL/blob/aedc21ec66ff03f329dcd4139945da8087e0d0e7/areal/trainer/ppo/actor.py)：

```text
concat_batch(data) 获得 trajectory group 元数据
  → prepare_policy_gradient_batch：在拆分前保存原始目标系数
  → stage_batch_for_engine：Megatron 整批转 CPU
  → split_training_batch_into_microbatches：PPO optimizer-step 划分
  → prepared_loss.for_steps：按实际步骤/DP 准备 normalization
  → engine.train_batch(loss_fn, loss_weight_fn)
  → engine 内执行 microbatch/packing/并行 schedule
```

先准备、再切分很重要：一组 prompt 的回答可能跨多个 optimizer step，不能在每个局部切片重新统计整个 prompt 的分母。

## 四种目标与原始分母

| 模式 | 目标单位与 engine weight | 不应误解为 |
| --- | --- | --- |
| `token_mean` | 原始有效 token 总数；局部 token loss 和除以原始 mask count | 经过 rejection 后留下 token 的均值 |
| `seq_mean` | 每个有效 response 内先做 token mean，再按有效 response 数聚合 | 每个 prompt 等权 |
| `prompt_mean` | 每个有效 prompt 的全组 token mean，再对有效 prompt 等权 | 只用当前 microbatch 内回答重新估计组大小 |
| `constant` | token loss 和 /（有效 response 数 × 固定长度 divisor） | token_mean 的别名；其长度权重不同 |

[`TokenMean`、`SequenceMean`、`PromptMean`、`ConstantLength`](https://github.com/areal-project/AReaL/blob/aedc21ec66ff03f329dcd4139945da8087e0d0e7/areal/utils/functional/loss_aggregation.py)分开保留 denominator mask 与经过 filtering 的 numerator mask。Rejection/importance 策略可以把分子设为零，但不会悄悄缩小原始分母；完全 masked 的有效回答与运输占位 tensor 也不是一回事。

Sequence 型目标用 `cu_seqlens` 恢复 packed sequence 的边界；没有边界的一维 tree-packed 输入当前只能使用 `token_mean`。修改 packing 时必须传递 loss mask、PG token weights 和 sequence 边界，而不是只拼 input_ids。

## Prompt mean：全组系数、实际步骤与 DP

`prepare_policy_gradient_batch` 要求二维 padded loss mask 与合法的 Python `group_sizes`：正整数，和等于 response 行数。它先算每 prompt 全组有效 token 数，为组内 token 写入 `PG_TOKEN_WEIGHTS = mask / group_token_count`，有效 token 为零的组不计入 active groups。

之后 `_PromptMeanBatch.for_steps` 汇总 **实际** optimizer step 数、全局 active prompt 数及每 step 的真实 response 行数；它沿 DP group 做小型计数 collective，不能把 CP 重复计入。这些 scalar 在 host 一次准备，避免每 microbatch 做同步取值。

设全局有效 prompt 数为 G、实际 optimizer step 数为 K，`step_scale=K/G`；一个 microbatch 的 `engine_weight=本地真实 response 行数/该 step 全局真实 response 行数`。`PromptMean.aggregate` 乘全组 token 系数和 step_scale，再除自己的 engine weight；engine 按 `loss × weight` 累加时该除法抵消，使跨分片的组仍保持原始目标系数。

这是**固定参数下，跨步骤 loss/梯度平均与全组目标一致**的保证；不表示执行不同数目的真实 optimizer step 后参数轨迹完全相同。Prompt 可以跨 step，不要求为了组完整性修改原 response schedule。

真实但全 masked 的 response step 仍保留正的行数权重，loss 为零；`TRANSPORT_DUMMY_KEY` 的纯通信占位 microbatch 则由[`compute_microbatch_loss_weight`](https://github.com/areal-project/AReaL/blob/aedc21ec66ff03f329dcd4139945da8087e0d0e7/areal/engine/core/train_engine.py)给零权重。混淆两者会改变归一化或把全零目标误判为运输 padding。

## 适用条件、性能代价与限制

- 当前非 `token_mean` 的蒸馏组合会在 `_ppo_update` 主动拒绝；不要只改 YAML 绕过校验。
- `max_tokens_per_mb`、packing 算法解决执行层 padding/容量；`ppo_n_minibatches` 改变 optimizer-step schedule。两者都要连同目标聚合、DP 权重与 grad clipping 对照，不能只记录 tokens/s。
- Megatron `stage_batch_for_engine` **原地修改** batch 字典，使 RPC 容器不继续持有全 batch GPU tensor；代价是 CPU 内存与搬运。只对 `data` 局部重绑定不会释放外部别名。
- Prompt preparation 增加系数 tensor 与小型 collective；收益主要是目标正确和避免 per-microbatch host/device 同步，不能宣称一定提高所有模型吞吐。

## 验证、诊断与回退

[`test_prompt_mean_actor.py`](https://github.com/areal-project/AReaL/blob/aedc21ec66ff03f329dcd4139945da8087e0d0e7/tests/test_prompt_mean_actor.py)验证四种模式不改变原 response 步骤；在 padded/packed、不同 requested steps 下，用固定参数 oracle 比较 prompt loss 与梯度，并覆盖真实全 masked step。分布式测试沿 Gloo DP 验证全组系数；`test_train_engine.py` 检查执行层 loss weight。它们是上游测试设计，**本页没有在 HCU 执行**。

现场回归先固定同一批 trajectory、行为 logp、reward/mask/分组和模型参数，比较不 packing / packing、不同 token budget 与 DP 下的 loss 和梯度；再做短训练和阶段质量验证。差异时按原始分母 → group metadata → packed boundary → DP/CP group → engine scaling 排查。回退应恢复经过验证的模式和 packing，不把改变 objective 当成容错手段。

回到[AReaL 总览](../overview/engineering-guide.md)，并联查[异步版本与恢复](async-version-and-recovery.md)。
