---
id: doc-ascend-mindspeed-8662240af6256dcb3821
title: Ascend/MindSpeed / docs/en/features/multi_parameter_pipeline.md
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
path: docs/en/features/multi_parameter_pipeline.md
raw_sha256: 341aa9cdfb5a40f42a8c32a0afb9c41bd448a8655b68141451dce537c93b77ce
sources: []
generated_body_sha256: 9a80af60d38920150e248354f5f83adfa961b37d93473578eb64679345b9ade8
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/features/multi_parameter_pipeline.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/multi_parameter_pipeline.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Multi-Parameter Pipeline

## Background and Challenges

In distributed training of large deep learning models, Pipeline Parallelism (PP) is a technique that splits a model into multiple stages and executes them concurrently on different devices to improve efficiency. However, when introducing multi-parameter passing support in multimodal scenarios, PP faces specific challenges:

- Communication design: Traditional PP typically involves the transmission of only a single tensor, but in the case of multi-parameter passing, the transfer of multiple variables must be handled. This not only increases communication complexity but also requires precise management of attributes such as shape and dtype for each variable. These attributes are often closely tied to the overall model architecture and are highly customized.
- Variable passing in forward propagation: During forward computation, it is necessary not only to correctly pass multiple variables according to the defined shapes but also to ensure that the data format received by each stage meets expectations, which imposes higher requirements on data flow design.
- Backward propagation computation extension: For backward propagation, in addition to gradient computation for the first output, corresponding operations must be performed on all other outputs to ensure the completeness and accuracy of the entire training process.

## Solution

To address the above challenges, the following solutions are designed to enable PP to effectively support multi-parameter passing:

- Optimized communication mechanism: An efficient communication mechanism is developed to support data transmission of multiple types and formats. Transmission parameters are customized for the specific requirements of each stage.
- Enhanced gradient computation logic: The backward propagation algorithm is improved so that the system can automatically identify and process gradient information from multiple outputs, ensuring that each output participates in the final weight update.

## Application Scenario

This feature is designed for large-scale neural network training tasks that involve processing extensive multimodal data — including text, images, and audio — where pipeline parallelism requires passing multiple parameters across stages.

## Usage

> [!NOTE]
>
> Users need to modify the `args.pipeline_tensor_shapes` value in the `validate_args` function within the `mindspeed/features_manager/pipeline_parallel/multi_parameter.py` module to match the tensor transmission of the actual model pipeline stages, including tensor dimensions (Shape) and data types (Dtype).
> Incompatible with `--moe-fb-overlap` and `dualpipev`.

To enable this feature, add the following parameters in the training script:

- Support for PP scenarios

```shell
# PP >= 2
--pipeline-model-parallel-size ${PP} \
--use-multiparameter-pipeline-model-parallel \
```

- Support for VPP scenarios

```shell
# PP >= 2, num-layers-per-virtual-pipeline-stage不为None
--pipeline-model-parallel-size ${PP} \
--num-layers-per-virtual-pipeline-stage 1 \
--use-multiparameter-pipeline-model-parallel \
```

## Effects

With PP multi-parameter support, you can handle complex multimodal data more flexibly while maintaining high communication efficiency.
