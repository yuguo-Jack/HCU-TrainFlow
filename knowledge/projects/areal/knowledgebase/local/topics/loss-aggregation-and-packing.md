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
reviewed_on: '2026-11-04'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime execution
sources:
- source: inclusionai-areal
  path: areal/trainer/ppo/actor.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 82f9349ac3d0bdcb2f686b451d0fef6b409a35c8a11f2a450ba9071dc027758f
- source: inclusionai-areal
  path: areal/trainer/ppo/loss_reduction.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: ec6332da715249fb9dd985962536578222fd611268044c96ab72668fd16c306f
- source: inclusionai-areal
  path: areal/utils/functional/loss_aggregation.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 030f9089f557d837bac5301f267f9685857b7e29c08a682d45f460e130313ed3
- source: inclusionai-areal
  path: areal/engine/core/train_engine.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: a24f263445ea85ffdc63dfebcbbee7536b3401e93e45cfe6f1a979be6724d66f
- source: inclusionai-areal
  path: areal/engine/megatron_engine.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: ee4159e666efe47efc63547119fe44efdf3289b0c68ee20b94337652bff39b54
- source: inclusionai-areal
  path: areal/engine/fsdp_engine.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 6e0d40e83de6614a343eb6a37264e602e7c215cfdf491fde8ae14b1d7d04d9fc
- source: inclusionai-areal
  path: areal/api/cli_args.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: fe0cfdb321273ce0b7a3290288146cfd3ea21e35bebcb8bcfb9bf018fda39e1e
- source: inclusionai-areal
  path: docs/en/algorithms/sequence_packing.md
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: d0bf74ba82d8ac45dcb2f7cb0ca1ff4f25831ef9742e4f5ff273a3d5e4705ef8
- source: inclusionai-areal
  path: tests/test_prompt_mean_actor.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 0ecb5c5e733dfd7055f012dc49567abd9350b9b63a489dbfc0ff4678f2d62142
- source: inclusionai-areal
  path: tests/test_prompt_mean_loss.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: e03e00914dd8b04c26387b6f3402ed01775605a4de965620f06424b38f298e26
- source: inclusionai-areal
  path: tests/test_train_engine.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 303da75e43e1ad6ae59b2e1cb49250d991e97c451cad409910ed975a3edf5509
- source: inclusionai-areal
  path: areal/api/loss.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 40c8290624c964d2ce9a4b9cfda79c2335ffdc7a27ffd08dde99ffab830b05c7
- source: inclusionai-areal
  path: tests/test_named_loss_contract.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 296136071e30396b0adbbd031fac011edf2a65754dec2481c96ccf05cf56b62a
- source: inclusionai-areal
  path: tests/test_named_loss_engines.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 87832a01cecb6bc24d38a0ba53b6bd723f608664b676038e131dc24647dda556
- source: inclusionai-areal
  path: areal/engine/r3/config.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: c9de319a50105d86d318d0b661ec1437c2eb7c771594cd5b025dbaaa92855db7
- source: inclusionai-areal
  path: areal/engine/r3/transport.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: d34a68360ac4b04ae26eb644af3389240662d2d3aab91fc751571aa7b91a4863
- source: inclusionai-areal
  path: areal/trainer/rl_trainer.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: e6fb96cd7e27c88414219906d1b42252b1bc552a7df3ff0dc0415d94bb956362
- source: inclusionai-areal
  path: areal/engine/megatron_utils/packed_context_parallel.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 04aca90d0958126880ba225f93b9c51b0ada3b1c38d1f88988b476179810b734
- source: inclusionai-areal
  path: areal/utils/score_centering.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: afa75d5401681598237355b1e97c49ca74809518279ec9f603a0db8642431d46
- source: inclusionai-areal
  path: areal/engine/sglang_remote.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 9ae79598aff49617b2cd7a44c6164cbd1e9a1ec3bc1a5f71ec67437939d9c8c5
- source: inclusionai-areal
  path: areal/workflow/rlvr.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 5343b6a3dbfd061d2e75c8c99f129a71a596aa1f8b8573bef9f8a8c950cd5fd6
- source: inclusionai-areal
  path: tests/test_score_centering.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: c1edd94ec569d9f7bb246eeca523c2eb84a2fc03b1c1eee5337efdad22e1501b
- source: inclusionai-areal
  path: tests/test_score_centering_parallel.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: eefb051d5b40d7020658220af778d5070e001fc28d8abed41dff089534df0d5b
- source: inclusionai-areal
  path: tests/test_policy_version_mask.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: a890db3f40d94ed6c89c2df32444342013900b77bdcfa248186a6765651c9924
pr_sources:
- pr-areal-project--areal-1546
---

# Loss 聚合、packing 与梯度归一化

## 问题：相同 rollout 换个 batch 划分，训练目标是否变了

RL 回答长短不一；把每个 microbatch 的平均 loss 直接再平均，会让长度/有效 token 不同的 microbatch 获得不同权重。2026-11-04 复核固定 `27879753c7611fee9a0af6e71a4f838db27b72a7` 中保留的 #1546机制：它 把 reduction 与 engine normalization 配对，支持四种目标。优化 packing、token budget、PPO minibatch 和 DP 时，应先明确哪种目标是模型配方的一部分。

## 配置与实现入口

`PPOActorConfig.loss_aggregation` 可选 `token_mean`、`seq_mean`、`prompt_mean`、`constant`，最后一种还要求正且有限的 `loss_aggregation_divisor`。不要把 `seq_mean` 与 prompt mean 混淆：一个 prompt 可以包含多个回答和多轮 trajectory。

入口为[`PPOActor._ppo_update`](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/trainer/ppo/actor.py)：

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

[`TokenMean`、`SequenceMean`、`PromptMean`、`ConstantLength`](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/utils/functional/loss_aggregation.py)分开保留 denominator mask 与经过 filtering 的 numerator mask。Rejection/importance 策略可以把分子设为零，但不会悄悄缩小原始分母；完全 masked 的有效回答与运输占位 tensor 也不是一回事。

Sequence 型目标用 `cu_seqlens` 恢复 packed sequence 的边界；没有边界的一维 tree-packed 输入当前只能使用 `token_mean`。修改 packing 时必须传递 loss mask、PG token weights 和 sequence 边界，而不是只拼 input_ids。

## Prompt mean：全组系数、实际步骤与 DP

`prepare_policy_gradient_batch` 要求二维 padded loss mask 与合法的 Python `group_sizes`：正整数，和等于 response 行数。它先算每 prompt 全组有效 token 数，为组内 token 写入 `PG_TOKEN_WEIGHTS = mask / group_token_count`，有效 token 为零的组不计入 active groups。

之后 `_PromptMeanBatch.for_steps` 汇总 **实际** optimizer step 数、全局 active prompt 数及每 step 的真实 response 行数；它沿 DP group 做小型计数 collective，不能把 CP 重复计入。这些 scalar 在 host 一次准备，避免每 microbatch 做同步取值。

设全局有效 prompt 数为 G、实际 optimizer step 数为 K，`step_scale=K/G`；一个 microbatch 的 `engine_weight=本地真实 response 行数/该 step 全局真实 response 行数`。`PromptMean.aggregate` 乘全组 token 系数和 step_scale，再除自己的 engine weight；engine 按 `loss × weight` 累加时该除法抵消，使跨分片的组仍保持原始目标系数。

这是**固定参数下，跨步骤 loss/梯度平均与全组目标一致**的保证；不表示执行不同数目的真实 optimizer step 后参数轨迹完全相同。Prompt 可以跨 step，不要求为了组完整性修改原 response schedule。

真实但全 masked 的 response step 仍保留正的行数权重，loss 为零；`TRANSPORT_DUMMY_KEY` 的纯通信占位 microbatch 则由[`compute_microbatch_loss_weight`](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/engine/core/train_engine.py)给零权重。混淆两者会改变归一化或把全零目标误判为运输 padding。

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

## token 版本过滤的目标对齐

`RLTrainer` 只在 `rollout.mask_stale_tokens=True` 时传max_head_offpolicyness给actor。`_policy_version_loss_mask` 在packing/CP之前把input-token versions向左roll到next-token target，末位置-1；要求shape一致和整数dtype，负版本与过期目标不进入分子。`grpo_loss_fn` 的normalizer仍绑定原denominator_mask，过滤仅额外相交numerator mask；context、reward、advantage和原prompt/group目标系数都保留。因此这是改变监督贡献的算法设置，不能当作缩短序列或减少完整forward成本。

当前条件只有非负版本和 `current_version-version <= limit`，**未额外排除未来版本**；未来/无效版本有独立fraction日志，但观测不等于拒绝。若出现未来版本，应先核对权重发布与token来源，再按恢复owner处理，不能用该mask声称版本已经一致。

MTP保留input-token provenance的单独mask，由实际model `_postprocess` 获取最终CP/THD metadata，先按首个额外target滚动两次、后续每层再一次，再乘各层per-token loss；原MCore base-mask计数不变。shape不符、显式labels或只有version mask而无MTP loss mask会拒绝，禁止用普通actor的一次roll直接复用给所有MTP层。

## Score centering 是另一种 surrogate

`use_score_centering` 选择REINFORCE：`advantage.detach() × (correction − detached_weight × current_logp)`。correction的head/tail系数detach，只有最后score项求导；可选TIS权重使用当前trainer/sampler概率，不能用proximal概率代替，也不能把correction再乘一次TIS权重。

native SGLang RLVR收集top-K sampler head；width须为1…1024的整数，ids不重复且非负，logp有限非正、head总mass不大于1，已采token在head中时概率须吻合。要求temperature=1、非greedy、top_p=1且不截断top_k、无frequency penalty/beam；OpenAI客户端拒绝此设置。actor要求每条trajectory都带匹配head，并与target shift保持一致。

当前仅普通FSDP actor支持（含受限TP/CP），拒绝tree、critic、recompute_logprob、distillation及SAPO/CISPO/decoupled/M2等组合；TIS只接受token ratio clamp、无lower bound。TP要求等宽词表shard，token rows/ids在TP内复制，SUM的local backward保持identity，checkpoint重算关闭early-stop以维持collective顺序。实现按chunk checkpoint FP32 log-softmax，**完整输入logits仍驻留**，entropy只作无梯度诊断；不能称为消除完整logits的LM-head融合。

`test_score_centering_parallel.py` 比较dense oracle、梯度及Adam更新，TP2/CP2用Gloo而混合TP2×CP2需4卡NCCL；真实模型回归需本地AREAL_TEST_MODEL。本页只阅读，未运行这些上游测试，也没有HCU/NVIDIA通过声明。

## 验证、诊断与回退

[`test_prompt_mean_actor.py`](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/tests/test_prompt_mean_actor.py)验证四种模式不改变原 response 步骤；在 padded/packed、不同 requested steps 下，用固定参数 oracle 比较 prompt loss 与梯度，并覆盖真实全 masked step。分布式测试沿 Gloo DP 验证全组系数；`test_train_engine.py` 检查执行层 loss weight。它们是上游测试设计，**本页没有在 HCU 执行**。

现场回归先固定同一批 trajectory、行为 logp、reward/mask/分组和模型参数，比较不 packing / packing、不同 token budget 与 DP 下的 loss 和梯度；再做短训练和阶段质量验证。差异时按原始分母 → group metadata → packed boundary → DP/CP group → engine scaling 排查。回退应恢复经过验证的模式和 packing，不把改变 objective 当成容错手段。

回到[AReaL 总览](../overview/engineering-guide.md)，并联查[异步版本与恢复](async-version-and-recovery.md)。


已阅读新增 [`test_policy_version_mask.py`](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/tests/test_policy_version_mask.py)：覆盖版本左移、零 lag、非法元数据、四种聚合保持原分母、全过滤零梯度及打包前 opt-in 调用。当前测试没有断言 future token 应被拒绝，不能以其存在掩盖上文的 future-version 接受边界；本轮未执行这些上游测试。

## 本轮补充固定证据

- [areal/api/loss.py](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/api/loss.py)
- [tests/test_named_loss_contract.py](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/tests/test_named_loss_contract.py)
- [tests/test_named_loss_engines.py](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/tests/test_named_loss_engines.py)
- [areal/engine/r3/config.py](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/engine/r3/config.py)
- [areal/engine/r3/transport.py](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/engine/r3/transport.py)
