---
id: doc-ascend-mindspeed-llm-f8d196836caeafd34112
title: Ascend/MindSpeed-LLM / docs/en/_menu.md
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
path: docs/en/_menu.md
raw_sha256: dc7bde787f0a70bf97089e54a9e6f3b20f7260ffc4ea7e55d1560c886e6ef642
sources: []
generated_body_sha256: ace88e489e76c5b98e748b623e0c71e6ad8138c223283666e778c7467ad43eed
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/_menu.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/_menu.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# MindSpeed LLM

- [MindSpeed LLM Introduction](introduction.md)
- [Software Installation](./pytorch/training/install_guide.md)
- [Model Usage]()
  - [User Guide](./pytorch/training/user_guide.md)
  - [Supported Models](./pytorch/models/supported_models.md)
  - [Large Model Distributed Pre-Training](./pytorch/training/pretrain/mcore/pretrain.md)
  - [Training with Online Data and Weight Loading](./pytorch/training/pretrain/mcore/train_from_hf.md)
  - [Single-Sample Fine-Tuning](./pytorch/training/finetune/mcore/single_sample_finetune.md)
  - [Streaming Inference](./pytorch/training/inference/inference.md)
- [Feature Description]()
  - [Feature List (Based on Megatron Training Backend)](./pytorch/features/README.md)
  - [Full Parameter Reference (Based on FSDP2 Training Backend)](./pytorch/features/fsdp2/arguments.md)
- [Model Migration]()
  - [Model Adaptation Guide (Based on FSDP2 Training Backend)](./pytorch/develop/fsdp2/model_adaptation.md)
  - [Precision Debugging](./pytorch/develop/precision_issue.md)
- [Model Performance Tuning](./pytorch/tuning/fsdp2_backend_performance_optimization.md)
- [Development Tools]()
  - [Performance Data Collection](./pytorch/tools/profiling.md)
  - [Weight Conversion](./pytorch/tools/checkpoint_convert_hf_mcore_large_params.md)
- [FAQ](FAQ.md)
