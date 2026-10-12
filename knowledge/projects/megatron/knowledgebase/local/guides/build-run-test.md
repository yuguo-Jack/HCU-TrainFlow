---
id: official-megatron-wiki/build-run-test
title: Megatron 安装、模型配置、数据、运行与分层测试
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
  path: pyproject.toml
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 22dc36250a9c8b155459a3fd6c38fbbee418659eb5c151d023dbf76640f40025
- source: nvidia-megatron-lm
  path: setup.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 22bb5f7fdf446a831d9261d4cbc8e81503569254941852ec98950792bd22f23c
- source: nvidia-megatron-lm
  path: docs/get-started/install.md
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: b5e97dc226f7ff5c18c7f91d5dd0c5439dd2850bb5276b57eb528a664011317a
- source: nvidia-megatron-lm
  path: docs/get-started/quickstart.md
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 12facd93f82e65b9ca752faeff7496de268832713ea3746dabc00e3c148db9dc
- source: nvidia-megatron-lm
  path: tests/README.md
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: ee9e3ffbb453d7c6ca3c91743b4d412c3068ce97db68cd89347c7fcc6fe128de
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
---

# Megatron 安装、模型配置、数据、运行与分层测试

## 安装入口与版本漂移

官方安装有PyPI `megatron-core`、源码editable和NGC镜像三路；当前pyproject打包`megatron.core`与`megatron.training`，其他examples/顶层训练入口仍以实际checkout为准。optional training/dev/lts依赖和编译扩展要求不同，安装Core包成功不保证完整LM recipe的所有依赖齐全。

本轮发现安装教程仍写Python≥3.10，而固定`pyproject.toml`已要求**Python≥3.12**，最低Torch≥2.6。实际源码安装以package metadata为准，release wheel另查对应tag metadata；不能把当前main的要求写成所有已发布版本要求。`training`与已弃用`mlm`extras、dev/lts路线也需核对当前包。

HCU使用匹配DTK/PyTorch/编译器、RCCL及HCU TE等的实际镜像/配方。官方dev依赖包含NVIDIA平台组件，不在HCU直接整套替换安装；记录源码SHA、wheel、解释器、import/扩展动态库路径、目标ISA与build选项。编译缓存放任务内，确认运行加载的确是构建候选，不能看源码A却运行wheelB。

## 模型配方和数据契约

先选实际HCU支持同模型recipe/用户patch，核对官方或已支持模型分支的config/provider/spec。必须确认hidden/heads/KVheads、attention/MLA/混合层、FFN、MoE专家/top-k/shared专家、MTP、norm/position、tokenizer/vocab、optimizer/精度。模型太大优先评估并行与显存，再只缩layer，不能将其他维度或Muon/Adam随意替换。

官方quickstart有`examples/run_simple_mcore_train_loop.py`与LLaMA3 FP8脚本；后者是NV特定配方，HCU用于核对模型语义。预训练数据通常由`tools/preprocess_data.py`生成`.bin/.idx`；input JSONL、tokenizer type/model、append-eod、document boundaries和实际输出文件必须可追溯。

SFT/packed数据另外核对response mask、position/cu_seqlens、跨文档attention与有效token定义。mock data适合运行/性能初查，不代替真实data/tokenizer或阶段收敛结论；所有输入index/checkpoint原件视为基线，不为测试覆盖。

## 从脚本到最终启动

实际入口可能是HCU包装脚本、Bridge recipe、顶层`pretrain_gpt.py`或Core例子。查当前入口支持的help/配置输出，追source脚本、环境覆盖、argv、cwd、mount、launcher/rank变量；help导入本身可能需要环境，不能认为无副作用。

保存task-local command card包含selected ref、devices/process groups、model/data/precision、microbatch/accumulation、output路径及与HCU recipe差异。官方CLI参数与typed cfg转换要共同验证。`torchrun --nproc_per_node=...`只是launcher形态，SSH+Docker/Slurm/K8s的网络/设备/env按现场确定，不照搬NGC启动参数。

## 测试路线与成功判据

| 层级 | 内容/源码入口 | 必须证明 |
| --- | --- | --- |
| 安装/基础primitive | Python import、设备/扩展、实际后端 | 正确包与候选已加载，无silent fallback |
| 单模块 | 模型/TE/attention/MoE/optimizer unit tests | forward、dgrad/wgrad、mask/layout与dtype正确 |
| 分布式契约 | DDP、schedule、checkpoint相关unit/integration | group/collective顺序、梯度累积、并行/状态一致 |
| 真实模型小跑 | HCU recipe、固定token样本 | optimizer真正更新、data/token计数/loss定义一致 |
| 稳定优化阶段 | 固定checkpoint/seed、局部回归后较长loss窗口 | 数值与性能范围明确，未偷偷改模型/数据语义 |
| 恢复/扩DP | 完整模型、save→reload、扩DP短校准 | model/optimizer/RNG/data/step一致，worst-rank余量与吞吐 |

`tests/README.md`还说明functional golden精度：新值带`value_precision=full`，旧golden走历史处理，deterministic/approximate比较不同。测试失败不能通过随手改golden消除；先确认改动语义、数值路径和适用容差，再按目标仓规范更新基准。

使用`python -m pytest <目标测试>`只表达测试入口，不承诺当前HCU依赖兼容全部NV测试。记录executed/passed/failed/skipped及skip原因；收集成功、0tests、fallback和empty output不作通过。性能比较在profiler-off稳定窗口另测，functional golden不代替同shape性能回归。

## 问题分流、版本和交付

导入/ABI失败查包/扩展/动态库；编译失败查实际compiler/gfx与依赖；初始化卡住查所有rank最早异常和group/bootstrap；模型shape/数值失败追provider→layer spec→backend；运行后OOM和恢复沿[memory](../topics/memory.md)/[checkpoint](../topics/checkpoint.md)定位。保留原配方回退，一次变更多项须明确耦合理由。

实际HCU主仓是最终优先出口，但既有用户patch任务先完成其工作流再按约定rebase/交付，避免中途换base污染数值/性能基线。PR归属训练引擎和实际底层库，按各仓规范附精确配置、测试、dispatch、阶段loss与profiler-off证据。

官方发布/roadmap与特性PR入口见[总览](../overview/overview.md)；更新`pyproject`、模型provider、argument-utils或quickstart时，同时复核本页、目录、数值/状态专题与适配Skill，避免只更新下载页。

## 固定源码与维护边界

- [pyproject.toml](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/pyproject.toml)
- [setup.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/setup.py)
- [docs/get-started/install.md](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/docs/get-started/install.md)
- [docs/get-started/quickstart.md](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/docs/get-started/quickstart.md)
- [tests/README.md](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/tests/README.md)
- [pretrain_gpt.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/pretrain_gpt.py)
- [gpt_builders.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/gpt_builders.py)
- [model_provider.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/model_provider.py)
- [megatron/training/arguments.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/training/arguments.py)

2026-10-12按上述固定源码/官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。
