---
id: doc-ascend-mindspeed-llm-3fcb0718796b5219c8a4
title: Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/recompute_relative.md
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
path: docs/en/pytorch/features/mcore/recompute_relative.md
raw_sha256: 0cef581124ad4b3bebbe08c4348f62d404c8ba856552afe77460c9fe59292752
sources: []
generated_body_sha256: 3bc6cfa9dc7700d23a9365b1b1603d8d2d9604279a38b89545b4de5f93b93617
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/recompute_relative.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/features/mcore/recompute_relative.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Recomputation

To reduce NPU memory usage during LLM training, MindSpeed LLM supports multiple forms of recomputation.

## Full Recomputation

For cases with very limited memory, full recomputation saves only the input activations for Transformer layers or layer groups, and it recomputes everything else. To enable full recomputation, set `--recompute-granularity full` and choose either the uniform or block method by setting `--recompute-method`.

**Uniform Method**:

`--recompute-method uniform`: Divides Transformer layers into groups of equal size, with each group size set by `--recompute-num-layers`, and stores the input and activation values for each group.

**Block Method**:

`--recompute-method block`: Applies recomputation to the first `--recompute-num-layers` Transformer layers. The remaining layers do not participate in recomputation.

## Selective Recomputation

Selective recomputation is recommended. It recomputes only the `core attention` part of the Transformer. It keeps in memory activations that consume less memory but are more expensive to recompute, and it recomputes activations that consume more memory but are cheaper to recompute.

You can enable it with `--recompute-granularity selective`.

## Activation Function Recomputation

Add `--recompute-activation-function` to the script to enable activation function recomputation.

Add `--recompute-activation-function-num-layers ${num}` to specify the number of layers for activation function recomputation.

You can enable activation function recomputation together with full recomputation:

1. When you enable both, only `block` is supported for `--recompute-method`.

2. When you enable both, each recomputation type runs according to the specified numbers of full recomputation layers and activation function recomputation layers. Therefore, no layer performs both full recomputation and activation function recomputation.

Note: The execution priority is to compute the full recomputation layers first and then the activation function recomputation layers. When pipeline parallelism is disabled, the sum of the full recomputation layer count and the activation function recomputation layer count should equal the total number of layers.

For detailed algorithm principles, see [Megatron recomputation](https://arxiv.org/abs/2205.05198) and MindSpeed [activation function recomputation](https://gitcode.com/Ascend/MindSpeed/blob/26.1.0_core_r0.12.1/docs/en/features/activation-function-recompute.md).
