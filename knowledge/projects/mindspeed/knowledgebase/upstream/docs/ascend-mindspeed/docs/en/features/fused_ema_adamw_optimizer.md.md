---
id: doc-ascend-mindspeed-67631413c4f44d6c9f2f
title: Ascend/MindSpeed / docs/en/features/fused_ema_adamw_optimizer.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed
commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
path: docs/en/features/fused_ema_adamw_optimizer.md
raw_sha256: f3bc7154a72037384492aef0393d1efa8f282961a48a8365455d6d1e7313ef33
sources: []
generated_body_sha256: e226be2ce3fba6c48ec215c4b8109e9f65f9da7479f79715744b68e06a750a96
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/fused_ema_adamw_optimizer.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/fused_ema_adamw_optimizer.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# fused_ema_adamw Optimizer

## Background and challenges

In the multimodal domain, an EMA model is often additionally generated during model training for downstream tasks. Therefore, EMA model data needs to be generated and saved during training. The fused_ema_adamw optimizer can additionally maintain a copy of EMA model parameters during model training, and the EMA model will be automatically saved to the model weights file when weights are saved.

## Solution

During training, the fused_ema_adamw optimizer maintains an `ema_params` state for the model parameters and updates it during each optimizer iteration. The update formula for the ema_params state is as follows:

    ema_params = ema_decay * ema_params + (1 - ema_decay) * model_params

```model_params``` represents the model parameters, and `ema_decay` is a hyperparameter. The `--ema-decay` can be specified in the training script using `--ema-decay <value>`. If not specified in the script, the default `ema_decay` is `0.9999`.<br>

## Application Scenario

Primarily used in multimodal training scenarios where the EMA model needs to be saved for subsequent tasks.<br>

## Usage

1. Add `--optimizer-selection fused_ema_adamw` to the script to enable the fused_ema_adamw optimizer. The optimizer's `ema_params` state saving functionality and the EMA model weights saving functionality will be enabled together.<br>
2. Add `--ema-decay <value>` to the script to specify `ema_decay`. If not specified, it defaults to `0.9999`.<br>

## Effects

1. Since the fused_ema_adamw optimizer needs to maintain an additional `ema_params` state during training, memory overhead will increase.<br>
2. When saving weights, the optimizer's `ema_params` state will be stored in the `distrib_optim.pt` file.<br>
3. When saving weights, the EMA model weight data will be stored in the `ema_model` field within the `model_optim_rng.pt` file.<br>

## Notes

1. The fused_ema_adamw optimizer does not support being enabled simultaneously with the parameter replica reuse feature. When using this optimizer, do not add the `--reuse-fp32-param` parameter to the training script.
2. The fused_ema_adamw optimizer needs to maintain an additional set of EMA data during training, which increases memory overhead. The extent of the memory increase varies depending on the training configuration. When using it, adjust the training script or model structure appropriately based on the actual changes in hardware memory.
