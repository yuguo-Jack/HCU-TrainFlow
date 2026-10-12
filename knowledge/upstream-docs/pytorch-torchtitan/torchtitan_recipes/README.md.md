---
id: doc-pytorch-torchtitan-78474b70c7370caa0651
title: pytorch/torchtitan / torchtitan_recipes/README.md
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
path: torchtitan_recipes/README.md
raw_sha256: a72fb9eab9eb7f376a50622327954f614694ed6aea5bb782aae51035e9c9157a
sources: []
generated_body_sha256: 1dfd32ae0fa342907049088ef5c37e938ca4a08330996459e93b0c5df4111ad7
source_state: current-scan
---

# pytorch/torchtitan / torchtitan_recipes/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan_recipes/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# TorchTitan recipes

This package contains complete, runnable training configurations. Core model
packages under `torchtitan.models` contain architecture definitions and model
flavors, but do not select datasets, optimizers, parallelism, or cluster paths.

Public recipes are limited to configurations that have been exercised by the
project in training, convergence, performance, or maintained feature workflows.
Configurations used only for CI live under `torchtitan_recipes.tests` and are
not recommendations for real training.

The package is organized by ownership:

- `models/` contains verified recipes for core models.
- `graph_trainer/`, `torchft/`, and `rl/` mirror their owning experimental or
  training subsystem.
- `overrides/` contains opt-in component implementations.
- `tests/` contains CI-only model fixtures (integration-suite configurations
  live with their test definitions in the repository's `tests/integration_tests/`).

| Module | Scope | Validation reference |
| --- | --- | --- |
| `torchtitan_recipes.models.llama3` | Llama 3 pretraining | `torchtitan/models/llama3/README.md`, `docs/benchmarks/` |
| `torchtitan_recipes.models.deepseek_v3` | DeepSeek V3 pretraining | `torchtitan/models/deepseek_v3/README.md` |
| `torchtitan_recipes.models.qwen3` | Qwen3 pretraining and SFT | `torchtitan/models/qwen3/README.md` |
| `torchtitan_recipes.models.flux` | Flux pretraining | `torchtitan/models/flux/README.md` |
| `torchtitan_recipes.models.muse_glimmer` | Muse Glimmer pretraining | `torchtitan/models/muse_glimmer/README.md` |
| `torchtitan_recipes.graph_trainer` | GraphTrainer training | `torchtitan/experiments/graph_trainer/README.md` |
| `torchtitan_recipes.rl` | RL examples | `torchtitan/rl/examples/` |
| `torchtitan_recipes.torchft.llama3` | TorchFT replicated training | `torchtitan/experiments/torchft/README.md` |

Select a recipe by its exact import path:

```bash
MODULE=torchtitan_recipes.models.llama3 CONFIG=llama3_8b ./run_train.sh
```

Bundled opt-in component overrides live under `torchtitan_recipes.overrides`.
The generic override mechanism is documented in `torchtitan/config/OVERRIDE.md`
and accepts external modules as well.
