---
id: doc-ascend-mindspeed-4e11a76e64fa2fe2dc5b
title: Ascend/MindSpeed / docs/en/features/data-parallel.md
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
path: docs/en/features/data-parallel.md
raw_sha256: 72507c77716f482b6e1dd6010fc1e8a3f3a6b0c271a32aa0870ca684c08f1000
sources: []
generated_body_sha256: f137e6dbee1c14397375f722388503d80abfd64de81dfee9b36b3557216b8fe9
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/data-parallel.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/data-parallel.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Megatron Data Parallelism

## Background and Challenges

When training models on large-scale datasets, a single computing device often cannot handle the processing load of the entire dataset, resulting in excessively long training cycles. To address this challenge, the original dataset must be effectively partitioned, ensuring that each computing device only needs to process a portion of the dataset, thereby significantly improving training efficiency.

## Solution

The data parallelism (DP) strategy divides the dataset into multiple batches and distributes them evenly across computing devices, so that each device is only responsible for processing a specific batch of data.

The implementation of this scheme requires the following two key elements:

- The model structure and parameters deployed on each computing device must remain completely identical.
- The data batches processed by each device must be different from one another, ensuring the parallelism and efficiency of the training process.

The overall approach of this scheme is as follows:

* Model replication: Store a complete model replica on each computing device.
* Data partitioning: The original dataset is subdivided into several batches, which are then evenly distributed across all computing devices to ensure load balancing.
* Gradient synchronization: After completing the forward computation and obtaining local gradients, an All-Reduce operation is performed to aggregate the gradients from all devices, calculate the average, and then broadcast the result back to each device, thereby maintaining global parameter consistency.

## Application Scenario

Data parallelism is applicable in the following scenarios:

* Large-scale datasets: When the training dataset is so large that a single device cannot complete processing within a reasonable time.
* Sufficient computing resources: When a sufficient number of computing devices are available to store multiple complete model replicas and support parallel training, thereby effectively shortening the training cycle and reducing the computational load on individual devices.

## Usage

Enabling and configuring data parallelism primarily depends on the following metrics:

* World size: The total number of NPUs participating in parallel training.
* Tensor model parallel size: The number of parallel partitions for model weights.
* Pipeline model parallel size: The degree of pipeline parallelism for the model architecture.
* Context parallel size: The parallel strategy for processing long sequence data.

data_parallel_size = world_size // (tensor_model_parallel_size \* pipeline_model_parallel_size \* context_parallel_size)

> [!NOTE]
>
> The total number of model layers must be divisible by the pipeline parallelism size.
> `global_batch_size` must be divisible by `data_parallel_size`.

## Effects

Data parallelism is automatically calculated based on the settings of other parallelism strategies. The data parallelism approach can significantly shorten the training cycle, especially when processing high-dimensional features and large-scale datasets, and can improve the utilization of hardware resources. The data parallelism architecture offers excellent horizontal scalability, enabling linear performance improvement as computing resources increase. It is easy to deploy and adjust in cluster environments of different scales to meet the computing requirements at various stages.
