---
id: doc-ascend-mindspeed-2a84bd01e9ded13c1c6d
title: Ascend/MindSpeed / docs/en/features/qat_quant.md
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
path: docs/en/features/qat_quant.md
raw_sha256: 3f57339f422e92ebf8cf3346e30fbae443888ea67fc10e9af4a7abfbe46f7fca
sources: []
generated_body_sha256: ea13b7fa8db66b684dd6d9138eb8c52a15f2cc038aaeb9bb09cdd696e1adc9e7
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/qat_quant.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/qat_quant.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# QAT Quantization

## Background and Challenges

As large models continue to grow in scale, the memory required for their training and inference has become a hardware bottleneck. To address this, low-precision training strategies reduce memory usage by compressing weight precision, making them a key technical direction in large model efficiency optimization.

## Solution

For fine-tuning and training scenarios, quantization error is introduced by simulating the quantization-dequantization process of the MXFP4 format, while weights are still stored and updated in high precision (such as BF16), allowing the model to adapt to the precision loss caused by quantization. During forward propagation, weights are quantized to MXFP4 (E2M1 + block scaling) and then dequantized back to high precision for computation. During backward propagation, gradient straight-through estimation (STE) is typically used to enable gradients to effectively update the original weights, thereby adapting to the W4A16 low-precision strategy.

## Usage

The following modes are supported for enabling low-precision quantization. Add the corresponding configuration to the training script:

1. Enable MXFP4 low-precision quantization for all linear layers:
`--qat-scheme w4a16-mxfp4`.

2. Enable MXFP4 low-precision quantization only for MoE layers:
`--qat-scheme w4a16-mxfp4-moe-only`.

3. Enable MXFP8 low-precision quantization for all linear layers:
`--qat-scheme w8a16-mxfp8`.

4. Enable MXFP8 low-precision quantization only for MoE layers:
`--qat-scheme w8a16-mxfp8-moe-only`.

### Notes

Other settings or no settings will use the original strategy.

## Effects

Precision loss is controlled within an acceptable range.
