---
id: doc-ascend-mindspeed-9536c70889f9034c3fb6
title: Ascend/MindSpeed / docs/zh/features/eod-reset.md
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
path: docs/zh/features/eod-reset.md
raw_sha256: 484a5c32ffa59faba1b2ae7ef8798da16167f33b94d0ef88e6044340e9556ffe
sources: []
generated_body_sha256: e913276b4b6f28ca3f6a8df0db96296ad4afd1b207b485286f56b568f162d2ed
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/eod-reset.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/eod-reset.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# 支持EOD Reset训练场景

## 背景与挑战

通常一个批次中输入进模型的文本序列是由多个文档（doc）拼接得到。在默认情况下，多个文档被视为同一序列，互相间的self attention没有掩盖。在特定情况下，多个文档间要求独立，文档间不能互相做self attention，在这种情况下attention mask和position ids需要在每个文档结束的位置（EOD）被重新设置。--reset-position-ids参数关闭时，整个序列计算位置编码；开启时，在每个序列内独立计算位置编码。

## 解决方案

通过调用底层flash-attention算子的可变长模式，支持EOD Reset训练场景。同时在EOD Reset训练场景下，支持Ring Attention长序列并行，对超长序列场景进行加速。

## 使用方法

1. 数据准备
    - 首先确保每一个文档的末尾都添加了EOD Token。
    - 对于`--attention-mask-type`为causal的情况，因为内部实现的需求，每个子序列的长度会被在线pad到CP*lcm(2, TP)的倍数，其中lcm为最小公倍数。该场景需要开启`--variable-seq-lengths`，因为pad会使得序列长度发生变化。

2. 参数设置
    - 打开`--reset-attention-mask`选项。
    - 使用`--reset-position-ids`选项，来代表位置编码是否reset。
    - `--attention-mask-type`可以指定为causal或者general，两者计算结果等价。causal为加速实现，general为基线方案。

> [!NOTE]
>
> Ascend EOD Reset训练场景下mask-type为general时，Ring/Hybrid Attention比Ulysses下降较多，为正常现象；mask-type为causal时，使用加速方案。
