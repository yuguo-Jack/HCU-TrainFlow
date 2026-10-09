---
id: doc-deepspeedai-deepspeed-7043ba9f5058705c72c4
title: deepspeedai/DeepSpeed / docs/_tutorials/zeropp.md
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
path: docs/_tutorials/zeropp.md
raw_sha256: 0d69a27046647010a2674bd91e7005bbd94f1936be6c728726968f977238282a
sources: []
generated_body_sha256: 4017ecac18fae005f3812d2647f7a35e374a82d50812c829679a713e3408d78e
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/_tutorials/zeropp.md

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/_tutorials/zeropp.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
title: "ZeRO++"
tags: training ZeRO communication-efficiency large-model
---

ZeRO++ is a system of communication optimization strategies built on top of [ZeRO](/tutorials/zero/) to offer unmatched efficiency for large model training regardless of the scale or cross-device bandwidth constraints. Read our [ZeRO++ blog](https://www.microsoft.com/en-us/research/blog/deepspeed-zero-a-leap-in-speed-for-llm-and-chat-model-training-with-4x-less-communication/) and [paper](https://arxiv.org/pdf/2306.10209.pdf) to learn more!

We recommend that you read the tutorials on [Getting Started](/getting-started/), [ZeRO](/tutorials/zero/)  and [Megatron-DeepSpeed](/tutorials/megatron/) before stepping through this tutorial.


## Three Components of ZeRO++
ZeRO++ consists of three key designs, namely quantized weights (*qwZ*), hiearchical partitioning ZeRO (*hpZ*), and quantized gradients (*qgZ*):
 - *qwZ* applies block-based quantization to reduce ZeRO parameter all-gather communication volume by half from FP16 to INT8.
 - *hpZ* eliminates inter-node backward parameter all-gather communication through data remapping and recomputation.
 - *qgZ* replaces gradients allreduce collective with a new communication efficient all-to-all based quantized gradient averaging.

Collectively, the three optimization reduces communication volume by 4x compared to ZeRO baseline. Each of the three components can be enabled independent of each other and collectively as a group as described in the next section.

## Training Environment

For this tutorial, we will configure a 18 billion parameter GPT-2 model using the DeepSpeed [Megatron-DeepSpeed](https://github.com/deepspeedai/Megatron-DeepSpeed/tree/master/) GPT-2 code. We will use 4 nodes of 16x [NVIDIA Tesla V100-SXM3 Tensor Core GPU](https://www.nvidia.com/en-us/data-center/v100/) with 32GB RAM per node for this exercise.


## Training a 18B parameter GPT-2 with ZeRO++
There are no change needed to the user code. However, since ZeRO++ extends ZeRO Stage 3 (ZeRO-3), appropriate flags need to be added to activate each or all of the three ZeRO++ communication collective optimizations. The three flags and their meanings and defaults and preferred values:

 - zero_quantized_weights: Boolean indicating whether to use quantized zero weights (*qwZ*), default is false.
 - zero_hpz_partition_size: number of ranks in *hpZ* (secondary partition) group, default is 1 meaning no hpZ, ideal is number of ranks (gpus) per node.
 - zero_quantized_gradients: Boolean indicating whether to use quantized zero gradients (*qgZ*), default is false.


### DeepSpeed Configuration Changes
An example snippet of deepspeed configurations with all three ZeRO++ optimization enable is shown below:
```json
{
    "zero_optimization": {
        "stage": 3,
        "reduce_bucket_size": 10000000,
        "reduce_scatter": true,

        "zero_quantized_weights": true,
        "zero_hpz_partition_size": 16,
        "zero_quantized_gradients": true,

        "contiguous_gradients": true,
        "overlap_comm": true
    }
}
```

Finally, to launch your experiment, issue the following command:

```python
       deepspeed pretrain_zeropp_gpt.py \
       --tensor-model-parallel-size 1 \
       --pipeline-model-parallel-size 1 \
       --num-layers 40 \
       --hidden-size 6144 \
       --seq-length 512 \
       --num-attention-heads 32 \
       --batch-size 1 \
       --zero-stage 3 \
       --deepspeed_config ds_zeropp_config.json \
       --deepspeed-activation-checkpointing \
       --fp16 \
       --checkpoint-activations
```

See more details on Megatron-DeepSpeed [tutorial](/tutorials/megatron/) examples on how to launch a Megatron-DeepSpeed job.


Here is a screenshots of the training log for both ZeRO baseline and ZeRO++:

ZeRO baseline
<a href="/assets/images/zeropp/ZeRO-baseline.png">
<img src="/assets/images/zeropp/ZeRO-baseline.png">
</a>

ZeRO++
<a href="/assets/images/zeropp/ZeROpp.png">
<img src="/assets/images/zeropp/ZeROpp.png">
</a>

Congratulations! You have completed the ZeRO++ tutorial.