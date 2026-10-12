---
id: doc-deepspeedai-deepspeed-f5899ca64862630de4d5
title: deepspeedai/DeepSpeed / docs/code-docs/source/schedulers.rst
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
path: docs/code-docs/source/schedulers.rst
raw_sha256: 40fbbe862f172d0139361422c5a070c98064b80cd1d9b9c0d0fe99c71190ed23
sources: []
generated_body_sha256: 42f06542ced4024530f4cf171e1cf80b0c895df275cd18b573ad103b17dec08f
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/code-docs/source/schedulers.rst

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/code-docs/source/schedulers.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Learning Rate Schedulers
=================================

DeepSpeed offers implementations of ``LRRangeTest``, ``OneCycle``, ``WarmupLR``, ``WarmupDecayLR``, ``WarmupCosineLR`` learning rate schedulers. When using a DeepSpeed's learning rate scheduler (specified in the `ds_config.json` file), DeepSpeed calls the `step()` method of the scheduler at every training step (when `model_engine.step()` is executed). When not using a DeepSpeed's learning rate scheduler:
  * if the schedule is supposed to execute at every training step, then the user can pass the scheduler to `deepspeed.initialize` when initializing the DeepSpeed engine and let DeepSpeed manage it for update or save/restore.
  * if the schedule is supposed to execute at any other interval (e.g., training epochs), then the user should NOT pass the scheduler to DeepSpeed during initialization and must manage it explicitly.

LRRangeTest
---------------------------
.. autoclass:: deepspeed.runtime.lr_schedules.LRRangeTest


OneCycle
---------------------------
.. autoclass:: deepspeed.runtime.lr_schedules.OneCycle


WarmupLR
---------------------------
.. autoclass:: deepspeed.runtime.lr_schedules.WarmupLR


WarmupDecayLR
---------------------------
.. autoclass:: deepspeed.runtime.lr_schedules.WarmupDecayLR


WarmupCosineLR
---------------------------
.. autoclass:: deepspeed.runtime.lr_schedules.WarmupCosineLR