---
id: doc-deepspeedai-deepspeed-b33c177d671e1b321859
title: deepspeedai/DeepSpeed / docs/code-docs/source/kernel.rst
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
path: docs/code-docs/source/kernel.rst
raw_sha256: a1925dbeda6fd99fc84de9c9417182b3bb8c6b050bee71f228a1b6142f4df7c8
sources: []
generated_body_sha256: c2395d63074a0eac0ca5721445305b954c361df84f7fb790bd7c2ca984bd69b3
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/code-docs/source/kernel.rst

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/code-docs/source/kernel.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Transformer Kernels
===================

The transformer kernel API in DeepSpeed can be used to create BERT transformer layer for
more efficient pre-training and fine-tuning, it includes the transformer layer configurations and
transformer layer module initialization.

Here we present the transformer kernel API.
Please see the `BERT pre-training tutorial <https://www.deepspeed.ai/tutorials/bert-pretraining/>`_ for usage details.

DeepSpeed Transformer Config
----------------------------
.. autoclass:: deepspeed.DeepSpeedTransformerConfig

DeepSpeed Transformer Layer
----------------------------
.. autoclass:: deepspeed.DeepSpeedTransformerLayer