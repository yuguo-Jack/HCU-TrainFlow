---
id: ecosystem/loongforge
title: LoongForge：两类训练入口、DP 均衡、EP 重叠与状态恢复
engine: loongforge
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
- source: baidu-baige-loongforge
  path: README.md
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: df67a100050c88b9b94082117cc5e918943639d9d51b1b7f971ae7a891bf584d
- source: baidu-baige-loongforge
  path: .gitmodules
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: b5aca9eaf884dfde53b152fc6000eff8a8c793339b659411f6e79292bf68b2ed
- source: baidu-baige-loongforge
  path: pyproject.toml
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: 37821ef7d7811a2d7866c06021e1ea21aece90985b36a0aa81ebca6aa7527089
- source: baidu-baige-loongforge
  path: setup_env.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: 74cf1a02f71d6e348be5e384c034905e9ca8461ea710d21ecabd0b2e1d15fd48
- source: baidu-baige-loongforge
  path: loongforge/train.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: cef9bf0d396232e0f5ed4ba019fabaa3e7f0dc70c1fba35e564660c190e07248
- source: baidu-baige-loongforge
  path: loongforge/train/parser.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: a0d64417a7b1fb4b2d492e3cfd779e0084ce44d8c95e8c571c7c95c0b2b1e432
- source: baidu-baige-loongforge
  path: loongforge/train/trainer_builder.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: 0d53b62a230bb244134a0fa72da29213ef8cbec1a983aea9042abd71d4708470
- source: baidu-baige-loongforge
  path: loongforge/embodied/README.md
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: 62f972c7f4fc6d641ef01335338493de8c57ec36800b42dfd60d6c4302f17639
- source: baidu-baige-loongforge
  path: tests/llm_vlm/README.md
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: 4a8afe672ea617f1bd30c91babafeac9522bcf880e55856c1473e3e0a92f0281
- source: baidu-loong-megatron
  path: megatron/core/transformer/transformer_config.py
  commit: 9d2d6b30f4099ed0e29300f76e19f55b72387ffc
  sha256: 1ddc625ba2d9304b535c88279d2db9a47796eaeb3617bad9a6e6674386a69d74
- source: baidu-loong-megatron
  path: megatron/training/arguments.py
  commit: 9d2d6b30f4099ed0e29300f76e19f55b72387ffc
  sha256: 8d3fbb2dc5c7a9b27983095682c54a37976b41b4a1c0f323df2b185df4c9a65c
- source: baidu-baige-loongforge
  path: loongforge/embodied/distributed/context.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: bf5eab8380de75047e01a03bc0732a8e115abe862d5e4fcdf515881b3243d83b
- source: baidu-baige-loongforge
  path: loongforge/embodied/train/utils/logging.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: dd5c527f623d33ce2bf5fdb94310f8e7b28aee6fee4d34afffd346ce4650ca39
- source: baidu-baige-loongforge
  path: loongforge/embodied/optimizer/tensor_wise_optimizer/tensor_wise_optimizer.py
  commit: 042a68102395b9f4024d1a61084592c4c618371a
  sha256: 2b9ff23e99cd892377b60a30e739b6d863e8e0d8ea2b7c8f10531401bbba3cdf
retrieved_on: '2026-11-04'
---

# LoongForge：两类训练入口、DP 均衡、EP 重叠与状态恢复

## 1. 定位与两条训练栈

LoongForge 同仓维护两类训练栈：Megatron-based 的 LLM/VLM/diffusion 栈，以及 **Torch-native 的 VLA/WAM embodied 栈**。前者入口 `loongforge/train.py`，后者 `loongforge/embodied/train.py`；源码明确它们不共用全部 parser/args/core。用前者的TP/PP/EP经验指导后者前，先判断模型和并行组织，不能只看“都是训练”就套同一配方。

它可提供激进调度、变长/多模态负载均衡、数据IO、显存与模型适配参考。HCU 实际出口仍为选定 HCU 训练工程和底层库；CUDA/DeepEP/TE扩展依赖及NV启动变量不代表HCU已有实现。

## 2. 目录和问题导航

| 路径 | 职责/问题入口 |
| --- | --- |
| `loongforge/train.py`、`train/{parser,trainer_builder}.py` | 配置→训练器→train，仅Megatron栈 |
| `loongforge/models/`、`configs/`、`examples/`、`examples_xpu/` | 模型provider、结构/recipe及按硬件区分的预训练/SFT/VLM/diffusion启动 |
| `loongforge/data/dp_balance/` | 预取/统计/代价拟合/样本重排；变长/视觉DP负载不均 |
| `loongforge/train/full_hetero_cpu_offload.py` | 另一类offload/异构训练入口，不与EP激活卸载混称 |
| `ops/`、`third_party/patches/` | 平台扩展与 TE 补丁，查实际导入、补丁目标和build；不继续使用旧根目录 patches 路径 |
| `third_party/Loong-Megatron` | Megatron的schedule、dispatcher与激活机制真正实现 |
| `loongforge/embodied/{data,model,train,distributed,optimizer}/` | 独立Torch训练、数据变换、DDP/FSDP/HSDP、checkpoint与optimizer |
| `tests/llm_vlm/`、`tests/embodied/` | 两栈分层测试；选定模型集不能代表全部模型 |
| `docs/source/features/`、`embodied_tutorial/` | 特性与模型教程，继续追源码/依赖 |

## 3. 构建安装与实际子提交

2026-11-04 检索父仓 `042a68102395b9f4024d1a61084592c4c618371a`，`.gitmodules` 仍指向 `baidu-baige/Loong-Megatron`，tracking branch 为 `loong-main/core_v0.15.0`；父树 gitlink 已从上轮 `cfcdede99642303b1dff0464b77a7df50ef6e4ea` 推进到 `9d2d6b30f4099ed0e29300f76e19f55b72387ffc`。本次沿这个子提交复核，branch 名和子仓 HEAD 都不替代父锁。EP schedule/offload、变量长参数校验、iterator、MTP 与广播所引原件保持不变；本轮子仓变化集中在 MLA 单 head RoPE 缓存、非对称 Q/KV 的 bottom-right causal mask 及其重算传播，不能只刷新依赖号而保留旧 mask/容量判断。

`pyproject.toml` 当前包版本 0.2.2、Python>=3.10，base dependencies 仍为空。安装入口按硬件合并为 `gpu` / `xpu` extras，各自包含 LLM/VLM/VLA 运行依赖；独立 `vla` extra 已移除，不能再分两次安装让后一步覆盖前一步的 pins。GPU extra 含具体 CUDA/cuDNN 依赖，版本组合不代表 HCU 兼容；父包安装成功也不证明 Megatron、TE、Energon 和 custom ops 已配套。

`setup_env.py` 只负责 NVIDIA TE 的 clone、指定 tag/branch、restore、应用 `third_party/patches/TransformerEngine_<tag>` 和构建安装，会写 checkout 与 Python 环境；它不是只读探测，也不安装整个训练栈。HCU任务先固定实际配套制品与开发副本，不能直接用该脚本覆盖现场 TE/Torch。

递归获取gitlink，确认两条训练入口的`--help`、实际import路径和扩展加载。源码/配置、Python依赖、通信和TE/attention库都固定；NV镜像内预装不能当HCU具备证据。

## 4. 运行和测试组织

Megatron栈以模型`examples`/配置交给`parse_train_args→build_model_trainer→trainer.train`，训练模式决定pretrain/SFT/VLM/diffusion函数。Torch栈独立解析配置、model registry、data/sampler、分布式wrapper和BaseTrainer；后者更适合复用compile/DDP/FSDP、输入处理、VLA/world model经验。

按具体模型保持结构、数据变换、label/loss/optimizer；不是把LoongForge README的模型名当成HCU已支持。测试从配置/接口→局部算子或数据→短训→并行和恢复，`tests/llm_vlm/README.md`给出相关分层，embodied的unit/smoke使用另一集合。上游测试描述与本次执行证据分开；本轮没有运行GPU训练。

当前 LLM/VLM E2E 指南将 `PFS_PATH` 定为只读数据/权重入口，`TRAINING_LOG_PATH` 为日志、dataset cache、锁和 checkpoint 的可写输出根，另外指定 LoongForge 与 Loong-Megatron 实际路径；测试入口不会自动下载缺失原件。默认/optional 配置、转换/训练步骤和模型 skip 分别检查，不以脚本返回或存在 baseline JSON 宣称所有模型通过，也不沿用旧固定 `/workspace/E2E/diff` 结果位置。

## 5. 数据、数值和状态契约

LLM/VLM变长packing的总token相同不表示attention计算相同，visual tokens和视频帧数也会改变负载；重排须保持sample、labels、loss权重、mask/position、多模态输入对应关系。模型配方固定tokenizer/sequence/GBS/MB/并行/精度，实验不要随意重写dim/optimizer。

Torch embodied还涉及视频解码/augmentation、action head、任务metric与stateful sampler。checkpoint由具体训练栈负责model/optimizer/scheduler/RNG/sampler进度；Megatron激活offload不是训练checkpoint，不能拿内存buffer做持久恢复状态。

## 6. 两条调用链与底层依赖

变长均衡链为train_step hook→RerunDataIterator预取→收集sequence统计→warmup计时拟合→DP分配/重排→实际tensor all-to-all→训练forward/backward。EP链为父仓flag→固定Loong-Megatron interleaved schedule→MoE dispatcher/延迟wgrad→细粒度recompute/offload。Torch checkpoint链为BaseTrainer每optimizer step→pending async检查→DCP / ZeRO writer 完成→跨rank结果投票与恢复marker；新 canonical state view 同时处理模块/参数别名，不能只靠 unwrapped load 说明全部恢复语义。

每条链的关键源码在以下专题；目录清单仅供找到代码，不意味着同仓所有模型/功能均已精读。

## 7. 重点优化/运维机制

- [变长/多模态DP负载均衡](../topics/loongforge-dp-balance.md)：代价模型和样本重排为何比按token数平均更合理；也说明额外通信/采样成本。
- [跨微批EP overlap与细粒度激活卸载](../topics/loongforge-ep-offload.md)：调度、延迟wgrad、D2H/H2D与NUMA如何联动；关联[既有案例](../cases/loongforge-ep-offload.md)。
- [变量长 ChunkPipe 的数值与缓存契约](../topics/loongforge-chunkpipe-variable-length.md)：序列分块的 prefix sum、最大槽位、MLA/MTP、P2P/TP shape 与 token 归一化；区别于跨微批 EP 重叠。
- [Torch-native异步checkpoint的完整性](../topics/loongforge-async-checkpoint.md)：不让已经写完的checkpoint等到下次save才被识别，避免子集rank进入collective。

## 8. 诊断、数值与回退

DP不均查各rank的sequence²/视觉负载及拟合残差，不仅看token数；overlap卡住查microbatch/VPP/dispatcher和异步依赖，OOM看活动chunk与offload buffer；async save恢复失败查数据完成、marker、失败投票和参数alias。不先怀疑单kernel再忽略上层数据/调度。

每项保持普通路径数值基线、相同effective batch与输入，局部梯度后再阶段loss；精度不同的性能数字不能直接对比。回退以机制包为单位：关闭均衡恢复普通sampler，关闭EP新调度配套撤销offload/recompute，禁用async回到同步保存。HCU长期训练仍以部署既有容错为唯一重启owner。

## 9. PR、版本和更新

[官方Releases](https://github.com/baidu-baige/LoongForge/releases)、[PR](https://github.com/baidu-baige/LoongForge/pulls)、[全仓导航](../../upstream/source-map/baidu-baige-loongforge.md)、[原文目录](../../upstream/docs/baidu-baige-loongforge)分别补发布、讨论、固定实现和教程。没有已登记独立roadmap页面不等于没有计划，按官方Issue/Discussion/Project在线确认。

[#261 异步checkpoint与DCP resume](../../upstream/prs/baidu-baige--LoongForge/PR-261.md)保留历史修复和当时 Gloo/detail-log 缺口；当前 Context / BaseTrainer / StageTimers 已创建、传递并销毁独立 Gloo stage_timing_group，不能把历史未解决状态直接当作当前源码结论；尚无本轮并发运行验证。tensor_wise 的 rank-local 保存/恢复 payload 另有静态不对称，不能由 DCP 格式或测试名认定完整可恢复。当前完成链及仍需验证项见异步 checkpoint 专题；不把历史 A800 数据推广为 HCU 预期。`wiki-search-pr "机制或模型" --engine loongforge`可找未写案例的PR，再追当前父仓及实际子gitlink。

更新同时核对两栈parser/配置、gitlink、DP样本与loss语义、EP schedule/activated tensor生命周期、checkpoint/恢复和测试。新官方机制已合入实际采用分支后，才考虑用等价回归退役HCU补丁。

本轮保留依据：父仓 parser、trainer builder、pyproject、setup_env、DP 均衡与 E2E 指南所引字节未变，故保留两栈入口、空 base dependencies、gpu/xpu extras、环境写入边界与数据/日志根契约。README 新增 LingBot-VLA-v2 / tensor_wise Muon 路线，embodied README 修正 GR00T 目录拼写且更新 Pi0.5 上游性能数字；这些不代表本页已审计新模型、所有 optimizer 或任何 HCU 实测。checkpoint 和 BaseTrainer 已有实质变化，按对应消费者复核，不能继续称实现/测试全部未变。

2026-11-04 固定 GitHub 最近10条 release 观测包含 [`v0.2.0`](https://github.com/baidu-baige/LoongForge/releases/tag/v0.2.0)（2026-08-20）。本页所述当前 DCP/TensorWise/MLA 行为来自所固定 master 与父树 gitlink，未证明全部进入 v0.2.0，也未将 API 的 target_commitish 当作解析后的完整提交。

## 固定证据与复核范围

- [README.md](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/README.md)
- [.gitmodules](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/.gitmodules)
- [pyproject.toml](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/pyproject.toml)
- [setup_env.py](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/setup_env.py)
- [loongforge/train.py](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/loongforge/train.py)
- [loongforge/train/parser.py](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/loongforge/train/parser.py)
- [loongforge/train/trainer_builder.py](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/loongforge/train/trainer_builder.py)
- [loongforge/embodied/README.md](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/loongforge/embodied/README.md)
- [tests/llm_vlm/README.md](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/tests/llm_vlm/README.md)

- [megatron/core/transformer/transformer_config.py](https://github.com/baidu-baige/Loong-Megatron/blob/9d2d6b30f4099ed0e29300f76e19f55b72387ffc/megatron/core/transformer/transformer_config.py)
- [megatron/training/arguments.py](https://github.com/baidu-baige/Loong-Megatron/blob/9d2d6b30f4099ed0e29300f76e19f55b72387ffc/megatron/training/arguments.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
