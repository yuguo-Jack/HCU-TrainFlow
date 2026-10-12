---
id: doc-ascend-mindspeed-44dcdc1cac46726bb66f
title: Ascend/MindSpeed / docs/en/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md
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
path: docs/en/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md
raw_sha256: 465129ba55e6466177a97aec18342cb47c0b90d4b9eefd9404b542419e7b64d4
sources: []
generated_body_sha256: ab59572ee06268d7dfaccaaea5dbf30e51ad7a994f93aceb23671c0e0672a37d
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Communication Overlap for Megatron MoE AlltoAll Dispatcher

## Background and Challenges

In MoE, a large amount of EP communication is not overlapped with computation, accounting for a significant proportion of end-to-end time. This overhead can be reduced by interleaving communication with computation, thereby improving model training performance.

## Solution

During the forward pass, asynchronous communication is used to overlap with computation as much as possible. Meanwhile, the entire computation graph is partitioned into subgraphs, enabling concurrent communication and computation during the backward pass to accelerate model training.
This feature supports both alltoall dispatchers, with targeted optimizations applied to the two different dispatchers: alltoall and alltoall_seq.
Additionally, the alltoall branch is compatible with Megatron's moe-shared-expert-overlap and, through finer-grained overlapping, achieves further performance improvements over the native solution.

## Usage

Enable this feature by turning on `--moe-alltoall-overlap-comm`.

If the branch is `alltoall_seq`, the following must also be enabled:

- `--moe-permutation-async-comm`.
- `--moe-token-dispatcher-type alltoall_seq`.
- `--moe-grouped-gemm`, currently only supports Grouped MLP.

And when tp>1, you need to also enable
`--moe-tp-extend-ep`

If the branch is the `alltoall` branch, you need to enable:

- `--moe-token-dispatcher-type alltoall`.
- `--moe-grouped-gemm`, currently only supports Grouped MLP.
- `--moe-tp-extend-ep` is not supported. If you need this feature, switch to `alltoall_seq`.

## Application Scenario

This feature is suitable for scenarios using the megatron-moe dropless branch where training performance needs to be improved. Compared with the baseline dispatcher scenario, performance can be improved by over 10%.
After enabling `--moe-shared-expert-overlap`, performance can still be improved by more than 4%.
Enabling this feature will increase memory usage, which is normal. In this case, you can use the [ZeroMemory feature](megatron-moe-zero-memory.md) to adjust memory usage.
