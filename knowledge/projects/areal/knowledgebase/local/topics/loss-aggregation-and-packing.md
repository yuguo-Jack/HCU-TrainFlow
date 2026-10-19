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
reviewed_on: '2026-10-20'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime execution
sources:
- source: inclusionai-areal
  path: areal/trainer/ppo/actor.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: c4b60120edf0427f86789e536ef53513dcba040c7c5645e23d861a45b125e088
- source: inclusionai-areal
  path: areal/trainer/ppo/loss_reduction.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: ec6332da715249fb9dd985962536578222fd611268044c96ab72668fd16c306f
- source: inclusionai-areal
  path: areal/utils/functional/loss_aggregation.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 030f9089f557d837bac5301f267f9685857b7e29c08a682d45f460e130313ed3
- source: inclusionai-areal
  path: areal/engine/core/train_engine.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: a24f263445ea85ffdc63dfebcbbee7536b3401e93e45cfe6f1a979be6724d66f
- source: inclusionai-areal
  path: areal/engine/megatron_engine.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 6f817b52dea9bdf7aa040f290b8a0894a4a6b5dd01488781d31cb5a6d9acf9e9
- source: inclusionai-areal
  path: areal/engine/fsdp_engine.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 91649f17b3e510309edf9dedd35e33b101e1b9d81a0321843b7f0d7fad7a2a40
- source: inclusionai-areal
  path: areal/api/cli_args.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 3c2ab3e451a4c31b8afe08befefb23728e682ce57df5401b383cc3847778fe5e
- source: inclusionai-areal
  path: docs/en/algorithms/sequence_packing.md
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: d0bf74ba82d8ac45dcb2f7cb0ca1ff4f25831ef9742e4f5ff273a3d5e4705ef8
- source: inclusionai-areal
  path: tests/test_prompt_mean_actor.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 0ecb5c5e733dfd7055f012dc49567abd9350b9b63a489dbfc0ff4678f2d62142
- source: inclusionai-areal
  path: tests/test_prompt_mean_loss.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: e03e00914dd8b04c26387b6f3402ed01775605a4de965620f06424b38f298e26
- source: inclusionai-areal
  path: tests/test_train_engine.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 6b1d232555b51025c6be87b366e2a96fca44ed7c5cad6d4dcf8e8579e87a767c
- source: inclusionai-areal
  path: areal/api/loss.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 40c8290624c964d2ce9a4b9cfda79c2335ffdc7a27ffd08dde99ffab830b05c7
- source: inclusionai-areal
  path: tests/test_named_loss_contract.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 296136071e30396b0adbbd031fac011edf2a65754dec2481c96ccf05cf56b62a
- source: inclusionai-areal
  path: tests/test_named_loss_engines.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 5353ad58b59bc0c256c03272f76403bbceade31f33f9213792d1e5fe868d41d4
- source: inclusionai-areal
  path: areal/engine/r3/config.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: c9de319a50105d86d318d0b661ec1437c2eb7c771594cd5b025dbaaa92855db7
- source: inclusionai-areal
  path: areal/engine/r3/transport.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: d34a68360ac4b04ae26eb644af3389240662d2d3aab91fc751571aa7b91a4863
pr_sources:
- pr-areal-project--areal-1546
---

# Loss 聚合、packing 与梯度归一化

## 问题：相同 rollout 换个 batch 划分，训练目标是否变了

RL 回答长短不一；把每个 microbatch 的平均 loss 直接再平均，会让长度/有效 token 不同的 microbatch 获得不同权重。固定官方 `3b936798` 的 #1546 把 reduction 与 engine normalization 配对，支持四种目标。优化 packing、token budget、PPO minibatch 和 DP 时，应先明确哪种目标是模型配方的一部分。

## 配置与实现入口

`PPOActorConfig.loss_aggregation` 可选 `token_mean`、`seq_mean`、`prompt_mean`、`constant`，最后一种还要求正且有限的 `loss_aggregation_divisor`。不要把 `seq_mean` 与 prompt mean 混淆：一个 prompt 可以包含多个回答和多轮 trajectory。

入口为[`PPOActor._ppo_update`](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/areal/trainer/ppo/actor.py)：

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

[`TokenMean`、`SequenceMean`、`PromptMean`、`ConstantLength`](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/areal/utils/functional/loss_aggregation.py)分开保留 denominator mask 与经过 filtering 的 numerator mask。Rejection/importance 策略可以把分子设为零，但不会悄悄缩小原始分母；完全 masked 的有效回答与运输占位 tensor 也不是一回事。

Sequence 型目标用 `cu_seqlens` 恢复 packed sequence 的边界；没有边界的一维 tree-packed 输入当前只能使用 `token_mean`。修改 packing 时必须传递 loss mask、PG token weights 和 sequence 边界，而不是只拼 input_ids。

## Prompt mean：全组系数、实际步骤与 DP

`prepare_policy_gradient_batch` 要求二维 padded loss mask 与合法的 Python `group_sizes`：正整数，和等于 response 行数。它先算每 prompt 全组有效 token 数，为组内 token 写入 `PG_TOKEN_WEIGHTS = mask / group_token_count`，有效 token 为零的组不计入 active groups。

之后 `_PromptMeanBatch.for_steps` 汇总 **实际** optimizer step 数、全局 active prompt 数及每 step 的真实 response 行数；它沿 DP group 做小型计数 collective，不能把 CP 重复计入。这些 scalar 在 host 一次准备，避免每 microbatch 做同步取值。

设全局有效 prompt 数为 G、实际 optimizer step 数为 K，`step_scale=K/G`；一个 microbatch 的 `engine_weight=本地真实 response 行数/该 step 全局真实 response 行数`。`PromptMean.aggregate` 乘全组 token 系数和 step_scale，再除自己的 engine weight；engine 按 `loss × weight` 累加时该除法抵消，使跨分片的组仍保持原始目标系数。

这是**固定参数下，跨步骤 loss/梯度平均与全组目标一致**的保证；不表示执行不同数目的真实 optimizer step 后参数轨迹完全相同。Prompt 可以跨 step，不要求为了组完整性修改原 response schedule。

真实但全 masked 的 response step 仍保留正的行数权重，loss 为零；`TRANSPORT_DUMMY_KEY` 的纯通信占位 microbatch 则由[`compute_microbatch_loss_weight`](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/areal/engine/core/train_engine.py)给零权重。混淆两者会改变归一化或把全零目标误判为运输 padding。

## 适用条件、性能代价与限制

- 当前非 `token_mean` 的蒸馏组合会在 `_ppo_update` 主动拒绝；不要只改 YAML 绕过校验。
- `max_tokens_per_mb`、packing 算法解决执行层 padding/容量；`ppo_n_minibatches` 改变 optimizer-step schedule。两者都要连同目标聚合、DP 权重与 grad clipping 对照，不能只记录 tokens/s。
- Megatron `stage_batch_for_engine` **原地修改** batch 字典，使 RPC 容器不继续持有全 batch GPU tensor；代价是 CPU 内存与搬运。只对 `data` 局部重绑定不会释放外部别名。
- Prompt preparation 增加系数 tensor 与小型 collective；收益主要是目标正确和避免 per-microbatch host/device 同步，不能宣称一定提高所有模型吞吐。

## 具名 loss：分子与各自的全局 mass

当前 `areal/api/loss.py` 新增 `LossValue` 和 `@named_loss_normalizer(names=...)`。原 scalar 回调返回 microbatch mean，engine 继续按 `local_weight/total_weight` 缩放；具名回调返回 `{name: 已求和分子}`，normalizer 返回每项独立的 batch-derived mass。不能把已平均的值直接装进 dict 再除一次，也不能把所有项共用有效 token 数而改变 aux/蒸馏等目标。

`compute_microbatch_loss_weight` 通过静态、排序后的唯一 schema 检查 key，mass 必须是无梯度、有限且非负的 scalar tensor；transport-only microbatch 直接构造 schema 相同的零 mass，不调用真实目标。`compute_total_loss_weight` 在 engine 的实际 DP 或 DP+CP group 上用同一顺序的一次向量 collective 汇总，各 rank（包括只有运输占位的 rank）必须声明同样 names。`normalize_loss` 各项分别除自己的全局 mass；分数 mass 不能 clamp 到 1，global mass 为零时保留 graph-connected zero，非有限分子仍拒绝。

这条新接口没有取代本页四种 PPO aggregation。将原 scalar 目标接到具名接口时，测试用 `旧 loss × 旧 local mass` 构成分子，才保留同一 loss/梯度。固定 `test_named_loss_contract.py` 覆盖四模式、padded/packed、跨 optimizer-step prompt、分数/空 mass 与纯 transport rank；`test_named_loss_engines.py` 继续检查 FSDP/Megatron、native/CP 路径和占位数据不调用回调。本轮是代码/测试阅读，没有在 HCU 执行这些组合。

## Router replay 的数据所有权

当前 `megatron.enable_router_replay` 默认关闭，MTP 和 router fusion 组合会被 engine 显式拒绝；已有普通 actor 不会仅因模块可导入而启用 replay。

R3 数据属于 actor 的路由 side channel，不是所有角色共享的普通 token feature。`PPOActor._compute_logp/_ppo_update` 要求 routed experts 与 valid mask 同时存在、engine 已启用 replay；按实际 optimizer microbatch 行映射拆分，在 context 退出时清空 engine pending tensors。reference/critic/teacher 必须保留自己的专家选择，不能把 actor 路由直接广播过去。普通配置解析要求 MoE 层为连续后缀，特定 bridge 的额外支持还需查对应消费者；interleaved/trailing dense 不能默认接受。

复核 rollout/train 首差时同时对齐 token shift、valid mask、expert-ID layout 与参数版本，再查看 rollout/train logp 和 KL 统计；存在 replay 不等于策略分布已经完全一致。现有短示例的三步运行规模不构成长训精度或吞吐证据；不满足配置/路由发现契约时按明确关闭收集与 replay 的完整路径回退。

## 验证、诊断与回退

[`test_prompt_mean_actor.py`](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/tests/test_prompt_mean_actor.py)验证四种模式不改变原 response 步骤；在 padded/packed、不同 requested steps 下，用固定参数 oracle 比较 prompt loss 与梯度，并覆盖真实全 masked step。分布式测试沿 Gloo DP 验证全组系数；`test_train_engine.py` 检查执行层 loss weight。它们是上游测试设计，**本页没有在 HCU 执行**。

现场回归先固定同一批 trajectory、行为 logp、reward/mask/分组和模型参数，比较不 packing / packing、不同 token budget 与 DP 下的 loss 和梯度；再做短训练和阶段质量验证。差异时按原始分母 → group metadata → packed boundary → DP/CP group → engine scaling 排查。回退应恢复经过验证的模式和 packing，不把改变 objective 当成容错手段。

回到[AReaL 总览](../overview/engineering-guide.md)，并联查[异步版本与恢复](async-version-and-recovery.md)。


## 本轮补充固定证据

- [areal/api/loss.py](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/areal/api/loss.py)
- [tests/test_named_loss_contract.py](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/tests/test_named_loss_contract.py)
- [tests/test_named_loss_engines.py](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/tests/test_named_loss_engines.py)
- [areal/engine/r3/config.py](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/areal/engine/r3/config.py)
- [areal/engine/r3/transport.py](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/areal/engine/r3/transport.py)
