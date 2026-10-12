---
id: official-megatron-wiki/topics/energon-recovery-throughput
title: Energon：数据空泡、Snapshot 恢复、Worker 与资源生命周期
engine: energon
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected source, official documentation and related PR reading; no HCU runtime
  validation
sources:
- source: nvidia-megatron-energon
  path: src/megatron/energon/loader.py
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 00f4780c39c023c999acead866c3056128d4ff4b8c9678ead1ccb8f5d498d1f0
- source: nvidia-megatron-energon
  path: src/megatron/energon/savable_loader.py
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 8c1a5e58984cd33e41ec17fdc6a55ef1efd9b3a02e6d7606cfbef9da89f6865a
- source: nvidia-megatron-energon
  path: src/megatron/energon/worker.py
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: d6bdaca8035e80518a70ce0283f123604749c4a8ab3f368d736df5cfc3e73c30
- source: nvidia-megatron-energon
  path: docs/source/basic/save_restore.md
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: b6db5d6072470133817e393d13330d758159c872cc6fcd22299104d8bdf87c61
- source: nvidia-megatron-energon
  path: docs/source/advanced/repro_scaling.md
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 4cccff0a2238bcdc2d6eabd253855cb3b6eeb16fa77b9bde80a6720a9535b46b
- source: nvidia-megatron-energon
  path: docs/source/advanced/parallelism.md
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 427aa86fba6a0bac1a9460255e46a93d7d67ec502a852d26105eccd313484f4e
- source: nvidia-megatron-energon
  path: tests/test_dataset.py
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 1ec677b1de77c839ba1e7f4fbecce7eb786f9d09e0d6d506da755260dcf45694
---

# Energon：数据空泡、Snapshot 恢复、Worker 与资源生命周期

## 1. 输入空泡与并发成本

CPU decode/encode、共享存储、worker队列/prefetch或H2D可能使GPU等待。先对齐batch-ready与step关键路径，查worker栈、CPU/IO、queue、hostRSS/FD和pinned memory；用相同shape mock作为隔离对照，不能替代真实数据验收。更多workers/prefetch既能隐藏延迟，也可能压垮主存/存储和CPU，并非单调加速。

当前loader默认prefetch factor等设置与checkpoint_interval_sec、min_samples、n_checkpoints分别影响pipeline和恢复成本。内部定期worker snapshot不是训练模型持久checkpoint；频度越密通常降低重放距离，却增加状态/内存/处理，按真实encoder代价选择。

## 2. Snapshot+消费offset的恢复模型

workers会预取未来样本，训练真正消费位置落后于worker当前状态。SavableLoader保留周期完整状态和消费计数/restore keys，save时绑定最近snapshot与offset；restore先恢复worker/RNG/wrapper，再重放到实际位置。仅globalstep或把prefetch最新状态当已消费进度可能造成样本遗漏。

`save_state_rank/restore_state_rank`用于各数据rank独立state；global接口gather/scatter时所有group ranks必须参与，只有目标rank写盘，不得只在writer调用collective。旧save_state/restore_state接口已弃用，按当前signature而非旧教程例子处理。

## 3. 并行域与缩扩约束

WorkerConfig的rank/world/group按数据DP，而非完整TP×PP×DPworld。model-parallel peers可以同DP身份独立读同数据或由消费者广播；所有实际持有iterator的rank须restore，不能把“只写一个副本”误解为“只恢复一个rank”。

Energon独立reproducible scaling要求相同major、global batch、seed offset，GBS可被MB×数据world×workers整除，且数据world×workers乘积保持相同。并非任意扩卡都自动保持数据顺序。Bridge当前按DP文件恢复仍要求同DPsize，详见[Bridge恢复专题](bridge-checkpoint-recovery.md)；独立库算法支持不代替消费者state迁移实现。

## 4. Close、watchdog与失败边界

当前Basic/Savable loader提供close/context manager，统一关闭iterator/workers/dataset，并保留析构清理。`tests/test_dataset.py::test_loader_close`覆盖WebDataset、JSONL、joined数据及不同workers的重复loader/GC/关闭和FD检查，属于生命周期证据；没有在本轮执行，不推定所有平台文件/进程资源均释放。

[#301](../../prs/NVIDIA--Megatron-Energon/PR-301.md)记录dataset永久失效/读者重开和状态调用的问题，应对照最终源码，不把提议的每项guard写成已存在；[#302](../../prs/NVIDIA--Megatron-Energon/PR-302.md)仍open，其iterator finalize变化另核对。当前关闭后的loader能否再迭代/save，应按接口与实际测试验证，不能默认安全复用同一loader对象。

watchdog默认超时诊断/是否fail由策略决定，不负责节点隔离或重新拉起；恢复仍由训练/站点唯一owner接管。记录原数据身份和最后共同step，区分网络storage阻塞、损坏sample、CPU线程死锁、队列耗尽和worker退出。

## 5. 验证、回退与维护

正常/中断恢复比较未来样本序列、batchtensor、RNG、有效token与阶段loss；再测恢复重放时间、长时内存/FD、提前break与异常退出。数据改变、augmentation非确定或state缺失保留缺口，不能静默从头读称resume正常。

回退可信数据配方、较少workers/prefetch或严格错误策略，代价和输入瓶颈说明清楚；保留训练state对应数据版本。更新loader/reader/wrapper、storageclient、workergroup和Bridge保存逻辑时同步[总览](../energon.md)与[packing专题](energon-encoding-packing.md)。

## 固定证据与复核范围

- [src/megatron/energon/loader.py](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/src/megatron/energon/loader.py)
- [src/megatron/energon/savable_loader.py](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/src/megatron/energon/savable_loader.py)
- [src/megatron/energon/worker.py](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/src/megatron/energon/worker.py)
- [docs/source/basic/save_restore.md](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/docs/source/basic/save_restore.md)
- [docs/source/advanced/repro_scaling.md](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/docs/source/advanced/repro_scaling.md)
- [docs/source/advanced/parallelism.md](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/docs/source/advanced/parallelism.md)
- [tests/test_dataset.py](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/tests/test_dataset.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
