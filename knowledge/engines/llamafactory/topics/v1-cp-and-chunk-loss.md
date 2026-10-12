---
id: engines/llamafactory/topics/v1-cp-and-chunk-loss
title: LlamaFactory v1：Ulysses CP、token 归一化与 chunked linear-CE
engine: llamafactory
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
- source: hiyouga-llama-factory
  path: src/llamafactory/v1/trainers/sft_trainer.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 9fe8f9fbde544a0440a836a5a0e7f252ec408671ea27dbe6dc7933200441b00c
- source: hiyouga-llama-factory
  path: src/llamafactory/v1/core/base_trainer.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 6c7102d5196274cfedf7e0137f885be43499a28bf80f3447c29ae8d3db26dc79
- source: hiyouga-llama-factory
  path: src/llamafactory/v1/plugins/model_plugins/chunk_loss.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 927bce64a084ff7e91e138f20be18cbf12a09b9ace788528c2a1d75312bf4350
- source: hiyouga-llama-factory
  path: src/llamafactory/v1/plugins/model_plugins/parallelization/batch.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 5a39296418d27be854272d2e1e29cfc4a13ca0d7db29ff2eb3c714f108c663e9
- source: hiyouga-llama-factory
  path: src/llamafactory/v1/plugins/model_plugins/parallelization/sequence_parallel.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 192feab0b5d261f2329b0895cfaa5372e364822ddf0096e796b3bedfab120247
- source: hiyouga-llama-factory
  path: src/llamafactory/v1/plugins/model_plugins/parallelization/ulysses.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: f7567a53a68bff026176b2b0c407a5a718eb17b912482bb95638b8aba236e90f
- source: hiyouga-llama-factory
  path: src/llamafactory/v1/plugins/trainer_plugins/distributed/deepspeed.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: a2ef30911f43fcdc48ded55a4047eb7e28cca29a70b7e76d797b8b68970208aa
- source: hiyouga-llama-factory
  path: tests_v1/plugins/model_plugins/test_chunk_loss.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: ca9e673b2f6fc19c53bb76547e17fb24d6cc18d2f36167cee6fae55e8ef1a20e
- source: hiyouga-llama-factory
  path: tests_v1/plugins/model_plugins/test_ulysses_cp.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: a59849e81879a56abbb540de393485786df8faa839e1ad6785a759a79d2285b9
---

# LlamaFactory v1：Ulysses CP、token 归一化与 chunked linear-CE

## 问题与真实入口

当长序列激活或 `tokens×vocabulary` logits 成为显存瓶颈，v1提供CP和chunk-loss组合。它们对应不同内存对象：CP分摊语言序列计算/激活；chunk loss避免一次物化完整输出logits。实际入口先确认 `USE_V1=1`；legacy trainer不自动获得这套插件。固定源码 `1fded918ac4723ac9966363f51ed4500866c5d1d`，总览见 [LlamaFactory](../../llamafactory.md)。

## 配置、batch所有权与调用链

`run_sft`创建ModelEngine/DistributedInterface；`SFTTrainer.__init__`在distributed wrapping前安装`chunk_loss_size`插件。`compute_loss`按`cp_size`选择 sequence-parallel loss；CP=1时有chunk插件走其compute_loss，否则按shifted logprob和loss_weights计算。

[`prepare_sequence_parallel_batch`](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/src/llamafactory/v1/plugins/model_plugins/parallelization/batch.py)将全语言序列补至CP整除，**先全局shift labels/weights，再按CP shard**；不能每shard独立shift使边界目标丢失。图像pixel/grid、音频feature等encoder-owned tensor保持原布局/复制，只有列举的language tensor补序列padding。VLM需要先由outer model融合媒体与语言，再在正确hook处切分。

返回对象明确包含 full model inputs、local shifted labels/weights与global weight sum。真3D mRoPE与广播复制的text position IDs不同：后者可恢复2D用于varlen边界，前者不应当作packed标记。

## Ulysses通信与分支一致性

[`UlyssesAttention.forward`](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/src/llamafactory/v1/plugins/model_plugins/parallelization/ulysses.py)分别对Q/K/V执行all-to-all，从local sequence/full heads变为full sequence/sharded heads，attention后再反向all-to-all。非causal多模态encoder attention直接走原函数，不套语言Ulysses。

HF可能将某rank的all-ones mask优化成None，而另一rank仍有padding。当前实现先all-gather“本rank是否有mask”布尔，再让所有rank进入同一mask collective分支；缺mask的rank贡献all-ones。直接按本rankNone判断会造成collective次序不一致/死锁。

Q/K/V仍是三次all-to-all，源码TODO的合并不是已实现优化。CP带来的收益和通信代价要基于序列长度、heads/GQA、设备互联和实际varlen实现；不能用卡数直接预测线性加速。

## Loss分子/分母与外层累积

`sequence_parallel_loss`要求自定义loss函数返回**local differentiable FP32 weighted sum**，不再次shift、normalize或执行CP collective。它用可微all-gather聚合标量分子，除以global weight sum；不同shard有效监督量不均时，局部mean等权平均是错误的。

CP loss返回后，`BaseTrainer.fit`仍根据step/microbatch有效token及DP reduction语义缩放。DeepSpeed路径由Accelerate的sync boundary推进step，不能再外加一次optimizer.step。改CP、batch/累积或后端时使用同一完整batch做梯度/参数更新对照，分别追CP、DP和accumulation三层比例。

## Chunked linear-CE的实现与限制

[`ChunkLoss`](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/src/llamafactory/v1/plugins/model_plugins/chunk_loss.py)替换output head forward，在激活状态将hidden分块做linear→FP32CE→weighted sum。内部forward已逐chunk算出所需梯度，保存hidden/head/bias梯度；外部backward乘上游grad_output。head/bias梯度先FP32累加，最后转回dtype，避免每chunk的BF16累加舍入。

它省去完整 `T×V` logits的峰值，但需要完整hidden梯度、head梯度（含FP32累积）与chunk workspace，并增加分块launch/重复CE的成本。不是所有模型都能挂：output embedding必须为plain `torch.nn.Linear`，每次forward只调用head一次，head后不能变换logits；模型forward hook检查输出对象与version counter。带softcap、特殊parallel head或自定义输出转换的模型需要独立实现，不能移除检查强行通过。

训练forward的`outputs.logits`在激活路径承载scalar loss，外层返回该对象以保留DDP/FSDP包装后的反向hooks；普通非训练forward仍执行原head输出真实logits。旁路返回内部state.loss可能绕开wrapper hook，这正是契约之一。

## 验证与回退

官方 [chunk loss tests](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/tests_v1/plugins/model_plugins/test_chunk_loss.py)覆盖eager损失/梯度、冻结head、外部loss scale、无监督样本、普通forward保留logits和DDP输出hook。[Ulysses tests](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/tests_v1/plugins/model_plugins/test_ulysses_cp.py)覆盖loss、position/layout、VLMencoder绕过、target shift等，部分需真实分布式设备。本文只精读测试设计，未在HCU执行。

任务至少比较CP=1/目标CP、chunk开关、完整/不完整累积窗口的loss/梯度/更新，测峰值显存和step时间，检查packed边界/mRoPE/zero-supervision。OOM可能来自FP32head-grad或其他全量物化而非logits，按实际memory snapshot归因。卡住先看mask路径和group；输出hook报错先查head类型/调用次数/post-head变换。

回退顺序按缺口选择：chunk关掉保留CP，或CP关掉保留chunk，分别与已验基线比较；backend未支持时回到兼容配方。更新需联动SFTTrainer、BaseTrainer、batch/hook、Ulysses/sequence loss、chunk-loss、distributed backend与tests_v1。关联 [PR #10762](../../../prs/hiyouga--LlamaFactory/PR-10762.md) 时核对最终代码，不把该PR的v1能力扩展到legacy。
