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
reviewed_on: '2026-11-18'
coverage: selected mechanisms, recipes and tests at pinned official source; not every
  model/backend and no HCU runtime execution
sources:
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/config.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 982bc8974c4a70665f1450dd96f843454626eb95aeebe5887305ac6e48548743
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage_1_and_2.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 0dd8a8c856a90e2aa0dae70d8d03f961d1b346800fdcabbf8e29ed149aec8bd8
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage3.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 64f3afdbacb757b0d8c0a9c08a4b6b6958b0bcbf597fd2eebd5a5c47821701cd
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/partition_parameters.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: a6e86a76cf3101f01746ad5e0c190fc51139b921b8b86d828140f107e1469449
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/partitioned_param_coordinator.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: a43fd966c88dc3699f5b18e2bfe51fac222e79365664addce9ed485d617a78d0
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/parameter_offload.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 7fec7e04a5d00a56ff88029242ea12c3dcd1a48d1c08aa868137d24f01efe340
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_config.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 3e240d16f1581bc1e8db115f211bcfb2f395d58e39b0a43ef7fa3e6c4bfb8545
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_context.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 0942060bc6e3c121e6dde772dc1757b577021f327b6072743e9a9fa61c39a651
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_stale_handle_wait.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 76b5a3cbeda906e00e3565c00fb2a0b5026d8dee43550f1af1f4acd453326565
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_tensor_fragment.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: ebbd12aa05d351d3d0c76b559acaaff219ea6b4830cee1b47ea4d8a5883f3cd5
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/config.py
  commit: 5420b75de3226e95b6412ed2d95380c0a819c89a
  sha256: 34033db3576399499f67ed1b37d90c279a0506dd2b5bddda1715f3c189592f73
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/engine.py
  commit: 5420b75de3226e95b6412ed2d95380c0a819c89a
  sha256: 97cf4fac9f0cfdb1e1ac5a289d2a4ec312843274c4c1c08bb6e8c1225c9de75e
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage_1_and_2.py
  commit: 5420b75de3226e95b6412ed2d95380c0a819c89a
  sha256: 61e0f21a348f3c98c44c32225ab25e1beddced12f36388a578acb1a608a8a454
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage3.py
  commit: 5420b75de3226e95b6412ed2d95380c0a819c89a
  sha256: d0abe8464970a378791847f64599395a26fbf5cca830676d9dffb4da5ddea1e3
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/partition_parameters.py
  commit: 5420b75de3226e95b6412ed2d95380c0a819c89a
  sha256: 5d10e92b8ba6835cc47ef84dbd25442a6752b6ffdc0232da3478ccc858033740
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/parameter_offload.py
  commit: 5420b75de3226e95b6412ed2d95380c0a819c89a
  sha256: 782d5dd87205f6d8938d7a0beab230c8523a37ca2b3b32a935fd6f21132db0b9
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/partitioned_param_coordinator.py
  commit: 5420b75de3226e95b6412ed2d95380c0a819c89a
  sha256: 17d04b568e7d1fd15d6cfdce465cd8cb36e81e259e846db82304e637b7b27fee
- source: deepspeedai-deepspeed
  path: deepspeed/ops/adam/cpu_adam.py
  commit: 5420b75de3226e95b6412ed2d95380c0a819c89a
  sha256: 8af512c18359b51668bb02392ef851f1e3539d30e030c9c518157c4fabd10767
retrieved_on: '2026-11-18'
---

# DeepSpeed ZeRO：分片、参数预取与 offload 生命周期

## 问题与配置入口

ZeRO 要减少的是模型训练状态的重复驻留，但训练时仍有全量模块参数、通信 bucket、activation 和临时转换存储。选择 stage 后不能只按静态状态除 DP 估算运行峰值。

| stage | 被分片的训练状态 | 主要代价 |
| --- | --- | --- |
| 1 | optimizer state | step 后参数同步，参数/梯度仍有复制 |
| 2 | optimizer state、gradients | 反向归约/分片，参数仍有复制 |
| 3 | 再加 parameters | 模块执行前 gather；trace/prefetch/release 对性能及峰值重要 |

[`DeepSpeedZeroConfig`](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/deepspeed/runtime/zero/config.py)限定 `offload_param` 只适用 stage 3，`offload_optimizer` 支持 1/2/3；部分 optimizer offload 的 ratio<1 只支持 stage 3。旧 CPU offload 布尔项有弃用路径，优先使用结构化配置，不同时混搭两代字段。

`reduce_bucket_size`、`allgather_bucket_size`、`stage3_prefetch_bucket_size` 是**参数元素数量**；按对应 dtype 计算 byte，另记并发 buffer、精度转换与 state。`contiguous_gradients` 让连续 buffer 避免碎片/便于归约，offload 路径也强制这一布局；它不是“无需额外 buffer”。

## 参数状态和实际执行顺序

[`partition_parameters.py`](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/deepspeed/runtime/zero/partition_parameters.py)以 `NOT_AVAILABLE`、`INFLIGHT`、`AVAILABLE` 跟踪分片参数。完整参数只在相应执行生命周期可用。共享参数/external parameter、重算和 leaf module 会延长或改变释放时机。

[`PartitionedParameterCoordinator.fetch_sub_module`](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/deepspeed/runtime/zero/partitioned_param_coordinator.py)的固定实现大致为：

1. leaf backward 需要时通过锁和完成事件协调并发 fetch。
2. 找出当前模块尚未可用的参数并发起 gather；在使用前等待各参数对应 handle，校验状态为 AVAILABLE，并处理当前计算流与 gather 流依赖。
3. 完整 trace 已建立时，从参数访问队列预取后续参数；受 `max_live_parameters` 与 prefetch bucket 限制，NVMe 分片还有单独预取路径。
4. 模块执行/反向结束进入 `release_sub_module`：移除活动使用者，只在没有阻止释放的所有权时重新分片；persistent、external、重算和 fast leaf 路径各有条件。

源码函数开头的注释描述“先预取再等待”，而当前函数体是在必要参数 wait 之后处理 trace prefetch；调优应按函数体与实际 trace 判断，不用注释当异步重叠的证据。

第一次执行记录模块和参数顺序；`reset_step` 检查跨 rank 一致后将 trace 置为 complete。依赖输入的不同分支、专家路由或不一致 hook 顺序可能使 trace 失效，不能把第一次迭代当成稳态 prefetch 表现。完整 trace 中 queue 与实际模块不匹配会报错，是需要定位动态控制流的线索。

当前 `d8241a9ba266405e1a58fadf19e24b2370f6d7fa` 把 `all_gather_coalesced` 的 `ds_id` 排序提前到按partition group分批之前。prefetcher可能给出跨rank迭代顺序不同的set；只保证每组内部flatten顺序仍不够，组间collective次序也要相同。新增 `TestMultiGroupGatherOrder.test_rank_dependent_param_order` 用两个同成员但不同对象的group和相反参数列表验证权重仍正确，不能把group成员相同当成collective可任意互换。

2026-11-04 的 coordinator 与前轮 trace/wait/release 消费链字节相同，因此当时保留旧结论；2026-11-18 的新版本另有下述实例缓存、NVMe 去重与销毁修订。旧 stale-handle 测试继续保留，新排序也不免除 handle 完成和参数释放后的状态检查。

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

[`stage_1_and_2.py`](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/deepspeed/runtime/zero/stage_1_and_2.py)有 reduce stream 的 `wait_stream`、`record_stream` 和 CPU 梯度累计/拷贝路径。不能把 Python 引用消失、`param.grad=None` 或 step 结束当成异步设备消费者完成。关 overlap 之后也可能保留异步 copy，因此是定位对照，不能证明所有权安全。

一个容易遗漏的 ZeRO-3 状态问题是 **同一个 coalesced gather handle 被多个参数引用**：第一次 wait 使参数可用，模块结束重新分片后，第二次 wait 不能把已释放参数再次标为 AVAILABLE。否则下一次 fetch 可能跳过 gather，计算在空参数上执行。[`test_zero_stale_handle_wait.py`](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/tests/unit/runtime/zero/test_zero_stale_handle_wait.py)直接构造这个循环，分别覆盖 gather 与单 rank no-gather，是真实状态契约测试。

验证从 `test_zero_config.py` 的解析、`test_zero_context.py` 的 gather/修改/重新分片到所用 stage 的多 rank forward/backward/step；共享参数、无 grad 的 block input、重算、MoE leaf 与 offload 必须纳入使用该特性时的回归。数值对照保留无 offload/无 overlap 基线，记录 norm、更新后的参数及阶段 loss，性能记录分片总量和 dtype。

## FP32 累积的归约结果与 compact partition

当参数是低精度、`gradient_accumulation_dtype==torch.float32` 且不属于排除的 Muon group 时，`_use_compact_grad_partition_buffer` 启用 owned local FP32 partition。`get_gradient_for_reduction` 不再把 `grad_accum` 先转换为参数 dtype；`_gradient_reduction_buffer_dtype` 区分 ZeRO-1 累积 staging 和 ZeRO-2 低精度 staging。`allreduce_bucket` 返回通信结果 tensor，各 allreduce/reduce-scatter 路径在回写低精度 staging 之前把属于本 rank 的片段加到 FP32 partition；noncontiguous fallback 也有单独的 preserving-FP32 路径。

这同时是精度与所有权契约：通信 dtype 为 FP32 并不保证中间保存不会丢精度，不能只检查 JSON。`GradPartitionBufferGroup` 用一个 flat partition 和多个 view 表达有效梯度/对齐 padding；动态 offload/reload 调用 `move_flat_partition` 搬迁整块并重建 view，避免一组 tensor 和 optimizer 消费的底层存储脱节。CPU optimizer offload 在累积边界从 owned FP32 slice 计算 norm、跟踪 overflow 并向 CPU 目标拷贝，保留既有 copy 完成等待。

复用时逐项记录参数/累积/通信 dtype、ZeRO stage、contiguous 与 reduce-scatter/overlap、CPU offload、累积 microbatch 数和实际 optimizer。FP32 partition 仍占本 rank 的状态内存，不能当成零额外缓存；Muon 例外、其它 dtype 和 stage-3 的不同代码路径不能混作同一分支。现有 `check_grad_overflow` 对 BF16 的判断也保留配置条件，不能从代码里出现 overflow tracker 推导所有配置都强制检查 NaN。

固定上游 `TestZeroBf16Fp32GradAccum` 用两 rank、BF16 参数、FP32 通信/累积与四次 microbatch，构造 BF16 无法精确表示的平均梯度并要求 `safe_get_full_grad` 返回逐位精确 FP32 结果；覆盖 stage1、stage2、stage2 CPU offload、非连续梯度及 stage3。另一测试 offload/reload 梯度后用 `safe_set_full_grad` 置零，再验 optimizer 不更新权重，直接检查 view/消费者身份。本轮仅阅读这些测试，未执行分布式或 HCU 回归。除局部梯度外仍需实际参数更新、恢复和阶段 loss 验收。

## CPU offload 的参与窗口与 pinned master

ZeRO-1/2现在按 **每个参数是否在本step窗口参与过backward** 判断host accumulator是否有效，不再仅用全局 `micro_step_id>0`。首次在boundary出现的FP32-master梯度可以先保留在owned partition，`_offload_partition_only_param_ids`防止finalize从旧host buffer覆盖；若step前又backward，恢复本rank片段后再累加。`all_grad_tensors`在非reentrant累计路径保留运行和直至step，使用累计grad_accum的reentrant路径则重新读取而非重复加总。验证要含分支中晚出现参数、多次boundary但尚未step及未参与参数，不能只测所有参数每微批都活跃。

ZeRO-3 CPU optimizer offload在构造时可pin CPU master，`_copy_pinned_master_to_device`先以master原dtype传设备再cast，并记录event后 **host synchronize**，确保下一forward的独立allgather stream拿到新值。函数里有non_blocking copy不表示这段端到端无等待；NVMe swapper管理的subgroup另走其生命周期。destroy还对构造时pin的master解pin。

checkpoint的FP32 master来源和optimizer状态加载已分开，`load_from_fp32_weights`不再控制Engine完整恢复，见[checkpoint专题](pipeline-schedule-and-checkpoint.md)。这与梯度累积是否保留FP32是两个不同边界。

## 2026-11-18：累积窗口、CPUAdam 与混合 dtype

以下按官方固定 `5420b75de3226e95b6412ed2d95380c0a819c89a` 的已读实现说明；前述 `d8241a9b` 的机制证据保留适用版本，未在本轮运行上游或 HCU 分布式测试。

### ZeRO-1/2 host ownership 与保留设备梯度

`accumulated_grads_in_cpu` 改为按 optimizer group 懒分配的一份 owned partition，首次非 boundary 累积才申请；GAS=1 不为这条 accumulator 另 pin 一份全参数副本。`_offload_unpublished_param_ids` 跟踪最后贡献发生在非 boundary 的参数，boundary 即使没有该参数的 backward，也必须发布其 host sum，供 norm、`safe_get_full_grad` 和 step 消费。回归不能只覆盖所有参数每个 microbatch 都参与的模型。

compact partition 在 boundary 先按本窗口所有参与参数计算 norm、拷到 host，并检查转换后 host dtype 的 overflow；FP32 有限值转成低精度仍可能溢出。只有 host 精确保存该累积值、既有 safety 路径启用且未设置保留时，才释放设备 partition 并将其标为 host-owned；下一次 backward 等 copy 后重建、恢复该累积和。允许精确恢复的条件是相同 dtype，或 FP32 host 保存从 BF16/FP16 扩宽的值，不是任意低精度 host 都可替代 FP32 累积。step/overflow 跳过与重置须清空残留和全部参与 ID。

配置 `retain_gpu_grad_partition_until_step` 默认 False，官方 config 将其描述为 ZeRO-2 CPU offload/FP32 累积的容量与复用取舍；共享实现的实际准入仍要按所用 stage/optimizer 查证。True 会把 compact partition 留到 step，增加该 rank 一份对应 dtype 的 partition 驻留，避免释放后再恢复；**当前 `_offload_compact_grad_partitions` 在检查 True 前已经执行 host copy**，不能照配置注释将其写成消除了每次 D2H。测量请求间恢复、copy、CPU/设备峰值及整体更新，不能仅数 allocation。原有 ready/reuse/record-stream 和 copy 完成保护继续成立。

### ZeRO-3 fused CPUAdam scale 与 BF16 回传

`_grad_scale_for_cpu_adam` 只在 DeepSpeedCPUAdam 的 CPU subgroup、FP32 master/gradient，且无 GradScaler、ZenFlow、NVMe swap、Muon并有原生支持时，把 unscale/clip 因子交给 `step(grad_scale=...)` 在加载梯度时融合。梯度存储本身暂未改写，`_deferred_grad_scale` 必须在下一步 overflow 检查、公开梯度读取/修改等边界，对未被新窗口覆盖的部分补齐；不能绕过这些 API 直接读取旧 raw gradient 宣称状态不等价或删除 bookkeeping。

满足上述条件，且目标设备 partition 为 BF16、`offload_optimizer.pin_memory` 启用、CPUAdam `copy_supported()` 时，`_cpu_adam_step_and_copy_back` 将更新和 BF16 量化写入两个交替 pinned buffer，再分块 H2D。复用一个 buffer 前等它上一轮 copy，最后一次 copy 的 event 在返回前 host synchronize，确保下一 forward 的独立 gather stream 看到新参数。它不是所有 CPU optimizer、dtype 或 NVMe 的通用快路。默认两个 `2**26` 元素 BF16 buffer 在首次走此路径时合计 **256 MiB pinned memory**，与 master、gradient 和通信临时量一起计入主机预算。源码声明保持 FP32 更新与 BF16 舍入契约，需按实际 CPU 指令实现和训练更新做回归；不能用源码声明代替收益或 HCU 数值验收。不满足条件时仍走原 pinned-master copy/cast 和完成等待。

### 保留 FP32 参数、offload 与销毁

`data_types.keep_in_fp32_modules` 从仅 buffers 扩到匹配的 parameters，但 engine 只允许 **ZeRO-3 且无 parameter CPU/NVMe offload** 的低精度模型保留 FP32 参数；不兼容的显式请求硬拒，AUTO 仅告警并保留 buffers。不能将 optimizer CPU offload 与 parameter offload 混为同一条件。相应 FP32 参数用 FP32 通信/累积，参数扁平区、梯度区与 bucket 按 dtype 拆分，all-reduce fetch 也按 dtype 分组。小 FP32-only bucket 的缩容不表示所有 bucket 都可任意缩小，异常后重入 backward 仍有边界。

设备上已为 FP32 的 subgroup 可让 master 与 weight partition alias，动态搬迁必须恢复这个共享身份。`offload_states` 对混合 dtype 的 `lp_params/lp_grads` 明确拒绝；只 offload `hp_params` 也不能释放仍与 `lp_params` alias 的那份设备存储。避免按“FP32 master 一律有第二份”计算收益，或忽略硬拒而把部分状态迁移当成全量 offload。

coordinator 的 release LRU 改为实例缓存，NVMe prefetch 对访问队列的重复参数去重。engine/parameter-offload 的 destroy 清理 hooks、全局 forward stack 与参数 optimizer 反向引用，并限制重复 destroy 误删新 engine 的条目；多次构建对照实验仍需核对实际引用、pending copy 和 pinned buffer 释放，不能靠丢 Python 变量证明内存已回收。

## 回退与更新

出现 trace/stream/state 问题，先缩成相同控制流的局部用例，保留各 rank 的访问顺序和状态日志。可回退预取/overlap/leaf 优化或换保守 stage；不要删除必要同步以掩盖错误。HCU 上还需查该分支 accelerator、collective 和 allocator 语义，不能由官方 CUDA 测试推断通过。

本页未在 HCU 实测。更新 coordinator、partition handle、offload buffer 或配置字段时，联动[总览](../overview/engineering-guide.md)、checkpoint 专题和对应 PR；固定旧证据完整不表示最新分支仍有相同生命周期。


## 本轮补充固定证据

- [tests/unit/runtime/zero/test_zero_tensor_fragment.py](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/tests/unit/runtime/zero/test_zero_tensor_fragment.py)
