---
id: doc-nvidia-megatron-lm-ab5e7ed7c4e22124eb10
title: NVIDIA/Megatron-LM / examples/gpt3/README.md
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
path: examples/gpt3/README.md
raw_sha256: 6d73cfb30ca3c6e081dcf8893b1535af02bdf0f8484f82a90174f7cb4d4f9124
sources: []
generated_body_sha256: aa6a3119ecd17dbc7876ac281e6ab7aeaf7e1eea32bb66b1c6135fe31efe0252
source_state: current-scan
---

# NVIDIA/Megatron-LM / examples/gpt3/README.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/examples/gpt3/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# GPT3 MODEL

## Table of contents
- [1. Training Setup](#1-training-setup)
- [2. Configurations](#2-configurations)
- [3. Training Results](#3-training-results)

## 1. Training setup
<a id="markdown-training-setup" name="training-setup"></a>

To run the model using a docker container run it as follows
```
PYTORCH_IMAGE=nvcr.io/nvidia/pytorch:24.01-py3
CHECKPOINT_PATH="" #<Specify path>
TENSORBOARD_LOGS_PATH=""#<Specify path>
VOCAB_FILE="" #<Specify path to file>/gpt2-vocab.json
MERGE_FILE="" #<Specify path to file>/gpt2-merges.txt
DATA_PATH="" #<Specify path and file prefix>_text_document

docker run \
  --gpus=all \
  --ipc=host \
  --workdir /workspace/megatron-lm \
  -v /path/to/data:/path/to/data \
  -v /path/to/megatron-lm:/workspace/megatron-lm \
  megatron-lm nvcr.io/nvidia/pytorch:24.01-py3 \
  bash examples/gpt3/train_gpt3_175b_distributed.sh $CHECKPOINT_PATH $TENSORBOARD_LOGS_PATH $VOCAB_FILE $MERGE_FILE $DATA_PATH "

```
NOTE: Depending on the environment you are running it the above command might like slightly different.


## 2. Configurations
<a id="markdown-configurations" name="configurations"></a>
The example in this folder shows you how to run 175B model. There are other configs you could run as well

### 345M
```
       --num-layers 12 \
       --hidden-size 512 \
       --num-attention-heads 8 \
       --seq-length 1024 \
       --tensor-model-parallel-size 1 \
       --pipeline-model-parallel-size 1 \

```

### 857M
```
       --num-layers 24 \
       --hidden-size 1024 \
       --num-attention-heads 16 \
       --seq-length 2048 \
       --tensor-model-parallel-size 1 \
       --pipeline-model-parallel-size 1 \

```