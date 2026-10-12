---
id: doc-ascend-mindspeed-llm-34100149fd70295dc454
title: Ascend/MindSpeed-LLM / docs/zh/menu/_menu.md
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
path: docs/zh/menu/_menu.md
raw_sha256: cf0ffe505a7a0ec360c6275ebbf69f00477aa14fda0a20ce0e646d5c28b4d50e
sources: []
generated_body_sha256: b7428692adcd641eef277c3ecb2a876257181a4c2d148db9ba4012b710cba223
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/zh/menu/_menu.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/zh/menu/_menu.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# MindSpeed LLM

- [MindSpeed LLM简介](../introduction.md)
- [软件安装](../pytorch/training/install_guide.md)
- [模型使用]()
  - [导读](../pytorch/training/user_guide.md)
  - [模型支持列表](../pytorch/models/supported_models.md)
  - [大模型分布式预训练](../pytorch/training/pretrain/mcore/pretrain.md)
  - [数据和权重在线加载训练](../pytorch/training/pretrain/mcore/train_from_hf.md)
  - [单样本微调](../pytorch/training/finetune/mcore/single_sample_finetune.md)
  - [FSDP2后端微调](../pytorch/training/finetune/fsdp2/finetune_fsdp2.md)
  - [流式推理](../pytorch/training/inference/inference.md)
- [特性说明]()
  - [特性列表（基于Megatron训练后端）](../pytorch/features/README.md)
  - [全量参数介绍（基于FSDP2训练后端）](../pytorch/features/fsdp2/arguments.md)
- [模型迁移]()
  - [模型适配指南（基于FSDP2训练后端）](../pytorch/develop/fsdp2/model_adaptation.md)
  - [精度调试](../pytorch/develop/precision_issue.md)
- [模型性能调优](../pytorch/tuning/fsdp2_backend_performance_optimization.md)
- [开发工具]()
  - [性能数据采集](../pytorch/tools/profiling.md)
  - [精度数据采集](../pytorch/tools/msprobe.md)
  - [模型输入输出采集](../pytorch/tools/model_io_trace.md)
  - [权重转换](../pytorch/tools/checkpoint_convert_hf_mcore_large_params.md)
- [FAQ](../FAQ.md)
