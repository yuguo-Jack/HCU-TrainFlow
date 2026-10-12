---
id: doc-ascend-mindspeed-ba97d3c25b5ff361f51a
title: Ascend/MindSpeed / docs/en/features/virtual-pipeline-parallel.md
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
path: docs/en/features/virtual-pipeline-parallel.md
raw_sha256: 1aa9a60ee90b4751379fb6671f88c9090b43812447104b2096e0984091a9190d
sources: []
generated_body_sha256: 7058c7e81ce341f63b637eed93cc1bf2a1ff714130970a8135819c0fc87710a2
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/virtual-pipeline-parallel.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/virtual-pipeline-parallel.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Megatron Virtual Pipeline Parallelism

## Background and Challenges

Although the [Megatron pipeline parallel](./pipeline-parallel.md) strategy can effectively partition models, it still suffers from a high bubble ratio during execution, leaving room for improvement in computing resource utilization.

## Solution

To address this issue, virtual pipeline parallelism technology was proposed, aiming to further subdivide computing tasks, reduce the bubble ratio, and improve training efficiency.

The core of Virtual Pipeline Parallelism (VPP) lies in further subdividing the model into more stages without increasing the number of devices, trading increased communication volume for a lower bubble ratio. With the same number of devices, more pipeline stages are created, exchanging more communication for a reduced bubble ratio.

Figure 1 Virtual pipeline parallelism

![VPP diagram](../figures/virtual-pipeline.PNG)

For more details, see the paper [Efficient Large-Scale Language Model Training on GPU Clusters Using Megatron-LM](https://people.eecs.berkeley.edu/~matei/papers/2021/sc_megatron_lm.pdf).

For example, assuming the model has a total of 16 layers, tensor parallelism size is 1, pipeline parallelism size is 4, and virtual pipeline parallelism size is 2, the model will be divided into 4 * 2 = 8 stages, with each stage containing 16/8 = 2 layers, as shown below:

    Device 0: [1, 2] [9, 10]
    Device 1: [3, 4] [11, 12]
    Device 2: [5, 6] [13, 14]
    Device 3: [7, 8] [15, 16]

The forward order is Device 0 -> Device 1 -> Device 2 -> Device 3 -> Device 0 -> Device 1 -> Device 2 -> Device 3

## Application Scenario

Given the performance bottlenecks in current data processing and model training, especially the need to optimize the bubble ratio (i.e., the proportion of idle or inefficient computation cycles), virtual pipeline parallelism demonstrates its unique advantages. This technology aims to effectively reduce the bubble ratio through an innovative parallel processing mechanism, significantly improving the overall performance and efficiency of model training. Specifically, it can optimize resource allocation and accelerate data processing workflows, thereby shortening training cycles and reducing computational costs.

## Usage

Virtual pipeline parallelism depends on pipeline parallelism. To enable virtual pipeline parallelism, add the following parameter configuration to the training script:

```bash
--num-layers-per-virtual-pipeline-stage  N     # N represents the number of layers per virtual pipeline stage
```

Additionally, when enabling this feature, the total number of model layers `L % N == 0` must hold, and `--pipeline-model-parallel-size` must be greater than or equal to `2`.

> [!NOTE]
>
> * Megatron virtual pipeline parallelism (VPP) directly affects how weights are partitioned. When saving or loading weight files, you must maintain consistency in VPP configuration parameters to ensure accurate model weight loading and stable system operation.
> * When training with the verl framework, mbridge is currently incompatible with VPP. Please use this feature when mbridge is not enabled.

## Effects

Through the virtual pipeline parallelism strategy, the bubble ratio is successfully reduced, further improving model training performance and resource utilization.
