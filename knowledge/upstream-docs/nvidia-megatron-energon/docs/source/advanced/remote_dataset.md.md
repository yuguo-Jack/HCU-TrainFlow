---
id: doc-nvidia-megatron-energon-ff056115191c323e5588
title: NVIDIA/Megatron-Energon / docs/source/advanced/remote_dataset.md
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
path: docs/source/advanced/remote_dataset.md
raw_sha256: efaea89c8be18b41863a7d01cd800f3599d88ce8359283b2a084fbd8df8aced1
sources: []
generated_body_sha256: 59ed26826ffe99209ef611c8c78227780ae8542662fada20c70880e12206700b
source_state: current-scan
---

# NVIDIA/Megatron-Energon / docs/source/advanced/remote_dataset.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/docs/source/advanced/remote_dataset.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--- Copyright (c) 2025, NVIDIA CORPORATION.
SPDX-License-Identifier: BSD-3-Clause -->

# Remote Dataset

Megatron Energon supports the use of remote datasets. Since version >5.2.0, Energon file access is based on [Multi Storage Client (MSC)](https://github.com/NVIDIA/multi-storage-client).
This means you can train or validate with your data right from any storage by simply swapping the dataset path for a so-called _MSC URL_.

## Prerequisites

For using a remote dataset, install energon with one or more of the extras:
* `s3`
* `aistore`
* `azure-storage-blob`
* `google-cloud-storage`
* `oci`

like this:
```sh
pip install megatron-energon[s3,oci]
```

Set up the msc config as described in [Multi Storage Client documentation](https://nvidia.github.io/multi-storage-client/).
You can also use the rclone config with msc, as was described prior to 5.2.0.

For fast data loading we recommend to activate MSC local caching:

```yaml
cache:
  size: 500G
  use_etag: true
  eviction_policy:
    policy: "fifo"
    refresh_interval: 3600
  cache_backend:
    cache_path: /tmp/msc_cache # prefer to use local NVMe, but Lustre path also works
```

And point MSC to the config with 

```sh
export MSC_CONFIG=/path/to/msc_config.yaml
```


## The URL syntax

The syntax is a simple as 

```
msc://CONFIG_NAME/PATH
```

For example:

```
msc://coolstore/mainbucket/datasets/somedata
```

You can use this URL instead of paths to datasets in

* Functions like `get_train_dataset`, `get_val_dataset`
* Inside [metadataset](../basic/metadataset) specifications
* As arguments to `energon prepare`, `energon prepare-media`, or `energon lint`. Note that those may be slow for remote locations.
* Or as a path to [`energon mount`](energon-mount) to locally inspect your remote dataset 😎

Example usage:

```python
ds = get_train_dataset(
    'msc://coolstore/mainbucket/datasets/somedata',
    batch_size=1,
    shuffle_buffer_size=100,
    max_samples_per_sequence=100,
)
```

## DSS URLs

In environments that provide datasets through the NVIDIA Dataset cache layout, Energon can also resolve DSS paths:

```
dss://DATASET_NAME@VERSION/path/inside/dataset
```

The dataset name and version are required. The path is resolved under `NVDATASET_CACHE_DIR`, so that environment variable must point to the local dataset cache root before loading DSS paths.