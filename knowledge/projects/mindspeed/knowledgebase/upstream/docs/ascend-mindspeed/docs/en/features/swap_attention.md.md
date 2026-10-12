---
id: doc-ascend-mindspeed-46fd1d9a64be0433ea68
title: Ascend/MindSpeed / docs/en/features/swap_attention.md
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
path: docs/en/features/swap_attention.md
raw_sha256: 0609b9fdae12e1fdd6ca22e44423e6081d733b89ab996c604323717e3f5459c6
sources: []
generated_body_sha256: 4e25abc95a8af7707e135ebed9d8149cd880e8bf74e7ffe08419ba8dec4325b1
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/swap_attention.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/swap_attention.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# swap-attention

## Background and Challenges

During large model training, using recomputation can significantly reduce memory usage, but it increases the computation time of the training process, leading to lower execution efficiency.

## Solution

A new swap-attention feature has been added, which uses device memory and CPU memory to store activations. While gradients are back-propagating, activations are prefetched from CPU memory to reduce recomputation, fully leveraging the advantage of high H2D bandwidth to supplement computation with networking and enhance computing power through networking, thereby improving MFU and accelerating large model training.

![swap_attention process](../figures/swap_attention.png)

## Application Scenario

* Performance optimization: In scenarios where full recomputation is required, you can replace it by enabling `--swap-attention` and `--recompute-num-layers [int]` to improve performance.

* Memory saving: For scenarios where recomputation is not required, enabling only `--swap-attention` can save memory with almost no performance loss, supporting configurations for larger models.

## Usage

* The parameter `--swap-attention` needs to be added. The prerequisite is that the fused operator of Flash Attention is enabled.

* `--swap-modules` is optional. The parameter type is string, with a default value of "input_norm,self_attention,post_attention_norm". Modules can be configured according to the model. In mcore scenarios, only the self_attention module is prefetched by default.

The following explains how to use the prefetch feature alone versus using it with a specified number of recompute layers, along with the differences between the two approaches.

**Enable prefetch only: `--swap-attention`**

When enabled, the activation values of the attention layer in each layer will be prefetched to improve computational efficiency.

![swap_attention prefetch](../figures/swap_attention1.png)

**Enable prefetching and specify the number of recomputation layers: `--swap-attention` and `--recompute-num-layers [int]`**

When enabled, the activations of the attention layer in each layer will be prefetched, while the fully connected layers of the first [int] layers will be recomputed.

![swap_attention prefetching and recomputation](../figures/swap_attention2.png)

## Effects

Compared with full recomputation, it provides performance gains; compared with no recomputation, it provides memory savings.

> [!NOTE]
>
> * The `[int]` in `--recompute-num-layers [int]` refers to the number of layers per pipeline parallel (PP) stage. The value of `[int]` should be less than or equal to `num-layers/pipeline-model-parallel-size`.
> * If performance fluctuations occur, they may be caused by cross-NUMA memory access. You can try to mitigate this by binding processes to cores: `export CPU_AFFINITY_CONF=1,lazy_bind:0`
> * `--swap-attention` is currently incompatible with LoRA fine-tuning.
