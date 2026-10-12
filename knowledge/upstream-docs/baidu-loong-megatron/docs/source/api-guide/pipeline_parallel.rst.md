---
id: doc-baidu-loong-megatron-bff4b4e7ca11a9697c3b
title: baidu-baige/Loong-Megatron / docs/source/api-guide/pipeline_parallel.rst
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
path: docs/source/api-guide/pipeline_parallel.rst
raw_sha256: 451c05ce0fe7566928e7d96873aeeb24015f6ff7a30127c0107d3c9064a631b3
sources: []
generated_body_sha256: 63ae9ca0cf81eb522b0142a36e5ab3d92c8baacc2b412243ba51b4ca099b5e8e
source_state: current-scan
---

# baidu-baige/Loong-Megatron / docs/source/api-guide/pipeline_parallel.rst

[Original at fixed commit](https://github.com/baidu-baige/Loong-Megatron/blob/64c279afb879229cff12fb293624e3691990403f/docs/source/api-guide/pipeline_parallel.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

pipeline\_parallel package
==========================

This package contains implementations for two different pipeline parallelism
schedules (one without interleaving and one with interleaving, see `Efficient
Large-Scale Language Model Training on GPU Clusters Using Megatron-LM <https://arxiv.org/abs/2104.04473>`_
for details), and a default no-pipelining schedule. It also contains methods
for the point-to-point communication that is needed between pipeline stages.

Submodules
----------

.. mdinclude:: pipeline_parallel_layout.md

pipeline\_parallel.p2p\_communication module
--------------------------------------------

Contains implementations for the various point-to-point communication needed
(e.g., `recv_forward` and `recv_backward`) in the different pipeline parallelism
schedules.

.. automodule:: core.pipeline_parallel.p2p_communication
   :members:
   :undoc-members:
   :show-inheritance:

pipeline\_parallel.schedules module
-----------------------------------

Contains implementations for two pipeline parallelism schedules
(`forward_backward_pipelining_with_interleaving`for pipeline parallelism with
interleaving, `forward_backward_pipelining_without_interleaving` for pipeline
parallelism without interleaving) and a default no-pipelining schedule
(`forward_backward_no_pipelining`). `get_forward_backward_func` returns the right
scheduling function to use based on the configuration being trained
(e.g., if pipeline-parallel size is 1, use `forward_backward_no_pipelining`).

.. automodule:: core.pipeline_parallel.schedules
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: core.pipeline_parallel
   :members:
   :undoc-members:
   :show-inheritance:
