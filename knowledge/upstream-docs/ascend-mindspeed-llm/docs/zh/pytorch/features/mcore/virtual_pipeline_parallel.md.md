---
id: doc-ascend-mindspeed-llm-63cd63863a210069e46f
title: Ascend/MindSpeed-LLM / docs/zh/pytorch/features/mcore/virtual_pipeline_parallel.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: 2fed626696175480ae1ab3342a94017301a25209
path: docs/zh/pytorch/features/mcore/virtual_pipeline_parallel.md
raw_sha256: 59fd6081256efe70bfbfbbbf159cace1da8da3f39366e5c6abcad47b92121472
sources: []
generated_body_sha256: 8c06f8fb0fca6528bf5407aa29ee9172b7c3202e78b42169ff9975578f9ef610
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/zh/pytorch/features/mcore/virtual_pipeline_parallel.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/zh/pytorch/features/mcore/virtual_pipeline_parallel.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# 虚拟流水线并行

## 问题分析

PipeDream 流水线并行切分粒度过大，运行过程中仍然有许多空泡（bubble），计算资源利用率仍有提高空间。

## 解决方案

将计算进一步细分，减少空泡。

### 解决思路

在设备数量不变的情况下，分出更多的流水线阶段，以更多的通信量，换取空泡比率降低。

![虚拟流水线并行前后向调度示意图](../../figures/virtual_pipeline_parallel/virtual-pipeline.png)

[原文链接](https://arxiv.org/abs/2104.04473?utm_source=chatgpt.com)

为了方便理解，举一个例子：假设模型层数为 16，张量并行大小为 1，流水线并行大小为 4，虚拟流水线并行大小为 2。模型会被分为 4 * 2 = 8 个阶段，每个阶段 16 / 8 = 2 层。

    Device 0: [1, 2] [9, 10]
    Device 1: [3, 4] [11, 12]
    Device 2: [5, 6] [13, 14]
    Device 3: [7, 8] [15, 16]

前向的顺序为 device 0 -> device 1 -> device 2 -> device 3 -> device 0 -> device 1 -> device 2 -> device 3。

## 使用场景

想要进一步减小空泡比率，提升性能。

## 使用方法

设置 `--num-layers-per-virtual-pipeline-stage N`，表示每个阶段的层数。要求模型的总层数满足 `L % N == 0`。

## 使用效果

空泡比率进一步减小。

## 注意事项

Megatron 虚拟流水线并行（VPP）会影响权重切分方式，保存、加载权重时需保证 VPP 配置一致，才能正常加载。
