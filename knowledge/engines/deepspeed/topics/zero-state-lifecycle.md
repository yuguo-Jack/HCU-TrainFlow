---
id: engines/deepspeed/topics/zero-state-lifecycle
title: DeepSpeed ZeRO：分片、参数预取与 offload 生命周期
engine: deepspeed
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
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/config.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: cf8beb53835f192afdf5a0c8a4b5bbf3fb09d1fdc767a0f46f66b1cdf38c650a
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage_1_and_2.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: aa9556509f8249b9e82f6208297311c69e25eb6e560e64c7670fe3bb928436b3
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage3.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: ccee95e1b4c7d43cb3523bc94a793411dafe15bd23c3cb7c348cb093168c7d42
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/partition_parameters.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: c7866c302ef1a9757b0c437254e369f8934a2f7ceb371f6f7e54a5391d10c311
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/partitioned_param_coordinator.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: a52014bb6bb754ba315c9f58eb6d5ee52781e7da154f939c7d0c70eb9cbf5e2a
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/parameter_offload.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 7fec7e04a5d00a56ff88029242ea12c3dcd1a48d1c08aa868137d24f01efe340
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_config.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 3e240d16f1581bc1e8db115f211bcfb2f395d58e39b0a43ef7fa3e6c4bfb8545
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_context.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 0942060bc6e3c121e6dde772dc1757b577021f327b6072743e9a9fa61c39a651
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_stale_handle_wait.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: a06caf747dd654b3cda2559cb8de569ac7769d690a6bd2bd30f20134e4e78f73
---

# DeepSpeed ZeRO：分片、参数预取与 offload 生命周期

## 问题与配置入口

ZeRO 要减少的是模型训练状态的重复驻留，但训练时仍有全量模块参数、通信 bucket、activation 和临时转换存储。选择 stage 后不能只按静态状态除 DP 估算运行峰值。

| stage | 被分片的训练状态 | 主要代价 |
| --- | --- | --- |
| 1 | optimizer state | step 后参数同步，参数/梯度仍有复制 |
| 2 | optimizer state、gradients | 反向归约/分片，参数仍有复制 |
| 3 | 再加 parameters | 模块执行前 gather；trace/prefetch/release 对性能及峰值重要 |

[`DeepSpeedZeroConfig`](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/deepspeed/runtime/zero/config.py)限定 `offload_param` 只适用 stage 3，`offload_optimizer` 支持 1/2/3；部分 optimizer offload 的 ratio<1 只支持 stage 3。旧 CPU offload 布尔项有弃用路径，优先使用结构化配置，不同时混搭两代字段。

`reduce_bucket_size`、`allgather_bucket_size`、`stage3_prefetch_bucket_size` 是**参数元素数量**；按对应 dtype 计算 byte，另记并发 buffer、精度转换与 state。`contiguous_gradients` 让连续 buffer 避免碎片/便于归约，offload 路径也强制这一布局；它不是“无需额外 buffer”。

## 参数状态和实际执行顺序

[`partition_parameters.py`](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/deepspeed/runtime/zero/partition_parameters.py)以 `NOT_AVAILABLE`、`INFLIGHT`、`AVAILABLE` 跟踪分片参数。完整参数只在相应执行生命周期可用。共享参数/external parameter、重算和 leaf module 会延长或改变释放时机。

[`PartitionedParameterCoordinator.fetch_sub_module`](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/deepspeed/runtime/zero/partitioned_param_coordinator.py)的固定实现大致为：

1. leaf backward 需要时通过锁和完成事件协调并发 fetch。
2. 找出当前模块尚未可用的参数并发起 gather；在使用前等待各参数对应 handle，校验状态为 AVAILABLE，并处理当前计算流与 gather 流依赖。
3. 完整 trace 已建立时，从参数访问队列预取后续参数；受 `max_live_parameters` 与 prefetch bucket 限制，NVMe 分片还有单独预取路径。
4. 模块执行/反向结束进入 `release_sub_module`：移除活动使用者，只在没有阻止释放的所有权时重新分片；persistent、external、重算和 fast leaf 路径各有条件。

源码函数开头的注释描述“先预取再等待”，而当前函数体是在必要参数 wait 之后处理 trace prefetch；调优应按函数体与实际 trace 判断，不用注释当异步重叠的证据。

第一次执行记录模块和参数顺序；`reset_step` 检查跨 rank 一致后将 trace 置为 complete。依赖输入的不同分支、专家路由或不一致 hook 顺序可能使 trace 失效，不能把第一次迭代当成稳态 prefetch 表现。完整 trace 中 queue 与实际模块不匹配会报错，是需要定位动态控制流的线索。

## 参数选择、收益与代价

| 参数/机制 | 想解决的问题 | 需要同时观察 |
| --- | --- | --- |
| persistence threshold / model persistence cap | 高频小参数避免多次 gather、小消息 | 常驻显存增加，checkpoint/生成峰值还有全参数 |
| prefetch bucket / max-live / reuse-distance | 提前拿参数，减少下一模块等待 | 预取是否命中、同时活跃参数、重复 fetch、OOM |
| module granularity / leaf | 多个细碎 hooks/gather 的主机开销 | 模块级完整参数的峰值及共享/重算参数正确释放 |
| `stage3_use_all_reduce_for_fetch_params` | 减少 host concat/slice 一类开销 | collective、通信量与特定输入实际收益 |
| `stage3_allgather_sequential` | 避免大 coalesced flatten 临时存储 | 消息次数/启动等待上升；不是同时满足最低延迟和最低峰值 |
| optimizer/parameter CPU 或 NVMe offload | 设备状态放不下 | CPU RAM、pinned memory、NUMA、copy/I/O/CPU optimizer 与计算的关键路径 |

`overlap_comm` 未填写时 stage 3 默认开启，其他 stage 默认关闭。记录解析后的配置。开关只声明允许路径，收益必须由通信是否被计算覆盖来确认；同时它改变 buffer 复用和 stream 依赖。

## 异步所有权与局部验证

[`stage_1_and_2.py`](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/deepspeed/runtime/zero/stage_1_and_2.py)有 reduce stream 的 `wait_stream`、`record_stream` 和 CPU 梯度累计/拷贝路径。不能把 Python 引用消失、`param.grad=None` 或 step 结束当成异步设备消费者完成。关 overlap 之后也可能保留异步 copy，因此是定位对照，不能证明所有权安全。

一个容易遗漏的 ZeRO-3 状态问题是 **同一个 coalesced gather handle 被多个参数引用**：第一次 wait 使参数可用，模块结束重新分片后，第二次 wait 不能把已释放参数再次标为 AVAILABLE。否则下一次 fetch 可能跳过 gather，计算在空参数上执行。[`test_zero_stale_handle_wait.py`](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/tests/unit/runtime/zero/test_zero_stale_handle_wait.py)直接构造这个循环，分别覆盖 gather 与单 rank no-gather，是真实状态契约测试。

验证从 `test_zero_config.py` 的解析、`test_zero_context.py` 的 gather/修改/重新分片到所用 stage 的多 rank forward/backward/step；共享参数、无 grad 的 block input、重算、MoE leaf 与 offload 必须纳入使用该特性时的回归。数值对照保留无 offload/无 overlap 基线，记录 norm、更新后的参数及阶段 loss，性能记录分片总量和 dtype。

## 回退与更新

出现 trace/stream/state 问题，先缩成相同控制流的局部用例，保留各 rank 的访问顺序和状态日志。可回退预取/overlap/leaf 优化或换保守 stage；不要删除必要同步以掩盖错误。HCU 上还需查该分支 accelerator、collective 和 allocator 语义，不能由官方 CUDA 测试推断通过。

本页未在 HCU 实测。更新 coordinator、partition handle、offload buffer 或配置字段时，联动[总览](../../deepspeed.md)、checkpoint 专题和对应 PR；固定旧证据完整不表示最新分支仍有相同生命周期。
