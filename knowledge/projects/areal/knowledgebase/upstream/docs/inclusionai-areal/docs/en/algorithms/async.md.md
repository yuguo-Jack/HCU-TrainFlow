---
id: doc-inclusionai-areal-9778e3a5aa4932bca5d1
title: areal-project/AReaL / docs/en/algorithms/async.md
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
path: docs/en/algorithms/async.md
raw_sha256: 06d507cdd362479eb2cb805239311bfebb6c23273775bc8c1351d3b006ac5cd2
sources: []
generated_body_sha256: d8fc4fb54df1bc04efa828918cd2e73b7dbe2252a1784af1049ade6ab724be10
source_state: current-scan
---

# areal-project/AReaL / docs/en/algorithms/async.md

[Original at fixed commit](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/docs/en/algorithms/async.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Asynchronous RL

AReaL natively supports asynchronous RL training, enabling overlapped rollout generation
and model training on disaggregated GPUs. This architecture maximizes GPU utilization by
running inference and training concurrently.

> **Note:** This guide applies to all algorithms when asynchronous training is enabled
> (i.e., `rollout.max_head_offpolicyness > 0`). Setting
> `rollout.max_head_offpolicyness=0` reverts AReaL to synchronous RL. The synchronous
> setting is useful for debugging but is typically 2x slower than asynchronous training.

## Overview

Traditional online RL algorithms assume synchronous execution: the model generates
rollouts, trains on them, and repeats. While simple, this approach leaves GPUs idle
during long rollouts and does not scale well.

Asynchronous RL breaks this constraint by overlapping rollout generation and training.
However, this introduces **off-policyness**: the policy version generating rollouts may
lag behind the training version. To maximize inference throughput, AReaL also supports
**partial rollouts**, where a single trajectory can be segmented across multiple policy
versions.

## Key Techniques

AReaL addresses the aforementioned algorithmic challenges with two complementary
techniques:

### 1. Off-Policyness Control

Limit how stale rollouts can be relative to the current training policy:

```yaml
rollout:
  max_head_offpolicyness: 4  # Allow up to 4 version steps behind
```

`mask_stale_tokens` defaults to `false`, preserving the existing training loss.
To also filter individual actor loss targets by token policy-version age, enable it
explicitly:

```yaml
rollout:
  max_head_offpolicyness: 4
  mask_stale_tokens: true
```

Tokens older than the limit are excluded from actor loss (including MTP). Rollouts
continue normally; context, rewards, PRM scores, advantage computation, and the
original loss normalization denominator are preserved.

**Configuration tips:**

- Set to `0` for synchronous RL (useful for debugging or baseline comparisons)
- Higher values increase throughput but may reduce training stability
- Typical range: 2-8 depending on model size and update frequency

### 2. Decoupled PPO Objective

Handle off-policy data with modified loss computation:

```yaml
actor:
  use_decoupled_loss: true     # Enable decoupled PPO objective
  recompute_logprobs: true     # Recompute logprobs during training
```

**Configuration options:**

- `use_decoupled_loss`: When `false`, uses standard PPO/GRPO objectives
- `recompute_logprobs`: When `false`, reuses logprobs from inference backend
  - **Note:** Must be `true` when `use_decoupled_loss` is enabled

> **Note:** The decoupled PPO loss may conflict with certain algorithm configurations
> (e.g., SAPO). The effects of asynchrony on these newer algorithms remain largely
> understudied.

## References

For a practical walkthrough of asynchronous training, see our
[GSM8K GRPO example](../tutorial/gsm8k_grpo.md).

For algorithmic details and empirical analysis, refer to the
[AReaL paper](https://arxiv.org/pdf/2505.24298).
