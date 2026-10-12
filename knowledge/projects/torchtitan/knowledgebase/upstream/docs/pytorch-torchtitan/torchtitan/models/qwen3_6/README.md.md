---
id: doc-pytorch-torchtitan-1f755df280d514521f8a
title: pytorch/torchtitan / torchtitan/models/qwen3_6/README.md
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
path: torchtitan/models/qwen3_6/README.md
raw_sha256: c174605ebba82d4170fb2a649bfd7e646a513d3e406446e8b8771e621f92010e
sources: []
generated_body_sha256: 6071a615095ac7abe9453337bbea373db2cafdf2a2a24b1c86003f27c8cde270
source_state: current-scan
---

# pytorch/torchtitan / torchtitan/models/qwen3_6/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/models/qwen3_6/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Qwen3.6

This is a lightweight version-specific package for Qwen3.6 checkpoints. The
model architecture and implementation remain in `torchtitan/models/qwen3_5/`
because Qwen3.6 uses the same Qwen3.5 Hugging Face architecture.

This directory owns only:

- the Qwen3.6 model flavors;
- documentation for Qwen3.6 checkpoint-specific behavior.

The shared model, Gated DeltaNet, RoPE, vision encoder, sharding,
parallelization, and state-dict adapter keep their existing Qwen3.5 names.

## Model variants

| Variant | Type | LLM dim | Layers | Heads | KV heads | Experts | Top-k |
|---|---|---:|---:|---:|---:|---:|---:|
| `27B` | Dense | 5120 | 64 | 24 | 4 | - | - |
| `35B-A3B` | MoE | 2048 | 40 | 16 | 2 | 256 | 8 |

Both released variants include the Qwen3.5 vision encoder. Released MTP
weights are not imported or exported because this model path currently trains
only the primary next-token decoder.

Pre-quantized FP8 repositories are not supported by the checkpoint adapter;
use the non-FP8 checkpoints as conversion inputs.

## Hugging Face assets

The former training configurations expected assets at
`assets/hf/Qwen3.6-27B` and `assets/hf/Qwen3.6-35B-A3B`, respectively. These
paths remain useful starting points for user-owned recipes, but TorchTitan does
not ship an unverified training recipe for either flavor.
