---
id: engines/areal/topics/async-version-and-recovery
title: AReaL：异步 admission、权重版本和事务式恢复边界
engine: areal
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime
  execution
sources:
- source: inclusionai-areal
  path: areal/infra/staleness_manager.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: ade1bd484e86d666421716159d6a675ca010c5b5acb8fca05f989389c7f4269d
- source: inclusionai-areal
  path: areal/infra/workflow_executor.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: eee33608c94575e1a777f870d53e44e4cdf6bd449a0a17041f7d7752871ea0e6
- source: inclusionai-areal
  path: areal/infra/controller/rollout_controller.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 7ec914806b02365d2b6c741628ded80b66f263df13dedb1d0dfff2e131d56f08
- source: inclusionai-areal
  path: areal/trainer/rl_trainer.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 62beff00ecd44dca988ffef3c3c4160afae4e488cecd64361a3dd90eaae3a559
- source: inclusionai-areal
  path: areal/workflow/rlvr.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: a532f6523bededa07171e0b60a3a1ff5f8151da71abfff80bd1bce6e3f74b45e
- source: inclusionai-areal
  path: areal/engine/sglang_remote.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 514a071bc5860d239b5618bd8adc3b2df530dc9a75b13b54c8275bef154c9c58
- source: inclusionai-areal
  path: areal/engine/awex/memory_saver.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 161c3547d949db44274c08c8a7a68a3af6c55a29772373f236f56bc576f0e57c
- source: inclusionai-areal
  path: areal/utils/recover.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: d5d8da8aae237f4c20af742b01c1d7d11779f3f760e1a587fa601ff327452f49
- source: inclusionai-areal
  path: areal/utils/checkpoint_pointer.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 3a4b2929487d194df9d2cfad7e753add58e899cd03121e12a8c4b5050d7c82f5
- source: inclusionai-areal
  path: areal/engine/fsdp_utils/checkpoint.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: fbd375c77013702ecfc511d4cfad0fc4fff8b0949cfe410f177d7ca7ed1cbe34
- source: inclusionai-areal
  path: docs/en/algorithms/async.md
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: fb2200da54686a7a923dcbe39ba5429c28a17bcd07b618103e7aeec25f947f81
- source: inclusionai-areal
  path: docs/en/reference/checkpointing.md
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: e477f1a57bee59e5e9e281c08536cc4baf7212081d80c5e10b46fd8984b8b12c
- source: inclusionai-areal
  path: tests/test_staleness_manager.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 0b6164520fd63f158d122b6f47dd4659a14982e29b02b74aba04acc57c2afeb8
- source: inclusionai-areal
  path: tests/test_recover.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 3f7ba10cf826025ea39e28fe2ebb96375089177ab93e2bf4b0ded33d1476932a
- source: inclusionai-areal
  path: tests/test_rollout_version_race.py
  commit: aedc21ec66ff03f329dcd4139945da8087e0d0e7
  sha256: 7a8cdfaf8694a43b9b19f5dab429d07a91d6390313f72a9d8b2b3c6a3e98631e
---

# 异步 admission、版本和恢复

## 问题与链路

异步 rollout 与训练并行会产生版本差。训练速度下降、reward 变慢或恢复后版本跳跃时，单纯提高推理并发可能扩大积压。本专题以官方 `aedc21ec` 区分 **提交容量、请求实际版本、权重发布和 durable checkpoint**，它们不是同一个计数。

```text
workflow enqueue → StalenessManager 判断提交容量 → 推理/奖励
  → accepted / rejected → trainer 消费 → actor optimizer update
  → pause → actor.update_weights → actor/critic/rollout set_version
  → checkpoint 内容与恢复 manifest 完成 → 发布 LATEST
  → resume 生成/admission
```

## 1. 容量公式与恢复后的计数修正

[`StalenessManager.get_capacity`](https://github.com/areal-project/AReaL/blob/aedc21ec66ff03f329dcd4139945da8087e0d0e7/areal/infra/staleness_manager.py)取两种约束的较小值：

```text
并发容量 = max(1, max_concurrent_rollouts) − running
版本容量 = (max_staleness + current_version + 1) × max(1, consumer_batch_size)
           − accepted − running
capacity = min(并发容量, 版本容量)
pending limit = (max_staleness + 1) × consumer_batch_size
```

`accepted` 是累计接纳量，消费 batch 后不会简单归零。Enqueue、submit、accept、reject 的计数迁移由 manager 加锁维护；容量可能为负，代表已有请求超出预算，不应把负数当成新的可用 slot。队列上限与正在执行请求数量也要分别观察。

从 checkpoint 恢复到版本 V 时，若 accepted 仍为零，公式会额外开放约 V 个 batch 的预算。当前 `RLTrainer` 初始化恢复后调用 `on_version_recovered(V)`，将 accepted 设为 `V×consumer_batch_size`，把可用版本预算恢复到 `(max_staleness+1)×batch_size−running`。所以恢复不仅是 `set_version`，还必须修正历史 admission 状态。

这是一种生产/消费节奏约束；单请求最终使用哪个版本，还要检查 token/response version。不能仅看 capacity 正常便宣布所有样本都在版本阈值内。

## 2. 权重发布与暂停协议

[`RLTrainer._update_weights_and_publish_version`](https://github.com/areal-project/AReaL/blob/aedc21ec66ff03f329dcd4139945da8087e0d0e7/areal/trainer/rl_trainer.py)先等待 `actor.update_weights(meta)` 返回，然后给 actor、critic、rollout、eval rollout 发布同一个版本。版本命名取 `global_step+1`；请求的版本信息应来自**实际提供服务的权重**，不是任务排队时或返回时的全局值。`test_rollout_version_race.py` 专门检查这个竞争条件。

Rollout controller 的 admission pause 与推理 engine 的 `pause_generation` 是两个层次。v1 AWEX colocated 转移中，reader 的更新事件循环依赖 engine 已 pause；权重安装清空旧缓存后还要 `abort_all_requests`，不能把旧请求 KV 与新权重继续混用。

当前 `weight_update_mode='awex'` 字段本身不足以判定同卡放置：v2 非 LoRA 分离部署也可能选 AWEX。主循环用 actor `_version` 与模式判断 v1 特例，恢复则还需要真实 actor/rollout placement。照搬一个模式名来开关 offload 可能导致等待 reader 或重复建立服务。

## 3. 共享显存：保存、转移与重新接纳的次序

一般循环在改参数前等待 checkpoint staging；v1 AWEX colocated 将训练保存移到 weight transfer **之前**，此时 actor 已 onload，避免后续恢复 actor 权重与推理 KV、转移暂存、TP all-gather 保存瞬态叠加。其他模式仍按自己的时序保存，不能把这条局部优化推广成所有引擎一律前置保存。

恢复 colocated AWEX 的协议更严格：

1. 连接 inference engine，暂停 admission 和 generation。
2. 释放 rollout 的 KV cache、weights、CUDA graph 对应区域。
3. 再加载训练 checkpoint，推送恢复版本的 actor 权重。
4. 确认版本，丢弃旧请求，恢复 graph/KV 与生成。
5. 全流程成功才重新开放 admission。

缺少 tag-aware offload/onload、pause_generation_sync 或 abort/continue 的 engine 会被拒绝。恢复失败后 colocated 请求保持暂停，不能在 `finally` 里无条件 resume。非 colocated 更新路径的失败语义不同，应读实际分支而不是套同一处理。

## 4. 什么 checkpoint 才能作为恢复入口

[`RecoverHandler.dump`](https://github.com/areal-project/AReaL/blob/aedc21ec66ff03f329dcd4139945da8087e0d0e7/areal/utils/recover.py)除了 actor/critic DCP payload，还保存 last step、saver/evaluator/logger 状态、dataloader state 和 DistributedSampler epoch。默认保存/加载 optimizer，若关闭对应字段则恢复性质改变；HF 权重导出不能代替这些训练状态。

**单控制器且非多 rank SPMD** 路径使用 generation + `LATEST`。先创建本次 manifest/payload，完成各角色保存；若有多个异步 Megatron engine，先等待其他异步 payload，再让最后的 publisher 通过 finalize 回调发布。没有异步 publisher 时同步完成后发布。不是看到 generation 目录就认为 checkpoint 已提交。

[`checkpoint_pointer.publish_latest`](https://github.com/areal-project/AReaL/blob/aedc21ec66ff03f329dcd4139945da8087e0d0e7/areal/utils/checkpoint_pointer.py)检查可加载的 manifest/payload 与单调 step，通过临时文件、fsync、`os.replace` 原子替换 `LATEST`，然后清理前一代。`resolve_checkpoint` 优先选择已发布指针，没有时才用 legacy 布局；已发布内容损坏会报一致性错误，不静默从头训练。磁盘清理必须尊重当前 LATEST 和未完成异步保存，不能按目录 mtime 删除。

SPMD/多 rank 路径仍使用 legacy 恢复布局；其 dataloader 状态按 rank 聚合，加载时要求 world size 与状态数量相符。不能因此宣称任意 DP/TP/PP 拓扑改变都可恢复。

## 5. 已明确的限制、验证与诊断

- `RecoverHandler._ensure_recover_supported` 对 **GatewayTrainController / `_version=v2` 明确抛 NotImplementedError**。这与能跑 v2 训练不矛盾；打开 recover 前必须检查实际控制器。
- `recover.mode=on/auto` 在当前实现均检查有效现存 checkpoint；没有资料时能返回非恢复运行。调度器“重启成功”不能代替核对恢复步、数据游标和优化器。
- `tests/test_recover.py` 覆盖异步 finalize 后发布、publisher 失败仍保持旧 LATEST、v2 拒绝、AWEX 失败不开放请求等；`test_staleness_manager.py` 覆盖恢复容量。这里是源码/测试阅读，**未做 HCU 集群失败注入**。

现场卡住时先比对 controller/worker/serving 版本、队列计数和暂停层次，再追转移 group、RPC 和 reader completion；不要一开始就调大 timeout。OOM 按保存、actor load、weight staging、KV/graph 恢复的阶段抓内存；数值异常检查 response version、行为 logp、数据位置与 loss 归一化。

现场验收需至少一次受控失败：记录最近已发布 checkpoint、停止/重启边界，确认恢复 step/数据/optimizer/rollout 版本与质量；节点健康和作业拉起仍交给集群容错工具。回到[AReaL 总览](../overview/engineering-guide.md)并联查[目标聚合专题](loss-aggregation-and-packing.md)。
