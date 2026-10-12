---
id: doc-ascend-mindspeed-1814b3c5703c01fa169e
title: Ascend/MindSpeed / docs/en/user-guide/verl.md
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
path: docs/en/user-guide/verl.md
raw_sha256: 99a80ed55ad84507f40d36977672791d359d6d887fb5b1ce7dcd3e57dce37731
sources: []
generated_body_sha256: 1d0c233dbd3753f0743a7b23ad858ba1ebf2702d511dcff1314a0f0970759d60
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/user-guide/verl.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/user-guide/verl.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Verl Using MindSpeed for Backend Training

## Environment Preparation

### 1. MindSpeed Installation

Install the corresponding dependencies according to the MindSpeed documentation.
> For details, see [MindSpeed Installation Guide](install_guide.md).

### 2. Verl Installation

Follow the Verl documentation to install the corresponding dependencies:
<!-- > See [Verl Installation Guide](https://github.com/verl-project/verl/blob/main/docs/ascend_tutorial/en/get_start/quick_start.rst). -->
> Note: If the CANN version used is higher than 8.3.RC1, the installed versions of vLLM and vLLM-Ascend must be greater than or equal to 0.9.1. For vLLM 0.9.1 installation, refer to <https://docs.vllm.ai/projects/ascend/en/v0.9.1/>.

## Enabling MindSpeed Backend

Ensure that the `strategy` configuration for the model is set to `megatron`, for example, `actor_rollout_ref.actor.strategy=megatron`. This can be set in a shell script or a config file.

MindSpeed custom input parameters can be passed through the `override_transformer_config` parameter. For example, to enable the FA feature for the `actor` model, use `+actor_rollout_ref.actor.megatron.override_transformer_config.use_flash_attn=True`.

## Supported Features

| Feature | Configuration Parameter | Status |
| ---- | ----- | ---- |
| FA (must be enabled) | +actor_rollout_ref.actor.megatron.override_transformer_config.use_flash_attn=True | Preview |
| TP           | actor_rollout_ref.actor.megatron.tensor_model_parallel_size  | Preview |
| PP           | actor_rollout_ref.actor.megatron.pipeline_model_parallel_size | Preview |
| EP           | actor_rollout_ref.actor.megatron.expert_model_parallel_size  | Preview |
| ETP          | actor_rollout_ref.actor.megatron.expert_tensor_parallel_size | Preview |
| SP           | actor_rollout_ref.actor.megatron.override_transformer_config.sequence_parallel | Preview |
| Distributed Optimizer | actor_rollout_ref.actor.megatron.override_transformer_config.use_distributed_optimizer | Preview |
| Recomputation       | actor_rollout_ref.actor.megatron.override_transformer_config.recompute_method<br>actor_rollout_ref.actor.megatron.override_transformer_config.recompute_granularity<br>actor_rollout_ref.actor.megatron.override_transformer_config.recompute_num_layers | Preview |
| CP           | actor_rollout_ref.actor.megatron.context_parallel_size<br>actor_rollout_ref.actor.megatron.override_transformer_config.context_parallel_size | Preview |
| mbridge           | actor_rollout_ref.actor.megatron.use_mbridge | Preview |
| RoPE Fusion Optimization           | +actor_rollout_ref.actor.megatron.override_transformer_config.position_embedding_type=rope<br>+actor_rollout_ref.actor.megatron.override_transformer_config.use_fused_rotary_pos_emb=True | Preview |
| SwiGLU Fusion Optimization   | +actor_rollout_ref.actor.megatron.override_transformer_config.swiglu=True<br>+actor_rollout_ref.actor.megatron.override_transformer_config.use_fused_swiglu=True | Preview |
| RMSNorm Fusion Optimization  | +actor_rollout_ref.actor.megatron.override_transformer_config.normalization=RMSNorm<br>+actor_rollout_ref.actor.megatron.override_transformer_config.use_fused_rmsnorm=True | Preview |
| MoE Grouped GEMM  | +actor_rollout_ref.actor.megatron.override_transformer_config.moe_grouped_gemm=True | Preview |
| MoE Token Permute and Unpermute Fusion Optimization  | +actor_rollout_ref.actor.megatron.override_transformer_config.use_fused_moe_token_permute_and_unpermute=True | Preview |

Mbridge does not currently support enabling VPP simultaneously; similarly, use VPP only when mbridge is not enabled.

Note: The "Preview" status indicates a preview, non-official release version, the "Released" status indicates an official release version, and the "Dev" status indicates that it is under development.
