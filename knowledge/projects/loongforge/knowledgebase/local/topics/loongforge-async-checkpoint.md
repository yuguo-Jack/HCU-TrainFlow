---
id: ecosystem/topics/loongforge-async-checkpoint
title: LoongForge Torch-native：异步保存完成投票与 DCP 恢复
engine: loongforge
kind: authored
stages:
- fault-tolerance
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-11-04'
coverage: frozen source delta and consumer review; unchanged files rechecked; no HCU runtime validation
sources:
- source: baidu-baige-loongforge
  path: loongforge/embodied/distributed/checkpoint.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: 8db853529938efa9b91cdc34cb677d89fa940c6d131384b7c7869b21ddc9ab26
- source: baidu-baige-loongforge
  path: loongforge/embodied/train/trainers/base_trainer.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: 55a0d1541023f1e11d19a45c54b300503b2c2856d0d00f690edc1b6333e48899
- source: baidu-baige-loongforge
  path: tests/embodied/unit/test_async_checkpoint_finalize.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: d63a03a60df4ad26c83023409869a7c9e8f8eed47df9cadb30a8bb2b2965c5ce
- source: baidu-baige-loongforge
  path: loongforge/embodied/README.md
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: 62f972c7f4fc6d641ef01335338493de8c57ec36800b42dfd60d6c4302f17639
- source: baidu-baige-loongforge
  path: loongforge/embodied/distributed/context.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: bf5eab8380de75047e01a03bc0732a8e115abe862d5e4fcdf515881b3243d83b
- source: baidu-baige-loongforge
  path: loongforge/embodied/train/utils/logging.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: dd5c527f623d33ce2bf5fdb94310f8e7b28aee6fee4d34afffd346ce4650ca39
- source: baidu-baige-loongforge
  path: loongforge/embodied/train/trainers/supervised/finetune_trainer.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: eceba08f41ed1cc66a13844d2702a018d72a1e266bce18b391a9382e55225592
- source: baidu-baige-loongforge
  path: loongforge/embodied/train/trainers/custom/tensor_wise_trainer.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: 40a150edbb02064bc08697ae048dd82d401d536440d7632998a42aadb7e705bf
- source: baidu-baige-loongforge
  path: loongforge/embodied/optimizer/tensor_wise_optimizer/tensor_wise_optimizer.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: 2b9ff23e99cd892377b60a30e739b6d863e8e0d8ea2b7c8f10531401bbba3cdf
- source: baidu-baige-loongforge
  path: tests/embodied/unit/test_tensor_wise_optimizer.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: 8fba57ed452b8c0b88472ec1a0faee388fbeabfc7a7c8a6aa678a4d3d4a76a0b
retrieved_on: '2026-11-04'
---

# LoongForge Torch-native：异步保存完成投票与 DCP 恢复

## 问题：文件写完仍被当作不可恢复

Embodied Torch栈用`resume_meta.json`标记可恢复checkpoint。若只在下一次save或exit才finalize async save，即使数据已经持久写完，故障发生在两次save之间时仍会丢掉这份完成的checkpoint。另一个问题是DCP对共享参数alias的FQN映射，DDP wrapper下恢复可能报告成批missing/unexpected。

## 源码与 PR 的修复链

[#261](../../upstream/prs/baidu-baige--LoongForge/PR-261.md)的当前实现由BaseTrainer每optimizer step调用`maybe_finalize_pending_save`。无pending直接返回；有pending时**所有rank**对完成状态`all_reduce(MIN)`，只有共同完成才进入`flush_pending_save`。rank-local `Future.done()`不能决定只有部分rank进入后者，否则内部collective会死锁。

`_async_save_completion`识别`AsyncSaveResponse.upload_completion`，等待持久写入的completion而非只等staging。`flush_pending_save`在`future.result()`成功后由主rank写marker，失败则共同处理并保留原错误；不能先写marker再在后台补数据。DCP resume将权重加载到unwrapped module，避免同一参数多属性alias在DDP FQN还原时丢键。

完成投票只检查 Future 已结束，不等于它没有异常；flush 再取结果并做全 rank 成功投票。rank0 的 marker 写入与其他 rank 的成功确认不是一个原子事务，失败集合会清理相应未完成目录。因此保留实际 Future/投票/marker 次序和失败日志，不能把单个 done、marker 或退出码作为跨 rank 持久化成功证明。2026-11-04 的父仓 `042a68102395b9f4024d1a61084592c4c618371a` 已改变 checkpoint 与 BaseTrainer；原完成投票单测字节未变，仅能保留其原覆盖，不能视为新增分支已回归。

## 运行契约与开销

只有实际使用async DCP等相关路径才有该机制，不等同Megatron schedule或所有格式的行为。pending时每step增加一次小完成投票；这换取更早确认已完成checkpoint，不改save interval或承诺GPU零开销。最终可恢复身份包括模型、optimizer、scheduler、RNG及stateful data sampler，marker存在不证明这些内容与当前模型兼容。

## 验证和已知边界

单测覆盖无pending、完成后commit、幂等、慢写、失败清理及等待upload；真实集群还需要kill在“数据完成/下一次save前”的窗口，证明这份checkpoint确实可resume。恢复检查参数alias、step与数据进度，watch旧rank/残留写进程。

历史 PR 描述曾留下 async-save 与 detail-log 的 Gloo abort；当前 `DistributedContext.init/destroy` 已单独创建/销毁 Gloo stage_timing_group，BaseTrainer 将它传给 `StageTimers.get_max_time_string` 的 CPU all_gather；分布式日志缺该组会明确报错。这条源码修改意在把 timing collective 与 DCP 异步 Gloo 顺序隔开，历史缺口不能直接当作当前状态；但未运行真实并发写盘/日志回归，不能宣称 Gloo 问题已在所有组合消除。临时 workaround 仅属于对应版本/实验。测试和 A800 实测是上游证据，本轮没有 HCU 运行或推广同等性能。

## 回退、诊断和更新

异常先查pending所有rank一致性、Future异常、storage持久化与marker次序；不要反复启动新的writer覆盖旧输出。可退到可信同步保存，代价是save暴露时间；保持上次可恢复checkpoint。更新DCP/PyTorch、wrapper/FQN或BaseTrainer循环同时复核本页与[总览](../overview/engineering-guide.md)，容错系统继续是唯一重启owner。

当前新增两类状态契约。`build_alias_map` 按模块对象与 tensor 对象身份生成 canonical key，`canonical_state_dict` 在保存时省略 alias、加载时补回，并移除临时 hooks；不会因两个不同 view 共享 storage 就合并。该机制覆盖模块别名中的非 tensor `_extra_state`，原 unwrapped strict load 仍保留，不能通过丢弃 TE 状态迁移 FP8。

ZeRO rank-local 状态现在先 `_cpu_snapshot`，再后台 `torch.save`；`_merge_futures` 等 DCP upload 与 ZeRO writer 全部结束后传播首个失败/取消，完成 marker 不能只看 DCP 一端。DCP staging 同步失败时按 `LOONGFORGE_ZERO_SAVE_DRAIN_TIMEOUT`（缺省 600 秒）有界等待 writer，超时不保证后台写线程已停止。文件 API/Future 完成也不构成已验证的掉电持久性或共享存储故障原子性。`FinetuneTrainer._save_checkpoint` 已传入 `data_cfg`，且需要 save_processor_config 开关命中才写 processor_config；自定义 trainer 仍逐项核对。

固定版本还存在一个静态可见的不对称：`_save_zero_optimizer_state` 将 `child.optim` 交给 `_local_optimizer_state_dict`，而 `_load_zero_optimizer_state` 通过 `_rank_local_optimizer` 将 tensor_wise 外层交给恢复 hook。`TensorWiseOptimizer.local_checkpoint_state_dict` 才包含 backend、manifest、FP32 master、param_sync_residuals 与内部状态；普通 inner state 不满足 `load_local_checkpoint_state_dict` 首先要求的 backend 身份。这不是没有 `.optim` 属性，而是保存端绕过外层完整状态 hook。`TensorWiseTrainer` 已拒绝 LoRA/非 DCP 的训练状态保存，但这一格式门禁不解决上述 payload 差异。上游存在 `test_checkpoint_round_trip_is_bitwise` 等测试，本轮未执行，不能按测试名宣称此固定版本完整恢复。采用前必须在实际配套确认修复与 save→load 的 master/下一步更新等价性；暂保留已验证训练栈/optimizer 的可信 checkpoint。

## 固定证据与复核范围

- [loongforge/embodied/distributed/checkpoint.py](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/loongforge/embodied/distributed/checkpoint.py)
- [loongforge/embodied/train/trainers/base_trainer.py](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/loongforge/embodied/train/trainers/base_trainer.py)
- [tests/embodied/unit/test_async_checkpoint_finalize.py](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/tests/embodied/unit/test_async_checkpoint_finalize.py)
- [loongforge/embodied/README.md](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/loongforge/embodied/README.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
