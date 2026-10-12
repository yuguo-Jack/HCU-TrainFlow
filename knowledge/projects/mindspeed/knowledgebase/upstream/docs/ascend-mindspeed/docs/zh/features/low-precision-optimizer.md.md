---
id: doc-ascend-mindspeed-f5e5632a12d6b436d898
title: Ascend/MindSpeed / docs/zh/features/low-precision-optimizer.md
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
path: docs/zh/features/low-precision-optimizer.md
raw_sha256: 13a5c56eb1edaa4b40845334236549a11fa6ddebdf67e5b04fb40b8593b6212b
sources: []
generated_body_sha256: d5a25ececf617953cc338c378c52b9a97a63a52c0cbd6e6d78d19636d83f0512
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/low-precision-optimizer.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/low-precision-optimizer.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# 低精度优化器

## 问题分析

大模型训练场景中，Adam类优化器在训练过程中会使用FP32全精度数据类型持续保存参数副本，梯度和优化器的一二阶动量，造成静态内存占用较大。

![Adam Optimizer Diagram](../figures/adam_optimizer.png)

## 解决方案

分别量化压缩优化器中保存的数据至低精度，以降低内存占用：

1. 将优化器内动量量化为E4M3格式的FP8或HiF8或MXFP8数据类型，降低动量内存占用。
2. 将梯度量化为半精度FP16，降低梯度内存占用。
3. 适配已有的参数副本复用算法，降低参数副本内存占用。

![Low Precision Optimizer Diagram](../figures/low_precision_optimizer.png)

在优化器更新参数前，需要先将被量化的数据反量化到 FP32 以保证计算精度，计算更新完成后再量化到低精度，计算流程如下图所示：

![Low Precision Optimizer Workflow Diagram](../figures/low_precision_optimizer_workflow.png)

## 使用方法

设置`--quant-states <fp8|hif8|mxfp8>`，开启优化器动量量化，量化数据类型可选`fp8`, `hif8`, `mxfp8`

设置`--quant-grads`，开启梯度量化压缩，梯度由FP32数据类型量化为FP16

兼容`reuse-fp32-param`特性

## 使用效果

降低优化器静态内存开销。

## 使用限制

1. 梯度量化压缩`--quant-grads`不支持GEMM梯度累加融合`--gemm-gradient-accumulation-fusion`。需要启用`--no-gradient-accumulation-fusion`来关闭梯度累加融合
2. 梯度量化压缩`--quant-grads`及动量量化压缩`--quant-states`不支持`--swap-optimizer`。若要使用低精度优化器，需要关闭`--swap-optimizer`特性
