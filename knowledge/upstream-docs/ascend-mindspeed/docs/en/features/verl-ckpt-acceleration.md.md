---
id: doc-ascend-mindspeed-48dc2a257ca86b7061a5
title: Ascend/MindSpeed / docs/en/features/verl-ckpt-acceleration.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed
commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
path: docs/en/features/verl-ckpt-acceleration.md
raw_sha256: 5bd3a49d438c6b9d7c7abaae7c6d5a9a82de1e75dba3cfd123723e03a2355f7c
sources: []
generated_body_sha256: d593e385e4d94a7304d81e456e3cc64baa6932b46825bef69b14b91007f61ffc
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/verl-ckpt-acceleration.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/verl-ckpt-acceleration.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Checkpoint Read/Write Performance Optimization in Verl+Megatron Post-Training

## Background and Challenges

In the current post-training scenario using the verl + Megatron backend, saving and loading checkpoints takes a long time, which affects training efficiency.

## Solution

To address the above issue, the most time-consuming validation logic in native Megatron and Torch has been skipped. Users can control whether to skip this validation to accelerate checkpoint loading and saving through a parameter.

## Application Scenario

* Post-training with the verl + Megatron backend

## Usage

Add the following parameter to the training script to enable checkpoint load and save acceleration:
`+actor_rollout_ref.actor.megatron.override_transformer_config.ckpt_acceleration=True`

## Effects

The above approach significantly improves the efficiency of loading and saving checkpoints in the verl + Megatron backend. The measured results in a qwen3-30b-dapo scenario with 16 devices × 2 nodes are as follows:
![verl-ckpt-acceleration.png](../figures/verl-ckpt-acceleration_en.png)
