---
id: doc-ascend-mindspeed-73e34e928472120cd02a
title: Ascend/MindSpeed / docs/zh/features/qat_quant.md
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
path: docs/zh/features/qat_quant.md
raw_sha256: 08ffcd9532af93bee6fb9f9ae240ac3466381f022059943f7e55985f20788bc6
sources: []
generated_body_sha256: c3fe3071acc20740733d6d3296a383ea8f0d51a2656f1cd91ab264ab62112205
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/qat_quant.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/qat_quant.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# QAT量化

## 背景与挑战

随着大模型规模持续增长，其训练和推理所需的显存已成为硬件瓶颈。为此，低精训练策略通过压缩权重精度来降低显存占用，使其成为大模型效率优化中一个关键技术方向。

## 解决方案

针对微调和训练场景，通过模拟MXFP4格式的量化-反量化过程引入量化误差，但权重仍以高精度（如BF16）存储和更新，从而让模型适应量化后的精度损失。前向传播中，权重会被量化为MXFP4（E2M1+块缩放）再反量化回高精度参与计算，反向传播则通常借助梯度直通估计（STE），使梯度能有效更新原始权重，从而适配W4A16的低精策略。

## 使用方法

分别支持以下模式开启低精量化功能，需在训练脚本中加入以下配置：

1. 所有线性层使用开启MXFP4低精量化功能：
`--qat-scheme w4a16-mxfp4`

2. 仅在MOE层使用开启MXFP4低精量化功能：
`--qat-scheme w4a16-mxfp4-moe-only`

3. 所有线性层使用开启MXFP8低精量化功能：
`--qat-scheme w8a16-mxfp8`

4. 仅在MOE层使用开启MXFP8低精量化功能：
`--qat-scheme w8a16-mxfp8-moe-only`

### 注意

其他设置或不设置均会使用原始策略。

## 使用效果

精度损失控制在可接受范围
