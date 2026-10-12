---
id: doc-ascend-mindspeed-llm-80b4de965be96b0b56fc
title: Ascend/MindSpeed-LLM / docs/en/pytorch/training/user_guide.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: 2fed626696175480ae1ab3342a94017301a25209
path: docs/en/pytorch/training/user_guide.md
raw_sha256: 52af8bcecfb8d211d83ad93774fc43cc55e04840715efea6ffaa695b36fcd844
sources: []
generated_body_sha256: 304101f69595a1d4c2a59f32f708dc446aa72aceb70e7d1aa25a285698c13491
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/training/user_guide.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/training/user_guide.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Model Usage Guide

MindSpeed LLM provides an end-to-end LLM training solution, covering distributed pretraining, distributed fine-tuning, and inference.

In [Quick Start (Megatron Training Backend)](./quick_start.md) or [Quick Start (FSDP2 Training Backend)](./fsdp2_quick_start.md), you can use the Qwen3-8B model to quickly master LLM pretraining and fine-tuning tasks. The following table describes in detail how to use MindSpeed LLM models.

**Table 1** Model training solutions and usage instructions

| Category | Content | Usage Scenario | Description |
| :--- | :--- | :--- | :--- |
| Pretraining | [Distributed Pretraining for LLMs](./pretrain/mcore/pretrain.md) | Provides data preprocessing and pretraining scripts for offline model pretraining | <ul><li>To load Hugging Face weights, perform weight conversion in advance.</li><li>To store logs in script files, create the <code>logs</code> folder in the running directory.</li></ul> |
| Pretraining | [Training with Online Data and Weight Loading](./pretrain/mcore/train_from_hf.md) | Integrates data preprocessing, weight conversion, and training into one process, providing a one-click solution from Hugging Face open-source data and weights to training | <ul><li>Currently supported Hugging Face model types include: <code>qwen3</code>, <code>qwen3-moe</code>, <code>deepseek3</code>, <code>glm45-air</code>, <code>bailing_mini</code>, <code>qwen3-next</code>, <code>seed-oss</code>, <code>deepseek32</code>, <code>magistral</code>, <code>deepseek2-lite</code>.</li><li>Currently, the automatic dataset conversion feature supports only the following raw data formats: <code>parquet, arrow, csv, json, jsonl, txt</code>. Other formats are not supported for now.</li><li>Currently, the <code>--enable-mg2hf-convert</code> weight conversion feature supports only single-node or shared storage environments and does not support Megatron-to-HF weight conversion for LoRA fine-tuned weights.</li></ul> |
| Fine-tuning | [Single-Sample Fine-Tuning](./finetune/mcore/single_sample_finetune.md) | Suitable for general instruction fine-tuning of single-turn tasks without historical dependencies | The parallel configuration of training parameters in the fine-tuning script (for example, TP/PP/EP/VPP) must be consistent with that used during weight conversion. |
| Inference | [MindSpeed LLM Streaming Inference](./inference/inference.md) | Supports streaming output of multiple generation strategies such as `greedy_search` and `beam_search` | Streaming inference currently uses a fixed `Instruction` input to compare model inference results. |
