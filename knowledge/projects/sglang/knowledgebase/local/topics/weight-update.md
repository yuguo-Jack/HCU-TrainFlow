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
reviewed_on: '2026-10-12'
coverage: reviewed implementation chains and official guides; not all models, backends
  or HCU runtime qualification
sources:
- source: sgl-project-sglang
  path: docs/docs/advanced_features/sglang_for_rl.mdx
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 751d2c54c7cc87780a7e9005a76930f73a562c6cf4d9db1574bef4eafaeecd76
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler_components/weight_updater.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 7e2f08d8c1ca67965261208f51bab17d0ab0bfd5b87a009d9dbd97fc381542e4
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 8ebda29ff526cf61826ff8b2a6c907ad4d9cce3d580401a300b00308bbeedc67
- source: sgl-project-sglang
  path: python/sglang/srt/managers/tokenizer_manager.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 3ff205aa036a3355ce93c420346dd00ef0bf4ba3013769cd8bcfa4f5ba59753f
- source: sgl-project-sglang
  path: python/sglang/srt/weight_sync/tensor_bucket.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: fc50064ea51c338262394ff0b7a849100e7c46761099e27a4478e9db0ea08cc2
- source: sgl-project-sglang
  path: test/registered/rl/test_update_weights_from_distributed.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 0c06da440fd0de2b7250cd17ff6f47506eb22e4341d651fb8d49fdd9d1a2643e
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

主干固定版本已经包含 [PR #43758](https://github.com/sgl-project/sglang/pull/43758)：`flush_cache_after_weight_update`在请求仍运行/排队时返回 `success=False`，服务不再因 assert 退出。**权重可能已经写入，weight version 也可能已经记录，失败响应不会把新参数回滚。** 应排空或按支持方式 retract 后显式 flush，再检查全部副本；不能将请求超时/400视为“完全没有修改”而盲目重试。

[PR #42561](https://github.com/sgl-project/sglang/pull/42561)截至2026-10-12仍open，提议逐runner记录已加载角色，处理 target 成功、draft 失败后的重复post-load/旧KV问题。本页固定main没有据此宣称已修复。使用draft时检查每个runner真实结果和缓存；失败后拒收该不一致轮次的样本，保留可恢复版本。

## Flat bucket：字节与生命周期

`FlattenedTensorBucket`先对每个tensor `flatten().view(torch.uint8)`，用`torch.cat`形成packed buffer。metadata包含name、原shape/dtype和start/end/numel；这里offset与numel来自uint8视图，表示**字节**。例如同一bucket中BF16与FP32不能按原元素数累计offset。

`reconstruct_tensors`按字节切片→view原dtype→reshape，得到的tensor可共享flat storage。减少逐tensor消息和额外接收copy的收益，依赖发送/接收协议一致且buffer在最后一次异步load前保持存活。若非连续tensor先flatten产生副本，也应算进峰值；bucket增大会增加host/device临时占用，不把“更大bucket”当无条件更快。

metadata验证覆盖名字唯一性、shape/dtype、字节范围/对齐和完整顺序，真正加载还要核对合并QKV、专家布局、tied权重、量化scale及target/draft版本。不能用均匀BF16小模型证明混合dtype大MoE传权正确。

## Pause、旧 KV 和 policy 归属

`pause_generation(mode="in_place")`当前只停止继续调度，保留running batch/队列状态；它不是“服务全空闲”。retract路径与在途输出也需读所选版本。更新旧权重期间的KV一般必须失效，prefix hit只在相同语义和有效权重下成立；保留cache的专用方案必须有明确版本隔离，不能为吞吐把flush关闭。

一个可靠消费者记录：训练step/参数hash→begin/update/end各rank结果→cache处理→weight version→重新开放生成→样本携带policy version。样本与logprob可追到更新前或更新后某一确定版本，不能让同一次请求静默跨越语义边界。

## 验证、性能分解与回退

局部回归先按真实模型参数名/shape/dtype检查首次和第二次更新，再比较固定输入logits/logprob；覆盖tied权重、多TP rank、target/draft、更新期间排队、RPC失败和重复控制请求。`test_update_weights_from_distributed.py`是实际组/加载验证入口；不能把一次transport广播成功等同模型已使用新权重。

时间分别记录训练export/gather、pack、发送、接收、load/post-load、barrier、cache flush与恢复首请求。端到端吞吐还纳入等待所有rollout副本的尾延迟；临时full tensor和packed buffer分开计峰值。优化传输时先守住当前policy/logprob边界，再减少消息或副本。

恢复来源优先完整可信checkpoint或可重传固定weight version；若实际加载状态未知，先停止生成并检查/重建对应rollout副本，不能随意切回旧KV。训练端恢复由消费者的既有owner统一执行，SGLang更新RPC不负责整个训练checkpoint。

## 固定证据与验证范围

- [docs/docs/advanced_features/sglang_for_rl.mdx](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/docs/docs/advanced_features/sglang_for_rl.mdx)
- [python/sglang/srt/managers/scheduler_components/weight_updater.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/sglang/srt/managers/scheduler_components/weight_updater.py)
- [python/sglang/srt/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/sglang/srt/managers/scheduler.py)
- [python/sglang/srt/managers/tokenizer_manager.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/sglang/srt/managers/tokenizer_manager.py)
- [python/sglang/srt/weight_sync/tensor_bucket.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/sglang/srt/weight_sync/tensor_bucket.py)
- [test/registered/rl/test_update_weights_from_distributed.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/test/registered/rl/test_update_weights_from_distributed.py)

本页在 2026-10-12 阅读上述固定源码和教程；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。
