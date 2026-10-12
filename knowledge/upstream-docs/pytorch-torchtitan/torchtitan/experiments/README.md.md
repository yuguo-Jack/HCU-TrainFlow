---
id: doc-pytorch-torchtitan-a82896bb4adc9bdcf014
title: pytorch/torchtitan / torchtitan/experiments/README.md
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
path: torchtitan/experiments/README.md
raw_sha256: 7cd9902b4283ea8749c5f8a00071145ac145ef14f17bf51b60bf3bc44e69f13c
sources: []
generated_body_sha256: 75e834fb620d9b3707c5f51381df4c3615c97436e7d3adef5903dce6c31cb251
source_state: current-scan
---

# pytorch/torchtitan / torchtitan/experiments/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/experiments/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

To accelerate contributions to and innovations around `torchtitan`, we are adding this new, experimental folder. Below are the general contributing guidelines, and we look forward to your contributions!

## Contributing Guidelines

We provide this `experiments/` folder to host experiments that add significant value to `torchtitan`, with the following principles. We refer to the part of `torchtitan` outside `experiments` as `core`.
1. Each subfolder in `experiments` will be an experiment, with a clear theme which can be flexible, such as
    - A new model, or preferably a new model architecture, with its training infrastructure including parallelization functions. Please see the [instructions](/torchtitan/models/README.md) on how to contribute a new model.
    - An enhancement or addition to the existing infrastructure of `torchtitan`.
2. It is the contributors' responsibility to justify the value of an experiment. `torchtitan` team will review proposals on a case-by-case basis. As part of the contribution, the contributors should provide documentation that clearly showcases the motivation and innovation of an experiment, including reports on performance and loss convergence.
3. An experiment should reuse existing `torchtitan` code as much as possible, such as modules in [`components/`](../components/), model base classes in [`models/base/`](../models/base/), and [`train.py`](../train.py). The main extension points are [new models](../models/README.md), [component overrides](../config/OVERRIDE.md), and [custom trainer configs](../config/README.md#adding-configuration-fields).
    - The extension points are subject to change. We kindly request that contributors provide feedback if they encounter issues reusing any components, rather than simply using a copy-and-paste approach.
    - The degree to which existing components are reused and whether duplications are legit will also be a criteria of whether an experiment would be accepted.
4. Each experiment is independent from other experiments, and can have its own dependencies (on top of [core dependencies](../../requirements.txt)), and its own tests. An experiment should not contain vendor-specific code, such as kernels written in a proprietary language. Those can be hosted outside as dependency.
5. The dependency from `experiments` to `core` is one-way. Anything in `experiments` is optional for `core` to run successfully. In particular, development in `core` is not blocked by breakage in `experiments`. We will utilize GitHub's [CI mechanism](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#onpushpull_requestpull_request_targetpathspaths-ignore) to help test an experiment periodically and only if the experiment itself is affected by a PR.
6. Each experiment needs to have an owner. The owner is responsible to work with `torchtitan` team to maintain the quality and healthiness of an experiment, which includes
    - adapting an experiment to changes in `core` and fix broken tests, no later than the next official `torchtitan` release;
    - responding to GitHub issues and questions in a timely manner.
7. `torchtitan` team reserve the right to remove an experiment. In particular, an experiment should be removed if
    - it has served its purpose (e.g., providing findings, or getting some features upstreamed to `core` or PyTorch, etc.), or
    - it gets stale (e.g. not being maintained).


## Current experiments

| Experiment | Test Status | Owners |
| ----- | ----: | ----: |
| [graph_trainer](./graph_trainer/) | [![GraphTrainer 8 GPU Integration Tests](https://github.com/pytorch/torchtitan/actions/workflows/integration_test_8gpu_graph_trainer.yaml/badge.svg?branch=main)](https://github.com/pytorch/torchtitan/actions/workflows/integration_test_8gpu_graph_trainer.yaml?query=branch%3Amain) [![GraphTrainer H100 8 GPU Integration Tests](https://github.com/pytorch/torchtitan/actions/workflows/integration_test_8gpu_graph_trainer_h100.yaml/badge.svg?branch=main)](https://github.com/pytorch/torchtitan/actions/workflows/integration_test_8gpu_graph_trainer_h100.yaml?query=branch%3Amain) | [@SherlockNoMad](https://github.com/SherlockNoMad) |
| [torchft](./torchft/) | [![TorchFT 8 GPU Integration Tests](https://github.com/pytorch/torchtitan/actions/workflows/integration_test_8gpu_torchft.yaml/badge.svg?branch=main)](https://github.com/pytorch/torchtitan/actions/workflows/integration_test_8gpu_torchft.yaml?query=branch%3Amain) | [@d4l3k](https://github.com/d4l3k) [@tushar00jain](https://github.com/tushar00jain) |
| [transformers_modeling_backend](./transformers_modeling_backend/) | [![Transformers modeling backend 8 GPU Integration Tests](https://github.com/pytorch/torchtitan/actions/workflows/integration_test_8gpu_transformers_modeling_backend.yaml/badge.svg?branch=main)](https://github.com/pytorch/torchtitan/actions/workflows/integration_test_8gpu_transformers_modeling_backend.yaml?query=branch%3Amain) | [@HosseinKaviani-H](https://github.com/HosseinKaviani-H) |
