---
id: doc-baidu-baige-loongforge-c8ceeb9c507a00cb211c
title: baidu-baige/LoongForge / docs/source/embodied_tutorial/quick_start_pi05.md
engine: loongforge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: baidu-baige/LoongForge
commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
path: docs/source/embodied_tutorial/quick_start_pi05.md
raw_sha256: 17ce839486b5b7fb0613d4c3186aff7cb2f8cdbc122950b480f5e336b556a882
sources: []
generated_body_sha256: 4406f1c067963d4098852fb426c6095d0d9669197f65b3c4bc4aaabfe764eb44
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source/embodied_tutorial/quick_start_pi05.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source/embodied_tutorial/quick_start_pi05.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Quick Start: Pi0.5 Training

This guide walks you through launching **Pi0.5 (π₀.₅)** fine-tuning and offline evaluation in the LoongForge framework.

## 0. Resource Preparation
### 0.1 Model Weights
The Pi0.5 main weights are specified by `CHECKPOINT_PATH` and loaded via `--pretrained-checkpoint`. The original HuggingFace safetensors format is supported:

```bash
hf download lerobot/pi05_base --local-dir /workspace/huggingface.co/lerobot/pi05_base
```
### 0.2 Tokenizer / Processor
Pi0.5 requires a tokenizer, specified by `TOKENIZER_PATH` and loaded via `--tokenizer-path`:

```bash
huggingface-cli download google/paligemma-3b-pt-224 --local-dir /workspace/huggingface.co/google/paligemma-3b-pt-224
```


### 0.3 Dataset
The script uses LIBERO data in LeRobot v3.0 format by default. If the dataset comes from a HuggingFace Dataset, download it to the same directory:

```bash
hf download lerobot/libero_10 --repo-type dataset --local-dir /workspace/libero_10
```
## 1. Data Configuration
For the standard LeRobot v3.0 format, no extra offline preprocessing is required. The GR00T sample transform and batch collator run online during training.

Default data configuration:

```yaml
data:
  image_size: 224
  image_normalize_mode: identity
```
## 2. Launch Training
First, set the paths:

```bash
cd /workspace/LoongForge

export LOONGFORGE_PATH=/workspace/LoongForge
export TOKENIZER_PATH=/workspace/huggingface.co/google/paligemma-3b-pt-224

export CHECKPOINT_PATH=/workspace/workspace/huggingface.co/lerobot/pi05_base

export DATA_PATH=/workspace/libero_10
export OUTPUT_DIR=/workspace/outputs/pi05
export TENSORBOARD_PATH=/workspace/tensorboard-log/pi05
```
### 2.1 Script


The DDP script already enables the main performance optimizations:

**DDP:**

```bash
bash examples/embodied/pi05/run_pi05_ddp_finetune.sh
```
**DDP + ZeRO-1:**

```bash
bash examples/embodied/pi05/run_pi05_ddp_zero1_finetune.sh
```
**FSDP:**

```bash
bash examples/embodied/pi05/run_pi05_fsdp_finetune.sh
```
### 2.2 Correctness Verification
To ensure training accuracy is not affected by the optimizations, we ran a step-by-step action loss comparison between LoongForge's Pi0.5 implementation and the official one under identical data, weights, and training configuration. The results show that LoongForge's performance optimizations are lossless with respect to training accuracy:
![alt text](../../assets/images/precision/pi05.png)




## 3. Evaluation
 LoongForge provides a standalone benchmark evaluation module (LIBERO / CALVIN / SimplerEnv / RoboTwin / ManiSkill). The benchmark client and policy server are decoupled via WebSocket.

### 3.1 Quick Run LIBERO
1. Edit the evaluation YAML

(Example: `examples/embodied/pi05/eval/configs/libero/smoke_steps10.yaml`), and fill in:

    * `server.ckpt_path`: the checkpoint from training (a directory containing `model.safetensors` or the weight file)
    * `server.dataset_statistics_path`: dataset statistics (for action denormalization; Pi0.5 default is q99)
    * `server.tokenizer_path`: PaliGemma tokenizer

2. Launch:

```bash
cd $LOONGFORGE_PATH
# Uses smoke_steps10.yaml by default; can be overridden via CONFIG
CONFIG=examples/embodied/pi05/eval/configs/libero/smoke_steps10.yaml \
  bash examples/embodied/pi05/eval/run_libero_eval.sh
```
