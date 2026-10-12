---
id: doc-ascend-mindspeed-llm-f9f13041ddb32e239100
title: Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/kvallgather-context-parallel.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: 2fed626696175480ae1ab3342a94017301a25209
path: docs/en/pytorch/features/mcore/kvallgather-context-parallel.md
raw_sha256: cb0d5bedbb782f612d2c47d9571cfdbb868ef286276fcf183280059395c91f9f
sources: []
generated_body_sha256: cf17c9f6c3fa89672cb689d2e1169401da90abecfeee20f17669ec2e48cb1cd3
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/kvallgather-context-parallel.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/features/mcore/kvallgather-context-parallel.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# KVAllGather Long-Sequence Parallelism

## Feature Overview

For sparse flash attention, lightning indexer, and lightning indexer loss, perform an All-Gather communication on the partitioned key and value tensors before computation to obtain the complete key and value tensors.

For a detailed introduction, see [`kvallgather_cp_algo`](https://gitcode.com/Ascend/MindSpeed/blob/26.1.0_core_r0.12.1/docs/en/features/kvallgather-context-parallel.md).

## Usage

| Key Parameter | Description |
| --- | --- |
| `--context-parallel-size [int]` | Number of context-parallel ranks to set. The default is 1. Configure it based on your requirements. |
| `--context-parallel-algo` `kvallgather_cp_algo` | Long-sequence parallelism algorithm option. Set it to `kvallgather_cp_algo` to enable KVAllGather long-sequence parallelism. |
| `--seq-length [int]` | Input sequence length. |

## Notes

1. This feature currently supports only the sparse flash attention fused operator, the lightning indexer fused operator, and the lightning indexer loss fused operator.
2. This feature currently supports only `attention-mask-type` set to `causal`.
3. This feature supports only fixed-length padding training scenarios. It uses a load-balanced sequence partitioning method, and `--seq-length` must be divisible by `2 * context-parallel-size`.
