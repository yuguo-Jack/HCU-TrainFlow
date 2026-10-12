---
id: doc-deepspeedai-deepspeed-a6e55db2a81f488a40a3
title: deepspeedai/DeepSpeed / docs/code-docs/source/model-checkpointing.rst
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
path: docs/code-docs/source/model-checkpointing.rst
raw_sha256: 36337931a30a724fa5847c909ec5fead0134302a19278e852ad4c0ea60a46884
sources: []
generated_body_sha256: efb8a8b9b14293e0bf0e6acedc2c1dd797295822326b00e349019443c66fbefe
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/code-docs/source/model-checkpointing.rst

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/code-docs/source/model-checkpointing.rst)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

Model Checkpointing
===================

DeepSpeed provides routines for checkpointing model state during training.

Loading Training Checkpoints
----------------------------
.. autofunction:: deepspeed.DeepSpeedEngine.load_checkpoint

Saving Training Checkpoints
---------------------------
.. autofunction:: deepspeed.DeepSpeedEngine.save_checkpoint


ZeRO Checkpoint fp32 Weights Recovery
-------------------------------------

DeepSpeed provides routines for extracting fp32 weights from the saved ZeRO checkpoint's optimizer states.

.. autofunction:: deepspeed.utils.zero_to_fp32.get_fp32_state_dict_from_zero_checkpoint

.. autofunction:: deepspeed.utils.zero_to_fp32.load_state_dict_from_zero_checkpoint

.. autofunction:: deepspeed.utils.zero_to_fp32.convert_zero_checkpoint_to_fp32_state_dict

.. autofunction:: deepspeed.utils.zero_to_fp32.convert_zero_checkpoint_to_state_dict


Avoiding ZeRO Checkpoint Bloat
------------------------------
ZeRO stage 1 and 2 checkpoints created using ``torch.save()`` can sometimes be larger than expected. This bloat
is caused by the interaction of ZeRO's tensor flattening and torch's tensor `storage management <https://pytorch.org/docs/stable/notes/serialization.html#preserve-storage-sharing>`_ .
You can avoid this problem by using the ``clone_tensors_for_torch_save`` utility of DeepSpeed as illustrated below.

.. autofunction:: deepspeed.checkpoint.utils.clone_tensors_for_torch_save

The following code snippet illustrates this functionality for creating a HuggingFace model checkpoint:

.. code-block:: python

    ds_config = {
     ...
    }
    model = AutoModelForCausalLM.from_pretrained("facebook/opt-13b", torch_dtype=torch.float16)
    ds_engine, _, _, _ = deepspeed.initialize(model=model, config_params=ds_config)
    lean_state_dict = deepspeed.checkpoint.utils.clone_tensors_for_torch_save(ds_engine.module.state_dict())
    ds_engine.module.save_pretrained("lean_after", state_dict=lean_state_dict)



Universal Checkpoints (under development)
------------------------------------------
Parallelism techniques such as ZeRO data parallelism (DP), Tensor parallelism (TP), Pipeline parallelism (TP), which shard model and/or
optimizer states make it difficult to resume training with a checkpoint that was created on a different number of GPUs. DeepSpeed provides the
Universal Checkpoint mechanism to address this problem. Universal Checkpoints give users the flexibility of changing the number of GPUs when training
with 3D (TP, PP, and DP) parallelism, and enables more efficient use of elastic training hardware. The easiest way to get started with
using Universal Checkpoints is to consult the `Megatron-DeepSpeed <https://github.com/deepspeedai/Megatron-DeepSpeed/blob/main/examples_deepspeed/universal_checkpointing/README.md>`_
and `BLOOM <https://github.com/bigscience-workshop/bigscience/blob/master/train/tr11-176B-ml/README.md#checkpoint-reshaping>`_ examples.