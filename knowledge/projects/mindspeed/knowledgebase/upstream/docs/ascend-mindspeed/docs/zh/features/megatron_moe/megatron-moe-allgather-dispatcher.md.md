---
id: doc-ascend-mindspeed-779fb56736d8b9da09cd
title: Ascend/MindSpeed / docs/zh/features/megatron_moe/megatron-moe-allgather-dispatcher.md
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
path: docs/zh/features/megatron_moe/megatron-moe-allgather-dispatcher.md
raw_sha256: be4ebaf90cfdaed3ac5050c2b4ba1539f9de0bb7d4b5c1c16334d15cca66c50c
sources: []
generated_body_sha256: e6b11a60ac43cff87a586709d0d4d85cb7c8c36d080cbdb70404f665b5e09ab1
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/megatron_moe/megatron-moe-allgather-dispatcher.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/megatron_moe/megatron-moe-allgather-dispatcher.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Allgather Dispatcher 分支优化

## 背景与挑战

**gather & scatter 算子替换**

在Megatron MoE中的Allgather分支，存在使用gather/scatter操作。gather/scatter功能为沿dim轴根据索引逐元素进行取值/赋值操作，此操作会有大量的随机地址，对性能造成巨大影响。

在Megatron MoE中对gather/scatter的调用主要是以下调用方式，通过对index做expand操作对维度进行扩展，再通过扩展后index对hidden_states进行逐元素取值/赋值。

```python
self.global_local_map = global_local_map.view(-1, 1).expand(-1, hidden_states.shape[-1])
local_hidden_states = torch.gather(global_hidden_states, 0, self.global_local_map)
```

**异步通信**

在Allgather dispatcher分支中，permute函数开头会分别对hidden_states、max_ind、max_prob三个数据做allgather通信，这些操作为串行操作，但各计算任务之间并非串行依赖关系。

## 解决方案

**gather & scatter 算子替换**

由于index是通过expand进行扩展的，因此它的每一行中的内容都是一致的，所以无需使用gather/scatter进行逐元素的操作，可通过index算子以及indexput算子进行逐行操作，对gather/scatter进行等价替换。

**异步通信**

通过对通信任务进行重新排序，并使用async=True参数进行异步下发，达到计算和通信并行的目的。

## 使用场景

本优化策略适用于部署了Mcore MoE（Mixture of Experts）架构的深度学习模型，并开启`--moe-token-dispatcher-type allgather`。

## 使用方法

开启参数`--moe-permutation-async-comm`。

## 使用效果

根据实际测试数据显示，类DeepSeek-V2的MoE模型，采用上述优化措施后，端到端训练吞吐提升约10%，相同训练步数下的墙钟时间相应缩短。
