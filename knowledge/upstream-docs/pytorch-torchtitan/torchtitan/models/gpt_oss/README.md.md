---
id: doc-pytorch-torchtitan-7f098d94d5ddb95ea5cc
title: pytorch/torchtitan / torchtitan/models/gpt_oss/README.md
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
path: torchtitan/models/gpt_oss/README.md
raw_sha256: 1be7daa44dd8c5d52844ffd167fcf34d0d34aff476dc754df1a10435f727f544
sources: []
generated_body_sha256: 6ffda6cd3020ccddb216c33f3dd348b1179e545973cd41fa6113830f0d8c4d51
source_state: current-scan
---

# pytorch/torchtitan / torchtitan/models/gpt_oss/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/models/gpt_oss/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# gpt-oss Model in torchtitan

## Quick Start
```bash
MODULE=torchtitan_recipes.tests.models.gpt_oss CONFIG=gpt_oss_debugmodel ./run_train.sh
```

The released 20B and 120B flavors conventionally use
`assets/hf/gpt-oss-20b` and `assets/hf/gpt-oss-120b`. TorchTitan keeps those
asset-path hints without shipping unverified full training recipes.

## Supported Features
- FSDP/HSDP, TP, EP, CP, PP
- Grouped matrix multiplication for efficient computation

CI already runs CP and PP on the debug model:
- `gpt_oss_pp+fsdp+cp+ep+sacop` (`gpt_oss_debugmodel_flex_fsdp2_cp2_pp2_ep4_sac`)
- `gpt_oss_pp+fsdp+ep+sacop`

Those jobs use Interleaved1F1B. FlexInnerAttention zero-bubble / split-backward PP
tests are disabled in `tests/integration_tests/features.py` because
FlexInnerAttention `BlockMask` is not a Tensor (`stage_backward_input` calls
`requires_grad` on every stage input). Full-backward schedules
(1F1B / GPipe / Interleaved1F1B) are unaffected.
