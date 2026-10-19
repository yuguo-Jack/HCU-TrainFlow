---
id: ecosystem/topics/mindspeed-llm-chunk-loss
title: MindSpeed-LLM：ChunkLoss 的 Logit 显存、梯度与入口区别
engine: mindspeed
kind: authored
stages:
- adapt
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-20'
coverage: selected source, official documentation and related PR reading; no HCU runtime validation
sources:
- source: ascend-mindspeed-llm
  path: mindspeed_llm/features_manager/memory/chunk_loss.py
  commit: 5a8ea03b12066067f39b1771782d12db236267ef
  sha256: 9e16aa4684213d3ef289d4662bad1123a08caae279e8052da4885f3d3755ab41
- source: ascend-mindspeed-llm
  path: mindspeed_llm/core/models/common/chunk_loss.py
  commit: 5a8ea03b12066067f39b1771782d12db236267ef
  sha256: bb31c1acb4fdd86af74798775ab902cdb179c23750f923797c8b14f41be0767c
- source: ascend-mindspeed-llm
  path: mindspeed_llm/fsdp2/features/chunkloss.py
  commit: 5a8ea03b12066067f39b1771782d12db236267ef
  sha256: c76c9ad4916cb19cde3ed2582a4919f3d4f4f23ed771aee455ec4ed46731dff1
- source: ascend-mindspeed-llm
  path: mindspeed_llm/fsdp2/train/trainer.py
  commit: 5a8ea03b12066067f39b1771782d12db236267ef
  sha256: 067ffa6493ca77d8d6252bff364d05becfd6d72feba7f8d0ebd49b7acdd17a67
- source: ascend-mindspeed-llm
  path: mindspeed_llm/fsdp2/models/common/modules.py
  commit: 5a8ea03b12066067f39b1771782d12db236267ef
  sha256: 722d3b3a59dd67e86477e15229557df0d682f3a358e7165ff9cea1adb742101b
- source: ascend-mindspeed-llm
  path: mindspeed_llm/fsdp2/models/qwen3/qwen3.py
  commit: 5a8ea03b12066067f39b1771782d12db236267ef
  sha256: 6ef04e7c376283c2d85b22dd02a800f2af2e9287538cb23624452f0d1a8bc578
- source: ascend-mindspeed-llm
  path: tests/mindspeed_llm/core/models/common/chunk_loss.py
  commit: 5a8ea03b12066067f39b1771782d12db236267ef
  sha256: bb31c1acb4fdd86af74798775ab902cdb179c23750f923797c8b14f41be0767c
- source: ascend-mindspeed-llm
  path: docs/en/pytorch/features/mcore/chunk_loss.md
  commit: 5a8ea03b12066067f39b1771782d12db236267ef
  sha256: 26acb0165f63a2f1e2ceba20489ce5a87c716dd2243ee53e2b0634c0fc3f4d3e
---

# MindSpeed-LLM：ChunkLoss 的 Logit 显存、梯度与入口区别

## 适用问题与两个入口

大词表模型的完整 logits `[B,S,V]` 在末层可能产生明显显存峰值。ChunkLoss 按 **序列维**分块计算 LM head / CE，避免所有 logits 同时驻留。源码注释有“feature dimension”表述，但当前 `torch.split(..., dim=1)` 对 `[B,S,H]` 是 S，分析应以真实布局为准。

MCore feature 注册 `--loss-compute-mode default|chunk` 与 `--loss-chunk-size`，实现位于 `core/models/common/chunk_loss.py`。FSDP2 trainer 使用另一份 `fsdp2/features/chunkloss.py`，由 `optimization_args.chunk_loss_size` 且 `stage=='pt'` 启用。**同一优化思想不意味着两个入口共享全部参数或覆盖 SFT。**现有 FSDP2预训练消费者是本专题重点链路。

## 配置→消费者→自定义 autograd

FSDP2 trainer `_build_chunk_loss` 将预训练已 shift 的 labels 保持原位，以 ignore_index 建 mask，`alpha=有效token总数`，沿序列分 chunk；每块使用同一个全局 alpha。trainer 将 loss_ctx / loss_mask 传入模型，Qwen3 forward→`LMHead.forward`；正常分支返回 logits，loss_ctx 分支直接返回 loss。不能让下游再构造完整 logits 或再次 shift。

`ChunkLoss.forward` 预分配 hidden-gradient、head-weight-gradient，逐块调用 `torch.func.grad_and_value(loss_forward, argnums=(0,1), has_aux=True)`，累加 chunk loss 与 weight gradient，并保存 input/weight gradient。backward 使用上游 grad_output 缩放这两个预计算梯度。head bias 当前明确不支持；DTensor/分片权重在 LMHead 的 local 处理仍要与 FSDP 状态所有权匹配。

## 收益与成本

临时 logits 峰值由完整 S 改为 chunk S，但仍保留全量 hidden gradient 和 head weight gradient，并没有把训练总内存降到“一个chunk”。小 chunk 增加 GEMM/CE 调用、weight gradient 累加与 launch，可能降低算力效率；大 chunk 更快却更占内存。先确认 LM head 是实际峰值再选它，避免为并非瓶颈的 logit 进行复杂改造。

性能比较记录 B/S/H/V、dtype、chunk size、有效token、peak allocated/reserved、head前反向和端到端步时，正式计时与首次 compile/分配分开。它不是通信 overlap 替代，也不自动解决 optimizer/activation 峰值。

## 数值与失败条件

比较普通 CE 与 chunk 路径的 loss、input/head gradients、optimizer step和阶段loss。边界包括 chunk不整除S、不同有效token、全忽略标签、梯度累计/grad scaling、shared/tied head、低精度和分片。每 chunk 各自求平均再相加会改变训练目标；需保持原全局分母。预训练外部 shift 与模型内部 SFT shift 不得叠加。

源码测试提供参考范围，未在本次 HCU执行。zip处理chunk时，label配置数量必须匹配 hidden chunks；存在 bias 或不支持分片/调用契约时应拒绝或回到普通实现，而不是静默漏最后一块。

## 回退与更新

回退普通 LMHead+CE 并保留数值基线/峰值代价；不能残留 loss_ctx 后又让 trainer 再计算一次 loss。修改两份ChunkLoss、model消费者、trainer normalization或feature参数时，同步复核[总览](../overview/engineering-guide.md)及对应单测，不把更新 MCore 文件算作 FSDP2已同步。

## 固定证据与复核范围

- [mindspeed_llm/features_manager/memory/chunk_loss.py](https://github.com/Ascend/MindSpeed-LLM/blob/5a8ea03b12066067f39b1771782d12db236267ef/mindspeed_llm/features_manager/memory/chunk_loss.py)
- [mindspeed_llm/core/models/common/chunk_loss.py](https://github.com/Ascend/MindSpeed-LLM/blob/5a8ea03b12066067f39b1771782d12db236267ef/mindspeed_llm/core/models/common/chunk_loss.py)
- [mindspeed_llm/fsdp2/features/chunkloss.py](https://github.com/Ascend/MindSpeed-LLM/blob/5a8ea03b12066067f39b1771782d12db236267ef/mindspeed_llm/fsdp2/features/chunkloss.py)
- [mindspeed_llm/fsdp2/train/trainer.py](https://github.com/Ascend/MindSpeed-LLM/blob/5a8ea03b12066067f39b1771782d12db236267ef/mindspeed_llm/fsdp2/train/trainer.py)
- [mindspeed_llm/fsdp2/models/common/modules.py](https://github.com/Ascend/MindSpeed-LLM/blob/5a8ea03b12066067f39b1771782d12db236267ef/mindspeed_llm/fsdp2/models/common/modules.py)
- [mindspeed_llm/fsdp2/models/qwen3/qwen3.py](https://github.com/Ascend/MindSpeed-LLM/blob/5a8ea03b12066067f39b1771782d12db236267ef/mindspeed_llm/fsdp2/models/qwen3/qwen3.py)
- [tests/mindspeed_llm/core/models/common/chunk_loss.py](https://github.com/Ascend/MindSpeed-LLM/blob/5a8ea03b12066067f39b1771782d12db236267ef/tests/mindspeed_llm/core/models/common/chunk_loss.py)
- [docs/en/pytorch/features/mcore/chunk_loss.md](https://github.com/Ascend/MindSpeed-LLM/blob/5a8ea03b12066067f39b1771782d12db236267ef/docs/en/pytorch/features/mcore/chunk_loss.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
