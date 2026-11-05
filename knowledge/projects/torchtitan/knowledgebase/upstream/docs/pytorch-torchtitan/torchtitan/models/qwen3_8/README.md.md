---
id: doc-pytorch-torchtitan-9463f9fb07c35726d79b
title: pytorch/torchtitan / torchtitan/models/qwen3_8/README.md
engine: torchtitan
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: pytorch/torchtitan
commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
path: torchtitan/models/qwen3_8/README.md
raw_sha256: 0413c2e1e2fe2e5500fbc7e0566c7e6db3b80d3418b4709f9dd26128ca4dc228
sources: []
generated_body_sha256: 6661e8af980ac0ee833adcf2264b2e98172530947e143e3a40579df1083090fa
source_state: current-scan
---

# pytorch/torchtitan / torchtitan/models/qwen3_8/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/qwen3_8/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Qwen3.8

This is a lightweight version-specific package for Qwen3.8 checkpoints. The
model architecture and implementation remain in `torchtitan/models/qwen3_5/`
because Qwen3.5 and Qwen3.8 use the same Qwen3.5 Hugging Face architecture.

This directory owns only:

- the Qwen3.8 model flavors;
- documentation for Qwen3.8 checkpoint-specific behavior.

The shared model, Gated DeltaNet, RoPE, vision encoder, sharding,
parallelization, and state-dict adapter keep their existing Qwen3.5 names.

## Supported Parallelisms

Qwen3.8 reuses the Qwen3.5 model implementation and parallelization (see the
note above), so it supports the same parallelisms documented in
[Qwen3.5's Supported Parallelisms](../qwen3_5/README.md#supported-parallelisms):

| Feature | Notes |
|---------|-------|
| FSDP / HSDP | Decoder sharded per-layer; vision encoder sharded as a single unit (one AllGather) |
| Tensor Parallelism (TP) | With Sequence Parallel; head-sharded TP on GatedDeltaNet projections |
| Expert Parallelism (EP) | For the `2.4T-A95B` MoE variant |
| Pipeline Parallel (PP) | Vision encoder assigned to first stage; 1F1B and Interleaved1F1B schedules |
| Context Parallelism (CP) | Attention Gym native CP for GatedDeltaNet; full attention supports K/V all-gather with contiguous, head-tail, or PTRR partitions and Ulysses with contiguous partitions |
| Sample Packing | Opt-in via `MMSamplePackingConfig` |

## Model variants

| Variant | Type | LLM dim | Layers | Heads | KV heads | Experts | Top-k | Vision |
|---|---|---:|---:|---:|---:|---:|---:|---|
| `27B` | Dense | 5120 | 64 | 24 | 4 | - | - | Yes |
| `2.4T-A95B` | MoE | 8192 | 92 | 64 | 4 | 512 | 10 | No |

Qwen3.8-27B is architecturally identical to Qwen3.5-27B. The 2.4T-A95B
checkpoint scales the same MoE decoder and stores its text-only language-model
weights under `model.*` instead of the multimodal `model.language_model.*`
prefix.

The Hugging Face configs add `output_gate_type: "swish"`; this matches the
existing SiLU/Swish gate in TorchTitan's Gated DeltaNet. Full-attention output
gating remains sigmoid. Released MTP weights are not imported or exported
because this model path currently trains only the primary next-token decoder.

Pre-quantized FP8 repositories are not supported by the checkpoint adapter;
use the non-FP8 checkpoints as conversion inputs.

## Hugging Face assets

The former training configurations expected assets at
`assets/hf/Qwen3.8-27B` and `assets/hf/Qwen3.8-2.4T-A95B`, respectively. These
paths remain useful starting points for user-owned recipes, but TorchTitan does
not ship an unverified training recipe for either flavor.
