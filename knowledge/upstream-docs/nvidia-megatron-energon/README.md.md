---
id: doc-nvidia-megatron-energon-d82ab49f91a6ba1662d9
title: NVIDIA/Megatron-Energon / README.md
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
path: README.md
raw_sha256: 6309cd798e11e2f2b47d770eb0d3ebc24a34c1dc474c4ab8d86c7e923bb50b63
sources: []
generated_body_sha256: 3bd9084f865c52dc933933b86f6eea41ec9bfa5607002f07d991a1d7a6ae029c
source_state: current-scan
---

# NVIDIA/Megatron-Energon / README.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->
<a name="top"></a>

<div align="center">
  <h4 align="center">Megatron's multi-modal data loader</h4>
  <h2 align="center">Megatron Energon</h2>
  <p align="center">
    <a href="https://github.com/NVIDIA/Megatron-Energon/actions/workflows/tests.yml"><img src="https://github.com/NVIDIA/Megatron-Energon/actions/workflows/tests.yml/badge.svg" alt="Tests"></a> <a href="https://nvidia.github.io/Megatron-Energon/"><img src="https://github.com/NVIDIA/Megatron-Energon/actions/workflows/documentation.yml/badge.svg" alt="Documentation"></a>
    <br />
    <a href="https://github.com/NVIDIA/Megatron-Energon/issues">Report Bug</a>
    ·
    <a href="https://github.com/NVIDIA/Megatron-Energon/issues">Request Feature</a>
  </p>
</div>

<br />

 _**DISCLAIMER**: This package contains research code. APIs may change._

# What is this?

**Megatron Energon** is the multi-modal data loader of [Megatron](https://github.com/NVIDIA/Megatron-LM) (you can also use it independently).

It's best at

- loading large training data to train large multi-modal models
- blending many different datasets together
- distributing the work across many nodes and processes of a cluster
- ensuring reproducibility and resumability
- adapting easily to various types of data samples and processing

Try using it together with [Megatron](https://github.com/NVIDIA/Megatron-LM) Core.

# Quickstart
**Megatron Energon** is a pip-installable python package that offers
- dataset-related classes that you can import in your project
- a command line utility for data preprocessing and conversion

This document is just a quick start. Please also check out the [documentation](https://nvidia.github.io/Megatron-Energon/).

## Installation

To install the latest stable version:
```shell
pip install megatron-energon
```

Or to install the current development version:
```shell
pip install git+https://github.com/NVIDIA/Megatron-Energon.git
```

**NOTE**: We encourage you to install the package (and not just import a local copy). This will ensure you have all the needed dependencies and that you can use the command line tool.

For more details on installing this package, see [here](https://nvidia.github.io/Megatron-Energon/intro/installation.html).

## Usage of command line tool

After installation, the command `energon` will be available.

Here are some examples for things you can do:

| Command | Description  |
|---|---|
| `energon prepare DATASET_ROOT` | Take an existing WebDataset and add the required yaml files to turn it into an energon-compatible dataset |
| `energon lint DATASET_ROOT` | Verify that the dataset complies with the energon dataset format and that all samples are loadable |


## Usage of the library

To get started, pick a [WebDataset](https://github.com/webdataset/webdataset)-compliant dataset and run `energon prepare DATASET_ROOT` on it, to run the interactive assistant and create the `.nv-meta` folder. As an alternative to WebDataset, Energon also supports the JSONL format, see [here](https://nvidia.github.io/Megatron-Energon/basic/data_prep.html).

Once done, try to load it from your Python program:

```python
from megatron.energon import get_train_dataset, get_loader, WorkerConfig


simple_worker_config = WorkerConfig(rank=0, world_size=1, num_workers=2)


train_ds = get_train_dataset(
    '/my/dataset/path',
    batch_size=2,
    shuffle_buffer_size=None,
    max_samples_per_sequence=None,
    worker_config=simple_worker_config,
)

train_loader = get_loader(train_ds)

for batch in train_loader:
    # Do something with batch
    # Infer, gradient step, ...
    pass
```

For more details, read the [documentation](https://nvidia.github.io/Megatron-Energon/).