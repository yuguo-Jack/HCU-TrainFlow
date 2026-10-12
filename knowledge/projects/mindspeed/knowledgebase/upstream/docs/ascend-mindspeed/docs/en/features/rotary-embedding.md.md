---
id: doc-ascend-mindspeed-a726d5d80980a5b1b325
title: Ascend/MindSpeed / docs/en/features/rotary-embedding.md
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
path: docs/en/features/rotary-embedding.md
raw_sha256: a992d543770e214d337b7bf4ef5b2f82df5ad9a5b4741b167a6693736be4f879
sources: []
generated_body_sha256: 0563bc1c4718042c06707a5e8c32888bf1f169504cc09a0f144b2dc2e024c3af
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/rotary-embedding.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/rotary-embedding.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Rotary Position Embedding Fusion

## Background and Challenges

RoPE (Rotary Position Embedding) is a position encoding technique widely used in large language models to effectively encode positional information of text sequences. RoPE combines the stability of absolute position encoding with the flexibility of relative position encoding, while also offering excellent length generalization capability. Although RoPE has been adopted in multiple cutting-edge models such as Llama and GLM, the PyTorch framework currently does not provide a dedicated implementation and optimization for RoPE. As a result, model developers typically need to implement RoPE through custom methods, which often incurs high computational and memory overhead.

## Solution

To address the above issues, we have introduced a fusion optimization solution for Rotary Embedding. By consolidating RoPE operations into a single operator, we significantly reduce the number of data transfers and temporary storage requirements, thereby optimizing model training performance. This optimization is implemented by MindSpeed through calling the TorchNPU-side interface, effectively improving the execution efficiency of RoPE in models.

## Application Scenario

Applicable to model architectures that use Rotary Embedding as the position encoding scheme.

## Usage

* Ensure the following parameters are set in the model configuration:
`--position-embedding-type rope`

* At the same time, enabling the RoPE fusion operator requires setting the following parameter:
`--use-fused-rotary-pos-emb`

## Effects

By using the fusion-optimized RoPE operator, model training performance is improved, while memory consumption and computational cost are effectively reduced. On the Llama-2-7b model, the performance improvement is approximately 1%.
