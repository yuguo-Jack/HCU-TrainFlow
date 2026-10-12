---
id: doc-ascend-mindspeed-288bf4c393f1108386b6
title: Ascend/MindSpeed / docs/en/features/ops_flops_cal.md
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
path: docs/en/features/ops_flops_cal.md
raw_sha256: 9ddd3646a4530b8bed61fb275452ff74fc3f874a0b03d04a8bf6d02e9898ab99
sources: []
generated_body_sha256: 48d16a4648bade1c1c2163aea151537814fa6c48d13e3a634f5fb7fecef244ef
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/ops_flops_cal.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/ops_flops_cal.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# TFLOPS Calculation

## Background and Challenges

MFU for large models is currently calculated by dividing the framework-printed TFLOPS value by effective computing power. However, this theoretical formula only applies to standard model architectures. Any structural modification invalidates it. HFU, meanwhile, still requires manual computation.

## Solution

We provide the API that counts the floating-point operations (FLOPs) of all MatMul-related operators. It also supports counting total FLOPs for forward/backward passes and recomputation during training.

The proposed API covers the following MatMul-related operators: `MatMul`, `BatchMatMul`, `FlashAttention`, as well as fused operators for `MC2`, `CoC`, `GEMM`, and `matmul_add_fp32`.

## Usage

To enable this feature, set `--op-cal-tflops` to invoke it.

## Effects

By printing `actual throughput per NPU (TFLOP/s/NPU)` and `actual throughput per NPU with recompute (TFLOP/s/NPU)`, you can conveniently calculate MFU and HFU.

> [!NOTE]
>
> Since this feature collects TFLOPS information for each card, the computation load varies across cards in CP/EP/PP scenarios. Therefore, the information from all cards must be aggregated and averaged at the end, which adds an extra all_reduce communication.
> Using this feature may affect performance because it adds an extra communication and calculates the floating-point operation count for each operator.
> In the Ring Attention long-sequence parallelism scheme under causal scenarios, some computations are reduced due to algorithm optimization. This causes a discrepancy between the theoretical value and the actual collected value. The theoretical reduction in FA computation is `(CP-1)/(2×CP)`.
> This feature does not currently support MLA scenarios.
