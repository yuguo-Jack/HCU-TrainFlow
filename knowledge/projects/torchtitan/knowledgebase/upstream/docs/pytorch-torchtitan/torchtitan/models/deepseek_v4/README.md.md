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
commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
path: torchtitan/models/deepseek_v4/README.md
raw_sha256: 557281c23bf8da30455f5fd72d26ee8f747ef6ce9a21258d10c451f1ef39a349
sources: []
generated_body_sha256: 219b7674e428d8a9fb5d583df1e93355fe607833d6dc28511a50d1d1b27feae7
source_state: current-scan
---

# pytorch/torchtitan / torchtitan/models/deepseek_v4/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/models/deepseek_v4/README.md)

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

Run the debug model on 4 GPUs with FSDP2, TP2, and EP2:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 NGPU=4 \
  MODULE=torchtitan_recipes.tests.models.deepseek_v4 CONFIG=deepseek_v4_debugmodel_fsdp2_tp2_ep2 \
  ./run_train.sh
```

## Status

The debug model has been smoke-tested with 4 GPUs using FSDP2, TP2, EP2, and the
`spmd_types` backend. The optional MTP path is available through
`deepseek_v4_mtp_debugmodel`. Checkpoint compatibility and larger-scale
convergence validation should be completed before adding production recipes.
