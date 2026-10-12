---
id: doc-deepspeedai-deepspeed-df1d8a00627072048764
title: deepspeedai/DeepSpeed / docs/code-docs/source/flops-profiler.rst
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
path: docs/code-docs/source/flops-profiler.rst
raw_sha256: 9707dde8d248d80ad15f4f4ab7538142a8bb6508bd2c8295d28c22dea75cf813
sources: []
generated_body_sha256: feeee0558136fee2ebb8ca98652468e0ec042c59d6a5c2d781ba4313292b2596
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/code-docs/source/flops-profiler.rst

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/code-docs/source/flops-profiler.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Flops Profiler

==============

The flops profiler in DeepSpeed profiles the forward pass of a model and measures its parameters, latency, and floating point operations. The DeepSpeed flops profiler can be used with the DeepSpeed runtime or as a standalone package.

When using DeepSpeed for model training, the flops profiler can be configured in the deepspeed_config file without user code changes. To use the flops profiler outside of the DeepSpeed runtime, one can simply install DeepSpeed and import the flops_profiler package to use the APIs directly.

Please see the `Flops Profiler tutorial <https://www.deepspeed.ai/tutorials/flops-profiler/>`_ for usage details.

Flops Profiler
---------------------------------------------------

.. automodule:: deepspeed.profiling.flops_profiler.profiler
   :members:
   :show-inheritance: