---
id: doc-ascend-mindspeed-d7a39ae3bb6a463da289
title: Ascend/MindSpeed / docs/en/features/megatron_moe/megatron-moe-allgather-overlap-comm.md
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
path: docs/en/features/megatron_moe/megatron-moe-allgather-overlap-comm.md
raw_sha256: 12e7bbbb91c81388364ea9eb8620366d920d599438f547dd1a430e3a0b88ca2a
sources: []
generated_body_sha256: 6450592598868b9f76c8f9f10b9e34a631d8e8e312cb5cb530255ed2260f3a68
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/megatron_moe/megatron-moe-allgather-overlap-comm.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/megatron_moe/megatron-moe-allgather-overlap-comm.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Communication Overlap for Megatron MoE Allgather Dispatcher

## Background and Challenges

In MoE, a large amount of EP communication is not hidden, accounting for a significant proportion of the end-to-end time. This overhead can be overlapped with computation to improve model training performance.

## Solution

During the forward pass, asynchronous communication is used to overlap with computation as much as possible. At the same time, the entire computation flow is split into subgraphs, enabling communication-computation overlap during the backward pass as well, thereby accelerating model training. This feature is specifically optimized for the `allgather dispatcher`.

## Usage

- Enable this feature by turning on `--moe-allgather-overlap-comm`.
- The following must also be enabled:
    - `--moe-permutation-async-comm`
    - `--moe-token-dispatcher-type allgather`
    - `--moe-grouped-gemm`, currently only supports Grouped MLP.

## Application Scenario

Applicable to megatron-moe, specifically the dropless scheme branch, when EP communication becomes a bottleneck and communication overlap for EP communication is needed.

> [!NOTE]
>
> Enabling this feature will increase memory usage, which is expected behavior.
