---
id: doc-baidu-loong-megatron-f6334dc09f38d521ce8c
title: baidu-baige/Loong-Megatron / docs/source/api-guide/distributed.rst
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
path: docs/source/api-guide/distributed.rst
raw_sha256: 8eb55fd5c6060a224d9e2df0da7c24d982982d21666eaa8741606da09d7ad3c3
sources: []
generated_body_sha256: e08b7f09831c6f20611499545b6b4c072822b8d6568ddec3a48b2cb964f18aa6
source_state: current-scan
---

# baidu-baige/Loong-Megatron / docs/source/api-guide/distributed.rst

[Original at fixed commit](https://github.com/baidu-baige/Loong-Megatron/blob/64c279afb879229cff12fb293624e3691990403f/docs/source/api-guide/distributed.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

distributed package
===================

This package contains various utilities to finalize model weight gradients
on each rank before the optimizer step. This includes a distributed data
parallelism wrapper to all-reduce or reduce-scatter the gradients across
data-parallel replicas, and a `finalize\_model\_grads` method to
synchronize gradients across different parallelism modes (e.g., 'tied'
layers on different pipeline stages, or gradients for experts in a MoE on
different ranks due to expert parallelism).

Submodules
----------

distributed.distributed\_data\_parallel
---------------------------------------

Model wrapper for distributed data parallelism. Stores gradients in a
contiguous buffer, and supports the option of overlapping communication
(all-reduce or reduce-scatter) with backprop computation by breaking up
full model's gradients into smaller buckets and running all-reduce /
reduce-scatter on each bucket asynchronously. 

.. automodule:: core.distributed.distributed_data_parallel
   :members:
   :undoc-members:
   :show-inheritance:

distributed.finalize\_model\_grads
----------------------------------

Finalize model gradients for optimizer step across all used parallelism modes.
Synchronizes the all-reduce / reduce-scatter of model gradients across DP replicas,
all-reduces the layernorm gradients for sequence parallelism, embedding gradients
across first and last pipeline stages (if not tied), and expert gradients for expert
parallelism.

.. automodule:: core.distributed.finalize_model_grads
   :members:
   :undoc-members:
   :show-inheritance:


Module contents
---------------

Contains functionality to synchronize gradients across different ranks before
optimizer step.

.. automodule:: core.distributed
   :members:
   :undoc-members:
   :show-inheritance:
