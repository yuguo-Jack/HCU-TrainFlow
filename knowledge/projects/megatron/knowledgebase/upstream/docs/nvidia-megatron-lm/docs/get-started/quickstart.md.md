---
id: doc-nvidia-megatron-lm-e13e93ebe9344f57266c
title: NVIDIA/Megatron-LM / docs/get-started/quickstart.md
engine: megatron
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: NVIDIA/Megatron-LM
commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
path: docs/get-started/quickstart.md
raw_sha256: 12facd93f82e65b9ca752faeff7496de268832713ea3746dabc00e3c148db9dc
sources: []
generated_body_sha256: daccf7d512bb23d6317a5f2cbf607b685f93d451aa665399b640e70370bf424f
source_state: current-scan
---

# NVIDIA/Megatron-LM / docs/get-started/quickstart.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/docs/get-started/quickstart.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!---
   Copyright (c) 2022-2026, NVIDIA CORPORATION. All rights reserved.
   NVIDIA CORPORATION and its licensors retain all intellectual property
   and proprietary rights in and to this software, related documentation
   and any modifications thereto. Any use, reproduction, disclosure or
   distribution of this software and related documentation without an express
   license agreement from NVIDIA CORPORATION is strictly prohibited.
-->

# Your First Training Run

This guide walks you through two training examples and then covers data preparation for your own datasets. You start with a minimal distributed loop to validate your environment, then run a full LLaMA-3 training job. Make sure you have completed [installation](install.md) before proceeding.

## Minimal Training Example

Start with the simplest possible setup, a distributed training loop using mock data on two GPUs. This verifies that your environment is configured correctly before moving to real models.

```bash
torchrun --nproc_per_node=2 examples/run_simple_mcore_train_loop.py
```

## LLaMA-3 Training Example

With the environment validated, run a production-scale example. The following script trains a LLaMA-3 8B model with FP8 mixed precision on eight GPUs using mock data, demonstrating tensor parallelism and optimized kernels.

```bash
./examples/llama/train_llama3_8b_h100_fp8.sh
```

## Data Preparation

To train on your own data, Megatron expects preprocessed binary files (`.bin` and `.idx`).

### 1. Prepare a JSONL File

Each line should contain a `text` field:

```json
{"text": "Your training text here..."}
{"text": "Another training sample..."}
```

### 2. Preprocess the Data

Run the preprocessing script to tokenize and convert your data into binary format:

```bash
python tools/preprocess_data.py \
    --input data.jsonl \
    --output-prefix processed_data \
    --tokenizer-type HuggingFaceTokenizer \
    --tokenizer-model /path/to/tokenizer.model \
    --workers 8 \
    --append-eod
```

### Key Arguments

- `--input`: Path to input JSON/JSONL file
- `--output-prefix`: Prefix for output binary files (`.bin` and `.idx`)
- `--tokenizer-type`: Tokenizer type (`HuggingFaceTokenizer`, `GPT2BPETokenizer`, and so on)
- `--tokenizer-model`: Path to tokenizer model file
- `--workers`: Number of parallel workers for processing
- `--append-eod`: Add end-of-document token

## Next Steps

- Explore [Parallelism Strategies](../user-guide/parallelism-guide.md) to scale your training
- Learn about [Data Preparation](../user-guide/data-preparation.md) best practices
- Explore [Advanced Features](../user-guide/features/index.md) for FP8 training, context parallelism, and more