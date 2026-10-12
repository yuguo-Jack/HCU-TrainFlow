---
id: doc-ascend-mindspeed-5a98274545de7e87a84e
title: Ascend/MindSpeed / docs/en/user-guide/performance_optimization.md
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
path: docs/en/user-guide/performance_optimization.md
raw_sha256: 78b127cdb69f498d2820a70f9d272fefdb9fd628d60bb366e98d7d7fb313353c
sources: []
generated_body_sha256: f456addb133dea0a3a6d2eae02018c9f9e8e9a04fda4127bc5d205b0dbf9929f
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/user-guide/performance_optimization.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/user-guide/performance_optimization.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Performance Tuning Guide

As the parameter scale of large models grows exponentially, the training process faces multiple challenges such as memory bottlenecks, low computational efficiency, and massive communication overhead. Particularly for models with hundreds of billions or even trillions of parameters, traditional data parallelism strategies can no longer meet the demands, and the complexity of hybrid parallelism strategies also imposes a steep learning curve on developers. How to efficiently utilize the computing resources of large-scale clusters and maximize training throughput has become the core challenge in large model training.

MindSpeed, as a large model training acceleration library designed for Ascend AI processors, provides a series of innovative solutions to address these challenges. Its core advantages include: an adaptive parallelism configuration strategy that automatically optimizes parallelism dimension partitioning based on model architecture and hardware topology; an efficient memory management mechanism that significantly reduces memory usage through techniques such as recomputation and activation compression; and deeply optimized communication operators that fully leverage the interconnect bandwidth advantages of Ascend chips. In terms of performance features, MindSpeed supports dynamic load balancing, fine-grained operator fusion, and optimization techniques for long sequences, achieving significant throughput improvements in typical large model training scenarios as demonstrated by benchmarks.

## Megatron-LM Performance Optimization

Building on the above technical foundation, MindSpeed further performs in-depth performance optimization for the Megatron-LM framework. By restructuring critical computation paths, optimizing distributed communication patterns, and introducing Ascend-specific operator acceleration capabilities, it achieves efficient training acceleration in large-scale cluster environments. For details, refer to [Megatron-LM Performance Optimization](./megatron_performance_optimization.md).
