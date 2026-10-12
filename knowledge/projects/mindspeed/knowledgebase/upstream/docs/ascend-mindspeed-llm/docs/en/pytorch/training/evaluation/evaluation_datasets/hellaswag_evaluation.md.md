---
id: doc-ascend-mindspeed-llm-c8e905a367298b760783
title: Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_datasets/hellaswag_evaluation.md
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
path: docs/en/pytorch/training/evaluation/evaluation_datasets/hellaswag_evaluation.md
raw_sha256: a513ab80b0ac5f4e37a4b8e1ed4b79a17d428b638612aa51d65198eb3fba7f6a
sources: []
generated_body_sha256: a3c4a10324f5f6c4222588aa42bbe807af391de0ffdfe00777404bef1e7a6a74
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_datasets/hellaswag_evaluation.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/training/evaluation/evaluation_datasets/hellaswag_evaluation.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# HellaSwag Evaluation

## Use Cases

### Problem Description

The HellaSwag evaluation set mainly tests the performance of natural language processing models on common-sense reasoning tasks. By providing context and multiple options, the model needs to choose the most reasonable next event or sentence ending. This task design evaluates how well the model understands complex situations and reasons with common sense.

### Features

The HellaSwag evaluation set focuses on the following aspects:

1. **Common-sense reasoning ability**: It tests whether the model can understand common sense in everyday situations and choose the most reasonable answer.
2. **Adversarial filtering**: It uses adversarial filtering to ensure that the questions in the dataset are challenging and can expose model weaknesses.
3. **Diverse scenarios**: The dataset covers a variety of real-life scenarios, such as sports, cooking, and family life, which ensures diversity and complexity in the data.
4. **Multiple-choice design**: Each question contains one context description and four options, and the model must choose the most reasonable answer from the options.
5. **High-quality annotation**: The dataset undergoes strict human annotation and verification to ensure accuracy and consistency.
6. **Suitable for multiple tasks**: It can be used for model training, evaluation, and optimization, and it performs especially well in practical applications such as dialogue systems and intelligent assistants.

Currently, the MindSpeed LLM repository supports the following evaluation mode for the HellaSwag evaluation set:

## Usage

### Direct Evaluation Mode

#### Impact

- This mode sends the question to be answered directly to the model for evaluation.

#### Recommended Parameters

`--max-new-tokens`

Set it to 32 to ensure that the task output is complete.
