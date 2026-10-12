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
reviewed_on: '2026-10-12'
coverage: selected source, official documentation and related PR reading; no HCU runtime
  validation
sources:
- source: baidu-baige-loongforge
  path: README.md
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: 388183748b51d058699634ce3bc974fdd1674387fdd89ac27e553dda8c69437b
- source: baidu-baige-loongforge
  path: .gitmodules
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: b5aca9eaf884dfde53b152fc6000eff8a8c793339b659411f6e79292bf68b2ed
- source: baidu-baige-loongforge
  path: pyproject.toml
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: 56fa6d70bf0d1e187cfb9d5594628d8d9648360ffd5a881b9e7bb77a1eb4c24c
- source: baidu-baige-loongforge
  path: setup_env.py
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: b971d9c245c989349bcf52829b79a94cec25e82045727a108b0c834f6505b3ba
- source: baidu-baige-loongforge
  path: loongforge/train.py
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: cef9bf0d396232e0f5ed4ba019fabaa3e7f0dc70c1fba35e564660c190e07248
- source: baidu-baige-loongforge
  path: loongforge/train/parser.py
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: a0d64417a7b1fb4b2d492e3cfd779e0084ce44d8c95e8c571c7c95c0b2b1e432
- source: baidu-baige-loongforge
  path: loongforge/train/trainer_builder.py
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: 0d53b62a230bb244134a0fa72da29213ef8cbec1a983aea9042abd71d4708470
- source: baidu-baige-loongforge
  path: loongforge/embodied/README.md
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: cea16e85bafe721b0a31015891d18b948974706c2acc263c871c0e98cac5217b
- source: baidu-baige-loongforge
  path: tests/llm_vlm/README.md
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: c90e1a24281ed1c2b4cfe13fa7676ec5e83e700b0de33fedf81bd6e6de7ef9af
---

# LoongForge：两类训练入口、DP 均衡、EP 重叠与状态恢复

## 1. 定位与两条训练栈

LoongForge 同仓维护两类训练栈：Megatron-based 的 LLM/VLM/diffusion 栈，以及 **Torch-native 的 VLA/WAM embodied 栈**。前者入口 `loongforge/train.py`，后者 `loongforge/embodied/train.py`；源码明确它们不共用全部 parser/args/core。用前者的TP/PP/EP经验指导后者前，先判断模型和并行组织，不能只看“都是训练”就套同一配方。

它可提供激进调度、变长/多模态负载均衡、数据IO、显存与模型适配参考。HCU 实际出口仍为选定 HCU 训练工程和底层库；CUDA/DeepEP/TE扩展依赖及NV启动变量不代表HCU已有实现。

## 2. 目录和问题导航

| 路径 | 职责/问题入口 |
| --- | --- |
| `loongforge/train.py`、`train/{parser,trainer_builder}.py` | 配置→训练器→train，仅Megatron栈 |
| `loongforge/model/`、`configs/`、`examples/` | 模型provider、结构/recipe、预训练/SFT/VLM/diffusion启动 |
| `loongforge/data/dp_balance/` | 预取/统计/代价拟合/样本重排；变长/视觉DP负载不均 |
| `loongforge/train/full_hetero_cpu_offload.py` | 另一类offload/异构训练入口，不与EP激活卸载混称 |
| `ops/`、`patches/` | 平台扩展及训练依赖适配，查实际导入与build |
| `third_party/Loong-Megatron` | Megatron的schedule、dispatcher与激活机制真正实现 |
| `loongforge/embodied/{data,model,train,distributed,optimizer}/` | 独立Torch训练、数据变换、DDP/FSDP/HSDP、checkpoint与optimizer |
| `tests/llm_vlm/`、`tests/embodied/` | 两栈分层测试；选定模型集不能代表全部模型 |
| `docs/source/features/`、`embodied_tutorial/` | 特性与模型教程，继续追源码/依赖 |

## 3. 构建安装与实际子提交

本轮父仓 `733126ddccaf49c4bfd780d384f00878c1f0a9a8` 的 `.gitmodules` 指向 `baidu-baige/Loong-Megatron`，tracking branch 为 `loong-main/core_v0.15.0`；**父树固定 gitlink `64c279afb879229cff12fb293624e3691990403f`**。branch名用于后续监测，不替代本次真正依赖。精读EP/offload时本页专题已沿固定子源码，而非用子仓当前HEAD。

`pyproject.toml` 要求Python>=3.10；base dependencies为空，GPU等optional extras与`setup_env.py`/扩展补丁承担实际安装。`pip install`父包成功不足以证明Megatron、TE、DeepSpeed、Energon或custom ops已配套。官方GPU extra列出的版本属于其运行组合，HCU按DTK镜像与对应工程重新核对，不能安装NV wheel覆盖现场Torch。

递归获取gitlink，确认两条训练入口的`--help`、实际import路径和扩展加载。源码/配置、Python依赖、通信和TE/attention库都固定；NV镜像内预装不能当HCU具备证据。

## 4. 运行和测试组织

Megatron栈以模型`examples`/配置交给`parse_train_args→build_model_trainer→trainer.train`，训练模式决定pretrain/SFT/VLM/diffusion函数。Torch栈独立解析配置、model registry、data/sampler、分布式wrapper和BaseTrainer；后者更适合复用compile/DDP/FSDP、输入处理、VLA/world model经验。

按具体模型保持结构、数据变换、label/loss/optimizer；不是把LoongForge README的模型名当成HCU已支持。测试从配置/接口→局部算子或数据→短训→并行和恢复，`tests/llm_vlm/README.md`给出相关分层，embodied的unit/smoke使用另一集合。上游测试描述与本次执行证据分开；本轮没有运行GPU训练。

## 5. 数据、数值和状态契约

LLM/VLM变长packing的总token相同不表示attention计算相同，visual tokens和视频帧数也会改变负载；重排须保持sample、labels、loss权重、mask/position、多模态输入对应关系。模型配方固定tokenizer/sequence/GBS/MB/并行/精度，实验不要随意重写dim/optimizer。

Torch embodied还涉及视频解码/augmentation、action head、任务metric与stateful sampler。checkpoint由具体训练栈负责model/optimizer/scheduler/RNG/sampler进度；Megatron激活offload不是训练checkpoint，不能拿内存buffer做持久恢复状态。

## 6. 两条调用链与底层依赖

变长均衡链为train_step hook→RerunDataIterator预取→收集sequence统计→warmup计时拟合→DP分配/重排→实际tensor all-to-all→训练forward/backward。EP链为父仓flag→固定Loong-Megatron interleaved schedule→MoE dispatcher/延迟wgrad→细粒度recompute/offload。Torch checkpoint链为BaseTrainer每optimizer step→pending async检查→跨rank完成投票→持久写入完成→恢复marker。

每条链的关键源码在以下专题；目录清单仅供找到代码，不意味着同仓所有模型/功能均已精读。

## 7. 三项优化/运维机制

- [变长/多模态DP负载均衡](topics/loongforge-dp-balance.md)：代价模型和样本重排为何比按token数平均更合理；也说明额外通信/采样成本。
- [跨微批EP overlap与细粒度激活卸载](topics/loongforge-ep-offload.md)：调度、延迟wgrad、D2H/H2D与NUMA如何联动；关联[既有案例](cases/loongforge-ep-offload.md)。
- [Torch-native异步checkpoint的完整性](topics/loongforge-async-checkpoint.md)：不让已经写完的checkpoint等到下次save才被识别，避免子集rank进入collective。

## 8. 诊断、数值与回退

DP不均查各rank的sequence²/视觉负载及拟合残差，不仅看token数；overlap卡住查microbatch/VPP/dispatcher和异步依赖，OOM看活动chunk与offload buffer；async save恢复失败查数据完成、marker、失败投票和参数alias。不先怀疑单kernel再忽略上层数据/调度。

每项保持普通路径数值基线、相同effective batch与输入，局部梯度后再阶段loss；精度不同的性能数字不能直接对比。回退以机制包为单位：关闭均衡恢复普通sampler，关闭EP新调度配套撤销offload/recompute，禁用async回到同步保存。HCU长期训练仍以部署既有容错为唯一重启owner。

## 9. PR、版本和更新

[官方Releases](https://github.com/baidu-baige/LoongForge/releases)、[PR](https://github.com/baidu-baige/LoongForge/pulls)、[全仓导航](../source-maps/baidu-baige-loongforge.md)、[原文目录](../upstream-docs/baidu-baige-loongforge/)分别补发布、讨论、固定实现和教程。没有已登记独立roadmap页面不等于没有计划，按官方Issue/Discussion/Project在线确认。

[#261 异步checkpoint与DCP resume](../prs/baidu-baige--LoongForge/PR-261.md)同时记录解决了什么和未解决的Gloo/detail-log问题；不把其A800实验数据推广为HCU预期。`wiki-search-pr "机制或模型" --engine loongforge`可找未写案例的PR，再追当前父仓及实际子gitlink。

更新同时核对两栈parser/配置、gitlink、DP样本与loss语义、EP schedule/activated tensor生命周期、checkpoint/恢复和测试。新官方机制已合入实际采用分支后，才考虑用等价回归退役HCU补丁。

## 固定证据与复核范围

- [README.md](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/README.md)
- [.gitmodules](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/.gitmodules)
- [pyproject.toml](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/pyproject.toml)
- [setup_env.py](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/setup_env.py)
- [loongforge/train.py](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/loongforge/train.py)
- [loongforge/train/parser.py](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/loongforge/train/parser.py)
- [loongforge/train/trainer_builder.py](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/loongforge/train/trainer_builder.py)
- [loongforge/embodied/README.md](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/loongforge/embodied/README.md)
- [tests/llm_vlm/README.md](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/tests/llm_vlm/README.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
