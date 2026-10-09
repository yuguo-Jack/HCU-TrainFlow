---
id: doc-volcengine-verl-1532ec3df187cd09b95a
title: verl-project/verl / docs/advance/megatron_extension.rst
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
path: docs/advance/megatron_extension.rst
raw_sha256: cf032eb488ee4c7057f8ea948f034278f4f77b52a7c6b7bb98bdd26494a5992d
sources: []
generated_body_sha256: 1e4d30518f6a8fa1c65a6e83d758246de686b5b8556e2366e29ceb776d1fd639
source_state: current-scan
---

# verl-project/verl / docs/advance/megatron_extension.rst

[Original at fixed commit](https://github.com/verl-project/verl/blob/5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d/docs/advance/megatron_extension.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Add models with the Megatron-LM backend
=========================================

Last updated: 04/25/2025.

Model
-----------


If use latest verl, we have direct support of ``GPTModel`` for Megatron backend. 
You can use the similar way of using Megatron to pretrain custom models. 
We list the steps here:

1. Find `model_initializer.py <https://github.com/verl-project/verl/blob/main/verl/models/mcore/model_initializer.py>`_
2. If your model is configurable by ``TransformerLayerSpec`` , you can
   directly use ``GPTModel``. Otherwise, Please implement a new
   ``ModelLayerSpec`` and ``ModelLayer`` here.
3. Use the right ``LayerSpec`` , ``TransformerConfig`` and ``HuggingfaceConfig`` 
   as arguments to initialize the GPTModel.
4. Return the model at last.