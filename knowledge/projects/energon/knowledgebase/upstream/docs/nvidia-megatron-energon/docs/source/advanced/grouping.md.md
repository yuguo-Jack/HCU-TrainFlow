---
id: doc-nvidia-megatron-energon-d6158b39be7954f3aca8
title: NVIDIA/Megatron-Energon / docs/source/advanced/grouping.md
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
path: docs/source/advanced/grouping.md
raw_sha256: 2ffe13d8a1780727ca5af88956c0e1b67c40291c7211595f563a0ddc910ddb92
sources: []
generated_body_sha256: f3dccf11726f09aecb1167cd196f321be4a12e3a52613b4bbd35ff1be31731a3
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/advanced/grouping.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/docs/source/advanced/grouping.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# Grouping

Grouping allows for rule-based batching of samples into one batch on the fly.

Note how this is different from [packing](packing) which joins multiple samples into one (and is done before batching).
On the other hand, grouping is an alternative to standard batching.

## Example use cases

* Select samples to batch based on image resolution, so that only samples of the same size are in one batch
* Select blended samples based on their dataset origin, so that one batch does not mix different tasks or data types

## How to group

To use grouping, you need to define the method {py:meth}`batch_group_criterion <megatron.energon.TaskEncoder.batch_group_criterion>` in your custom task encoder.
This method gets a sample and returns a hashable value that will be used to cluster/group the samples
and it also returns the batch size for that group.

Samples with the same batch group criterion will be batched together. Once enough samples for one group
have been collected (reached the batch size for that group), they will be batched and pushed down the pipeline
to the next processing step.

Here's an example task encoder that batches samples based on their image aspect ratios:

```python
class GroupingTaskEncoder(DefaultTaskEncoder):
    def batch_group_criterion(self, sample: CaptioningSample) -> Tuple[Hashable, Optional[int]]:
        aspect_ratio = sample.image.shape[2] / sample.image.shape[1]

        # Bin aspect ratios into 3 groups
        if aspect_ratio < 0.8:
            return "portrait", 8
        elif aspect_ratio < 1.2:
            return "square", 8
        else:
            return "landscape", 8
```

In the example, the aspect ratio is sorted into one of three bins and a string is used as the grouping key.
The batch size used here is always 8.

Here is another example where each batch contains only images with the exact same size.
Note how the image shape itself is used as the grouping key.

```python
class GroupingTaskEncoder(DefaultTaskEncoder):
    def batch_group_criterion(self, sample: CaptioningSample) -> Tuple[Hashable, Optional[int]]:
        batch_size = 4 if sample.image.shape[1] < 512 else 2
        return sample.image.shape, batch_size
```

For images with a height of less than 512 pixels, the batch size will be 4, for larger images it's reduced to 2.


## Fixed global batch size

Instead of specifying the batch size for each group individually, you can also specify the batch size as usually when calling
`get_train_dataset`. The `batch_group_criterion` method should then return `None` for the batch_size.