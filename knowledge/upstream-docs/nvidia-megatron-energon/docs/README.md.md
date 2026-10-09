---
id: doc-nvidia-megatron-energon-07b0937cb45ba711b294
title: NVIDIA/Megatron-Energon / docs/README.md
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
path: docs/README.md
raw_sha256: 585d56fc283a688836fff84bc495c2908634811fc9cfb7cdf647c7aecff523d0
sources: []
generated_body_sha256: 209bf627beba557e565f79a02a15a8f79db8fcb1de2ff16f1b1eef9f0bfb643d
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/README.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/docs/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# Building the documentation

To build the documentation, you need sphinx and additional packages:

- nvidia-sphinx-theme
- sphinx    
- sphinxcontrib-napoleon
- myst-parser

You can install these like

`pip install nvidia-sphinx-theme sphinx sphinxcontrib-napoleon myst-parser sphinx-click`

Use `make html` to build it.

Or use PyCharm by adding a configuration:

    `Run -> Edit Configurations -> Add new Configuration -> Python docs -> Sphinx task`

Use the `src/docs/source` folder as input folder and the `src/docs/build` as output.