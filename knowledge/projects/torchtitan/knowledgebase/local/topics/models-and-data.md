---
id: official-torchtitan-wiki/models-and-data
title: TorchTitan 模型配方、数据语义与 Kimi/FLUX 适配边界
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
  path: torchtitan/models/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 6758bb16baee18d8e992697932dbc055c6e63f290c2a8c246bb0578b5f25a514
- source: pytorch-torchtitan
  path: torchtitan/models/kimi_k3/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 48883ae505cd2bc21c63be5a8a9e3d33dddaa4da108ada1688b0e1d7d407f40c
- source: pytorch-torchtitan
  path: torchtitan/models/kimi_k3/flavors.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 1d7238bde8c8868ab66a26cff532adab4600056103167ea9c9ca2362c61e7a77
- source: pytorch-torchtitan
  path: torchtitan_recipes/tests/models/kimi_k3.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 10e8b85a47a3beabce5c9bf7cc7b6dc496712790140647ed3c2b084f881ccf56
- source: pytorch-torchtitan
  path: torchtitan/models/flux/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 945d9a8a89c7726d786a526c20e141814300a33f6fed8736d697fcf69853c8a4
- source: pytorch-torchtitan
  path: torchtitan/components/data/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 71a525c8a44f5a637df29cedf0db79c74cc6004fd2326d3dbc37a1d0ea3565e3
- source: pytorch-torchtitan
  path: torchtitan_recipes/tests/models/llama3.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: a248bb7d8e9b72b304281491fd594e8f7ad2f0a53dac03672f9e36e8057853f9
- source: pytorch-torchtitan
  path: torchtitan/config/transform/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 605a14077539325cb66eb17f52939bd35ed2d97e78f80fa547d6aec1cb53b78a
- source: pytorch-torchtitan
  path: torchtitan/models/deepseek_v4/model.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 251e9d7578110b0efdf1d7f276869cf3bc22667c72e824da6187f79faf51f333
- source: pytorch-torchtitan
  path: torchtitan_recipes/rl/model_configs.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: d62f1526bb38cb195554426f9f19d7f688f7f0c84c52ec8e905159709e1499e8
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_model_defaults.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 44bf357ff2ddfa185feca23384b2152168c25c0727dcc253f14616e36c6e2427
- source: pytorch-torchtitan
  path: torchtitan/models/kimi_k3/model.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 2b08c9a6e05dcc63fd14a5525300f7c63274ee4b08bcee86bd5377d0fa6ecb73
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/vllm/model_wrapper.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: dfd3054a05f24eefa3e7bfaa5ffc24433700ede8579e53d8371277ae9a0f56e8
- source: pytorch-torchtitan
  path: torchtitan/training_engine.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 2ffe06874d3a03ccc91d407f1bc91d5f2beaa9c746738dd3a3646f1c800a798f

pr_sources:
- pr-pytorch--torchtitan-5280
- pr-pytorch--torchtitan-5266
---
# TorchTitan 模型配方、数据语义与 Kimi/FLUX 适配边界

## 配方不只是模型名字

模型族目录包含结构与 flavor，recipe 决定本次训练使用的 flavor、优化器、数据、loss、并行与替换实现。主线可查 Llama、Qwen、DeepSeek、Kimi、GPT-OSS、Muse、FLUX 等入口，但每个模型的预训练/SFT/RL、TP/CP/EP/PP 和量化支持不同。支持表、具体 recipe、配置断言与真实测试必须一致。

适配时逐项记录：层数与层类型序列、hidden/head/latent 维度、词表和 tokenizer、RoPE/位置编码、attention mask、MoE 专家数/top-k/路由、norm 与激活、精度、初始化/权重转换、优化器参数分组、数据与训练目标。优先从已支持该模型的官方分支、PR、配方获得证据；容量不足时先调整合法层数，不静默改架构或优化器。

## Kimi K3：特别容易被简化错的部分

该提交的官方说明包含混合 KDA/Gated MLA、LatentMoE、Attention Residual 和多模态路径。模型卡中发布权重/推理格式的描述，不能直接用来断言当前训练 recipe 已实现同样量化流程。debug recipe 是测试结构，不是完整模型训练验收。

`torchtitan_recipes/tests/models/kimi_k3.py::_dist_muon_optimizer` 将合适矩阵交给 DistMuon，其他参数由 AdamW 处理；包括 embedding、norm、bias、LM head、部分标量/卷积与视觉塔。它不是“全模型统一 Muon”或“全模型 AdamW”。per-head/分块矩阵与专家权重有专门的 compute sharding，必须核对分组和布局。

当前 `_KimiK3TrainerConfig.__post_init__` 对使用 DistMuon 且 `tensor_parallel_degree > 1` 主动报错，因为 TP 可产生未支持的 `_StridedShard`。这代表优化器布局约束，不是加一个环境变量即可解决。若为容量或性能需要 TP，应寻找当前官方支持路径或处理布局；换成 AdamW 会改变训练语义，不能当作原配方的无损修复。

KDA、MLA 和 Attention Residual 的后端分别核查；有关 H100/Blackwell 的依赖要求不能自动套给 HCU。数值转换脚本的 debug 结果只能覆盖它实际比较的模型和张量。

## FLUX 与 Torch 原生生成训练

FLUX 的 flow-matching loss、图文条件和数据流与自回归 next-token loss 不同。应从 `models/flux`、对应 Trainer/recipe 和 FLUX extra 入手，不能用语言模型 tokens/s 或交叉熵等价标准替代。官方页面存在历史路径或省略 NGPU 的示例，安装以当前 `.ci/docker/requirements-flux.txt`/package extra 为准，启动以 `run_train.sh` 的真实默认和所选配方为准。

该路径值得借鉴原生 Torch 的局部编译、显存生命周期、数据吞吐和 CP 方法；TP/PP 等支持以该模型当前实现为准。混合精度、conditioning、sampling/validation 的变化要看生成任务质量指标。

## Grain 数据流水线与 SFT

典型链路是 Source → 单数据集处理/过滤 → 混合、拼接或 packing → GrainDataLoader 的 batch/collate/prefetch → TrainingMicrobatch。原始样本数、packing 后序列数、padding 后 token 数和实际参与 loss 的 token 数不是同一个量。

- 预训练的 concat/split 与 SFT 的会话渲染、assistant mask、first-fit packing 分开核对；修改模板/tokenizer 会改变监督目标。
- 记录数据集 revision、处理器、随机种子、shuffle、worker、packing 和有效 token 分布；吞吐对比必须使用同一个训练目标。
- 检查 loader 状态是否进入 checkpoint；恢复后的样本顺序和游标是恢复验收的一部分。
- 下载数据/tokenizer 到可复用位置，避免所有 rank 同时联网下载导致限流或启动失衡。迁移时共享存储路径由站点配置给出，不能写死某任务路径。

## 配置转换的联动

LoRA、量化、异步 TP、dispatcher 和 CP transform 可能改模块类型、权重布局和接口。保持明确应用顺序，查看转换前后有效配置；一个 transform 覆盖掉另一个 transform 的特性时要明确失效或报错，不能只统计命令行开关。定位源码后联合 [数值](training-and-numerics.md)、[并行](parallelism-and-memory.md) 和 [低精度](moe-and-low-precision.md) 专题判断。

## 当前模型树与配方默认变化

Kimi K3当前统一为 `layer.attention`（KDA或KimiMLA）和 `layer.feed_forward`（DenseFeedForward或LatentMoE），MLA实现从model.py移至attention.py。attention metadata按真实inner-attention类型选择，vLLM替换时要保留首个full-attention选择、YaRN/softmax scale与分片。旧 `delta_attention`/`moe` FQN需要同步更新DistMuon sharding/regex、override、remat和权重adapter；不能只改某一个属性名。

本固定提交Kimi构造器/测试recipe默认attention backend改为varlen，DistMuon的owned/block/per-expert compute layout显式使用BF16。TP布局的既有限制仍应由当前recipe断言验证；不能为了避开varlen依赖或布局约束悄悄换attention/optimizer而继续称作原配方。原Attention Residual局部算子案例的算法与历史实验范围保留，当前调用者变化另行核对。

README还新增Muse-Spark-Open模型与已验证text recipe的导航，但源码中的多模态结构不等于各模态/阶段都有同样验证。RL默认的FP32 LM head、冻结router和aux loss移除见[TitanRL](titanrl.md)，不能套用到同名模型的监督预训练。

## 当前输入与 MLA 消费者

`preprocess_inputs` 现在直接返回 inputs、labels、model kwargs、loss kwargs 四项，per-token loss kwargs 与 labels 一起做 CP 切分；引擎不再在模型预处理后另行附加未切分数据。`max_context_length` 从 training 移入 model，不能只改引擎字段。RL 移除旧的统一 CP>1 拒绝后，也仍要验证具体模型/attention/分片组合，不能以删除断言宣布全模型 CP 可用。

Kimi flavor 的 `wkv_b` 与 packed KV 维度现在进入 `MLAAttention.Config`，拥有独立 sharding；vLLM wrapper 区分 compressed MLA cache 与 materialized K/V，后者配 Flex 仍拒绝并要求 varlen。旧候选 PR 的禁用条件不应一概当作当前 main；实际 recipe、backend、checkpoint adapter 和 parity 测试分别核对。

## 固定证据与使用边界

本页以官方主线 `485c065cb248863bf2e2c65588becd6d7a8bcf83` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/models/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/README.md)
- [torchtitan/models/kimi_k3/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/kimi_k3/README.md)
- [torchtitan/models/kimi_k3/flavors.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/kimi_k3/flavors.py)
- [torchtitan_recipes/tests/models/kimi_k3.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan_recipes/tests/models/kimi_k3.py)
- [torchtitan/models/flux/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/flux/README.md)
- [torchtitan/components/data/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/components/data/README.md)
- [torchtitan_recipes/tests/models/llama3.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan_recipes/tests/models/llama3.py)
- [torchtitan/config/transform/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/transform/README.md)

- [PR #5280：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5280.md)
- [PR #5266：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5266.md)

## FLUX 与 RL 的入口变化

FLUX 图像配方依赖专门的 `.ci/docker/requirements-flux.txt`；图片特征管线、资产目录和训练主环境分开核对，不能照搬文本模型的依赖集合。TitanRL 当前使用 `--output-dir` 指定输出位置，启动与资产说明见 [运行测试](../guides/build-run-test.md) 和 [TitanRL](titanrl.md)；源码存在配方不代表 HCU 已验证。
## DeepSeek V4 辅助目标的适配检查

当前 decoder 将 `aux_loss_denominator` 和 `padding_mask` 继续传入 attention，并在优化器 hook 注册中加入辅助 loss 的清零逻辑（[PR #4835](https://github.com/pytorch/torchtitan/pull/4835)）。只对齐主 loss 或只移植 attention kernel 会漏掉 indexer 辅助训练路径；应核对有效 token 分母、累积窗口、清零时机以及重算是否重复计数。该模型定义的变化不表示其他模型需要启用相同辅助目标。

固定入口：[DeepSeekV4Model](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/deepseek_v4/model.py)。

## 本次补充的实现与测试依据

- [torchtitan_recipes/rl/model_configs.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan_recipes/rl/model_configs.py)
- [tests/rl/unit_tests/cpu/test_model_defaults.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/rl/unit_tests/cpu/test_model_defaults.py)

- [torchtitan/models/kimi_k3/model.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/kimi_k3/model.py)

- [torchtitan/rl/generator/vllm/model_wrapper.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/generator/vllm/model_wrapper.py)

- [torchtitan/training_engine.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/training_engine.py)
