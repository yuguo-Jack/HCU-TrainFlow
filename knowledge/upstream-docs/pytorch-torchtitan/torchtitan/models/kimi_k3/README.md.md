---
id: doc-pytorch-torchtitan-0f8ea4b9321f59208c0f
title: pytorch/torchtitan / torchtitan/models/kimi_k3/README.md
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
path: torchtitan/models/kimi_k3/README.md
raw_sha256: 48883ae505cd2bc21c63be5a8a9e3d33dddaa4da108ada1688b0e1d7d407f40c
sources: []
generated_body_sha256: 655be31b6b7aaf97124b2bfa25b20b7c533162b3809364d65a70956ee1ea2dbe
source_state: current-scan
---

# pytorch/torchtitan / torchtitan/models/kimi_k3/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/models/kimi_k3/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Kimi K3

Kimi K3 combines a hybrid Kimi Delta Attention (KDA) and Multi-head Latent
Attention (MLA) decoder with LatentMoE and a MoonViT-V2 vision encoder.

## Prerequisites

Install the additional dependencies:

```bash
pip install -r .ci/docker/requirements-vlm.txt
```

KDA uses Attention Gym kernels, which need an NVIDIA GPU with CUDA capability
9.0 or newer. Attention Gym runs its CuTe kernels on SM100/SM103 and its Triton
kernels on other GPUs.

## Architecture

Kimi K3 is built on Kimi Delta Attention (KDA) and Attention Residuals
(AttnRes), with 69 KDA layers and 24 Gated MLA layers. Stable LatentMoE selects
16 of 896 experts per token, and MoonViT-V2 provides native vision input.

## Released Model Configuration

The values below follow the
[official Kimi K3 model card](https://huggingface.co/moonshotai/Kimi-K3) and
describe the released model.

| Component | Configuration |
|-----------|---------------|
| Architecture | Mixture-of-Experts (MoE) |
| Parameters | 2.8T total, 104B activated |
| Decoder | 93 layers, 1 dense layer, hidden size 7168, 96 attention heads |
| Attention | 69 KDA layers and 24 Gated MLA layers, context length 1048576 |
| LatentMoE | Dimension 3584, hidden size 3072 per expert, 896 experts, top-16 routing, 2 shared experts |
| Vocabulary | 160K |
| Activation | SiTU-GLU |
| Vision encoder | MoonViT-V2, 401M parameters |
| Quantization | MXFP4 weights and MXFP8 activations with quantization-aware training |
| Modality | Text and image |

## Supported Parallelisms

| Feature | Notes |
|---------|-------|
| FSDP2 / HSDP | Decoder sharded per layer; vision encoder sharded as a separate unit |
| Context parallel | Attention Gym native CP for KDA; MLA supports all-gather K/V with contiguous or head-tail partitions and Ulysses with contiguous partitions |
| Tensor / sequence parallelism | Supported |
| Expert parallelism | Supported |
| Pipeline parallelism | Supported |

## Numerical Parity

The parity script reduces the released Hugging Face configuration to match
TorchTitan's local `debugmodel` configuration before initializing both models.

End-to-end KL divergence against the Hugging Face implementation (multimodal
inputs): **1.0212e-5**, with **100% top-1 and top-5 match**.

Vision parity: pixel preprocessing max difference **1.192e-7**; projected vision
features cosine similarity **0.999987** and max difference **3.125e-2**.

Test scripts:

- `scripts/checkpoint_conversion/numerical_tests_kimi_k3.py` -- Hugging Face vs.
  TorchTitan comparison
- `tests/unit_tests/gpu/models/kimi_k3/test_kimi_k3.py` -- KDA and FSDP2 correctness
