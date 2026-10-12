---
id: official-megatron-wiki/energon
title: Megatron Energon：数据组织、Packing、吞吐与确定性恢复
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
  path: README.md
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 6309cd798e11e2f2b47d770eb0d3ebc24a34c1dc474c4ab8d86c7e923bb50b63
- source: nvidia-megatron-energon
  path: pyproject.toml
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: d10e46393b937e078fd34e0eedae62368944639d8052854a1b90f1f015ae9fbc
- source: nvidia-megatron-energon
  path: docs/source/basic/quickstart.md
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 59e78a090549aecec01aa86c5ae75ef37f56637a1045cf740446f6cc4c051a9f
- source: nvidia-megatron-energon
  path: docs/source/basic/task_encoder.md
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 0f10499347e02b15f04fbcdac053bccb4640ae205b8951c8bcff718443850164
- source: nvidia-megatron-energon
  path: docs/source/basic/save_restore.md
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: b6db5d6072470133817e393d13330d758159c872cc6fcd22299104d8bdf87c61
- source: nvidia-megatron-energon
  path: docs/source/advanced/parallelism.md
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 427aa86fba6a0bac1a9460255e46a93d7d67ec502a852d26105eccd313484f4e
- source: nvidia-megatron-energon
  path: src/megatron/energon/loader.py
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 00f4780c39c023c999acead866c3056128d4ff4b8c9678ead1ccb8f5d498d1f0
- source: nvidia-megatron-energon
  path: src/megatron/energon/savable_loader.py
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 8c1a5e58984cd33e41ec17fdc6a55ef1efd9b3a02e6d7606cfbef9da89f6865a
- source: nvidia-megatron-energon
  path: src/megatron/energon/task_encoder/base.py
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: d4fce3a940e2a673d3e7a40376f7741799b6c687b1e6ddea7202d66c8e943706
- source: nvidia-megatron-energon
  path: tests/test_dataset.py
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 1ec677b1de77c839ba1e7f4fbecce7eb786f9d09e0d6d506da755260dcf45694
pr_sources:
- pr-nvidia--megatron-energon-302
---

# Megatron Energon：数据组织、Packing、吞吐与确定性恢复

## 1. 定位与训练链路

Energon是可独立使用的多模态数据加载/处理组件，负责数据混合、shard、随机顺序、编码、packing、batch及可恢复加载，不执行GPU模型训练或优化器。Megatron/Bridge等消费者负责mask/position/模型输入、loss与保存关联；GPU空泡可能来自本组件，但不能据此把它当kernel分析库。

本页固定develop `accdabc3983843665a34cd1578c0e82d2403e3a9`，官方README提示研究型API可能变化。实际HCU父仓锁定的Energon与此develop分别核对，不能自动用latest替掉训练依赖。

## 2. 目录与问题路径

| 路径 | 职责/继续阅读 |
| --- | --- |
| `src/megatron/energon/loader.py` | `get_loader`/`get_savable_loader`与默认prefetch/checkpoint/watchdog |
| `savable_loader.py` | worker状态、periodic checkpoint/skip-forward、rank/global save/restore、close |
| `worker.py`、`rng.py` | DP shard、worker身份、seed/group与日志，数据重复/偏移先查这里 |
| `task_encoder/base.py` | encode、pack选择/聚合、batch、stateless与随机augmentation恢复 |
| `flavors/` | WebDataset/JSONL等格式、reader/index/shard和storage接口 |
| `wrappers/` | shuffle/mix/batch/map/watchdog等流水线与状态组合 |
| `metadataset/`及配置模块 | 数据混合/关联/分split配置，按完整树选择实际类 |
| `tools/`、CLI模块 | prepare/lint等数据预处理，不代替语义/模型验收 |
| `tests/test_dataset.py`、`test_dataset_det.py`等 | 数据覆盖、生命周期、确定性/恢复；IO/平台条件单列 |
| `docs/source/basic`、`advanced` | 使用、TaskEncoder、恢复、packing、并行、错误处理 |

官方internals code_structure目前不是完整实现手册，以上路径来自固定树与实际源码；不能以空占位文档宣称全架构已解释。

## 3. 安装与依赖

当前包Python>=3.10、hatchling/hatch-vcs构建；torch、WebDataset、storage client、Pillow/PyYAML等构成基本依赖。video/audio decode、torchvision transforms和不同云存储有optional extras，按数据类型安装，不用`all`掩盖不需要的重量依赖。HCU保留已有Torch配对，确认实际`megatron.energon`import路径与版本，避免源码copy或namespace冲突。

官方提供stable PyPI与Git安装开发版，二者有区别；固定版本和数据schema/TaskEncoder code revision一起保存。单机CPU读取可先验，但不能推定共享存储、多机、video decoder和训练集成均通过。

## 4. 准备、运行与测试

WebDataset先`energon prepare DATASET_ROOT`建立元数据，`energon lint DATASET_ROOT`检查格式/样本可加载；JSONL有对应支持及限制，按版本文档确认。prepared/lint成功不保证tokenization、mask/label或数据混合目标正确。

library从WorkerConfig和TaskEncoder创建train/val dataset，再`get_loader`或`get_savable_loader`迭代。**WorkerConfig属于dataset**，继续传loader的旧worker_config参数已弃用，不会重配dataset，配置不一致会报错。dataset已包含batch/packing组织，不能让普通TorchDataLoader再重复batch。

验证先少量样本/数据类型、ID/encoder输出与batch契约，再正常迭代→保存恢复→提前退出close→异常样本→多rank。相邻单测和确定性测试提供入口；本轮没有执行上游Python/GPU测试。成功标准是实际样本/有效token、复现性、资源释放和消费者数值，不能只看loader持续yield。

## 5. 样本、数值与状态所有权

固定dataset split/blend权重、shards/index、tokenizer/encoder、augmentation、seed、shuffle、packing与MB。global rank不直接等于数据DP rank；同一model-parallel replica可能各rank独立读取相同batch，也可能由一个rank读后广播，按消费者确定。

TaskEncoder保证sample变换与packing/batch语义；training保证causal/segment mask、position、cu-seqlens、labels和loss分母。packing减少padding但不能允许不相关样本互相attention或改归一化。保存loader state包含worker/RNG/wrapper/消费offset，不只是globalstep；模型、optimizer和数据checkpoint要绑定同一训练时刻。

## 6. 调用链

storage reader→dataset factory/shard→shuffle/mix/wrapper→TaskEncoder.encode→packing buffer/select/pack→batch→loader worker/prefetch→训练消费者。SavableLoader周期保存worker状态，主进程记录实际消费位置，恢复回到相应checkpoint并重放偏移；close由loader统一停止workers/iterator并关闭dataset资源。

`get_loader`为BasicDataLoader，`get_savable_loader`为SavableDataLoader；其内部checkpoint与训练持久checkpoint是不同层次。API默认不等于所有数据的最佳值。

## 7. 两项深入机制

- [TaskEncoder、Packing与确定性](topics/energon-encoding-packing.md)：减少padding的收益、buffer开销、stateless/restore_seeds及模型mask契约。
- [加载吞吐、保存恢复与生命周期](topics/energon-recovery-throughput.md)：prefetch/worker/IO导致GPU空泡、snapshot+offset、缩扩限制、watchdog与资源关闭。

## 8. 诊断、恢复和训练质量

GPU等待数据先对齐batch-ready时间、worker栈、IO/decode/CPU、queue、hostRSS/FD与H2D，再用mock隔离模型计算；不能一见空泡就改kernel或无条件增加workers。默认普通错误可能log并skip样本，restore默认严格抛错；skip会改变数据分布/有效token，应计数告警，不能当健康训练。

watchdog timeout会打印worker栈，只有相应fail_on_timeout策略才导致失败，均不等于集群容错。结合唯一恢复owner定位IO/损坏样本/队列，保留loader/data身份。连续与中断恢复比较样本ID、batch、随机状态和有效token，按消费者实际model-parallel读法在所有需要rank恢复。

## 9. PR、文档与更新

[官方教程](https://nvidia.github.io/Megatron-Energon/)、[Releases](https://github.com/NVIDIA/Megatron-Energon/releases)、[PR](https://github.com/NVIDIA/Megatron-Energon/pulls)、[全仓导航](../source-maps/nvidia-megatron-energon.md)、[原文目录](../upstream-docs/nvidia-megatron-energon/)分别补使用/版本/讨论/源码。没有独立本地roadmap则按官方Issue/Discussion继续查证，不从PR标题编造计划。

[#301 close后dataset可复用](../prs/NVIDIA--Megatron-Energon/PR-301.md)提供对象所有权与资源清理讨论，本轮固定测试也覆盖dataset重用；[#302](../prs/NVIDIA--Megatron-Energon/PR-302.md)仍是open，iterator finalize细节不能据标题写为已落地。当前源码仍保留loader析构清理，不把PR描述每个提议直接当最终实现。

`wiki-search-pr "restore packing/loader close" --engine energon`可补未收录问题，随后读固定代码/测试。更新loader/worker/TaskEncoder/wrappers与消费者Bridge的数据checkpoint同时复核本页和两专题；major版本、DP/worker数、encoding变化保留各自恢复范围。

## 固定证据与复核范围

- [README.md](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/README.md)
- [pyproject.toml](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/pyproject.toml)
- [docs/source/basic/quickstart.md](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/docs/source/basic/quickstart.md)
- [docs/source/basic/task_encoder.md](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/docs/source/basic/task_encoder.md)
- [docs/source/basic/save_restore.md](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/docs/source/basic/save_restore.md)
- [docs/source/advanced/parallelism.md](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/docs/source/advanced/parallelism.md)
- [src/megatron/energon/loader.py](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/src/megatron/energon/loader.py)
- [src/megatron/energon/savable_loader.py](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/src/megatron/energon/savable_loader.py)
- [src/megatron/energon/task_encoder/base.py](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/src/megatron/energon/task_encoder/base.py)
- [tests/test_dataset.py](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/tests/test_dataset.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
