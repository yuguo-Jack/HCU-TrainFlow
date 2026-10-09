---
id: engines/deepspeed-offload-lifetime
title: DeepSpeed ZeRO-1/2 offload：梯度所有权与流顺序
engine: deepspeed
kind: authored
stages: [optimize, fault-tolerance]
review_level: pr-diff-and-selected-source-reading
runtime_validated: false
pr_sources: [pr-deepspeedai--deepspeed-8632]
sources: []
---

# DeepSpeed ZeRO-1/2 offload：梯度所有权与流顺序

## 问题与动机

[PR #8632 完整来源页](../prs/DeepSpeedAI--DeepSpeed/PR-8632.md) 在排查 CPU offload 下 NaN 时强化梯度存储生命周期和流顺序。范围是 ZeRO-1/2 的 optimizer CPU/NVMe offload 相关共享路径；不能推广到 ZeRO-3 或另有调度逻辑的 ZenFlow。

这是正确性修复，不能把“减少同步”天然视为优化。训练中的生产者、归约和 D2H 消费者可能运行在不同流上，tensor 在 Python 里仍存在也不能单独保证 buffer 没被复用。

## 改动与实现线索

主要路径位于 `runtime/zero/stage_1_and_2.py`：`reduce_independent_p_g_buckets_and_remove_grads` → reduction → `copy_grads_in_partition` → CPU 梯度累积/step。完整文件和 head/base 对照在来源页。

- 超过 bucket 的大梯度创建独立存储，防止原始存储提前复用。
- 每个 bucket 生产者记录 readiness event，消费者等待，包括大梯度分支。
- contiguous IPG buffer 在消费完成后记录复用事件，下一次写入等待。
- 消费张量的 stream 注册存储生命周期，D2H 写入顺序显式化。
- optimizer step、CPU buffer 重置、checkpoint 加载和销毁等边界等待尚未完成的 offload copy。

PR 保留原 overlap barrier，并在其上增加约束；修改后也没有一个可以随意关闭这些保护的新配置项。即使 overlap_comm 关闭，offload 仍可能涉及异步路径。

## 如何验证与定位

构造同时覆盖正常 bucket、超大梯度、多个累积 microbatch、CPU/NVMe offload、overlap 开关和恢复边界的回归。检查训练值、梯度、CPU accumulator、optimizer 更新及 NaN；不要只跑一个无 offload 小模型。

性能测量分别记录原始数据生产、等待、归约、D2H 和 CPU optimizer，再看端到端。新增等待可能暴露真实依赖，而先前更短的耗时可能来自竞态；数值正确优先于有问题的“快”基线。

## HCU 迁移与回退

先核对 HCU 分支是否已有等价修复以及 runtime 的 stream/event/allocator 语义。不能直接假定 CUDA stream API 的名称相同就意味着所有行为相同；必要时读实际 HIP/PyTorch 后端和底层实现。

若候选引起回归，可切回经验证的无问题配置并保留故障证据，而不是删除生命周期保护。调参和实现稳定后再安排阶段 loss；单测通过不等同长训已验证。本案例没有 HCU 实测数据，所有现场记录留在私有经验 Wiki。
