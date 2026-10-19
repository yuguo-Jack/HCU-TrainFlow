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
reviewed_on: '2026-10-20'
coverage: selected source, official documentation and related PR reading; no HCU runtime validation
sources:
- source: nvidia-megatron-energon
  path: src/megatron/energon/loader.py
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: 00f4780c39c023c999acead866c3056128d4ff4b8c9678ead1ccb8f5d498d1f0
- source: nvidia-megatron-energon
  path: src/megatron/energon/savable_loader.py
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: 8c1a5e58984cd33e41ec17fdc6a55ef1efd9b3a02e6d7606cfbef9da89f6865a
- source: nvidia-megatron-energon
  path: src/megatron/energon/worker.py
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: d6bdaca8035e80518a70ce0283f123604749c4a8ab3f368d736df5cfc3e73c30
- source: nvidia-megatron-energon
  path: docs/source/basic/save_restore.md
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: b6db5d6072470133817e393d13330d758159c872cc6fcd22299104d8bdf87c61
- source: nvidia-megatron-energon
  path: docs/source/advanced/repro_scaling.md
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: 4cccff0a2238bcdc2d6eabd253855cb3b6eeb16fa77b9bde80a6720a9535b46b
- source: nvidia-megatron-energon
  path: docs/source/advanced/parallelism.md
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: 427aa86fba6a0bac1a9460255e46a93d7d67ec502a852d26105eccd313484f4e
- source: nvidia-megatron-energon
  path: tests/test_dataset.py
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: 83b947681603f6825a2349c7881e735409b53a6ca0152851a9ee6254eff0fb2b
- source: nvidia-megatron-energon
  path: src/megatron/energon/flavors/common/dataset_sampler.py
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: 35d1b00fa7dec5914d928fa558cf07ee4cb5b29005c3f2aac653ba9c0c513d78
- source: nvidia-megatron-energon
  path: src/megatron/energon/flavors/common/manifest/sharder.py
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: a88e23aabbc593dac1bee74ddd2ca9999cf03a7ee5981eb09b313a3b9016ebb0
- source: nvidia-megatron-energon
  path: src/megatron/energon/rng.py
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: bfa73c2a2e38947a659dac65b2d29ade26523fcc06390f0acaaf7c428149abb0
- source: nvidia-megatron-energon
  path: docs/source/internals/compatibility.md
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: 024c424612f9aa007417bd247881f1b837b47cb60295215d9216c49b77196c93
---

# Energon：数据空泡、Snapshot 恢复、Worker 与资源生命周期

## 1. 输入空泡与并发成本

CPU decode/encode、共享存储、worker队列/prefetch或H2D可能使GPU等待。先对齐batch-ready与step关键路径，查worker栈、CPU/IO、queue、hostRSS/FD和pinned memory；用相同shape mock作为隔离对照，不能替代真实数据验收。更多workers/prefetch既能隐藏延迟，也可能压垮主存/存储和CPU，并非单调加速。

当前loader默认prefetch factor等设置与checkpoint_interval_sec、min_samples、n_checkpoints分别影响pipeline和恢复成本。内部定期worker snapshot不是训练模型持久checkpoint；频度越密通常降低重放距离，却增加状态/内存/处理，按真实encoder代价选择。

## 2. Snapshot+消费offset的恢复模型

workers会预取未来样本，训练真正消费位置落后于worker当前状态。SavableLoader保留周期完整状态和消费计数/restore keys，save时绑定最近snapshot与offset；restore先恢复worker/RNG/wrapper，再重放到实际位置。仅globalstep或把prefetch最新状态当已消费进度可能造成样本遗漏。

`save_state_rank/restore_state_rank`用于各数据rank独立state；global接口gather/scatter时所有group ranks必须参与，只有目标rank写盘，不得只在writer调用collective。旧save_state/restore_state接口已弃用，按当前signature而非旧教程例子处理。

## 2a. 大数据集索引常量内存与版本边界

本轮 `DatasetSampler._pending_slices` 不再分配/保存全量随机待处理列表：无 shuffle 返回 `range(num_slices)`；有限 epoch shuffle 以 `FeistelPermutation(num_slices × shuffle_over_epochs, seed)` 按位置取索引，再对 num_slices 取模；replacement 模式继续用 worker RNG 逐个抽取。Feistel 在下一幂次二进制域做默认八轮置换，对域外结果 cycle walking，形成目标范围内的双射。它降低随 slice 数增长的索引内存，但每次查找有整数运算/cycle walking 的 CPU 成本，不代表所有加载场景都更快。

`Sharder` 对 `max_samples_per_sequence==1` 直接创建每 worker 的 range offsets，`_clean_offsets` 保留 range，sampler 配置也用 start/stop/step 表达，避免为每个 sample 展开 Python offsets 列表。此特化不代表所有 sequence cap、packing buffer 或 reader 缓存都变为常量内存。

保存字段现在包含 `_pending_slices_seed`、`_pending_slices_offset`、active slices 和 worker RNG，而旧版保存 pending index 列表。随机顺序算法与状态布局都已变化：固定 seed、样本集合相同或 Python API 别名可用，均不能证明跨版本精确续训。升级前保留原 loader/dataset 版本和可信 checkpoint；若要迁移旧状态，必须另有明确迁移实现与旧状态输入测试，不默认从头读取冒充 resume。

上游 `test_max_samples_per_sequence_one_uses_compact_indexes` 检查 range offsets、单 epoch 全覆盖、下一 epoch 顺序变化，以及保存十个 batch 后恢复的剩余序列与下一 epoch 相同。这是同版本、特定配置的恢复依据，不是全 worker/DP/旧 checkpoint 的兼容认证。比较 host RSS、state bytes、batch-ready 与重放成本时固定样本顺序版本，避免把数据流变化当成模型性能提升。

## 3. 并行域与缩扩约束

WorkerConfig的rank/world/group按数据DP，而非完整TP×PP×DPworld。model-parallel peers可以同DP身份独立读同数据或由消费者广播；所有实际持有iterator的rank须restore，不能把“只写一个副本”误解为“只恢复一个rank”。

Energon独立reproducible scaling要求相同major、global batch、seed offset，GBS可被MB×数据world×workers整除，且数据world×workers乘积保持相同。并非任意扩卡都自动保持数据顺序。Bridge当前按DP文件恢复仍要求同DPsize，详见[Bridge恢复专题](../../../../bridge/knowledgebase/local/topics/bridge-checkpoint-recovery.md)；独立库算法支持不代替消费者state迁移实现。

## 4. Close、watchdog与失败边界

当前Basic/Savable loader提供close/context manager，统一关闭iterator/workers/dataset，并保留析构清理。`tests/test_dataset.py::test_loader_close`当前覆盖 WebDataset、JSONL 及不同 workers 的重复 loader/GC/关闭和 FD 检查；旧 joined fixture 已随实现移除，不能继续作为当前覆盖。测试属于生命周期证据，本轮没有执行，不推定所有平台文件/进程资源均释放。

[#301](../../upstream/prs/NVIDIA--Megatron-Energon/PR-301.md)记录dataset永久失效/读者重开和状态调用的问题，应对照最终源码，不把提议的每项guard写成已存在；[#302](../../upstream/prs/NVIDIA--Megatron-Energon/PR-302.md)截至2026-10-20已关闭且未合并，不再作为待合并能力。当前关闭后的loader能否再迭代/save，应按接口与实际测试验证，不能默认安全复用同一loader对象。

watchdog默认超时诊断/是否fail由策略决定，不负责节点隔离或重新拉起；恢复仍由训练/站点唯一owner接管。记录原数据身份和最后共同step，区分网络storage阻塞、损坏sample、CPU线程死锁、队列耗尽和worker退出。

## 5. 验证、回退与维护

正常/中断恢复比较未来样本序列、batchtensor、RNG、有效token与阶段loss；再测恢复重放时间、长时内存/FD、提前break与异常退出。数据改变、augmentation非确定或state缺失保留缺口，不能静默从头读称resume正常。

回退可信数据配方、较少workers/prefetch或严格错误策略，代价和输入瓶颈说明清楚；保留训练state对应数据版本。更新loader/reader/wrapper、storageclient、workergroup和Bridge保存逻辑时同步[总览](../overview/energon.md)与[packing专题](energon-encoding-packing.md)。

## 固定证据与复核范围

- [src/megatron/energon/loader.py](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/src/megatron/energon/loader.py)
- [src/megatron/energon/savable_loader.py](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/src/megatron/energon/savable_loader.py)
- [src/megatron/energon/worker.py](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/src/megatron/energon/worker.py)
- [docs/source/basic/save_restore.md](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/docs/source/basic/save_restore.md)
- [docs/source/advanced/repro_scaling.md](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/docs/source/advanced/repro_scaling.md)
- [docs/source/advanced/parallelism.md](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/docs/source/advanced/parallelism.md)
- [tests/test_dataset.py](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/tests/test_dataset.py)

- [src/megatron/energon/flavors/common/dataset_sampler.py](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/src/megatron/energon/flavors/common/dataset_sampler.py)
- [src/megatron/energon/flavors/common/manifest/sharder.py](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/src/megatron/energon/flavors/common/manifest/sharder.py)
- [src/megatron/energon/rng.py](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/src/megatron/energon/rng.py)
- [docs/source/internals/compatibility.md](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/docs/source/internals/compatibility.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
