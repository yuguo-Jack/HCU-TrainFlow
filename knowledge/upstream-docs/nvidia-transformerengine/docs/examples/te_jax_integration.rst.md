---
id: doc-nvidia-transformerengine-9fcdaba51386df2fc69b
title: NVIDIA/TransformerEngine / docs/examples/te_jax_integration.rst
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
path: docs/examples/te_jax_integration.rst
raw_sha256: 32275530253da7ae3bfc614c1113b296544250a00823af7e178976c6dad18001
sources: []
generated_body_sha256: 16f84349e454ed6228420377f093e464aa028252eef388cf98e9ce5a858e026b
source_state: current-scan
---

# NVIDIA/TransformerEngine / docs/examples/te_jax_integration.rst

[Original at fixed commit](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/docs/examples/te_jax_integration.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

..
    Copyright (c) 2022-2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

    See LICENSE for license information.

JAX: Integrating TransformerEngine into an existing framework
=============================================================

This is the landing page for a series of focused documents on bringing
TransformerEngine into a JAX+Flax codebase one optimization at a time. Each
linked page isolates a single feature so you can see exactly what changes are
required and what are the performance benefits.

Pick a topic
------------

.. list-table::
   :header-rows: 1
   :widths: 25, 15, 60

   * - Document
     - Status
     - Covers
   * - `Dense GEMMs <jax/dense.html>`_
     - **Available**
     - ``nn.Dense`` → quantized GEMM; single-GPU speedup; multi-GPU speedup;
   * - `Collective GEMMs <jax/collective_gemm.html>`_
     - *Coming soon*
     -
   * - `Attention <jax/attention.html>`_
     - **Available**
     - Single-GPU and context-parallel attention tutorials
   * - `Expert Parallelism <jax/expert_parallelism.html>`_
     - *Coming soon*
     -


Quantization recipes at a glance
--------------------------------

TE exposes its quantization choices as **recipes**. Please see
`Low-precision Training
<https://docs.nvidia.com/deeplearning/transformer-engine/features/low_precision_training/index.html>`_
for a more detailed description of each recipe.

..  _jax_recipe_table_overview:
.. list-table::
   :header-rows: 1
   :widths: 25, 15, 30, 30

   * - Recipe
     - Hardware
     - State
     - Description
   * - ``MXFP8BlockScaling``
     - Blackwell+
     - none
     - Block-scaled FP8 (32-element blocks)
   * - ``NVFP4BlockScaling``
     - Blackwell+
     - requires a Flax RNG ``sr_rng``
     - FP4 with 2D block scaling and stochastic rounding
   * - ``DelayedScaling``
     - Hopper+
     - amax history (Flax variables)
     - Per-tensor FP8 with amax history
   * - ``Float8CurrentScaling``
     - Hopper+
     - none
     - Per-tensor FP8 without an amax history

Import them from ``transformer_engine.common.recipe``.


Conventions used across these documents
---------------------------------------

* **Framework.** Flax Linen. (TE/JAX uses Linen; see
  `Flax NNX/Linen interop
  <https://flax.readthedocs.io/en/latest/guides/bridge_guide.html>`_ and
  `Haiku/Flax interop
  <https://dm-haiku.readthedocs.io/en/latest/notebooks/flax.html>`_ if you're on
  a different stack.)
* **Baseline dtype.** bf16 for inputs and parameters.
* **Benchmarking.** ``quickstart_jax_utils.speedometer`` runs a JIT-compiled
  fwd+bwd loop with warmup 


.. toctree::
   :hidden:

   jax/dense
   jax/collective_gemm
   jax/attention
   jax/expert_parallelism