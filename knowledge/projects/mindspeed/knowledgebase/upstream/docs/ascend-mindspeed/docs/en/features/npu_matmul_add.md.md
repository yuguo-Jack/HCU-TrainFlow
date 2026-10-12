---
id: doc-ascend-mindspeed-ce442279663abb185709
title: Ascend/MindSpeed / docs/en/features/npu_matmul_add.md
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
path: docs/en/features/npu_matmul_add.md
raw_sha256: ed6cc807afe362ba94fa1f6f2e4a77ea55414775225077a003b046ecccfc86b7
sources: []
generated_body_sha256: d6b9dc0a2d73f64c8157f062aba846ce9f2e270004dd4083f669715ef33be1fd
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/npu_matmul_add.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/npu_matmul_add.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# matmul_add Fusion

## Background and Challenges

When gradient accumulation is enabled during model training, the accumulation efficiency is slow, and the Add operator accounts for a high proportion of the gradient accumulation process.

## Solution

MindSpeed merges the matmul operation and the add operation into a single fused operator. For the operator interface, see [npu_matmul_add](../ops/npu_matmul_add.md).

## Application Scenario

Applicable to Llama and GPT large models.

## Usage

Enabling the fused operator requires installing ATB (Ascend Transformer Boost). Refer to [Software Installation](../user-guide/install_guide.md) to complete the installation.

Remove `--no-gradient-accumulation-fusion` to call the Matmul_Add fused operator.

### Notes

* npu_matmul_add_fp32 does not currently support MFU (Model FLOPS Utilization) statistics.
* There is a certain precision difference between the fused operator and the small operators.
Root cause of the precision difference:
After the small operator's matmul operation is completed, the result is first downcast (from fp32 to bf16) and then upcast (from bf16 to fp32) before the final add operation. This downcast-then-upcast process loses some precision, whereas the fused operator skips this step and performs the accumulation directly, resulting in a precision difference.<br>
The specific change process is as follows:
  * Small operator dtype change process: `bf16*bf16=fp32->bf16->fp32+fp32=fp32`
  * Fused operator dtype change process: `bf16*bf16=fp32+fp32=fp32`

## Effects

When memory is not fully utilized, enabling the Matmul_Add fused operator will improve model training performance. For the Llama2-7b model, the performance gain is approximately 2%.
