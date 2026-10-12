---
id: engines/llamafactory/topics/sft-packing-and-multimodal
title: LlamaFactory SFT：packing、attention 与多模态位置契约
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
  path: src/llamafactory/data/processor/supervised.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: f1b4b8db32179f7471e7c0bf45806533f8cabe8ade98d3a6b427d80a94b959cf
- source: hiyouga-llama-factory
  path: src/llamafactory/data/collator.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: d9c0c4d5583001c9e2f9825de7dbf2f57cd7c724d0b3c70b4e9cd61cda08edb2
- source: hiyouga-llama-factory
  path: src/llamafactory/train/sft/workflow.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: aaa1f92b66c4985fe1c1d47a6c28831a1cd0b107d77e3819c2ea174e37a1384b
- source: hiyouga-llama-factory
  path: src/llamafactory/model/model_utils/attention.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 6d96c69ab918e356ad6f851431a4e71e90a702a584bff05d24d06d29d74ccee4
- source: hiyouga-llama-factory
  path: tests/data/processor/test_supervised.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 31424b62cf7bd38b6990e80119e7a744514733e077c751121b914ae4d7972ff0
- source: hiyouga-llama-factory
  path: tests/data/test_collator.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 36db2247be20161d673f75f54e1ce5eb21bc4627b56e41822112d13984ffaa69
- source: hiyouga-llama-factory
  path: tests/model/model_utils/test_packing.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 8f55134b4c16d30961d2ce06b182b44592150c113ee43b3b2b44ed1fb1760295
---

# LlamaFactory SFT：packing、attention 与多模态位置契约

## 问题、适用范围与调用链

packing 的目标是在保留有效监督和样本隔离的前提下减少 padding。legacy 路径为 `run_sft → get_dataset → Supervised/PackedSupervisedDatasetProcessor → SFTDataCollatorWith4DAttentionMask → model → CustomSeq2SeqTrainer`。本页阅读固定 `1fded918ac4723ac9966363f51ed4500866c5d1d` 的 legacy 机制；v1 CP/chunk-loss 见 [另一专题](v1-cp-and-chunk-loss.md)，总览见 [工程页](../../llamafactory.md)。

## 模板与监督目标先于布局优化

[`_encode_data_example`](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/src/llamafactory/data/processor/supervised.py)先让 mm plugin 处理 messages/media 与 token，再由 template 产生多轮 source/target。`train_on_prompt` 决定 prompt 是否监督；`mask_history` 优先截取最后轮次并屏蔽早期 target。`efficient_eos` 还会改变 source label 与结尾目标。

长度截断由 source/target 的联合预算控制。字段解析错误、模板选错或 mask_history 改变都能使 loss 降低/吞吐上升，却不代表同一训练任务变快。基线必须固定模板、截断、labels 和有效 target 数。

## Packing 的真实 metadata

`PackedSupervisedDatasetProcessor` 用 `greedy_knapsack` 组合长度不超过 cutoff 的样本，拼 token/labels，position IDs 按每个子序列重新从零生成。输出长度为 `cutoff_len+1` 的实现细节与 next-token/attention 处理相关，不应按直觉改回 cutoff。

| 字段/条件 | 本轮源码行为 | 需要核对 |
| --- | --- | --- |
| 普通 packing | attention_mask 对拼接样本多为 1 | 模型可能允许跨子样本 attention；不能称它与隔离样本完全等价 |
| `neat_packing` | mask 用子序列索引 1,2,…，padding 为0 | block-diagonal/varlen 必须消费这些边界 |
| `PackingParams.sequence_boundaries` | 累计子序列位置 | 与 input/position/labels 同步 |
| image/video/audio subseq IDs | 每个媒体属于哪个子序列 | mRoPE 与媒体展开不能跨样本混配 |
| right padding | label IGNORE_INDEX；position 补0 | 有效 target 计数与 backend unpad 一致 |

本轮 metadata 只在 neat_packing 路径生成；空媒体列表用 sentinel 避免 dataset concat 错误。这是数据传输约定，不应当成真实媒体索引。

## Collator 与 attention 分支

[`prepare_4d_attention_mask`](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/src/llamafactory/data/collator.py)把“同子序列、非 padding、causal”的条件组成 4D additive mask；`block_diag_attn` 且非 FA2 时使用该路径，大小按序列平方增长，必须记入显存。

neat-packing+FA2 路径要求 batch size=1，部分 model type 明确不支持。collator 可删 padding位置，同时选择 `attention_mask=None` 让 Transformers 使用 position IDs 识别 packed varlen。注释仍提示 FA3/FA4 兼容需另外处理，因此不能只把 backend 名替换成新版本就认为完整支持。

非 FA2 路径的 `DataCollatorForSeq2Seq(pad_to_multiple_of=8)` 可能补 input/mask 而不补 position IDs；当前 collator 右补 position IDs，避免 q 与 cos/sin 长度不匹配。这里的补0只作用于已 masked 的末尾，不能用它掩盖真正的子样本位置错误。

## 多模态 mRoPE 为什么需要逐子序列处理

媒体 token 数和 grid/layout 决定 mRoPE。`_compute_rope_position_ids_with_packing` 按 sequence boundaries 和媒体 subseq IDs 切出每段媒体/语言输入，调用各段 RoPE，再沿最后序列维拼接；2D与3D位置的 batch维不同。把全 pack 当作单样本计算位置，会把后段媒体和前段 offset 混在一起。

dummy image 是用于保持多模态模型调用/分布式一致性的占位路径；它还会带额外 padding/mask。验证时要区分真实媒体与 dummy，不用“模型里出现了 pixel_values”推断本批有真实视觉数据。

## 性能预期与上限

packing 减少 padding，FA2 varlen 还能减少 padding对应的注意力工作；4D mask 可能付出高额物化/带宽成本。多媒体 processor/位置计算、CPU拷贝和媒体 tower 保持工作量，不能按语言 token压缩比例直接预测完整训练收益。

报告有效训练 token/step、处理 token、真实样本数、媒体规模、step墙钟、峰值显存以及实际attention backend。若主要成本在 vision encoder 或 data processor，优化packing可能几乎不改善端到端，这需从profile解释。

## 验证、排障与回退

逐项对照原样本与pack的 token/labels/有效 target，检查任一子样本不能访问别段，FA2/SDPA路径的位置/输出/梯度一致性；VLM覆盖多个子样本不同媒体数、无媒体/dummy、3D mRoPE、末尾pad。模板/attention替换后的阶段loss需对照已有基线。

官方 [supervised processor tests](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/tests/data/processor/test_supervised.py)、[collator tests](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/tests/data/test_collator.py)和 [packing tests](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/tests/model/model_utils/test_packing.py)是回归入口，本文未执行HCU测试。RoPE长度报错先对每个字段实际shape；loss异常先检查mask/分段，避免直接认定attention kernel数值错误。

遇到未支持的模型/backend，退回已验未packing路径或兼容neat实现，再定位缺口；保留吞吐/内存差异，不将关闭样本隔离作为同语义优化。更新同时复核processor、collator、model attention/packing patch、模板和测试，不能只刷新README支持表。
