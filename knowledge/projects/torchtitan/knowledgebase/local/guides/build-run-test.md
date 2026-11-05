---
id: official-torchtitan-wiki/build-run-test
title: TorchTitan 安装、Python 配方、启动与分层测试
engine: torchtitan
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-11-04'
retrieved_on: '2026-11-04'
coverage: Curated source chains and official evidence at a fixed main commit; not all models, backends
  or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: pyproject.toml
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 4c8bd1c4a4c82eaea345ccb97abf671a1e59faf92df2d9fa147ce21c5e7fe780
- source: pytorch-torchtitan
  path: .ci/docker/requirements.txt
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 099347f7fad10ba1a21e9e689bf27e8bb4cff19e4e2716addef18cd7e17c3486
- source: pytorch-torchtitan
  path: .ci/docker/requirements-rl.txt
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 1ab5e0be999db70997ace51b9413fc398e651048f063fdd7ca6c272ef28559d9
- source: pytorch-torchtitan
  path: run_train.sh
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: f88bd97eff8c7a4b8623dae59ed03a94d80bf7fb9b7941e376f7caddd74863ee
- source: pytorch-torchtitan
  path: torchtitan/config/loader.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 809e852e7f25119748c6ab27be9eab0750f129f4e899935116768129d12df1e9
- source: pytorch-torchtitan
  path: torchtitan/config/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: e62e3776a4dd1c2179b3643d9e611f5a6f53fc972ac16de4588ee96a99a06b9b
- source: pytorch-torchtitan
  path: torchtitan_recipes/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 80bf0cdce6473544775bf13189368107b72642a97efb075a9486e77a21ecbe1c
- source: pytorch-torchtitan
  path: torchtitan_recipes/tests/models/llama3.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: a248bb7d8e9b72b304281491fd594e8f7ad2f0a53dac03672f9e36e8057853f9
- source: pytorch-torchtitan
  path: tests/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 73f9a9597a0aaeef657c103ec1cc544375c0e9229f49a9a50abcd8d3a02af248
- source: pytorch-torchtitan
  path: docs/debugging.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 523e0d62eca05f837e9ec4da6530a60e4cd95a8f8f55d7f2a8a0f8b1d542fd49
- source: pytorch-torchtitan
  path: torchtitan/models/flux/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 945d9a8a89c7726d786a526c20e141814300a33f6fed8736d697fcf69853c8a4
- source: pytorch-torchtitan
  path: torchtitan/rl/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: c4f1816a03546f6ffd5d800a3008aedfdf24a9fa34161a6cfa3fb5cae6184c72
- source: pytorch-torchtitan
  path: torchtitan/config/configs.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 3465866709813651cc91114c4a006a5cc3c05d6069e9f04200e68d10c91c3659
- source: pytorch-torchtitan
  path: torchtitan/distributed/activation_remat.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 4e935605e29f904ad5c5bef1036e265021f42c334a7a17c6d01083040dffc5a7
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 3b46f79840dec9f3efd25319247fe259c0009daeec74bf381d06c483ddea8b09
- source: pytorch-torchtitan
  path: torchtitan/config/parallelism.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 64e4a9d95288e2de09146dd99dd075760a74265f9e8c2384a36f0995d3546232
- source: pytorch-torchtitan
  path: torchtitan/distributed/local_compile.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 258d7980f3a28c310d0fb1a31319c4124677de921de573d6fd22878879a96f93
- source: pytorch-torchtitan
  path: torchtitan/training_engine.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 2ffe06874d3a03ccc91d407f1bc91d5f2beaa9c746738dd3a3646f1c800a798f
- source: pytorch-torchtitan
  path: tests/unit_tests/cpu/test_trainer.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: b9681edfc274190ede7dcbba70a8bc82b814b51d4facf3618feb3c6961e0891d

pr_sources:
- pr-pytorch--torchtitan-5277
- pr-pytorch--torchtitan-5280
- pr-pytorch--torchtitan-5288
---
# TorchTitan 安装、Python 配方、启动与分层测试

## 1. 先锁提交和环境

本页是所引用官方提交的使用说明，不是 HCU 已验证安装脚本。官方要求 Python 3.11+，使用较新的 PyTorch nightly 及匹配 TorchAO/扩展；必须核对 `.ci/docker/requirements*.txt` 和实际 recipe。不能在 HCU 环境执行官方 CUDA wheel 安装命令来覆盖现有 Torch。

基础依赖包含 Grain、datasets、tokenizers、renderers、safetensors，以及版本明确的 `spmd_types`、`torch_remat`、`torch_checkpointing`。RL 另外涉及 Monarch、TorchStore、vLLM、环境/奖励依赖；FLUX/VLM/开发测试使用各自 extra。锁下列信息：TorchTitan SHA、Torch/DTK、TorchAO、attention 与通信扩展版本、Python、构建选项、设备型号和可用并行规模。官方 `.ci` 的 wheel/硬件选择只适用于它明确支持的平台。

在匹配依赖已就绪的环境中，可用 `python -m pip install -e . --no-deps` 安装该 checkout；`--no-deps` 不会补依赖，也不证明依赖兼容。当前 `pyproject.toml` 同时打包 `torchtitan` 和 `torchtitan_recipes`；从旧版本升级后重新安装，否则在仓外可能找不到新 recipe 包。

## 2. 当前配置入口

`ConfigLoader` 以 `--module` 导入 Python 模块，用 `--config` 指定返回 Config 的函数。主要变更放在 recipe 或有类型的 `--override` 中。当前保留的运行控制包括 `--comm-backend`、`--output-dir`、`--resume-step`、`--print-config`；不能照抄旧文档中的任意 `--training.*`/TOML 字段。

```bash
# 官方 debug recipe 的单机单进程入口；数据/tokenizer 和匹配 GPU 环境须先就绪。
NGPU=1 MODULE=torchtitan_recipes.tests.models.llama3 \
  CONFIG=llama3_debugmodel ./run_train.sh

# 查看该提交的解析器；正式启动前保存最终 recipe、override 和有效配置。
python -m torchtitan.train --help
```

`run_train.sh` 默认 `NGPU=8`，即使某篇模型 README 把省略 NGPU 的命令称作单卡，也应看脚本实际默认。脚本通过 localhost rendezvous 启动单机 `torchrun`，**不提供可直接照用的多机集群配方**。多机需采用现场 launcher：一致的共享代码/数据、节点数、每节点进程数、node rank、rendezvous、接口和通信库配置，并保存各 rank 环境。TorchTitan recipe 描述模型语义，现场 HCU 脚本描述如何正确运行，两者必须同时核对。

改变 CP/EP/TP 时应先构造 `ParallelismConfig`，将其传给 `build_model_config` 再建立 Trainer.Config。当前模型 Config 已包含分片布局；模型建完后单独修改 CP/EP 字段可能留下错误配置。

## 3. 测试分层及其证明范围

| 层次 | 官方入口 | 可以证明 | 不可以证明 |
| --- | --- | --- | --- |
| CPU unit | `python -m pytest tests/unit_tests/cpu` | 配置、状态与可在 CPU 覆盖的逻辑 | GPU kernel、通信或性能 |
| GPU unit | `tests/unit_tests/gpu`；按测试 marker 选择单/多卡 | 指定硬件/后端下的局部正确性 | 未运行的模型/并行组合 |
| Fake PG 集成 | `tests.integration_tests.run_tests` 的 `fake_pg` 模式 | 虚拟并行 shape、编译与 API 路径 | 真实 all-reduce/A2A、跨 rank 梯度及吞吐 |
| Real PG 集成 | 同入口的 `real_pg`、实际 `--ngpu` | 真正通信与相应数值/性能回归 | 长训练收敛、故障恢复与所有卡型 |
| RL 测试 | `tests/rl/unit_tests/{cpu,gpu}`、相应集成配方 | trainer/generator/权重同步的特定组合 | 所有预训练模型均可用于 RL |
| 阶段验收 | 同数据、状态与有效 token 的参考短跑和阶段 loss | 本次改动在该环境的接受依据 | 仅凭上游 golden 推断 HCU 等价 |

```bash
python -m tests.integration_tests.run_tests --help
python -m tests.integration_tests.run_tests ./outputs/integration \
  --test_suite features,models --execution_mode fake_pg --ngpu 1
```

Fake PG 仍需它使用的 GPU 算子和依赖，不是纯 CPU 模拟器。PP 可通过 `FAKE_PP_RANK` 或 `real_pp_fake_spmd` 有限检查；后者只把 PP 通信变真，其他域仍可为 fake。正式性能、loss 或故障结论必须使用 Real PG。

## 4. HCU 适配顺序

先复用 HCU 兼容 Torch/DTK 环境与已支持模型脚本，再对照官方 recipe 的模型结构、优化器、数据、mask、精度和训练目标。逐项核实 attention、TorchAO、Triton/CuTe、DeepEP、Monarch/TorchStore 的实际实现；缺少某后端时选语义一致的实现并记录差异，不能用 debug recipe 或换优化器掩盖模型不匹配。

完成导入/配置检查、小规模真实训练、局部正确性和恢复基线后再分析性能。只缩 layer 也应保持架构合法；其他维度变动需任务明确授权并标为流程验证模型。出现配置/ABI/后端错误时，沿 [源码地图](../overview/source-map.md) 追查，不把反复重新安装作为默认处理。

## 本固定开发线的升级检查

依赖清单新增 `pyarrow<26`，renderers 为0.1.12、attn-gym 为0.0.17，`spmd_types==0.3.1`、`torch_remat==0.2.2`、`torch_checkpointing==0.1.1` 已由旧 Git 固定提交改为发行版依赖；这些只是当前 `.ci` 的版本事实，升级 HCU 已有环境前仍需核对实际兼容矩阵，不自动安装本页依赖。

当前 TrainingEngine 字段为 `activation_remat`，用 `ActivationRematConfig` / `FullActivationRematConfig` / `DefaultActivationRematConfig` 配置；禁用用 None。逐组 Graph 字段为 `training.accelerator_graph_per_microbatch_group`，旧 `cuda_graph_per_accumulation_group` 已改名。它要求均匀 tensor metadata 和相同梯度参与参数集合，并拒绝 `fsdp_defer_gradient_reduction=True`。`preprocess_microbatch_groups_lazily=True` 则要求关闭 CUDA graphs 且无 SDC replay；它改变输入物化时刻，不改变有效 token 预算。

RL 多机 launcher 现在将预先构造的 actor system 传给 `Controller.setup_async(actor_system=...)`；Monarch 的 host meshes/GPU 分配实现已移到 `actors/monarch/provisioning.py`，`train.py` 不再暴露旧的 provisioning 调用链。默认 actor 仍为 Monarch；替换其框架不是只改一个名字。

当前 `RELEASE.md` 增补 B200 的 RC GPU 验证与 DeepEP remat 梯度检查，明确 RC GPU 工作流使用 Real PG、未覆盖 ROCm/Fake PG，RL也未包含在该GPU工作流。工作流列出项目与测试不等于该固定main提交的所有job已经通过。

## 配置迁移需沿消费者验证

根配置新增 `precision=PrecisionConfig(dtype="float32", param_dtype="bfloat16", reduce_dtype="float32")`；旧 `training.dtype` / `mixed_precision_param` / `mixed_precision_reduce` 不应继续传入。FSDP CPU offload 现在位于 `parallelism.fsdp_enable_cpu_offloading`，仍要求 `debug.distinct_seed_mesh_axes` 包含 `dp_shard`；`max_context_length` 移至模型配置。`model.local_compile.regions` 替代旧 `local_compile_regions` 列表。

Graph 开关为 `training.disable_accelerator_graphs`、`training.accelerator_graph_per_microbatch_group`、`optim.enable_accelerator_graph`。`ConfigLoader` 在 recipe 赋值和 launch options 后再次调用根 `__post_init__`；override 仍有自身后续阶段。保存最终解析结果并核对断言，不能只证明旧字段名称已替换。当前 source/test 修复了 PP capture 的四项 microbatch 与首个 loss kwargs 传递，但本轮没有运行 GPU/PP/HCU 组合。

## 固定证据与使用边界

本页以官方主线 `485c065cb248863bf2e2c65588becd6d7a8bcf83` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [pyproject.toml](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/pyproject.toml)
- [.ci/docker/requirements.txt](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/.ci/docker/requirements.txt)
- [.ci/docker/requirements-rl.txt](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/.ci/docker/requirements-rl.txt)
- [run_train.sh](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/run_train.sh)
- [torchtitan/config/loader.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/loader.py)
- [torchtitan/config/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/README.md)
- [torchtitan_recipes/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan_recipes/README.md)
- [torchtitan_recipes/tests/models/llama3.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan_recipes/tests/models/llama3.py)
- [tests/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/README.md)
- [docs/debugging.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/docs/debugging.md)

- [PR #5277：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5277.md)
- [PR #5280：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5280.md)
- [PR #5288：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5288.md)

## 当前文档命令修正

主线 [PR #5311](https://github.com/pytorch/torchtitan/pull/5311) 修复不可解析的示例命令。FLUX 依赖文件为 `.ci/docker/requirements-flux.txt`；RL 的输出目录用 `--output-dir`，资产路径先核对 Python recipe 的赋值与 train.py 接受的参数。知识库的运行示例也须跟源码参数解析一致，不能因旧 README 有某个 flag 就强行传入。旧版本回放仍使用其自己的配置和接口。

- [torchtitan/models/flux/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/flux/README.md)
- [torchtitan/rl/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/README.md)

## 本次补充的实现与测试依据

- [torchtitan/config/configs.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/configs.py)
- [torchtitan/distributed/activation_remat.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/activation_remat.py)
- [torchtitan/rl/actors/monarch/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/actors/monarch/README.md)

- [torchtitan/config/parallelism.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/parallelism.py)

- [torchtitan/distributed/local_compile.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/local_compile.py)

- [torchtitan/training_engine.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/training_engine.py)

- [tests/unit_tests/cpu/test_trainer.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/unit_tests/cpu/test_trainer.py)
