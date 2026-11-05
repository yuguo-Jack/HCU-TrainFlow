---
id: doc-inclusionai-areal-181e2ab12a0894f0c4fa
title: areal-project/AReaL / docs/en/tutorial/megatron.md
engine: areal
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: areal-project/AReaL
commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
path: docs/en/tutorial/megatron.md
raw_sha256: c0728d6313cc6f41c519355a4f6b92c0194f773fbbd54f3a02f8daf19cbca4ca
sources: []
generated_body_sha256: 5711bf754bdb3544e6a465f57d6abd9374be98a1e008426182fc7ca8f48c65ce
source_state: current-scan
---

# areal-project/AReaL / docs/en/tutorial/megatron.md

[Original at fixed commit](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/docs/en/tutorial/megatron.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Fine-tuning Large MoE Models

Compared to PyTorch FSDP, Megatron-LM supports full 5D parallelism, delivering better
scaling and efficiency. AReaL fully supports customized RL training with Megatron-LM as
the backend. This guide explains how to harness the Megatron training backend and train
large MoE models for your application.

## Enabling Megatron Backend

Shifting from FSDP to Megatron requires only a single line of change: the
`actor.backend` field from `fsdp:d4` to `megatron:d4`.

For a complete guide on allocation mode syntax, parallelism dimensions, and GPU
calculations, see the [Allocation Mode Reference](../reference/alloc_mode.md).

## Bridge Backend Selection

`MegatronEngine` supports two bridge backends configured by
`actor.megatron.bridge_type`:

```yaml
actor:
    megatron:
        bridge_type: mbridge  # default (backward compatible)
```

Set `bridge_type: megatron-bridge` to use the new backend.

For trade-offs and migration guidance, see the
[Megatron Bridge Backend Reference](../reference/bridge_backend.md).

## Freezing Vision Parameters

Qwen3-VL and Qwen3.5 (including Qwen3.8-27B) using `megatron-bridge` freeze the vision
encoder and its projector/merger by default. No environment variable or CLI override is
needed. The explicit equivalent is:

```yaml
actor:
  megatron:
    bridge_type: megatron-bridge
    freeze_vision_model: true
    freeze_vision_projection: true
```

The equivalent CLI overrides are `actor.megatron.freeze_vision_model=true` and
`actor.megatron.freeze_vision_projection=true`. These settings reach the native model
provider before DDP and optimizer construction. To freeze only the encoder while keeping
the merger trainable, set `freeze_vision_model: true` and
`freeze_vision_projection: false`. Freeze both components to keep cached visual
embeddings valid across language-model updates, assuming the image preprocessing is
unchanged.

Both options default to `null`: Qwen3-VL/Qwen3.5 resolve this to `true`, while other
models preserve their provider's freezing policy. Set either option to `false` to train
that component. Explicit settings with an unsupported bridge or provider raise an error.
Qwen4-Exp (Qwen3.8 Flash Next) uses a separate `mcore-bridge` adapter that already
freezes its entire `visual` module, including its merger, without these options.

## MoE Parallel Strategy

For MoE models, Megatron supports separate parallelism for attention and FFN modules
using the hybrid syntax. For example:

```
megatron:(attn:d1p4t2c2|ffn:d1p4t1e4)
```

This 16-GPU configuration uses PP=4, with attention modules using TP=2 and CP=2, while
expert modules use TP=1 and EP=4. See
[MoE Parallel Folding](https://github.com/NVIDIA/Megatron-LM/tree/main/megatron/core/transformer/moe#moe-parallel-folding)
for details on this feature.

**Tuning Guides:**

- [Megatron Performance Best Practice](https://github.com/NVIDIA/Megatron-LM/tree/main/megatron/core/transformer/moe#performance-best-practice)
- [verl with Megatron Practice](https://github.com/ISEEKYAN/verl_megatron_practice)

## Aligning Inference and Training Precision

Due to the sparse nature of MoE models, the logits calculated by forward passes during
inference and training could be severely misaligned, leading to unstable training
results. To mitigate this instability, it is highly recommended to set
`actor.megatron.use_deterministic_algorithms=True` to disable nondeterministic
calculations in Megatron, although this may cause a ~10-20% slowdown in training steps.

As an example, you can run GRPO on the Qwen3 30B-A3B MoE model and GSM8K dataset (on a
32-GPU ray cluster) directly with the following command:

```bash
# NOTE: Allocation mode here is only for illustration purposes. It is not optimized.
python3 examples/math/gsm8k_rl.py --config <megatron_config.yaml> \
    scheduler.type=ray \
    experiment_name=megatron-moe-gsm8k-grpo trial_name=trial-0 \
    rollout.backend=sglang:d4t4 actor.backend=megatron:(attn:d1p4t2c2|ffn:d1p4t1e4) \
    cluster.n_nodes=4 cluster.n_gpus_per_node=8 actor.path=Qwen/Qwen3-30B-A3B \
    actor.megatron.use_deterministic_algorithms=True
```
