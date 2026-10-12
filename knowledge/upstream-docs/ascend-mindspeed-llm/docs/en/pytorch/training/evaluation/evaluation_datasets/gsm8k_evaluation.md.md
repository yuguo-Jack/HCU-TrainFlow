---
id: doc-ascend-mindspeed-llm-ab0977fa7908a4990644
title: Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_datasets/gsm8k_evaluation.md
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
path: docs/en/pytorch/training/evaluation/evaluation_datasets/gsm8k_evaluation.md
raw_sha256: 85a8fb071ef3fcec0d76a1dcea640b4394eebf521d34b041b0438c28509a9ac9
sources: []
generated_body_sha256: 6b3aa998723840be77417bed7c6e26806afba9f4e54e646065d79fdb50581d3e
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_datasets/gsm8k_evaluation.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/training/evaluation/evaluation_datasets/gsm8k_evaluation.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# GSM8K Evaluation

## Use Cases

### Problem Description

The **Grade School Math 8K (GSM8K)** dataset contains 8,500 high-quality, linguistically diverse grade-school math word problems. It is designed to support question-answering tasks for basic math problems that require multi-step reasoning.

### Features

The GSM8K evaluation set focuses on the following aspects:

- These problems usually require 2 to 8 steps to solve. The solution process mainly depends on carrying out a series of simple calculations in sequence and using basic arithmetic operations, including addition, subtraction, multiplication, and division, to obtain the final answer.
- In addition, the solution process is described in natural language rather than as a simple mathematical expression.

Currently, the MindSpeed LLM repository provides two GSM8K evaluation modes.

## Usage

### 1. Direct Evaluation Mode (Default)

#### Impact

- This mode concatenates the [template prompt](../../../../../../mindspeed_llm/tasks/evaluation/eval_impl/fewshot_template/gsm8k_3shot_template.json) with the question to be answered, then feeds the result to the model for evaluation.

#### Recommended Parameters

`--max-new-tokens`

Set this to 512.

### 2. Chain-of-Thought (CoT) Evaluation Mode

#### Impact

- This mode applies CoT prompts to GSM8K tasks.
- This mode uses the CoT template prompt as the evaluation template, concatenates it with the question the model needs to answer, and then feeds the result to the model for evaluation.

#### Recommended Parameters

`--max-new-tokens`

Set this to 512 or higher.

`--chain-of-thought`

Enable CoT evaluation mode.

## References

Cobbe, K., Kosaraju, V., Bavarian, M., Chen, M., Jun, H., Kaiser, L., Plappert, M., Tworek, J., Hilton, J., Nakano, R., Hesse, C., & Schulman, J. (2021). *Training verifiers to solve math word problems* [Preprint]. arXiv preprint arXiv:2110.14168.
