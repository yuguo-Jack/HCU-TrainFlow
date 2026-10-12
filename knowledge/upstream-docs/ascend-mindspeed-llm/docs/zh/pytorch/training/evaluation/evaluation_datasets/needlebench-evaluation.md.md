---
id: doc-ascend-mindspeed-llm-b18dd3601fa07c125930
title: Ascend/MindSpeed-LLM / docs/zh/pytorch/training/evaluation/evaluation_datasets/needlebench-evaluation.md
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
path: docs/zh/pytorch/training/evaluation/evaluation_datasets/needlebench-evaluation.md
raw_sha256: bdaef516389961ff148016b82eae61751084faacdcef6914ca0c547a1643d0a4
sources: []
generated_body_sha256: 66cfda954a7447114d50d235e94cc703a07c519453e72024724d735eb60f219d
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/zh/pytorch/training/evaluation/evaluation_datasets/needlebench-evaluation.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/zh/pytorch/training/evaluation/evaluation_datasets/needlebench-evaluation.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# NeedleBench 精度测试

## 概述

NeedleBench 是由上海人工智能实验室和清华大学的研究团队开发的一个用于评估大语言模型（LLMs）在处理超长文本（长达百万级上下文窗口）时的检索和推理能力的框架。它专门设计用于压力测试模型在中英双语环境下的长文本处理能力。

下载 NeedleBench 测试集：[opencompass/NeedleBench](https://huggingface.co/datasets/opencompass/NeedleBench)

下载 tiktoken 所需要的缓存文件：[cl100k_base.tiktoken](https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken)

目前 MindSpeed-LLM 仓库仅支持 Single-Needle-Retrieval (S-RT) 测试。

## 参数配置

- --max-new-tokens 设置为 64
- --seq-length, --max-position-embeddings, --max-tokens-to-oom 可设置为 4096, 8192, 32768, 131072, 262144, 524288, 1048576，用于测试对应长度的 NeedleBench 精度
- 开启 YARN。YARN 的配置参照 [YARN](../../../features/mcore/yarn.md) 的说明文档

NeedleBench 精度测试如下：

| 模型                                                                 | 任务     | MindSpeed-LLM | 社区([OpenCompass](https://opencompass.readthedocs.io/en/latest/advanced_guides/needleinahaystack_eval.html)) |
|--------------------------------------------------------------------|--------|---------------|---------------------|
| [Qwen2-7B-Instruct](https://huggingface.co/Qwen/Qwen2-7B-Instruct) | NeedleBench-128K-Single-Needle-Retrieval   | 70.19%        | 70.25%              |
| [Qwen2-7B-Instruct](https://huggingface.co/Qwen/Qwen2-7B-Instruct) + YARN                                       | NeedleBench-128K-Single-Needle-Retrieval | 87.03%        | 88.63%              |
