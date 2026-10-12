---
id: doc-baidu-baige-loongforge-0819cc845a740626daf1
title: baidu-baige/LoongForge / docs/source/features/fp8_communication.md
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
path: docs/source/features/fp8_communication.md
raw_sha256: 75d4408d6f9700805f15d548e97337545c9eed3248abb26046d38664bdd60b4f
sources: []
generated_body_sha256: e0e82f2582a8ac7ce9d375069027c1ad41b91bfc499abc5658a265d76ada165d
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source/features/fp8_communication.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source/features/fp8_communication.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# FP8 Communication

LoongForge provides two opt-in FP8 communication optimizations for the embodied training stack. Both reduce cross-rank traffic by communicating in FP8 E4M3 instead of BF16/FP32, and both change **communication precision only** — forward and backward computation are unaffected, and neither converts weights, activations, or GEMMs to FP8 (that is the separate end-to-end [FP8 training](fp8_training.md) feature).

Pick the one that matches your parallel strategy; they operate on different collectives and are not used together.

| | [FSDP2 Delta-FP8 Param AllGather](delta_fp8_allgather.md) | [DDP FP8 Grad AllReduce](fp8_grad_comm_hook.md) |
| --- | --- | --- |
| Parallel strategy | FSDP2 | DDP |
| Compresses | Parameter AllGather | Gradient all-reduce |
| Method | Blockwise FP8 delta vs a persistent BF16 reference | FP8 AllToAll → local FP32 reduce → FP8 AllGather |
| Enable with | `--fsdp-delta-fp8-allgather` | `--ddp-comm-hook fp8_a2a_allgather_hook` |

Support in the communication path does not by itself establish numerical or performance suitability for every model. Validate loss, step time, and peak memory against the same model's BF16/FP32 baseline before adopting either in a new recipe.

```{toctree}
:maxdepth: 1

delta_fp8_allgather
fp8_grad_comm_hook
```
