---
id: doc-ascend-mindspeed-llm-2a99ed8eac4ceed0a287
title: Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/mc2.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
path: docs/en/pytorch/features/mcore/mc2.md
raw_sha256: 9c62e212a5fa4ff920388fa7a250b750f8fd24c61f9284d1656366db78c39ca8
sources: []
generated_body_sha256: 58dba3f64cd05c6249efc791edf4d7d3623eb96a97ce58b801c169c67bd455af
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/mc2.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/f5f84bbbac05be79f883b30629d7f637e6f4649e/docs/en/pytorch/features/mcore/mc2.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Ascend MC2

## Prerequisites

This feature is supported only in environments that use `CANN 8.0.RC2`, `Ascend HDK 24.1.RC2`, or a later version.

If you try to use this configuration in an unsupported version, the system may behave abnormally, including runtime errors.

MindSpeed LLM disables MC2 by default. To enable MC2, comment out `args.use_ascend_mc2 = False` in the `validate_args_decorator` function in `mindspeed_llm/training/arguments.py`.
**Note: Enabling MC2 may affect accuracy for some models.**

## Issue Analysis

In LLM training scenarios that enable tensor parallelism (TP) and sequence parallelism (SP), there is a strong dependency between Matmul computation and All-Reduce operations when SP is disabled, or between Matmul computation and All-Gather/Reduce-Scatter operations when SP is enabled. When the model has many parameters, both communication and computation are heavy here. If they run sequentially, they introduce long waiting and idle time.

## Solution

Ascend developed the MC2 solution for Matmul computations and communication operations that have strong dependencies.

MC2 uses operator fusion to combine Matmul computation and collective communication operations. It splits large computation and communication tasks into smaller computation subtasks and communication subtasks. It then uses a pipeline so that communication subtasks and computation subtasks can overlap, which reduces waiting and idle time and improves utilization.

### Approach

On the Python script side, MC2 fuses the original sequential Matmul and All-Gather/Reduce-Scatter operations through the MC2 operator interface.

For details, see the [code implementation](https://gitcode.com/ascend/MindSpeed/blob/core_r0.8.0/mindspeed/core/tensor_parallel/ascend_turbo/mc2_linears_seq_parallel.py).

For the MC2 operator interface, see the [`torch_npu.npu_mm_all_reduce_base` interface documentation](https://www.hiascend.com/document/detail/zh/Pytorch/60RC1/apiref/apilist/ptaoplist_000449.html).

## Use Cases

When TP and SP are enabled, we recommend enabling MC2 for further optimization.

## Usage

Set `--use-ascend-mc2` to enable the MC2 operator.

## Effects

In training scenarios that enable TP and SP, MC2 can reduce memory overhead and improve computation efficiency.

## Notes

1. In MCore scenarios with `--use-mcore-models` enabled, the MLP part of MoE models does not enable MC2.

2. The Ascend 950PR&950DT products do not yet support this feature.
