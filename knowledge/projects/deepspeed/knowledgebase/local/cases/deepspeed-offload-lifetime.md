---
id: engines/deepspeed-offload-lifetime
title: DeepSpeed ZeRO-1/2 offload：梯度所有权与流顺序
engine: deepspeed
kind: authored
stages:
- optimize
- fault-tolerance
review_level: pr-diff-and-selected-source-reading
runtime_validated: false
pr_sources:
- pr-deepspeedai--deepspeed-8632
sources:
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage_1_and_2.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: aa9556509f8249b9e82f6208297311c69e25eb6e560e64c7670fe3bb928436b3
reviewed_on: '2026-10-12'
---

# DeepSpeed ZeRO-1/2 offload：梯度所有权与流顺序

## 问题与动机

[PR #8632 完整来源页](../../upstream/prs/deepspeedai--DeepSpeed/PR-8632.md) 在排查 CPU offload 下 NaN 时强化梯度存储生命周期和流顺序。范围是 ZeRO-1/2 的 optimizer CPU/NVMe offload 相关共享路径；不能推广到 ZeRO-3 或另有调度逻辑的 ZenFlow。

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

若候选引起回归，可切回经验证的无问题配置并保留故障证据，而不是删除生命周期保护。调参和实现稳定后再安排阶段 loss；单测通过不等同长训已验证。本案例没有 HCU 实测数据。中间排查留在任务 workspace；可复用环境经验和已验收的最终总结按知识筛选规范进入共享 Wiki。

## 当前源码与更新范围

2026-10-12 复核官方 master 固定提交 `1c862f7df93f0345b977c67f5408d967b94bf4ae` 的 [`stage_1_and_2.py`](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/deepspeed/runtime/zero/stage_1_and_2.py)：大梯度独立存储、bucket ready/reuse event 和 offload copy 等待仍有实现依据。事件/record_stream 路径还检查 accelerator 的 `resolves_data_dependency()`；不能把某后端的显式事件数当成所有设备的执行模式。

更新时联动 [DeepSpeed 总览](../overview/engineering-guide.md)、[ZeRO 生命周期专题](../topics/zero-state-lifecycle.md)、本案例与实际调用方。PR 的改因、当前主干和现场所用 HCU 分支分别查证。
