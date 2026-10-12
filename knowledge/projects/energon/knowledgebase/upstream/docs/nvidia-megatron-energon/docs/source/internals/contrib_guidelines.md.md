---
id: doc-nvidia-megatron-energon-8c63b515344199ee743a
title: NVIDIA/Megatron-Energon / docs/source/internals/contrib_guidelines.md
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
path: docs/source/internals/contrib_guidelines.md
raw_sha256: 156c8885e914340b5a15400951cce40ef33b2f44ea4c3d892bf2af6b3fc92cb0
sources: []
generated_body_sha256: 5753081422c284cf5d41da07f2c6037a1e2b22ed75277f53684f6922c6bf2ccc
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/internals/contrib_guidelines.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/docs/source/internals/contrib_guidelines.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# Contribution Guidelines

If you want to contribute to this repository please adhere to the following guidelines

- Always use [black](https://pypi.org/project/black/) and [isort](https://pycqa.github.io/isort/) to format your code before committing
- Check that all license headers are present using `python3 scripts/license_headers.py --fix .`
- Python `@dataclass` and `NamedTuple` are preferred over dictionaries, which don't allow for IDE
  auto-completion and type checking
- User-exposed classes and methods should be documented in Google-style docstrings that are parsed by sphinx
  and end up in this documentation
- Breaking changes should be marked in the message of pull requests:
  - `CHECKPOINT BREAKING CHANGE`: When the save/restore structure changed incompatibly (check test `test_metadataset:TestDataset.test_save_restore_state_train`)
  - `ITERATION ORDER BREAKING CHANGE`: When the order of iterating samples changed, i.e. experiments would not be exactly reproducible (check tests `test_dataset:TestDataset.test_current_batch_index_generator`, `test_dataset:TestDataset.test_current_batch_index`, maybe more)
  - `API BREAKING CHANGE`: When the external programming api changed incompatibly
  - `DATASET CONFIG BREAKING CHANGE`: When the dataset config (`.nv-meta` folder) changed incompatibly
  - `METADATASET CONFIG BREAKING CHANGE`: When the metadataset config changed
- In a release, all breaking changes except checkpoint lead to a new major version.