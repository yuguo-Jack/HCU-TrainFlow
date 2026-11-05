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
reviewed_on: '2026-11-04'
coverage: frozen source delta and consumer review; unchanged files rechecked; no HCU runtime validation
sources:
- source: nvidia-megatron-lm
  path: pyproject.toml
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 5eb07103781cbe8ad94d53331dace3c963f0f40c8ff98c1af467217b21086930
- source: nvidia-megatron-lm
  path: setup.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 22bb5f7fdf446a831d9261d4cbc8e81503569254941852ec98950792bd22f23c
- source: nvidia-megatron-lm
  path: docs/get-started/install.md
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: dea288d82bc434fe1fabb77601c676e17c6cacdd7a9cfd64c47eb16ec9ec7920
- source: nvidia-megatron-lm
  path: docs/get-started/quickstart.md
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 12facd93f82e65b9ca752faeff7496de268832713ea3746dabc00e3c148db9dc
- source: nvidia-megatron-lm
  path: tests/README.md
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 5df6b6157e62c4476b0d10f5d555018898eed459aacf5ba9d420c4754e9457a2
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

# Megatron 安装、模型配置、数据、运行与分层测试

## 安装入口与版本漂移

官方安装有PyPI `megatron-core`、源码editable和NGC镜像三路；当前pyproject打包`megatron.core`与`megatron.training`，其他examples/顶层训练入口仍以实际checkout为准。optional training/dev/lts依赖和编译扩展要求不同，安装Core包成功不保证完整LM recipe的所有依赖齐全。

当前安装教程已修正为与固定 `pyproject.toml` 一致的 **Python≥3.12**，最低 Torch≥2.6；旧教程 Python≥3.10 的漂移不再是当前事实。NGC dev/LTS 配对改由 `.ngc_version.dev`/`.ngc_version.lts` 指定，不能按“上个月”猜镜像。当前 dev 依赖还包含 FlashInfer≥0.7.2,<0.8 与 cuDNN Frontend[cutedsl] 1.32 等 NVIDIA 组件；release wheel 另查对应 tag metadata，`training` 与已弃用 `mlm` extras 分开核对，不把 main 要求推广到所有版本。

HCU使用匹配DTK/PyTorch/编译器、RCCL及HCU TE等的实际镜像/配方。官方dev依赖包含NVIDIA平台组件，不在HCU直接整套替换安装；记录源码SHA、wheel、解释器、import/扩展动态库路径、目标ISA与build选项。编译缓存放任务内，确认运行加载的确是构建候选，不能看源码A却运行wheelB。

## 模型配方和数据契约

先选实际HCU支持同模型recipe/用户patch，核对官方或已支持模型分支的config/provider/spec。必须确认hidden/heads/KVheads、attention/MLA/混合层、FFN、MoE专家/top-k/shared专家、MTP、norm/position、tokenizer/vocab、optimizer/精度。模型太大优先评估并行与显存，再只缩layer，不能将其他维度或Muon/Adam随意替换。

官方quickstart有`examples/run_simple_mcore_train_loop.py`与LLaMA3 FP8脚本；后者是NV特定配方，HCU用于核对模型语义。预训练数据通常由`tools/preprocess_data.py`生成`.bin/.idx`；input JSONL、tokenizer type/model、append-eod、document boundaries和实际输出文件必须可追溯。

SFT/packed数据另外核对response mask、position/cu_seqlens、跨文档attention与有效token定义。mock data适合运行/性能初查，不代替真实data/tokenizer或阶段收敛结论；所有输入index/checkpoint原件视为基线，不为测试覆盖。

## 从脚本到最终启动

实际入口可能是HCU包装脚本、Bridge recipe、顶层`pretrain_gpt.py`或Core例子。查当前入口支持的help/配置输出，追source脚本、环境覆盖、argv、cwd、mount、launcher/rank变量；help导入本身可能需要环境，不能认为无副作用。

保存task-local command card包含selected ref、devices/process groups、model/data/precision、microbatch/accumulation、output路径及与HCU recipe差异。官方CLI参数与typed cfg转换要共同验证。`torchrun --nproc_per_node=...`只是launcher形态，SSH+Docker/Slurm/K8s的网络/设备/env按现场确定，不照搬NGC启动参数。

## 配置定稿与探测范围

当前 `ConfigContainerBase.validate()` 只校验，运行初始化调用幂等的 `finalize()` 才定稿布局、RNG 和 RL/DDP 派生值；不要依赖反复 validate 的副作用。定稿后改变布局或随机策略须建立新容器，不能修改原对象后继续复用。`initialize_megatron` 还可由调用方指定 `build_tokenizer=False`，这表示外部负责分词，不代表数据契约可省略。

`fake_process_group` 跳过真实分布式通信，可用于单卡容量探测；它不能验收 collective、分布式正确性或端到端吞吐。TP user-buffer 初始化使用实际 batch 的 sequence length 与 microbatch，VLM 还需 decoder 的文本加图像长度；模型位置容量不能替代实际输入长度。

`cfg.data` 先构建不带 tokenizer 的 GPT/FIM 配置；validate 检查无需 tokenizer 的字段与数据集类型，finalize 填充其他 section 所拥有的并行/验证字段，runtime 绑定同一 tokenizer 后才完成数据校验。provider 将该对象原样交 builder，packed/scheduler 输入在 TP0 的每个 PP stage 建数据，其余按首尾/MTP rank 规则。`DataloaderConfig.pin_memory`、`persistent_workers`、`drop_last` 当前明写只声明、训练循环仍用内建值，不能仅靠 YAML 设置声称已改变 loader。

新版 `tests/README.md` 对复用多 topology 的 A2A 测试要求显式销毁新建 communicator：`destroy_model_parallel` 清引用不等于从 Torch registry 注销 group，须先结束 NCCL EP/释放 flex 缓冲再销毁其借用 group，并保留默认/先前 group。这是测试隔离指导，本轮未运行对应分布式测试。quickstart 与 setup.py 原件未变，因此保留其安装/单模块入口和已有 golden 精度边界。

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

- [pyproject.toml](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/pyproject.toml)
- [setup.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/setup.py)
- [docs/get-started/install.md](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/docs/get-started/install.md)
- [docs/get-started/quickstart.md](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/docs/get-started/quickstart.md)
- [tests/README.md](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/tests/README.md)
- [pretrain_gpt.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/pretrain_gpt.py)
- [gpt_builders.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/gpt_builders.py)
- [model_provider.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/model_provider.py)
- [megatron/training/arguments.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/training/arguments.py)

2026-11-04按上述固定源码、实际消费者与官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。