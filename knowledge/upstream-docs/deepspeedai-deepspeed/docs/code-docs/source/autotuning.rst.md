---
id: doc-deepspeedai-deepspeed-5f90cbcafbfee43a7023
title: deepspeedai/DeepSpeed / docs/code-docs/source/autotuning.rst
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
path: docs/code-docs/source/autotuning.rst
raw_sha256: 4aab0d9a24e5bc7ecaf9a13b5e69b75a199d7f76097c7536ea9e6b1f0f820e7e
sources: []
generated_body_sha256: 27b4cb3b91ce22d06973257ee1d29288a11ee2ef6212a3627a96ceaf51ccdc93
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/code-docs/source/autotuning.rst

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/code-docs/source/autotuning.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Autotuning
==============
One pain point in model training is to figure out good performance-relevant configurations such as micro-batch size to fully utilize the hardware and achieve a high throughput number. This configuration exploring process is commonly done manually but is important since model training is repeated many times and benefits from using a good configuration. Not only is the hand-tuning process time-consuming, but the outcome is hardware-dependent. This means that a good configuration on one hardware might not be the best on another different hardware. The user thus has to hand tune the configuration again. With DeepSpeed, there are more configuration parameters that could potentially affect the training speed, thus making it more tedious to manually tune the configuration.

The DeepSpeed Autotuner mitigates this pain point and automatically discovers the optimal DeepSpeed configuration that delivers good training speed.
The Autotuner uses model information, system information, and heuristics to efficiently tune system knobs that affect compute and memory efficiencies, such as ZeRO optimization stages, micro-batch sizes, and many other ZeRO optimization configurations.
It not only reduces the time and resources users spend on tuning, but also can discover configurations better than hand-tuned methods.

Please see the `Autotuning tutorial <https://www.deepspeed.ai/tutorials/autotuning/>`_ for usage details.

Autotuner
---------------------------------------------------
.. autoclass:: deepspeed.autotuning.autotuner
   :members: