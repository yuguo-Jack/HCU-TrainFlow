---
id: doc-baidu-baige-loongforge-cc2f8e94a373d9be45c4
title: baidu-baige/LoongForge / docs/source/features/fused_linear_cross_entropy.md
engine: loongforge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: baidu-baige/LoongForge
commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
path: docs/source/features/fused_linear_cross_entropy.md
raw_sha256: 01bb42f64dcce8060b441733ff908792be585083c2d637efc2b9472537fc519b
sources: []
generated_body_sha256: 29ea00a75e591057b5c2abaacd110bd1e2cd0e7154d47dab5e91cd784038dec0
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source/features/fused_linear_cross_entropy.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source/features/fused_linear_cross_entropy.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Fused Linear Cross Entropy

LoongForge provides a memory optimization solution for the model output layer. By fusing the `hidden @ weight.T` linear projection with the cross-entropy loss into a single operation, combined with chunked computation, it significantly reduces peak memory usage during the vocabulary projection stage.

In standard training, the output layer produces a complete logits tensor of shape `(num_tokens, vocab_size)`, which is retained again during the backward pass, resulting in doubled memory overhead. For a typical configuration (num_tokens=16384, vocab_size=129280), logits-related memory alone can reach **~40 GB**. This optimization addresses the problem through a two-step progressive approach:

- **Step 1 (Operator Fusion)**: Fuses the linear projection and cross-entropy into a single autograd Function, with the backward controlled by the framework, saving only lightweight statistics (per-token max and sum-of-exp), eliminating the need to store complete logits between forward and backward passes
- **Step 2 (Chunked Computation)**: Splits weight along the vocabulary dimension into small chunks (default `vocab_per_split=3072`), computes and immediately discards each chunk using an online Softmax algorithm, so the complete logits tensor is **never instantiated**

LoongForge provides two implementation paths, and the framework **automatically selects based on GPU architecture**;

## Usage
Add the following parameters to the training launch script:

```bash
--cross-entropy-loss-fusion \
--cross-entropy-fusion-impl linear
```

---

## 1. Generic Implementation

LoongForge implements a pure PyTorch generic version using strategies such as mixed precision, buffer reuse, in-place operations, and Autograd, enabling this optimization to run on **any CUDA GPU** while also achieving notable performance advantages over the native Torch implementation.

Core design: Pre-allocate a small buffer of width `vocab_per_split`, write each matmul directly into this buffer (via the `out=` parameter), the result is immediately consumed by online softmax within the same loop iteration, and overwritten in the next round — the complete logits never accumulate at the Python level:

```python
matmul_buf = torch.empty((num_tokens, vocab_per_split), ...)  # allocate only one chunk size

for split_idx in range(num_splits):
    torch.matmul(hidden, weight[v_start:v_end].t(), out=matmul_buf)  # write into reused buffer
    logits_chunk.sub_(new_max.unsqueeze(1)).exp_()                    # in-place, immediately consumed
    accumulate.mul_(torch.exp(maximum - new_max)).add_(chunk_sum)     # update statistics
    maximum = new_max
    # next matmul directly overwrites the buffer, complete logits never existed
```

The backward pass likewise recomputes chunk by chunk, using the `maximum` and `accumulate` saved from the forward pass (both of shape `(num_tokens,)`) to restore the softmax probabilities for each chunk, without needing to save the complete logits.

### Features
* Works on **any CUDA GPU**, no hardware restrictions
* **22~26%** faster than the native implementation on A800
* Online Softmax guarantees **numerically identical results** to the native implementation (loss/gradient difference < 1e-5)
* Supports DP / TP / SP parallelism strategies, supports FP8 training


---


## 2. Tuning Parameters

Control chunk size via environment variables to balance memory usage and performance:

```bash
# Default value 3072, optimal balance between memory and performance (recommended)
export LCE_GENERIC_FWD_VOCAB_SPLIT_SIZE=3072
export LCE_GENERIC_BWD_VOCAB_SPLIT_SIZE=3072

# Increase chunk size when memory is sufficient to improve GPU utilization
export LCE_GENERIC_FWD_VOCAB_SPLIT_SIZE=8192

# Decrease chunk size when memory is extremely limited
export LCE_GENERIC_FWD_VOCAB_SPLIT_SIZE=512
```
