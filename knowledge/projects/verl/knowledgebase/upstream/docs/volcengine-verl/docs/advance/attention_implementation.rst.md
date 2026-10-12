---
id: doc-volcengine-verl-6447c17f8472f9145bb8
title: verl-project/verl / docs/advance/attention_implementation.rst
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
path: docs/advance/attention_implementation.rst
raw_sha256: c5423539e121cfb52ec7742c248b2860696f414718283a91672d4662b97ddc9f
sources: []
generated_body_sha256: c42456aaea77b60e7034318d1c76b0c97e9cc2f7a2aaf79c080b847eeb15f28e
source_state: current-scan
---

# verl-project/verl / docs/advance/attention_implementation.rst

[Original at fixed commit](https://github.com/verl-project/verl/blob/5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d/docs/advance/attention_implementation.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

.. _attention-implementation-override:

Attention Implementation Override
==================================

Last updated: 10/31/2025.

By default, VERL's FSDP workers use ``flash_attention_2`` as the attention implementation for improved performance. 
However, you can now override this setting to use different attention implementations based on your needs.

Supported Attention Implementations
-----------------------------------

The following attention implementations are supported (subject to model and hardware compatibility):

- ``flash_attention_2``: High-performance attention implementation (default)
- ``eager``: Standard PyTorch attention implementation
- ``sdpa``: Scaled Dot-Product Attention (PyTorch native)

When to Override
----------------

You might want to override the attention implementation in the following scenarios:

- **Debugging**: Use ``eager`` for easier debugging and better error messages
- **Compatibility**: Some models or hardware configurations may not support ``flash_attention_2``
- **Memory constraints**: Different implementations have different memory characteristics
- **Performance tuning**: Testing different implementations for optimal performance

Configuration Examples
-----------------------

PPO Training with Eager Attention
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To override the attention implementation for the actor, rollout, and reference models:

.. code:: bash

    python3 ppo_trainer.py \
        +actor_rollout_ref.model.override_config.attn_implementation=eager \
        [other parameters...]

PPO Training with SDPA Attention
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    python3 ppo_trainer.py \
        +actor_rollout_ref.model.override_config.attn_implementation=sdpa \
        [other parameters...]

Critic Model Override
~~~~~~~~~~~~~~~~~~~~~

For training configurations that include a critic model, you can also override its attention implementation:

.. code:: bash

    python3 ppo_trainer.py \
        +actor_rollout_ref.model.override_config.attn_implementation=eager \
        +critic.model.override_config.attn_implementation=eager \
        [other parameters...]

YAML Configuration
~~~~~~~~~~~~~~~~~~

You can also specify the attention implementation in your YAML configuration file:

.. code:: yaml

    actor_rollout_ref:
      model:
        override_config:
          attn_implementation: eager
          # other overrides...

    critic:  # if using a critic model
      model:
        override_config:
          attn_implementation: eager
          # other overrides...

Important Notes
---------------

**Backward Compatibility**: If you don't specify ``attn_implementation`` in the override config, 
VERL will continue to use ``flash_attention_2`` by default, ensuring backward compatibility with existing configurations.

**Model Support**: Not all models support all attention implementations. Ensure your model is compatible 
with the chosen attention implementation before training.

**Performance Impact**: Different attention implementations have varying performance characteristics. 
``flash_attention_2`` typically offers the best performance, while ``eager`` provides better debugging capabilities.

**Hardware Dependencies**: Some attention implementations (like ``flash_attention_2``) may require 
specific hardware or CUDA versions. If you encounter compatibility issues, try using ``eager`` or ``sdpa``.

Troubleshooting
---------------

If you encounter errors when using a specific attention implementation:

1. **Check model compatibility**: Verify that your model supports the chosen attention implementation
2. **Try eager attention**: Use ``attn_implementation=eager`` as a fallback for debugging
3. **Check hardware requirements**: Ensure your hardware supports the attention implementation
4. **Review error messages**: Attention implementation errors often provide clear guidance on supported options

Example Error Resolution
~~~~~~~~~~~~~~~~~~~~~~~~

If you see an error like "flash_attention_2 is not supported", you can resolve it by switching to eager attention:

.. code:: bash

    # Instead of the default flash_attention_2
    python3 ppo_trainer.py +actor_rollout_ref.model.override_config.attn_implementation=eager

This override ensures your training can proceed while you investigate the flash attention compatibility issue.