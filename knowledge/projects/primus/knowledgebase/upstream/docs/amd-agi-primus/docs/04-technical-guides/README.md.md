---
id: doc-amd-agi-primus-4b62f33960673840c0bb
title: AMD-AGI/Primus / docs/04-technical-guides/README.md
engine: primus
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: AMD-AGI/Primus
commit: 8e7a2406111e1c2c3d22112ddb3a1741c619b2ea
path: docs/04-technical-guides/README.md
raw_sha256: 8a079e689e7404e990b2572b8f831a6f44547085812cb719b585c6b20b963412
sources: []
generated_body_sha256: 8c94c1d8d912849d104fa44ae0cb4ec8bcc89dac7b3b1dc8874edd9939b63355
source_state: current-scan
---

# AMD-AGI/Primus / docs/04-technical-guides/README.md

[Original at fixed commit](https://github.com/AMD-AGI/Primus/blob/8e7a2406111e1c2c3d22112ddb3a1741c619b2ea/docs/04-technical-guides/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Technical guides

Deep technical topics for advanced users.

- [Parallelism strategies](parallelism-strategies.md): DP, TP, PP, SP, CP, EP, FSDP explained
- [Parallelism configuration](parallelism-configuration.md): per-backend parallelism setup and batch size relationships
- [Collective operations](collective-operations.md): NCCL/RCCL operations and their role in each parallelism strategy
- [Performance tuning](performance-tuning.md): HipBLASLt, Primus-Turbo, FP8, MoE optimization
- [MoE training deep-dive](moe-training.md): bottlenecks and Primus-Turbo optimizations for Mixture-of-Experts models
- [MegaMoE fused MoE layer](mega-moe.md): FlyDSL-based fused MoE layer for EP-only bf16 training, setup and reproduction
- [Data preparation](data-preparation.md): tokenization, data formats, mock data
- [Checkpoint management](checkpoint-management.md): formats, save/load, distributed checkpointing
- [Multi-node networking](multi-node-networking.md): InfiniBand, RoCE, AINIC configuration
- [AINIC bundle versions](ainic-bundle-versions.md): rebuilding a training image against a different AINIC bundle
- [Profiling and observability](profiling-and-observability.md): Torch profiler, TraceLens, memory snapshots, projection, pp_vis
- [Logging and experiment tracking](logging-and-experiment-tracking.md): TensorBoard, WandB, MLflow setup per backend
- [Fault tolerance and elastic training](fault-tolerance-and-elastic-training.md): graceful exit, auto-resume, in-process restart, torchft
- [Determinism and reproducibility](determinism-and-reproducibility.md): deterministic mode, seeds, trade-offs
- [Diffusion models](diffusion-models/README.md): Flux diffusion architecture, data pipeline, and FP8 / MXFP4 training
- [Hybrid models](hybrid-models/README.md): Zebra-Llama hybrid recurrent-attention (Mamba/KDA/GDN + MLA) models, FLA-parity recipes, and checkpoint conversion
- [Native SFT and LoRA](native-sft-lora.md): Megatron-native SFT/LoRA runbook (BF16 / FP8 / FP4), no Megatron-Bridge dependency
- [Native SFT LoRA on MI455X](LoRA_Native_Trainer_MI455_README.md): 1-GPU gfx1250 recipes (Llama-3.2-1B + 70B/72B/235B proxies)
- [SpecForge](specforge/introduction.md): speculative-decoding draft training — capture, offline train, and online train through `primus-cli`

---

[← Documentation home](../README.md)
