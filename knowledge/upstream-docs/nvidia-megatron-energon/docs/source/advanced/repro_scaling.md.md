---
id: doc-nvidia-megatron-energon-97bb782056a6c90e960e
title: NVIDIA/Megatron-Energon / docs/source/advanced/repro_scaling.md
engine: energon
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: NVIDIA/Megatron-Energon
commit: d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b
path: docs/source/advanced/repro_scaling.md
raw_sha256: 4cccff0a2238bcdc2d6eabd253855cb3b6eeb16fa77b9bde80a6720a9535b46b
sources: []
generated_body_sha256: 559e0f3799f7d4d7728e2f833c9c7cfee34c98c8a545c8233cb580147dd98e7a
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/advanced/repro_scaling.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/docs/source/advanced/repro_scaling.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# Reproducible Scaling

A special use case is to re-run or continue a training run with the exact same data order, but using a different number of nodes or ranks.

Since version 2.0.0, Megatron Energon supports this behavior if a few constraints are met:

* The energon major version must be the same across runs
* The global batch size must stay the same across runs
* The global batch size must be a multiple of `micro-batch size * world_size * num_workers`
  * The multiple of that is the number of gradient accumulation steps in your training
* The product `world_size * num_workers` must stay the same across runs, such that the global number of workers stays the same
* When using random seed offsets in your  {py:class}`WorkerConfig <megatron.energon.WorkerConfig>`, those need to be the same

By obeying these rules, you will be able to reproduce the same global batches. Let's look at an example.

| Name  | Global batch size | Micro batch size | World size | Number of Workers | Gradient accumulation steps |
| ----- | ----------------- | ---------------- | ---------- | ----------------- | --------------------------- |
| Run 1 | 8                 | 2                | 4          | 1                 | 1                           |
| Run 2 | 8                 | 2                | 1          | 4                 | 4                           |

Iterating the dataset will yield the same global batches for both of these runs, if the seed is set correctly.

In practice, you will need to adapt your worker config accordingly.