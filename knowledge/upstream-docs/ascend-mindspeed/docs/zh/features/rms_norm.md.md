---
id: doc-ascend-mindspeed-16c9e4b43315398ac1be
title: Ascend/MindSpeed / docs/zh/features/rms_norm.md
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
path: docs/zh/features/rms_norm.md
raw_sha256: a599a1d337d5effdaaca99e979e9727f787c5ec3775ba255d8021305d88af394
sources: []
generated_body_sha256: bbd7f23d64479c5974a1550751cea31a719cf98cc4ddf3a3181abe523df30613
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/rms_norm.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/rms_norm.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# rms_norm融合优化

## 背景与挑战

在诸如LLaMA、LLaMA2和Baichuan等大型语言模型（LLM）中，RMSNorm（Root Mean Square Norm）作为一种归一化技术被广泛应用。然而，由于PyTorch框架本身未直接提供RMSNorm运算符接口，模型中常以自定义形式实现RMSNorm，这在一定程度上影响了执行效率。

## 解决方法

MindSpeed 针对上述情况，对RMSNorm操作进行了融合优化，将其集成到单个运算符中，有效减少了数据传输次数和临时存储需求。算子接口见[rms_norm](../ops/rms_norm.md)。

## 使用场景

当模型选用RMSNorm作为其归一化方法，并且训练脚本中已包含以下配置时：
`--normalization RMSNorm`。

## 使用方法

启用RMSNorm融合优化，需在训练脚本中加入以下参数配置：
`--use-fused-rmsnorm`
Mcore分支下该算子仅支持使能融合特性。

## 使用效果

在Llama-2-7b模型下，启用融合算子RMSNorm后，内存节省约12%，性能提升约2.7%，不仅能够有效节省内存资源，还能提升模型训练效率。
