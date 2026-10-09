---
id: doc-deepspeedai-deepspeed-153fe5a80b0bbfc510a5
title: deepspeedai/DeepSpeed / docs/code-docs/source/inference-init.rst
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
path: docs/code-docs/source/inference-init.rst
raw_sha256: 6c5128213254de087415fc4563a81f654271d77d35dea676fa9ed081a1af5b51
sources: []
generated_body_sha256: 4cbc65556b508bd09d42e2d5ffc3feaec6cc8ae8910d3529030455d5cfa0b033
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/code-docs/source/inference-init.rst

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/code-docs/source/inference-init.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Inference Setup
-----------------------
The entrypoint for inference with DeepSpeed is ``deepspeed.init_inference()``.

Example usage:

.. code-block:: python

    engine = deepspeed.init_inference(model=net, config=config)

The ``DeepSpeedInferenceConfig`` is used to control all aspects of initializing
the ``InferenceEngine``. The config should be passed as a dictionary to
``init_inference``, but parameters can also be passed as keyword arguments.

.. _DeepSpeedInferenceConfig:
.. autopydantic_model:: deepspeed.inference.config.DeepSpeedInferenceConfig

.. _DeepSpeedTPConfig:
.. autopydantic_model:: deepspeed.inference.config.DeepSpeedTPConfig

.. _DeepSpeedMoEConfig:
.. autopydantic_model:: deepspeed.inference.config.DeepSpeedMoEConfig

.. _QuantizationConfig:
.. autopydantic_model:: deepspeed.inference.config.QuantizationConfig

.. _InferenceCheckpointConfig:
.. autopydantic_model:: deepspeed.inference.config.InferenceCheckpointConfig


Example config:

.. code-block:: python

    config = {
	"kernel_inject": True,
	"tensor_parallel": {"tp_size": 4},
	"dtype": "fp16",
	"enable_cuda_graph": False
    }

.. autofunction:: deepspeed.init_inference