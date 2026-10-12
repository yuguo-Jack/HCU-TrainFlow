---
id: doc-baidu-loong-megatron-3a185e2b95af90b9f1b0
title: baidu-baige/Loong-Megatron / docs/source/api-guide/dist_checkpointing.strategies.rst
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
path: docs/source/api-guide/dist_checkpointing.strategies.rst
raw_sha256: dba5d8e7329edb57771d7df8b9e81b2938fee517730a00f9f4f9f98fa103d8b4
sources: []
generated_body_sha256: dd02b5ce070c77fd58226c734570b90223657756c7adc878f085743bfabbbbc0
source_state: current-scan
---

# baidu-baige/Loong-Megatron / docs/source/api-guide/dist_checkpointing.strategies.rst

[Original at fixed commit](https://github.com/baidu-baige/Loong-Megatron/blob/64c279afb879229cff12fb293624e3691990403f/docs/source/api-guide/dist_checkpointing.strategies.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

dist\_checkpointing.strategies package
======================================

Package defining different checkpoint formats (backends) and saving/loading algorithms (strategies).

Strategies can be used for implementing new checkpoint formats or implementing new (more optimal for a given use case) ways of saving/loading of existing formats.
Strategies are passed to `dist_checkpointing.load` and `dist_checkpointing.save` functions and control the actual saving/loading procedure.

Submodules
----------

dist\_checkpointing.strategies.base module
------------------------------------------

.. automodule:: core.dist_checkpointing.strategies.base
   :members:
   :undoc-members:
   :show-inheritance:

dist\_checkpointing.strategies.tensorstore module
-------------------------------------------------

.. automodule:: core.dist_checkpointing.strategies.tensorstore
   :members:
   :undoc-members:
   :show-inheritance:

dist\_checkpointing.strategies.two\_stage module
------------------------------------------------

.. automodule:: core.dist_checkpointing.strategies.two_stage
   :members:
   :undoc-members:
   :show-inheritance:

dist\_checkpointing.strategies.zarr module
------------------------------------------

.. automodule:: core.dist_checkpointing.strategies.zarr
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: core.dist_checkpointing.strategies
   :members:
   :undoc-members:
   :show-inheritance:
