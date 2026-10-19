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
commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
path: docs/source/index.md
raw_sha256: 71ac76ff2b4cc03c5bebd08ba27af002a08763c70c24983f1eb3416ea75d5434
sources: []
generated_body_sha256: 5cbf9afd904f1c6efa3a9fd1cb325524a62aec47b696bd085fc56c24b9299db6
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/index.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/docs/source/index.md)

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
basic/recipe
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
internals/code_structure
internals/dataset_formats
internals/savability
internals/recipe_checkpoint
internals/packing_blending
internals/epath_storage
internals/compatibility
internals/contrib_guidelines
```

# Indices and tables

- [](genindex)
- [](modindex)
