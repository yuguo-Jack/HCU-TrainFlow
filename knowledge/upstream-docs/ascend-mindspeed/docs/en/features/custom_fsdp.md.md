---
id: doc-ascend-mindspeed-4dbf836b07a891509057
title: Ascend/MindSpeed / docs/en/features/custom_fsdp.md
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
path: docs/en/features/custom_fsdp.md
raw_sha256: be2409f9a657181820e956c22cd322252b8e690df7bc92a763179eed45b761f6
sources: []
generated_body_sha256: eba2e77f5b6ccc66eaa55f854300ebb923de2c5d9d096f0e95ffaee038c9dcc7
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/custom_fsdp.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/custom_fsdp.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Megatron Fully Sharded Data Parallelism (FSDP)

## Background and Challenges

As large model weights increase, there is a need to further improve memory utilization efficiency. The previous ZeRO-1 operation only shards the optimizer states within the DP domain, but does not shard the model weights and gradients. This makes model weights and gradients account for the bulk of static memory usage. FSDP can also shard weights and gradients within the DP domain, thereby further reducing the size of static memory.

## Solution

Each DP rank only holds a shard of the parameters. Before the forward pass of each weight block, an All Gather is performed within the DP domain. After the forward pass, the gathered weights are released, retaining only the shard. Before the backward pass, an All Gather is first performed to obtain the complete weights. After the backward pass, a Reduce Scatter is performed to sum the gradients across all DP ranks, while retaining only the shard corresponding to that DP rank.

## Application Scenario

When DP > 1, the model weights occupy a large amount of memory, and you want to further shard the weights and gradients to save memory.

## Usage

To enable fully sharded data parallelism, add the following configuration:

    ```bash
    --use-custom-fsdp
    --data-parallel-sharding-strategy optim_grads_params
    --no-gradient-accumulation-fusion
    --use-distributed-optimizer
    ```

You need to disable `CUDA_DEVICE_MAX_CONNECTIONS`.

    ```bash
    unset CUDA_DEVICE_MAX_CONNECTIONS
    ```

## Effects

The model and weights are further sharded, reducing memory usage. However, because additional communication is introduced in each forward and backward pass, performance will decrease.

> [!NOTE]
>
> MindSpeed adapts the basic functionality of this feature. It is not recommended to combine it with other features in the repository. For usage, [refer to this script](../../../tests_extend/system_tests/feature_tests/custom_fsdp.sh).
