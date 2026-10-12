---
id: doc-pytorch-torchtitan-d9fb2d46adfe297e343a
title: pytorch/torchtitan / torchtitan/quantization/README.md
engine: torchtitan
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: pytorch/torchtitan
commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
path: torchtitan/quantization/README.md
raw_sha256: c83d0b237d478207891164a49972280f065b7bbd9026ad8fc91cf8aa91d587c9
sources: []
generated_body_sha256: 8d343768e3d03f495955d7e570663b61d67d4c4b90999601c442874c28c9a720
source_state: current-scan
---

# pytorch/torchtitan / torchtitan/quantization/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/quantization/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Low-Precision Training

TorchTitan provides the following low-precision training formats:

- [MXFP8](mxfp8/README.md) for dense and MoE models on Blackwell GPUs.
- [NVFP4](nvfp4/README.md) for experimental dense training on Blackwell GPUs.

## TorchAO and TorchTitan Boundary

TorchTitan owns the training integration for these formats: modules, autograd,
recipe selection, distributed composition, and the lifecycle of quantized
weight operands. Persistent model parameters and checkpoint state remain in
high precision.

TorchAO supplies the low-level quantization, layout-transformation, and matrix
multiplication kernels. This boundary lets TorchTitan integrate low-precision
training with FSDP and other parallelisms while TorchAO evolves and optimizes
the underlying kernels independently.
