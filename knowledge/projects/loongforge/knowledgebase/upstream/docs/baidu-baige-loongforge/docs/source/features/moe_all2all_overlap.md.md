---
id: doc-baidu-baige-loongforge-a42248168742bd699795
title: baidu-baige/LoongForge / docs/source/features/moe_all2all_overlap.md
engine: loongforge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: baidu-baige/LoongForge
commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
path: docs/source/features/moe_all2all_overlap.md
raw_sha256: bd5b07da7b731f7cc3b3d0259ea4c9153da39fa0da7622e3a6cc493aaa46a615
sources: []
generated_body_sha256: 8ea99b88411f237f5bf673313007008b5e7f2429b0f03766b35c6ab9709d8741
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source/features/moe_all2all_overlap.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source/features/moe_all2all_overlap.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# MoE All-to-All Overlap  
LoongForge provides communication-oriented optimizations for MoE models. By adding the corresponding Megatron launch flags, the All-to-All traffic in Expert Parallel (EP) can be overlapped with computation, delivering the best training throughput.

---

## 1. 1F1B A2A Overlap

During MoE training the EP-induced All-to-All is usually one of the dominant bottlenecks. Inspired by DSv3 DualPipe, this framework interleaves the forward / backward computation of different micro-batches with EP All-to-All on the time axis. The expensive EP communication is thus hidden behind compute, greatly reducing its impact on overall throughput.

### Features
* Hide All-to-All with micro-batch overlap  
* Split weight-gradient and activation-gradient transfers for better PP overlap  
* FP8 training support  

### Usage
Add the following launcher flags:

```bash
--overlap-moe-expert-parallel-comm \
--delay-wgrad-compute
```

Prerequisite: Interleave 1F1B schedule must be enabled.

For best overlap we recommend:

```bash
export CUDA_DEVICE_MAX_CONNECTIONS=32
```
*(This may slightly hurt TP overlap; choose according to whether TP or EP dominates communication.)*

---

## 2. Fine-Grained Activation Offload

In long-context training the activation memory grows rapidly with sequence length and soon becomes the limiting factor. The common remedy is to combine Tensor Parallelism (TP) with **full-layer recomputation** to compress activation footprint.  
However, the 1F1B A2A overlap strategy relies on module-wise interleaving of adjacent batches, making traditional full-layer recomputation incompatible.

To solve this, the framework introduces **module-level selective recomputation plus fine-grained activation offload**, approximating the memory savings of full-layer recomputation while preserving the overlap schedule (see figure).
![offload_stream](../../assets/images/offload.png)

### Features
* Activation offload & reload hidden behind compute  
* Tensor-level offload granularity  
* FP8 training support  

### Usage
Enable **module-level selective recomputation**:

```bash
--recompute-granularity selective \
--recompute-modules a2a_overlap_attn a2a_overlap_post_attn a2a_overlap_mlp
```

Enable **tensor-level activation offload**:

```bash
--fine-grained-activation-offloading \
--offload-tensors dispatched_input pre_mlp_layernorm_output
```

Additionally, bind each process to the NUMA node local to its GPU to improve D2H/H2D bandwidth:

```bash
--bindpcie
```
