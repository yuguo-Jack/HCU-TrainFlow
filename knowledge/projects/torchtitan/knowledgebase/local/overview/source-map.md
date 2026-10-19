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
reviewed_on: '2026-10-20'
coverage: Curated source chains and official evidence at a fixed main commit; not all models, backends
  or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 3634007b5cca45b6e3ce61742e818c4c7fdb9c5147092cc4872e0752c00f7b75
- source: pytorch-torchtitan
  path: torchtitan_recipes/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: a72fb9eab9eb7f376a50622327954f614694ed6aea5bb782aae51035e9c9157a
- source: pytorch-torchtitan
  path: torchtitan/train.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: ccdc21c169ecd6e16133a06ee17c9cce8587389c1b06b60bac798ef5571efb3b
- source: pytorch-torchtitan
  path: torchtitan/trainer.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: c49922cf3d47918901135fc0b798141479cb16b24fb1004b19b255a663c13288
- source: pytorch-torchtitan
  path: torchtitan/training_engine.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 04d566f414d65830070069c7bde9eba232da16a23f329abc4446f565abb2006e
- source: pytorch-torchtitan
  path: torchtitan/config/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: e62e3776a4dd1c2179b3643d9e611f5a6f53fc972ac16de4588ee96a99a06b9b
- source: pytorch-torchtitan
  path: torchtitan/models/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 305862c59075c4425651256a40d0fa0c04f412eec5cbdc949a4769f49a0c1f2f
- source: pytorch-torchtitan
  path: tests/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 0872f733f18e85e085802fff3813cd1ee359ec1cc10b8d5929642e62d4c4e712
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 5f4cdb46330683cb8bd2a65d764662712972fb8989afe35a9b9dfbe5e3270209
- source: pytorch-torchtitan
  path: torchtitan/models/common/linear/linear.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 6fa01212bbaa44502862b3aba0b16e1955a77a09cbda6ff304839836a42834f0
- source: pytorch-torchtitan
  path: torchtitan/models/common/moe/moe.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 624dec01425b93538969ddea2d68e1f9a3465bd77076ea1746c55d6f7fcb0315
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/engine_loop.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 9c4679f1923f8d2f0a946b8576bccec5a810bf54e3996cc5c0af385341222a15
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
| `torchtitan/models/<模型>/`、`models/common/{attention,linear,moe}/` | 架构、flavor、attention、MoE、Linear、权重转换 | 实际使用的 recipe、算子 override 和对应单测 |
| `torchtitan/distributed/` | mesh、FSDP、PP、重算、graph、FlexShard 等 | 每个并行域实际成员、collective 顺序与 buffer 生命周期 |
| `torchtitan/components/data/`、`loss/`、`optim/`、`checkpointer/` | 数据、loss、优化器及可恢复状态 | token mask、参数分组、分片、异步保存和恢复一致性 |
| `torchtitan/quantization/` | TorchAO kernel 接入、低精度模块与 autograd | scale/布局、FSDP 权重生命周期、硬件限制 |
| `torchtitan/rl/{controller,trainer,generator,actors,routing,rollout}/` | 独立服务、engine loop、actor placement、路由、环境与model state dict传输 | `actors/monarch/`、TorchStore、`generator/vllm/` 和数据/策略版本 |
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
| RL 首次权重同步 OOM | `rl/trainer/trainer.py`、`rl/generator/engine_loop.py`、`rl/generator/vllm/model_wrapper.py` | CPU staging、FSDP group、KV cache 和权重版本同步 |

## 文件路径改动也是更新事件

近期目录重组把配方迁到 `torchtitan_recipes`，把测试分为 CPU/GPU/多卡。旧 PR 中的路径是当时证据，当前调用链要用固定新提交重新查。保留 PR base/head 链接，不把历史 diff 的文件名自动改成新路径。

[完整文件路径索引](../../upstream/source-map/pytorch-torchtitan.md)覆盖全仓目录，包含没有精读的文件；[原始树清单](../../../../../catalog/repositories/pytorch-torchtitan.json)保存 blob SHA。阅读本文可先缩小范围，再通过 `wiki-code` 或普通 Git checkout 看当前调用者、实现与测试。源码缓存可清理，公共 Wiki、教程和 PR 证据独立保存。

## 当前入口与 FQN 的迁移检查

- 原 `models/common/linear.py` 的实现位于 `models/common/linear/linear.py`，对外 re-export 与实现文件分开；Async Linear 和 inplace helper 在同一包。普通 MoE 与 token dispatcher 在 `models/common/moe/`。
- 多种 decoder 的 MoE 现在是 `layers.<id>.feed_forward`；Kimi 的 KDA/MLA 都是 `layers.<id>.attention`，不再用 `delta_attention` 或独立 `moe` 字段。对应 checkpoint adapter、optimizer regex、override/remat FQN 和 trace 名一起核对。
- `distributed/activation_remat.py` 放 plain dataclass 配置，入口是 `activation_remat.apply(model)`；旧 `SelectiveAC.Config().build()` 不再是当前调用链。
- RL 的 Controller 由 `actors/system.py` 定义的接口取得 handles；Monarch placement、GPU mesh 与 TorchStore client 初始化在 `actors/monarch/`。领域层不直接导入 Monarch；不要继续在已删除的 `rl/distributed/WEIGHT_SYNC.md` 或 `rl/model/` 找当前实现。
- RL 请求失败先追 `generator/engine_loop.py`、`generator/dispatcher.py`，模型加载追 `generator/vllm/model_wrapper.py`，CPU 顺序测试现为 `test_trainer_loop.py`。历史 PR 路径仍按其固定 base/head 保留。

## 固定证据与使用边界

本页以官方主线 `a242475253433725f10f39c18f5ccbfdf188e097` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/README.md)
- [torchtitan_recipes/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan_recipes/README.md)
- [torchtitan/train.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/train.py)
- [torchtitan/trainer.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/trainer.py)
- [torchtitan/training_engine.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/training_engine.py)
- [torchtitan/config/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/config/README.md)
- [torchtitan/models/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/models/README.md)
- [tests/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/README.md)

- [PR #5277：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5277.md)
- [PR #5280：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5280.md)

## 本次补充的实现与测试依据

- [torchtitan/rl/actors/monarch/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/actors/monarch/README.md)
- [torchtitan/models/common/linear/linear.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/models/common/linear/linear.py)
- [torchtitan/models/common/moe/moe.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/models/common/moe/moe.py)
- [torchtitan/rl/generator/engine_loop.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/generator/engine_loop.py)
