---
id: doc-ascend-mindspeed-915dc3b75a0563fe06f0
title: Ascend/MindSpeed / docs/zh/features/alibi.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed
commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
path: docs/zh/features/alibi.md
raw_sha256: 48ad6c5dfea93008452badbd621471c558d6afe8beb3816379d0e8029163cc9e
sources: []
generated_body_sha256: c465088324151fa91c23723d8e41eac41fbdfe6eb9cb06468e56f658f27a5494
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/alibi.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/alibi.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Alibi 位置编码

## 背景与挑战

当大模型在训练和预测时的输入长度不一致时，模型的泛化能力会下降。若外推能力不佳，大模型在处理长文本或多轮对话时的效果就会受到限制。正弦位置编码的外推能力比较弱，RoPE（Rotary Position Embedding）的外推能力有一定提高但仍然有限。

## 解决方案

支持Alibi位置编码，提高模型外推能力。

### 解决思路

Alibi算法给attention score添加了一个预设的线性偏置矩阵（如下图所示），使模型能够理解输入之间的相对位置关系。由于位置信息直接作用于attention score上，位置差异性被突出，使模型具有较强的外推能力。
<p align="center"> <img src="../figures/alibi.png" height="180px" width="400px" alt="alibi位置编码"></p>

[原文链接](https://arxiv.org/pdf/2108.12409)

## 使用方法

（1）当前alibi特性只支持开启Flash Attention v2情形，请确保开启`--use-fusion-attn-v2`。

（2）对于开启`--use-fusion-attn-v2`特性的情形下，需要设置`--position-embedding-type alibi`和`--alibi-fusion-attn-type 2`。`--alibi-fusion-attn-type`目前仅支持取0或2，
0表示生成alibi后传入，1暂不开放， 2表示核内生成。
如果要设置alibi为对角线对称取反，则需设置`alibi_diagonal_opposite`，反之（亦是默认情况，且与2时核内生成一致）无需进行设置。

（3）目前alibi位置编码已经支持ring-attention长序列并行，当前只支持mask为causal的场景，以及`--alibi-fusion-attn-type`为2的压缩模式。暂不支持Ulysses长序列并行和混合长序列并行。

（4）开启`--use-fusion-attn-v2`特性和长序列并行时，alibi编码不支持开启dropout。

## 使用效果

模型外推能力提高。
