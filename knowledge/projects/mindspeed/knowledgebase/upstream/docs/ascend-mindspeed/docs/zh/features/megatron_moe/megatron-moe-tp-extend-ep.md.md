---
id: doc-ascend-mindspeed-e5af64cdf2cd51208b0b
title: Ascend/MindSpeed / docs/zh/features/megatron_moe/megatron-moe-tp-extend-ep.md
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
path: docs/zh/features/megatron_moe/megatron-moe-tp-extend-ep.md
raw_sha256: 5760c920f3ad193f1ae0623a0da6af8b3460243062b3868d3107c3e5e40b8406
sources: []
generated_body_sha256: 6085f3992c219758319d36cb7edd048dc14b8e0ebf51cb7d7adb30fa02181825
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/megatron_moe/megatron-moe-tp-extend-ep.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/megatron_moe/megatron-moe-tp-extend-ep.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Megatron MoE TP拓展EP

## 背景与挑战

开启TP+EP后，专家层TP组切分专家参数，MoE细粒度小专家场景TP切分后GMM算子效率下降严重。

## 解决方案

针对小专家场景TP切分后GMM算子效率下降问题，专家层TP组不切分专家参数，切分专家数量。

## 使用场景

细粒度小专家，类DeepSeek-V2模型，每个专家的参数量较小。

## 使用方法

- 开启特性：添加`--moe-tp-extend-ep`启用该功能。
- 必选配套参数：必须同时确保开启以下两个参数：
    - `--moe-permutation-async-comm`
    - `--moe-grouped-gemm`（注意：目前仅支持Grouped MLP）
- 配置约束：需要确保`--num-experts`能被`--tensor-model-parallel-size`与`--expert-model-parallel-size`的乘积整除。

> [!NOTE]
>
> - 当前该特性不支持MoE Token drop and pad模式，即`--moe-expert-capacity-factor`需要为None。
> - 当前仅支持alltoall_seq dispatcher。

## 使用效果

通过避免TP切分专家参数，提高小专家场景GMM算子效率，从而提高模型整体训练性能，在类DeepSeek-V2万亿参数级别的MoE模型下，并且为细粒度小专家，性能最高提升10%以上。
