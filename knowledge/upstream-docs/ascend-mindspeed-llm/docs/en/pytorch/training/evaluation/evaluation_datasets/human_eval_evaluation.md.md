---
id: doc-ascend-mindspeed-llm-f9c0beed78f35b848da7
title: Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_datasets/human_eval_evaluation.md
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
path: docs/en/pytorch/training/evaluation/evaluation_datasets/human_eval_evaluation.md
raw_sha256: cd6792920c32aaf510cefc5bff734b0e831502d33f2212ab3296cf6c8ee4a4f3
sources: []
generated_body_sha256: aa06d71812c80034965332764b309c03d755ff8cb65306e317aa5ade2005c1b2
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_datasets/human_eval_evaluation.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/training/evaluation/evaluation_datasets/human_eval_evaluation.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# HumanEval Evaluation

## Use Cases

### Problem Description

- In the field of evaluating code generation in LLMs, accurately measuring the quality and correctness of generated code is a key problem. The HumanEval dataset provides an effective solution to this challenge.
- It aims to evaluate code generation models objectively and systematically, determine how reliable and practical their generated code is in real scenarios, and help optimize and improve the model so that it better meets the needs of practical applications such as software development.

### Features

The HumanEval dataset has several notable features:

- It contains a series of representative programming problems that cover many common programming task scenarios, such as data structure operations, algorithm implementation, and string processing. These problems can comprehensively assess code generation models across different domains.
- Each problem in the dataset includes a detailed description and corresponding test cases, which provide a clear standard and basis for evaluation and ensure that the evaluation results are objective and accurate.
- Its problem design emphasizes code readability and consistency, which encourages the model to generate high-quality, maintainable code that matches the requirements of real development. Therefore, the dataset provides a comprehensive assessment of code generation models from multiple angles and helps improve model performance so that it can adapt to complex and changing programming application scenarios.

MindSpeed-LLM evaluates the content in the `human_eval` problem set. `human_eval` is the task name of the HumanEval dataset in the code directory.

## Usage

### 1. Direct Evaluation Mode (Default)

#### Impact

- MindSpeed-LLM does not use any prompt template for `human_eval` evaluation. Instead, it evaluates the target question directly and outputs the final answer. In other words, the model directly receives the question-paragraph pair without any prompt template.

- This mode uses beam search for model inference.

- After the LLM outputs an answer for each question, the program uses `logger.info` to indicate whether the question passes evaluation.

#### Recommended Parameters

`--max-new-tokens`

Set this to 1024 to ensure that the code is output completely.

### 2. Alternative Template Output Mode

#### Impact

- Like direct evaluation mode, this evaluation mode also does not use any custom prompt.

- This mode uses the standard inference method for model output. Therefore, it does not use sampling or beam search for inference.

- Unlike direct evaluation mode, this mode judges the inference results of the model only after all questions have finished inference.

#### Recommended Parameters

`--alternative-prompt`

Set to true to enable alternative template output mode.

`--max-new-tokens`

Set this to 1024 to ensure that the code is output completely.
