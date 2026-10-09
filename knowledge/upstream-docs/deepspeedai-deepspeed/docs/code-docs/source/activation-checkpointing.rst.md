---
id: doc-deepspeedai-deepspeed-71121bd33fd4e3c5cf70
title: deepspeedai/DeepSpeed / docs/code-docs/source/activation-checkpointing.rst
engine: deepspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: deepspeedai/DeepSpeed
commit: bc1ad320a9afb516797577924a9983c6d7cd6793
path: docs/code-docs/source/activation-checkpointing.rst
raw_sha256: ecf1c2d55659d9aab2c2040a8d9acc3257f48fee9d7e5179189e3d76384c3310
sources: []
generated_body_sha256: 4fa16fe81e7a6b22b6986ed86094348f1a34bf9bca8bc09fddbb258f426e11f4
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/code-docs/source/activation-checkpointing.rst

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/code-docs/source/activation-checkpointing.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Activation Checkpointing
========================

The activation checkpointing API's in DeepSpeed can be used to enable a range
of memory optimizations relating to activation checkpointing. These include
activation partitioning across GPUs when using model parallelism, CPU
checkpointing, contiguous memory optimizations, etc.

Please see the `DeepSpeed JSON config <https://www.deepspeed.ai/docs/config-json/>`_
for the full set.

Here we present the activation checkpointing API. Please see the enabling
DeepSpeed for `Megatron-LM tutorial <https://www.deepspeed.ai/tutorials/megatron/>`_
for example usage.

Configuring Activation Checkpointing
------------------------------------
.. autofunction:: deepspeed.checkpointing.configure

.. autofunction:: deepspeed.checkpointing.is_configured


Using Activation Checkpointing
------------------------------
.. autofunction:: deepspeed.checkpointing.checkpoint

Keyword arguments are forwarded to the checkpointed function. Tensor values passed by
keyword participate in autograd just like positional tensor arguments.

.. autofunction:: deepspeed.checkpointing.reset


Configuring and Checkpointing Random Seeds
------------------------------------------
.. autofunction:: deepspeed.checkpointing.get_cuda_rng_tracker

.. autofunction:: deepspeed.checkpointing.model_parallel_cuda_manual_seed

.. autoclass:: deepspeed.checkpointing.CudaRNGStatesTracker

.. autoclass:: deepspeed.checkpointing.CheckpointFunction