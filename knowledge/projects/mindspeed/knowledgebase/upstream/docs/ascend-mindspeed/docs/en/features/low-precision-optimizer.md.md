---
id: doc-ascend-mindspeed-2de3cbed2ca89fe77ea8
title: Ascend/MindSpeed / docs/en/features/low-precision-optimizer.md
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
path: docs/en/features/low-precision-optimizer.md
raw_sha256: 4e5a6e503a7c2290b3d6d464f31abe90202088161a77aabbf9f55b9ba4a78f5f
sources: []
generated_body_sha256: fa5dfbcc4a5df5b35769a014e207c5915534d8c33adc2cbec43f144e923bb497
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/low-precision-optimizer.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/low-precision-optimizer.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Low-Precision Optimizer

## Problem Analysis

In large model training scenarios, Adam-type optimizers continuously save parameter copies, gradients, and first- and second-order momentum of the optimizer using FP32 full-precision data types during training, resulting in significant static memory usage.

![Adam Optimizer Diagram](../figures/adam_optimizer.png)

## Solution

Quantize and compress the data stored in the optimizer to low precision respectively, to reduce memory usage:

1. Quantize the momentum in the optimizer to the E4M3 format FP8, HiF8, or MXFP8 data type, reducing momentum memory usage.
2. Quantize gradients to half-precision FP16, reducing gradient memory usage.
3. Adapt the existing parameter replica reuse algorithm to reduce parameter replica memory usage.

![Low Precision Optimizer Diagram](../figures/low_precision_optimizer_en.png)

Before the optimizer updates parameters, the quantized data must first be dequantized to FP32 to ensure computational accuracy. After the update is complete, it is quantized back to low precision. The computation workflow is shown in the following diagram:

![Low Precision Optimizer Workflow Diagram](../figures/low_precision_optimizer_workflow.png)

## Usage

Set `--quant-states <fp8|hif8|mxfp8>` to enable optimizer momentum quantization. The quantization data type can be `fp8`, `hif8`, or `mxfp8`.

Set `--quant-grads` to enable gradient quantization compression. Gradients are quantized from the FP32 data type to FP16.

Compatible with the `reuse-fp32-param` feature

## Effects

Reduces the static memory usage of the optimizer.

## Usage Constraints

1. `--quant-grads` does not support `--gemm-gradient-accumulation-fusion`. You need to enable `--no-gradient-accumulation-fusion` to disable gradient accumulation fusion.
2. `--quant-grads` and `--quant-states` do not support `--swap-optimizer`. To use the low-precision optimizer, you need to disable the `--swap-optimizer` feature.
