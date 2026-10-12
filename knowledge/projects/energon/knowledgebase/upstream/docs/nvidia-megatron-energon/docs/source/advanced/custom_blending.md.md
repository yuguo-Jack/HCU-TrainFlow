---
id: doc-nvidia-megatron-energon-3c4ebc00ac6e710f2f38
title: NVIDIA/Megatron-Energon / docs/source/advanced/custom_blending.md
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
path: docs/source/advanced/custom_blending.md
raw_sha256: d04c22f00fbc9693ac0a01d38486df7d988476e2cea54bbea7f514d4e55d9646
sources: []
generated_body_sha256: 0a23e60bb5f6606a578f3fcc82e06bf55cf106fd19d94321b76aa6202915216d
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/advanced/custom_blending.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/docs/source/advanced/custom_blending.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# Customized Blending

In your Task Encoder you could customize the blend of datasets by overriding the `build_train_datasets` method as shown below.


```{warning}
This interface is not stable and may be subject of changes quite often for new features we add. So if you change
how the datasets are plugged together, consider that this may have to be adapted to future changes.
```

```py

class CaptioningTaskEncoder(
    DefaultTaskEncoder[CaptioningSample, CaptioningSample, CaptioningRawBatch, CaptioningBatch]
):
    ...
    
    def build_train_datasets(
        self,
        *,
        datasets: List[Tuple[BaseCoreDatasetFactory[T_sample], float]],
        worker_config: WorkerConfig,
        batch_size: Optional[int],
        batch_drop_last: bool = False,
        packing_buffer_size: Optional[int] = None,
        virtual_epoch_length: int = 0,
        shuffle_buffer_size: Optional[int] = None,
    ) -> SavableDataset[T_batch]:
        # The default implementation uses MixDataset, which mixes the datasets according to their weights
        # This could be customized, e.g. to batch the datasets first (i.e. each batch only contains data from a single datset)
        # and then blend, which would yield the same distribution.
        dataset = BlendDataset(
            *datasets,
            worker_config=worker_config,
        )
        # Build batches from blended samples
        dataset = self.build_batch(
            dataset,
            batch_size=batch_size,
            batch_drop_last=batch_drop_last,
            worker_config=worker_config,
        )
        # Optionally epochize
        if virtual_epoch_length > 0:
            dataset = EpochizeDataset(
                dataset,
                length=virtual_epoch_length,
                worker_config=worker_config,
            )
        return dataset

```