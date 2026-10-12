---
id: doc-ascend-mindspeed-1f49d9b308b331f97806
title: Ascend/MindSpeed / docs/zh/features/unaligned_linear.md
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
path: docs/zh/features/unaligned_linear.md
raw_sha256: 3c03bcdb1e5f25a68ec4fa35ad084ac237652762b50dbfb33d5016cebcf08e33
sources: []
generated_body_sha256: 5723f315dc5a016b7627b32714a96f68623f297b0ac303c4ed80547f3fd08f83
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/unaligned_linear.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/unaligned_linear.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# unaligned linear 非对齐线性层

## 背景与挑战

类Megatron-LM框架已成为大模型训练的主流方案之一，TP（Tensor Parallelism，张量并行）是大模型训练的基本并行范式，该范式在部分场景仍存在不足，例如要求大模型的注意力头数及序列长度要能整除TP，不满足条件将在参数校验中抛出异常。本特性提供了一种注意力头数及序列长度不能整除TP的解决方案。

## 解决方案

- 序列长度不能整除TP：和pad方案（将序列长度pad到TP的整数倍）不同，该方案通过序列分配策略来解决，小于 **(seq_len%tp_size)** 的tp卡分配 **(seq_len//tp_size+1)** 序列长度，其他分配 **(seq_len//tp_size)** 序列长度，例如seq_len=1026，tp_size=4，tp0和tp1分配的序列长度为257，tp2和tp3分配的序列长度为256。

- 注意力头数不能整除TP：对于MHA结构模型，小于 **(num_attention_heads%tp_size)** 的tp卡分配 **(num_attention_heads//tp_size+1)** 个注意力头，其他卡分配 **(num_attention_heads//tp_size)** 注意力头，例如num_attention_heads=25，tp_size=4，tp0分配的注意力头为7个，tp1、tp2和tp3分配的注意力头均为6个。值得注意的是，模型的注意力相关权重TP切分和头数相关，假设hidden_size=3200，qkv_weight大小为(9600,3200)，dense_weight大小为(3200,3200)，tp0的qkv权重大小为(2688,3200)，dense权重大小为(3200,896)，tp1、tp2和tp3的qkv权重大小为(2304, 3200)，dense权重大小为(3200,768)。注意，对于GQA结构模型，权重切分和注意力头切分按num_query_groups比例分配。

## 使用场景

序列长度或注意力头数不能整除TP的场景可以使用该特性。

## 使用方法

在模型参数中添加`--unaligned-linear`参数。

> [!NOTE]
>
> - 非对齐的线性层会引起各TP的负载不均衡。
> - 该特性不支持mc2、2D张量并行及CP特性(要求TP*CP能被注意力头数整除)等。
> - 特殊的模型结构需要特殊适配该特性，当前已适配MHA、GQA结构，暂不支持MOE、MLA等结构。

启用非对齐线性层，需要在训练脚本中加入以下参数：

```bash
# 开启非对齐线性层
--unaligned-linear
```

## 使用效果

- 补充功能场景：补充注意力头数、序列长度不能被TP整除的场景。
- 潜在性能影响：各TP处理的注意力头数、序列长度不一致，负载不均衡，建议模型结构设计时考虑该情况。

综上所述，该特性是为了完善TP(张量并行)场景下的限制约束，特性本身会带来负载不均衡的性能影响，所以在模型设计和超参优化时注意这一影响。

> [!NOTE]
>
> 非对齐线性层不支持在legacy分支使用，即不支持和`--use-legacy-models`同时开启。
