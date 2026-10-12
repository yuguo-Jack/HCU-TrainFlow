---
id: doc-ascend-mindspeed-f801e65b502dc522d2fa
title: Ascend/MindSpeed / docs/en/features/fusion-attn-v2.md
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
path: docs/en/features/fusion-attn-v2.md
raw_sha256: 0feda9937bf26a25fa7451bc4794351ae58a37d76e1be93df24ff8f31e9d9244
sources: []
generated_body_sha256: 041bfe5f01f1fbb6815382949c3c9eab7c71d65dc77c49c277b4e930f283bf4d
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/fusion-attn-v2.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/fusion-attn-v2.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# fusion_attention_v2

## Application Scenario

This method is the V2 version of FlashAttention, which extends certain functionalities beyond the V1 version. It currently only supports specific scenarios such as [ALiBi position encoding](./alibi.md) and is disabled by default.

For other scenarios, it is essentially identical to the V1 version, and it is not recommended to enable it proactively. For operator details, see [API Description](../ops/fusion_attention.md).

## Usage

Set `--use-fusion-attn-v2` to invoke this algorithm.

## Effects

The basic effect is equivalent to FlashAttention. For specific scenarios such as [ALiBi Positional Encoding](./alibi.md), it must be manually enabled.
