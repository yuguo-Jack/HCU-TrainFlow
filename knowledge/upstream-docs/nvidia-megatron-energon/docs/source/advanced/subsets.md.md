---
id: doc-nvidia-megatron-energon-b6fecacdd7631aac8458
title: NVIDIA/Megatron-Energon / docs/source/advanced/subsets.md
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
path: docs/source/advanced/subsets.md
raw_sha256: 210ea2f5c58241412096d9c745ee3ba8a50c6db210ebd961954c633115a507f6
sources: []
generated_body_sha256: da63d729a142fc8b84fb32da0739b6bf2f82da7e5c012fa0269183c4aa27b348
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/advanced/subsets.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/docs/source/advanced/subsets.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# Dataset Subsets

Dataset subsets allow restricting a dataset (or parts of a metadataset hierarchy) to a specific portion of the available samples.
This is useful for rapid prototyping, ablation studies, different training stages, or constructing disjoint train/validation/test splits that differ from the original dataset configuration.

A subset is defined by a two-element `range` list consisting of `[start, end]` (where `start` is inclusive, `end` exclusive).
Each element can be either

* a **percentage** string (e.g. `"0%"`, `"12.5%"`, `"100%"`) – interpreted relative to each inner
  dataset size, or
* an **absolute** integer – interpreted as a sample index. Absolute indices are only allowed for
  *leaf* datasets (`path` to a prepared dataset containing `.nv-meta`).

## Basic example

The snippet below keeps the first 80 % of *COYO* `train` split (as defined in the `split.yaml`) for training while
evaluating on the remaining 20 % of the `train` split. Note how the `subset` key is placed directly next to the corresponding `path`.

```yaml
__module__: megatron.energon
__class__: MetadatasetV2
splits:
  train:
    path: ./coyo
    subset: {range: [0%, 80%]}
  val:
    path: ./coyo
    split: train
    subset: {range: [80%, 100%]}
```

## Nested subsets and merging rules

Subsets can appear at any level that ultimately yields samples
(direct `path` reference to a prepared dataset containing `.nv-meta`, `join`, `blend`, `blend_epochized`).
When multiple subsets are nested, the *inner* subset is applied first, then the portion selected by the *outer* subset is applied *within* the already selected range.
For percentages the ranges are composed multiplicatively.

Example: the outer subset `[0%, 50%]` followed by an inner subset `[25%, 75%]` results in the final
range `[25%, 50%]` of the original dataset.

Absolute indices short-circuit merging: they can **only** be specified at the leaf level and must
not be combined with another absolute range farther up the hierarchy.

## Absolute ranges

Absolute indices are handy when exact sample counts are required.

## Advanced examples

The following configuration combines the absolute ranges with the nested rules. The inner subset takes
the first **1000** samples from *COCO* train split and mixes them with the full *COYO* train split using
weight-based blending. The outer nesting then reduces the inner ranges to the first 50%, thus only taking
the first **500** samples of *COCO*, mixed with the first **50%** of the *COYO* dataset effectively.

```yaml
__module__: megatron.energon
__class__: MetadatasetV2
splits:
  train:
    # The subset is applied to each blended dataset separately.
    # I.e. for the first, the sample range is [0, 500], for the second the range is [0%, 50%]
    subset: {range: [0%, 50%]}
    blend:
      - weight: 1.0
        path: ./coco
        subset:
          # Take exactly 1000 samples (indices 0-999)
          range: [0, 1000]
      - weight: 1.0
        path: ./coyo
```

Absolute ranges can also be specified to run up to the end of the dataset using the `end` keyword:

```yaml
__module__: megatron.energon
__class__: MetadatasetV2
splits:
  train:
    path: ./coyo
    subset: {range: [1422, end]}
```

## Python usage

No API changes are required on the Python side – subsets are fully specified in the YAML. Simply
load the dataset with the regular helpers.