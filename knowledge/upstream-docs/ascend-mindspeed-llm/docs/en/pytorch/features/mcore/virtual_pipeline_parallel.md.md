---
id: doc-ascend-mindspeed-llm-8bfa569975f2097146d5
title: Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/virtual_pipeline_parallel.md
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
path: docs/en/pytorch/features/mcore/virtual_pipeline_parallel.md
raw_sha256: 3e90d9f572b1143f3e1353b0b7d839e611e4ba8f3eeb71b30b7b21d1e523d811
sources: []
generated_body_sha256: 98bfe1f87863bb06ade6cff64f95e60c7a15bb736ace8bd6a1f09e2662773a92
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/virtual_pipeline_parallel.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/features/mcore/virtual_pipeline_parallel.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Virtual Pipeline Parallelism

## Problem Analysis

PipeDream pipeline parallelism uses a chunk size that is too large. During execution, many pipeline bubbles remain, and there is still room to improve compute resource utilization.

## Solution

Further subdivide the computation to reduce bubbles.

### Approach

With the number of devices unchanged, divide the workload into more pipeline stages and trade additional communication for a lower bubble ratio.

![Virtual pipeline parallel forward and backward scheduling diagram](../../figures/virtual_pipeline_parallel/virtual-pipeline.png)

[Original paper link](https://arxiv.org/abs/2104.04473?utm_source=chatgpt.com)

For ease of understanding, here is an example. Assume that the model has 16 layers, the tensor parallel size is 1, the pipeline parallel size is 4, and the virtual pipeline parallel size is 2. The model is divided into 4 * 2 = 8 stages, and each stage has 16 / 8 = 2 layers.

    Device 0: [1, 2] [9, 10]
    Device 1: [3, 4] [11, 12]
    Device 2: [5, 6] [13, 14]
    Device 3: [7, 8] [15, 16]

The forward order is `device 0 -> device 1 -> device 2 -> device 3 -> device 0 -> device 1 -> device 2 -> device 3`.

## Use Cases

To further reduce the bubble ratio and improve performance.

## Usage

Set `--num-layers-per-virtual-pipeline-stage N`. This specifies the number of layers in each stage. The total number of layers must satisfy `L % N == 0`.

## Effects

The bubble ratio decreases further.

## Notes

Megatron virtual pipeline parallelism (VPP) affects the weight sharding scheme. When you save and load weights, ensure that the VPP configuration stays consistent so the weights load correctly.
