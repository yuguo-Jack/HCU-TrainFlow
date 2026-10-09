---
id: doc-nvidia-megatron-lm-b6ccc3069d398dc89365
title: NVIDIA/Megatron-LM / megatron/core/distributed/README.md
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
path: megatron/core/distributed/README.md
raw_sha256: bc5d1c22c609bc2d174c5d97e143e65ef8d5a989e02016cbb0bbd737fc9aeff4
sources: []
generated_body_sha256: a15fa9228da6a9f5670b50756e0071440a36a546347ece3d94cc9d19aa79c3fa
source_state: current-scan
---

# NVIDIA/Megatron-LM / megatron/core/distributed/README.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/megatron/core/distributed/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Distributed Data Parallelism

This module contains algorithms, data structures, and utilities used for different types of distributed data parallelism, such as DDP and FSDP.

## Distributed Data Parallelism

This is the default data parallelism used with all parallelism topologies in Megatron-LM.

## Megatron-FSDP

To use Megatron-FSDP in Megatron-LM, enable the following arguments:

```
--use-megatron-fsdp
--ckpt-format fsdp_dtensor
--init-model-with-meta-device
```

## FSDP2

To use FSDP2 in Megatron-LM, enable the following arguments:

```
--use-torch-fsdp2
--no-gradient-accumulation-fusion
--ckpt-format torch_dist
```