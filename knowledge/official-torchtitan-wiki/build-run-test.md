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
reviewed_on: '2026-10-12'
coverage: Curated source chains and official evidence at a fixed main commit; not
  all models, backends or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: pyproject.toml
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 0341afacb518276f192c2c8a836c32426e80856bf8c5f0ff194c3028c221520d
- source: pytorch-torchtitan
  path: .ci/docker/requirements.txt
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 2c5535dbc6350c655d158ed14adeb8ceea69853bea625781fe32f77a2d389e1d
- source: pytorch-torchtitan
  path: .ci/docker/requirements-rl.txt
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 1ab5e0be999db70997ace51b9413fc398e651048f063fdd7ca6c272ef28559d9
- source: pytorch-torchtitan
  path: run_train.sh
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: f88bd97eff8c7a4b8623dae59ed03a94d80bf7fb9b7941e376f7caddd74863ee
- source: pytorch-torchtitan
  path: torchtitan/config/loader.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 8e943af9319c881efa76598de21def00662a024a98093d175ccc5dc2bfef48f2
- source: pytorch-torchtitan
  path: torchtitan/config/README.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: e62e3776a4dd1c2179b3643d9e611f5a6f53fc972ac16de4588ee96a99a06b9b
- source: pytorch-torchtitan
  path: torchtitan_recipes/README.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: a72fb9eab9eb7f376a50622327954f614694ed6aea5bb782aae51035e9c9157a
- source: pytorch-torchtitan
  path: torchtitan_recipes/tests/models/llama3.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: f2e6289611a2da2009bf947a2dbeae60a98432741e0100b19877e483c3c976d6
- source: pytorch-torchtitan
  path: tests/README.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 0872f733f18e85e085802fff3813cd1ee359ec1cc10b8d5929642e62d4c4e712
- source: pytorch-torchtitan
  path: docs/debugging.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 0938badc6722b624d4c07d6e2a620c02fa9cf4bb0e7b26b9d5de77c8b0586b0a
pr_sources:
- pr-pytorch--torchtitan-5277
- pr-pytorch--torchtitan-5280
- pr-pytorch--torchtitan-5288
---

# TorchTitan 安装、Python 配方、启动与分层测试

## 1. 先锁提交和环境

本页是所引用官方提交的使用说明，不是 HCU 已验证安装脚本。官方要求 Python 3.11+，使用较新的 PyTorch nightly 及匹配 TorchAO/扩展；必须核对 `.ci/docker/requirements*.txt` 和实际 recipe。不能在 HCU 环境执行官方 CUDA wheel 安装命令来覆盖现有 Torch。

基础依赖包含 Grain、datasets、tokenizers、renderers、safetensors，以及固定提交的 `spmd_types`、`torch_remat`、`torch_checkpointing`。RL 另外涉及 Monarch、TorchStore、vLLM、环境/奖励依赖；FLUX/VLM/开发测试使用各自 extra。锁下列信息：TorchTitan SHA、Torch/DTK、TorchAO、attention 与通信扩展版本、Python、构建选项、设备型号和可用并行规模。官方 `.ci` 的 wheel/硬件选择只适用于它明确支持的平台。

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

完成导入/配置检查、小规模真实训练、局部正确性和恢复基线后再分析性能。只缩 layer 也应保持架构合法；其他维度变动需任务明确授权并标为流程验证模型。出现配置/ABI/后端错误时，沿 [源码地图](source-map.md) 追查，不把反复重新安装作为默认处理。

## 固定证据与使用边界

本页以官方主线 `65aaaa960698ab5d6e98c874177b41b9c30e9c58` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [pyproject.toml](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/pyproject.toml)
- [.ci/docker/requirements.txt](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/.ci/docker/requirements.txt)
- [.ci/docker/requirements-rl.txt](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/.ci/docker/requirements-rl.txt)
- [run_train.sh](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/run_train.sh)
- [torchtitan/config/loader.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/config/loader.py)
- [torchtitan/config/README.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/config/README.md)
- [torchtitan_recipes/README.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan_recipes/README.md)
- [torchtitan_recipes/tests/models/llama3.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan_recipes/tests/models/llama3.py)
- [tests/README.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/tests/README.md)
- [docs/debugging.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/docs/debugging.md)

- [PR #5277：描述、review、评论及 diff](../prs/pytorch--torchtitan/PR-5277.md)
- [PR #5280：描述、review、评论及 diff](../prs/pytorch--torchtitan/PR-5280.md)
- [PR #5288：描述、review、评论及 diff](../prs/pytorch--torchtitan/PR-5288.md)
