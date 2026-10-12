---
id: doc-ascend-mindspeed-597296aeaa3f727130e2
title: Ascend/MindSpeed / docs/zh/features/distributed-optimizer.md
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
path: docs/zh/features/distributed-optimizer.md
raw_sha256: da3df356195903229388c4e3ef90a701e3b50727c28cd1318a1b6ee2340a6477
sources: []
generated_body_sha256: 7d200c05b1fe1cef6cae2f17843963347cfce76280206b9d2c51fabf2b61fb89
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/distributed-optimizer.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/distributed-optimizer.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Megatron分布式优化器

## 背景与挑战

在数据并行（Data Parallelism，DP）框架下，各计算设备在梯度聚合（All-Reduce）前独立执行任务，实现高效并行处理。然而，All-Reduce操作后，所有设备基于相同的梯度、参数及优化器状态执行一致的更新流程，这不仅导致了计算资源的冗余，也增加了存储负担，影响整体效率。

## 解决方案

为解决上述问题，引入分布式优化器策略，其核心在于将原本集中式的计算与存储需求分散至各个设备上，通过优化通信机制确保各设备间的协同作业。具体而言，该策略将重复的内存分配和计算任务分解，并借助高效通信机制进行信息交换，从而在不牺牲最终结果的前提下，显著降低内存占用与计算时间。

## 使用场景

在DP规模大于1的分布式训练场景中，优化器状态会被均匀切分到各个DP组中。各DP组通过ReduceScatter操作对梯度进行局部更新，随后，各DP组独立完成权重的部分更新。最终，通过一次AllGather操作汇总所有模型权重，实现全局同步，确保模型一致性。

## 使用方法

在部署分布式优化器时，只需在脚本中加入以下配置：

```bash
--use-distributed-optimizer      # 启用分布式优化器功能
```

## 使用效果

启用分布式优化器后，由于优化器状态被切分，系统能够显著减少内存消耗，又因为每张卡只需完成局部权重的更新，提升了计算资源的利用率，实现更高效的并行计算性能。
