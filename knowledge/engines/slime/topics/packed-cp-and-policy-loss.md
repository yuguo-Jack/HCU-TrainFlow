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
reviewed_on: '2026-10-12'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime
  execution
sources:
- source: thudm-slime
  path: slime/backends/megatron_utils/data.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 581ed42c5bd2dcfe0af5b262cce8d5fee1719bf30da4ca3ec9bb1de73806abef
- source: thudm-slime
  path: slime/backends/megatron_utils/loss.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 65c68c20b2a967e4331ce918cb72910657e6caf977638f3afbc6791d2f06ae15
- source: thudm-slime
  path: slime/backends/megatron_utils/arguments.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: aa9f5b7341d4d9f5554e7d376a6d916999e469bca7a7699f0d465e6290a2e2e9
- source: thudm-slime
  path: slime/backends/megatron_utils/actor.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 66a159753c6c3e1c8509b781f301551caf0a27e2dfe5c810dea8003b75b3710d
- source: thudm-slime
  path: slime/utils/ppo_utils.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 5b936ff1c1cd9114a1f35bf657add6241f2ac4da83f2db6b55ef35ddd0da7e3f
- source: thudm-slime
  path: docs/en/advanced/policy-mismatch.md
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 5cee4b66dc494b1146a0bbc7b549e50037602972ef39b74feb40a97f05501f74
- source: thudm-slime
  path: docs/en/advanced/parallelism-memory.md
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 6071c1eadf948dc39300e51300dd9dcae05830d58df3e2f44db5e60081893f82
- source: thudm-slime
  path: tests/test_loss_cp_invariance.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 271fd279f2e4a9f8bae711de032fa3afdf3c3eaa0e9f18368a03fb87a7b7a018
- source: thudm-slime
  path: tests/test_policy_loss.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 328ad469218438ebc83785eafc78708b958a7658d4fbaa2655f59934bade1481
---

# Slime：packed CP、策略 loss 与 sample/token 分母

## packed数据与CP不是一个开关

[`data.py`](https://github.com/THUDM/slime/blob/05e3b017fed9e02de418c2fbac9d75602a534be5/slime/backends/megatron_utils/data.py)把不同样本tokens、length和response loss mask拼到Megatron输入；label/logprob位置、sample边界与attention约定同时处理。默认zigzagCP按每序列2×CP块配早晚位置；allgatherCP则对padded packed流取连续片段，两种layout不能混用后端。[并行文档](https://github.com/THUDM/slime/blob/05e3b017fed9e02de418c2fbac9d75602a534be5/docs/en/advanced/parallelism-memory.md)说明causal负载差异，而不是承诺某种kernel必然更快。

当前[`arguments.py`](https://github.com/THUDM/slime/blob/05e3b017fed9e02de418c2fbac9d75602a534be5/slime/backends/megatron_utils/arguments.py)对CP>1的allgatherCP限定支持的DSA模型类；稀疏attention的HCU后端可能进一步限定CP=1。确认model class、最终config及attention接口，而不是只export同名环境变量。

## 有效响应和三个策略概率

policy loss在[`loss.py`](https://github.com/THUDM/slime/blob/05e3b017fed9e02de418c2fbac9d75602a534be5/slime/backends/megatron_utils/loss.py)从模型logits取得logprob/entropy，与batch中old/rollout概率、advantages和response masks结合。prompt与pad不应进入response目标；EOS/truncation、动态过滤和mask变化也会改变分母。

`compute_policy_loss`实现clipped目标，负advantage的dualclip有单独界限；GSPO、CISPO、OPSM等配置走各自路径，不能统一称为同一PPO。使用TIS/mismatchmetrics时，policy梯度可能使用修改后的responsemask，reporting又保留原mask统计。排查“metric改善但loss变了”要同时保存两种mask及其denominator。

[`policy-mismatch文档`](https://github.com/THUDM/slime/blob/05e3b017fed9e02de418c2fbac9d75602a534be5/docs/en/advanced/policy-mismatch.md)用于理解生成backend与训练backend的概率差、重要性校正和取舍；校正不是绕过底层数值错误的工具。先确认相同权重、token/temperature和采样，再分析batch形态、低精度/融合算子或陈旧策略。

## loss wrapper 如何衔接 MCore

`loss_function(args, batch, num_microbatches, step_global_batch_size, logits)`明确使用**当前step全DP样本数**，避免按配置globalbatch或假定每rank持有相同样本数。它选择policy/value/SFT/custom，并可对loss函数做nonreentrantcheckpoint减少保存中间量。

- sample平均模式：将本地sample-mean和按 `num_microbatches / step_global_batch_size × DP(with CP)` 缩放，抵消MCore调度/归约的缩放。
- token模式：用配套tokennormalizer及CP因子交给MCore；源码的num_tokens逐sample将mask sum至少钳到1，不能把这个值描述为所有情况下完全等于mask有效token数。
- logging分别累计token分母或留下sample分母placeholder，由consumer用实际step_global_batch_size填入，不把每microbatch分母平均。

allgatherCP中有的rank可能只有padding或不贡献loss；源码添加 `0 * logits.sum()` 强制所有rank经过attentionautograd，使gather的backwardreduce-scatter都执行，避免其他rank死锁。删除零项不改变本地数学loss，却可能破坏collective参与协议。

## 性能与验证

packing减少padding和重复launch；CP延长可处理序列但引入远端attention/索引及gatherworkspace，不是所有内存都会除CP。lossrecompute减少中间存储又增加计算；必须看logprob/entropy等hotpath实际占比，不能仅依据功能存在决定开启。

[`test_loss_cp_invariance.py`](https://github.com/THUDM/slime/blob/05e3b017fed9e02de418c2fbac9d75602a534be5/tests/test_loss_cp_invariance.py)检查sample-mean路径在不同DP/CP下的梯度不变性；[`test_policy_loss.py`](https://github.com/THUDM/slime/blob/05e3b017fed9e02de418c2fbac9d75602a534be5/tests/test_policy_loss.py)手算dualclip并以AST检查eps_clip_c传到训练调用。一个是归约契约，一个是局部算法/接线，均不构成整模型HCU精度验证。

实际回归保留相同rollout固定数据，对比CP1/CP>1、不同microbatch、变长/全mask、重复group和token/samplemode，检查逐samplelogprob、gradnorm与更新参数；阶段后再做loss/reward对比。遇到错误先回退原packed/CP/融合路径，不随意改mask或训练目标。本页未实测HCU；更新需联动[总览](../../slime.md)、MCore依赖、attention实现与data接口。
