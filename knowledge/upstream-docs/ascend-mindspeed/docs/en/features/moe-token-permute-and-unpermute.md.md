---
id: doc-ascend-mindspeed-dbfc9dd9c583950b76b1
title: Ascend/MindSpeed / docs/en/features/moe-token-permute-and-unpermute.md
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
path: docs/en/features/moe-token-permute-and-unpermute.md
raw_sha256: 1dc8871cc7330929fb3332498b68139a64457918bf0f3018d8dcacfe7f21894d
sources: []
generated_body_sha256: c6a328a14e5e805cd55bf772b56dfb3de065ec304a868c650922bd9e57c057d8
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/moe-token-permute-and-unpermute.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/moe-token-permute-and-unpermute.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# MoE Token Permute and Unpermute Fusion

## Background and Challenges

In the MoE architecture, the MoEAlltoAllTokenDispatcher scheduler is responsible for assigning tokens to various experts for processing and then reassembling the processed results back into the original token order. This process typically involves the following steps:

- Token routing: determining which expert should process each token. This is accomplished through an expert gating mechanism, which selects the most suitable expert for each token.
- Data rearrangement (Permute): grouping tokens by their selected experts so that each expert can process its assigned tokens in parallel. This typically involves permuting the tokens.
- Expert processing: each expert processes its assigned tokens in parallel.
- Result reassembly (Unpermute): after processing is complete, the results from different experts need to be reassembled back into the original token order.

In the above workflow, the data rearrangement and result reassembly steps are among the performance bottlenecks. This is because these two steps involve significant data movement, especially when using distributed training.

## Solution

To optimize this process, MindSpeed fuses the MoE Token Permute and Unpermute operations into a single operator, thereby improving model training performance.

## Usage

1. Add `--moe-permute-fusion` or `--use-fused-moe-token-permute-and-unpermute` to the launch script. Both are equivalent, but `--moe-permute-fusion` is recommended as the preferred option.
2. The following configuration is recommended for optimal performance; otherwise, enabling this fused operator may degrade performance in certain scenarios.

- When `--moe-token-dispatcher-type alltoall` is set, configure `--expert-tensor-parallel-size 1`.
- When `--moe-token-dispatcher-type alltoall_seq` is set, enable `--moe-tp-extend-ep`.

## Usage Constraints

1. Supported dispatcher types: Currently, only `--moe-token-dispatcher-type alltoall` and `--moe-token-dispatcher-type alltoall_seq` are supported. `--moe-token-dispatcher-type allgather` is not yet supported.
2. Compatibility between the fusion operator and expert capacity parameters: To enable `--moe-expert-capacity-factor`, `--moe-pad-expert-input-to-capacity` must also be enabled for compatibility with the fusion operator. If only `--moe-expert-capacity-factor` is enabled without `--moe-pad-expert-input-to-capacity`, the fusion operator is not yet compatible.
3. System environment requirements: Limited to system environments with version identifiers `CANN 8.3.RC1` / `TorchNPU 7.2.RC1` and all subsequent iterative versions.

## Effects

Enabling the fusion operator not only effectively saves memory resources but also improves model training performance.
