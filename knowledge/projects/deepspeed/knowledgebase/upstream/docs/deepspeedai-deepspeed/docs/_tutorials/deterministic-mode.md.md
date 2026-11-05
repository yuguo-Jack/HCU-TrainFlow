---
id: doc-deepspeedai-deepspeed-5613c9c67f59ed2beeec
title: deepspeedai/DeepSpeed / docs/_tutorials/deterministic-mode.md
engine: deepspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: deepspeedai/DeepSpeed
commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
path: docs/_tutorials/deterministic-mode.md
raw_sha256: 045e8ef1e2c4a73ed9884942ecd0130017981d38c78031d61e26d373fb737551
sources: []
generated_body_sha256: 986f84907a14bbfbda8f9696f28e99c8bce7469c670845f3ce7d60a46bddee78
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/_tutorials/deterministic-mode.md

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/docs/_tutorials/deterministic-mode.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
title: "Deterministic Mode"
---

The JSON boolean `deterministic_mode` selects an NVIDIA CUDA/PyTorch execution policy.
It defaults to `false` and does not select a Megatron numerical strategy.
Set the workspace environment before the first CUDA operation:

```bash
export CUBLAS_WORKSPACE_CONFIG=:4096:8
```

```json
{
    "train_micro_batch_size_per_gpu": 2,
    "deterministic_mode": true,
    "zero_optimization": {"stage": 2}
}
```

Parsing does not change input configuration or process-global PyTorch settings.
Engine initialization enables strict deterministic algorithms, disables TF32
and cuDNN benchmarking, and enables deterministic cuDNN algorithms.
PyTorch raises for recognized nondeterministic operations without an alternative.
Non-NVIDIA-CUDA enabling currently raises, including a CUDA-compatible accelerator whose DeepSpeed identity is not `cuda`, such as KLXPU. The disabled flag is a no-op.

The flag does not change gradient precision, GAS, TP/EP, overlap, NCCL algorithms
or AutoEP arithmetic, and does not reject configurations merely because they
have not been tested. Existing configuration validation still applies.
Custom kernels, collectives and scheduling are not fully covered by PyTorch's
checks: independently validate complete workload repeatability on a pinned
software/hardware stack and topology. No Megatron bitwise guarantee is implied.

Callers own model initialization, seeds, data ordering and checkpoint RNG/
dataloader state. Engine initialization cannot retroactively make earlier
model construction or CUDA operations deterministic. Workspace settings are
validated, not installed too late. Process-global runtime settings are not
restored by engine teardown or a subsequent disabled engine.

Custom paths also consult PyTorch's deterministic setting:

- FPDT passes the setting to FlashAttention backward in GPU/offloaded paths.
- Legacy DeepSpeedTransformerLayer rejects stochastic_mode=True at construction
  and execution, including when determinism is enabled after model construction.
- Triton grouped GEMM bypasses timing autotuning and uses the first fixed
  configuration for forward, input gradients and weight gradients. Deterministic
  launches also select IEEE `tl.dot` precision, because disabling PyTorch TF32
  does not control Triton input precision. Default autotuning and TF32 precision
  remain unchanged when deterministic algorithms are disabled.

Fixed kernel selection is not certification of every shape/backend, and may
reduce performance. FPDT RNG/communication and full distributed repeatability
still require workload validation. Warn-only PyTorch mode also selects these
paths; legacy stochastic execution raises rather than silently proceeding.

There is no OpGuard or Transformer Engine runtime dependency.
The broader compatibility proposal is
https://github.com/deepspeedai/DeepSpeed/issues/8915.
