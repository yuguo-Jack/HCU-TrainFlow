---
id: doc-bbuf-ai-infra-auto-driven-skills-ba813fb838238ad21d07
title: BBuf/AI-Infra-Auto-Driven-SKILLS / docs/assets/sglang-model-day0-support-demo/scope-contract.md
engine: tooling
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: BBuf/AI-Infra-Auto-Driven-SKILLS
commit: 154cc565d0374746442bac17bd69368b888f4775
path: docs/assets/sglang-model-day0-support-demo/scope-contract.md
raw_sha256: bf0e209a90c9d3aab2827ca2a11b1e15277d1ef2d5f127f33e82fa02c307fa9e
sources: []
generated_body_sha256: e6643e8e1bb8e286a6bb98786965b5d7541be601dc8da1a9b36e8a14ff1926b9
source_state: current-scan
---

# BBuf/AI-Infra-Auto-Driven-SKILLS / docs/assets/sglang-model-day0-support-demo/scope-contract.md

[Original at fixed commit](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/blob/154cc565d0374746442bac17bd69368b888f4775/docs/assets/sglang-model-day0-support-demo/scope-contract.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Day-0 Scope Contract

## Release Cut

- Model: `Aurora-Hybrid-70B-VL`
- Checkpoint revision: `1111111111111111111111111111111111111111`
- SGLang revision: `2222222222222222222222222222222222222222`
- Primary platform: NVIDIA B200, eight GPUs
- Target release date: 2026-08-15
- Owner: public model-support working group

Day-0 covers one immutable fictional checkpoint and a correctness-first eager
fallback. Optimized kernels are optional unless the model cannot fit.

## Required Capabilities

| Lane | Required value | Success criterion |
| --- | --- | --- |
| Checkpoint | BF16 text-plus-vision | Complete weight audit and deterministic short generation |
| API | Reasoning and one tool call | Streaming/non-streaming fields match |
| Topology | TP8 unified and TP4+TP4 PD | Correctness, state transfer, and liveness pass |
| Speculative | Remote-loaded MTP draft | Target parity for accepted lengths zero through four |
| Multimodal | One RGB image | Processor and server embeddings agree |

## Out of Scope

- AMD and NPU execution
- Quantized MoE kernels
- Multi-image and video requests
