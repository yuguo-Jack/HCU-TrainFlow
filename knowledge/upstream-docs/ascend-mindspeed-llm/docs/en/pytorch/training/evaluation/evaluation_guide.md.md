---
id: doc-ascend-mindspeed-llm-f3d70499ab0164eb329a
title: Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_guide.md
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
path: docs/en/pytorch/training/evaluation/evaluation_guide.md
raw_sha256: 2b382515128fa371ff06f5b8fdae3083e00b824fb0b323f85ebd8e6ed5e27f0c
sources: []
generated_body_sha256: 59e336d72ad55c48fd085d81a6db58906662b5384268a2afcab55f9c9a080b2d
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/training/evaluation/evaluation_guide.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/training/evaluation/evaluation_guide.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Evaluation Guide

MindSpeed-LLM supports accurate evaluation of large models on public benchmark datasets.
For detailed statistics, see [models_evaluation.md](./models_evaluation.md).

## Environment Variables

Refer to [Model Script Environment Variables](../../features/mcore/environment_variable.md) for configuration of the environment variables used in the script.

## Introduction to Distributed LLM Evaluation

### 1. Benchmark Evaluation

The naming convention and startup method for MindSpeed-LLM benchmark evaluation scripts are as follows:

```shell
# Naming and startup: examples/mcore/model_name/evaluate_xxx.sh
# For reference: https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.0.0/examples/mcore/llama2/evaluate_llama2_7b_mmlu_ptd.sh
bash examples/mcore/llama2/evaluate_llama2_7b_mmlu_ptd.sh
```

```shell
# Modify the model parameter path and tokenizer path
TOKENIZER_PATH="./model_from_hf/llama-2-7b-hf/"  # Tokenizer path
CHECKPOINT="./model_weights/llama-2-7b-mcore"    # Checkpoint path
# Configure the task and dataset path
DATA_PATH="./mmlu/data/test/"
TASK="mmlu"  # Supports mmlu, ceval, agieval, bbh, boolq, human_eval

# Start the evaluation script
# For reference: https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.0.0/examples/mcore/llama2/evaluate_llama2_7b_mmlu_ptd.sh
bash examples/mcore/llama2/evaluate_llama2_7b_mmlu_ptd.sh
```

`--max-new-tokens`

This parameter controls the model generation length. The output length for multiple-choice questions is shorter than that for code tasks. This parameter has a significant impact on evaluation performance.

`--evaluation-batch-size`

You can enable multi-batch inference to improve evaluation performance.

`--broadcast`

When expert parallelism is enabled, you must set this flag for evaluation.

### 2. Instruction-Tuning Evaluation

Use the following naming convention and startup method for evaluation scripts with instruction-tuned weights:

```shell
# For reference: https://gitcode.com/Ascend/MindSpeed-LLM/blob/26.0.0/examples/mcore/llama2/evaluate_llama2_7b_full_mmlu_ptd.sh
bash examples/mcore/llama2/evaluate_llama2_7b_full_mmlu_ptd.sh
```

`--prompt-type`

Model chat template. Use it to select the corresponding chat template for evaluation.

`--hf-chat-template`

If the tokenizer of the model already has the `chat_template` attribute, you can add `--hf-chat-template` to use the built-in chat template of the model for evaluation.

`--eval-language`

Set this based on the language of the evaluation dataset. The default is `en`. If the evaluation dataset is Chinese, set this to `zh`.

### 3. LoRA Weight Evaluation

Use the following naming convention and startup method for evaluation scripts with LoRA weights:

```shell
# Start the evaluation script with LoRA weights loaded. Naming style and startup method:
bash examples/mcore/codellama/evaluate_codellama_34b_lora_ptd.sh
```
