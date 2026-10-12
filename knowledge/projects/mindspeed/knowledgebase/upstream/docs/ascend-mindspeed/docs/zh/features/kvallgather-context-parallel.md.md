---
id: doc-ascend-mindspeed-7bb982fd94757dd29b05
title: Ascend/MindSpeed / docs/zh/features/kvallgather-context-parallel.md
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
path: docs/zh/features/kvallgather-context-parallel.md
raw_sha256: b87c036e9ee98ba4fcf433fda998c144bbbc6bfe35eea748e94a12e674146f8e
sources: []
generated_body_sha256: 4b2cfdddbe60761a9e65e48a21e2c5004dcee7a00534a68b2ceffc13592f1e6c
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/kvallgather-context-parallel.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/kvallgather-context-parallel.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# KVAllGather长序列并行

## 背景与挑战

从生成式AI到科研模型，长序列训练正在变得非常重要。 在生成式AI领域，会话式AI、长文档摘要和视频生成等任务都需要在空间和时间层面对长上下文进行推理。 同样，章节和书籍级别的摘要（数万甚至数十万字）在会话式AI和摘要任务中也非常重要。现有的数据、张量和流水线等并行方法无法在序列维度进行切分。当序列维度(S)增长时，训练内存开销会以 $O$($S^2$) 的速度增长。因此需要针对长序列场景进行特定的优化解决长训练场景的训练需求。

## 解决方案

在KVAllGather长序列并行方案中，各计算设备首先在序列维度上分别持有不同片段的数据样本。随后，在注意力计算开始前，通过对已分片的key和value执行all-gather通信操作，使每个设备都能获取完整的key和value序列。最后，每个设备利用本地的query与完整的key、value进行注意力计算，得到对应的输出结果。

更多关于KVAllGather长序列并行方案的细节请参见原文：

> Section 3.3.2 of "The Llama 3 Herd of Models" <https://arxiv.org/abs/2407.21783>

## 使用场景

KVAllGather长序列并行方案具有良好的通用性，能够灵活支持各类attention mask，在实际应用中受到的约束较少。

在GQA（Grouped-Query Attention）、MQA（Multi-Query Attention）等场景下，由于对key和value进行all-gather通信所需的时间远少于整体计算时间，因此该方案带来的收益更为显著。

该方案可与FlashAttention完全兼容，目前已默认启用FlashAttention进行加速计算。

## 使用方法

| 重要参数 | 参数说明 |
| ---------------------------------------------------- | --------------------------------------------------------- |
| --context-parallel-size [int] | 开启CP对应的数量，默认为1（不开启并行），需设置大于1才会开启并行，根据用户需求配置。 |
| --context-parallel-algo kvallgather_cp_algo | 长序列并行算法选项，设置为`kvallgather_cp_algo`，开启KVAllGather长序列并行。 |
| --seq-length [int] | 输入序列的长度。 |

## 使用效果

利用多个计算设备对输入序列进行并行切分，降低单设备的内存消耗，相比不开启序列并行单步耗时增加，相比重计算计算效率提升。

## 注意事项

1. 开启KVAllGather长序列并行时需要同时设置`--transformer-impl transformer_engine`，否则特性不支持。
2. 当前仅支持`--attention-mask-type`为`causal`。
3. 对于定长padding训练场景，采用负载均衡的序列切分方式，`--seq-length`要求能被 2 * context-parallel-size整除。
4. 对于EOD Reset训练场景，采用常规的序列切分方式，`--seq-length`要求能被 context-parallel-size整除。
