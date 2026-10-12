---
id: ecosystem/topics/mindspeed-context-parallel
title: MindSpeed：Ring、Hybrid 与 KV All-Gather 上下文并行
engine: mindspeed
kind: authored
stages:
- adapt
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected source, official documentation and related PR reading; no HCU runtime
  validation
sources:
- source: ascend-mindspeed
  path: mindspeed/features_manager/context_parallel/context_parallel_feature.py
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: 965840f69c4a944f21ca3303b18a67cbb2daa7e72c9443b10bd5483e3eae9dd9
- source: ascend-mindspeed
  path: docs/en/features/ring-attention-context-parallel.md
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: dece78275526a481193bda7a7e973576c69c5d0e606248e0bb3d56408f649359
- source: ascend-mindspeed
  path: docs/en/features/kvallgather-context-parallel.md
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: f714c5c862a86a417d8c0c9597e8963d4c7e43b5e226be20e4f4821096e38115
---

# MindSpeed：Ring、Hybrid 与 KV All-Gather 上下文并行

## 适用问题与代价模型

长序列 attention 的激活/计算使单卡不够或计算严重不均时，CP 将序列拆到多个 rank。收益来自每 rank 序列/激活减少和可重叠交换；代价是 KV 或 attention 中间结果通信、额外 buffer、group 管理与不均。CP 是训练数学布局变化，不能只替换一个 attention kernel 后宣称完成。

## 三类入口和约束

`context_parallel_feature.py` 的 algo 选择含 megatron_cp_algo、hybrid、hybrid_adaptive、kvallgather 及特定模型路径。Ring 路径检查 sequence 可被 `2×CP` 整除，CP window 必须在有效范围内并能整除相应 ring degree；window 和 send/recv group 共同决定调度。

Hybrid 同时拆 Ulysses 和 ring：CP degree 要能被 Ulysses degree 整除，ring degree>1，head 数满足 Ulysses×TP 的分布，sequence 仍需匹配 2×CP。不是把两个开关叠起来就成立。KV all-gather 对 TE causal/SBHD 与 reset mask/THD 存在不同整除要求，不能把 packed varlen 与普通固定长度规则混用。

## 从配置到 attention 的完整链

feature 参数验证→model parallel group 初始化/销毁 patch→batch 的 CP 分片→DotProductAttention/TEDotProductAttention 替换→RoPE position 与 attention mask→KV交换/attention。KV/Ulysses与ring对应的 TE wrapper 不相同。排查首个数值差异应沿 token 位置和数据分片回到 group，再追 kernel；普通单卡 attention 单测无法证明这条分布式链正确。

## 数值、负载和性能验证

用固定输入对 CP=1 与目标 CP 的全局输出/loss/梯度对比，包含 causal mask、变长、packed cu-seqlens、RoPE、首尾边界和不同 rank。检查 global/local sequence 映射、通信顺序和 RNG。CP、TP、PP 与 MTP 组合各按实际消费者测试，不能从 head 可整除推断全部支持。

性能采集看各 rank attention/交换、batch-ready 与 HBM 峰值；ring window 增大可能改善并发，也可能增加交换/内存。KV all-gather 得到更多连续计算，但缓存更大；是否优于 ring 要在真实 seq/head/dtype/拓扑下比较。没有 HCU/NPU同规模实测，不写估计加速比。

## 诊断、回退和维护

卡住先核对组成员、某 rank shape/异常与 ring send/recv顺序；loss 偏差先核对 mask/position/data ownership；OOM 查 buffer 生命周期和最坏 rank。先退回已验证 CP算法或CP=1，在容量允许下定位，不随意改模型结构。更新 feature、group、batch shard、attention、RoPE 和 LLM recipe 时共同复核[总览](../mindspeed.md)，并对照 HCU 对应分支实现。

## 固定证据与复核范围

- [mindspeed/features_manager/context_parallel/context_parallel_feature.py](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/mindspeed/features_manager/context_parallel/context_parallel_feature.py)
- [docs/en/features/ring-attention-context-parallel.md](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/ring-attention-context-parallel.md)
- [docs/en/features/kvallgather-context-parallel.md](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/kvallgather-context-parallel.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
