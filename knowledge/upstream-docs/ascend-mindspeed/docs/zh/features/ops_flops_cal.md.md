---
id: doc-ascend-mindspeed-e97c52b530e9369becf7
title: Ascend/MindSpeed / docs/zh/features/ops_flops_cal.md
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
path: docs/zh/features/ops_flops_cal.md
raw_sha256: e50079a9444fa5d270260cadc2ac51b03c184d62c845ffd3073215cde6d7fd6c
sources: []
generated_body_sha256: 4a2f102113d2cd38f704cd0211ae549fd8a6aba960bfa616863547772b8acced
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/ops_flops_cal.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/ops_flops_cal.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# TFLOPS计算

## 背景与挑战

当前大模型在计算MFU时，依赖框架理论打印值TFLOPS/有效算力得到，但是理论值计算适用于一般模型，如果针对模型结构进行变动，将不再适用，同时HFU的计算目前需要手动计算。

## 解决方案

提供接口可以统计所有涉及MatMul计算的算子的浮点计算次数，同时能统计到模型正反向训练以及重计算的总浮点计算次数。

目前支持的涉及MatMul的算子有MatMul、BatchMatMul、FlashAttention、MC2相关融合算子、CoC相关融合算子、GEMM相关融合算子及matmul_add_fp32融合算子。

## 使用方法

设置`--op-cal-tflops`参数即可启用该统计功能。

## 使用效果

通过打印值`actual throughput per NPU (TFLOP/s/NPU)`和`actual throughput per NPU with recompute (TFLOP/s/NPU)`可以方便计算MFU和HFU。

> [!NOTE]
>
> - 由于此功能统计的是各卡的TFLOPS信息，在CP/EP/PP场景下，各卡计算量不同，因此在最后需要汇总各卡的信息进行平均，额外增加一个all_reduce通信。
> - 使用此功能由于会增加一个额外通信以及计算各算子的浮点计算次数，可能影响性能。
> - 由于在Ring Attention长序列并行方案中，在causal场景下，由于算法优化缘故，会有部分计算减少，因此会导致理论值和实际统计值不符合的现象，理论计算上FA的计算减少值为`(CP-1)/(2×CP)`。
> - 此功能暂不支持MLA场景。
