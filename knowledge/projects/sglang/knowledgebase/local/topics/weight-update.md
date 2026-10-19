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
reviewed_on: '2026-10-20'
coverage: reviewed implementation chains and official guides; not all models, backends or HCU runtime qualification
sources:
- source: sgl-project-sglang
  path: docs/docs/advanced_features/sglang_for_rl.mdx
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 751d2c54c7cc87780a7e9005a76930f73a562c6cf4d9db1574bef4eafaeecd76
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler_components/weight_updater.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 7e2f08d8c1ca67965261208f51bab17d0ab0bfd5b87a009d9dbd97fc381542e4
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: fc96ed4b680fdf55621a5397f844cfd4cbd30213f44eec8a888b7cce75cafe60
- source: sgl-project-sglang
  path: python/sglang/srt/managers/tokenizer_manager.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 8ec0f948dfa68fa545616f34c28c7f9fc9d120c1c1d2ebf300cba506ddef1986
- source: sgl-project-sglang
  path: python/sglang/srt/weight_sync/tensor_bucket.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: a4b7bcf408954a2443c6ecc8f78b2c932f72abf3308e0d0ee922161023be470c
- source: sgl-project-sglang
  path: test/registered/rl/test_update_weights_from_distributed.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 0c06da440fd0de2b7250cd17ff6f47506eb22e4341d651fb8d49fdd9d1a2643e
- source: sgl-project-sglang
  path: python/sglang/srt/model_executor/model_runner_components/weight_updater.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 01f96bb8bf1f62558c0329a853c1b047633a9f6a333796ab509dbec8bea41868
- source: sgl-project-sglang
  path: python/sglang/srt/model_executor/model_runner_components/weight_exporter.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: c864b58cb1877eee2413a5c4959e2fc8137e0bced599e34c620f830876d20c77
- source: sgl-project-sglang
  path: python/sglang/srt/model_loader/loader.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 3ced5c62f7422ff487fb71924b391d9a4ffc2597f6f84f3ff936eda0210bd2c5
- source: sgl-project-sglang
  path: python/sglang/srt/model_loader/weight_utils.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 95e185cc57bcdcf93c46a6fcfb9bdc8b9f8be3168e98f11a7deacee107351a24
- source: sgl-project-sglang
  path: python/sglang/srt/checkpoint_engine/checkpoint_engine_worker.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 743478af6c281abb483153ab46cce6d6284c6625c9544035c9c9ebc4d55fb461
- source: sgl-project-sglang
  path: test/registered/unit/model_executor/test_derived_weight_cache.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 47e38d1a5762556a6c24ed0540fca99d304f712edde19b2ef2a66f79b667df2e
- source: sgl-project-sglang
  path: test/registered/unit/model_executor/test_weight_update_tensor_rank.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 31b96be5cb43f8292fc7d23b02b957219a59576964044e4ee6457f7c29e4bbfe
- source: sgl-project-sglang
  path: python/sglang/srt/managers/tokenizer_control_mixin.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 8a57a3710fac18cfdcc5b47249127ea43d44bf41d590e44ef8667ff59e3d7697
- source: sgl-project-sglang
  path: python/sglang/srt/managers/io_struct.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: a1fd901e2998b0789f7ec70b032e645cde80404ec3540374d16125d84582e682
- source: sgl-project-sglang
  path: python/sglang/srt/entrypoints/engine.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 059c29dabd318a2766024ae8cd62d82e4f4c95bd67ebd9aa346ee8ddd6ad5423
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

begin 还会调用 `restore_weights_before_loading` 撤销部分量化原地 packing，end 再按会话状态执行模型 post-load 和量化 postprocess；它们是实际状态转换，不是空的事务标记。后续某次 load 被拒绝，不代表 begin 没改过布局，也不能据此安全地继续生成或跳过收尾。

调用方还要保持 selector 一致：manager 仅检查会话存在，各次 update 用该请求的 selector，end 才用 begin 保存的 selector；未逐次校验二者相等。当前 Python Engine 的 begin 暴露 selector，而 tensor/distributed update 封装默认请求 all，不会自动继承 begin 的 target/draft 选择。tokenizer 的锁按各次控制调用取得，并非覆盖整个 begin→end 窗口的持续隔离；tensor/distributed/IPC 控制入口还要求服务内部 DP size 为 1。多个独立 rollout 副本仍由训练消费者协调，不能由一次 RPC 推出全部副本同步或整个窗口已排空。

主干固定版本已经包含 [PR #43758](https://github.com/sgl-project/sglang/pull/43758)：`flush_cache_after_weight_update`在请求仍运行/排队时返回 `success=False`，服务不再因 assert 退出。**权重可能已经写入，weight version 也可能已经记录，失败响应不会把新参数回滚。** 应排空或按支持方式 retract 后显式 flush，再检查全部副本；不能将请求超时/400视为“完全没有修改”而盲目重试。

[PR #42561](https://github.com/sgl-project/sglang/pull/42561)截至2026-10-20仍open，提议逐runner记录已加载角色，处理 target 成功、draft 失败后的重复post-load/旧KV问题。本页固定main没有据此宣称已修复。使用draft时检查每个runner真实结果和缓存；失败后拒收该不一致轮次的样本，保留可恢复版本。

## 在线更新的门禁与派生权重

runner 的 `WeightUpdater` 在 disk、tensor、distributed load 和 checkpoint-engine IPC 加载入口检查派生权重缓存：补偿 mHC 的 TF32/BF16 splits、HPC-Ops bf16xfp32 GEMM 的缓存 splits，以及模型模块声明的 `_derived_weight_cache_error` 均可能拒绝更新。原因是原地写参数不能刷新这些派生值，captured graph 还可能保留旧引用；flush KV 不能修复这种不一致。门禁条件应在启动时确定并在各 rank 一致，不能让部分 rank 继续 collective、部分 rank提前退出。

这项门禁位于具体 load 入口，不能扩大为“拒绝前没有任何副作用”：distributed manager 先接收权重再逐 runner 加载，tensor manager 先反序列化，而 begin 可能已经还原 packing。独立的 `weight_cache_mode != off` 门禁还禁止原地更新共享 daemon 的权重；disk/distributed/IPC 会检查该模式，tensor 路径也检查。共享权重模式与普通一次性 IPC payload 的 ownership 不同，详见 [共享权重与 sleep](memory-and-scheduling.md#共享权重与sleep的边界)。

普通 tensor payload 按部署 TP rank 取对应的 `LocalSerializedTensor` 条目，不能用 draft 内部缩小后的 attention-TP rank 索引。`direct` 路线按模型现有参数名调用默认 loader，非标量要求 shape 一致；它不自动完成训练端到推理端的合并 QKV、专家分片或量化转换。对应 rank 单测只断言该索引选择，不证明任意模型布局和 dtype 数值等价。

## 磁盘重载、IPC 收尾与导出失败

disk 更新当前只接受 `DefaultModelLoader` 及其子类，冷启动支持的其他 loader 不能自动视为支持在线重载。代码先把 `model_config.model_path` 改为本次请求路径；加载异常后虽然日志写“Rolling back to original weights”，重试 iterator 仍从这个已改路径构造，未保存旧参数快照或旧路径。因此该日志不是恢复原 policy 的证明，重试自身也可能失败；以实际参数、配置和可信完整版本确认恢复。

checkpoint-engine IPC 使用独立 worker 封装；其量化/模型 post-hook 异常在该封装中仅记 warning，没有重新抛出。上层 RPC 因而可能返回成功而收尾未完成。验收同时检查 post-hook 日志、scale/派生状态和固定输入数值，不能以“IPC 已完成”替代模型可用。`WeightExporter` 另尊重模块的 `_weight_export_error`，可拒绝远端 seed、保存或取权重；接收 API 存在不保证该模型能作为导出端。

## Flat bucket：字节与生命周期

`FlattenedTensorBucket`先对每个tensor `flatten().view(torch.uint8)`，用`torch.cat`形成packed buffer。metadata包含name、原shape/dtype和start/end/numel；这里offset与numel来自uint8视图，表示**字节**。例如同一bucket中BF16与FP32不能按原元素数累计offset。

`reconstruct_tensors`按字节切片→view原dtype→reshape，得到的tensor可共享flat storage。减少逐tensor消息和额外接收copy的收益，依赖发送/接收协议一致且buffer在最后一次异步load前保持存活。若非连续tensor先flatten产生副本，也应算进峰值；bucket增大会增加host/device临时占用，不把“更大bucket”当无条件更快。

metadata验证应覆盖名字唯一性、shape/dtype、字节范围/对齐和完整顺序，真正加载还要核对合并QKV、专家布局、tied权重、量化scale及target/draft版本。不能用均匀BF16小模型证明混合dtype大MoE传权正确。

接收端新增 `FlattenedTensorBucket.empty(names,dtypes,shapes,device)`：按声明 dtype/shape 计算 byte ranges，一次分配 uint8 receive buffer，避免为构造 bucket 先建各参数空 tensor 再 cat/copy。入口用 strict zip 拒绝元数据长度不等，拒绝负维、未按 dtype itemsize 对齐的 offset 和零项 bucket；不会自动插 padding 修正不合法布局。它降低准备阶段副本，但仍需完整接收 buffer、load 完成和存储存活，不能把分配成功当作数据已接收或 session 已提交。

## Pause、旧 KV 和 policy 归属

`pause_generation(mode="in_place")`当前只停止继续调度，保留running batch/队列状态；它不是“服务全空闲”。retract路径与在途输出也需读所选版本。更新旧权重期间的KV一般必须失效，prefix hit只在相同语义和有效权重下成立；保留cache的专用方案必须有明确版本隔离，不能为吞吐把flush关闭。

一个可靠消费者记录：训练step/参数hash→begin/update/end各rank结果→cache处理→weight version→重新开放生成→样本携带policy version。样本与logprob可追到更新前或更新后某一确定版本，不能让同一次请求静默跨越语义边界。

## 验证、性能分解与回退

局部回归先按真实模型参数名/shape/dtype检查首次和第二次更新，再比较固定输入logits/logprob；覆盖tied权重、多TP rank、target/draft、更新期间排队、RPC失败和重复控制请求。`test_update_weights_from_distributed.py`是实际组/加载验证入口；不能把一次transport广播成功等同模型已使用新权重。

时间分别记录训练export/gather、pack、发送、接收、load/post-load、barrier、cache flush与恢复首请求。端到端吞吐还纳入等待所有rollout副本的尾延迟；临时full tensor和packed buffer分开计峰值。优化传输时先守住当前policy/logprob边界，再减少消息或副本。

恢复来源优先完整可信checkpoint或可重传固定weight version；若实际加载状态未知，先停止生成并检查/重建对应rollout副本，不能随意切回旧KV。训练端恢复由消费者的既有owner统一执行，SGLang更新RPC不负责整个训练checkpoint。

## 固定证据与验证范围

- [docs/docs/advanced_features/sglang_for_rl.mdx](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/docs/docs/advanced_features/sglang_for_rl.mdx)
- [python/sglang/srt/managers/scheduler_components/weight_updater.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/managers/scheduler_components/weight_updater.py)
- [python/sglang/srt/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/managers/scheduler.py)
- [python/sglang/srt/managers/tokenizer_manager.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/managers/tokenizer_manager.py)
- [python/sglang/srt/weight_sync/tensor_bucket.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/weight_sync/tensor_bucket.py)
- [test/registered/rl/test_update_weights_from_distributed.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/test/registered/rl/test_update_weights_from_distributed.py)

- [python/sglang/srt/model_executor/model_runner_components/weight_updater.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/model_executor/model_runner_components/weight_updater.py)
- [python/sglang/srt/model_executor/model_runner_components/weight_exporter.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/model_executor/model_runner_components/weight_exporter.py)
- [python/sglang/srt/model_loader/loader.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/model_loader/loader.py)
- [python/sglang/srt/model_loader/weight_utils.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/model_loader/weight_utils.py)
- [python/sglang/srt/checkpoint_engine/checkpoint_engine_worker.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/checkpoint_engine/checkpoint_engine_worker.py)
- [test/registered/unit/model_executor/test_derived_weight_cache.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/test/registered/unit/model_executor/test_derived_weight_cache.py)
- [test/registered/unit/model_executor/test_weight_update_tensor_rank.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/test/registered/unit/model_executor/test_weight_update_tensor_rank.py)

- [python/sglang/srt/managers/tokenizer_control_mixin.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/managers/tokenizer_control_mixin.py)
- [python/sglang/srt/managers/io_struct.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/managers/io_struct.py)
- [python/sglang/srt/entrypoints/engine.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/entrypoints/engine.py)

本页在 2026-10-20 阅读上述固定源码和教程；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。
