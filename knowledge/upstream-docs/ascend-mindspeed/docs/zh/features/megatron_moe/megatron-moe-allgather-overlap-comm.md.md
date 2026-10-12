---
id: doc-ascend-mindspeed-3ffbe4e4f9623a9763ed
title: Ascend/MindSpeed / docs/zh/features/megatron_moe/megatron-moe-allgather-overlap-comm.md
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
path: docs/zh/features/megatron_moe/megatron-moe-allgather-overlap-comm.md
raw_sha256: 36b89b661fa2f9d7f615c2669a16c3060b2f0ef8952f2bce56df1dc5c8dd5735
sources: []
generated_body_sha256: 38ace0eabc7fc29f97f51d31cfcf8f6a75e343695c2c1d327419171b8f750960
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/megatron_moe/megatron-moe-allgather-overlap-comm.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/megatron_moe/megatron-moe-allgather-overlap-comm.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Megatron MoE Allgather Dispatcher分支通信隐藏优化

## 背景与挑战

MoE中，存在大量的EP通信没有做通信隐藏，端到端时间占比大。这些耗时可以通过和计算交替进行，从而提高模型的训练性能。

## 解决方案

在前向过程中，使用异步通信来尽可能与计算做互相掩盖。同时，对整个计算流程进行子图切分，从而在反向过程中也进行通算并行，加速模型训练。此特性对allgather dispatcher进行了针对性优化。

## 使用方法

- 开启特性：添加`--moe-allgather-overlap-comm`启用该功能。
- 必选配套参数：必须同时确保开启以下三个参数：
    - `--moe-permutation-async-comm`
    - `--moe-token-dispatcher-type allgather`
    - `--moe-grouped-gemm`（注意：目前仅支持Grouped MLP）

## 使用场景

适用于megatron-moe，dropless方案分支时，在ep通信瓶颈时，需要通信隐藏ep通信的场景。

> [!NOTE]
>
> 启动该特性会导致显存占用增加，属正常现象。
