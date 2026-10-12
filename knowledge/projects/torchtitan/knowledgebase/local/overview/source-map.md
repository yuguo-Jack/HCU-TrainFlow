---
id: official-torchtitan-wiki/source-map
title: TorchTitan 代码目录与问题定位地图
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
  path: torchtitan_recipes/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: a72fb9eab9eb7f376a50622327954f614694ed6aea5bb782aae51035e9c9157a
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
  path: torchtitan/config/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: e62e3776a4dd1c2179b3643d9e611f5a6f53fc972ac16de4588ee96a99a06b9b
- source: pytorch-torchtitan
  path: torchtitan/models/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: c8f50dedb90e280b96a6b0832c5cd76a7ae37daf1e11d18d70cca5407c281da6
- source: pytorch-torchtitan
  path: tests/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 0872f733f18e85e085802fff3813cd1ee359ec1cc10b8d5929642e62d4c4e712
pr_sources:
- pr-pytorch--torchtitan-5277
- pr-pytorch--torchtitan-5280
---
# TorchTitan 代码目录与问题定位地图

## 目录按责任分层

| 路径 | 主要职责 | 排查或修改时一起看的内容 |
| --- | --- | --- |
| `run_train.sh`、`torchtitan/train.py` | 单机示例 launcher、配置加载、构建和收尾 | 现场多机 launcher、环境、ConfigLoader；脚本默认不等于集群配置 |
| `torchtitan_recipes/models/`、`tests/models/` | 常规模型配方与集成测试配方 | 配方函数、模型 flavor、数据与优化器；debug 配方不代替正式模型 |
| `torchtitan_recipes/overrides/`、`rl/`、`graph_trainer/`、`torchft/` | 可组合覆盖、RL、实验训练与容错配方 | 对应实现及组合约束，避免只看函数名 |
| `torchtitan/config/`、`config/transform/` | 可构建 Config、验证、模型转换与 override | 转换顺序、并行上下文、量化/LoRA/dispatcher 兼容性 |
| `torchtitan/trainer.py` | 监督训练的数据、token 预算、循环、日志、验证 | `TrainingEngine`、数据 pipeline、loss 与 metrics |
| `torchtitan/training_engine.py` | 初始化模型、并行执行、前后向、优化器、checkpoint、profiler | 分布式包装、实际 Optim 和 Checkpointer 类型 |
| `torchtitan/models/<模型>/`、`models/common/` | 架构、flavor、attention、MoE、Linear、权重转换 | 实际使用的 recipe、算子 override 和对应单测 |
| `torchtitan/distributed/` | mesh、FSDP、PP、重算、graph、FlexShard 等 | 每个并行域实际成员、collective 顺序与 buffer 生命周期 |
| `torchtitan/components/data/`、`loss/`、`optim/`、`checkpointer/` | 数据、loss、优化器及可恢复状态 | token mask、参数分组、分片、异步保存和恢复一致性 |
| `torchtitan/quantization/` | TorchAO kernel 接入、低精度模块与 autograd | scale/布局、FSDP 权重生命周期、硬件限制 |
| `torchtitan/rl/` | 控制器、trainer、generator、rollout、环境、权重同步 | Monarch、TorchStore、vLLM 和数据/策略版本 |
| `torchtitan/observability/` | profiler、指标、结构化日志 | 日志统计窗口、trace 输出和显存快照 |
| `torchtitan/experiments/` | GraphTrainer、TorchFT、HF modeling backend | 各目录 README、CI 范围和未支持组合 |
| `scripts/`、`.ci/`、`tests/` | 安装、转换、损失对比、构建依赖、CPU/GPU/集成测试 | 当前真实调用参数、测试硬件与 golden 的来源 |

## 从现象追到调用链

| 问题 | 首先定位 | 下一步 |
| --- | --- | --- |
| 模型参数/优化器不符合预期 | recipe → `build_model_config` → flavor；`optim.optimizer.optimizers` | 看 Config 构造后的有效对象，核对权重分组 regex 和真实优化器类型 |
| 改 CP/EP 后尺寸或 mesh 错误 | `config/parallelism.py`、`distributed/parallelism_context.py` | 模型是否在新的 ParallelismConfig 下重新构造；不能只改字段 |
| loss 随 DP/packing 变化 | `Trainer.train_step` → token 计数 → `TrainingEngine.forward_backward` | loss token 与路由 token、reduce 分母、FSDP 梯度缩放 |
| GEMM/融合 kernel 慢 | 模型 forward → common module/override → 实际 kernel | 从 profile 提取前后向 shape/dtype/layout，再查对应 PR、基线和测试 |
| MoE A2A/负载不均 | router → token dispatcher → routed experts → combine | 每 rank 路由量、scratch 容量、通信等待和重算 replay |
| graph 后不更新或梯度丢失 | `distributed/cuda_graph.py` → `Optim.zero_grad` → parameter grad | capture/replay 使用的 buffer 与 Python `.grad` 是否保持同一生命周期 |
| checkpoint 完成但不能续训 | `components/checkpointer/base.py` → 具体 backend | model-only 导出与完整恢复的区别；检查 data/optimizer/scheduler/step |
| RL 首次权重同步 OOM | `rl/trainer.py`、`rl/generator.py`、`rl/model/vllm_wrapper.py` | CPU staging、FSDP group、KV cache 和权重版本同步 |

## 文件路径改动也是更新事件

近期目录重组把配方迁到 `torchtitan_recipes`，把测试分为 CPU/GPU/多卡。旧 PR 中的路径是当时证据，当前调用链要用固定新提交重新查。保留 PR base/head 链接，不把历史 diff 的文件名自动改成新路径。

[完整文件路径索引](../../upstream/source-map/pytorch-torchtitan.md)覆盖全仓目录，包含没有精读的文件；[原始树清单](../../../../../catalog/repositories/pytorch-torchtitan.json)保存 blob SHA。阅读本文可先缩小范围，再通过 `wiki-code` 或普通 Git checkout 看当前调用者、实现与测试。源码缓存可清理，公共 Wiki、教程和 PR 证据独立保存。

## 固定证据与使用边界

本页以官方主线 `65aaaa960698ab5d6e98c874177b41b9c30e9c58` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/README.md)
- [torchtitan_recipes/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan_recipes/README.md)
- [torchtitan/train.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/train.py)
- [torchtitan/trainer.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/trainer.py)
- [torchtitan/training_engine.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/training_engine.py)
- [torchtitan/config/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/config/README.md)
- [torchtitan/models/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/models/README.md)
- [tests/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/tests/README.md)

- [PR #5277：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5277.md)
- [PR #5280：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5280.md)