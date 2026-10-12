---
id: doc-ascend-mindspeed-54a96fd866df7f953356
title: Ascend/MindSpeed / docs/en/features/kvallgather-context-parallel.md
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
path: docs/en/features/kvallgather-context-parallel.md
raw_sha256: f714c5c862a86a417d8c0c9597e8963d4c7e43b5e226be20e4f4821096e38115
sources: []
generated_body_sha256: 3be62e01f61a3ad65ca4df1f21ffd451b92afb46664ea3d5199cd36deb7bdf12
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/kvallgather-context-parallel.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/kvallgather-context-parallel.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# KVAllGather Long Sequence Parallelism

## Background and Challenges

From generative AI to scientific research models, long sequence training is becoming increasingly important. In the generative AI domain, tasks such as conversational AI, long document summarization, and video generation all require reasoning over long contexts in both spatial and temporal dimensions. Similarly, chapter- and book-level summarization (tens or even hundreds of thousands of words) is also critical in conversational AI and summarization tasks. Existing parallelism methods such as data, tensor, and pipeline parallelism cannot partition along the sequence dimension. As the sequence dimension (S) grows, the training memory overhead increases at a rate of $O$($S^2$). Therefore, specific optimizations for long sequence scenarios are needed to address the training requirements of long-sequence training.

## Solution

In the KVAllGather long sequence parallelism scheme, each compute device first holds different segments of the data sample along the sequence dimension. Then, before the attention computation begins, an all-gather communication operation is performed on the sharded keys and values, enabling each device to obtain the complete key and value sequences. Finally, each device uses its local query to perform attention computation with the complete keys and values, producing the corresponding output.

For more details on the KVAllGather long-sequence parallelism scheme, see the original paper:

> Section 3.3.2 of [The Llama 3 Herd of Models](<https://arxiv.org/abs/2407.21783>)

## Application Scenario

The KVAllGather long-sequence parallelism scheme is highly versatile, flexibly supporting various attention masks with minimal constraints in practical apps.

In scenarios such as GQA (Grouped-Query Attention) and MQA (Multi-Query Attention), the time required for all-gather communication of keys and values is far less than the overall computation time, making the benefits of this scheme even more significant.

This approach is fully compatible with FlashAttention, which is enabled by default for accelerated computation.

## Usage

| Important Parameter | Parameter Description |
| ---------------------------------------------------- | --------------------------------------------------------- |
| `--context-parallel-size [int]` | Sets the number of parallel processes for CP. The default is `1` (parallelism disabled). To enable parallelism, set this value to greater than `1` according to user requirements. |
| `--context-parallel-algo kvallgather_cp_algo` | Long-sequence parallel algorithm option. Set to `kvallgather_cp_algo` to enable KVAllGather long-sequence parallelism. |
| `--seq-length [int]` | The length of the input sequence. |

## Effects

By partitioning the input sequence across multiple compute devices, this approach reduces memory consumption on individual devices. Compared to not using sequence parallelism, per-step latency increases, but computational efficiency improves over recomputation.

## Notes

1. When enabling KVAllGather long sequence parallelism, you must also set `--transformer-impl transformer_engine`; otherwise, the feature is not supported.
2. Currently, only `--attention-mask-type` set to `causal` is supported.
3. For fixed-length padding training scenarios, a load-balanced sequence partitioning method is used, and `--seq-length` must be divisible by `2 * context-parallel-size`.
4. For EOD Reset training scenarios, a conventional sequence partitioning method is used, and `--seq-length` must be divisible by context-parallel-size.
