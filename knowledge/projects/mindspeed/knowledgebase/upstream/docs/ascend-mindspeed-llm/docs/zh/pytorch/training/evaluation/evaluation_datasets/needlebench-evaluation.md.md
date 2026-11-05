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
commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
path: docs/zh/pytorch/training/evaluation/evaluation_datasets/needlebench-evaluation.md
raw_sha256: 00ab059dec25540732af6d50424e5a4f27a229e4d7eebb00e49d75db84633335
sources: []
generated_body_sha256: f3e04e05c83687bfca6c7db00a30290365bbd8ef4cbfd80f7b796aff48fe17eb
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/zh/pytorch/training/evaluation/evaluation_datasets/needlebench-evaluation.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/f5f84bbbac05be79f883b30629d7f637e6f4649e/docs/zh/pytorch/training/evaluation/evaluation_datasets/needlebench-evaluation.md)

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

| 模型                                                                 | 任务     | MindSpeed-LLM | 社区([OpenCompass](https://doc.opencompass.org.cn/faq/needleinahaystack_eval.html)) |
|--------------------------------------------------------------------|--------|---------------|---------------------|
| [Qwen2-7B-Instruct](https://huggingface.co/Qwen/Qwen2-7B-Instruct) | NeedleBench-128K-Single-Needle-Retrieval   | 70.19%        | 70.25%              |
| [Qwen2-7B-Instruct](https://huggingface.co/Qwen/Qwen2-7B-Instruct) + YARN                                       | NeedleBench-128K-Single-Needle-Retrieval | 87.03%        | 88.63%              |
