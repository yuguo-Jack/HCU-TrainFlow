---
id: doc-deepspeedai-deepspeed-4209fc6085acc26ebf72
title: deepspeedai/DeepSpeed / docs/code-docs/source/moe.rst
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
path: docs/code-docs/source/moe.rst
raw_sha256: bad5a0b90db15c4e82cef6996419e92bd054df293f83b76e3d43710891174fe8
sources: []
generated_body_sha256: e4cb8a3973c5092a13e2101af2e505492f296a6f8013b2d2e4dffffa681c13a1
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/code-docs/source/moe.rst

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/code-docs/source/moe.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Mixture of Experts (DeepSpeed MoE)
==================================

DeepSpeed provides two forms of MoE support: DeepSpeed MoE and :doc:`AutoEP
(Automatic Expert Parallelism) <autoep>`. DeepSpeed MoE is the explicit
``deepspeed.moe.layer.MoE`` API for constructing MoE layers in model code. This
page introduces the DeepSpeed MoE API.

See also the `Mixture of Experts (DeepSpeed MoE) tutorial
<https://www.deepspeed.ai/tutorials/mixture-of-experts/>`__ for training
examples and configuration details.

.. autoclass:: deepspeed.moe.layer.MoE
    :members: