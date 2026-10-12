---
id: doc-nvidia-megatron-lm-77e24aebfbf4066a9890
title: NVIDIA/Megatron-LM / docs/user-guide/features/megatron_rl.md
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
path: docs/user-guide/features/megatron_rl.md
raw_sha256: a8dd0e119f77a4e468da8575c15ecdc867ea00023bfb44fe46c400ac6cb06395
sources: []
generated_body_sha256: 6d39f4d10f0a3e73737657aa7a320c896a37390b3e176fd0ebe09d5d5d323338
source_state: current-scan
---

# NVIDIA/Megatron-LM / docs/user-guide/features/megatron_rl.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/docs/user-guide/features/megatron_rl.md)

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

# Megatron RL

Reinforcement learning library for post-training large language models at scale.

## Overview

[**Megatron RL**](https://github.com/NVIDIA/Megatron-LM/tree/dev/megatron/rl) adds native reinforcement learning capabilities to Megatron-LM for large-scale RL-based post-training of foundation models.

> **Note:** Megatron RL is under active development and primarily designed for research teams exploring RL post-training on modern NVIDIA hardware. For production deployments, use [**NeMo RL**](https://github.com/NVIDIA-NeMo/RL).

## Key Features

- **Decoupled Design** - Separates agent and environment logic from the core RL implementation
- **Inference Backends** - Megatron, OpenAI, and Hugging Face inference stacks
- **Trainer or Evaluator** - Manages rollout generation and coordinates with inference systems
- **Megatron Integration** - Native integration with Megatron Core inference system

## Architecture

### Components

**Agents and Environments**
- Accept inference handles
- Return experience rollouts with rewards
- Implement custom RL logic

**Trainer or Evaluator**
- Controls rollout generation
- Coordinates with inference systems
- Manages training loops

**Inference Interface**
- Exposes a `.generate(prompt, **generation_args)` endpoint
- Supports multiple backends (Megatron, OpenAI, Hugging Face)

## Use Cases

- RLHF (Reinforcement Learning from Human Feedback)
- Custom reward-based fine-tuning
- Policy optimization for specific tasks
- Research on RL post-training techniques

## Resources

- **[Megatron RL GitHub](https://github.com/NVIDIA/Megatron-LM/tree/dev/megatron/rl)**: Source code and documentation
- **[Megatron Core Inference](../../api-guide/core/transformer.md)**: Native inference integration