---
id: doc-nvidia-megatron-lm-686d19f37661fca270bf
title: NVIDIA/Megatron-LM / docs/user-guide/features/moe.md
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
path: docs/user-guide/features/moe.md
raw_sha256: 004d1c2bc849bb6a96e77099872a1cb282907e28be774953c2ae40aa39b094c6
sources: []
generated_body_sha256: 994ec18180034b7c9022009b05b0afe6717adbb62007a22afb8f7f6fd2307697
source_state: current-scan
---

# NVIDIA/Megatron-LM / docs/user-guide/features/moe.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/docs/user-guide/features/moe.md)

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

# Mixture of Experts

```{toctree}
:maxdepth: 1
:caption: MoE Features

multi_token_prediction
multi_latent_attention
../../api-guide/router_replay
```

```{include} ../../../megatron/core/transformer/moe/README.md
```