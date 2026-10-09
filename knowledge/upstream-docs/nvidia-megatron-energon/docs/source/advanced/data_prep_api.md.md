---
id: doc-nvidia-megatron-energon-82eb32e67f84014dd574
title: NVIDIA/Megatron-Energon / docs/source/advanced/data_prep_api.md
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
path: docs/source/advanced/data_prep_api.md
raw_sha256: 2ccccab10575f303995b19e709fbd9b2a20cb3bb149051beea1d9a6c53c22f96
sources: []
generated_body_sha256: 7105a419e9318341125c4bd2f989cba508f187e25a845268974c0b0436bd566b
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/advanced/data_prep_api.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/docs/source/advanced/data_prep_api.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# Programmatic Data Preparation

Below, we provide an example function that shows how to prepare a dataset programmatically.
The example uses WebDataset tar shards.

```python
from megatron.energon.flavors import BaseWebdatasetFactory

def prepare_one_dataset(path: Path, num_workers: int, template_dir: Path):

    if (path / ".nv-meta" / "dataset.yaml").exists():
        print(f"Dataset {path} already prepared. Skipping.")
        return

    # Fixed settings
    tar_index_only = False
    split_parts_ratio = [("train", 1), ("val", 0), ("test", 0)]
    split_parts_patterns = None
    
    # Get all tar files
    all_tars = list(path.glob("**/*.tar")) + list(path.glob("**/*.tgz"))
    all_tars = [str(p.relative_to(path)) for p in sorted(all_tars)]

    if len(all_tars) == 0:
        print("Did not find any tar files. Exiting.")
        return

    print(f"Found {len(all_tars)} tar files in total. The first and last ones are:")
    print(f"- {all_tars[0]}")
    print(f"- {all_tars[-1]}")

    def progress_fn(els, length=None):
        with click.progressbar(
            els,
            label="Indexing shards",
            show_pos=True,
            length=length,
        ) as bar:
            for el in bar:
                yield el

    found_types, duplicates = BaseWebdatasetFactory.prepare_dataset(
        path,
        all_tars,
        split_parts_ratio=split_parts_ratio,
        split_parts_patterns=split_parts_patterns,
        progress_fn=progress_fn,
        tar_index_only=tar_index_only,
        shuffle_seed=None,
        workers=num_workers,
    )

    # Copy sample loader and dataset.yaml templates
    for file in template_dir.glob("*"):
        shutil.copy(file, path / ".nv-meta" / file.name)
```

For non-tar shard lists, use the generic manifest writer
`megatron.energon.flavors.common.manifest.write.write_manifest_dataset_metadata`
with `ShardInfo` entries for each shard and a `dataset_definition` that points to the corresponding factory.
Single-file datasets such as `.jsonl` are detected directly and do not require a manifest.

Example usage:

First, create a template directory with the `dataset.yaml` file, and optionally the `sample_loader.py` file.
Let's call it `template_dir`.

Then, run the script:

```python
if __name__ == "__main__":
    prepare_one_dataset(Path("/path/to/dataset"), 16, Path("/path/to/template_dir"))
```

## Custom Dataset Formats

Preparation and runtime path detection are separate extension points. This page
covers writing prepared metadata; registering a custom or specialized runtime
dataset factory belongs in [Custom Dataset Factories](custom_dataset_factories.md).
That page also explains provider priority, import timing, reader contracts, and
the tests needed for a new format.