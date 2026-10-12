---
id: doc-inclusionai-areal-304990610c6bd231a838
title: areal-project/AReaL / docs/en/reference/lora.md
engine: areal
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: areal-project/AReaL
commit: 01de0a83e17cb12c918fc791466138ddbd4168c9
path: docs/en/reference/lora.md
raw_sha256: 816d15f449eefe9c07931c23634045390188e436af64cd61fc24ad78621b9227
sources: []
generated_body_sha256: dce0609973dc12445a7979075f1396f6267789182c4b65bf577b5ae106ffb4f4
source_state: current-scan
---

# areal-project/AReaL / docs/en/reference/lora.md

[Original at fixed commit](https://github.com/areal-project/AReaL/blob/01de0a83e17cb12c918fc791466138ddbd4168c9/docs/en/reference/lora.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# LoRA Reference

LoRA is a parameter-efficient fine-tuning technique that injects trainable low-rank
matrices into pre-trained weights, typically around linear layers. Compared with
full-parameter fine-tuning, this reduces memory usage and compute cost substantially,
making RL fine-tuning of large models much more practical on limited hardware.

In AReaL, this is especially useful for:

- reinforcement learning with very large models, including 70B+ models, on relatively
  modest hardware such as 8 x 80 GB GPUs,
- enabling larger batch sizes because LoRA reduces training memory pressure,
- simplifying transfer and deployment because only the LoRA adapters need to be saved
  and shipped,
- \[Future\] fine-tune multiple LoRA adapters more efficiently in parallel for better
  hardware utilization (see RFC
  [#609](https://github.com/areal-project/AReaL/issues/609)).

This guide explains how to enable LoRA in RL training and configure the related
parameters.

## Backend Support

The current LoRA support matrix in AReaL is:

| Engine   | vLLM | SGLang |
| -------- | ---- | ------ |
| FSDP2    | ✅   | ✅     |
| Megatron | ✅   | ❌     |
| Archon   | ❌   | ❌     |

**Example scripts:**

| Engine       | Example script                                    |
| ------------ | ------------------------------------------------- |
| FSDP2        | `examples/math/gsm8k_grpo_lora.yaml`              |
| Megatron     | `examples/math/gsm8k_grpo_megatron_lora.yaml`     |
| Megatron MoE | `examples/math/gsm8k_grpo_megatron_lora_moe.yaml` |

For Megatron + vLLM, AReaL now supports:

- LoRA fine-tuning on MoE architectures such as Qwen3 MoE with XCCL-based LoRA weight.
- Cross-node LoRA training when the Megatron and rollout groups span multiple nodes.

## Core LoRA Parameters

| Parameter         | What it controls                                                                                        | Typical values        |
| ----------------- | ------------------------------------------------------------------------------------------------------- | --------------------- |
| `use_lora`        | Enables LoRA fine-tuning mode.                                                                          | `true` / `false`      |
| `lora_rank` (`r`) | Rank of the low-rank adapters. Higher rank increases capacity and memory/compute cost.                  | `8`, `16`, `32`, `64` |
| `lora_alpha`      | LoRA scaling factor. Effective adapter scale is commonly thought of as proportional to `alpha / r`.     | `16`, `32`, `64`      |
| `target_modules`  | Which model submodules receive LoRA adapters. This is the most important architecture-specific setting. | e.g. \[`all-linear`\] |
| `peft_type`       | PEFT method type. In AReaL configs, this is LoRA.                                                       | `lora`                |

## Practical Notes

- Start with `r=16` or `r=32` for most models, then tune upward only if needed.
- Keep `target_modules` consistent with your model architecture naming.
- For Megatron backend, LoRA requires `megatron-bridge` instead of `mbridge`.