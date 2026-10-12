---
id: doc-deepspeedai-deepspeed-c51cebeaab2f348ade6a
title: deepspeedai/DeepSpeed / docs/code-docs/source/pipeline.rst
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
path: docs/code-docs/source/pipeline.rst
raw_sha256: bd5115425eee2ededa4ecacd8b82a9f0ccd7920bb66d20afc38ae4e1d4b9cb2a
sources: []
generated_body_sha256: f3e3a1cf48dfaf62abb532155ac68cff2cd4c1b6bab94e46a9213ff76f5d2369
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/code-docs/source/pipeline.rst

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/code-docs/source/pipeline.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Pipeline Parallelism
====================

Model Specification
--------------------
.. autoclass:: deepspeed.pipe.PipelineModule
    :members:

.. autoclass:: deepspeed.pipe.DualPipeVModule
    :members:

.. autoclass:: deepspeed.pipe.LayerSpec
    :members:

.. autoclass:: deepspeed.pipe.TiedLayerSpec
    :members:

.. autoclass:: deepspeed.runtime.pipe.ProcessTopology
    :members:

Training
--------
.. automodule:: deepspeed.runtime.pipe.engine
    :members:

.. autoclass:: deepspeed.runtime.pipe.dualpipev.DualPipeVEngine
    :members:

Extending Pipeline Parallelism
------------------------------
.. automodule:: deepspeed.runtime.pipe.schedule
    :members: