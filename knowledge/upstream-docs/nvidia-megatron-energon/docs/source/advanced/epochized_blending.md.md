---
id: doc-nvidia-megatron-energon-04ee1270600b2b14d2a2
title: NVIDIA/Megatron-Energon / docs/source/advanced/epochized_blending.md
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
path: docs/source/advanced/epochized_blending.md
raw_sha256: ea2ecd02d03226f7ba0195b508c27def1618f678179679103bd517dfc883b495
sources: []
generated_body_sha256: 62420414be2cf4a2dbbd1c560df5998728c5a6e2fa5e1b2e16b744b4a5f409ee
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/advanced/epochized_blending.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/docs/source/advanced/epochized_blending.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# Epochized Blending

As an alternative to blending with a weight for each dataset, blending can be made accurate and
iterating the dataset can follow epochs (i.e. interrupt iteration after an epoch) with this concept.

Here is an example `metadataset.yaml` config file that changes to epochized blending:

```yaml
__module__: megatron.energon
__class__: MetadatasetV2
splits:
  train:
    # Blend the following datasets, repeating coco 5 times, coyo-train 2 times and coyo-val 1 times
    blend_epochized:
      - repetitions: 5
        path: ./coco
        # ... Other parameters
      - repetitions: 2
        path: ./coyo
      - repetitions: 1
        path: ./coyo
        split_part: val
```

Now, the call to `get_train_dataset` requires the additional parameter `repeat=False` to interrupt iterating after one epoch:

```py
from megatron.energon import get_train_dataset, get_loader, WorkerConfig


loader = get_loader(get_train_dataset(
    'metadataset.yaml',
    batch_size=2,
    shuffle_buffer_size=100,
    max_samples_per_sequence=100,
    worker_config=WorkerConfig.default_worker_config(),
    repeat=False,
))

# This will now stop iterating after the datasets have been iterated (coco 5 times, coyo-train 2
# times and coyo-val 1 times). Of course, the data is still being shuffled between all those
# datasets.
for batch in loader:
    print(batch)

# This will iterate the second epoch
for batch in loader:
    print(batch)

```

If used as dataset for `get_val_dataset`, the `repetitions` are ignored.
The metadataset would also work without setting `repeat=False`, but then the shuffle buffer will shuffle samples across bounderies of epochs.