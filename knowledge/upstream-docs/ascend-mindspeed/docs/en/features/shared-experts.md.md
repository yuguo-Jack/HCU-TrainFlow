---
id: doc-ascend-mindspeed-c85a37a6cc96bf1e61e9
title: Ascend/MindSpeed / docs/en/features/shared-experts.md
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
path: docs/en/features/shared-experts.md
raw_sha256: 2989b64119fc8227e82eab0f0cb7f3ae3b289e06032e709d74cc6d68c9ca17b7
sources: []
generated_body_sha256: 0eb1a1db0e665c21ff25f82f595407ee8c46b9b45ae8b0f6f0587e7103fc34a4
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/shared-experts.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/shared-experts.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Shared Experts

## Background and Challenges

Large language models face significant computational cost issues when scaling parameter sizes. With the evolution of Mixture of Experts (MoE) models, the concepts of routed experts and shared experts have emerged. For routed experts, input data passes through a routing module that selects experts with higher probabilities for computation; for shared experts, input data does not need to go through the routing module—all data is processed by the shared experts. The computation results of routed experts and shared experts are summed to produce the final output of the MoE module.

## Solution

By combining shared experts with routed experts, the MoE model can attend to both the commonality and specificity of input data across different input scenarios, thereby improving the model's generalization capability.

Some experts are designated as shared experts to capture and integrate common knowledge across different contexts, thereby reducing parameter redundancy in other routed experts.

For more information about shared experts, see [DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models](https://arxiv.org/pdf/2401.06066).

Figure 1 Shared expert isolation

![img](../figures/shared-experts.png)

## Application Scenario

Usage in MoE scenarios: `--moe-model-type megatron_moe`.

## Usage

Shared expert-related commands and parameter descriptions:

| Command Parameter                     | Description                   |
|--------------------------|------------------------|
| `--n-shared-experts [int]` | Number of shared experts                 |

> [!NOTE]
>
> * Enabling shared experts requires mcore mode, meaning `--use-legacy-models` is not set.
> * The command parameter for configuring the intermediate hidden layer size of shared experts is the same as that for routed experts: `--ffn-hidden-size [int]`

## Effects

By enabling shared experts, parameter redundancy among other routed experts can be reduced, parameter efficiency can be improved, and each routed expert can be ensured to focus on unique aspects.
