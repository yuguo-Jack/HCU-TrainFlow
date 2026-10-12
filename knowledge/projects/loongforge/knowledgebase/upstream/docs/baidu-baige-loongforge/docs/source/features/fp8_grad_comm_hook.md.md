---
id: doc-baidu-baige-loongforge-c5fb520dc0d56193c180
title: baidu-baige/LoongForge / docs/source/features/fp8_grad_comm_hook.md
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
path: docs/source/features/fp8_grad_comm_hook.md
raw_sha256: a07a3736000208571a67e1d8d0ee9d333380c3974442ba3d32c31fa033053f93
sources: []
generated_body_sha256: 741329345cd000fd34f274cd9179787a2a72b715ac2cd5b9d37f54464f14d80e
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source/features/fp8_grad_comm_hook.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source/features/fp8_grad_comm_hook.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# DDP FP8 Grad AllReduce

DDP FP8 Grad AllReduce (`fp8_a2a_allgather_hook`) is an opt-in DDP communication optimization for the LoongForge embodied training stack. It compresses the gradient all-reduce by quantizing each gradient bucket to FP8 E4M3, running an AllToAll, reducing locally in FP32, requantizing, and gathering the result back with an AllGather. It changes communication precision only; forward and backward computation are unaffected.

This hook operates on **gradients under DDP**. It is the DDP counterpart of [FSDP2 Delta-FP8 Param AllGather](delta_fp8_allgather.md), which compresses parameter AllGather traffic under FSDP2. Pick the one that matches your parallel strategy; they are not used together. Both are independent of LoongForge's end-to-end [FP8 training](fp8_training.md) and do not convert weights, activations, or GEMMs to FP8.

## 1. Requirements

- DDP data parallel with the hook registered via `--ddp-comm-hook fp8_a2a_allgather_hook`
- A CUDA device and the NCCL distributed backend
- An NVIDIA GPU with compute capability 8.9 or later
- PyTorch FP8 E4M3 support and a Triton backend exposing `tl.float8e4nv`

Buckets smaller than `--ddp-comm-hook-fp8-min-mib` and buckets that would exceed the scratch budget fall back to full-precision AllReduce instead of failing the run, so an unsupported or under-budgeted bucket degrades gracefully.

## 2. Usage

Append the hook flag to a DDP embodied launcher:

```bash
bash path/to/ddp_launcher.sh \
    --ddp-comm-hook fp8_a2a_allgather_hook
```

Selective-precision exemption is on by default (`--ddp-comm-hook-fp8-exempt 1d,embed`), which recovers most of the FP8 loss gap at negligible cost. Support in the communication path does not by itself establish numerical or performance suitability for every model. Validate loss, step time, and peak memory against the same model's full-precision DDP baseline before adopting it in another recipe.

## 3. Configuration

| Argument | Default | Description |
| --- | --- | --- |
| `--ddp-comm-hook` | `None` | Set to `fp8_a2a_allgather_hook` to enable the hook |
| `--ddp-comm-hook-fp8-block` | `256` | Elements sharing one FP32 scale; power of two in `[1, 1024]`. Smaller tracks the local dynamic range more tightly but adds `4/block` bytes on the wire (1.6% at 256) |
| `--ddp-comm-hook-fp8-min-mib` | `8.0` | Buckets smaller than this use plain AllReduce; `0` quantizes every bucket |
| `--ddp-comm-hook-fp8-max-scratch-gb` | `24.0` | Total resident comm scratch across buckets (~1.15x each). Over-budget buckets degrade to AllReduce; there is no value that removes the cap |
| `--ddp-comm-hook-fp8-exempt` | `1d,embed` | Comma list of parameter classes kept at the exact FP32 cross-rank mean (see 4.1); `''` disables |
| `--ddp-comm-hook-fp8-error-feedback` | `none` | `none` / `allgather` / `both` — carry a quantization point's residual into the next step (see 4.2) |

Keep the default block size unless a matched loss and performance validation supports changing it.

## 4. How It Works

For each eligible gradient bucket the hook performs:

1. Quantize the bucket per block into an FP8 E4M3 payload with an FP32 scale.
2. AllToAll the payloads so each rank owns one shard of every rank's contribution.
3. Reduce the owned shard locally in FP32.
4. Requantize the reduced shard and AllGather it across ranks.
5. Dequantize the gathered shards back into the bucket buffer.

Because every rank dequantizes the same AllGather result, the final bucket is bit-identical across ranks. Two lossy quantization points sit on this path (the pre-AllToAll bucket and the pre-AllGather shard), and their E4M3 rounding error is systematically same-signed rather than zero-mean, so over a long run it accumulates into a loss bias relative to the full-precision baseline. The next two subsections describe two independent, orthogonal ways to suppress that bias.

### 4.1 Selective-precision exemption (`--ddp-comm-hook-fp8-exempt`)

FP8 block quantization is far harsher on 1-D tensors (RMSNorm/LayerNorm scales, biases): they hold few elements yet share a 256-element block scale with much larger neighbours, so their mantissa is dragged off. These 1-D scales multiply activations directly and are highly loss-sensitive, as are embeddings and output heads. Exemption pulls this small, precision-sensitive set out of the FP8 path and gives it an exact FP32 cross-rank mean (one extra AllReduce, `÷world_size`) patched back over the FP8-reduced buffer; everything else stays FP8.

| Token | Meaning | Detection (structural, model-agnostic) |
| --- | --- | --- |
| `1d` | Every 1-D tensor (norm scales, biases) | `param.dim() <= 1` |
| `embed` | Params of an `nn.Embedding` module | Owning module class |
| `head` | Output-head params | Leaf module named `lm_head` / `output` / `score` / `classifier` |

Detection is structural (module class / leaf name), not name-substring, so a container that merely has `head`/`embed` in its path is never swept in wholesale, and the token embedding is caught whatever it is named. Unknown tokens are rejected at startup. The default exempt set is typically a tiny fraction of trainable elements, so the extra AllReduce is negligible. Exempting a large trainable vocabulary embedding (e.g. `tune_llm=True`) can grow the exempt set enough to erase the throughput gain — use `1d` then; the per-bucket exempt fraction is logged at INFO.

### 4.2 Error feedback (`--ddp-comm-hook-fp8-error-feedback`)

Error feedback (EF) attacks the same accumulated bias with a classic residual: `v = g + residual; q = quant(v); residual = v − dequant(q)`. Carrying each quantization point's residual into the next step makes the residual sequence telescope, bounding the accumulated bias at `e_0 − e_T` instead of drifting. Residuals are stored in FP32 — a lower-precision residual would reintroduce the very drift EF removes.

| Mode | Quantization points covered | Resident residual per element |
| --- | --- | --- |
| `none` | — | 0 |
| `allgather` | Pre-AllGather shard only | 0.5 bytes |
| `both` | Pre-AllToAll bucket + pre-AllGather shard | 4.5 bytes |

`allgather` covers the larger of the two error contributions for 1/9 of the memory. Residuals are the only cross-step state; they are dropped whenever the bucket layout changes (DDP rebuild), since a residual is tied to a byte offset in the buffer.

### 4.3 Combining exemption and error feedback

Exemption and error feedback are orthogonal and can be enabled together; the combination is most useful in precision-sensitive setups. When both are on, the exempt parameters keep their exact FP32 cross-rank mean and are left untouched by error feedback, so the two mechanisms stay independent.

## 5. Troubleshooting

| Symptom | Action |
| --- | --- |
| Startup reports an unsupported device, backend, or Triton FP8 type | Use a full-precision comm hook or run on a supported CUDA/NCCL environment |
| Throughput does not improve | Confirm buckets are above `--ddp-comm-hook-fp8-min-mib`, are not degrading on the scratch budget, and that gradient all-reduce is a material bottleneck |
| OOM with error feedback | `both` roughly doubles resident scratch; use `allgather`, or prefer exemption which adds no memory |
| Loss diverges from the baseline | Confirm exemption is on (default), restore the default block size, and validate against the same model's full-precision baseline |
| Exemption seems to have no effect | Check the INFO log for the per-bucket exempt fraction; ensure parameter names are registered before any dtype/device cast that rebuilds parameters |
