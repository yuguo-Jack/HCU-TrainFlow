---
id: doc-pytorch-torchtitan-e0d3161bda95e924c3dd
title: pytorch/torchtitan / torchtitan/rl/examples/verifiers/dapo_math/README.md
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
path: torchtitan/rl/examples/verifiers/dapo_math/README.md
raw_sha256: a3d0d83f7aa9bc86edead81b650b0f4978a8094fec3540978fc902b519f64a99
sources: []
generated_body_sha256: 6c8439e83f8e6241eda5ee33cef22244a037c84139cba544f12eddd3ffc66527
source_state: current-scan
---

# pytorch/torchtitan / torchtitan/rl/examples/verifiers/dapo_math/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/rl/examples/verifiers/dapo_math/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# DAPO Math with Verifiers

This example keeps the existing [DAPO Math](../../dapo_math) recipe unchanged
and replaces only its rollout path with
[Verifiers](https://github.com/PrimeIntellect-ai/verifiers).

It uses Verifiers' null harness and a local subprocess runtime for a
single-turn math task. No tools or sandbox are provided, so do not use this
configuration for untrusted code execution.

## Setup

Follow the [TitanRL setup](../../../README.md), then install this example's dependencies:

```bash
pip install -r torchtitan/rl/examples/verifiers/dapo_math/requirements.txt

python scripts/download_hf_assets.py \
  --repo_id Qwen/Qwen3-4B-Base \
  --all
```

## Run

```bash
python -m torchtitan.rl.train \
  --module torchtitan_recipes.rl.verifiers_dapo_math \
  --config rl_dapo_qwen3_4b_verifiers_8k
```

Use `rl_dapo_qwen3_4b_verifiers_32k` for the 32K response variant.
