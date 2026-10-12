---
id: doc-modelscope-ms-swift-6b61deea90ab6712de0d
title: modelscope/ms-swift / docs/source_en/Megatron-SWIFT/GKD.md
engine: swift
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: modelscope/ms-swift
commit: 22249748429ce7e8516640e35cbe997e572a233a
path: docs/source_en/Megatron-SWIFT/GKD.md
raw_sha256: 76b27c78f2e483b20c090a76618bde680edc6c56f2b11ebb12b91c4667697298
sources: []
generated_body_sha256: 6d1ee10ae0c854eb2459747f56f7edcd1820c37cf60fdc6de9acc410b462339c
source_state: current-scan
---

# modelscope/ms-swift / docs/source_en/Megatron-SWIFT/GKD.md

[Original at fixed commit](https://github.com/modelscope/ms-swift/blob/22249748429ce7e8516640e35cbe997e572a233a/docs/source_en/Megatron-SWIFT/GKD.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# GKD

If you are new to GKD/OPD-RL, please refer to the [distillation documentation](../Instruction/Distillation.md) first.

GKD (Generalized Knowledge Distillation) is a training method that transfers knowledge from a teacher model to a student model by computing the Jensen-Shannon Divergence (JSD) loss between their output distributions.

## Feature Support

Megatron GKD currently supports the following features:

- **Training Modes**: Full parameter training and LoRA fine-tuning
- **Parallelism Strategies**: Context Parallel (CP), Pipeline Parallel (PP), Tensor Parallel (TP), and Expert Parallel (EP)
- **Model Support**: Compatible with LLMs and MLLMs in Megatron-SWIFT
- **Teacher Offload**: Supports offloading teacher model to CPU to save GPU memory
- **Online Generation**: Supports on-policy generation using vLLM for student model
- **Multi-turn Training**: Supports multi-turn GKD via `--multi_turn_scheduler`, sharing the same `MultiTurnScheduler` infrastructure as GRPO.

## Parameters

### GKD-specific Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--teacher_model` | str | - | Path or model ID of the teacher model<br>*Can be omitted when using `teacher_model_server` |
| `--teacher_model_server` | str | None | Teacher API URL; single URL or multi-teacher JSON. See [distillation docs](../Instruction/Distillation.md#multi-teacher-routing) |
| `--teacher_tag_key` | str | `"dataset"` | Column name for matching sample tags to teacher `tags` in multi-teacher routing |
| `--gkd_logits_topk` | int | None | Number of Top-K logits; required when using external API |
| `--beta` | float | 0.5 | JSD divergence interpolation coefficient:<br>• 0.0: Forward KL<br>• 0.5: Symmetric JSD<br>• 1.0: Reverse KL |
| `--lmbda` | float | 0.5 | On-Policy learning probability:<br>• 0.0: Pure Off-Policy<br>• 1.0: Pure On-Policy |
| `--temperature` | float | 0.9 | Temperature for sampling and loss computation |
| `--sft_alpha` | float | 0 | Mix in a  proportion of SFT loss; applied to non-student-generated completions |
| `--max_completion_length` | int | 512 | Maximum tokens for generation |

### Batch-related Parameters

Same as Megatron SFT, use the following parameters to control batch size:

| Parameter | Description |
|-----------|-------------|
| `--micro_batch_size` | Training batch size per DP group |
| `--global_batch_size` | Global batch size: `micro_batch_size × dp_size × gradient_accumulation_steps` |

## Reference

For more parameters, please refer to [Command-line Parameters](./Command-line-parameters.md)

For training scripts, please refer to [Megatron GKD Scripts](https://github.com/modelscope/ms-swift/blob/main/examples/megatron/rlhf/gkd)

Training script using Teacher Server reference [here](https://github.com/modelscope/ms-swift/blob/main/examples/megatron/rlhf/gkd/teacher_server.sh)