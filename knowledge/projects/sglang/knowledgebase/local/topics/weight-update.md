---
id: engines/sglang/weight-update
title: SGLang 权重同步：会话、混合 dtype 与缓存一致性
engine: sglang
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-11-04'
coverage: reviewed implementation chains and official guides; not all models, backends or HCU runtime qualification
sources:
- source: sgl-project-sglang
  path: docs/docs/advanced_features/sglang_for_rl.mdx
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 68ed10e2b44ce57413380df288feb3dc0b1f8a6b650589cf6ba97a340566b20f
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler_components/weight_updater.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 2e65bb16c08c45f126666e2109d8fdf3139e37fccc9b889a6e4f4692bd8b1032
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: d6158d7d4271ef93991e69965f101a183b63f33baa041468cf83355a24d474f0
- source: sgl-project-sglang
  path: python/sglang/srt/managers/tokenizer_manager.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 5a34747dfc5592c45b4e8a82c1ad767e4e57cade786eedc9ddf94bd37926ef30
- source: sgl-project-sglang
  path: python/sglang/srt/weight_sync/tensor_bucket.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: a4b7bcf408954a2443c6ecc8f78b2c932f72abf3308e0d0ee922161023be470c
- source: sgl-project-sglang
  path: test/registered/rl/test_update_weights_from_distributed.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: a76b527b0aeb9397288bcb7f1d653934d248e077031ba03c636cd0e792ce1e1e
- source: sgl-project-sglang
  path: python/sglang/srt/model_executor/model_runner_components/weight_updater.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: ff30b299cc3672fff0970fee1afd9fb85c31db3fb990d9132f7f7a8e7d4f5c00
- source: sgl-project-sglang
  path: python/sglang/srt/model_executor/model_runner_components/weight_exporter.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 36ded4febd1682e387f537103ec8c099efd9a2df6c464c61b4226295ac88bf2a
- source: sgl-project-sglang
  path: python/sglang/srt/model_loader/loader.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: bd88c390348f1687414600c841724e1d835e5df83d32a2177929b5f699c35b56
- source: sgl-project-sglang
  path: python/sglang/srt/model_loader/weight_utils.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 5d6ae761e2ce485ea20991184e7c46c6ae6676b6c62586cbd025bbd1ad27f89a
- source: sgl-project-sglang
  path: python/sglang/srt/checkpoint_engine/checkpoint_engine_worker.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 743478af6c281abb483153ab46cce6d6284c6625c9544035c9c9ebc4d55fb461
- source: sgl-project-sglang
  path: test/registered/unit/model_executor/test_derived_weight_cache.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 834d8a7ba689b1cc9ff1aebf25e6645c480fe37ba1989938eb8854507e244b04
- source: sgl-project-sglang
  path: test/registered/unit/model_executor/test_weight_update_tensor_rank.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: b66356d7813de03b4c69dae1796e52af2d820886805016295087eafbfb3867c8
- source: sgl-project-sglang
  path: python/sglang/srt/managers/tokenizer_control_mixin.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 768a0c85aa39f8b56c875f6440195d38d5ae8b3d6307fd532ac97dfc7042e0f1
- source: sgl-project-sglang
  path: python/sglang/srt/managers/io_struct.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: ffabefb816db79855af39bb5e65de075ac13bf6edcc4a3468e1d3f49a5684082
- source: sgl-project-sglang
  path: python/sglang/srt/entrypoints/engine.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: cc13ef61843629907135f3258ac3efceca1da95e1e959cba77c72e1e0b405033
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/kv_weight_version_tracker.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 43688f519119233fe8c3f56d4ff658a70340fb3145a45e4b8f73c109791add05
pr_sources:
- pr-sgl-project--sglang-42561
- pr-sgl-project--sglang-43758
---

# SGLang 权重同步：会话、混合 dtype 与缓存一致性

## 问题和阅读链

RL 更新不仅是搬运参数：训练端完成 optimizer 后，多个生成副本需要安装同一 policy version，并消除旧权重对应的 KV、图/量化派生状态和在途样本歧义。读取 [工程总览](../overview/engineering-guide.md)确认消费者版本，再沿 `Engine/tokenizer_manager` 的控制请求→Scheduler 类型分发→`SchedulerWeightUpdaterManager`→worker/model-runner updater→模型 loader；训练 export 端同样要读，不能只改 receiver。

## 选择传权方式

| 方式 | 适用问题 | 必须核对的成本和契约 |
| --- | --- | --- |
| `update_weights_from_disk` | checkpoint 为共同真源、增加 rollout 实例 | 文件完成状态、格式、存储读带宽与恢复来源 |
| `update_weights_from_tensor` | 同机/共卡、可传 tensor 的消费者 | 序列化/IPC、tensor ownership、会话、buffer 最后使用 |
| `update_weights_from_distributed` | 训推分离或跨节点 | 专用更新组、rank映射、dtype/shape/顺序、所有 rank 同时参与 |
| IPC/专用 transport | checkpoint-engine 等明确接入 | 平台 ABI、句柄存活、异步完成、发送/接收两端版本 |

`init_weights_update_group`只是建立通信，不代表任一更新已完成；被更新模型、target/draft selector 和各TP rank仍须一致。HCU 先核对支持的 fork transport，不能因接口叫 NCCL 就直接假定任意 RCCL 路径或设备 IPC 等价。

## 当前会话边界与部分失败

当前 manager 的 tensor/distributed 路径要求 `begin_weight_update()`→一次或多次更新→`end_weight_update()`。begin 记录 selector、准备各 runner，end 对同组 runner 做收尾；重复 begin 或会话外 update 返回失败。`loaded_weights`当前是会话级状态，不是逐runner全部状态证明。

begin 当前先对所选全部 runner 调用派生权重缓存检查，任何一个不支持即在本 manager 开始 restore 前返回失败；这也覆盖绕过普通 load 的 P2P/RDMA 写入方。检查通过后才逐 runner 调用 `restore_weights_before_loading` 撤销部分量化原地 packing，记录会话并做 TP barrier。此提前检查缩小了拒绝前的副作用，但不是跨 rank 的事务：各 rank 配置和判断必须一致，后续 prepare/load/end 仍可能失败。

`loaded_weights` 仍是会话中的一个 bool：只有一次更新所选 runner 全部成功才设为真，不能表示每个角色分别完成了哪一步。end 使用 begin 保存的 selector，并以 `not loaded_weights` 决定是否执行 post-load，之后再清会话和 barrier。target 已写、draft 失败或 end 抛异常时可能留下部分参数、layout 或开放会话；没有逐 runner 日志或快照式回滚。

调用方还要保持 selector 一致：manager 仅检查会话存在，各次 update 用该请求的 selector，end 才用 begin 保存的 selector；未逐次校验二者相等。当前 Python Engine 的 begin 暴露 selector，而 tensor/distributed update 封装默认请求 all，不会自动继承 begin 的 target/draft 选择。tokenizer 的锁按各次控制调用取得，并非覆盖整个 begin→end 窗口的持续隔离；tensor/distributed/IPC 控制入口还要求服务内部 DP size 为 1。多个独立 rollout 副本仍由训练消费者协调，不能由一次 RPC 推出全部副本同步或整个窗口已排空。

主干固定版本已经包含 [PR #43758](https://github.com/sgl-project/sglang/pull/43758)：`flush_cache_after_weight_update`在请求仍运行/排队时返回 `success=False`，服务不再因 assert 退出。**权重可能已经写入，weight version 也可能已经记录，失败响应不会把新参数回滚。** 应排空或按支持方式 retract 后显式 flush，再检查全部副本；不能将请求超时/400视为“完全没有修改”而盲目重试。

[PR #42561](https://github.com/sgl-project/sglang/pull/42561) 提议逐 runner 记录已加载角色，处理 target 成功、draft 失败后的重复 post-load/旧 KV 问题。2026-11-04 复查其状态为 closed、未合入；2026-11-01 的关闭说明是闲置 PR 数量超软上限，并非技术问题已解决。当前固定 main 仍无该 per-runner 记账。使用 draft 时检查每个 runner 的结果和缓存；失败后拒收该不一致轮次的样本，保留可恢复版本。

## 在线更新的门禁与派生权重

runner 的 `WeightUpdater` 在 disk、tensor、distributed load 和 checkpoint-engine IPC 加载入口检查派生权重缓存：补偿 mHC 的 TF32/BF16 splits、HPC-Ops bf16xfp32 GEMM 的缓存 splits，以及模型模块声明的 `_derived_weight_cache_error` 均可能拒绝更新。原因是原地写参数不能刷新这些派生值，captured graph 还可能保留旧引用；flush KV 不能修复这种不一致。门禁条件应在启动时确定并在各 rank 一致，不能让部分 rank 继续 collective、部分 rank提前退出。

具体 load 入口仍保留门禁；会话 begin 已通过并不保证后续请求无副作用：distributed manager 先接收权重再逐 runner 加载，tensor manager 先反序列化，而 begin 可能已经还原 packing。独立的 `weight_cache_mode != off` 门禁还禁止原地更新共享 daemon 的权重；disk/distributed/IPC 会检查该模式，tensor 路径也检查。共享权重模式与普通一次性 IPC payload 的 ownership 不同，详见 [共享权重与 sleep](memory-and-scheduling.md#共享权重与sleep的边界)。

普通 tensor payload 按部署 TP rank 取对应的 `LocalSerializedTensor` 条目，不能用 draft 内部缩小后的 attention-TP rank 索引。`direct` 路线按模型现有参数名调用默认 loader，非标量要求 shape 一致；它不自动完成训练端到推理端的合并 QKV、专家分片或量化转换。对应 rank 单测只断言该索引选择，不证明任意模型布局和 dtype 数值等价。

## 磁盘重载、IPC 收尾与导出失败

disk 更新当前只接受 `DefaultModelLoader` 及其子类，冷启动支持的其他 loader 不能自动视为支持在线重载。当前 disk 路线也在实际 load/postprocess 前执行 `restore_weights_before_loading(model, target_device)`；必须将恢复布局和后续收尾一起验收。代码先把 `model_config.model_path` 改为本次请求路径；加载异常后虽然日志写“Rolling back to original weights”，重试 iterator 仍从这个已改路径构造，未保存旧参数快照或旧路径。因此该日志不是恢复原 policy 的证明，重试自身也可能失败；以实际参数、配置和可信完整版本确认恢复。

checkpoint-engine IPC 使用独立 worker 封装；其量化/模型 post-hook 异常在该封装中仅记 warning，没有重新抛出。上层 RPC 因而可能返回成功而收尾未完成。验收同时检查 post-hook 日志、scale/派生状态和固定输入数值，不能以“IPC 已完成”替代模型可用。`WeightExporter` 另尊重模块的 `_weight_export_error`。当前远端 seed/send 可直接返回 `(False, reason)`，`get_weights_by_name` 可返回 `None`，保存请求则可能转成失败 RPC；调用者须核对业务结果，不能只验传输或 HTTP 返回。接收 API 存在不保证该模型能作为导出端。

loader 的 post-load 还包括设备特定 padding、共享专家配置决策和模块自己的 `refresh_gemma_weight` / `refresh_conv_weights`；IPC cache 的别名恢复同样改用后者，不能只补参数而跳过派生状态。PT 文件加载现在坚持 `weights_only=True`，移除了 legacy tar 的非安全加载回退；旧 checkpoint 格式失败应先确认格式/转换与可信来源，不以关闭限制作为通用恢复。dummy 初始化的 uint8 `weight_scale_inv` 使用 UE8M0 中性值 127，这不是在线 refit 已获得真实 scale 的证明。

## Flat bucket：字节与生命周期

`FlattenedTensorBucket`先对每个tensor `flatten().view(torch.uint8)`，用`torch.cat`形成packed buffer。metadata包含name、原shape/dtype和start/end/numel；这里offset与numel来自uint8视图，表示**字节**。例如同一bucket中BF16与FP32不能按原元素数累计offset。

`reconstruct_tensors`按字节切片→view原dtype→reshape，得到的tensor可共享flat storage。减少逐tensor消息和额外接收copy的收益，依赖发送/接收协议一致且buffer在最后一次异步load前保持存活。若非连续tensor先flatten产生副本，也应算进峰值；bucket增大会增加host/device临时占用，不把“更大bucket”当无条件更快。

metadata验证应覆盖名字唯一性、shape/dtype、字节范围/对齐和完整顺序，真正加载还要核对合并QKV、专家布局、tied权重、量化scale及target/draft版本。不能用均匀BF16小模型证明混合dtype大MoE传权正确。

接收端新增 `FlattenedTensorBucket.empty(names,dtypes,shapes,device)`：按声明 dtype/shape 计算 byte ranges，一次分配 uint8 receive buffer，避免为构造 bucket 先建各参数空 tensor 再 cat/copy。入口用 strict zip 拒绝元数据长度不等，拒绝负维、未按 dtype itemsize 对齐的 offset 和零项 bucket；不会自动插 padding 修正不合法布局。它降低准备阶段副本，但仍需完整接收 buffer、load 完成和存储存活，不能把分配成功当作数据已接收或 session 已提交。

## Pause、旧 KV 和 policy 归属

`pause_generation(mode="in_place")` 当前只停止继续调度，保留 running batch/队列状态；它不是服务全空闲。retract 会处理 overlap 在途结果、decode-offload 和可重启请求；PD decode 已发握手的请求也须退出旧状态并在 continue 前重新 bootstrap。当前 PD prefill 对未完成的 mid-chunk 请求仍有显式 TODO：因为 KV sender 生命周期而保留，跨更新后可能带有旧权重 prefix。不能声称所有 retract 路线都会重算为新 policy。

新增 prompt KV 版本观测沿 `KvWeightVersionRecord` 在 forward 捕获目标模型写入的虚拟/原始 slots 和当前 weight version，在结果处理后记入 tracker。prefill 完成时按 prompt slots 返回连续版本 spans；未写版本会报错。它只支持 generation、非 encoder-decoder、PP=1，且不记录 draft。该功能可揭示混合版本 prefix，但不负责失效、清理或拒收；更新后的缓存和样本准入仍由消费者验收。

一个可靠消费者记录：训练step/参数hash→begin/update/end各rank结果→cache处理→weight version→重新开放生成→样本携带policy version。样本与logprob可追到更新前或更新后某一确定版本，不能让同一次请求静默跨越语义边界。

## 验证、性能分解与回退

局部回归先按真实模型参数名/shape/dtype检查首次和第二次更新，再比较固定输入logits/logprob；覆盖tied权重、多TP rank、target/draft、更新期间排队、RPC失败和重复控制请求。`test_update_weights_from_distributed.py`是实际组/加载验证入口；不能把一次transport广播成功等同模型已使用新权重。

时间分别记录训练export/gather、pack、发送、接收、load/post-load、barrier、cache flush与恢复首请求。端到端吞吐还纳入等待所有rollout副本的尾延迟；临时full tensor和packed buffer分开计峰值。优化传输时先守住当前policy/logprob边界，再减少消息或副本。

恢复来源优先完整可信checkpoint或可重传固定weight version；若实际加载状态未知，先停止生成并检查/重建对应rollout副本，不能随意切回旧KV。训练端恢复由消费者的既有owner统一执行，SGLang更新RPC不负责整个训练checkpoint。

## 固定证据与验证范围

- [docs/docs/advanced_features/sglang_for_rl.mdx](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/docs/docs/advanced_features/sglang_for_rl.mdx)
- [python/sglang/srt/managers/scheduler_components/weight_updater.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/managers/scheduler_components/weight_updater.py)
- [python/sglang/srt/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/managers/scheduler.py)
- [python/sglang/srt/managers/tokenizer_manager.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/managers/tokenizer_manager.py)
- [python/sglang/srt/weight_sync/tensor_bucket.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/weight_sync/tensor_bucket.py)
- [test/registered/rl/test_update_weights_from_distributed.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/test/registered/rl/test_update_weights_from_distributed.py)

- [python/sglang/srt/model_executor/model_runner_components/weight_updater.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/model_executor/model_runner_components/weight_updater.py)
- [python/sglang/srt/model_executor/model_runner_components/weight_exporter.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/model_executor/model_runner_components/weight_exporter.py)
- [python/sglang/srt/model_loader/loader.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/model_loader/loader.py)
- [python/sglang/srt/model_loader/weight_utils.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/model_loader/weight_utils.py)
- [python/sglang/srt/checkpoint_engine/checkpoint_engine_worker.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/checkpoint_engine/checkpoint_engine_worker.py)
- [test/registered/unit/model_executor/test_derived_weight_cache.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/test/registered/unit/model_executor/test_derived_weight_cache.py)
- [test/registered/unit/model_executor/test_weight_update_tensor_rank.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/test/registered/unit/model_executor/test_weight_update_tensor_rank.py)

- [python/sglang/srt/managers/tokenizer_control_mixin.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/managers/tokenizer_control_mixin.py)
- [python/sglang/srt/managers/io_struct.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/managers/io_struct.py)
- [python/sglang/srt/entrypoints/engine.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/entrypoints/engine.py)

- [python/sglang/srt/mem_cache/kv_weight_version_tracker.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/mem_cache/kv_weight_version_tracker.py)


本页在 2026-11-04 复核上述固定源码和教程；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。
