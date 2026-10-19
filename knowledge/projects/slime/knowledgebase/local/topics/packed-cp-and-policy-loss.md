---
id: engines/slime/topics/packed-cp-and-policy-loss
title: Slime：packed CP、策略 loss 与 sample/token 分母
engine: slime
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
- source: thudm-slime
  path: slime/backends/megatron_utils/data.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: b01a78b17b7d9ed93666982af378b6d2d74951473cad85f432e44d4cb8f926c8
- source: thudm-slime
  path: slime/backends/megatron_utils/loss.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 92ca932bd18019d5899272da1ae65da4a9f8172c4dbdeecbf6897b1f62d7e754
- source: thudm-slime
  path: slime/backends/megatron_utils/arguments.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 20bc1b4278c0eaa051a877a8e5482f9671490d417c37a6b22375c5bbfef82dee
- source: thudm-slime
  path: slime/backends/megatron_utils/actor.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 9f0e0cd3119c8354cd76c1972c908143b7f933b2653a1f53a2a898b1f8b13739
- source: thudm-slime
  path: slime/utils/ppo_utils.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: fce003ac385badbe6946732ef4137bd968a823b0d51f52cc1903ebd8bb61e0ba
- source: thudm-slime
  path: docs/en/advanced/policy-mismatch.md
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 5cee4b66dc494b1146a0bbc7b549e50037602972ef39b74feb40a97f05501f74
- source: thudm-slime
  path: docs/en/advanced/parallelism-memory.md
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 3f797e9973ec95f8a8f9a119eeb0b14aff6eff32129988bc950493efe49f8bed
- source: thudm-slime
  path: tests/test_loss_cp_invariance.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 271fd279f2e4a9f8bae711de032fa3afdf3c3eaa0e9f18368a03fb87a7b7a018
- source: thudm-slime
  path: tests/test_policy_loss.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 120c60a9e284b691dab54be58027eb67ae534d1e39cf416f4a2555a14834c589
- source: thudm-slime
  path: tests/test_ppo_logprob_entropy.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 18e292c347343b512f2179e5ac0ce62168aa69ecfebcfb3c3d831076e80c771b
---

# Slime：packed CP、策略 loss 与 sample/token 分母

## packed数据与CP不是一个开关

[`data.py`](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/data.py)把不同样本tokens、length和response loss mask拼到Megatron输入；label/logprob位置、sample边界与attention约定同时处理。默认zigzagCP按每序列2×CP块配早晚位置；allgatherCP则对padded packed流取连续片段，两种layout不能混用后端。[并行文档](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/parallelism-memory.md)说明causal负载差异，而不是承诺某种kernel必然更快。

当前[`arguments.py`](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/arguments.py)对CP>1的allgatherCP限定支持的DSA模型类；稀疏attention的HCU后端可能进一步限定CP=1。确认model class、最终config及attention接口，而不是只export同名环境变量。

## 有效响应和三个策略概率

policy loss在[`loss.py`](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/loss.py)从模型logits取得logprob/entropy，与batch中old/rollout概率、advantages和response masks结合。prompt与pad不应进入response目标；EOS/truncation、动态过滤和mask变化也会改变分母。

`compute_policy_loss`实现clipped目标，负advantage的dualclip有单独界限；GSPO、CISPO、OPSM等配置走各自路径，不能统一称为同一PPO。使用TIS/mismatchmetrics时，policy梯度可能使用修改后的responsemask，reporting又保留原mask统计。排查“metric改善但loss变了”要同时保存两种mask及其denominator。

[`policy-mismatch文档`](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/policy-mismatch.md)用于理解生成backend与训练backend的概率差、重要性校正和取舍；校正不是绕过底层数值错误的工具。先确认相同权重、token/temperature和采样，再分析batch形态、低精度/融合算子或陈旧策略。

## loss wrapper 如何衔接 MCore

`loss_function(args, batch, num_microbatches, step_global_batch_size, logits)`明确使用**当前step全DP样本数**，避免按配置globalbatch或假定每rank持有相同样本数。它选择policy/value/SFT/custom，并可对loss函数做nonreentrantcheckpoint减少保存中间量。

- sample平均模式：将本地sample-mean和按 `num_microbatches / step_global_batch_size × DP(with CP)` 缩放，抵消MCore调度/归约的缩放。
- token模式：用配套tokennormalizer及CP因子交给MCore；源码的num_tokens逐sample将mask sum至少钳到1，不能把这个值描述为所有情况下完全等于mask有效token数。
- logging分别累计token分母或留下sample分母placeholder，由consumer用实际step_global_batch_size填入，不把每microbatch分母平均。

allgatherCP中有的rank可能只有padding或不贡献loss；源码添加 `0 * logits.sum()` 强制所有rank经过attentionautograd，使gather的backwardreduce-scatter都执行，避免其他rank死锁。删除零项不改变本地数学loss，却可能破坏collective参与协议。

## Logprob 重算、一次 gather 与主机同步

`calculate_log_probs_and_entropy(chunk_size>0)` 现进入 `_ChunkedLogProbEntropy`，forward 仅保留调用方 logits/tokens/可选 keep-mask；backward 再逐行块调用原 logprob/entropy 计算并把梯度写入一次分配的完整 `grad_input`。这样避免每块保留 FP32 full-vocab softmax，也避免若干独立可微 chunk 合并时重复分配完整 logits 梯度。代价是 backward 重算和分块 launch，完整 logits/最终梯度仍存在；`once_differentiable` 不承诺高阶反向。只有启用 entropy gradient 时 entropy 才参与反向。

默认 zigzag CP 的两个响应区间现先组成 row indices，再一次 `index_select`，避免分别切片的 backward 各产生完整 `[T,V]` 梯度。没有 response rows 时使用连接原图的空 slice，避免大索引输入下空 index_select 的零 grid 问题；这与 allgather-CP 保留零 loss collective 参与项相辅相成，不能为了移除“空运算”而删除。

`PackedSeqParamsWithCPUOffsets` 在已有 CUDA cu-seqlens 外保留 CPU tuple，Python 切片/max-length 不必逐层读取 CUDA scalar。loss 日志通过 detach/stack 组合设备 scalar，代替从 tensor 列表构造新 tensor 造成逐个同步；稀疏支持集也合并 host 坐标和传输。收益需从 host wait、分配峰值与端到端步时验证，不能仅按少一次 API 计算加速比。

固定 `test_ppo_logprob_entropy.py` 用 saved-tensors hooks 检查只保留输入存储，覆盖 keep-mask、entropy gradient、空输入与分块/非分块参考；其词表并行回归另有分布式条件。`test_policy_loss.py` 新增 dtype、sample/token mode 和 tensor/Python metric 组合，直接检验日志值不带图且 loss 梯度/normalizer 不变。本轮仅阅读，没有运行 HCU 或真实 TP/CP 回归。

## 性能与验证

packing减少padding和重复launch；CP延长可处理序列但引入远端attention/索引及gatherworkspace，不是所有内存都会除CP。lossrecompute减少中间存储又增加计算；必须看logprob/entropy等hotpath实际占比，不能仅依据功能存在决定开启。

[`test_loss_cp_invariance.py`](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_loss_cp_invariance.py)检查sample-mean路径在不同DP/CP下的梯度不变性；[`test_policy_loss.py`](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_policy_loss.py)手算dualclip并以AST检查eps_clip_c传到训练调用。一个是归约契约，一个是局部算法/接线，均不构成整模型HCU精度验证。

实际回归保留相同rollout固定数据，对比CP1/CP>1、不同microbatch、变长/全mask、重复group和token/samplemode，检查逐samplelogprob、gradnorm与更新参数；阶段后再做loss/reward对比。遇到错误先回退原packed/CP/融合路径，不随意改mask或训练目标。本页未实测HCU；更新需联动[总览](../overview/engineering-guide.md)、MCore依赖、attention实现与data接口。


## 本轮补充固定证据

- [tests/test_ppo_logprob_entropy.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_ppo_logprob_entropy.py)
