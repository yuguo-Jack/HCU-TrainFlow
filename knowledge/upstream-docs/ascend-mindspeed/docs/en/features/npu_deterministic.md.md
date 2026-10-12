---
id: doc-ascend-mindspeed-3a4cb8430c45100a1a48
title: Ascend/MindSpeed / docs/en/features/npu_deterministic.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed
commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
path: docs/en/features/npu_deterministic.md
raw_sha256: a411c4429fbdef78b4258aaf69401e3b8d95cead80bc06c3c3c27c14e4547f20
sources: []
generated_body_sha256: e2d21880a6fca7df06a8daaee32217763e849d1acdc1ab436949b3e0ceb8821d
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/npu_deterministic.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/npu_deterministic.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Deterministic Computing

## Background and Challenges

During training, various random factors can cause the training process to be inconsistent across experiments, preventing their LOSS curves and performance curves from perfectly overlapping.
However, repeatable and comparative experiments sometimes require deterministic computing results to ensure reproducibility.

## Solution

To meet this requirement, the deterministic computing feature has been introduced. It allows users to ensure the consistency of training results across multiple runs through Ascend chips, thereby aiding tasks such as performance tuning and controlled experiments.

## Application Scenario

When you need to conduct performance comparisons or reproduce specific scenarios.

## Usage

To enable this feature, add `--npu-deterministic` to your script.

## Effects

The deterministic computing feature ensures that multiple experiments with the same parameters produce identical results.
