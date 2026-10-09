---
id: doc-deepspeedai-deepspeed-caac2767641dd8a47277
title: deepspeedai/DeepSpeed / docs/code-docs/source/optimizers.rst
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
path: docs/code-docs/source/optimizers.rst
raw_sha256: acab0ca2f4adf96640f839f09fd73c8b1035d5b13e0e2a23d93d5ff1876484e3
sources: []
generated_body_sha256: eb7fb3781b6241904b21fc499e122ef7de844ad348a16e94ccb3790f6d229b08
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/code-docs/source/optimizers.rst

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/code-docs/source/optimizers.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Optimizers
===================

DeepSpeed offers high-performance implementations of ``Adam`` optimizer on CPU; ``FusedAdam``, ``FusedLamb`` optimizers on GPU.

Adam (CPU)
----------------------------
.. autoclass:: deepspeed.ops.adam.DeepSpeedCPUAdam

FusedAdam (GPU)
----------------------------
.. autoclass:: deepspeed.ops.adam.FusedAdam

FusedLamb (GPU)
----------------------------
.. autoclass:: deepspeed.ops.lamb.FusedLamb