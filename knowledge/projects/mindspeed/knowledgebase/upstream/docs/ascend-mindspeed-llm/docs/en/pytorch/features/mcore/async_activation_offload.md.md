---
id: doc-ascend-mindspeed-llm-99ecdf2f806a038b0f6d
title: Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/async_activation_offload.md
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
path: docs/en/pytorch/features/mcore/async_activation_offload.md
raw_sha256: e3679e0b312aa6d80ebb89018af523fc8b4aa0a40e51b22695f322d8fac05a3b
sources: []
generated_body_sha256: f990c1bf38ff7ca7e0922eb7b7f6eb2eff687298a655fcdb5d63cb4d53b70dae
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/async_activation_offload.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/features/mcore/async_activation_offload.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Async Activation Offload

## Background and Challenges

As model parameter counts grow and sequence lengths increase, memory demand during training rises sharply. Current approaches to optimizing activation memory mainly rely on activation recomputation and sequence parallelism. These techniques have the following bottlenecks:

- Activation recomputation saves memory by discarding activation values from the forward pass and recomputing them during the backward pass. This introduces a large amount of redundant computation.
- Sequence parallelism can reduce memory use by distributing the computation for a single sequence across multiple devices. However, frequent cross-device communication can be difficult to hide effectively.

To address these challenges, you can use the asynchronous activation offload strategy.

## Solution

- Memory optimization: Offload activation tensors from the device side to the host side, which significantly reduces peak memory usage.
- Asynchronous execution: Use multiple streams to make offload (device-to-host, D2H) and load (host-to-device, H2D) operations asynchronous. Therefore, the copy overhead can overlap with computation.
- Early prefetch: During the backward pass, use the prefetch mechanism to load the tensors needed next in advance and hide load latency.

## Usage

This feature supports organizing tensor lifecycles by block, which lets you manage activation values for different model blocks flexibly. The following example shows how to use it.

```python
with async_save_on_cpu(
    h2d_stream=h2d_stream,
    d2h_stream=d2h_stream,
    block_idx=block_idx,
    depth=depth,
    custom_check_fn=your_check_fn
):
    # The forward pass for one block of the model. This is only an example
    output = layer(input)
```

### Parameter Details

- `h2d_stream` / `d2h_stream`: The H2D and D2H streams. It is recommended that you create dedicated global streams for H2D and D2H tasks so they run asynchronously with the computation stream.
- `block_idx`: The index of the current block in the model.
- `depth`: The total number of layers in the model.
- `custom_check_fn`: A custom validation function. Only activation values that return `True` after validation are offloaded. In practice, you should select parts with heavy computation and a small activation footprint, and combine them with a recomputation strategy. For activation values with a large activation footprint and short compute time, use recomputation. For activation values with a small activation footprint and long compute time, use offload. Otherwise, the overhead of H2D and D2H becomes too large and is difficult to hide with computation.

## Use Cases and Results

- Long-sequence scenarios: The computation cost of self-attention grows quadratically with sequence length. With this approach, you can offload the activation values from the forward pass of self-attention and skip recomputing self-attention during the recomputation stage. In typical scenarios, end-to-end performance improves by more than 20 percent.
- FSDP2 scenarios: Under the FSDP2 distributed strategy, model parameters are partitioned and gathered. For shorter sequence lengths, computation time cannot mask communication time. You can use this approach to offload the activation values at the recomputation entry point. After saving memory, you can increase the micro-batch size or sequence length to raise the compute-to-communication ratio. In typical scenarios, end-to-end performance improves by more than 60 percent.
