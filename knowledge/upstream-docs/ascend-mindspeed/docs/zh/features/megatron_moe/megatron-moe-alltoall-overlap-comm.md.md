---
id: doc-ascend-mindspeed-cfcfac9b64d8dc8cece7
title: Ascend/MindSpeed / docs/zh/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md
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
path: docs/zh/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md
raw_sha256: 3fa214274b1cbc0e80dc02bf90fd8dd33758d0ad3106fe94ef92387feefdd2c9
sources: []
generated_body_sha256: 2dbd69bb6736b7f4da6840abe384bab74b0ac2d9b2e7e93e2b7ed16f5d7a5629
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Megatron MoE alltoall dispatcher分支通信隐藏优化

## 背景与挑战

MoE中，存在大量的EP通信没有做通信隐藏，端到端时间占比大。这些耗时可以通过和计算交替进行，从而提高模型的训练性能。

## 解决方案

在前向过程中，使用异步通信来尽可能与计算做互相掩盖。同时，对整个计算流程进行子图切分，从而在反向过程中也进行通算并行，加速模型训练。
此特性同时支持两种alltoall dispatcher，根据alltoall与alltoall_seq这两种不同的dispatcher，进行了针对性优化。
此外，alltoall分支中，兼容了Megatron的moe-shared-expert-overlap方案，并通过更细粒度的掩盖，可做到较原生方案，性能进一步提升。

## 使用方法

打开`--moe-alltoall-overlap-comm`启用该特性。

若分支为`alltoall_seq`分支，则同时需要开启：

- `--moe-permutation-async-comm`。
- `--moe-token-dispatcher-type alltoall_seq`。
- `--moe-grouped-gemm`，目前仅支持Grouped MLP。

且在tp>1时，需要同时开启
`--moe-tp-extend-ep`

若分支为`alltoall`分支，则需要开启：

- `--moe-token-dispatcher-type alltoall`。
- `--moe-grouped-gemm`，目前仅支持Grouped MLP。
- 不支持开启`--moe-tp-extend-ep`。如使用该特性，请切换为`alltoall_seq`。

## 适用场景

适用megatron-moe，dropless方案分支时候，需要提高训练性能的场景。相较基准dispatcher场景，性能可提升10%+。
在开启`--moe-shared-expert-overlap`后，仍可提高4%以上的性能。
启动该特性会导致显存占用增加，属正常现象。此时，可搭配ZeroMemory特性调整显存使用状况。ZeroMemory介绍及设置可参考[ZeroMemory文档](megatron-moe-zero-memory.md)。
