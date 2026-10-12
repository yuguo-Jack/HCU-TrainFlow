---
id: doc-ascend-mindspeed-4d6c04b67a76e3453a67
title: Ascend/MindSpeed / docs/en/features/swiglu.md
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
path: docs/en/features/swiglu.md
raw_sha256: 66ae0f9d3927b5d6ab5faecd10d09875804c29fe6570f03dfdc0b5ca74a6f168
sources: []
generated_body_sha256: 20a39a28620552fcde87f8f61de5d6aab6e6dd261f8dbe68d9db7d34ecee47e8
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/swiglu.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/swiglu.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# swiglu Fusion

## Background and Challenges

SwiGLU (Swish-Gated Linear Unit) is commonly used in the activation layers of large language models such as LLaMA, LLaMA2, and Baichuan. However, since the PyTorch standard library lacks a direct operator interface for SwiGLU, models typically implement SwiGLU functionality by combining a series of basic operators, which results in suboptimal execution efficiency.

## Solution

To address this challenge, MindSpeed applies fusion optimization to the SwiGLU operation, encapsulating it as a high-performance fused operator that significantly reduces the number of data transfers between memory and the need for temporary data storage. For the operator interface, see [swiglu](../ops/swiglu.md).

## Application Scenario

When the model design uses SwiGLU as the activation function for the MLP layer, and the training script already includes the following configuration option:
`--swiglu`

## Usage

To enable SwiGLU fusion optimization, add the following parameter configuration to the training script:
`--use-fused-swiglu`

Under the mcore branch, only enabling this fused operator is supported.

## Effects

On the Llama-2-7b model, enabling the fusion-optimized SwiGLU operator saves approximately 16.6% memory and improves performance by about 4.7%, which not only effectively reduces memory consumption but also significantly enhances the operational efficiency of model training.
