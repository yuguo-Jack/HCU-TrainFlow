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
reviewed_on: '2026-11-04'
coverage: frozen source delta and consumer review; unchanged files rechecked; no HCU runtime validation
sources:
- source: nvidia-megatron-lm
  path: pretrain_gpt.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 37bff81772b4cff0548d94876e9699a66276af578b3902c5bef13fbb5b7af612
- source: nvidia-megatron-lm
  path: gpt_builders.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 6cbcee1cfeb9cd6d7d0f89938c59e84380c713c9faf3436c5ff6c0b1a521ba18
- source: nvidia-megatron-lm
  path: model_provider.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 9e4fde24c6615e43ab242c1c9d69b4785554de3afd39a159488264e61c3ac653
- source: nvidia-megatron-lm
  path: megatron/training/arguments.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 91ec8ceb30b9af6d1bad58256e965e5b1f6cbf70ef120f450b09e570b2f44cce
- source: nvidia-megatron-lm
  path: megatron/training/initialize.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 2c84d59d36b0dc98f70c58670065b0cb9357197ea91463bd0ce0b6869505006b
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 1cfba3a404c97febc4c2e40895467372e6ab540006dc6a6e22fbc547087a5b75
- source: nvidia-megatron-lm
  path: megatron/core/parallel_state.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 0e773fa36d6e169825ea8cdd1d6547d8fcb8b3c18dde09d1ab45279c2018c4ee
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 39f34cb0f9005ad53b4d318346a7b6bbb88931a19d5f868805a42e83dd1eece6
- source: nvidia-megatron-lm
  path: megatron/training/argument_utils.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 3a71f13e18b312c4cf2e8a6830e225dfd855d9836b01f1a183a9c11af114d622
- source: nvidia-megatron-lm
  path: megatron/training/config/container.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 4965eeb1ad25b950348a29557799fd920f1c2207544c83992eb22e537a8758b2
- source: nvidia-megatron-lm
  path: megatron/training/config/dataset_config.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: ad183c58c35e91b065577d0f3fdb5ef89fbf6282a4e6de1fad1950926c8b030d
- source: nvidia-megatron-lm
  path: megatron/training/datasets/providers.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: a28174f91d974d5ac17d577ed53da2a71af8df16988edca006cc4ccac2c10938
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/optimizer_config.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: f83b46a8a901bb7c792076544e2fefda3b76830ef2d971ecb976f0ac557fbc67
retrieved_on: '2026-11-04'
---

# Megatron 代码目录：从配置、训练步到计算和恢复

## 目录与问题映射

| 位置 | 主要职责与调用者 | 建议问题入口 |
| --- | --- | --- |
| `pretrain_gpt.py` | get_batch、forward_step、loss_func；调用training pretrain | token/mask/packing/SFT loss |
| `gpt_builders.py`、`model_provider.py` | GPT配置、layer spec及pipeline-stage模型构造 | 模型结构/后端/spec不匹配 |
| `megatron/training/arguments.py` | CLI parse、兼容参数与仍保留的模型/运行约束 | flag 迁移、废弃 alias 和配置入口 |
| `training/argument_utils.py`、`training/config/container.py` | CLI→typed 配置；跨 section 校验、finalize | 参数默认/派生值、实际消费所有者 |
| `training/config/dataset_config.py`、`training/datasets/providers.py` | cfg.data 的类型、分词器绑定与 GPT dataset builder | 数据源/packing、构建 rank、声明但未消费字段 |
| `core/optimizer/optimizer_config.py` | optimizer-local/run/model 校验、dtype 与 alias 定稿 | 旧 validation 消失后应追的新位置 |
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

## 新布局与状态的精确入口

- `core/tensor_parallel/gtp_parallel_layout.py`：同一组 rank 的 token 与 weight 两种视图、独立 batch 数和权重复制数；继续到 `parallel_state.py` 的真实 group。
- `core/transformer/moe/virtual_expert_load_balancer.py`：路由规划、权重推送、虚拟梯度回并和对称内存释放；不是只有 dispatcher 改名。
- `core/full_cuda_graph.py` 与 `core/rerun_state_machine.py`：图内保存验证点的值、每次 replay 后的主机检查；不能通过关闭检查掩盖 capture 限制。
- `training/ckpt/glu_checkpointing.py`：模型 FC1 的规范行布局与 optimizer 的运行布局；与 `training/checkpointing.py` 的完整恢复入口一起核对。

本轮迁移有三个容易误判的入口：`get_megatron_optimizer_config` 已从 training.py 移除，配置由 dataclass 工厂构造并在 `OptimizerConfig.finalize_optimizer_config` 定稿；dataset provider 委托 `build_gpt_datasets(cfg.data)`；`train` 的数据源和 eval 由 `next_train_iterator`/`run_eval` 回调注入。旧 `core_gpt_dataset_config_from_args` 仍作为兼容 wrapper 重导出，不表示主要构建仍在 pretrain_gpt.py。`get_batch` 可接收模型携带的 process-group collection，不能只查全局 MPU。原 GTP、GLU 和 async/rerun 导航保留，其对应实现/状态所有者仍存在。

## 从症状进入源码

loss变化先查`pretrain_gpt.loss_func`和`schedules.forward_step_calc_loss`，再查训练report reduction及optimizer step；不是先改融合kernel。空泡先查data/host/PP/通信等待后再追driver。OOM沿param/grad/activation/gather/graph/checkpoint所有者查。恢复失败沿training tracker/config/RNG→Core strict/sharded metadata→backend和loader状态查。

Core→TE/cuDNN/编译器及通信库问题可以继续读实际底层依赖分支；保存源码SHA、import/库加载路径、调用参数和实际consumer。任务替换表为官方module→HCU实现→dispatch条件→测试/回退，不按库名推断同一实现。

## 查代码与更新

搜索示例：`wiki-search "start_param_sync" --engine megatron`；证据不足再`wiki-search-pr "parameter gather hook" --engine megatron`，读取最终head/base与caller/test。普通查阅只缓存，开发/PR使用独立最新checkout。

目录移动、新provider、新spec或配置迁移时联动[build/run](../guides/build-run-test.md)、[training](../topics/training-and-loss.md)、[overlap](../topics/overlap.md)及模型适配/优化Skill。批量源采集不能替代沿新的消费链复核正文。

## 固定源码与维护边界

- [pretrain_gpt.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/pretrain_gpt.py)
- [gpt_builders.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/gpt_builders.py)
- [model_provider.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/model_provider.py)
- [megatron/training/arguments.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/training/arguments.py)
- [megatron/training/initialize.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/training/initialize.py)
- [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/training/training.py)
- [megatron/core/parallel_state.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/parallel_state.py)
- [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/transformer/transformer_config.py)

2026-11-04按上述固定源码、实际消费者与官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。