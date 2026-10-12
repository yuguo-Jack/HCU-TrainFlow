---
id: doc-ascend-mindspeed-54de256e84664340c50f
title: Ascend/MindSpeed / docs/zh/features/swiglu.md
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
path: docs/zh/features/swiglu.md
raw_sha256: 24f49affb14ed95d9e579696082a04daa7150b3ae3424373a34a6cde20f8660e
sources: []
generated_body_sha256: 2e2e8b555af0da93e85f0f4e9c5e06b64b8b787ea4495b996e6a121505dfbb89
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/swiglu.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/swiglu.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# SwiGLU融合优化

## 背景与挑战

SwiGLU（Swish-Gated Linear Unit，Swish门控线性单元激活函数）常见于LLaMA、LLaMA2、Baichuan等大型语言模型中激活层。然而，由于PyTorch标准库中缺乏直接支持SwiGLU的算子接口，模型通常会以一系列基础算子组合的方式来实现SwiGLU功能，这种方式的执行效率并不理想。

## 解决方法

为应对这一挑战，MindSpeed对SwiGLU操作进行了融合优化，将其封装为一个高性能的融合算子，显著减少了数据在内存间的传输次数以及临时数据的存储需求。算子接口见[swiglu](../ops/swiglu.md)。

## 使用场景

当模型设计中采用了SwiGLU作为MLP层的激活函数，并且训练脚本中已包含以下配置项：
`--swiglu`

## 使用方法

启用SwiGLU融合优化，需在训练脚本中加入以下参数配置：
`--use-fused-swiglu`

mcore分支下仅支持使能该融合算子。

## 使用效果

在Llama-2-7b模型下，通过启用融合优化后的SwiGLU算子，内存节省约16.6%，性能提升约4.7%，不仅可以有效降低内存消耗，还能大幅提升模型训练的运行效率。
