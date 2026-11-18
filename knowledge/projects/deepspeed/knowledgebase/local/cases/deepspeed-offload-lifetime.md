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
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 0dd8a8c856a90e2aa0dae70d8d03f961d1b346800fdcabbf8e29ed149aec8bd8
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage_1_and_2.py
  commit: 5420b75de3226e95b6412ed2d95380c0a819c89a
  sha256: 61e0f21a348f3c98c44c32225ab25e1beddced12f36388a578acb1a608a8a454
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/config.py
  commit: 5420b75de3226e95b6412ed2d95380c0a819c89a
  sha256: 34033db3576399499f67ed1b37d90c279a0506dd2b5bddda1715f3c189592f73
reviewed_on: '2026-11-18'
retrieved_on: '2026-11-18'
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

2026-11-04 复核官方 master 固定提交 `d8241a9ba266405e1a58fadf19e24b2370f6d7fa` 的 [`stage_1_and_2.py`](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/deepspeed/runtime/zero/stage_1_and_2.py)：大梯度独立存储、bucket ready/reuse event 和 offload copy 等待仍有实现依据。事件/record_stream 路径还检查 accelerator 的 `resolves_data_dependency()`；不能把某后端的显式事件数当成所有设备的执行模式。

2026-11-04 的同文件增加 compact FP32 gradient partition 与动态 offload 的 view 重建，详见[ZeRO 专题](../topics/zero-state-lifecycle.md)。这些精度/存储改动不撤销本案例的 ready/reuse/record-stream/copy 完成保护；复核时应分别检查“数值保存在哪里”和“谁何时能重写该存储”，不能拿 FP32 累积替代流顺序验收。

2026-11-04 的固定实现还新增按参数追踪累积窗口：`_offload_accumulated_param_ids` 判定该参数本step是否已有有效host梯度，而非用全局micro-step数；第一次在boundary出现的FP32 master梯度可暂留partition，`_offload_partition_only_param_ids` 阻止finalize回填过期host存储。若step前再次backward，从owned片段恢复后继续累加，step等待copy并清空两组ID。

因此本案例的原ready/reuse/copy保护继续适用，但回归输入应增加晚出现参数、部分参数无梯度、连续多个请求boundary和reentrant重算。compact FP32 partition与这些ID分别控制精度/数值来源，events控制可重写时刻，不能互相替代。ZeRO-3新pinned master路径由[ZeRO专题](../topics/zero-state-lifecycle.md)单独解释，不扩大本PR的修复范围。

2026-11-18 继续核对 `5420b75de3226e95b6412ed2d95380c0a819c89a`：原 ready/reuse/copy 等待仍保留。新的 `_offload_unpublished_param_ids` 要在 boundary 发布先前非 boundary 参与、但本次没有梯度的参数，不能只按“当前 backward 的参数”取 host sum。host accumulator 改为每组懒分配 owned partition，恢复临时量时清零本 rank 片段外区域，避免 overflow 检查读到 scratch 残值。

compact GPU partition 只有在 host 精确保存其值且 safety 路径允许时，才在边界 copy 完成依赖下释放；下一 backward 恢复 host-owned sum。`retain_gpu_grad_partition_until_step=True` 保留该分片到 step，**当前实现仍先执行 D2H**，不能用配置描述替代函数次序或删除 copy 完成事件。回归增加同一窗口多个 boundary、只在非 boundary 参与的参数、overflow 丢弃后的新窗口、不同 host/累积 dtype 及开关两侧的实际峰值和更新。此为共享 ZeRO-1/2 当前路径的演进，不将其归入历史 PR 的原始范围，也不把 ZeRO-3 fused CPUAdam 的新路径并入本案例。

更新时联动 [DeepSpeed 总览](../overview/engineering-guide.md)、[ZeRO 生命周期专题](../topics/zero-state-lifecycle.md)、本案例与实际调用方。PR 的改因、当前主干和现场所用 HCU 分支分别查证。
