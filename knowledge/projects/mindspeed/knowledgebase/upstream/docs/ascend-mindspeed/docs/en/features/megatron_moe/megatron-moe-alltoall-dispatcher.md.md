---
id: doc-ascend-mindspeed-3bfd08c0c1a99d889dbd
title: Ascend/MindSpeed / docs/en/features/megatron_moe/megatron-moe-alltoall-dispatcher.md
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
path: docs/en/features/megatron_moe/megatron-moe-alltoall-dispatcher.md
raw_sha256: 4fea38f149872024d20e145a01d014d44686846b6a901e7fbb1828473ee45a7e
sources: []
generated_body_sha256: c8d9f1860b7158ae7f1f23502e966d4e3d5a4e9fe317b3b1ace784fe3c365b7a
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/megatron_moe/megatron-moe-alltoall-dispatcher.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/megatron_moe/megatron-moe-alltoall-dispatcher.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Alltoall Dispatcher Optimization

## Background and Challenges

**repeat_interleave Parallelism**

In the Alltoall dispatcher branch, the repeat_interleave operator is invoked. This operator uses only a single block dimension for serial computation on a single launch stream, resulting in long execution times. Moreover, the operator's output is not used until after the alltoall, permute, and alltoallv operations.

**Computation-Communication Overlapping**

In the alltoall branch, the permutation function performs an allgather operation to complete the split H dimension of all tokens, and then performs expert computation on the data blocks. This operation is serial, but since there is no dependency between tokens of different experts, it can be modified to a parallel operation.

## Solution

**For repeat_interleave Parallelism**

By creating a new dispatch stream, the repeat_interleave operator invocation is offloaded to the new stream. When block dim resources are sufficient, the two operators can be computed in parallel, saving time.

**For Computation-Communication Overlapping**

Tokens can be split according to the requirements of each expert, and then allgather communication and expert computation are performed on the tokens one by one. Since the computation of the first expert depends only on the first communication and there is no dependency between experts, the communication for the second expert can proceed concurrently while the first expert's computation is being performed, achieving computation-communication overlapping.

## Application Scenario

When using mcore MoE, the `--moe-token-dispatcher-type alltoall` option is enabled.

## Usage

Enable the `--moe-permutation-async-comm` parameter.

> [!NOTE]
>
> When `--moe-grouped-gemm` is enabled, expert computation is merged into a single operator, so the computation-communication overlapping optimization becomes ineffective.

## Effects

Enabling this feature reduces training time and improves performance.
