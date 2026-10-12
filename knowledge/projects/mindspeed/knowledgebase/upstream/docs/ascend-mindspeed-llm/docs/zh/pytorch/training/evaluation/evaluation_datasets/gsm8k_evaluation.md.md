---
id: doc-ascend-mindspeed-llm-7e2b427c21ebb18f3ffb
title: Ascend/MindSpeed-LLM / docs/zh/pytorch/training/evaluation/evaluation_datasets/gsm8k_evaluation.md
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
path: docs/zh/pytorch/training/evaluation/evaluation_datasets/gsm8k_evaluation.md
raw_sha256: d33b61a3d4c62329b8476779ba68868358dc65aec7974d92bd46331b53f6507f
sources: []
generated_body_sha256: 5ad0da2feeb4e4800d587e3c3707c05939ee7c31c8af750635758599a672f87c
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/zh/pytorch/training/evaluation/evaluation_datasets/gsm8k_evaluation.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/zh/pytorch/training/evaluation/evaluation_datasets/gsm8k_evaluation.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# GSM8K 评估

## 使用场景

### 问题描述

**GSM8K（小学数学 8K）**数据集包含 8500 道高质量、语言多样化的小学数学应用题，旨在支持对需要多步推理的基础数学问题进行问答任务。

### 特性介绍

GSM8K 评估集专注于以下方面：

- 这些题目通常需要经过 2 到 8 个步骤来求解，其解决过程主要依赖于依次进行一系列简单的计算，利用基本的算术运算（加、减、乘、除）得到最终答案。
- 此外，解题过程采用自然语言来描述，而非单纯的数学表达式。

目前 MindSpeed-LLM 仓库对 GSM8K 评估有两种评估模式：

## 使用方法

### 1. 直接评估模式（默认）

#### 使用影响

- 此模式将会直接将[模板提示](../../../../../../mindspeed_llm/tasks/evaluation/eval_impl/fewshot_template/gsm8k_3shot_template.json)和需要回答的问题输入到模型中，进行评估

#### 推荐参数配置

【--max-new-tokens】

设置为 512。

### 2. 思维链（CoT）评估模式

#### 使用影响

- 该模式会将思维链（CoT）提示应用于 GSM8K 任务。
- 此模式将会读取 GSM8K 评估的 CoT 模板的 prompt 作为评估模板，在与需要模型回答的问题连接后，输入到模型中，进行评估。

#### 推荐参数配置

【--max-new-tokens】

设置为 512 或者以上。

【--chain-of-thought】

使能思维链（CoT）评估模式

## 参考文献

Cobbe, K., Kosaraju, V., Bavarian, M., Chen, M., Jun, H., Kaiser, L., Plappert, M., Tworek, J., Hilton, J., Nakano, R., Hesse, C., & Schulman, J. (2021). *Training verifiers to solve math word problems* [Preprint]. arXiv preprint arXiv:2110.14168.
