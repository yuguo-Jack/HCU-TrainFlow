---
id: doc-ascend-mindspeed-llm-ff50c863a0666b029692
title: Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_datasets/ceval_evaluation.md
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
path: docs/en/pytorch/training/evaluation/evaluation_datasets/ceval_evaluation.md
raw_sha256: fd3d7d114695884e59d9068ed26fa7bf5570ebf79e65b824ae562643a08ee7ec
sources: []
generated_body_sha256: f7b332a32ba20a976cf5384bebb0bfbd3888ee886591777e30a40b011203c792
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_datasets/ceval_evaluation.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/training/evaluation/evaluation_datasets/ceval_evaluation.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# CEval Evaluation

## Use Cases

### Problem Description

CEval is a Chinese, multidisciplinary benchmark dataset jointly built by Chinese universities and research institutions. It has the following core features:

- **Dataset size**: It contains 13,468 multiple-choice questions across 52 subjects.

- **Academic authority**: The questions come from Chinese higher education exams and professional qualification certifications. Therefore, they are representative of the subject areas.

- **Knowledge depth**: Answering the questions requires both subject knowledge and logical reasoning ability.

- **Subject coverage**: It covers four major categories, including humanities, social sciences, STEM, and interdisciplinary subjects.

MindSpeed LLM evaluates the content in the CEval question set.

## Usage

### 1. Direct Evaluation Mode (Default)

#### Usage Instructions

This mode reads the external CEval [template file](../../../../../../mindspeed_llm/tasks/evaluation/eval_impl/fewshot_template/ceval_5shot_template.json) and uses it as the evaluation template. It concatenates the template with the question that the model needs to answer, then feeds the result to the model for direct evaluation.

In this mode, the first output of the model is taken as the answer.

The advantage of this mode is that it is direct and fast, and it can directly evaluate the pretrained weights of the model.

#### Recommended Parameters

`--max-new-tokens`

Set this to 2 to ensure that a single option character is generated.

### 2. Fine-Tuned Template Evaluation Mode

#### Usage Instructions

This mode reads the `_dev.csv` files for the corresponding questions in the sibling `dev` folder under the `DATA_PATH` path in your startup script. It uses those files as template questions and processes them before feeding them to the model.

Unlike direct evaluation mode, this mode shuffles the template questions in the `dev` file based on the seed. After they are concatenated with the questions the model needs to answer and processed through the chat template, the resulting dialogue dictionary is fed into the model for evaluation.

The advantage of this mode is that evaluation is faster, and it is suitable for evaluating fine-tuned model weights.

#### Recommended Parameters

`--max-new-tokens`

Set this to 2 to ensure that a single option character is generated.

`--prompt-type`

This parameter specifies the model template type. It should match the `--prompt-type` parameter configured when you fine-tune the model in the MindSpeed LLM repository.

### 3. Alternative Template Output Mode

#### Usage Instructions

Like fine-tuned template evaluation mode, this mode also uses the `_dev.csv` files for the corresponding questions in the sibling `dev` folder under the `DATA_PATH` path in your evaluation script as template questions.

Unlike the other evaluation modes, this mode does not shuffle the template questions. After the template questions are concatenated with the questions the model needs to answer, the dialogue dictionary is not processed. Instead, the result is fed directly to the model to obtain the forward output.

The advantage of this mode is that it uses the same evaluation template used by leading industry evaluation solutions, and it can achieve better evaluation scores.

#### Recommended Parameters

`--max-new-tokens`

Set this to 2 to ensure that a single option character is generated.

`--alternative-prompt`

Set to true to enable alternative template output mode.
