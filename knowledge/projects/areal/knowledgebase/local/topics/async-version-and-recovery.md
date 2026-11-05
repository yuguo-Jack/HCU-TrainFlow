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
reviewed_on: '2026-11-04'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime execution
sources:
- source: inclusionai-areal
  path: areal/infra/staleness_manager.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: ade1bd484e86d666421716159d6a675ca010c5b5acb8fca05f989389c7f4269d
- source: inclusionai-areal
  path: areal/infra/workflow_executor.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 5124bc5e0eb61001e72c448e22e5db55babde24d512369f444f6390c41e4681c
- source: inclusionai-areal
  path: areal/infra/controller/rollout_controller.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 3b132eb8d7b66369893afecc884d19883247784dff09512b971fcc42891d28b8
- source: inclusionai-areal
  path: areal/trainer/rl_trainer.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: e6fb96cd7e27c88414219906d1b42252b1bc552a7df3ff0dc0415d94bb956362
- source: inclusionai-areal
  path: areal/workflow/rlvr.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 5343b6a3dbfd061d2e75c8c99f129a71a596aa1f8b8573bef9f8a8c950cd5fd6
- source: inclusionai-areal
  path: areal/engine/sglang_remote.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 9ae79598aff49617b2cd7a44c6164cbd1e9a1ec3bc1a5f71ec67437939d9c8c5
- source: inclusionai-areal
  path: areal/engine/awex/memory_saver.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 161c3547d949db44274c08c8a7a68a3af6c55a29772373f236f56bc576f0e57c
- source: inclusionai-areal
  path: areal/utils/recover.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: d5d8da8aae237f4c20af742b01c1d7d11779f3f760e1a587fa601ff327452f49
- source: inclusionai-areal
  path: areal/utils/checkpoint_pointer.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 3a4b2929487d194df9d2cfad7e753add58e899cd03121e12a8c4b5050d7c82f5
- source: inclusionai-areal
  path: areal/engine/fsdp_utils/checkpoint.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: fbd375c77013702ecfc511d4cfad0fc4fff8b0949cfe410f177d7ca7ed1cbe34
- source: inclusionai-areal
  path: docs/en/algorithms/async.md
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 06d507cdd362479eb2cb805239311bfebb6c23273775bc8c1351d3b006ac5cd2
- source: inclusionai-areal
  path: docs/en/reference/checkpointing.md
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 6b00349b9355a58f34cd3eed907671a172e341e4c2bcc1f20b8e3d40ca6b7e78
- source: inclusionai-areal
  path: tests/test_staleness_manager.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 0b6164520fd63f158d122b6f47dd4659a14982e29b02b74aba04acc57c2afeb8
- source: inclusionai-areal
  path: tests/test_recover.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 3f7ba10cf826025ea39e28fe2ebb96375089177ab93e2bf4b0ded33d1476932a
- source: inclusionai-areal
  path: tests/test_rollout_version_race.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 7a8cdfaf8694a43b9b19f5dab429d07a91d6390313f72a9d8b2b3c6a3e98631e
- source: inclusionai-areal
  path: areal/engine/fsdp_engine.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 6e0d40e83de6614a343eb6a37264e602e7c215cfdf491fde8ae14b1d7d04d9fc
- source: inclusionai-areal
  path: areal/v2/weight_update/gateway/app.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 4466ce0e81b39282b470b7c0991546c7db317ce2a0ceaef04ad7f56d5ffa8632
- source: inclusionai-areal
  path: areal/v2/weight_update/controller/controller.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 6a3037239a0ce0528e1f35356b7aba62517ca7705609f106a10afa6a175a6079
- source: inclusionai-areal
  path: areal/v2/training_service/controller/controller.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: dcc52ae17612e969d15e9379949e5645a109bb4a31790667a24b0b8f8204281f
- source: inclusionai-areal
  path: areal/engine/awex/plugins/sglang_plugin.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: d67384ea2a9953c7d74601fb5ce9e1487d266d81721e64e3793fd9afd349ac00
- source: inclusionai-areal
  path: areal/utils/rollout_metrics.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 3aec41512f5bfbe03f6e1a337f13c7acc2077c7212fa9aa327679f78b36e895e
- source: inclusionai-areal
  path: areal/engine/megatron_utils/activation_storage.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 679125ab902bbcc804f79d2d26a36a61a47601a8b15eeb0192c204d2cdb818d3
- source: inclusionai-areal
  path: tests/test_megatron_activation_storage.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: f27d193e5ccb7266ab0c76000541627c64f7258020a257394ee964d88c411d7b
- source: inclusionai-areal
  path: areal/engine/awex/metadata.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 51d9e057bd9f4c25d32dbecf20b9078adc3f04a8db49b0d1541f265ca9fa9c17
- source: inclusionai-areal
  path: areal/engine/awex/adapters/megatron_adapter.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 974ddc9a9c09a94c98c1079acd5ed96fb42c2dffb437b47ad8d3b37936eecf0c
- source: inclusionai-areal
  path: tests/test_megatron_vision_freezing.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: 1d2af31c51421c0fa9dc1b32f062d8b78eec22281ce099efef0b0cf8b97beb49
- source: inclusionai-areal
  path: areal/infra/remote_inf_engine.py
  commit: 27879753c7611fee9a0af6e71a4f838db27b72a7
  sha256: be905076f6f1d3c62bba90b7ece53d329cdd129ebf6fb08f327251e6e88444e0
---

# 异步 admission、版本和恢复

## 问题与链路

异步 rollout 与训练并行会产生版本差。训练速度下降、reward 变慢或恢复后版本跳跃时，单纯提高推理并发可能扩大积压。2026-11-04 本专题以官方 `27879753c7611fee9a0af6e71a4f838db27b72a7` 区分 **提交容量、请求实际版本、权重发布和 durable checkpoint**，它们不是同一个计数。

```text
workflow enqueue → StalenessManager 判断提交容量 → 推理/奖励
  → accepted / rejected → trainer 消费 → actor optimizer update
  → pause → actor.update_weights → actor/critic/rollout set_version
  → checkpoint 内容与恢复 manifest 完成 → 发布 LATEST
  → resume 生成/admission
```

## 1. 容量公式与恢复后的计数修正

[`StalenessManager.get_capacity`](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/infra/staleness_manager.py)取两种约束的较小值：

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

### admission、token过滤与quality窗口

版本容量仍由StalenessManager控制，文件内容哈希未变。新 `mask_stale_tokens` 不调整该公式或拒绝rollout，只在训练端额外过滤actor/MTP目标；原归一分母、context与advantage保留。当前过滤未排除future版本，日志中的future_version_fraction也不会阻断发布；异常版本仍需调查实际已装权重与token provenance，详见[目标专题](loss-aggregation-and-packing.md)。

quality metrics现在随task result穿过预取/远程RPC，在消费者取出形成batch时交给ConsumedMetrics；等待中的未来结果不会提前进入当前窗口。已消费但无trajectory的rejected attempts仍贡献记录的quality scalar，`__count`是观测数，reward_sample_count按episode、group_attempt_count按group。PRM/operational指标保留wall-clock窗口，accepted/admission累计计数与这些窗口均值分开解释。

`BatchTaskDispatcher.wait_results` 与默认 `consume=True` 的 `wait_for_task` 在取出结果后触发 consume；远程controller改调 `get_rollout_result` 携带trajectory+metrics，避免把worker预取期间的值直接当当前训练batch质量。控制面返回契约失败仍单独传播，不伪装成可消费正常trajectory。

## 2. 权重发布与暂停协议

[`RLTrainer._update_weights_and_publish_version`](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/trainer/rl_trainer.py)先等待 `actor.update_weights(meta)` 返回，然后给 actor、critic、rollout、eval rollout 发布同一个版本。版本命名取 `global_step+1`；请求的版本信息应来自**实际提供服务的权重**，不是任务排队时或返回时的全局值。`test_rollout_version_race.py` 专门检查这个竞争条件。

v2 还有实际成功门禁缺口，不能把上述函数“返回”理解为权重安装成功。固定实现中，weight-update gateway 捕获传输异常后仍以 HTTP 200 返回 `WeightUpdateResult(status="error")`，不会推进它的 `pair_info.last_version`；客户端仅检查 HTTP 状态并返回该结果。`GatewayTrainController.update_weights` 当前没有检查 `result.status/error`，便继续 generation 并返回，上层 `RLTrainer` 随后可能发布新版本。因此应同时核对更新结果、gateway/worker 实际版本与新权重 logprob；错误结果不能作为继续使用该版本的依据。HTTP/RPC 直接抛异常时的路径又不同。这里记录源码中现存的限制，没有在上游修复或做设备失败注入。

Rollout controller 的 admission pause 与推理 engine 的 `pause_generation` 是两个层次。v1 AWEX colocated 转移中，reader 的更新事件循环依赖 engine 已 pause；权重安装清空旧缓存后还要 `abort_all_requests`，不能把旧请求 KV 与新权重继续混用。

当前 `weight_update_mode='awex'` 字段本身不足以判定同卡放置：v2 根据 `use_lora` 选择 disk（LoRA）或 AWEX（非 LoRA），忽略 v1 的该模式字段，分离部署也可走 AWEX。主循环用 actor `_version` 与模式判断 v1 特例，恢复则还需要真实 actor/rollout placement。照搬一个模式名来开关 offload 可能导致等待 reader 或重复建立服务。

当前 colocated 设备分配先核对 worker 已隔离的设备可见命名空间：若恰好只暴露该 server 所需卡数，logical base 必须是 0，不能再把物理 GPU ID 或 SLURM_LOCALID 偏移叠加。AWEX 的 transfer rank base 又是独立的密集传输身份，不能与逻辑 device ID 混为一个编号。覆盖 worker 复用/隔离与未隔离两种部署，避免同节点多实例错卡或传输重名。

`pause_generation_sync` 当前使用一次 RPC 尝试并留足暂停宽限；SGLang 先中止 in-flight 请求再暂停 scheduler。控制端超时不证明原 pause 已停止，盲重试可能把请求排在仍执行的暂停后，掩盖真实状态。现场先核原 RPC、engine pause/admission 与恢复 owner，再决定后续操作；本项目的超时常量不能直接成为其它部署通用默认。

AWEX colocate 的 SGLang plugin 另有严格依赖合同：当前只允许 `0.5.9`、`0.5.10.post1`、`0.5.18.dev10+g85b539146`、`0.5.19.dev125+g119b5ffe4`，其他版本在 patch 前报错；SGLang 官方较新 main 不会自动进入这个 allowlist。该 plugin 还拒绝会使 memory saver 失效的 expandable-segments 配置，actor 与 rollout 的 allocator 环境需按各自消费者核对。不能从传权模式相同推断 scheduler hook、pauseable Graph 或 sleep 接口兼容。

### 视觉缓存和实际设备放置

AWEX plugin在receiver初始化读取 `frozen_visual_embeddings is True` 的积极证明，未知/legacy sender默认False。成功native flush只处理KV/pool，因此plugin额外清视觉embedding cache：未冻结时每次清；冻结时首次也清，再设initialized以允许后续复用。图像hash不含视觉权重版本，单独冻结vision encoder不能证明projector/merger也不变；部分更新/未确认flush后不能提前宣布缓存有效。

该证明的生产者是 [`awex/metadata.py`](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/engine/awex/metadata.py)：native Qwen3-VL/Qwen3.5 路线要求 Megatron-Bridge、找到实际 actor 的 `vision_model`，且其全部参数 `requires_grad=False`；不是只看 CLI 或 rollout 端模型。Qwen4 实验路线另外使用自己的 frozen binder/各分片证明。Megatron adapter 在 eager publish 或 legacy 初始化时发布元数据，receiver 的积极判断也不能替代发布后真实权重/flush 的完成检查。

[`test_megatron_vision_freezing.py`](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/tests/test_megatron_vision_freezing.py) 读取了 provider 的真实 freeze 方法，分别检查 encoder 与 projection/merger 是否退出 optimizer、无梯度且 step 后不变；缺 provider 时会 skip。这是上游测试的合同，本轮未执行，不能将单独 freeze encoder 当成整个视觉路径冻结。

colocated SGLang现在显式保留传入的 `_awex_transfer_rank_base`。未提供时，已隔离设备命名空间使用logical base0但保留controller密集传输offset，未隔离环境则跟随解析出的实际worker placement，而非假定controller枚举等于Slurm local order。设备ID与通信rank是两个身份，跨节点/多实例重新接管要分别核对。新disable_prefill_cuda_graph字段默认None以省略flag，只有目标SGLang支持该flag时才使用，不能借此解除现有version allowlist。

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

[`RecoverHandler.dump`](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/utils/recover.py)除了 actor/critic DCP payload，还保存 last step、saver/evaluator/logger 状态、dataloader state 和 DistributedSampler epoch。默认保存/加载 optimizer，若关闭对应字段则恢复性质改变；HF 权重导出不能代替这些训练状态。

**单控制器且非多 rank SPMD** 路径使用 generation + `LATEST`。先创建本次 manifest/payload，完成各角色保存；若有多个异步 Megatron engine，先等待其他异步 payload，再让最后的 publisher 通过 finalize 回调发布。没有异步 publisher 时同步完成后发布。不是看到 generation 目录就认为 checkpoint 已提交。

[`checkpoint_pointer.publish_latest`](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/utils/checkpoint_pointer.py)检查可加载的 manifest/payload 与单调 step，通过临时文件、fsync、`os.replace` 原子替换 `LATEST`，然后清理前一代。`resolve_checkpoint` 优先选择已发布指针，没有时才用 legacy 布局；已发布内容损坏会报一致性错误，不静默从头训练。磁盘清理必须尊重当前 LATEST 和未完成异步保存，不能按目录 mtime 删除。

FSDP 的训练 checkpoint 另有 scheduler 状态边界：`with_optim=True` 在 DCP/HF 保存前将 replicated scheduler state 写入临时文件并原子替换 `lr_scheduler.pt`，通过既有同步保存 collectives 保证各 rank 完成前文件就绪；load 在 optimizer 恢复后载入 scheduler。缺该文件的旧 checkpoint 只告警，继续使用当前 scheduler；`with_optim=False` 不恢复它。要保持连续学习率轨迹，仍需相同 scheduler 配置、总训练步数和 step 身份，不能因 optimizer 已加载就声称精确恢复。

SPMD/多 rank 路径仍使用 legacy 恢复布局；其 dataloader 状态按 rank 聚合，加载时要求 world size 与状态数量相符。不能因此宣称任意 DP/TP/PP 拓扑改变都可恢复。

训练侧activation释放同样要遵守消费者边界：weight-residency路径在forward/backward范围跟踪TE/MCore activation，完整backward返回后才release；nested recompute保护外层输入/grad和返回tensor，异常discard不resize。`ActivationStorageTracker.release`会按storage指针去重并保护参数/buffer别名，不是checkpoint持久状态，也不能移到仍有backward消费者之前以降低表面峰值。固定 `27879753c7611fee9a0af6e71a4f838db27b72a7` 的checkpoint_pointer/recover和v2 status消费者未改，保留下列恢复限制。

## 5. 已明确的限制、验证与诊断

- `RecoverHandler._ensure_recover_supported` 对 **GatewayTrainController / `_version=v2` 明确抛 NotImplementedError**。这与能跑 v2 训练不矛盾；打开 recover 前必须检查实际控制器。
- `recover.mode=on/auto` 在当前实现均检查有效现存 checkpoint；没有资料时能返回非恢复运行。调度器“重启成功”不能代替核对恢复步、数据游标和优化器。
- `tests/test_recover.py` 覆盖异步 finalize 后发布、publisher 失败仍保持旧 LATEST、v2 拒绝、AWEX 失败不开放请求等；`test_staleness_manager.py` 覆盖恢复容量。这里是源码/测试阅读，**未做 HCU 集群失败注入**。

现场卡住时先比对 controller/worker/serving 版本、队列计数和暂停层次，再追转移 group、RPC 和 reader completion；不要一开始就调大 timeout。OOM 按保存、actor load、weight staging、KV/graph 恢复的阶段抓内存；数值异常检查 response version、行为 logp、数据位置与 loss 归一化。

现场验收需至少一次受控失败：记录最近已发布 checkpoint、停止/重启边界，确认恢复 step/数据/optimizer/rollout 版本与质量；节点健康和作业拉起仍交给集群容错工具。回到[AReaL 总览](../overview/engineering-guide.md)并联查[目标聚合专题](loss-aggregation-and-packing.md)。


## 本轮补充固定证据

- [areal/engine/fsdp_engine.py](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/engine/fsdp_engine.py)

- [areal/v2/weight_update/gateway/app.py](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/v2/weight_update/gateway/app.py)
- [areal/v2/weight_update/controller/controller.py](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/v2/weight_update/controller/controller.py)
- [areal/v2/training_service/controller/controller.py](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/v2/training_service/controller/controller.py)
- [areal/engine/awex/plugins/sglang_plugin.py](https://github.com/areal-project/AReaL/blob/27879753c7611fee9a0af6e71a4f838db27b72a7/areal/engine/awex/plugins/sglang_plugin.py)
