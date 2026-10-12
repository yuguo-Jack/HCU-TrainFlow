---
id: doc-ascend-mindspeed-llm-4442c98b0d5d8af661cf
title: Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_datasets/needlebench-evaluation.md
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
path: docs/en/pytorch/training/evaluation/evaluation_datasets/needlebench-evaluation.md
raw_sha256: b934b53f8d9a5296b310ac65d53eea11eb315541553eef231319588b7f81301c
sources: []
generated_body_sha256: 5763f36793e2f58c645ae0701f7429982870eaa4cab591840231252ab16816b4
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_datasets/needlebench-evaluation.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/training/evaluation/evaluation_datasets/needlebench-evaluation.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# NeedleBench Accuracy Test

## Overview

NeedleBench is a framework developed by a research team at Shanghai Artificial Intelligence Laboratory and Tsinghua University to evaluate the retrieval and reasoning capabilities of LLMs when processing ultra-long text with context windows of up to one million tokens. It is designed specifically to stress-test the long-text processing capabilities of a model in bilingual Chinese-English contexts.

Download the NeedleBench test set: [opencompass/NeedleBench](https://huggingface.co/datasets/opencompass/NeedleBench)

Download the cache file required by `tiktoken`: [cl100k_base.tiktoken](https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken)

Currently, the MindSpeed LLM repository supports only the Single-Needle-Retrieval (S-RT) test.

## Parameter Configuration

- Set `--max-new-tokens` to 64.
- Set `--seq-length`, `--max-position-embeddings`, and `--max-tokens-to-oom` to 4096, 8192, 32768, 131072, 262144, 524288, or 1048576 to evaluate NeedleBench accuracy at the corresponding sequence length.
- Enable YaRN. Configure YaRN according to the [YaRN](../../../features/mcore/yarn.md) documentation.

The NeedleBench accuracy test results are as follows:

| Model | Task | MindSpeed LLM | Community Version ([OpenCompass](https://opencompass.readthedocs.io/en/latest/advanced_guides/needleinahaystack_eval.html)) |
|---|---|---|---|
| [Qwen2-7B-Instruct](https://huggingface.co/Qwen/Qwen2-7B-Instruct) | NeedleBench-128K-Single-Needle-Retrieval | 70.19% | 70.25% |
| [Qwen2-7B-Instruct](https://huggingface.co/Qwen/Qwen2-7B-Instruct) + YaRN | NeedleBench-128K-Single-Needle-Retrieval | 87.03% | 88.63% |
