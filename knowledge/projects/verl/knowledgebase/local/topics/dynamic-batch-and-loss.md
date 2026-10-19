---
id: engines/verl/topics/dynamic-batch-and-loss
title: verl：动态批次的硬 token 上限、GRPO 分组与 loss 聚合
engine: verl
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
- source: volcengine-verl
  path: verl/utils/seqlen_balancing.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: f0536d757a8c8eb1a15d63e7174a8995ebbf180481845576f1817ee6020b4902
- source: volcengine-verl
  path: verl/trainer/ppo/core_algos.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: 369b614f239f237a04a38a40b1877cd6fd14aa7bd5f9ff4fe4d7758b682a6948
- source: volcengine-verl
  path: verl/trainer/ppo/ray_trainer.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: eb41f99ccc66976eab14ebe35aa1aa5b7318e02469240ef1569ac4c884c94312
- source: volcengine-verl
  path: verl/workers/engine_workers.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: 301323b0a8665d236189c3438b835ee4b2ba8bc8cfced1890684070d403ef7a8
- source: volcengine-verl
  path: verl/workers/config/actor.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: d7631944b186f162b897022c9fac8b2f0ede7f8bb6cba4276d98e5d5033fd60b
- source: volcengine-verl
  path: tests/utils/test_seqlen_balancing.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: 658fb094f2edb2fe6914ded167e4b18aba3543d5b5410a93a2816622a7b9c48d
- source: volcengine-verl
  path: tests/trainer/ppo/test_loss_aggregation_on_cpu.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: b22649fdfcfc1fabcebd3cc8ba4c08e88eacb12722fee41e67b785e15a6cae0f
- source: volcengine-verl
  path: tests/trainer/ppo/test_core_algos_on_cpu.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: 0a60e917589ab91646989f0a8616f810fea0dc70047d2b8c13914f4977f5569c
- source: volcengine-verl
  path: tests/trainer/ppo/test_rollout_corr_integration.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: 3d8c1a1471043a5cbe03cf010c0b2e3dff293370c79b2273aa70a02261bdd759
- source: volcengine-verl
  path: verl/models/mcore/model_forward_fused.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: 52ca25fc8ef6721f65e8ed26758f5ca083e37e1364f38e1e72d209869e27de67
- source: volcengine-verl
  path: verl/utils/kernel/linear_cross_entropy.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: 15dfe6d168640ae817f4558f187e9fd515231e910ba42935b7a3969e268b07f6
- source: volcengine-verl
  path: tests/models/test_model_forward_fused.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: 39856c176a8bac1aa03d338eae10bb40ef6d2d7d3a2455c54e73b76de4d82f1b
- source: volcengine-verl
  path: tests/workers/test_megatron_liger_fused_kernels_on_cpu.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: be3b7b19adaf53a007a33a18a7142fed6aa7736e8e482788c99f10c3c8ddca27
- source: volcengine-verl
  path: verl/workers/config/rollout.py
  commit: 8f016846e3010e225072a947270dc0c1b98c1cd0
  sha256: f62e366c906a152a2fc61328afb33c711125f036e05d82b82189333c4ffc47b4
---

# verl：动态批次的硬 token 上限、GRPO 分组与 loss 聚合

## 要解决的问题

RL response 长度变化大，固定样本数 micro batch 容易因长序列 OOM，或让不同 DP rank 的计算时间差别很大。按 token budget 切分和负载重排能改善效率，但必须保持样本、group、loss 与同步次数契约。

配置从 actor 的 `use_dynamic_bsz`、`ppo_max_token_len_per_gpu` 与 rollout/ref logprob 对应预算进入 engine；这些是各阶段不同预算，不是同一个 universal batch size。[`ActorConfig`](https://github.com/verl-project/verl/blob/8f016846e3010e225072a947270dc0c1b98c1cd0/verl/workers/config/actor.py)对固定 micro batch、模式和 SP/remove-padding 做校验，不能靠删 assert 接受不支持组合。

## `rearrange_micro_batches` 的真实上限

[`seqlen_balancing.py`](https://github.com/verl-project/verl/blob/8f016846e3010e225072a947270dc0c1b98c1cd0/verl/utils/seqlen_balancing.py)先得到有效序列长：nested 用 offsets 差，普通 tensor 用 attention mask，但普通输入的初始单序列上限校验还使用 padded shape 的 S。`max_token_len` 必须足够容纳最长输入；不能误解为仅 response token 数。

1. `force_group_size` 将连续样本作为不可分割组，先检查 batch 整除，并汇总各组 token 数/工作量。
2. `ceil(total tokens / budget)` 只是初始下界，不保证不可分样本可放入这些桶。
3. 在 DP group 同步最大 micro batch 数，按 VPP 等 `num_batches_divided_by` 向上取整；fatal constraints先跨rank同步，避免一个rank先报错而其他rank挂在collective。
4. 用平衡算法分组，逐桶检查实际 token 数；不满足则增加桶数并重新分配，直到满足硬上限或报无法满足。
5. 保持 forced group 不拆；所有参与 DP rank 要能提供同样数量的**非空组**。当前实现会对请求数超过最少组数报错，不能按旧注释假定自动补任意空批。
6. 返回 batch 及原 row index mapping；推断后用 reverse index 恢复顺序，UID、reward、logprob 和 route replay同样要跟着恢复。

## 工作量估算和调度代价

`calculate_workload(L) = 24576×L + L²` 来自 hidden=4096 的 dense transformer 近似，返回相对工作量，**不是当前模型的实际 FLOPs/roofline 上限**。MoE、稀疏attention、多模态和不同hidden需另建模型或使用实测。均衡按相对权重而不是只按样本数。

动态 micro batch 平衡开启时，先按工作量排序，再把较小批放两端，旨在减小 PP warm-up/cool-down bubble。更多桶增加launch、调度和归约次数；更大budget增加峰值。同时记录最大/均值rank工作量、token/桶、GPU等待与peak，而不是仅看平均step。

## GRPO grouping 与概率来源

[`compute_grpo_outcome_advantage`](https://github.com/verl-project/verl/blob/8f016846e3010e225072a947270dc0c1b98c1cd0/verl/trainer/ppo/core_algos.py)沿 response token 求总reward，按 prompt index求组内mean/std，再把每sample优势广播回response并乘response mask。单样本组特殊mean=0/std=1，`norm_adv_by_std_in_grpo`控制是否除std。重排不能把group index重新编号为每row或丢掉prompt身份。

`RayPPOTrainer.fit` 的 decoupled 路径重算 π_old，bypass用rollout概率作为old；rollout correction有自己的重要性权重/拒绝统计。省掉一次前向可能改变数值目标；对比同一response的behavior、proximal和current logprob，比只比较最终scalarloss更易定位。

## 聚合分母必须与全 batch 匹配

[`agg_loss`](https://github.com/verl-project/verl/blob/8f016846e3010e225072a947270dc0c1b98c1cd0/verl/trainer/ppo/core_algos.py)用 global batch 计数维持分片/切microbatch后的语义：

| 模式 | 聚合与含义 |
| --- | --- |
| token-mean | 本地有效token loss sum / 全batch有效token数 × DP；DP>1必须提供global token count |
| token-sum | 本地有效token sum × DP，以补偿DP梯度平均；尺度随数据量变化 |
| seq-mean-token-sum | 每序列token sum，再按有有效token的全局sequence数平均 |
| seq-mean-token-sum-norm | 再除固定scale或当前horizon；动态horizon会改变尺度 |
| seq-mean-token-mean | 先每序列有效token平均，再全sequence平均；与tokenmean对长短response的权重不同 |

Megatron PP schedule 还需要配套 num_microbatches/CP 缩放，FSDP 用该loss直接backward。不能“每microbatch平均再平均”冒充全tokenmean。TrainingWorker准备global有效token信息，再进入engine，复核这条完整传递链。

## Liger TP output-head 的固定容量与 runtime owner

Megatron 开启 `use_fused_kernels` 与 `use_liger`，且满足 BF16 等实际条件时，output-head 调用 Liger 的公共 TP fused scaled-CE API。`_plan_liger_flsce_capacity` 在 reference 初始化前联合 actor training、actor logprob 与 reference 的现有 max-token limits，各乘对应 CP，取最大 token 与最小 TP 的词表容量；不是从首个小 microbatch 的实际 shape 临时猜 workspace。固定 microbatch 配置下这些 token limit 并不约束 batch 本身，仍须覆盖最大 packed/对齐后的 output-head 输入。

`_configure_liger_runtime` 要求合法 token capacity 和可整除 TP 的词表；所有 PP/VPP 阶段（包括没有 output weight 的阶段）参与。`configure_liger_flsce` 将 TP partition ranks 跨 WORLD 汇总、生成对应组身份，以 WORLD bootstrap 调用 Liger configure。可选 native wheel/hardware 的 eligibility 与算子 fallback 由 Liger 决定，verl 不自建 NVSHMEM 或缓存；缺公共配置 API 是依赖错误，不能静默冒充 native 成功。配置后不能随 batch 增长自动扩容，每进程多个 native contexts 的操作需串行。

native 初始化成功时，legacy DeepEP V1 的 dispatch/combine RDMA allocation hints 若非零会被拒绝，避免另一个 lazy NVSHMEM owner 随后占用同进程；同节点零 RDMA buffer 不被此门控一律禁止。使用兼容 dispatcher 或关闭该 fused head 是明确回退，不能只屏蔽错误。对称 heap/workspace 不随参数、optimizer offload 或推理 sleep 自动释放，须单独计入共卡最高峰值；本轮未做 native/GPU 回归。

`test_megatron_liger_fused_kernels_on_cpu.py` 的 mock 回归覆盖每个 PP/VPP阶段、ref先建而actor容量更大/TP更小、双flag/role/backend门控、optional fallback及只拒绝实际RDMA配置；`test_model_forward_fused.py` 检查 output-processor hook 与旧 patch 的幂等/消费者接线。它们提供局部契约入口，不证明跨节点 DeepEP 与 native Liger 训练可用。

rollout 的 top-k logprob 预算也与执行 batch 分开：当前 schema 不再强制采样 top_p=1/top_k=-1，但仍要求 vLLM、processed_logprobs 与 calculate_log_probs，返回 head 小于采样 top_k 会告警。是否覆盖真实 sampling support 决定后续近似，不能把 topk_log_probs 参数值当作完整分布或修改训练目标的许可。

## 验证、失败和更新

[`test_seqlen_balancing.py`](https://github.com/verl-project/verl/blob/8f016846e3010e225072a947270dc0c1b98c1cd0/tests/utils/test_seqlen_balancing.py)检查分组/预算/重排；[`test_loss_aggregation_on_cpu.py`](https://github.com/verl-project/verl/blob/8f016846e3010e225072a947270dc0c1b98c1cd0/tests/trainer/ppo/test_loss_aggregation_on_cpu.py)针对token-sum检查mask、1/2/4microbatch不变性和DP均值模拟。它们不是所有mode的HCU分布式验证。

回归应覆盖变长、全mask、n=1/n>1、forced组超过预算、DP组样本数不同、VPP整除、还原index与loss/梯度一致性。失败优先回退固定保守microbatch或原聚合，不改训练目标来掩盖错误。本页未执行设备测试。更新切分算法、engine normalization、lossmode或driver平衡时联动[总览](../overview/engineering-guide.md)和权重/恢复专题。


## 本轮补充固定证据

- [verl/models/mcore/model_forward_fused.py](https://github.com/verl-project/verl/blob/8f016846e3010e225072a947270dc0c1b98c1cd0/verl/models/mcore/model_forward_fused.py)
- [verl/utils/kernel/linear_cross_entropy.py](https://github.com/verl-project/verl/blob/8f016846e3010e225072a947270dc0c1b98c1cd0/verl/utils/kernel/linear_cross_entropy.py)
- [tests/models/test_model_forward_fused.py](https://github.com/verl-project/verl/blob/8f016846e3010e225072a947270dc0c1b98c1cd0/tests/models/test_model_forward_fused.py)
- [tests/workers/test_megatron_liger_fused_kernels_on_cpu.py](https://github.com/verl-project/verl/blob/8f016846e3010e225072a947270dc0c1b98c1cd0/tests/workers/test_megatron_liger_fused_kernels_on_cpu.py)
- [verl/workers/config/rollout.py](https://github.com/verl-project/verl/blob/8f016846e3010e225072a947270dc0c1b98c1cd0/verl/workers/config/rollout.py)
