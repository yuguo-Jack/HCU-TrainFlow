---
id: doc-ascend-mindspeed-llm-759e5cddffd876d3cc07
title: Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/deepseek4_fine_grained_recompute.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
path: docs/en/pytorch/features/mcore/deepseek4_fine_grained_recompute.md
raw_sha256: 8fcbab12797cfb682cbe959cdc8915a719634a506642f013586b8b8dc5588d29
sources: []
generated_body_sha256: 41e101535ef72c5913494b2e510a9742d56e2530d9f3893579b842ba034471e7
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/deepseek4_fine_grained_recompute.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/f5f84bbbac05be79f883b30629d7f637e6f4649e/docs/en/pytorch/features/mcore/deepseek4_fine_grained_recompute.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# DeepSeek V4 Fine-Grained Recompute 

## Overview

DeepSeek V4 fine-grained recompute reduces NPU memory usage by recomputing some intermediate results in CSA and MHC during the backward pass, which reduces the number of activations stored during training. This feature adds a certain amount of recomputation overhead. Therefore, you are advised to enable it based on the model configuration and memory conditions.

CSA recompute and MHC recompute are independent of each other. You can enable them separately or together.

## How to Use

| Key Parameter | Description |
|---------------------------------|-------------------------------------------------------------------------------------------------|
| --recompute-csa-attention | Enables DeepSeek V4 CSA fine-grained recompute. It covers the supported Q projection, Indexer, Sparse Attention, and output projection computations. When combined with `--recompute-norm`, it recomputes the Q normalization of the target layers. |
| --mhc-recompute | Enables fine-grained recompute of the fused NPU MHC pre/post. You must also configure `--enable-mhc` and `--use-fused-mhc`. |

To enable only CSA fine-grained recompute:

```shell
--recompute-csa-attention
```

To enable only MHC fine-grained recompute:

```shell
--enable-mhc \
--use-fused-mhc \
--mhc-recompute
```

To enable both types of fine-grained recompute:

```shell
--recompute-csa-attention \
--enable-mhc \
--use-fused-mhc \
--mhc-recompute
```

## Notes

1. This feature currently applies only to DeepSeek V4 MCore training scenarios, and it is disabled by default.
2. `--recompute-csa-attention` and `--mhc-recompute` have no parameter dependency between them. When you enable both, they coordinate the release timing of intermediate activations.
3. `--mhc-recompute` takes effect only for the fused NPU MHC implementation. Therefore, you must enable `--enable-mhc` and `--use-fused-mhc` at the same time.
4. Fine-grained recompute takes effect only during training with gradient computation enabled. This recompute is not enabled for the MTP layer at present.
5. Once enabled, this feature trades additional computation overhead for memory savings. The actual benefit depends on the model size, sequence length, and parallelism configuration.
