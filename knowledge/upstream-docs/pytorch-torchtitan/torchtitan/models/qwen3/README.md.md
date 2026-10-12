---
id: doc-pytorch-torchtitan-530438e85d994d060b69
title: pytorch/torchtitan / torchtitan/models/qwen3/README.md
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
path: torchtitan/models/qwen3/README.md
raw_sha256: 361f49438757006f3f7c085f7ac6f4044fdad626517cb8727c0a67032f810af1
sources: []
generated_body_sha256: 265a0b84237e8cf23dd453b1e72a060278e9a115dfc86a37a6868b142f76ddb0
source_state: current-scan
---

# pytorch/torchtitan / torchtitan/models/qwen3/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/models/qwen3/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

## Available features
#### Dense Model
- Qwen3 dense model:
    - supports FSDP/HSDP, TP, CP, DDP.
    - Supports AC, torch.compile.
- Qwen3 MoE model:
    - Supports FSDP/HSDP, TP, CP, DDP, EP.
    - Supports AC, torch.compile.
    - MoE models use Token Choice routing. Load-balancing follows the original
      Qwen3 training recipe (auxiliary loss).

Dense and MoE debug models are covered by `tests/integration_tests/models.py`
(FSDP+TP+CP, and FSDP+TP+CP+EP for MoE).

Model architectures exist for 4B, 8B, and 235B-A22B, but those sizes do not
yet have verified training recipes.

## Download Qwen3 tokenizer
```python scripts/download_hf_assets.py --repo_id <hf_repo_name> --assets tokenizer```

For example, the 0.6B and 1.7B repositories are `Qwen/Qwen3-0.6B` and
`Qwen/Qwen3-1.7B`. The conventional local directory is
`assets/hf/<repository basename>` for every supported flavor.


## Remaining work
- Add verified recipes for 4B, 8B pretraining, and 235B-A22B.
- Verify learning rate and schedule on longer training jobs, or cite official
  references.
- Compare against established performance benchmarks.
