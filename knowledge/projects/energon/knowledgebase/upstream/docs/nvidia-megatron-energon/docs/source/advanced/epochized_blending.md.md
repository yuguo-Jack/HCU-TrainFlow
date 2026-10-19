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
commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
path: docs/source/advanced/epochized_blending.md
raw_sha256: da6e3e52f5daf6a905eb8ed92a0a8a0b7616d04f3554a3427761210bb9fb6f7e
sources: []
generated_body_sha256: 5743aca0208ccacf6e3894c06cb09cd0e101cb121d1b027cfd02cb5634908116
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/advanced/epochized_blending.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/docs/source/advanced/epochized_blending.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# Epochized Blending

As an alternative to blending with a weight for each dataset, blending can be made accurate and
iterating the dataset can follow epochs (i.e. interrupt iteration after an epoch) with this concept.

Here is an example `recipe.yaml` config file that changes to epochized blending:

```yaml
__module__: megatron.energon
__class__: Recipe
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
    'recipe.yaml',
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
The recipe would also work without setting `repeat=False`, but then the shuffle buffer will shuffle samples across bounderies of epochs.
