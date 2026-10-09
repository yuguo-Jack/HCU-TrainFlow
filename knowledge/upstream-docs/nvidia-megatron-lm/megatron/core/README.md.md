---
id: doc-nvidia-megatron-lm-6a5365aaaf5a4e7cc5e6
title: NVIDIA/Megatron-LM / megatron/core/README.md
engine: megatron
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: NVIDIA/Megatron-LM
commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
path: megatron/core/README.md
raw_sha256: 229c12d19ab7f970e787877a511cd9dbbc5a31d22508191c5c1cf0a5f3e96212
sources: []
generated_body_sha256: 6ca57455fab0d3b8b7e8903d87754e94e7bfa49f76d9a98d4da75468869f42b2
source_state: current-scan
---

# NVIDIA/Megatron-LM / megatron/core/README.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/megatron/core/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<div align="center">

Megatron Core
=============
<h4>Production-ready library for building custom training frameworks</h4>

<div align="left">

## ⚡ Quick Start

```bash
# Install Megatron Core
uv pip install megatron-core

# Distributed training example (2 GPUs, mock data)
torchrun --nproc_per_node=2 examples/run_simple_mcore_train_loop.py
```

# What is Megatron Core?

**Megatron Core** is an open-source PyTorch-based library that contains GPU-optimized techniques and cutting-edge system-level optimizations. It abstracts them into composable and modular APIs, allowing full flexibility for developers and model researchers to train custom transformers at-scale on NVIDIA accelerated computing infrastructure.

## 🚀 Key Components

### GPU-Optimized Building Blocks
- **Transformer Components**: Attention mechanisms, MLP layers, embeddings
- **Memory Management**: Activation recomputation
- **FP8 Precision**: Optimized for NVIDIA Hopper, Ada, and Blackwell GPUs

### Parallelism Strategies
- **Tensor Parallelism (TP)**: Layer-wise parallelization (activation memory footprint can be further reduced using sequence parallelism)
- **Pipeline Parallelism (PP)**: Depth-wise model splitting and pipelining of microbatches to improve efficiency
- **Context Parallelism (CP)**: Long sequence handling ([documentation](https://docs.nvidia.com/megatron-core/developer-guide/latest/user-guide/features/context_parallel.html))
- **Expert Parallelism (EP)**: Split experts of an MoE model across multiple GPUs


## 🔗 Examples & Documentation

**Examples:**
- **[Simple Training Loop](https://github.com/NVIDIA/Megatron-LM/blob/main/examples/run_simple_mcore_train_loop.py)** - Basic usage
- **[Multimodal Training](https://github.com/NVIDIA/Megatron-LM/blob/main/examples/multimodal/)** - Vision-language models
- **[Mixture-of-Experts](https://github.com/yanring/Megatron-MoE-ModelZoo)** - MoE examples
- **[Mamba Models](https://github.com/NVIDIA/Megatron-LM/blob/main/examples/mamba/)** - State-space models

**Documentation:**
- **[📚 API Guide](https://docs.nvidia.com/megatron-core/developer-guide/latest/api-guide/index.html)** - Complete API documentation
- **[💡 Developer Guide](https://docs.nvidia.com/megatron-core/developer-guide/latest/index.html)** - Custom framework development

---

*For complete installation instructions, performance benchmarks, and ecosystem information, see the [main README](../../README.md).*