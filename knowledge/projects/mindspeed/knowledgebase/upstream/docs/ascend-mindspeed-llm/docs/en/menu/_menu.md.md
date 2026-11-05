---
id: doc-ascend-mindspeed-llm-5f12ca18cb1bda7383fb
title: Ascend/MindSpeed-LLM / docs/en/menu/_menu.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
path: docs/en/menu/_menu.md
raw_sha256: 52b51b649996df225921936285f90caa001c021746f3021d4ebb916fa9daccb2
sources: []
generated_body_sha256: 95f0c0389e1a35e63ce521a3c64ea589a8460f463f161e6328d493ef07ff59c6
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/menu/_menu.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/f5f84bbbac05be79f883b30629d7f637e6f4649e/docs/en/menu/_menu.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# MindSpeed LLM 

- [MindSpeed LLM Introduction](../introduction.md)
- [Software Installation](../pytorch/training/install_guide.md)
- [Model Usage]()
  - [User Guide](../pytorch/training/user_guide.md)
  - [Supported Models](../pytorch/models/supported_models.md)
  - [Distributed LLM Pretraining](../pytorch/training/pretrain/mcore/pretrain.md)
  - [Training with Online Data and Weight Loading](../pytorch/training/pretrain/mcore/train_from_hf.md)
  - [Single-Sample Fine-Tuning](../pytorch/training/finetune/mcore/single_sample_finetune.md)
  - [Fine-Tuning with the FSDP2 Backend](../pytorch/training/finetune/fsdp2/finetune_fsdp2.md)
  - [Streaming Inference](../pytorch/training/inference/inference.md)
- [Feature Description]()
  - [Feature List (Based on the Megatron Training Backend)](../pytorch/features/README.md)
  - [Full Parameter Reference (Based on the FSDP2 Training Backend)](../pytorch/features/fsdp2/arguments.md)
- [Model Migration]()
  - [Model Adaptation Guide (Based on the FSDP2 Training Backend)](../pytorch/develop/fsdp2/model_adaptation.md)
  - [Precision Debugging](../pytorch/develop/precision_issue.md)
- [Model Performance Tuning](../pytorch/tuning/fsdp2_backend_performance_optimization.md)
- [Development Tools]()
  - [Performance Data Collection](../pytorch/tools/profiling.md)
  - [Precision Data Collection](../pytorch/tools/msprobe.md)
  - [Model Input and Output Collection](../pytorch/tools/model_io_trace.md)
  - [Weight Conversion](../pytorch/tools/checkpoint_convert_hf_mcore_large_params.md)
- [FAQ](../FAQ.md)
