---
id: official-megatron-wiki/source-map
title: Megatron 代码目录：从配置、训练步到计算和恢复
engine: megatron
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: reviewed training, parallel, state and backend implementation chains; not
  all models or runtime combinations
sources:
- source: nvidia-megatron-lm
  path: pretrain_gpt.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: ead299ef4e42cd444a931fe61d5778b274acae572d9fca3025de5549dd2c02f5
- source: nvidia-megatron-lm
  path: gpt_builders.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 6cbcee1cfeb9cd6d7d0f89938c59e84380c713c9faf3436c5ff6c0b1a521ba18
- source: nvidia-megatron-lm
  path: model_provider.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 9e4fde24c6615e43ab242c1c9d69b4785554de3afd39a159488264e61c3ac653
- source: nvidia-megatron-lm
  path: megatron/training/arguments.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: eca958faeab77e1df81073998ea07aa3cc8a5884f96f6182782d620942139bd2
- source: nvidia-megatron-lm
  path: megatron/training/initialize.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: e093f7728b47ae4ef7b3310fd13ecc243805cd309976d7a846fb23b338cb7fda
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: e436206da1fe3ec5b8b5da8a06e1c8d6a7e08f149a0079107d83f1d68284e469
- source: nvidia-megatron-lm
  path: megatron/core/parallel_state.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 414ecaf3b1891e8d621e5ec86a80af9d2d313d4393ac11e83832ff4bf7257dd2
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 36ebc84d850af5653d6f17aa2147f61b79f82b7a05422b8d0eba8943bafb0f87
---

# Megatron 代码目录：从配置、训练步到计算和恢复

## 目录与问题映射

| 位置 | 主要职责与调用者 | 建议问题入口 |
| --- | --- | --- |
| `pretrain_gpt.py` | get_batch、forward_step、loss_func；调用training pretrain | token/mask/packing/SFT loss |
| `gpt_builders.py`、`model_provider.py` | GPT配置、layer spec及pipeline-stage模型构造 | 模型结构/后端/spec不匹配 |
| `megatron/training/arguments.py` | parse、validation与旧flag约束 | 同名flag语义变动、optimizer配置 |
| `training/argument_utils.py`、配置/全局服务 | argv转typed运行/模型配置 | 明明设置了flag却走默认值 |
| `training/initialize.py` | 分布式初始化、设备、seed和依赖 | bootstrap卡住、rank/device错位 |
| `training/training.py` | setup、train_step、train、日志、profile和save/eval切换 | step空泡、跳步、数据消费与调度 |
| `core/parallel_state.py` | 创建TP/PP/CP/DP/EP等group | 一个rank实际属于哪个域 |
| `core/pipeline_parallel/schedules.py` | 非pipeline/非交错/交错fwd/bwd与P2P | PP bubble、微批不整除、loss缩放 |
| `core/models/gpt/`、`core/transformer/` | 层spec、attention/MLP/MoE、config validation | 融合分支、重算、shape/精度 |
| `core/extensions/transformer_engine.py` | Core语义到TE模块与recipe | TE ABI、first-microbatch、低精度缓存 |
| `core/distributed/` | DDP hooks、param/grad buffer/bucket、FSDP | 梯度/参数通信、显存与同步顺序 |
| `core/optimizer/` | optimizer主状态、分片、CPU offload | 更新、clip、overflow和峰值 |
| `core/dist_checkpointing/`、`training/checkpointing.py` | 分片后端与训练状态保存/加载 | async finalize、shard不完整、恢复拓扑 |
| `core/rerun_state_machine.py` | 数值结果重跑/异常与保存退出决策 | 非有限loss、重跑与数据游标 |
| `tests/unit_tests/`、`tests/functional_tests/`、`examples/` | 局部行为、分布式训练与官方recipe | 定义修改所需验证范围 |

具体符号/语义见[工程指南](engineering-guide.md)及[总览](overview.md)各专题。完整路径清单见[来源地图](../../upstream/source-map/nvidia-megatron-lm.md)；目录存在说明可追查，不说明每个文件都已精读。

## 配置消费链必须闭合

实际HCU模型脚本→最终argv/环境→parse与validate→argument-utils/TransformerConfig→provider/layer spec→module→backend→真实trace/测试。当前仓含typed cfg与历史args共存，`training.py`的一些服务设置从`get_run_config()`读取；不要只改args字段而未确认cfg传播。

模型配置、运行/记录配置、并行组、optimizer/precision配置分别表达。选定一项优化时记录定义、消费、约束和接口测试四个位置；编译成功或flag被接受不能代替实际dispatch证据。

## 从症状进入源码

loss变化先查`pretrain_gpt.loss_func`和`schedules.forward_step_calc_loss`，再查训练report reduction及optimizer step；不是先改融合kernel。空泡先查data/host/PP/通信等待后再追driver。OOM沿param/grad/activation/gather/graph/checkpoint所有者查。恢复失败沿training tracker/config/RNG→Core strict/sharded metadata→backend和loader状态查。

Core→TE/cuDNN/编译器及通信库问题可以继续读实际底层依赖分支；保存源码SHA、import/库加载路径、调用参数和实际consumer。任务替换表为官方module→HCU实现→dispatch条件→测试/回退，不按库名推断同一实现。

## 查代码与更新

搜索示例：`wiki-search "start_param_sync" --engine megatron`；证据不足再`wiki-search-pr "parameter gather hook" --engine megatron`，读取最终head/base与caller/test。普通查阅只缓存，开发/PR使用独立最新checkout。

目录移动、新provider、新spec或配置迁移时联动[build/run](../guides/build-run-test.md)、[training](../topics/training-and-loss.md)、[overlap](../topics/overlap.md)及模型适配/优化Skill。批量源采集不能替代沿新的消费链复核正文。

## 固定源码与维护边界

- [pretrain_gpt.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/pretrain_gpt.py)
- [gpt_builders.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/gpt_builders.py)
- [model_provider.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/model_provider.py)
- [megatron/training/arguments.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/training/arguments.py)
- [megatron/training/initialize.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/training/initialize.py)
- [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/training/training.py)
- [megatron/core/parallel_state.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/parallel_state.py)
- [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/transformer/transformer_config.py)

2026-10-12按上述固定源码/官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。
