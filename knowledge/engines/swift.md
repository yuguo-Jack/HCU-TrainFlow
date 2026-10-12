---
id: engines/swift
title: ms-swift：训练入口、数据契约、Megatron 与 GRPO 工程指南
engine: swift
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime
  execution
sources:
- source: modelscope-ms-swift
  path: README.md
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 4cf3ac10fe15d52a4bbf6886e1d158e10b202f04980a0be3e4050a33ba9fc942
- source: modelscope-ms-swift
  path: setup.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 1a7fe144134dff38afa385c749c201d88827cea7692ba4007e58f9ccfd379275
- source: modelscope-ms-swift
  path: docs/source_en/GetStarted/SWIFT-installation.md
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 2f80ce9327d85ebe959a9883bdd435027082e3eb4abb1b76883675da7bbd7fed
- source: modelscope-ms-swift
  path: swift/cli/main.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: fcc9f982a76102f792139c65de3b211b4af2c633801e7f0807996ac77dfcba88
- source: modelscope-ms-swift
  path: swift/cli/_megatron/main.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: e1a89aee02857b246054b9ae232804b99670fa54545c2d9f22e78153bbc0d55f
- source: modelscope-ms-swift
  path: swift/pipelines/train/sft.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 744ceb388ae51f3f50f95f9ceb208980696ba95eaa1f01aaabb0584bd78515b6
- source: modelscope-ms-swift
  path: swift/template/base.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 212b92b190bed8c2c987864ffa93a1cd3a9e45ffa6ba19736e42b7bd88d9c4e4
- source: modelscope-ms-swift
  path: swift/trainers/seq2seq_trainer.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 4bb65c60321cd619dd44a530e1b228ce470c625a9134666758c21d1337f79163
- source: modelscope-ms-swift
  path: swift/megatron/arguments/megatron_args.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: ee5b040132967d6520efea1ed2eeed92fb45fc1b552a734652d1935e5a979230
- source: modelscope-ms-swift
  path: swift/megatron/trainers/base.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: a5e44bee709f375c7768f1eb864ec1cef04b06c7cb4f3dd9252b19be2427ccbd
- source: modelscope-ms-swift
  path: swift/megatron/trainers/trainer.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: b7efa15ead7a4f049495c4a0639c27edf6b99bddf9795c47c178a555cbcbf6dc
- source: modelscope-ms-swift
  path: swift/megatron/trainers/grpo_trainer.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 34ec4b21ec0e33b2920d1b3712e86abccf594f08cce055417ec723ea7b38378b
- source: modelscope-ms-swift
  path: swift/megatron/trainers/rollout_mixin.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: c77710d5f900e455a8873f2a5495bdf57d7bd6628a6c2a54bed61b798272886d
- source: modelscope-ms-swift
  path: tests/train/test_packing.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 74ed18c014402f0ce0f2a22f947bf7e406184111a85cea9852765e06942f5c11
- source: modelscope-ms-swift
  path: tests/train/test_chunked_cross_entropy.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: dfca2f2e3787ecbdaa555129d59dc2cb03e70c0f704432fa34f4af86fd8288a5
- source: modelscope-ms-swift
  path: tests/train/test_trainer_partial_accumulation.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: dfeaa1943e3d70e1ffe458b547b11ce8d92d1fab2a08e033cde47f825ceccbe4
- source: modelscope-ms-swift
  path: tests/train/test_vllm_weight_sync.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: c2ea7e3e682623d839fc5eb31fee97c659ee984811a5dfaa6777be97c7afd3d2
---

# ms-swift：训练入口、数据契约、Megatron 与 GRPO 工程指南

## 定位与阅读路线

ms-swift 连接模型/模板/数据注册、微调方法和多个训练/推理后端。普通 `swift sft` 基于 Transformers trainer，`megatron sft` 基于 Megatron Core，`swift rlhf`/`megatron rlhf` 又引入策略算法和 rollout 引擎。定位性能或精度问题时先写清入口、训练 backend、tuner、attention 实现和生成 backend；“使用 Swift”不足以确定执行链。

本页阅读官方 main 固定提交 `409170095f24b45b8945715341504d99b70a2bc0`。官方安装文档明确 main 对应 4.x、3.x 使用 `release/3.12`；不能把新 trainer 行为套到旧 HCU patch 分支。已有 HCU 配方和实际依赖优先，官方源用于确认机制和模型语义。

深入专题：

- [SFT packing、序列并行与 loss 归一化](swift/topics/sft-packing-and-loss.md)：数据流、样本边界、分母与 chunked CE。
- [Megatron GRPO 的权重切换与显存生命周期](swift/topics/megatron-grpo-weight-lifecycle.md)：首次/后续同步、LoRA、sleep/offload、缓存和异常恢复。

## 工程目录与问题入口

| 目录/文件 | 职责 | 从什么问题进入 |
| --- | --- | --- |
| `swift/cli/main.py`、`cli/_megatron/main.py` | 命令到模块分派，YAML/JSON 转参数，torchrun | 启动到错误 backend、环境变量未生效、rank 不符 |
| `swift/arguments/`、`megatron/arguments/` | 普通与 Core 参数、默认值和组合验证 | batch/并行约束、recompute、模型配置差异 |
| `swift/model/`、`swift/template/` | 模型/processor 注册、对话模板、token/mask | 新模型、VLM 输入、loss 异常、padding/packing |
| `swift/dataset/`、`pipelines/train/sft.py` | 载入、缓存、编码、streaming/packing | CPU 等待、样本重复、数据预处理峰值 |
| `swift/trainers/` | HF trainer 扩展、loss、dataloader、checkpoint | 普通 SFT 的 loss/accumulation、生成评估 |
| `swift/megatron/trainers/base.py`、`trainer.py` | Core 生命周期、forward/loss、日志 | TP/PP/CP/EP、梯度归约、Core schedule 对齐 |
| `grpo_trainer.py`、`rollout_mixin.py` | on-policy 批次、reward/logprob、推理同步 | rollout 等待、策略版本错位、共卡 OOM |
| `examples/train/`、`examples/megatron/`、`tests/` | 模型 recipe、参数示例、契约与集成测试 | 找可复用启动脚本和针对当前机制的回归 |

从 [完整源码目录](../source-maps/modelscope-ms-swift.md) 查更细路径；目录覆盖代表可定位，不表示所有模型实现已精读。

## 安装与依赖确认

[官方安装说明](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/docs/source_en/GetStarted/SWIFT-installation.md)提供 `python -m pip install -e .` 和 `.[megatron]` 等 extras。HCU 任务在自身工作 checkout/镜像使用兼容依赖，安装后记录 `ms-swift`、PyTorch、Transformers、PEFT、Core/TE、attention 与 rollout 引擎的实际版本和导入路径；不能因 optional extra 安装成功就认定设备扩展可执行。

`setup.py` 注册 `swift` 与 Megatron CLI；普通入口解析配置中的 `ENV`，已有进程环境优先于配置同名值，并打印最终命令。`NPROC_PER_NODE` 或 `NNODES` 出现会启用 torchrun，继续读取 `MASTER_ADDR`、`MASTER_PORT`、`NODE_RANK`。因此环境核对要保存实际展开命令和有效环境，不能仅阅读 YAML 中写了什么。

Core 和 vLLM/SGLang 的模型覆盖及 API 版本分别验证；同一容器里多个扩展来源时确认实际加载产物。官方 CUDA 镜像和安装片段提供上游依赖参考，HCU 启动仍选择目标 HCU 工程已支持的脚本。

## 运行、模型与数据契约

先从官方 [Quick start](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/docs/source_en/GetStarted/Quick-start.md)、`examples/train/` 或 Megatron 模型 recipe 找对应架构、训练目标和 tuner。记录模型 revision、tokenizer/processor、模板、冻结/trainable 参数、优化器、精度、长度限制和数据切分；SFT、预训练、GRPO 的数据与目标不能混用。容量不足优先保留架构参数、只缩 layer，改变其他参数需要独立说明和验证。

普通 SFT 链：`cli_main → SwiftSft.__init__ → _prepare_model_tokenizer/_prepare_template → _prepare_dataset → prepare_model → TrainerFactory → trainer.train`。模板进入 train mode，`_prepare_template` 检查是否支持 packing/padding-free。GRPO/GKD 延后编码；cached dataset 不能和 streaming 组合；预训练的 `truncation_strategy=split` 另有任务类型和 lazy-tokenize 约束。

Megatron 链：Megatron CLI → 参数校验/模型桥接 → `BaseMegatronTrainer` 的 model、optimizer、scheduler 与 schedule → `MegatronTrainer.forward_step → model → loss_func`。并行字段含 TP/PP/CP/EP、sequence parallel、overlap 及 recompute，但实际支持受模型、Core/TE 和 HCU 分支约束。需要同时保留 `micro_batch_size`、`global_batch_size`、DP 域和梯度累积，而不是只记录卡数。

SFT label 中 `-100` 表示不计训练目标；prompt、历史轮次和多模态占位的权重由模板/loss-scale 规则生成。packing 重置 position IDs、合并样本时仍需使 backend 尊重分段，详见 [数据专题](swift/topics/sft-packing-and-loss.md)。吞吐分别报告实际处理 token 和有效训练 token。

## 性能与内存：该优化什么

| 机制 | 收益来源 | 需要付出的代价/核验 |
| --- | --- | --- |
| packing、padding-free、SP | 减少 padding；分摊长序列激活 | attention 分段、loss mask/分母、跨卡通信；多模态支持单独查 |
| logits/CE 内存优化 | 少物化无用 logits 或分块计算 CE | 模型输出契约、aux loss、反向及 retained graph；chunked CE 不等于消除完整 logits |
| Core 并行、recompute、overlap | 调节单卡驻留/流水线空泡/通信等待 | recompute 增算、通信与显存 buffer；不能改归约语义换吞吐 |
| RL 共卡 sleep/offload | 给 rollout KV/训练激活分时使用显存 | 权重更新、缓存失效、D2H/H2D 和切换峰值，按整轮墙钟判断 |
| 日志 reduce 延后 | 减少每 microbatch 的全局同步 | 所有相应 rank 仍参与 collective；日志窗口与训练梯度分开解释 |

当前 `MegatronTrainer.loss_func` 返回本地 loss sum、有效 token 数及日志 stats；普通 logging loss 的 DP/CP reduce 延后到 `_log_callback`。但 `enable_channel_loss` 的路径仍同步频道键和值，不能把这一结论扩大成“所有日志都没有 microbatch 通信”。

用 profile 判断数据/CPU、Core schedule、计算、通信或 rollout 哪个占主要墙钟；固定 shape 单测、算子上限和融合分析由 TrainFlow 优化阶段承接。显存账本同时包含训练权重/master/optimizer、激活、生成权重/KV、LoRA merge 副本、bridge 导出与通信 buffer，测量切换最高峰值。

## 数值、故障与恢复

| 现象 | 先检查 | 再追源码/对照 |
| --- | --- | --- |
| packing/SP 后 loss 变化 | 输入 token、label shift、样本边界、有效 token 分母 | Template → Seq2SeqTrainer/GatherLoss → backend；固定 batch 对比梯度 |
| 共卡 rollout OOM | weights/KV 的唤醒时刻、训练 offload、导出副本 | `_generate_completions`/`offload_context`，非 offload 小规模对照 |
| GRPO reward/KL 异常 | group、response mask、old/ref/rollout logprob、policy version | GRPO trainer、reward/advantage 与实际推理实现 |
| logging 卡住 | 所有 last-stage DP/CP rank 是否参加同一 reduce | `_log_callback`，全掩码 shard 也须贡献零值 |
| 恢复/保存异常 | checkpoint 完整性、模型/optimizer/data/RNG、并行布局 | 普通 trainer 或 Core 分片链；Flash Checkpoint/Universal 的实际依赖 |

`SwiftSft.train` 的 finally 保存 trainer state；这份日志并不等同已完成持久 checkpoint。Flash Checkpoint 有等待最新完整写入的调用；开启 elastic callback 会检查 Universal checkpoint，否则可能从头开始，不能把“进程重新启动”当成数据进度已恢复。

## 分层验证与官方测试

首次接入：导入与实际扩展 → 模板/编码样本 → 一次 forward/backward/step → 保存恢复 → 相同 policy version 的训练/生成闭环。后续优化使用局部契约回归和阶段 loss。以下是当前官方测试入口，本页没有在 HCU 执行它们：

- [test_packing.py](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/tests/train/test_packing.py)：packing 示例与训练参数组合，实际依赖目标模型环境。
- [test_chunked_cross_entropy.py](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/tests/train/test_chunked_cross_entropy.py)：CE/梯度、共享 logits、重复反向；CPU 数学契约不代表设备实现性能。
- [test_trainer_partial_accumulation.py](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/tests/train/test_trainer_partial_accumulation.py)：实际不足设定梯度累积的窗口与合并 batch 对照。
- [test_vllm_weight_sync.py](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/tests/train/test_vllm_weight_sync.py)：权重同步相关条件；模型、backend 和部署组合另做端到端验收。

## 教程、PR、发布与持续更新

常用官方入口：[文档](https://swift.readthedocs.io/en/latest/)、[Releases](https://github.com/modelscope/ms-swift/releases)、[Issues/功能规划](https://github.com/modelscope/ms-swift/issues)、[PR](https://github.com/modelscope/ms-swift/pulls)。规划、PR 合入、4.x 发布和 HCU 可用分别核对；本页不宣称某 issue 是永久 roadmap。

已收录 PR：[loss weight 说明 #10188](../prs/modelscope--ms-swift/PR-10188.md)、[Core checkpoint metadata 修复 #10242](../prs/modelscope--ms-swift/PR-10242.md)。解释“为什么改”继续读 review、最终代码和测试；仅阅读描述不能保证对当前源码的判断。

检索用 `wiki-search "packing loss denominator" --engine swift`，不足时 `wiki-search-pr "loss weight" --engine swift`，再追完整固定源码。运行 `wiki-update PROJECT modelscope-ms-swift` 时联动本页、两个专题、CLI、trainer、rollout 和实际依赖；新增模型/模板、chunk-loss、Core/TE/vLLM API 变化都可能改变结论。共享资料只保留官方机制、通用经验和最终里程碑，逐轮任务数据保留工作区。
