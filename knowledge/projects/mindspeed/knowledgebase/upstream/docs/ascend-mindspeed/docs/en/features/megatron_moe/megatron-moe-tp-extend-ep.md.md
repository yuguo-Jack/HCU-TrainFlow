---
id: doc-ascend-mindspeed-c86960b13793379f6ac1
title: Ascend/MindSpeed / docs/en/features/megatron_moe/megatron-moe-tp-extend-ep.md
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
path: docs/en/features/megatron_moe/megatron-moe-tp-extend-ep.md
raw_sha256: 555e8cfa88c82731aa463a9e525b265c02ae9eac6854a77dd0c275dce4b7992e
sources: []
generated_body_sha256: 7e674b17a36a4f2797be55a9014909a9ff8ccb8c0a35055f7a77706816d987e7
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/megatron_moe/megatron-moe-tp-extend-ep.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/megatron_moe/megatron-moe-tp-extend-ep.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Megatron MoE TP Extended EP

## Background and Challenges

When TP+EP is enabled, the expert layer TP group partitions expert parameters. In fine-grained small expert scenarios of MoE, the GMM operator efficiency drops significantly after TP partitioning.

## Solution

To address the GMM operator efficiency degradation after TP partitioning in small expert scenarios, the expert layer TP group does not partition expert parameters but instead partitions the number of experts.

## Use Cases

Fine-grained small experts, similar to DeepSeek-V2 models, where each expert has a small number of parameters.

## Usage

- Enable `--moe-tp-extend-ep` to use this feature.
- The following must also be enabled:
  - `--moe-permutation-async-comm`
  -`--moe-grouped-gemm`, currently only supports Grouped MLP.
- Configuration constraint: Ensure that `--num-experts` is divisible by the product of `--tensor-model-parallel-size` and `--expert-model-parallel-size`.

> [!NOTE]
>
> - Currently, this feature does not support the `Moe Token drop and pad` mode, meaning `--moe-expert-capacity-factor` must be `None`.
> - Currently, only the `alltoall_seq dispatcher` is supported.

## Performance

By avoiding TP splitting of expert parameters, the GMM operator efficiency is improved in small expert scenarios, thereby enhancing the overall model training performance. For MoE models at the trillion-parameter scale similar to DeepSeek-V2 with fine-grained small experts, the performance can be improved by over 10%.
