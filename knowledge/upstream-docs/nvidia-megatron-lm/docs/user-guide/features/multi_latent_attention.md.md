---
id: doc-nvidia-megatron-lm-9ba3134272afaa2ea0f7
title: NVIDIA/Megatron-LM / docs/user-guide/features/multi_latent_attention.md
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
path: docs/user-guide/features/multi_latent_attention.md
raw_sha256: 5838806b6b555a21a37a703371971c247066929fec4d4e612a06c4645dd40fea
sources: []
generated_body_sha256: 8afc228066322e830859daa7af820cdd71cbd4e6a20bf7954415b93c43b6605a
source_state: current-scan
---

# NVIDIA/Megatron-LM / docs/user-guide/features/multi_latent_attention.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/docs/user-guide/features/multi_latent_attention.md)

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

# Multi-Latent Attention

## Multi-Latent Attention Overview

Multi-Latent Attention (MLA) is an attention variant from the DeepSeek team. It uses multiple latent spaces to change how attention is computed. That design often lowers cost for large language models (LLMs) compared with standard attention and can shrink the KV cache. The DeepSeek-V2 technical report compares MLA to Multi-Head Attention (MHA) on quality and cache size.

## Enabling Multi-Latent Attention

To enable MLA in Megatron-LM, set the following on the command line:

- `--multi-latent-attention` to turn on MLA.
- Use `MLATransformerConfig` for MLA-specific model settings when you build the training configuration.