---
id: doc-baidu-loong-megatron-c772f24177e0919a65dc
title: baidu-baige/Loong-Megatron / docs/source/api-guide/tensor_parallel.rst
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
path: docs/source/api-guide/tensor_parallel.rst
raw_sha256: cd77b4928765261c5a09f5cc5e2465b0037414083fa333c9123ce4ca33b46075
sources: []
generated_body_sha256: 93dfd845a18c664cf4c59b4cf494d5ef0279e6b27839ff6dba60a57e837a2ec4
source_state: current-scan
---

# baidu-baige/Loong-Megatron / docs/source/api-guide/tensor_parallel.rst

[Original at fixed commit](https://github.com/baidu-baige/Loong-Megatron/blob/64c279afb879229cff12fb293624e3691990403f/docs/source/api-guide/tensor_parallel.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

tensor\_parallel package
========================

This package contains an implementation for tensor parallelism in transformer
models (see `Megatron-LM: Training Multi-Billion Parameter Language Models
Using Model Parallelism <https://arxiv.org/abs/1909.08053>`_ and `Reducing
Activation Recomputation in Large Transformer Models <https://arxiv.org/abs/2205.05198>`_
for details).

Submodules
----------

tensor\_parallel.cross\_entropy module
--------------------------------------

.. automodule:: core.tensor_parallel.cross_entropy
   :members:
   :undoc-members:
   :show-inheritance:

tensor\_parallel.data module
----------------------------

.. automodule:: core.tensor_parallel.data
   :members:
   :undoc-members:
   :show-inheritance:

tensor\_parallel.layers module
------------------------------

.. automodule:: core.tensor_parallel.layers
   :members:
   :undoc-members:
   :show-inheritance:

tensor\_parallel.mappings module
--------------------------------

.. automodule:: core.tensor_parallel.mappings
   :members:
   :undoc-members:
   :show-inheritance:

tensor\_parallel.random module
------------------------------

.. automodule:: core.tensor_parallel.random
   :members:
   :undoc-members:
   :show-inheritance:

tensor\_parallel.utils module
-----------------------------

.. automodule:: core.tensor_parallel.utils
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: core.tensor_parallel
   :members:
   :undoc-members:
   :show-inheritance:
