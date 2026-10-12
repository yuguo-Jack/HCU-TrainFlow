---
id: doc-baidu-loong-megatron-d48a5db953cf096a3c94
title: baidu-baige/Loong-Megatron / docs/source/api-guide/transformer.rst
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
path: docs/source/api-guide/transformer.rst
raw_sha256: a083e2f1b07ba0c79c0bc118fe7cadbca9a619940f8cbc621f0650e64e185953
sources: []
generated_body_sha256: 8179443c8caf8fa51ca966ff8a5fe420b365333dd053b7820dd8eadbae48cd4d
source_state: current-scan
---

# baidu-baige/Loong-Megatron / docs/source/api-guide/transformer.rst

[Original at fixed commit](https://github.com/baidu-baige/Loong-Megatron/blob/64c279afb879229cff12fb293624e3691990403f/docs/source/api-guide/transformer.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

transformer package
===================

The `transformer` package provides a customizable and configurable
implementation of the transformer model architecture. Each component
of a transformer stack, from entire layers down to individual linear
layers, can be customized by swapping in different PyTorch modules
using the "spec" parameters (see `here
<https://docs.nvidia.com/nemo-framework/user-guide/latest/nemotoolkit/nlp/nemo_megatron/mcore_customization.html>`_). The
configuration of the transformer (hidden size, number of layers,
number of attention heads, etc.) is provided via a `TransformerConfig`
object.

Submodules
----------

transformer.attention module
----------------------------

This is the entire attention portion, either self or cross attention,
of a transformer layer including the query, key, and value
projections, a "core" attention calculation (e.g. dot product
attention), and final output linear projection.

.. automodule:: core.transformer.attention
   :members:
   :undoc-members:
   :show-inheritance:

transformer.dot\_product\_attention module
------------------------------------------

This is a PyTorch-only implementation of dot product attention. A more
efficient implementation, like those provided by FlashAttention or
CUDNN's FusedAttention, are typically used when training speed is
important.

.. automodule:: core.transformer.dot_product_attention
   :members:
   :undoc-members:
   :show-inheritance:

transformer.enums module
------------------------

.. automodule:: core.transformer.enums
   :members:
   :undoc-members:
   :show-inheritance:

transformer.identity\_op module
-------------------------------

This provides a pass-through module that can be used in specs to
indicate that the operation should not be performed. For example, when
using LayerNorm with the subsequent linear layer, an IdentityOp can be
passed in as the LayerNorm module to use.

.. automodule:: core.transformer.identity_op
   :members:
   :undoc-members:
   :show-inheritance:

transformer.mlp module
----------------------

This is the entire MLP portion of the transformer layer with an input
projection, non-linearity, and output projection.

.. automodule:: core.transformer.mlp
   :members:
   :undoc-members:
   :show-inheritance:

transformer.module module
-------------------------

This provides a common base class for all modules used in the
transformer that contains some common functionality.

.. automodule:: core.transformer.module
   :members:
   :undoc-members:
   :show-inheritance:

transformer.transformer\_block module
-------------------------------------

A block, or stack, of several transformer layers. The layers can all
be the same or each can be unique.

.. automodule:: core.transformer.transformer_block
   :members:
   :undoc-members:
   :show-inheritance:

transformer.transformer\_config module
--------------------------------------

This contains all of the configuration options for the
transformer. Using a dataclass reduces code bloat by keeping all
arguments together in a dataclass instead of passing several arguments
through multiple layers of function calls.

.. automodule:: core.transformer.transformer_config
   :members:
   :undoc-members:
   :show-inheritance:

transformer.transformer\_layer module
-------------------------------------

A single standard transformer layer including attention and MLP blocks.

.. automodule:: core.transformer.transformer_layer
   :members:
   :undoc-members:
   :show-inheritance:

transformer.utils module
------------------------

Various utilities used in the transformer implementation.

.. automodule:: core.transformer.utils
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: core.transformer
   :members:
   :undoc-members:
   :show-inheritance:
