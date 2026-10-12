---
id: doc-ascend-mindspeed-dfb187b5ea2bd49ad588
title: Ascend/MindSpeed / docs/en/features/multi-head-latent-attention.md
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
path: docs/en/features/multi-head-latent-attention.md
raw_sha256: 612fbd2e3b915b7b638ccd32e815672951f57e3e92f72bfeef7d8a43678b727a
sources: []
generated_body_sha256: 1fc9bd774bc15a5a7db3f3efb43cd03c2d78780678913125e2bcd50ce0a4ad4c
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/multi-head-latent-attention.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/multi-head-latent-attention.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Megatron Multi-Head Latent Attention

## Background and Challenges

Traditional Transformer models typically use the multi-head attention (MHA) mechanism, which computes correlations among query, key, and value matrices, enabling the model to capture dependencies between different parts of an input sequence. During the inference generation phase, to avoid redundant computation, the model needs to maintain a KV cache. However, the memory footprint of this cache is proportional to factors such as sequence length, batch size, hidden layer dimension, and the number of attention heads. This issue causes significant memory overhead when the model is used in real-world apps, becoming a major bottleneck for model scaling. To address this problem, DeepSeek proposed Multi-head Latent Attention (MLA), which optimizes the KV cache storage structure to effectively reduce memory usage, thereby improving model efficiency during inference.

## Solution

Unlike the traditional KV cache, MLA does not directly store the complete key and value matrices. Instead, it represents keys and values through a compressed latent vector, reducing the KV cache via low-rank compression techniques. During training, the query also undergoes low-rank compression to reduce activation memory. The following figure compares the working mechanisms of MLA with MHA, Grouped-Query Attention (GQA), and Multi-Query Attention (MQA).
![multi-head-latent-attention.png](../figures/multi-head-latent-attention.png)

For more details on MLA, see the paper [DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model](<https://arxiv.org/abs/2405.04434>).

## Application Scenario

MLA addresses the memory bottleneck of standard Transformer models. It can be used as a general model architecture to reduce memory usage and improve inference efficiency.

## Usage

To enable MLA, add the following parameter configuration to your training script:

`--multi-latent-attention`：Use Multi-Head Latent Attention

`--q-lora-rank`：Rank of Query tensor's low rank representation

`--kv-lora-rank`：Rank of Key and Value tensors' low rank representation

`--qk-head-dim`：Dimension of the head in the QK projection. q_head_dim = qk_head_dim + qk_pos_emb_head_dim

`--qk-pos-emb-head-dim`：Dimension of the position embedding in the QK projection

`--v-head-dim`：Dimension of the head in the V projection

`--rotary-scaling-factor`：Rotary scaling factor for the rotary embeddings

## Performance

Compared with traditional MHA, MLA can significantly reduce KV cache usage while retaining the ability to recover all information in the key and value matrices. Its feature representation capability is superior to other KV cache methods (such as GQA, MQA, etc.), ensuring model performance.
