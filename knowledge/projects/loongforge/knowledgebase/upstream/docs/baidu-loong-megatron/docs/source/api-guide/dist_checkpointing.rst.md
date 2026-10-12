---
id: doc-baidu-loong-megatron-60b20bf4bfc9a7b9c007
title: baidu-baige/Loong-Megatron / docs/source/api-guide/dist_checkpointing.rst
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
path: docs/source/api-guide/dist_checkpointing.rst
raw_sha256: cd3dfa960f3a2e5eec0e13945c5f5dc15ecfc5394ed9b54e27e3c7eed7c33d9c
sources: []
generated_body_sha256: de16cbc641ce2906197b55ab284417a82df13c50864199090488b0ec63ff8e2f
source_state: current-scan
---

# baidu-baige/Loong-Megatron / docs/source/api-guide/dist_checkpointing.rst

[Original at fixed commit](https://github.com/baidu-baige/Loong-Megatron/blob/64c279afb879229cff12fb293624e3691990403f/docs/source/api-guide/dist_checkpointing.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

dist\_checkpointing package
===========================

A library for saving and loading the distributed checkpoints.
A "distributed checkpoint" can have various underlying formats (current default format is based on Zarr)
but has a distinctive property - the checkpoint saved in one parallel configuration (tensor/pipeline/data parallelism)
can be loaded in a different parallel configuration.

Using the library requires defining sharded state_dict dictionaries with functions from  *mapping* and *optimizer* modules.
Those state dicts can be saved or loaded with a *serialization* module using strategies from *strategies* module.

Safe Checkpoint Loading
-----------------------

Since **PyTorch 2.6**, the default behavior of `torch.load` is `weights_only=True`.
This ensures that only tensors and allow-listed classes are loaded, reducing the risk of arbitrary code execution.

If you encounter an error such as:

.. code-block:: bash

   WeightsUnpickler error: Unsupported global: GLOBAL argparse.Namespace was not an allowed global by default.

you can fix it by explicitly allow-listing the missing class in your script:

.. code-block:: python

   import torch, argparse

   torch.serialization.add_safe_globals([argparse.Namespace])


Subpackages
-----------

.. toctree::
   :maxdepth: 4

   dist_checkpointing.strategies

Submodules
----------

dist\_checkpointing.serialization module
----------------------------------------

.. automodule:: core.dist_checkpointing.serialization
   :members:
   :undoc-members:
   :show-inheritance:

dist\_checkpointing.mapping module
----------------------------------

.. automodule:: core.dist_checkpointing.mapping
   :members:
   :undoc-members:
   :show-inheritance:

dist\_checkpointing.optimizer module
------------------------------------

.. automodule:: core.dist_checkpointing.optimizer
   :members:
   :undoc-members:
   :show-inheritance:

dist\_checkpointing.core module
-------------------------------

.. automodule:: core.dist_checkpointing.core
   :members:
   :undoc-members:
   :show-inheritance:

dist\_checkpointing.dict\_utils module
--------------------------------------

.. automodule:: core.dist_checkpointing.dict_utils
   :members:
   :undoc-members:
   :show-inheritance:


dist\_checkpointing.utils module
--------------------------------

.. automodule:: core.dist_checkpointing.utils
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: core.dist_checkpointing
   :members:
   :undoc-members:
   :show-inheritance:
