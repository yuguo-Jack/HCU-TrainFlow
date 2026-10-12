---
id: official-torchtitan-wiki/overview
title: TorchTitan 官方工程：定位、能力边界与阅读路线
engine: torchtitan
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: Curated source chains and official evidence at a fixed main commit; not
  all models, backends or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: dd4941f16439ed538500a40fe13f02f49d87c51c7a7a419289bee3e3d3e3d9bb
- source: pytorch-torchtitan
  path: RELEASE.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 8388a4b6b862d114c98eb7887ddf1700c9408c5e13991b62e2868a2be5add126
- source: pytorch-torchtitan
  path: pyproject.toml
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 0341afacb518276f192c2c8a836c32426e80856bf8c5f0ff194c3028c221520d
- source: pytorch-torchtitan
  path: torchtitan/train.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: ccdc21c169ecd6e16133a06ee17c9cce8587389c1b06b60bac798ef5571efb3b
- source: pytorch-torchtitan
  path: torchtitan/trainer.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: e7a7162304a1741cfa86ef7969d7619f985f2263f9aace617bdc6955185c41f4
- source: pytorch-torchtitan
  path: torchtitan/training_engine.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 9c6293218d8c0a6ea50e3e1ac060d8a78b6df8eae4156009f7868016f7b6cdfd
- source: pytorch-torchtitan
  path: torchtitan/rl/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: d0cced32ef4222b2473689607eadcb749cbb4650e6da9da27df32353842908e6
---
# TorchTitan 官方工程：定位、能力边界与阅读路线

## 在 TrainFlow 中的定位

TorchTitan 是 PyTorch 原生训练工程，围绕 DTensor、DeviceMesh、FSDP2 及张量/流水线/上下文/专家并行组织训练。当前主线同时包含预训练、SFT、TitanRL，以及图编译、低精度和分布式算子的实验路径。它适合研究 PyTorch 原生训练如何把模型、并行布局、优化器、数据和可恢复训练组织起来；不能把它简单看作另一份 Megatron 启动脚本。

本 Wiki 单独维护官方主线的模型语义和实现机制。HCU 上部署时，仍先通过 HCU-Knowledge 查找适用的 HCU 分支、Torch/DTK/算子库和站点脚本；没有验证的上游 CUDA 特性保留为参考。这里没有声明新增一个已在 HCU 跑通的训练后端。

## 建议阅读顺序

| 任务 | 入口 | 应带走的结果 |
| --- | --- | --- |
| 找代码、确定责任归属 | [目录与调用链](source-map.md) | recipe、引擎、分布式、算子和测试的准确入口 |
| 安装并跑通模型 | [构建运行与测试](build-run-test.md)、[模型与数据](models-and-data.md) | 版本锁、有效配置、模型语义、依赖与短跑基线 |
| loss、梯度或优化器异常 | [训练与数值](training-and-numerics.md) | token 分母、梯度缩放、优化器分组与证据对照 |
| 卡数、显存、吞吐权衡 | [并行与显存](parallelism-and-memory.md) | mesh、微批、重算、驻留和通信开销 |
| 编译、融合和 overlap | [编译与通信](compile-fusion-and-communication.md)、[MoE 与低精度](moe-and-low-precision.md) | 实际执行路径、适用条件及回退 |
| profile 与瓶颈解释 | [性能采集与诊断](profiling-and-diagnosis.md) | 多 rank 证据、TraceLens 分析与算子优化优先级 |
| 长稳、恢复、扩展 DP | [checkpoint 与稳定性](checkpoint-and-stability.md) | 完整恢复状态、存储压力和唯一恢复控制方 |
| 强化学习训练 | [TitanRL](titanrl.md) | rollout、权重版本、trainer/generator 精度与内存边界 |
| 查 PR、判断过时、更新 | [版本、教程与更新](releases-prs-and-update.md) | release/main/open PR 的区别和增量复核路线 |

## 能力与验证分开看

- **标准训练路径**：`Trainer` 负责数据与监督训练循环，`TrainingEngine` 负责模型、前后向、优化器和状态；RL 复用引擎而不复用整个监督训练循环。
- **配置方式**：当前主线使用 Python recipe；`torchtitan_recipes` 是独立顶层包。旧 TOML、旧 CLI 字段和旧目录必须按提交核对，不能混用。
- **分布式与性能**：FSDP2/HSDP、TP/PP/CP/EP、区域重算、局部编译、MoE dispatcher、低精度模块均有各自约束，并非任意组合都被验证。
- **实验路径**：GraphTrainer、TorchFT、NVFP4、特定 RL 模型和未合入优化分别记录成熟度。功能出现在源码里不代表全部模型、后端、精度和并行组合都可用。
- **硬件边界**：MXFP8/NVFP4、CuTe/Dist-MoE、对称显存、attention 后端和 graph 的要求需逐项核对。当前 `cuda_graphs_supported()` 显式排除 ROCm；设置开关不代表真实捕获执行。

## 重点优化案例

1. [WGRAD 原地累积](cases/inplace-wgrad-accumulation.md)：减少显存流量，但必须守住梯度所有权、累积精度和 PP 调度约束。
2. [Kimi Attention Residual 融合](cases/kimi-attnres-fusion.md)：独立算子显著提速，端到端却不一定胜过局部编译。
3. [RL 权重同步内存](cases/rl-weight-sync-memory.md)：分别减少训练侧临时权重与生成侧全模型双份驻留。

查不到答案时，通过 Wiki search 的在线 PR 检索追到官方 PR 和固定 head/base 源码；本地只精选部分专题，不意味着未精选的模型、PR 或文件不可检索。

## 固定证据与使用边界

本页以官方主线 `65aaaa960698ab5d6e98c874177b41b9c30e9c58` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/README.md)
- [RELEASE.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/RELEASE.md)
- [pyproject.toml](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/pyproject.toml)
- [torchtitan/train.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/train.py)
- [torchtitan/trainer.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/trainer.py)
- [torchtitan/training_engine.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/training_engine.py)
- [torchtitan/rl/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/rl/README.md)

## 本轮机制更新入口

[并行与显存](parallelism-and-memory.md)补充 EMA pinned CPU 初始化；[MoE 与低精度](moe-and-low-precision.md)补充全局 batch 辅助 loss 计数语义；[TitanRL](titanrl.md)补充单请求失败、会话路由释放与 engine loop 故障边界。实际配置、模型 loss 与生成权重版本仍按同一上下文验收。