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
commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
path: torchtitan/models/qwen3_8/README.md
raw_sha256: df8758300f5743f46f7eec44f92530253c3c3877b65ab2ff66e4ff102aca143f
sources: []
generated_body_sha256: 3f36eb9ae6c187ca6f2bb47ee77cd167ac3d81071cef33ef1e4b7eafd7745747
source_state: current-scan
---

# pytorch/torchtitan / torchtitan/models/qwen3_8/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/models/qwen3_8/README.md)

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
