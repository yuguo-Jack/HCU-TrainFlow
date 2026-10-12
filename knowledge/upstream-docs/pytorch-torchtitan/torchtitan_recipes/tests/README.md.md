---
id: doc-pytorch-torchtitan-40cc4b121517c2d2a8bd
title: pytorch/torchtitan / torchtitan_recipes/tests/README.md
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
path: torchtitan_recipes/tests/README.md
raw_sha256: 6ab82fecab3ace58582c8890348d64e2e2c47dfe06298726c1af2c3b4617aadb
sources: []
generated_body_sha256: 5ca843ae38fefbc2671c0eb752803182b6e22a717cf210e1fbfee7f71425daad
source_state: current-scan
---

# pytorch/torchtitan / torchtitan_recipes/tests/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan_recipes/tests/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Test recipes

These recipes exist to exercise TorchTitan in CI. They are not recommendations
for production training.

- `models/` contains reusable debug configurations for individual models.
- `graph_trainer/` and `torchft/` contain subsystem-specific test recipes.
- `rl/` contains debug-model and CI recipes for RL examples, one module per
  example (verified recipes live in `torchtitan_recipes/rl/`).
- `transformers_modeling_backend.py` contains the test recipes for that
  standalone test surface.

Keep a configuration with its model when it only changes model-local test
setup. A configuration that represents one entry of a cross-model or hardware
test matrix lives next to its test definition in `tests/integration_tests/`,
so adding an integration test edits one file.
