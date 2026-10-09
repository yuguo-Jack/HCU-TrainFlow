---
id: doc-deepspeedai-deepspeed-823fa19620f27de5cf74
title: deepspeedai/DeepSpeed / docs/code-docs/source/monitor.rst
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
path: docs/code-docs/source/monitor.rst
raw_sha256: 62473971b380ebd58a002359bfa9802d1b7383b76546c373568e39bdf9e07fdc
sources: []
generated_body_sha256: 662b3b0a0952ad5a64fd020f8103d2cc988d9bb287393314c96c52d21273b787
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/code-docs/source/monitor.rst

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/code-docs/source/monitor.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Monitoring
==========

Deepspeed’s Monitor module can log training details into a
Tensorboard-compatible file, to WandB, or to simple CSV files. Below is an
overview of what DeepSpeed will log automatically.

.. csv-table:: Automatically Logged Data
    :header: "Field", "Description", "Condition"
    :widths: 20, 20, 10

    `Train/Samples/train_loss`,"The training loss.",None
    `Train/Samples/lr`,"The learning rate during training.",None
    `Train/Samples/loss_scale`,"The loss scale when training using `fp16`.",`fp16` must be enabled.
    `Train/Samples/elapsed_time_ms_forward`,"The global duration of the forward pass.",`flops_profiler.enabled` or `wall_clock_breakdown`.
    `Train/Samples/elapsed_time_ms_backward`,"The global duration of the forward pass.",`flops_profiler.enabled` or `wall_clock_breakdown`.
    `Train/Samples/elapsed_time_ms_backward_inner`,"The backward time that does not include the gradient reduction time. Only in cases where the gradient reduction is not overlapped, if it is overlapped then the inner time should be about the same as the entire backward time.",`flops_profiler.enabled` or `wall_clock_breakdown`.
    `Train/Samples/elapsed_time_ms_backward_allreduce`,"The global duration of the allreduce operation.",`flops_profiler.enabled` or `wall_clock_breakdown`.
    `Train/Samples/elapsed_time_ms_step`,"The optimizer step time.",`flops_profiler.enabled` or `wall_clock_breakdown`.

TensorBoard
-----------
.. _TensorBoardConfig:
.. autopydantic_model:: deepspeed.monitor.config.TensorBoardConfig

WandB
-----
.. _WandbConfig:
.. autopydantic_model:: deepspeed.monitor.config.WandbConfig

Comet
-----
.. _CometConfig:
.. autopydantic_model:: deepspeed.monitor.config.CometConfig

CSV Monitor
-----------
.. _CSVConfig:
.. autopydantic_model:: deepspeed.monitor.config.CSVConfig