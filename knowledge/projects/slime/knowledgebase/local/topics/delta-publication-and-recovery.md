---
id: engines/slime/topics/delta-publication-and-recovery
title: Slime：disk delta 全量基线、版本发布与联合恢复
engine: slime
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-20'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime execution
sources:
- source: thudm-slime
  path: train.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 9ab1d9a987182dc5ae57d19ca82a3807fd18adee8cecf0afe118cadbd8939939
- source: thudm-slime
  path: slime/data/checkpoint.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 98e0b5724e59ee2e6f9df3459f4d598cc987a2e060f2de372abe15d92166adb7
- source: thudm-slime
  path: slime/backends/megatron_utils/checkpoint.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 2307489cbd9916ddbf6ab9f93f508cf3796d2dc3d9a986f9e58426d9fbeb830b
- source: thudm-slime
  path: slime/backends/megatron_utils/update_weight/update_weight_from_disk_delta.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: ac78a67f02d146331f377c9246b60109d039101b99b5d4058ad6932981411293
- source: thudm-slime
  path: slime/backends/sglang_utils/sglang_engine.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 9ccc2851e1ea0b37981154f2d9250226f8267d7bfa96262989930a1904c27eeb
- source: thudm-slime
  path: docs/en/advanced/delta-weight-sync.md
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 2c0f424890480c6d8465e3f0455542c2adc8495de0d7bad311149b0b342c9966
- source: thudm-slime
  path: docs/en/advanced/fault-tolerance.md
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 1f120c4b4cd11d830dff3b0d4e50d676a293821a00f0370868a5cdedbc2e72ae
- source: thudm-slime
  path: tests/test_disk_delta_recovery.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 0d0753a32ba90f91dc51871f7c62ca474f99ad1a13385dcf94ac8f0e4c56c125
- source: thudm-slime
  path: tests/test_disk_delta_checkpoint_index.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 19e276c354338dea683ceed6854c247fe2eca34c56e28c51d74f029ef951fe28
- source: thudm-slime
  path: tests/test_training_recovery.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 84797613939502cca123d0903761f8e3ae19f350ae1aaf5f18bddaaeefc8c7b9
- source: thudm-slime
  path: tests/test_straw_checkpoint_rewind.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 4aed63ada40d8ec972e2fc963e0b8b503061a006498c7f7c8df93d6f0bc54d63
---

# Slime：disk delta 全量基线、版本发布与联合恢复

## 版本边界先确认

本页是官方main的固定实现；HCU旧维护线可能第一轮仅capturebaseline，因此先核对真实`UpdateWeightFromDiskDelta.update_weights`。**当前main第一次、trainer恢复或engine拓扑改变时都发布当前训练权重的全量HFcheckpoint，并从这些精确tensor建立CPU snapshot**，不拿原始HFcheckpoint的旧weights当当前baseline。

配置见[delta教程](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/delta-weight-sync.md)：`--update-weight-mode delta --update-weight-transport disk`，sharedversion目录与hostlocalcheckpoint分别设置。这是一条磁盘传输协议，不是普通tensorcollective，也不是optimizercheckpoint。目录必须为专用任务产物，不能指向原始模型材料。

## 完整发布与增量链

[`update_weight_from_disk_delta.py`](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/backends/megatron_utils/update_weight/update_weight_from_disk_delta.py)维护`_needs_full_sync`和每tensorbyte snapshot。初始化/fullseed先扫描所有已有`weight_v*`目录，选高于**所有已尝试版本**的新版本，防止丢失回复后误认旧localcheckpoint已是新恢复状态；保留旧版本目录。

full发布遍历非expert/expertHFtensor，写safetensorsshards、精确bytesnapshot、assets并finalizeindex。后续将new与old的bytes差分，用xor/overwrite编码、zstd压缩，只写变更tensor，并记新完整tensorchecksum。

- xor更小，但必须在正确base上恰好应用一次，重复应用会还原。
- overwrite记录绝对修改byte，在正确协议条件下更适合重复应用；仍需要base/version/checksum判断。
- index包含target/baseversion、encoding/compression/checksum，分片编号和weightmap由Gloo协调而非依赖另一host立刻看到文件。
- `_atomic_write`发布单文件；单shard出现不等于所有文件、index和consumer都完成，也不代表GPUweights已经更新。

## host pull、GPU reload和失败

发送端post-writehook完成共享文件可见性，再barrier；rank0等待各engine`pull_weights(target)`。官方教程规定接收端逐host应用、校验后才成功，具体实现来自匹配的SGLangpatch，升级时需同时读consumer。

随后按flush策略pausegeneration（abort或in_place），必要时flushcache，从hostlocalcheckpoint调用普通`update_weights_from_disk`，再continuegeneration；最后训练rankbarrier。这解释“hostcheckpoint到位”和“GPU可生成新版本”的两个不同完成边界。

`_needs_full_sync`仅在reload成功后清零，新seed失败重试会重新选更高版本；稳态增量中snapshot可能已推进后再遭reload失败，仍不能推断所有host会自动回滚。失败后保留各hostbase/target/checksum与已发布index，按支持的重建fullbaseline恢复一致性，而非仅递增driver版本。

## 收益与资源成本

增量可减少wirebytes，却增加HFgather、CPUbytesnapshot、diff/compression、hostIO及校验。记录`perf/update_weights_density`、wirebytes、CPU/RAM、D2H、发布/pull/reload时间与完整RLstep。高变化密度或低带宽CPU可能让fullsync更合适，不能从delta文件小推导端到端更快。

## durable checkpoint 和恢复接管

[`slime/data/checkpoint.py`](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/slime/data/checkpoint.py)先等待必要model/critic保存、rollout/data状态，再写jointcommit，最后通知`checkpoint_committed`允许recovery释放旧数据。它校验完整commit，不由modeltracker猜完成。`training_completed`只释放运行队列capacity，不推进durable边界。

[容错文档](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/fault-tolerance.md)当前保留named detachedServingCluster，Ray不丢时新attempt可复用；RolloutManager处理数据转换/分发，TrainingRecovery管理checkpoint后需重放的batch。straw或debugrolloutdump保留样本/rewardpostprocessing，以便训练回退后重放；普通model保存不包含所有在途生成。

恢复要保存model、scheduler、RNG及有状态optimizer；statelessAdam省moment有单独scheduler文件和精度边界，不承诺bitwise同样更新。TP/PP改变还可能重初始化RNG。recovery接入**不会自动重试训练job**，节点故障/集群抢占仍由调度器和既有容错规则处理。不能在重启前盲目`ray stop`/`pkill sglang`破坏可复用服务。

## 当前 in-place rewind 与 empty queue 的区别

`resolve_checkpoint` 现在保留请求的 `args.save`，以 `rollout/session.json`、generation 和 `rewind_pending` 记录恢复计划；不再为每次回退自动建立 branches 子目录。解析阶段只选择 model/source 边界，实际队列重置和清理应由持有原作业锁的 controller 执行，不能由另一个恢复 owner 预先删目录。选择显式 step 或旧 tracker 时保留该请求，不能用后面不完整的 save 进度代替。

`RestorePlan.mode` 当前是 new/resume/rewind/empty。有效 queue snapshot 对应 rewind；缺失/损坏 queue、dataset cursor 或 builder metadata 可在保留有效模型分量检查后告警降为 empty，而不是将所有恢复一律拒绝。此路径不能提供同一待训练样本集合或精确数据 cursor 的保证；必须保留 warning、所选模型 step、数据恢复种类和新的版本边界。模型分量自身缺失/变化仍不能当成合法 data fallback。

首次 checkpoint 前的中断可恢复原 WAL，要求初始模型/输入和共享 Straw pool 相符；已加载 checkpoint 后的恢复计数与 replay 边界以实际模型加载完成为准。保留 serving 时，SGLang adapter 按排序后的 group name 销毁旧训练通信组，防止不同 worker 以不同 set 迭代顺序销毁而互等；重复 detach 也保留最初 admission 暂停状态，不能把自身暂停误记成原状态。

固定 `test_straw_checkpoint_rewind.py` 是四 GPU 的训练/serving 集成脚本，检查同目录从 step1 重新训练 step2 前的 producer cursor、pending 样本和空 in-flight 状态；`test_training_recovery.py` 补充不可用初始 rollout 不再反复校验、模型加载后再推进边界。脚本与断言提供验证入口，本轮未执行 GPU/多机恢复，不能把它写成已完成的容错实测。

## 证据、验证和更新

[`test_disk_delta_recovery.py`](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_disk_delta_recovery.py)用真实文件/tensorcodec、mockcollective/RPC测试当前fullseed、已有失败目录、丢回复后重试和xor/overwrite；不是实际SGLang多机reload测试。index/训练recovery测试是相邻契约入口。

现场验证应覆盖首次/稳态、旧HF与新恢复weights、空delta、缺shard/checksum、部分host失败、admission暂停、jointcommit失败和Ray丢失。分别标记服务恢复、模型恢复和data重放结果。本页未运行设备故障注入。更新publisher、SGLangconsumer、sessionidentity、checkpointcommit或训练loop时同时复核[总览](../overview/engineering-guide.md)及对应案例。


## 本轮补充固定证据

- [tests/test_straw_checkpoint_rewind.py](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/tests/test_straw_checkpoint_rewind.py)
