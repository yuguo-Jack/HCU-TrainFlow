---
id: official-megatron-wiki/bridge
title: Megatron Bridge：配方、Provider、通信与完整训练状态
engine: bridge
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-11-18'
coverage: fixed source delta and actual consumer review; historical pins retained; no HCU runtime validation
sources:
- source: nvidia-nemo-megatron-bridge
  path: README.md
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: c5338daa70661d52a663d4919f2f6012b9ffe9d72e5eac6a2eef96a1cf07ea2a
- source: nvidia-nemo-megatron-bridge
  path: pyproject.toml
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 044abb1c08a098005b4207d1919d8ec6a034955ede261af3684261ea2ce8640d
- source: nvidia-nemo-megatron-bridge
  path: docs/training/entry-points.md
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: b2adf198c102593158c53b3c5dce1eb118655c54b117b41726bd77ea82d17665
- source: nvidia-nemo-megatron-bridge
  path: docs/training/config-container-overview.md
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 384b425f0c180976d4d472da569fca71b6af5fd42bd1a1f07ab36af9481daef1
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/config.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: deeafbdcdbb8738f7ca6d2e0190e159b542d6bc6e1fab919eca9d4f740e4bd93
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/pretrain.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: d224e0dda091430b0e52bf094fafee119e201e2213755de68f81fc572cbc7714
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/train.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 03f09f7ff1da6cc83f04ea9450280bf33adcd873ced83d50e7c35531910adddf
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/gpt_provider.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 2354707c4c81b5e05c6e62e4613092c26e7271dd17aa293ace75d1bc736abd4f
- source: nvidia-nemo-megatron-bridge
  path: docs/releases/software-versions.md
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: b3ff95aed883fe9583144a10d88d0508abbaab8fe7c5524777da67f913d0ff43
- source: nvidia-nemo-megatron-bridge
  path: docs/training/checkpointing.md
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: effe7f073c2edd1ee8340ecc3f16ceba506be520f5f939ffb1c5368dc7eb35b4
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/dpo_train.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 45c7e92be9a7c390efbcbaf800569987dc2e66a7877283e0de1250901ddecfb4
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/data/builders/dpo.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 71d0f8a0a5df6ec78a265aba09856091e1a1ea20740f20c28c9ec2bc0dfd700a
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/conversion/auto_bridge.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 1634f53dfb7f086f73c467d980553a4483663cf61f48738d2103cff5319dd465
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/hf_pretrained/state.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 0729aa811936cc1f6caa02cbe54f3d9d74cd6173464bb03555a6341d54a0c849
- source: nvidia-nemo-megatron-bridge
  path: README.md
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: 422ef3137765d4bd7b2a478bae109baa33c50eb37255673ef710a689834b14f2
- source: nvidia-nemo-megatron-bridge
  path: pyproject.toml
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: cb14b27dd667adaf27777c27a5f472338d4ae33a31c5a44afa048cb1b750a99a
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/config.py
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: fca097a18062d74b23785fe30782d507df32bb1e89816112e377cb70b284a261
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/gpt_provider.py
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: da3c92f65431864e3079e09167dbcdb96e911731e0bff73d82795894977fd625
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/train.py
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: a438b252612cbe51cced1193f917333dc08cdae445f3c9497517d34ca7781638
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/pretrain.py
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: 6534422c772f10bb8927f3c13e981d40a7758c1d63b458cc5b8372cfa1190c3c
retrieved_on: '2026-11-18'
---

# Megatron Bridge：配方、Provider、通信与完整训练状态

## 1. 定位与 HCU/生态关系

Megatron Bridge连接官方模型recipe、HF config/权重与Megatron Core训练，支持pretrain、SFT/PEFT和LLM/VLM等模型入口。Core负责底层模型并行/schedule，TE与attention/算子库负责具体实现，Energon负责特定数据流水线；Bridge不是每个底层能力的替代。

HCU独立Bridge patch仓、HCU Megatron-LM内嵌Bridge和本页官方main是不同版本关系。使用模型先参考适用HCU脚本/配方和实际依赖，官方用于核对结构/训练语义和新特性，不能覆盖现场HCU环境变量或随意混装各仓gitlink。

## 2. 目录和问题路径

| 路径 | 职责/追查方向 |
| --- | --- |
| `scripts/training/{train.sh,setup_experiment.py,run_recipe.py}` | 启动器、模型/recipe选择、模式、dataset与覆盖；trace/配置不符从这里进入 |
| `src/megatron/bridge/recipes/` | 模型及硬件配方，预训练/SFT/LoRA/DoRA参数；函数名不代替实际配置 |
| `models/gpt_provider.py`、`model_provider.py`及各模型family | layer spec、PP/VPP/MTP、pre/post process与模型构建 |
| `models/conversion/` | AutoBridge、mapping、HF/native权重布局与导出 |
| `training/{config,pretrain,setup,train}.py` | ConfigContainer、生命周期、optimizer/data、step/同步与callbacks |
| `training/comm_overlap.py`、`mixed_precision`相关模块 | DP/TP/PP/CP/EP条件和最终配置传播，TE precision |
| `data/energon/`、`data/` | 数据provider、batch/loss与可恢复加载 |
| `training/{fault_tolerance,inprocess_restart}.py` | NVRX/进程内重启及进程组所有权 |
| `tests/unit_tests/`、`tests/functional_tests/` | 配方/provider/转换/loop单测与真实分布式组；skip不代表训练通过 |
| `docs/training/`、`docs/skills/`、`docs/releases/` | 稳定指南、具体机制参数/验证与发布配对 |

## 3. 安装、版本与真实加载

本页当前固定官方 `11d8b349d2daff3523bb9655b04f4ad33a9e9ea9`；实际父树 `3rdparty/Megatron-LM` 为 `a463e854a7aba6e93aa03cb0a7cdd49ee4612cb6`，与独立 Core 专题的 `91260b59` 不同。`pyproject.toml` 要求 Python>=3.12,<3.13，Transformers 改为 >=5.21.1,<5.24，明确跳过会破坏 Step-3.5 config 的 5.21.0；uv 约束另限制 pyarrow<26、httpx<1，并为所选 Core 镜像 CUDA13/架构相关 FlashInfer JIT-cache 元数据。包依赖、uv resolver 覆盖、发布容器和现场 HCU 镜像分别核对，不能把这张 NV wheel 清单直接装进 HCU 环境。build isolation、Torch/扩展 ABI 与实际 import 路径仍需按所用提交验证。

release software-versions表列NeMo容器的Core/TE/Torch/Bridge组合，是发布配对，不自动代表main与HCU部署相同。本页提供查找机制；真实任务保存Bridge/Core/TE/attention/Energon及patch版本、import路径、库制品和有效配置。不能为读Wiki把最新NV依赖装进HCU训练镜像。

## 4. 配方、启动与测试

统一脚本选择`--model`或`--recipe`之一、`--mode pretrain|sft|lora|dora`，再选mock/local-jsonl等数据；尾部ConfigContainer字段覆盖优先于便捷参数。Slurm/container的env/mount显式配置，不以host export推断容器收到。HCU使用其兼容脚本，保留平台改动与resolved config。

Python `pretrain(config, forward_step_func, callbacks)`适合GPT/Mock数据；finetune用于SFT/PEFT且需要初始化或resume权重来源。配方测试先确认provider、并行、dtype、数据与optimizer；然后局部forward/backward/权重转换、短训练和checkpoint恢复；复杂EP/graph/resiliency必须用实际多rank依赖验证。

新增 DPO 走 `DPODatasetConfig → dpo_train → finetune` 和专用 forward/loss，不是给普通 SFT batch 换一个 loss 名。需要先用实际 reference 权重、相同 tokenizer/template 和样本规则生成 reference-logprob 产物，满足成对行数、CP/MTP 和规约约束；详见 [Provider 与数据专题](../topics/bridge-provider-conversion.md)。recipe 名和新增配置单测不构成 HCU DPO 已训练的证据。

成功判据是选定模型真实结构、patch/dispatch生效、step和有效token推进、局部数值/阶段loss及状态恢复符合预期。mock或缩层test配方只能证明相应变体，不推导全模型吞吐/显存或收敛。

## 5. 模型、数据和数值契约

`GPTModelProvider`根据layer spec和真实进程组决定PP/VPP、decoder/MTP、embedding/output所在stage。模型参数、QKV排列、RoPE、vocab padding、embedding tying、tokenizer/special tokens、dtype/scale必须和HF基准一致。转换成功不等于模型数值已对齐。

forward_step返回输出与loss函数，普通loss元组与带token计数的元组有不同聚合口径；packed/SFT/VLM要明确mask、有效token分母及batch布局。全参训练、PEFT frozen base、optimizer/scheduler/RNG与数据iterator分别有状态所有者。不要把初始化权重、adapter resume与完整训练resume混在一个load字段。

## 6. 生命周期与调用链

recipe→ConfigContainer validate/finalize/runtime update→GlobalState→provider/get_model→Core模型与layer spec→optimizer/data setup→Core forward/backward schedule→train_step/sync/callback/checkpoint。`pretrain`支持进程内restart包装，但已由调用方初始化distributed group时会拒绝该模式，避免重复接管进程组。

排障沿最终配置→provider→Core固定版本→TE/attention/通信实际实现→对应测试。存在ProfilingConfig/Straggler/FaultTolerance字段不表示已经部署可用；parser、条件、扩展加载和执行证据必须同时满足。

## 7. 三项机制专题

- [配方、Provider与权重映射](../topics/bridge-provider-conversion.md)：layer spec/PP/MTP、低精度初始化、HF转换及PEFT选择。
- [多并行域通信重叠与内存](../topics/bridge-overlap-memory.md)：DP/TP/PP/CP/EP不同约束、延迟wgrad/graph、收益与buffer/资源竞争。
- [完整checkpoint和恢复责任](../topics/bridge-checkpoint-recovery.md)：初始化vsresume、reshard/data位置、NVRX/恢复owner、保存性能。

其他模型/backend没有在本轮全部精读；完整源码目录和在线检索可继续追问，不能用三篇专题宣称覆盖所有特性。

## 8. 诊断、精度与回退

训练初始loss异常先核对模型/数据/权重映射和精度，取得首差而非直接换kernel。overlap不生效看最终flags与实际trace；多rank卡住取最后共同step、组/collective/异常和存储状态。转换roundtrip只是权重证据，仍需固定输入logits、梯度、optimizer step与阶段loss；FP8有损反量化或skip项目显式登记。

全新实验把`checkpoint.load=None`、save独立目录，避免common recipe默认目录误续跑。保存阻塞单独计时、验证async完成标记和数据位置，恢复后持续观测loss、step、显存及旧进程残留。NVRX与HCU站点容错的能力/依赖不同，唯一恢复owner由任务确定。

README 新列 Inkling 2 Small 和 ERNIE-5.5 的官方模型入口。前者宣传的转换、图文推理和 GB200 配方，后者列出的 SFT 入口均需继续核对对应 verification card、模型结构和配方依赖；这里没有采纳为 HCU 已支持，也不由模型列表推广全部训练组合。

## 9. PR、发布和更新入口

[官方文档](https://docs.nvidia.com/nemo/megatron-bridge/latest/)、[Releases](https://github.com/NVIDIA-NeMo/Megatron-Bridge/releases)、[PR](https://github.com/NVIDIA-NeMo/Megatron-Bridge/pulls)、[固定源码导航](../../upstream/source-map/nvidia-nemo-megatron-bridge.md)和[原文](../../upstream/docs/nvidia-nemo-megatron-bridge)各有职责。`wiki-search-pr "问题/机制" --engine bridge`可找未写案例的PR，再读取讨论、head/base、实现和测试；open、merged、released、HCU采用和任务实测分别确认。

[#6140](../../upstream/prs/NVIDIA-NeMo--Megatron-Bridge/PR-6140.md)保留 decoder replacement 后 precision 初始化的历史定位。对 [#6406](../../upstream/prs/NVIDIA-NeMo--Megatron-Bridge/PR-6406.md)，当前 `mtp_block_spec` 已接收显式 `pp_rank`，并传到 callable spec 和最终 Core builder；旧“最终调用尚未传 rank”的结论只适用于 `41af2dcf`。无全局 MPU 的调用者仍须传真实所属 PP rank，不能由接口新增推定所有调用点、GPU 或 HCU 已通过，详见 Provider 专题。

相对上轮 `2b1c8ccd7285cfd09b82afd523859dbe04d754e4`，本轮训练侧变化包括 emerging optimizer 的 LayerWise 分布规范化、MFSDP V2 checkpoint / dtype 校验边界、退出时 DataLoader 和 local graph runner 的释放，以及 collective adapter 导出只在 rank0 保留完整权重并广播写入错误。Qwen3 MoE 的 H100 recipe 改走 builder-backed `get_model_config()`，ModelOpt 导出改用 prepared plan 与 grouped stream；这些入口不能和旧 provider/导出 API 混用。README 新增 MiniCPM-o 4.5 的 text/image/audio understanding，明确不含 speech generation 或 SFT/LoRA recipes；不由模型列表推导全部训练组合可用。DPO 数据/loss、确定性委托和旧权重清理机制来自此前版本，其未变消费者继续保留。

更新核对实际Core/TE/Energon版本和HCU父gitlink，同时复核总览、三专题、模型recipe和依赖调用。PR讨论变化可能修正结论，即使文件哈希未变也检查；roadmap若在Issue/Discussion/Project继续在线查，不把采集PR窗口称作全部历史覆盖。

2026-11-18 复核还改变了配置与退出方法：Megatron-FSDP 选择转到 `cfg.ddp.use_megatron_fsdp`，显式梯度 dtype 和最终 Core finalize 决定真实精度；异常退出先清理 optimizer 持有的 graph 引用而不等待可能失败的 CUDA collective。HF 转换补了平面 RoPE config 搬运、精确 key 排除和有限的 ModelOpt 映射支持，分别见三项专题。DPO builder/数据/评分/step/loss、主要训练指南和版本配对表字节未变，保留其原数值与数据位置约束；NVRx 文档这次仅增旧版 inprocess guide 链接，未改变既有弃用/恢复 owner 判定。主仓内容、Core gitlink和现场部署仍是三项独立证据。

2026-11-04 固定 GitHub 最近10条 release 观测已包含 [`v0.7.0`](https://github.com/NVIDIA-NeMo/Megatron-Bridge/releases/tag/v0.7.0)（2026-10-30）。该发行记录不把本页 main 的 LayerWise/FSDP/ModelOpt 等所有变化自动纳入0.7.0；release 配对表、tag 原件、main 与 HCU 使用锁分别确认。

## 2026-11-18 固定消费者

- [README.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/README.md)
- [pyproject.toml](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/pyproject.toml)
- [src/megatron/bridge/training/config.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/src/megatron/bridge/training/config.py)
- [src/megatron/bridge/models/gpt_provider.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/src/megatron/bridge/models/gpt_provider.py)
- [src/megatron/bridge/training/train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/src/megatron/bridge/training/train.py)
- [src/megatron/bridge/training/pretrain.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/src/megatron/bridge/training/pretrain.py)

## 固定证据与复核范围

- [README.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/README.md)
- [pyproject.toml](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/pyproject.toml)
- [docs/training/entry-points.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/docs/training/entry-points.md)
- [docs/training/config-container-overview.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/docs/training/config-container-overview.md)
- [src/megatron/bridge/training/config.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/training/config.py)
- [src/megatron/bridge/training/pretrain.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/training/pretrain.py)
- [src/megatron/bridge/training/train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/training/train.py)
- [src/megatron/bridge/models/gpt_provider.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/models/gpt_provider.py)
- [docs/releases/software-versions.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/docs/releases/software-versions.md)
- [docs/training/checkpointing.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/docs/training/checkpointing.md)

- [src/megatron/bridge/training/dpo_train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/training/dpo_train.py)
- [src/megatron/bridge/data/builders/dpo.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/data/builders/dpo.py)
- [src/megatron/bridge/models/conversion/auto_bridge.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/models/conversion/auto_bridge.py)
- [src/megatron/bridge/models/hf_pretrained/state.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/models/hf_pretrained/state.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
