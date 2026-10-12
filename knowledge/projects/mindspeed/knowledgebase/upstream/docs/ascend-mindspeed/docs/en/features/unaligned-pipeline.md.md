---
id: doc-ascend-mindspeed-f1d17f7058af98f52581
title: Ascend/MindSpeed / docs/en/features/unaligned-pipeline.md
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
path: docs/en/features/unaligned-pipeline.md
raw_sha256: 8fa0cefcee161660ff973d9d753774f468d7581df9f051e905f75af6ca06016a
sources: []
generated_body_sha256: e76cc31f8c3ee3cb2e32ce7b8c41d6486eb9825a666a64e2a2ed1be4b62cf93c
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/unaligned-pipeline.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/unaligned-pipeline.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Non-aligned PP and VPP Allocation

## Background and Challenges

Megatron-LM-like frameworks have become one of the mainstream solutions for large model training. PP (Pipeline Parallelism) and VPP (Virtual Pipeline Parallelism) are fundamental parallel paradigms for large model training, but they suffer from computational imbalance in certain scenarios. Specifically:

- **Embedding Layer**: When processing text or categorical data, the embedding layer converts high-dimensional sparse features into low-dimensional dense vector representations. This process involves index lookups and potentially large-scale matrix multiplications. Particularly in natural language processing apps, the vocabulary may contain hundreds of thousands or even millions of entries. High-dimensional lookup and conversion operations consume substantial computational resources.

- **Logits Layer**: The logits layer at the end of the network is typically a fully connected layer that maps the final hidden states to the output space, providing unnormalized predictions for subsequent loss function computation. If the classification task involves a large number of categories, the weight matrix of this layer becomes extremely large, making the matrix multiplication operation a performance bottleneck.

- **Multi-Token Prediction**: A module located at the end of the network that extends the prediction scope to multiple future tokens at each position. It expands the estimation capability of the logits layer while placing higher demands on computational resources.

The computational complexity of the above operations increases with the number of input features and categories, which may lead to reduced training speed and create performance bottlenecks in environments with limited computational resources.

## Solution

To address the above challenges, we have introduced the "Unaligned PP and VPP Sharding" feature, which allows users to dynamically adjust the computational load of the model within the training pipeline by specifying the number of transformer layers distributed to each PP stage and VPP stage. This mechanism helps distribute the workload more evenly across multiple computing nodes, thereby optimizing the utilization of overall computational resources.

## Application Scenario

- This feature is particularly useful when users encounter performance bottlenecks caused by uneven distribution of computational resources. By redistributing compute-intensive tasks, it effectively reduces idle time (bubbles) in the pipeline, thereby improving system throughput and efficiency.

## Usage

Add `--pipeline-num-transformer-layers` to the model parameters, using a two-dimensional matrix to represent the number of transformer layers in PP and VPP domains. The horizontal axis represents PP rank, and the vertical axis represents VPP rank.
Assume `pipeline_num_transformer_layers = [[0,1],[1,1]*4,[1,0]]`, `pp_rank = 0`, and `vpp_rank = 1`, then `pipeline_num_transformer_layers[pp_rank][vpp_rank]`contains only 1 layer.
If VPP is not configured, it can be set as `pipeline_num_transformer_layers = [[1],[2]*4,[1]]`. If `pp_rank = 1`, then `pipeline_num_transformer_layers[pp_rank]` contains 2 layers.

### Precautions

- Ensure that the total number of layers in the array matches the value in the `--num-layers` configuration item.
- Since the default VPP in the framework is evenly split, the content of a single PP stage must be divisible by `--num-layers-per-virtual-pipeline-stage`. The actual effective configuration is controlled by the number of layers in the array.

### Setting Training Script Parameters

```shell
# Enable non-aligned PP/VPP
--pipeline-num-transformer-layers [[0,1],[1,1]*4,[1,0]] \
```

## Effects

By implementing a custom strategy for controlling the number of transformer layers in PP and VPP stages, it is expected to significantly reduce pipeline bubbles, thereby optimizing the computation flow and improving system performance. This not only helps accelerate the model training process but also maximizes hardware resource utilization.
