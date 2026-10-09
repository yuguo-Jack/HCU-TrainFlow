---
id: doc-nvidia-transformerengine-ab3e8e4c1778cdd4b135
title: NVIDIA/TransformerEngine / docs/examples/jax/attention.rst
engine: transformer-engine
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: NVIDIA/TransformerEngine
commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
path: docs/examples/jax/attention.rst
raw_sha256: fc4e7894e9e691997e69c6675cf9fa5eda5d0ce70c0e2562f7e916f6b2c84e8e
sources: []
generated_body_sha256: 61977501b4e119bc7c974bbcf58ddf05484392bc10db1159aa7e2787249a34bf
source_state: current-scan
---

# NVIDIA/TransformerEngine / docs/examples/jax/attention.rst

[Original at fixed commit](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/docs/examples/jax/attention.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

..
    Copyright (c) 2022-2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

    See LICENSE for license information.

JAX: Attention with TransformerEngine
=====================================

Transformer Engine's JAX attention APIs support self-attention and
cross-attention with MHA, GQA, and MQA. Inputs can use standard BSHD or packed
THD layouts, with Q/K/V supplied separately or in packed forms.

Common options include causal and padding masks, bias, dropout, sliding-window
attention (SWA), attention sinks, and experimental ``score_mod`` callbacks for
FlexAttention-style customization. The API also supports different Q/K and V
head dimensions, as used by the attention operation after the projection
stages in DeepSeek-style MLA.

For long contexts, selected BSHD and THD configurations support context
parallelism with Ring or AllGather collectives. Exact fused-kernel availability
depends on the input shape, dtype, GPU architecture, and feature combination;
see the `JAX DotProductAttention API reference
<../../api/jax.html#transformer_engine.jax.flax.DotProductAttention>`_ for the
full interface. Choose the tutorial that matches how the sequence dimension is
distributed in your model.

`← Back to the JAX integration overview <../te_jax_integration.html>`_

Pick a tutorial
---------------

.. list-table::
   :header-rows: 1
   :widths: 30, 70

   * - Tutorial
     - Covers
   * - `Single-GPU Attention <attention_single_gpu.html>`_
     - BSHD GQA + SWA; performance against a native JAX baseline;
       DeepSeek-style MLA head dimensions
   * - `Context-Parallel Attention <attention_context_parallel.html>`_
     - Packed THD GQA + SWA on four GPUs; Ring and AllGather CP with striped
       load balancing; performance against single-GPU fused attention

.. toctree::
   :hidden:

   attention_single_gpu
   attention_context_parallel