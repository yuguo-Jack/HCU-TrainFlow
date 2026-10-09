---
id: doc-nvidia-megatron-lm-d04089776e8b7ba8bc26
title: NVIDIA/Megatron-LM / docs/user-guide/features/index.md
engine: megatron
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: NVIDIA/Megatron-LM
commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
path: docs/user-guide/features/index.md
raw_sha256: ec6321bd33ed44752c83bc794bac8caba829d5f3de85e90dc31a06a5552aee7e
sources: []
generated_body_sha256: 7a73fa3c8fd914326322f7821988950648ffb291d1fb00da3e5a99a0d9f90a64
source_state: current-scan
---

# NVIDIA/Megatron-LM / docs/user-guide/features/index.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/docs/user-guide/features/index.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!---
   Copyright (c) 2022-2026, NVIDIA CORPORATION. All rights reserved.
   NVIDIA CORPORATION and its licensors retain all intellectual property
   and proprietary rights in and to this software, related documentation
   and any modifications thereto. Any use, reproduction, disclosure or
   distribution of this software and related documentation without an express
   license agreement from NVIDIA CORPORATION is strictly prohibited.
-->

# Advanced Features

Guides for Megatron Core training and inference features.

```{toctree}
:maxdepth: 2

cuda_graph
fine_grained_activation_offloading
low_precision_training
moe
megatron_fsdp
dist_optimizer
checkpoint-merge
optimizer_cpu_offload
paged_stash
tokenizers
megatron_energon
megatron_rl
../../mcore-inference-user-guide
```