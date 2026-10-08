---
id: official-megatron-wiki/moe
title: MoE：路由、负载、通信与 grouped GEMM
engine: megatron
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/moe_layer.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 99d18814749a6ba9ecca2cca1875e0c723eff1c06d328768ac6570f1641c0e2e
- source: nvidia-megatron-lm
  path: docs/user-guide/features/moe.md
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 004d1c2bc849bb6a96e77099872a1cb282907e28be774953c2ae40aa39b094c6
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 7fc7af4f3f6fe67a6a1d7f9a7df63c5eaf245bc2cb686ff09a0adc58292daa6a
---

# MoE：路由、负载、通信与 grouped GEMM

## 工作负载分解

把 router/top-k、token permutation、dispatch、expert GEMM/activation、combine、shared expert、辅助 loss 分开。每专家 token 数分布和 padding/capacity 策略决定真实 GEMM 形状，不能只登记 hidden size 与总 token 数。

## 可复用分析

保存每层路由直方图、EP 组和最慢 rank，判断是 token 不均、通信量、kernel 粒度还是 CPU 分发开销。对 grouped GEMM 提取每个 group 的 M/N/K、dtype、转置、leading dimension/stride 和 scaling。hipBLASLt/grouped 的调优需求形成可复现 size 工单；不要宣称自动完成其 tune。

## 优化与正确性

融合前核对 NV 路径的 permutation、padding、scale、FP8 缓存及 backward 状态。优先复用已有 Flash-Train/HCU TE 能力，再决定补实现。跨微批 EP overlap 改变张量生命周期，不能只看 forward 正确；需检查梯度累计、重算/RNG、load-balance loss 和 optimizer 更新。

不同实现对 shared-expert overlap 的约束可能相反。必须以目标分支具体实现为准，不把 MindSpeed 或 Bridge 的同名/近义 flag 当作相同语义。参考移植详见生态案例。

## 固定源码与更新范围

- [megatron/core/transformer/moe/moe_layer.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/core/transformer/moe/moe_layer.py)
- [docs/user-guide/features/moe.md](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/docs/user-guide/features/moe.md)
- [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/core/transformer/transformer_config.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
