---
id: doc-nvidia-megatron-energon-a56832cac242d0b73d3c
title: NVIDIA/Megatron-Energon / docs/source/index.md
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
path: docs/source/index.md
raw_sha256: 324b0bf26b400bbcee8752e03af4230941269b05a0c97fa25f5cb610e962bd1f
sources: []
generated_body_sha256: a97a075ee8ccd8c7137a10e84adbf9122de0fd0bf47f9e9134573c8915868631
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/index.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/docs/source/index.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# Megatron-Energon Documentation

This is the documentation of Megatron's multi-modal data loader "Energon".

We recommend getting started in the [Introduction](intro/introduction) section, which explains what Energon is and how to install it.

Once installed, check out the **Basic Usage** section starting with [Quickstart](basic/quickstart) for some basic examples and tutorials.
Some underlying concepts, will be explained in the rest of that section.

For specific use cases and advanced usage, please read **Advanced Usage**.

In the end you will also find some documentation on how to interface with energon programmatically and how to contribute to the code base.

```{toctree}
---
caption: Introduction
maxdepth: 2
---

intro/introduction
intro/installation
```


```{toctree}
---
caption: Basic Usage
maxdepth: 2
---
basic/quickstart
basic/data_prep
basic/data_decoding
basic/basics_flow
basic/task_encoder
basic/metadataset
basic/save_restore
basic/glossary
```


```{toctree}
---
caption: Advanced Usage
maxdepth: 2
---
advanced/remote_dataset
advanced/crude_datasets
advanced/custom_sample_loader
advanced/repro_scaling
advanced/packing
advanced/grouping
advanced/joining_datasets
advanced/subsets
advanced/epochized_blending
advanced/custom_blending
advanced/parallelism
advanced/error_handling
advanced/data_prep_api
advanced/custom_dataset_factories
```


```{toctree}
---
caption: API
maxdepth: 2
---
api/modules
api/cli
```


```{toctree}
---
caption: Internals
maxdepth: 2
---
internals/contrib_guidelines
internals/code_structure
```

# Indices and tables

- [](genindex)
- [](modindex)