---
id: doc-baidu-baige-loongforge-db077ffc5ba26b660280
title: baidu-baige/LoongForge / docs/source_zh/features/moe_all2all_overlap.md
engine: loongforge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: baidu-baige/LoongForge
commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
path: docs/source_zh/features/moe_all2all_overlap.md
raw_sha256: b60d5088ebca76fd12111619c3e47b3b934c25b36136329461073f9ae4baacca
sources: []
generated_body_sha256: 47353d2ba9dd43a21e05f1716e75ae20d5a54b01dc2890b5520a38d0175998e9
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source_zh/features/moe_all2all_overlap.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source_zh/features/moe_all2all_overlap.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# MoE All2All 重叠
LoongForge 为 MoE 模型提供面向通信的优化。通过添加相应的 Megatron 启动参数，专家并行（EP）中的 All-to-All 通信可以与计算重叠，实现最佳训练吞吐量。

---

## 1. 1F1B A2A 重叠

在 MoE 训练中，EP 引起的 All-to-All 通常是主要瓶颈之一。受 DSv3 DualPipe 启发，本框架在时间轴上将不同微批次的前向/反向计算与 EP All-to-All 交织进行。代价高昂的 EP 通信因此被隐藏在计算之后，大大减少了其对整体吞吐量的影响。

### 特性
* 通过微批次重叠隐藏 All-to-All 通信
* 拆分权重梯度和激活梯度传输，以获得更好的流水线并行重叠
* 支持 FP8 训练

### 使用方法
添加以下启动参数：

```bash
--overlap-moe-expert-parallel-comm \
--delay-wgrad-compute
```

前提条件：必须启用 Interleave 1F1B 调度。

为获得最佳重叠效果，建议：

```bash
export CUDA_DEVICE_MAX_CONNECTIONS=32
```
*（这可能会略微影响 TP 重叠；请根据 TP 还是 EP 占据通信主导来选择。）*

---

## 2. 细粒度激活卸载

在长上下文训练中，激活内存随序列长度快速增长，很快成为限制因素。常见的补救方法是将张量并行（TP）与**全层重计算**结合以压缩激活占用。
然而，1F1B A2A 重叠策略依赖于相邻批次的逐模块交织，使得传统的全层重计算不兼容。

为解决此问题，框架引入了**模块级选择性重计算加细粒度激活卸载**，在保留重叠调度的同时近似全层重计算的内存节省（见图）。
![offload_stream](../../assets/images/offload.png)

### 特性
* 激活卸载与重新加载隐藏在计算之后
* 张量级卸载粒度
* 支持 FP8 训练

### 使用方法
启用**模块级选择性重计算**：

```bash
--recompute-granularity selective \
--recompute-modules a2a_overlap_attn a2a_overlap_post_attn a2a_overlap_mlp
```

启用**张量级激活卸载**：

```bash
--fine-grained-activation-offloading \
--offload-tensors dispatched_input pre_mlp_layernorm_output
```

此外，将每个进程绑定到其 GPU 所在的 NUMA 节点，以提高 D2H/H2D 带宽：

```bash
--bindpcie
```
