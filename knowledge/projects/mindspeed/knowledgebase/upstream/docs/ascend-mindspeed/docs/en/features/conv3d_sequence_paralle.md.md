---
id: doc-ascend-mindspeed-ba582b009608d468af43
title: Ascend/MindSpeed / docs/en/features/conv3d_sequence_paralle.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed
commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
path: docs/en/features/conv3d_sequence_paralle.md
raw_sha256: 360b808defc4b6dd726409a03384540d39e55e249017b9f2f802114af6f374d4
sources: []
generated_body_sha256: 1009437375628fa9069c8a36e5e9b0f382116af71a9e94558b36c31dd7e1afaa
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/conv3d_sequence_paralle.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/conv3d_sequence_paralle.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# conv3d Sequence Parallelism

## Background and Challenges

In model architectures for fields such as multimodal and machine vision, conv3d modules are often used for 3D convolution operations on feature maps. In large models, the time consumed by convolution operations increases as the scale of the feature map grows.
Since the convolution process for each block of the feature map is executed sequentially, there is actually no dependency constraint on the execution order among the blocks. In distributed training, 3D convolution operations need to be parallelized to improve convolution speed.

## Solution

Construct a `Conv3DSequenceParallel` class that splits the input feature map along the depth dimension of the convolution kernel and then performs parallel convolution.

- **Forward process**:
 Construct the `Conv3DSequenceParallel` class, split the input feature map along the depth dimension of the convolution kernel, distribute it to different process groups for conv3d 3D convolution operations, and perform a gather operation on the convolution results before outputting them to downstream modules.<br>
- **Backward process**:
 The `Conv3DSequenceParallel` class performs a split operation on the gradients obtained from downstream backward propagation, splitting the gradients along the depth dimension, distributing them to parallel 3D convolution modules for backward propagation, and then performing a gather operation on the backward gradients from the parallel 3D convolution modules before outputting them to upstream modules.
![conv3d sequence parallelism](../figures/conv3d_sequence_parallel_en.png)

## Application Scenario

Applicable to training models that contain conv3d (non-padding mode) modules.

## Usage

Replace the original conv3d module with `Conv3DSequenceParallel` and specify the relevant parameters to achieve parallel acceleration.<br>
The `Conv3DSequenceParallel` module interface is as follows:<br>

`Conv3DSequenceParallel(pg, in_channels, out_channels, kernel_size, stride, dilation, bias, param_async, dtype, sp_size)`

- `pg`: Required input. Data type: `torch.distributed.ProcessGroup`. Specifies the communication process group.
- `in_channels`: Required input. Data type: `int`. Specifies the number of input channels.
- `out_channels`: Required input. Data type: `int`. Specifies the number of output channels.
- `kernel_size`: Optional attribute. Data type: `tuple(int, int, int)`. Default value: `(1, 1, 1)`. Specifies the convolution kernel size.
- `stride`: Optional attribute. Data type: `tuple(int, int, int)`. Default value: `(1, 1, 1)`. Specifies the convolution stride size for each dimension.
- `dilation`: Optional attribute. Data type: `int` or `tuple(int, int, int)`. Default value: `1`. Specifies the dilation rate.
- `bias`: Optional attribute. Data type: `bool`. Default value: `True`. Indicates whether bias is enabled.
- `param_async`: Optional attribute. Data type: `bool`. Default value: `False`. Indicates whether asynchronous parameter communication is enabled.
- `dtype`: Optional attribute. Data type: `torch.dtype`. Default value: `torch.bfloat16`. Specifies the data type of the convolution layer.
- `sp_size`: Optional attribute. Data type: `int`. Default value: `1`. Specifies the sequence parallel size.

## Effects

Distributes the convolution operations of each convolution region to process groups for parallel execution, improving the efficiency of 3D convolution.

## Notes

The `Conv3DSequenceParallel` module does not support padding mode. Therefore, conv3d modules that use padding cannot be replaced with the `Conv3DSequenceParallel` module.
