---
id: doc-pytorch-torchtitan-f80b253d59f840378c4e
title: pytorch/torchtitan / docs/benchmarks/llama3-8b_h200_202506_trainy-whitefiber.md
engine: torchtitan
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: pytorch/torchtitan
commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
path: docs/benchmarks/llama3-8b_h200_202506_trainy-whitefiber.md
raw_sha256: ddc7d66b95a88b834da93103de19e24a056dc4af9f6e615aa8280b1c709fe726
sources: []
generated_body_sha256: c3b6165a7f6acdf23eb4401c0666d5155d9ca3d7debfbf3aa368754a6192d2f9
source_state: current-scan
---

# pytorch/torchtitan / docs/benchmarks/llama3-8b_h200_202506_trainy-whitefiber.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/docs/benchmarks/llama3-8b_h200_202506_trainy-whitefiber.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

This was performed by Trainy team on WhiteFiber in June 2025, to get a baseline of performance
of the Trainy platform on H200s platform over multiple hosts.

### Models

Llama 3.1 8B

### Hardware

Each host has

- 8 NVIDIA H200 GPUs connected via NVLink.
- Hosts are inter-connected with a backend RDMA fabric with 400Gb/s (Mellanox CX-7) per GPU.

### Configuration

Runs were invoked with the following, where `NUM_NODES` was `4` and `8`.

**Warning**: the command below reflects the original invocation at the time of this benchmark. The torchtitan CLI has since changed to use `--module` and `--config` flags instead of `--job.config-file`. See the current [README](/README.md) for up-to-date usage.
```
  torchrun \
    --nnodes $NUM_NODES  \
    --nproc_per_node 8 \
    --rdzv_id 101 \
    --rdzv_backend c10d \
    --rdzv_endpoint "$MASTER_ADDR:29500" \
    torchtitan/train.py \
    --job.config-file torchtitan/models/llama3/train_configs/llama3_8b.toml \
    --metrics.enable_wandb \
    --training.local_batch_size=2 \
    --training.compile \
    --model.converters="quantize.linear.float8" \
    --quantize.linear.float8.enable_fsdp_float8_all_gather \
    --quantize.linear.float8.precompute_float8_dynamic_scale_for_fsdp \
    --quantize.linear.float8.force_recompute_fp8_weight_in_bwd \
    --profiler.profile_freq 1000000
    --training.steps 2000
```

### Results

Detailed performance results and training configurations can be found in the tables below along and can visualized in [this WandB report](https://api.wandb.ai/links/asaiacai/w4c46stp). `TPS` and `Memory(GiB)` are arbitrarily sampled at the 100th iteration:

| NUM_NODES | TPS/GPU | Memory(GiB) |
| ----- | ----: | ----: |
| 4 | 10938 | 47.96 |
| 8 | 10753 | 46.97 |


### Versions and Dates

| repo | commit | date |
| --- | --- | --- |
| torch | [2.8.0a0+5228986c39](https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes/rel-25-05.html) | 2025/05/29 |
| torchao | [0afa4c1](https://github.com/pytorch/ao/commit/0afa4c1bd28c82921e360ddbd1b27c9d6da5b947) | 2025/06/13 |
| torchtitan | [e7c0cae](https://github.com/pytorch/torchtitan/commit/e7c0cae934df78d6e9c2835f42ff1f757dc3fddc) | 2025/06/13 |
