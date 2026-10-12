---
id: doc-ascend-mindspeed-llm-10461e23fe2a6643dba4
title: Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_datasets/boolq_evaluation.md
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
path: docs/en/pytorch/training/evaluation/evaluation_datasets/boolq_evaluation.md
raw_sha256: 86a1287107620e4fc113e876e6d7c43d4a745d77b7eed6546811a17f09f516eb
sources: []
generated_body_sha256: 7f9f77ec5062a4053d1a95df1f6259a188f73d77fc05e4bad4c64eb959958dd7
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_datasets/boolq_evaluation.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/training/evaluation/evaluation_datasets/boolq_evaluation.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# BoolQ Evaluation

## Use Cases

### Problem Description

BoolQ is a boolean question-answering dataset created by Google Research. It has the following core features:

- Dataset size: It contains 15,942 triples of question, passage, and answer.

- Natural generation: The questions come from real search scenarios rather than being created manually.

- Complex context: The average passage length reaches 163 words, which requires deep semantic understanding.

- Domain coverage: It spans more than 650 topics and includes knowledge from multiple domains.

### Features

The BoolQ dataset includes three `.jsonl` files, and each line is a JSON dictionary in the following format:

```json
{
  "question": "is france the same timezone as the uk",
  "passage": "At the Liberation of France in the summer of 1944, Metropolitan France kept GMT+2 as it was the time then used by the Allies (British Double Summer Time). In the winter of 1944--1945, Metropolitan France switched to GMT+1, same as in the United Kingdom, and switched again to GMT+2 in April 1945 like its British ally. In September 1945, Metropolitan France returned to GMT+1 (pre-war summer time), which the British had already done in July 1945. Metropolitan France was officially scheduled to return to GMT+0 on November 18, 1945 (the British returned to GMT+0 on October 7, 1945), but the French government canceled the decision on November 5, 1945, and GMT+1 has since then remained the official time of Metropolitan France.",
  "answer": false,
  "title": "Time in France"
}
```

These files are:

- `train.jsonl`: 9,427 labeled training examples
- `dev.jsonl`: 3,270 labeled development examples
- `test.jsonl`: 3,245 unlabeled test examples

MindSpeed LLM evaluates the content in the `dev` question set.

## Usage

### 1. Direct Evaluation Mode (Default)

#### Impact

- MindSpeed LLM does not use any prompt template for BoolQ evaluation. Instead, it evaluates the target question directly and outputs the final answer. In other words, the model receives the question-passage pair directly, without any prompt template.

- The output layer computes the token probabilities of `Yes` and `No`. The final prediction is determined by comparing the probabilities. `P(Yes) > P(No)` maps to `True`, and all other cases map to `False`.

- Note that the accuracy may be 3 to 5 percentage points too high.

#### Recommended Parameters

`--max-new-tokens`

Set this to 3 or 4.

### 2. Alternative Template Output Mode

#### Impact

- Like direct evaluation mode, this mode does not use a prompt template. Unlike direct evaluation mode, this mode expects the model to output option `A` or `B`, which correspond to the `True` and `False` answers respectively. That is, `A` maps to `True`, and `B` maps to `False`.

#### Recommended Parameters

`--alternative-prompt`

Enable `Alternative Template Output Mode`.

`--max-new-tokens`

Set this to 3 or 4.

`--origin-postprocess`

If you enable this parameter, the model output is passed through answer mapping. For example, if the model does not output option `A` or `B` as expected and instead outputs `True`, this parameter maps `True` back to `A`.
