---
id: doc-nvidia-megatron-energon-9f6b46dd28af985ad0e7
title: NVIDIA/Megatron-Energon / docs/source/basic/basics_flow.md
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
path: docs/source/basic/basics_flow.md
raw_sha256: 43aca3e3cd23a033770698eaefca8a7dc4d2ef168eace9f95254cee87d1e997e
sources: []
generated_body_sha256: bcba854b5b4d9a48ae69111f77e0e816e88d83e06a75fdd9efdba356fd186286
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/basic/basics_flow.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/docs/source/basic/basics_flow.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# Data Flow

![energon data flow](../images/data_flow.png)

The steps of how the data flows through those task encoder methods is explained in [](task_encoder).

(flavors_general)=
## Dataset Flavors

The datasets are organized in "flavors", i.e. each modality returned by the dataset is a "flavor".
A modality can for example be a {py:class}`CaptioningSample <megatron.energon.CaptioningSample>` or an 
{py:class}`VQASample <megatron.energon.VQASample>`. The dataset class combines the source data format
and the iterated sample format. For example, the {py:class}`CaptioningWebdataset <megatron.energon.CaptioningWebdataset>` 
combines the webdataset loader with the {py:class}`CaptioningSample <megatron.energon.CaptioningSample>`.

For all types, see [](sect-sample-types)