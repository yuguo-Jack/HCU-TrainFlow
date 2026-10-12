---
id: doc-amd-agi-primus-1fc0fdbeeb2a7f08e3b6
title: AMD-AGI/Primus / docs/02-user-guide/README.md
engine: primus
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: AMD-AGI/Primus
commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
path: docs/02-user-guide/README.md
raw_sha256: 07600a1af55753b57783587293adad21c2f7edc0b68396a7edd5b28d7d611d43
sources: []
generated_body_sha256: 66892e72dea595cd14768da72b51af00e583689ab882068ca949890c365550f2
source_state: current-scan
---

# AMD-AGI/Primus / docs/02-user-guide/README.md

[Original at fixed commit](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/docs/02-user-guide/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# User guide

Core workflows and day-to-day usage.

- [Primus tools](primus-tools.md): start here—an at-a-glance catalog of all Primus tools and ecosystem projects with how-to starting points
- [CLI reference](cli-reference.md): `primus-cli` modes, flags, and subcommands
- [Configuration system](configuration-system.md): YAML configuration model, presets, overrides, inheritance
- [Environment and XLA flags](environment-and-xla-flags.md): where to set env vars, how to override `XLA_FLAGS` safely, how to verify what took effect
- [Pretraining](pretraining.md): pretraining **concepts**: backends, YAML structure, parallelism, configuration inventory
- [End-to-end training recipes](end-to-end-training-recipes.md): pretraining **commands**: copy-paste, GPU-arch-specific run commands
- [Megatron-LM training performance validation](megatron-lm-training.md): reproduce the published Megatron backend benchmarks on the `rocm/primus` image
- [TorchTitan training performance validation](torchtitan-training.md): reproduce the published TorchTitan backend benchmarks on the `rocm/primus` image
- [JAX MaxText training performance validation](jax-maxtext-training.md): reproduce the AMD-published MaxText benchmarks via Primus, MAD, or the standalone scripts
- [Post-training](posttraining.md): SFT and LoRA fine-tuning via Megatron Bridge
- [Node-smoke test instruction](node-smoke-test-instruction.md): screen a cluster fast and exclude bad nodes before launching a real training job
- [Preflight](preflight.md): cluster diagnostics and environment validation
- [Run preflight without a container](preflight-without-container.md): run cluster-diagnostic tool directly on the host
- [Micro-benchmarking](micro-benchmarking.md): GEMM, RCCL, and dense-GEMM benchmark suites
- [Projection](projection.md): memory and performance projection tools
- [Tuning agent](tuning-agent.md): LLM-driven search for an optimal training configuration (uses projection as an oracle)

---

[← Documentation home](../README.md)
