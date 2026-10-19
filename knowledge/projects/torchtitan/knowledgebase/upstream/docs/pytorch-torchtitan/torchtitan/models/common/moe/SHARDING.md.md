---
id: doc-pytorch-torchtitan-f080e0f56c612bd60e67
title: pytorch/torchtitan / torchtitan/models/common/moe/SHARDING.md
engine: torchtitan
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: pytorch/torchtitan
commit: a242475253433725f10f39c18f5ccbfdf188e097
path: torchtitan/models/common/moe/SHARDING.md
raw_sha256: fb7ce1f5e6020f5256dcb4ace71f4c2ebb409ca1ddb9dcf4a9207948dc2aa715
sources: []
generated_body_sha256: 4bde428eb323d45fd00d994d5a8e9d2d29fd132a45e94cb9d725bdb7e4793d96
source_state: current-scan
---

# pytorch/torchtitan / torchtitan/models/common/moe/SHARDING.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/models/common/moe/SHARDING.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# MoE Sharding

Config-based sharding for MoE submodules, implemented in
[`sharding.py`](sharding.py). Mesh axis names (`ep`, `edp_shard`) and how
EP reuses ranks from the dense world mesh are in
[`torchtitan/distributed/PARALLELISM_CONTEXT.md`](../../../distributed/PARALLELISM_CONTEXT.md).

## Overview

The diagram below shows the MoE layer's SPMD layout flow using `spmd_types` for
the two supported expert-parallel configurations (SP on/off). For MoE models,
`expert_parallel_degree` must be at least `tensor_parallel_degree`.

![MoE Sharding](../../../../assets/images/moe_sharding.png)

[Excalidraw source](https://excalidraw.com/#json=fZ1o2BuwXSVIGQhXM5gbr,KHKKckUbQXm68uiS3i_L7w)

## Configurations

"MoE input src → dst" shows the input redistribution at the MoE boundary.
"Routed input src → dst" shows the redistribution before routed-expert
dispatch and computation.
"Routed expert weights" describes the routed expert weight placement.

| Config | Routed expert mesh | Routed expert weights | MoE input src → dst | Routed input src → dst | MoE output |
|--------|-------------------|----------------------|---------------------|------------------------|------------|
| EP on, SP on | sparse (`ep`/`edp_shard`) | `Shard(0)` on EP | `Shard(0)` -> `Shard(0)` | `Shard(0)` -> `Shard(0)` | `Partial` -> `Shard(0)` |
| EP on, SP off | sparse (`ep`/`edp_shard`) | `Shard(0)` on EP | `Replicate` -> `Replicate` | `Replicate` -> `Shard(0)` | `Partial` -> `Replicate` |

## Submodule sharding

- **MoE wrapper**: input/output redistribution between `sp_layout` and
  `desired_input_layouts`. With EP, output is sequence-sharded or `Partial`
  and redistributed to `sp_layout` at the boundary. Without EP, TP/SP are
  disabled and routed-expert activations remain replicated.
- **Router gate**: weights `Replicate`, output stays DTensor.
- **Shared experts** (w13/w2): dense-family TP plan. `ColumnParallelLinear`
  gathers the w13 input. The local w2 projection produces `Partial`. With EP
  and SP off, it stays `Partial` until the shared and routed paths are added,
  then the MoE boundary performs the single all-reduce. With SP on, the w2
  boundary reduces `Partial` to `Shard(0)` before the paths are added.
- **Routed experts** (`RoutedExperts`): the local SPMD region runs
  dispatch/compute/combine on local tensors while checking its input and
  output layout contracts. Expert-weight `state_shardings` live on its `w13`
  and `w2` grouped linears and are unsharded when EP is disabled.
- **Routed-output postprocessing**: `output_postprocess` operates on dispatched
  expert outputs on the sparse expert mesh. `offsets_E` is required to
  identify which rows of `routed_output_RD` is from which expert.
  Currently, `output_postprocess` only takes in `routed_output_RD`,
  and thus the same operation must be applied to all of the expert outputs.
  So its parameters should use `Replicate` on `dp_replicate`,
  `edp_shard`, and `ep`.
