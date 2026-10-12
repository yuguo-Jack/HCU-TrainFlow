---
id: doc-ascend-mindspeed-885cd5e868c2eb7b7e44
title: Ascend/MindSpeed / docs/en/features/eod-reset.md
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
path: docs/en/features/eod-reset.md
raw_sha256: fa44cf5209170529b97802a8a64b4e2ae059bed757084d9e0a3fef9f0b5dc491
sources: []
generated_body_sha256: 54994e191054b617d06a1b991e91083875ab4bae4059f5cb78ebd09ca47a9612
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/eod-reset.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/eod-reset.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Support for the EOD Reset Training Scenario

## Background and Challenges

Typically, a text sequence fed into the model within a batch is formed by concatenating multiple documents. By default, these documents are treated as a single sequence, with no masking applied to the self attention between them. In certain cases, the documents are required to be independent, meaning they cannot perform self attention on each other. In this scenario, the attention mask and position ids need to be reset at the end of each document (EOD). When the `--reset-position-ids` parameter is disabled, position encoding is calculated for the entire sequence; when enabled, position encoding is calculated independently within each sequence.

## Solution

The EOD Reset training scenario is supported by invoking the variable-length mode of the underlying flash-attention operator. Additionally, in the EOD Reset training scenario, Ring Attention parallelism for long sequences is supported to accelerate processing for ultra-long sequence scenarios.

## Usage

1. Data Preparation
    - First, ensure that an EOD token is added to the end of each document.
    - When `--attention-mask-type` is set to `causal`, due to internal implementation requirements, the length of each subsequence will be padded online to a multiple of CP × lcm(2, TP), where lcm is the least common multiple. In this scenario, `--variable-seq-lengths` must be enabled because padding will cause the sequence length to change.

2. Parameter Settings
    - Enable the `--reset-attention-mask` option.
    - Use the `--reset-position-ids` option to indicate whether position encoding is reset.
    - `--attention-mask-type` can be specified as `causal` or `general`; both produce equivalent computation results. `causal` is an accelerated implementation, while `general` is the baseline approach.

> [!NOTE]
>
> In the Ascend EOD Reset training scenario, when mask-type is set to general, Ring/Hybrid Attention performance drops significantly compared to Ulysses, which is expected behavior. When mask-type is set to `causal`, the accelerated implementation is used.
