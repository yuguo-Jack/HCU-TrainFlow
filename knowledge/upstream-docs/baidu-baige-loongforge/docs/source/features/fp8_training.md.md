---
id: doc-baidu-baige-loongforge-44fd2b5c2f2c0b431f0d
title: baidu-baige/LoongForge / docs/source/features/fp8_training.md
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
path: docs/source/features/fp8_training.md
raw_sha256: 9ef10f9a7790801143878581e904aa37ab10cd7d42cdb955ad411e301c8c3ad7
sources: []
generated_body_sha256: 045d79640cca75dcb33cd22abbefc3d3eda6524b8634ced15a184e8715002b7f
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source/features/fp8_training.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source/features/fp8_training.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# FP8 Training

DeepSeek-V3 models adopt **Blockwise FP8** training:  
* Finer-grained scaling (tile-wise for activations, block-wise for weights) replaces per-tensor quantisation, cutting quantisation noise.  
* Up-to-date amax statistics reduce distribution-shift error that plagues delayed updates.  

This section lists the feature flags / environment variables required to turn the scheme on in LoongForge, gives a proven recipe, and collects troubleshooting hints.

---

## 0. Prerequisites

| Item | Requirement |
|------|-------------|
| **Hardware** | Native FP8 support |
| **Software** | Transformer Engine enabled in the framework |
| **Care** | FP8 is numerically stricter → keep NaN/Inf/overflow monitors active while you dial in the setup |

---

## 1. Feature switches

### 1.1 CLI arguments

| Argument | Meaning |
|----------|---------|
| `--fp8-format e4m3` | Use **E4M3** (4-bit exponent, 3-bit mantissa) for FP8 tensors. Must be combined with `--fp8-recipe blockwise`. |
| `--fp8-recipe blockwise` | Turn on **block-wise / tile-wise quantisation** and per-block/tile amax tracking. Requires `--fp8-format e4m3`. |
| `--fp8-param-gather` | Keep **weights in FP8** during distributed gather/communication and throughout the param buffer. Lowers memory and traffic, but needs a full convergence & checkpoint regression test. |

### 1.2 Environment variables

| Variable | Purpose |
|----------|---------|
| `FP8_QUANT_FWD_INP_AMAX_EPS` | Epsilon clamp for **forward activation** amax (avoid div-by-zero → NaN). **Default 0, recommended 1e-12** |
| `FP8_QUANT_FWD_WEIGHT_AMAX_EPS` | Same for **forward weight** amax. |
| `FP8_QUANT_BWD_GRAD_AMAX_EPS` | Same for **backward gradient** amax. If NaN appears in back-prop, check this first. |
| `NVTE_FP8_BLOCK_SCALING_FP32_SCALES` | Store scaling factors in **FP32** instead of E8M0 when set to `1`. Do **not** enable on Blackwell. |
| `NVTE_FP8_BLOCK_SCALING_FWD_INP_POWER2` | Force **E8M0** scales for forward activations when set to `1`. |
| `NVTE_FP8_BLOCK_SCALING_FWD_WEIGHT_POWER2` | Force **E8M0** scales for forward weights when set to `1`. |
| `NVTE_FP8_BLOCK_SCALING_BWD_GRAD_POWER2` | Force **E8M0** scales for backward grads when set to `1`. |

---

## 2. Recommended recipe

### Stage 1 – baseline (prove stability)
```bash
--fp8-format e4m3 \
--fp8-recipe blockwise
```
Train until loss/metrics match the BF16 reference.

### Stage 2 – optimise (save memory)
```bash
--fp8-format e4m3 \
--fp8-recipe blockwise \
--fp8-param-gather
```
Re-run full convergence + downstream eval + checkpoint round-trip.

### Universal epsilon guard (add at the top of your launch script)
```bash
export FP8_QUANT_FWD_INP_AMAX_EPS=1e-12
export FP8_QUANT_FWD_WEIGHT_AMAX_EPS=1e-12
export FP8_QUANT_BWD_GRAD_AMAX_EPS=1e-12
```

---

## 3. Quick troubleshooting checklist

| Symptom | Likely fix |
|---------|------------|
| NaN/Inf in loss or grads | Raise the three `*_AMAX_EPS` values gradually (1e-12 → 1e-10). |
| Divergence vs. BF16 | Disable `--fp8-param-gather` first; if still diverging, lower LR 10-20 %. |
| Checkpoint reload failure | Ensure the same FP8 flags & epsilon values were used when the checkpoint was saved. |

With the above switches and epsilon guards, Blockwise FP8 training in LoongForge is ready for production-scale runs.

---

## 4. Related

For scenarios where full FP8 may regress (small MoE experts, high TP, short sequences), see [Adaptive FP8 Training](adaptive_fp8.md) for a benchmark-driven per-module precision selection mechanism.
