---
id: doc-ascend-mindspeed-9a1f5d8d3e363359d946
title: Ascend/MindSpeed / docs/en/features/rms_norm.md
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
path: docs/en/features/rms_norm.md
raw_sha256: 7db37a2d9ebfed5d0b268ddb0b41c9c29f341136d69d8dd40d31187dcb9bbd5a
sources: []
generated_body_sha256: bfec09833055101ab83ed0a82b3d4ce7946bf44e7af18cec3441e4a202b7ed7f
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/rms_norm.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/rms_norm.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# rms_norm Fusion

## Background and Challenges

In large language models (LLMs) such as Llama, Llama2, and Baichuan, RMSNorm (Root Mean Square Norm) is widely used as a normalization technique. However, since the PyTorch framework does not natively provide an RMSNorm operator interface, RMSNorm is often implemented in a custom manner within models, which impacts execution efficiency to some extent.

## Solution

To address this, MindSpeed performs fusion optimization on the RMSNorm operation, integrating it into a single operator, which effectively reduces the number of data transfers and temporary storage requirements. For the operator interface, see [rms_norm](../ops/rms_norm.md).

## Application Scenario

When the model uses RMSNorm as its normalization method and the training script already includes the following configuration:
`--normalization RMSNorm`.

## Usage

To enable RMSNorm fusion optimization, add the following parameter configuration to the training script:
`--use-fused-rmsnorm`
Under the Mcore branch, this operator only supports enabling the fusion feature.

## Effects

For the Llama-2-7b model, after enabling the fused operator RMSNorm, memory savings are approximately 12% and performance improves by about 2.7%, which not only effectively conserves memory resources but also enhances model training efficiency.
