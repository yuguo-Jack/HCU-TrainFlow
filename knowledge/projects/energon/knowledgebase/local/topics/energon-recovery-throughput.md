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
reviewed_on: '2026-11-18'
coverage: Selected fixed-source changes and affected consumers; no upstream/HCU runtime
  execution
sources:
- source: nvidia-megatron-energon
  path: src/megatron/energon/loader.py
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: 00f4780c39c023c999acead866c3056128d4ff4b8c9678ead1ccb8f5d498d1f0
- source: nvidia-megatron-energon
  path: src/megatron/energon/savable_loader.py
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: 8c1a5e58984cd33e41ec17fdc6a55ef1efd9b3a02e6d7606cfbef9da89f6865a
- source: nvidia-megatron-energon
  path: src/megatron/energon/worker.py
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: d6bdaca8035e80518a70ce0283f123604749c4a8ab3f368d736df5cfc3e73c30
- source: nvidia-megatron-energon
  path: docs/source/basic/save_restore.md
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: b6db5d6072470133817e393d13330d758159c872cc6fcd22299104d8bdf87c61
- source: nvidia-megatron-energon
  path: docs/source/advanced/repro_scaling.md
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: 4cccff0a2238bcdc2d6eabd253855cb3b6eeb16fa77b9bde80a6720a9535b46b
- source: nvidia-megatron-energon
  path: docs/source/advanced/parallelism.md
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: 427aa86fba6a0bac1a9460255e46a93d7d67ec502a852d26105eccd313484f4e
- source: nvidia-megatron-energon
  path: tests/test_dataset.py
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: 83b947681603f6825a2349c7881e735409b53a6ca0152851a9ee6254eff0fb2b
- source: nvidia-megatron-energon
  path: src/megatron/energon/flavors/common/dataset_sampler.py
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: 35d1b00fa7dec5914d928fa558cf07ee4cb5b29005c3f2aac653ba9c0c513d78
- source: nvidia-megatron-energon
  path: src/megatron/energon/flavors/common/manifest/sharder.py
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: a88e23aabbc593dac1bee74ddd2ca9999cf03a7ee5981eb09b313a3b9016ebb0
- source: nvidia-megatron-energon
  path: src/megatron/energon/rng.py
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: bfa73c2a2e38947a659dac65b2d29ade26523fcc06390f0acaaf7c428149abb0
- source: nvidia-megatron-energon
  path: docs/source/internals/compatibility.md
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: 03cbc7dadc02504d4e348aeaf87866153791870cd55b04a945f09dff47be50d7
- source: nvidia-megatron-energon
  path: src/megatron/energon/recipe/recipe.py
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: f5b43761fca94c1dd4d36e5bc655ecd5beb2974bc002d265f503ca6d3d3ba28c
- source: nvidia-megatron-energon
  path: src/megatron/energon/recipe/dataset_loader.py
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: e7a4dfafa532bc145253611966a23e3906a760a33140cab7f5eb4e5872d46afd
- source: nvidia-megatron-energon
  path: src/megatron/energon/flavors/common/filter_index.py
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: d2cc184330d0a53be41b1f8c753e2ca06a992a91ab11f7599571050ffbd33aca
- source: nvidia-megatron-energon
  path: tests/test_filter_index.py
  commit: e33bbe768a4f7a629377a365c8af9a7b98b1219e
  sha256: bfa633d01e0fdd6405f738bf1ccebf8d10138c1e229ff59767f28b7b6e25af4a
- source: nvidia-megatron-energon
  path: src/megatron/energon/flavors/common/dataset_sampler.py
  commit: 8ba04a3aa4200725a136258e00a6facf3bd15acd
  sha256: fe88bf4ed490ef249b253face9960ba55f597ddb604b77b07d56793bdfad7e3f
- source: nvidia-megatron-energon
  path: src/megatron/energon/flavors/common/filter_index.py
  commit: 8ba04a3aa4200725a136258e00a6facf3bd15acd
  sha256: 982449eded6142e111df7304da31918932f9e98988d77b56059c4387305b9fda
- source: nvidia-megatron-energon
  path: src/megatron/energon/rng.py
  commit: 8ba04a3aa4200725a136258e00a6facf3bd15acd
  sha256: 23f5973dc29c5faaa6eb2f996e3e934a29fb6f7ef864310f4fa352e76469391a
- source: nvidia-megatron-energon
  path: src/megatron/energon/task_encoder/base.py
  commit: 8ba04a3aa4200725a136258e00a6facf3bd15acd
  sha256: 53e8825432d392d36f5308d77dbbbbffb28a8a0ae96d018959e15fde5f641403
- source: nvidia-megatron-energon
  path: tests/test_dataset.py
  commit: 8ba04a3aa4200725a136258e00a6facf3bd15acd
  sha256: 4925982cdbc7511e73968600f453356317638e97033cc895a5e4a1b3f1c75f34
- source: nvidia-megatron-energon
  path: tests/test_filter_index.py
  commit: 8ba04a3aa4200725a136258e00a6facf3bd15acd
  sha256: 817a9f7bb7533d4792252b8843ae0b32a29cd50194d7ada8a0f0dcccce00a464
retrieved_on: '2026-11-18'
---

# Energon：数据空泡、Snapshot 恢复、Worker 与资源生命周期

## 1. 输入空泡与并发成本

CPU decode/encode、共享存储、worker队列/prefetch或H2D可能使GPU等待。先对齐batch-ready与step关键路径，查worker栈、CPU/IO、queue、hostRSS/FD和pinned memory；用相同shape mock作为隔离对照，不能替代真实数据验收。更多workers/prefetch既能隐藏延迟，也可能压垮主存/存储和CPU，并非单调加速。

当前loader默认prefetch factor等设置与checkpoint_interval_sec、min_samples、n_checkpoints分别影响pipeline和恢复成本。内部定期worker snapshot不是训练模型持久checkpoint；频度越密通常降低重放距离，却增加状态/内存/处理，按真实encoder代价选择。

## 2. Snapshot+消费offset的恢复模型

workers会预取未来样本，训练真正消费位置落后于worker当前状态。SavableLoader保留周期完整状态和消费计数/restore keys，save时绑定最近snapshot与offset；restore先恢复worker/RNG/wrapper，再重放到实际位置。仅globalstep或把prefetch最新状态当已消费进度可能造成样本遗漏。

`save_state_rank/restore_state_rank`用于各数据rank独立state；global接口gather/scatter时所有group ranks必须参与，只有目标rank写盘，不得只在writer调用collective。旧save_state/restore_state接口已弃用，按当前signature而非旧教程例子处理。

## 2a. 大数据集索引常量内存与版本边界

当前 `DatasetSampler._pending_slices` 已使用此前引入的常量内存实现，2026-11-04 该文件字节未变；2026-11-18 已增加下述顺序流路径；它不分配/保存全量随机待处理列表：无 shuffle 返回 `range(num_slices)`；有限 epoch shuffle 以 `FeistelPermutation(num_slices × shuffle_over_epochs, seed)` 按位置取索引，再对 num_slices 取模；replacement 模式继续用 worker RNG 逐个抽取。Feistel 在下一幂次二进制域做默认八轮置换，对域外结果 cycle walking，形成目标范围内的双射。它降低随 slice 数增长的索引内存，但每次查找有整数运算/cycle walking 的 CPU 成本，不代表所有加载场景都更快。

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

2026-11-04 检索固定 `e33bbe768a4f7a629377a365c8af9a7b98b1219e`：所引 loader / worker / sampler / sharder / RNG / 测试及恢复文档字节不变，保留 snapshot+消费 offset、Feistel 状态、DP×worker 缩扩与资源关闭限制。compatibility 文档新增 `test_filter_index.py` 作为格式/工厂变更验证入口；Recipe 新 filter 将改变可见样本身份，旧 state 或同名数据路径不能自动证明过滤索引兼容。验证应增加 filter 索引与源数据的版本、样本 ID / 有效 token、保存后未来序列复现，并明确原 Bridge 的同 DP size 消费者限制仍然成立。本轮没有执行这些测试。

补采的 filter 实现将原样本整数地址映射为过滤后的地址：manifest sidecar 位于 `.nv-meta/filter_<name>.json/.idx`，单文件数据使用旁置同名后缀，当前索引版本为 2。`FilterView` 验证版本、shard 名/顺序、原样本计数和 primary 文件 byte size，并按选定 split 的 shard 顺序翻译；它不校验 companion 文件或完整内容 hash，同大小改写不由这些检查自动识别。`TranslatedIndexReader` 将 restore key 的整数位置改为 filtered_index，故必须保留对应 filter 原件，不能换 filter 后沿用旧位置。上游 `test_filtered_training_recipe_checkpoint`、stale filter、分 rank/worker、BINIDX passthrough 测试提供特定范围参考，本轮未运行，不扩大为全部格式/分布式恢复兼容。

## 顺序 slice reader 与新增 packing 的恢复边界

在 `8ba04a3aa4200725a136258e00a6facf3bd15acd`，sampler 对支持 `SequentialSampleReader` 的 reader 延迟建立每个 active slice 的 `iter_slice(current, stop)`；整数 restore key 与 active slice 位置继续保存，打开的 iterator 不进入 checkpoint。`reset_state_own`、新迭代和 close 会关闭旧流，耗尽 slice 时也显式释放，恢复后从保存位置重新开流。普通 indexed reader 保留原逐样本读取路线。filter 的顺序 reader 仍负责 filtered_index 的身份翻译，不能用原始 sample index 替代它。

连续流改变 IO 路径，不改变此前 filter 文件/样本身份的校验限制，也不提供 Bridge 任意 DP size 的状态迁移。验证增加活跃 slice 中途保存、filtered reader、提前 break/close/再用，以及未来样本序列与 FD/host RSS；上游新增测试是已读证据，本轮没有执行。

Streaming packing 的 partial slice 和 pushback 也属于数据状态；保存/恢复必须与相同 encoder、混合单位、mask/有效 token 目标绑定。`SystemRng` 只保存/恢复 CPU 侧随机流，设备随机变换需要自管状态。新增或变化的数据路径先做同版本中断恢复，再评估旧 checkpoint 迁移，不能由吞吐或样本总数相同判定恢复正确。

## 固定证据与复核范围

- [src/megatron/energon/loader.py](https://github.com/NVIDIA/Megatron-Energon/blob/e33bbe768a4f7a629377a365c8af9a7b98b1219e/src/megatron/energon/loader.py)
- [src/megatron/energon/savable_loader.py](https://github.com/NVIDIA/Megatron-Energon/blob/e33bbe768a4f7a629377a365c8af9a7b98b1219e/src/megatron/energon/savable_loader.py)
- [src/megatron/energon/worker.py](https://github.com/NVIDIA/Megatron-Energon/blob/e33bbe768a4f7a629377a365c8af9a7b98b1219e/src/megatron/energon/worker.py)
- [docs/source/basic/save_restore.md](https://github.com/NVIDIA/Megatron-Energon/blob/e33bbe768a4f7a629377a365c8af9a7b98b1219e/docs/source/basic/save_restore.md)
- [docs/source/advanced/repro_scaling.md](https://github.com/NVIDIA/Megatron-Energon/blob/e33bbe768a4f7a629377a365c8af9a7b98b1219e/docs/source/advanced/repro_scaling.md)
- [docs/source/advanced/parallelism.md](https://github.com/NVIDIA/Megatron-Energon/blob/e33bbe768a4f7a629377a365c8af9a7b98b1219e/docs/source/advanced/parallelism.md)
- [tests/test_dataset.py](https://github.com/NVIDIA/Megatron-Energon/blob/e33bbe768a4f7a629377a365c8af9a7b98b1219e/tests/test_dataset.py)

- [src/megatron/energon/flavors/common/dataset_sampler.py](https://github.com/NVIDIA/Megatron-Energon/blob/e33bbe768a4f7a629377a365c8af9a7b98b1219e/src/megatron/energon/flavors/common/dataset_sampler.py)
- [src/megatron/energon/flavors/common/manifest/sharder.py](https://github.com/NVIDIA/Megatron-Energon/blob/e33bbe768a4f7a629377a365c8af9a7b98b1219e/src/megatron/energon/flavors/common/manifest/sharder.py)
- [src/megatron/energon/rng.py](https://github.com/NVIDIA/Megatron-Energon/blob/e33bbe768a4f7a629377a365c8af9a7b98b1219e/src/megatron/energon/rng.py)
- [docs/source/internals/compatibility.md](https://github.com/NVIDIA/Megatron-Energon/blob/e33bbe768a4f7a629377a365c8af9a7b98b1219e/docs/source/internals/compatibility.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
