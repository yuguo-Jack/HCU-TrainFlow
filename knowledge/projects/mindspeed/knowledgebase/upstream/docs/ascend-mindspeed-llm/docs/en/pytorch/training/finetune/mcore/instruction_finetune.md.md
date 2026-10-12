---
id: doc-ascend-mindspeed-llm-b285f2d06ce63c52ff3a
title: Ascend/MindSpeed-LLM / docs/en/pytorch/training/finetune/mcore/instruction_finetune.md
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
path: docs/en/pytorch/training/finetune/mcore/instruction_finetune.md
raw_sha256: 8dfd351773f0e8130e9259a5a668f555737a9fc0d6ecb02a7115bf62d711f0e8
sources: []
generated_body_sha256: 41cc6bdd13b18c6f14b1de48d1a12f3f26a0bbbf0396abd0cb2e8e0a73b9b91c
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/training/finetune/mcore/instruction_finetune.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/training/finetune/mcore/instruction_finetune.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Instruction Fine-Tuning for LLMs

## Use Cases

Although LLMs have strong language capabilities after pretraining, they often lack task awareness or interaction skills. Instruction fine-tuning makes models more flexible and better able to generalize across tasks by training them on multi-task, diverse datasets.
Instruction fine-tuning first collects datasets from multiple tasks and converts each task into instruction-form inputs. This helps LLMs improve generalization across diverse tasks. Specifically, it uses paired instruction and response samples in supervised learning. Therefore, the model learns to perform specific tasks. The basic principle of instruction fine-tuning is as follows.

![General pipeline of instruction tuning](../../../figures/instruction_finetune/General_pipeline_of_instruction_tuning.png)
*Source: [Instruction Tuning for Large Language Models: A Survey.](https://arxiv.org/pdf/2308.10792v5)*

Based on the data format used for instruction fine-tuning, there are three common use cases.

### [Single-Sample Fine-Tuning](./single_sample_finetune.md)

Each data record is an independent task sample that includes an instruction and a target response. It suits question answering, translation, and single-turn tasks.

- Example data format:

    ```json
    {
        "instruction": "Please translate the following sentence into English: I love natural language processing.",
        "response": "I love natural language processing."
    }
    ```

### [Multi-Sample Pack Fine-Tuning](./multi_sample_pack_finetune.md)

To improve training efficiency, multiple samples are concatenated and packed into one long sequence. This reduces padding and improves memory utilization.

- Original samples:

    ```json
    [
        {
            "instruction": "Please translate the following sentence into English: We are developing a new artificial intelligence assistant.",
            "response": "We are developing a new AI assistant."
        },
        {
            "instruction": "Please list three examples of renewable energy.",
            "response": "Solar, wind, and hydropower are three common examples of renewable energy."
        }
    ]
    ```

- Example of the packed input:

    ```text
    <bos> Instruction: Please translate the following sentence into English: We are developing a new artificial intelligence assistant.
    Response: We are developing a new AI assistant. <eos>
    Instruction: Please list three examples of renewable energy.
    Response: Solar, wind, and hydropower are three common examples of renewable energy. <eos>
    ```

### [MindSpeed LLM Multi-Turn Conversation Fine-Tuning](./multi_turn_conversation.md)

This format trains the model for continuous conversation and preserves context information. Each sample includes one or more turns of dialogue between the user and the model.

- Example data:

    ```json
    {
        "conversations": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hello, what can I help you with?"},
            {"role": "user", "content": "What is reinforcement learning?"},
            {"role": "assistant", "content": "Reinforcement learning is a method that lets an agent learn a policy through trial and error."}
        ]
    }
    ```

- Example of the constructed input:

    ```text
    <user>: Hello
    <assistant>: Hello, what can I help you with?
    <user>: What is reinforcement learning?
    <assistant>: Reinforcement learning is a method that lets an agent learn a policy through trial and error.
    ```

## Usage Constraints

- The fine-tuning script and data preprocessing method vary by sequence type. The following table uses Qwen3 instruction fine-tuning as an example.

    | Sequence length | Characteristics | Training script | Data Preprocessing Method |
    |--------|--------------------------------|----|---------------------------------------------------------|
    | Fixed-length sequence | Low performance. Not recommended. | Do not use the `--no-pad-to-seq-lengths` parameter during training. | Use the default preprocessing script, such as `data_convert_qwen3_instruction.sh`. |
    | Dynamic-length sequence | High sample throughput. | The training script must use the `--no-pad-to-seq-lengths` parameter. | Use the default preprocessing script, such as `data_convert_qwen3_instruction.sh`. |
    | Packed sequence | High token throughput. Supports parallelism for long sequences. | The training script must use the `--reset-attention-mask` parameter and must not enable `--no-pad-to-seq-lengths`. | Use the preprocessing script configured for pack mode. See [Multi-Sample Pack Fine-Tuning](./multi_sample_pack_finetune.md). |

    Choose the corresponding instruction fine-tuning training script and data preprocessing script based on your use case.

- The default template used by the current fine-tuning data preprocessing is aligned with Llama Factory 0.8.2. If you need alignment with later versions, set the `prompt-type` parameter to `qwen_lf` during the fine-tuning data preprocessing stage.
