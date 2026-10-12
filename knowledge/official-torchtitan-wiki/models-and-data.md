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
reviewed_on: '2026-10-12'
coverage: Curated source chains and official evidence at a fixed main commit; not
  all models, backends or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/models/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: c8f50dedb90e280b96a6b0832c5cd76a7ae37daf1e11d18d70cca5407c281da6
- source: pytorch-torchtitan
  path: torchtitan/models/kimi_k3/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 48883ae505cd2bc21c63be5a8a9e3d33dddaa4da108ada1688b0e1d7d407f40c
- source: pytorch-torchtitan
  path: torchtitan/models/kimi_k3/flavors.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: d09991c1bd12a012e9e02f3920c9babd2ca76cc044fdf2e9f98db942e479f4ca
- source: pytorch-torchtitan
  path: torchtitan_recipes/tests/models/kimi_k3.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 198f69c5f92c1352649a27be9d1e6827dca887f328c4ab0e2ff00ee655bef684
- source: pytorch-torchtitan
  path: torchtitan/models/flux/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 63090efd1c71ea0b10f0b4ed318959ab7eaf37336276997f712b9aa662175ca6
- source: pytorch-torchtitan
  path: torchtitan/components/data/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 71a525c8a44f5a637df29cedf0db79c74cc6004fd2326d3dbc37a1d0ea3565e3
- source: pytorch-torchtitan
  path: torchtitan_recipes/tests/models/llama3.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: f2e6289611a2da2009bf947a2dbeae60a98432741e0100b19877e483c3c976d6
- source: pytorch-torchtitan
  path: torchtitan/config/transform/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: d24fa16f2b8cef0aed3a4f601d55ec88f5a22b44572c00c0e411d8933ed5bcef
- source: pytorch-torchtitan
  path: torchtitan/models/deepseek_v4/model.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 702cb94df888a49656687e8e4c3a9f107d07042c70719c891cfbfb48a4ff7792
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

## 固定证据与使用边界

本页以官方主线 `65aaaa960698ab5d6e98c874177b41b9c30e9c58` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/models/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/models/README.md)
- [torchtitan/models/kimi_k3/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/models/kimi_k3/README.md)
- [torchtitan/models/kimi_k3/flavors.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/models/kimi_k3/flavors.py)
- [torchtitan_recipes/tests/models/kimi_k3.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan_recipes/tests/models/kimi_k3.py)
- [torchtitan/models/flux/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/models/flux/README.md)
- [torchtitan/components/data/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/components/data/README.md)
- [torchtitan_recipes/tests/models/llama3.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan_recipes/tests/models/llama3.py)
- [torchtitan/config/transform/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/config/transform/README.md)

- [PR #5280：描述、review、评论及 diff](../prs/pytorch--torchtitan/PR-5280.md)
- [PR #5266：描述、review、评论及 diff](../prs/pytorch--torchtitan/PR-5266.md)

## FLUX 与 RL 的入口变化

FLUX 图像配方依赖专门的 `.ci/docker/requirements-flux.txt`；图片特征管线、资产目录和训练主环境分开核对，不能照搬文本模型的依赖集合。TitanRL 当前使用 `--output-dir` 指定输出位置，启动与资产说明见 [运行测试](build-run-test.md) 和 [TitanRL](titanrl.md)；源码存在配方不代表 HCU 已验证。
## DeepSeek V4 辅助目标的适配检查

当前 decoder 将 `aux_loss_denominator` 和 `padding_mask` 继续传入 attention，并在优化器 hook 注册中加入辅助 loss 的清零逻辑（[PR #4835](https://github.com/pytorch/torchtitan/pull/4835)）。只对齐主 loss 或只移植 attention kernel 会漏掉 indexer 辅助训练路径；应核对有效 token 分母、累积窗口、清零时机以及重算是否重复计数。该模型定义的变化不表示其他模型需要启用相同辅助目标。

固定入口：[DeepSeekV4Model](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/models/deepseek_v4/model.py)。
