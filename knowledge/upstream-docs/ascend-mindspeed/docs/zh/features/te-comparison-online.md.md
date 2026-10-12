---
id: doc-ascend-mindspeed-d672e22c47e59ebfb6ca
title: Ascend/MindSpeed / docs/zh/features/te-comparison-online.md
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
path: docs/zh/features/te-comparison-online.md
raw_sha256: fa72f721c265deec2e73e3b9c1ffe808a9d033522b5524967c4e8db6298889b7
sources: []
generated_body_sha256: f8018c768e8a9ce279db62526f4e521c1edf770d5e19b470495d7d698bb20f74
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/te-comparison-online.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/te-comparison-online.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# 低精度在线比对

## 问题分析

在模型训练中，精度问题往往难以定位。为了提高精度追踪效率，保障低精度模块可靠性，需要一种实时监控低精度计算结果的方式，同时减少问题定位的成本。

## 解决方法

低精度在线比对功能通过对比不同硬件（NPU、CPU）和不同精度（BF16）的计算结果，帮助用户实时检查低精度操作（包括 cast 和 quant_matmul）的精度差异。启用该特性后，将同时进行 NPU 和 CPU/BF16 上的计算，并输出误差值，方便用户检测潜在的精度问题。

## 使用场景

该功能适用于开启低精度训练的模型。

## 使用方法

1. 在训练脚本的参数列表中加入 `--te-comparison-with-cpu`，即开启将CPU计算结果作为精度标杆的低精度在线比对。
2. 在训练脚本的参数列表中加入 `--te-comparison-with-bf16`，即开启将BF16计算结果作为精度标杆的低精度在线比对。

## 使用效果

在低精度计算过程中，将输出每一步NPU上 cast 和 quant_matmul 操作与精度标杆（CPU 或 BF16）之间的误差。如果误差超出预设范围，将会提示错误并终止训练过程。
