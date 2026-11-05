---
id: doc-pytorch-torchtitan-e1fef1d346129d221046
title: pytorch/torchtitan / torchtitan/models/deepseek_v4/README.md
engine: torchtitan
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: pytorch/torchtitan
commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
path: torchtitan/models/deepseek_v4/README.md
raw_sha256: ae1fd5ee8ec394dc9e7dbe3bc5a039f416a4cddf3ee59fc8a8885e385b54953f
sources: []
generated_body_sha256: 0c896913f61b5226f7a51822369190c53cdbf3188f202e10a1ba550c0ecc0e6c
source_state: current-scan
---

# pytorch/torchtitan / torchtitan/models/deepseek_v4/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/deepseek_v4/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# DeepSeek V4

This folder contains the TorchTitan implementation of DeepSeek V4.

The model entry point is `torchtitan.models.deepseek_v4.build_model_config`. Debug
training configurations used by CI live in
`torchtitan_recipes.tests.models.deepseek_v4`:

- `deepseek_v4_debugmodel`
- `deepseek_v4_mtp_debugmodel`

The `deepseek_v4_flash` and `deepseek_v4_pro` architecture flavors remain
available through `build_model_config`; no unverified full training recipes are
shipped for them.

## Components

- `model.py`: decoder model and transformer block definitions.
- `attention.py`: DeepSeek V4 sparse attention variants, including sliding
  window attention, heavily compressed attention, and compressed sparse
  attention.
- `compressor.py`: KV compression and sparse-index selection helpers.
- `mhc.py`: multi-token/head-coupled branch mixing modules.
- `moe.py`: DeepSeek V4 MoE router and expert wrapper.
- `sharding.py`: declarative sharding config for TP, SP, EP, FSDP, DTensor, and
  `spmd_types`.
- `state_dict_adapter.py`: checkpoint key mapping for DeepSeek V4.

## Smoke Test

Run the DistMuon + AdamW debug model on 4 GPUs with FSDP4 and EP4:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 NGPU=4 \
  MODULE=torchtitan_recipes.tests.models.deepseek_v4 CONFIG=deepseek_v4_debugmodel_fsdp4_ep4 \
  ./run_train.sh
```

## Status

The AdamW debug model has been smoke-tested with 4 GPUs using FSDP2, TP2, EP2,
and the `spmd_types` backend. The optional MTP path is available through
`deepseek_v4_mtp_debugmodel`. Checkpoint compatibility and larger-scale
convergence validation should be completed before adding production recipes.
