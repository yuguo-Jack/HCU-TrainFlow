---
id: doc-ascend-mindspeed-llm-58dd3658b3a024da60a0
title: Ascend/MindSpeed-LLM / docs/zh/pytorch/features/mcore/recompute_relative.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: 2fed626696175480ae1ab3342a94017301a25209
path: docs/zh/pytorch/features/mcore/recompute_relative.md
raw_sha256: 7f4c8eaf869bf04c425d7eb19133adeb4c5e1d021391e302a38bcfd57152774d
sources: []
generated_body_sha256: 7b6e7f649732e06850fcdccd3da6a000343cbafa7c8f75086167f5d3305a2c52
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/zh/pytorch/features/mcore/recompute_relative.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/zh/pytorch/features/mcore/recompute_relative.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# 重计算

为了减少在训练大模型时的 NPU 内存使用，MindSpeed-LLM 支持多种形式重计算（recomputation）。

## 全量重计算

对于内存非常有限的情况，全量重计算只保存 Transformer 层或层组的输入激活值，其他部分全部重新计算。要启用全量重计算，请使用 `--recompute-granularity full`。在该模式下，有两种重计算方法：均匀（uniform）和分块（block），可以通过 `--recompute-method` 参数选择。

**均匀方法**: 

`--recompute-method uniform`：将Transformer 层均匀划分组（每组大小--recompute-num-layers），按组存储输入和激活值。

**分块方法**: 

`--recompute-method block`：将前 --recompute-num-layers 个 Transformer 层重计算，剩余层不进行重计算。

## 选择性重计算

选择性重计算（推荐使用）：只重计算Transformer 中的 `core attention` 部分，将占用较少内存存储空间且重计算开销较高的激活保留在内存中，并将占用较多内存存储空间但重新计算开销相对较低的激活重新计算。

可通过 `--recompute-granularity selective` 来使能。

## 激活函数重计算

脚本中添加 `--recompute-activation-function` 可开启激活函数重计算。

添加 `--recompute-activation-function-num-layers ${num}` 可指定激活函数重计算的层数。

激活函数重计算可以与全重计算同时开启：

1. 同时开启时，仅支持 --recompute-method 为 `block`

2. 同时开启时，会按照指定的全重计算和激活函数重计算的层数做各自类型的重计算，即不会有一层既做全重计算又做激活函数重计算。

（注意点：执行优先级是先计算全重计算层，后计算激活函数重计算层。在流水线并行未开启的情况下，全重计算层数和激活函数重计算层数之和应该等于总层数。）

详细的算法原理可参见 [Megatron 重计算](https://arxiv.org/abs/2205.05198)、MindSpeed [激活函数重计算](https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/activation-function-recompute.md) 章节。
