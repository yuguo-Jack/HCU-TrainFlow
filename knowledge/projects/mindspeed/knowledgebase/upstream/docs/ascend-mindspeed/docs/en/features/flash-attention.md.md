---
id: doc-ascend-mindspeed-b6ebeea351952db18e3c
title: Ascend/MindSpeed / docs/en/features/flash-attention.md
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
path: docs/en/features/flash-attention.md
raw_sha256: 113abbc41f62b36e591456c3bf407239fb78521d946f2c399f8111ac64a54e5d
sources: []
generated_body_sha256: 1852745487ea6de59541946f1696632763f8107b5934727d6e681ba3291481d7
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/flash-attention.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/flash-attention.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Flash Attention

## Background and Challenges

In the field of deep learning, Transformer models are widely used in various domains such as natural language processing, speech recognition, and computer vision due to their outstanding performance. However, when processing long sequence data, the time and space complexity of their SelfAttention mechanism grows quadratically with the sequence length, leading to significant increases in computation time and memory consumption, which becomes a bottleneck for the further evolution of Transformer models. To address this, approximate attention methods have emerged, aiming to speed up model processing by reducing computation and memory usage, but they carry the risk of degrading model quality. Such methods often reduce complexity by sacrificing SelfAttention computation precision, implementing sparse attention mechanisms, or introducing alternative attention patterns, but this comes with potential compromises in model effectiveness, which is especially pronounced in detail-sensitive tasks.

## Solution

To overcome the above challenges, Flash Attention technology was introduced. Flash Attention is an efficient attention mechanism designed to significantly reduce the computation time and memory overhead of Transformer models when processing long sequences while maintaining model performance. The key to accelerating attention lies in optimizing IO memory access, i.e., reducing the number of read/write operations on on-chip memory.

Flash Attention is an exact attention method that optimizes IO memory access overhead. Its principle is shown in Figure 1. It reduces the number of memory reads/writes between high-bandwidth memory (on-chip memory) and SRAM through techniques such as Tiling, recomputation, and Kernel Fusion.

* Tiling: Uses faster SRAM instead of on-chip memory. However, SRAM has limited memory capacity and cannot complete the full attention computation for all data at once, so block-wise computation is required.
* Recomputation: Discards intermediate results from being written back and recomputes them when needed, trading computation for memory access.
* Kernel fusion: Fuses multiple operations into a single operation, using one kernel to complete the entire computation based on Tiling.

<p align="left"> <img src="../figures/flash_attention.png" height="280px" width="850px"></p>

For more information about Flash Attention, see [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/pdf/2205.14135).

## Application Scenario

This method is applicable to self-attention related models, especially for long sequence input scenarios. This feature is enabled by default when long sequence parallelism is turned on.

## Usage

Set the following parameter to call this algorithm:

```bash
--use-flash-attn
```

## Effects

It can significantly improve model training efficiency and save training memory overhead. Under the Llama2-7b model, the performance improvement is approximately 34%.
