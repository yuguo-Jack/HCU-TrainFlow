---
id: doc-baidu-loong-megatron-f28b837f69504ef67717
title: baidu-baige/Loong-Megatron / docs/source/api-guide/multi_latent_attention.rst
engine: loongforge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: baidu-baige/Loong-Megatron
commit: 64c279afb879229cff12fb293624e3691990403f
path: docs/source/api-guide/multi_latent_attention.rst
raw_sha256: 352e1e15fa95c044d37c9ebeee2f958ee76e84baf2db572c54ac0976da23fc34
sources: []
generated_body_sha256: e6f3bec61f236279badcfc938b4b955c90f196039b05f7137549862d6a122994
source_state: current-scan
---

# baidu-baige/Loong-Megatron / docs/source/api-guide/multi_latent_attention.rst

[Original at fixed commit](https://github.com/baidu-baige/Loong-Megatron/blob/64c279afb879229cff12fb293624e3691990403f/docs/source/api-guide/multi_latent_attention.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Multi-Latent Attention
======================

Multi-Latent Attention overview 
-------------------------------

Multi-Latent Attention ("MLA") is an innovative attention mechanism introduced by Deepseek team that enhances the efficiency of attention computation by leveraging multiple latent spaces. This approach is particularly beneficial for large language models (LLMs), as it reduces the computational burden associated with traditional attention mechanisms. According to Deepseek-V2 technical report, MLA achieves better performance compared to Multi-Head Attention (MHA) and requires smaller KV cache.

Enabling Multi-Latent Attention
-------------------------------

To enable MLA in Megatron-LM, set the following flags in command line:
- `--multi-latent-attention` to enable MLA in MLP.
- Set `MLATransformerConfig` to configure MLA.
