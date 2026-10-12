---
id: doc-ascend-mindspeed-8ad15b989f87e9ecd463
title: Ascend/MindSpeed / docs/en/features/unaligned-ring-context-parallel.md
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
path: docs/en/features/unaligned-ring-context-parallel.md
raw_sha256: 455fc87bcc0c6caef2d8017869d8cb92ba57a017ed64bee0675d19bdf099fbf0
sources: []
generated_body_sha256: 3ba0bfcee1186cc90ca18cb37207e6d3263fe97c73acb882933666d34d69ec07
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/unaligned-ring-context-parallel.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/unaligned-ring-context-parallel.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Unaligned Ring Long Sequence Parallelism

## Background and Challenges

With the development of generative AI and scientific research models, long sequence training has become increasingly important. However, traditional Ring sequence parallelism requires that the sequence length must be divisible by the Context Parallel size (CP size). This imposes limitations when processing dynamic or irregular inputs, especially in multimodal apps where the sequence length of input data may be unpredictable and frequently changing. Therefore, a mechanism is needed to support operations in these unaligned scenarios to accommodate a wider range of application scenarios.

## Solution

To address the limitations of traditional Ring sequence parallelism when processing unaligned sequence lengths, the "Unaligned Ring" mechanism establishes a shape negotiation protocol, exchanges effective length information before communication, and isolates changes through `get_unaligned_cp_shapes` to obtain the current rank length and target rank length. It transmits non-uniform sequences during chunked computation and communication, enabling RingAttention computation with non-uniform partitioning.

## Application Scenario

The "Unaligned Ring" feature is applicable to the following typical scenarios:

- Multimodal learning: When processing various types of data such as images, videos, and text, the sequence lengths of different data types vary significantly, making it difficult to unify them to a fixed CP size.
- Real-time data analysis: When processing streaming data, the arrival time of data is uncertain, resulting in potentially different sequence lengths for each processing operation.
- Personalized recommendation systems: The sequence lengths of user behavior data are usually different, and in such cases, support for unaligned operations is also required.

## Usage

To use the "Unaligned Ring" feature, pass the `shapes` parameter when calling the `ringattn_context_parallel` interface, as shown in the example code below.

```python
# Example code
 output = ringattn_context_parallel(q, k, v, head_num, cp_para, softmax_scale, attn_mask, dropout_p, shapes=shapes)

```

`get_unaligned_cp_shapes` is an important function in unaligned Ring sequence parallelism. The main purpose of the `shapes` parameter is to obtain the sub-sequence length information after unaligned splitting of the sequence. Within the function, elements are accessed via `shapes[block_id]` and `shapes[next_block_id]`, so the `shapes` parameter can be any data structure that supports index access through the `[]` operator, including but not limited to:

1. List: for example, [100, 100, 20]
2. Tuple: for example, (100, 100, 20)
3. Dictionary: for example, {0: 100, 1: 100, 2: 20}

The `get_unaligned_cp_shapes` function ultimately returns a list containing two elements: `shapes[block_id]` and `shapes[next_block_id]`, which correspond to the values at the `block_id` and `next_block_id` indices, respectively.

```python
def get_unaligned_cp_shapes(shapes, block_id, next_block_id):
    if shapes is None:
        return None
    unaligned_cp_shapes = [shapes[block_id], shapes[next_block_id]]
    return unaligned_cp_shapes
```

## Effects

By introducing "unaligned ring," the system improves its adaptability to different input lengths. This not only resolves the issues encountered by traditional ring sequence parallelism when processing dynamic or irregular input sequences, but also maintains good scalability.

## Notes

1. Unaligned ring long sequence parallelism currently only supports the scenario where `--attention-mask-type` is `general`.
