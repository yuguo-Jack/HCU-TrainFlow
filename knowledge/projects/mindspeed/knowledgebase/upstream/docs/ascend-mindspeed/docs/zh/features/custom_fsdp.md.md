---
id: doc-ascend-mindspeed-88b61feaa0d62d4dce62
title: Ascend/MindSpeed / docs/zh/features/custom_fsdp.md
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
path: docs/zh/features/custom_fsdp.md
raw_sha256: 747aec3a9183acb5f07c06b2c02ee886e190f43cf5539b7224cedf0f0a4e20eb
sources: []
generated_body_sha256: 4c655ae17e6755ff75b348273bf2062b356bba3ee5edf3c6d81f1de37e1cb043
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/custom_fsdp.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/custom_fsdp.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Megatron 全分片数据并行（Fully Sharded Data Parallel, FSDP）

## 背景与挑战

随着大模型权重增加，需要进一步提高显存利用效率。之前的ZeRO-1操作只对优化器的状态在DP域内进行切分，但是对模型权重和梯度并未做切分。这使得模型权重和梯度占用静态显存的主要部分。FSDP能将权重和梯度也在DP域内切分，从而进一步降低静态显存的大小。

## 解决方案

令每个DP rank只含参数的分片，在每一块权重前向传播前，在DP域内做All Gather，前向结束后释放得到的权重，仅保留分片。在反向前先All Gather，获得完整的权重，反向后做Reduce Scatter，对所有DP rank的梯度进行加和，同时只保留该DP rank对应的部分分片。

## 使用场景

在DP大于1时，模型权重占显存较多，想要进一步切分权重和梯度以节省显存。

## 使用方法

1. 为了开启全分片数据并行，需要加入以下配置：

    ```bash
    --use-custom-fsdp
    --data-parallel-sharding-strategy optim_grads_params
    --no-gradient-accumulation-fusion
    --use-distributed-optimizer
    ```

2. 需要关闭CUDA_DEVICE_MAX_CONNECTIONS。

    ```bash
    unset CUDA_DEVICE_MAX_CONNECTIONS
    ```

## 使用效果

模型和权重被进一步切分，显存下降。但是因为每次前向反向都新增了通信，性能会下降。

> [!NOTE]
>
> MindSpeed适配该特性的基本功能，不建议与仓内其他特性组合，使用方法请[参考脚本](../../../tests_extend/system_tests/feature_tests/custom_fsdp.sh)。
