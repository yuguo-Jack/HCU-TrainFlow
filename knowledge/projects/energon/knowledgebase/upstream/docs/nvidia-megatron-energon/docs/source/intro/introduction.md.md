---
id: doc-nvidia-megatron-energon-9a263098dd6be72563d9
title: NVIDIA/Megatron-Energon / docs/source/intro/introduction.md
engine: energon
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: NVIDIA/Megatron-Energon
commit: d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b
path: docs/source/intro/introduction.md
raw_sha256: c25c50083d99d92b9ed928d5f8a77443d60ee842380772b21ae57b4a518def0b
sources: []
generated_body_sha256: 43f3eeefeca02fa9b785fd8f00a0fb8689b52aaba532810316be5a9241745b93
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/intro/introduction.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/docs/source/intro/introduction.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# General

Megatron-Energon is a data loader that works best with your [Megatron](https://github.com/NVIDIA/Megatron-LM) project.
However, you can use it in any of your PyTorch-based deep learning projects.

What can it offer compared to other data loaders?

The most important features are:

* Comes with a standardized WebDataset-based format on disk
* Optimized for high-speed multi-rank training
* Can handle very large datasets
* Can easily mix and blend multiple datasets
* Its state is savable and restorable (deterministic resumability)
* Handles various kinds of multi-modal data even in one training run

Energon also comes with a command line tool that you can use to prepare your datasets.