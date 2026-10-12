---
id: doc-ascend-mindspeed-62a8b6e028a53d527360
title: Ascend/MindSpeed / docs/en/features/recomputation.md
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
path: docs/en/features/recomputation.md
raw_sha256: e6f4a15d61724a3154cd4324fdc036c0f96fc3ac3fc8e1af4236edea4ff98b5d
sources: []
generated_body_sha256: a6d110329323b3b0bed85edc68258b9f30ba4af93e6a92a84feb424239de7ee0
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/recomputation.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/recomputation.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Megatron Recomputation

## Background and Challenges

In the training pipeline of large models, traditional practice requires storing the activations generated during the forward propagation phase for subsequent gradient computation during backpropagation. This requirement causes the number of saved activations to grow linearly with model depth, significantly increasing the pressure on hardware memory resources.

## Solution

To address the above challenges, a recomputation strategy is proposed. Specifically, during the forward propagation and loss function computation phases, the memory space of activations that are no longer needed is released immediately, and activations are only recomputed as needed during backpropagation. By effectively shortening the lifecycle of activations, this method significantly reduces the memory burden and improves overall resource utilization efficiency.

## Application Scenario

The recomputation feature can be enabled when memory is insufficient, and it is divided into the following two modes:

* Selective recomputation (recommended): Focuses on recomputing the core_attention component within the Transformer architecture. This strategy retains activations that occupy little memory but are expensive to recompute, while applying activation recomputation to those that occupy large amounts of memory but are relatively cheap to recompute. This approach achieves efficient memory management while maintaining model performance.

* Full recomputation: Suitable for extreme environments where memory resources are critically limited. In this mode, except for the input data, all activations are recomputed when needed, minimizing memory dependency to the greatest extent.

## Usage

* Selective recomputation:

```bash
--recompute-activations   # Enable selective recomputation
```

* Full recomputation:

```bash
--recompute-granularity full    # Enable full recomputation
--recompute-method uniform/block  # Specify the recomputation method
```

`--recompute-method` can be set to either `uniform` or `block`:

* `--recompute-method uniform`: Divides Transformer layers evenly into groups (each group size is `--recompute-num-layers`), storing inputs and activations per group.
* `--recompute-method block`: Recomputes the first `--recompute-num-layers` Transformer layers, while the remaining layers are not recomputed.

> [!NOTE]
>
> * When `--recompute-activations` and `--recompute-granularity full` are configured together, selective recomputation takes effect.
> * When the script is configured with `--recompute-method block`, `--recompute-granularity full`, and `--num-layers-per-virtual-pipeline-stage N`, users can configure how many layers each VPP stage recomputes via the `--recompute-num-layers N` parameter. The parameter `--enable-recompute-layers-per-pp-rank` can be used to modify the semantics of `--recompute-num-layers N` in this scenario, where the new semantics indicate that VPP is ignored and the number of recomputed layers is configured per PP stage.
> * In the legacy branch, enabling `--use-flash-attn` will prevent the use of selective recomputation.

## Effects

Adopting recomputation brings a clear trade-off:

* Avoid long-term retention of intermediate activations, significantly reducing memory usage.

* Recomputing activations comes with extra computational cost and performance degradation. As such, the adoption and configuration of recompute should take memory usage into account holistically.
