---
id: doc-ascend-mindspeed-5d199f31f37ecfafd9f4
title: Ascend/MindSpeed / docs/zh/_menu.md
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
path: docs/zh/_menu.md
raw_sha256: f82f5b96835dbb05da0b77b435cf19d920d4e4ef5c606c27b6ff6cc285e74386
sources: []
generated_body_sha256: 5094bac9940f2752984fdbecba55296249c335fa317bffe5644d5bc4a9100a4f
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/_menu.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/_menu.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# MindSpeed Core

- [简介](introduction.md)
- [软件安装](./user-guide/install_guide.md)
- [特性说明]()
  - [特性总览](./features/feature_list.md)
  - [Megatron特性]()
    - [Megatron数据并行](./features/data-parallel.md)
    - [Megatron张量并行](./features/tensor-parallel.md)
    - [Megatron流水并行](./features/pipeline-parallel.md)
    - [Megatron虚拟流水线并行](./features/virtual-pipeline-parallel.md)
    - [Megatron分布式优化器](./features/distributed-optimizer.md)
    - [Megatron序列并行](./features/sequence-parallel.md)
    - [Megatron异步DDP](./features/async-ddp.md)
    - [Megatron权重更新通信隐藏](./features/async-ddp-param-gather.md)
    - [Megatron重计算](./features/recomputation.md)
    - [Megatron分布式权重](./features/dist_ckpt.md)
    - [Megatron全分片并行](./features/custom_fsdp.md)
    - [Megatron Transformer Engine](./features/transformer_engine.md)
    - [Megatron Multi-head Latent Attention](./features/multi-head-latent-attention.md)
  - [并行策略特性]()
    - [Ascend Ulysses长序列并行](./features/ulysses-context-parallel.md)
    - [Ascend Ring Attention长序列并行](./features/ring-attention-context-parallel.md)
    - [Ascend Double Ring Attention长序列并行](./features/double-ring.md)
    - [Ascend混合长序列并行](./features/hybrid-context-parallel.md)
    - [Ascend自定义空操作层](./features/noop-layers.md)
    - [Ascend DualPipeV](./features/dualpipev.md)
  - [内存优化特性]()
    - [Ascend激活函数重计算](./features/activation-function-recompute.md)
    - [Ascend重计算流水线独立调度](./features/recompute_independent_pipelining.md)
    - [Ascend Mask归一](./features/generate-mask.md)
    - [Ascend BF16参数副本复用](./features/reuse-fp32-param.md)
    - [Ascend swap_attention](./features/swap_attention.md)
    - [Ascend Norm重计算](./features/norm-recompute.md)
    - [Ascend Hccl Buffer自适应](./features/hccl-group-buffer-set.md)
    - [Ascend Swap Optimizer](./features/swap-optimizer.md)
    - [Virtual Optimizer](./features/virtual-optimizer.md)
  - [亲和计算特性]()
    - [Ascend Flash Attention](./features/flash-attention.md)
  - [通信优化特性]()
    - [Ascend Gloo存档落盘优化](./features/hccl-replace-gloo.md)
    - [Ascend高维张量并行](./features/tensor-parallel-2d.md)
  - [Mcore MoE特性]()
    - [Ascend Megatron MoE GMM](./features/megatron_moe/megatron-moe-gmm.md)
    - [Ascend Megatron MoE Allgather Dispatcher性能优化](./features/megatron_moe/megatron-moe-allgather-dispatcher.md)
    - [Ascend Megatron MoE Alltoall Dispatcher性能优化](./features/megatron_moe/megatron-moe-alltoall-dispatcher.md)
    - [Ascend Megatron MoE TP拓展EP](./features/megatron_moe/megatron-moe-tp-extend-ep.md)
    - [Megatron MoE Allgather Dispatcher分支通信隐藏优化](./features/megatron_moe/megatron-moe-allgather-overlap-comm.md)
    - [Ascend共享专家](./features/shared-experts.md)
    - [1F1B Overlap](./features/megatron_moe/megatron-moe-fb-overlap.md)
    - [专家并行动态负载均衡（数参互寻）](./features/balanced_moe.md)
  - [关键场景特性]()
    - [Ascend EOD Reset训练场景](./features/eod-reset.md)
  - [多模态特性]()
    - [Ascend PP支持动态形状](./features/variable_seq_lengths.md)
    - [Ascend PP支持多参数传递](./features/multi_parameter_pipeline.md)
    - [Ascend PP支持多参数传递和动态形状](./features/multi_parameter_pipeline_and_variable_seq_lengths.md)
    - [Ascend非对齐线性层](./features/unaligned_linear.md)
    - [Ascend非对齐Ulysses长序列并行](./features/unaligned-ulysses-context-parallel.md)
  - [其他特性]()
    - [Ascend TFLOPS计算](./features/ops_flops_cal.md)
- [特性开发](./user-guide/feature_development.md)
- [模型迁移](user-guide/model-migration.md)
- [性能调优](user-guide/megatron_performance_optimization.md)
- [FAQ](FAQ.md)
