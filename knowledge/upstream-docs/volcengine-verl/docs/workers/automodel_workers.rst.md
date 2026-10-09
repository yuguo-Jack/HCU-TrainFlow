---
id: doc-volcengine-verl-1b17adf423b46bb9eb2e
title: verl-project/verl / docs/workers/automodel_workers.rst
engine: verl
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: verl-project/verl
commit: 5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d
path: docs/workers/automodel_workers.rst
raw_sha256: 0449c69bdfe21014a2c1dec2256877678d4e22cdb9605bc7f7f14f539e7db706
sources: []
generated_body_sha256: 6b54e244d6e86effaf733765034955355f31a25a80cdccf76ccdf2a4c79ee3c2
source_state: current-scan
---

# verl-project/verl / docs/workers/automodel_workers.rst

[Original at fixed commit](https://github.com/verl-project/verl/blob/5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d/docs/workers/automodel_workers.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Automodel Backend
=================

Last updated: 03/07/2026.

We support the Automodel (nemo_automodel) backend by implementing the
``AutomodelEngine`` and ``AutomodelEngineWithLMHead`` engine classes.
The Automodel backend delegates model building, parallelization, optimizer
sharding, LR scheduling, gradient clipping, and checkpointing to
nemo_automodel's infrastructure while using verl's training loop,
data pipeline, and loss function.

**Requirements**

- Automodel r0.3.0
- transformers v5.0.0

**Pros**

- Supports FSDP2 and TP distributed strategies out of
  the box.

- Native support for Mixture-of-Experts (MoE) models with Expert
  Parallelism (EP) via DeepEP.

- TransformerEngine (TE) integration for optimized attention, linear
  layers, and RMSNorm.

- Readily supports any HuggingFace model without checkpoint conversion.

**Cons**

- Pipeline parallelism is not yet supported.


SFT Examples
------------

We provide example SFT training scripts using the Automodel backend in
`examples/sft/gsm8k/ <https://github.com/verl-project/verl/blob/main/examples/sft/gsm8k/>`_.

Basic: Qwen2.5-0.5B with FSDP2
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A minimal example using ``Qwen/Qwen2.5-0.5B-Instruct`` with FSDP2 and
no parallelism:

.. code:: shell

   bash examples/sft/gsm8k/run_qwen2_5_0_5b_automodel.sh 4 /tmp/automodel_sft_test

See `run_qwen2_5_0_5b_automodel.sh <https://github.com/verl-project/verl/blob/main/examples/sft/gsm8k/run_qwen2_5_0_5b_automodel.sh>`_.

Advanced: Qwen3-30B MoE with Expert Parallelism
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A larger-scale example using ``Qwen/Qwen3-30B-A3B-Base`` (MoE model)
with Expert Parallelism (EP=8), DeepEP, TransformerEngine backend, and
torch_mm experts backend:

.. code:: shell

   bash examples/sft/gsm8k/run_qwen3_30b_automodel.sh 8 /tmp/automodel_sft_30b

See `run_qwen3_30b_automodel.sh <https://github.com/verl-project/verl/blob/main/examples/sft/gsm8k/run_qwen3_30b_automodel.sh>`_.