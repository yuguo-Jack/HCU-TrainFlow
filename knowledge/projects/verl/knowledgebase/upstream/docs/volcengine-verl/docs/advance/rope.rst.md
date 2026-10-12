---
id: doc-volcengine-verl-691eec2f03dc3de8d733
title: verl-project/verl / docs/advance/rope.rst
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
path: docs/advance/rope.rst
raw_sha256: 234699b1fb7c6df60d205688d5436a5b3e87f6e414a79df4f1a050f18cb5a50b
sources: []
generated_body_sha256: 56bee316709a788fc9c138f5e3b5b076e321b82ba6cc70e5f8c812d78af06796
source_state: current-scan
---

# verl-project/verl / docs/advance/rope.rst

[Original at fixed commit](https://github.com/verl-project/verl/blob/5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d/docs/advance/rope.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

RoPE Scaling override
=======================================

Last updated: 05/14/2025.

Some models such as `Qwen/Qwen2.5-7B-Instruct <https://huggingface.co/Qwen/Qwen2.5-7B-Instruct#processing-long-texts>`_ support RoPE Scaling but don't have it defined in their config.json file.
For example, this model supports this configuration:

.. code:: python

    {
        ...,
        "rope_scaling": {
            "factor": 4.0,
            "original_max_position_embeddings": 32768,
            "type": "yarn"
        }
    }



In order to support a longer context for such models, you must override the model configs when starting the trainer.

PPO example:

.. code:: bash

    +actor_rollout_ref.model.override_config.rope_scaling.type=yarn \
    +actor_rollout_ref.model.override_config.rope_scaling.factor=4.0 \
    +actor_rollout_ref.model.override_config.rope_scaling.original_max_position_embeddings=32768 \


And for the critic model

.. code:: bash

    +critic.model.override_config.rope_scaling.type=yarn \
    +critic.model.override_config.rope_scaling.factor=4.0 \
    +critic.model.override_config.rope_scaling.original_max_position_embeddings=32768 \