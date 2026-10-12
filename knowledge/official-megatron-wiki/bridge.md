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
reviewed_on: '2026-10-12'
coverage: selected source, official documentation and related PR reading; no HCU runtime
  validation
sources:
- source: nvidia-nemo-megatron-bridge
  path: README.md
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 3515094a66363c951dfe8abc8a33ad3f3dc7703b0865a1b449b3c2d0cb65002e
- source: nvidia-nemo-megatron-bridge
  path: pyproject.toml
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 93380dfdfd247a3d06df57560b75461d12f5b373fd44aa0ea75ec7176d9e3744
- source: nvidia-nemo-megatron-bridge
  path: docs/training/entry-points.md
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: b2adf198c102593158c53b3c5dce1eb118655c54b117b41726bd77ea82d17665
- source: nvidia-nemo-megatron-bridge
  path: docs/training/config-container-overview.md
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 384b425f0c180976d4d472da569fca71b6af5fd42bd1a1f07ab36af9481daef1
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/config.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: f0ddd9f5450e353dad5cdf067ba8b01088e3e29ff35e521fa622141e03fe080d
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/pretrain.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 28a0fec822239d825da13838dcb6d86ee4b6ac13a52865bb351dc668e59225bf
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/train.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 413a9f26ed5d92a2cc419481897a174c6d11af4d9623a2cc2610b6478c70b561
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/gpt_provider.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 2354707c4c81b5e05c6e62e4613092c26e7271dd17aa293ace75d1bc736abd4f
- source: nvidia-nemo-megatron-bridge
  path: docs/releases/software-versions.md
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: b3ff95aed883fe9583144a10d88d0508abbaab8fe7c5524777da67f913d0ff43
- source: nvidia-nemo-megatron-bridge
  path: docs/training/checkpointing.md
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: effe7f073c2edd1ee8340ecc3f16ceba506be520f5f939ffb1c5368dc7eb35b4
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

本页精读官方main `53681c1aa264b54a1afa320830738382ee2a44f4`。当前`pyproject.toml`要求Python>=3.12,<3.13；build依赖Torch/pybind11，基础依赖含Core extras、NVRX及模型库，一些TE/SSM扩展有单独build isolation要求。应按该提交安装文档/锁文件与实际运行镜像配套，不将包classifiers或单个pip成功当兼容证据。

release software-versions表列NeMo容器的Core/TE/Torch/Bridge组合，是发布配对，不自动代表main与HCU部署相同。本页提供查找机制；真实任务保存Bridge/Core/TE/attention/Energon及patch版本、import路径、库制品和有效配置。不能为读Wiki把最新NV依赖装进HCU训练镜像。

## 4. 配方、启动与测试

统一脚本选择`--model`或`--recipe`之一、`--mode pretrain|sft|lora|dora`，再选mock/local-jsonl等数据；尾部ConfigContainer字段覆盖优先于便捷参数。Slurm/container的env/mount显式配置，不以host export推断容器收到。HCU使用其兼容脚本，保留平台改动与resolved config。

Python `pretrain(config, forward_step_func, callbacks)`适合GPT/Mock数据；finetune用于SFT/PEFT且需要初始化或resume权重来源。配方测试先确认provider、并行、dtype、数据与optimizer；然后局部forward/backward/权重转换、短训练和checkpoint恢复；复杂EP/graph/resiliency必须用实际多rank依赖验证。

成功判据是选定模型真实结构、patch/dispatch生效、step和有效token推进、局部数值/阶段loss及状态恢复符合预期。mock或缩层test配方只能证明相应变体，不推导全模型吞吐/显存或收敛。

## 5. 模型、数据和数值契约

`GPTModelProvider`根据layer spec和真实进程组决定PP/VPP、decoder/MTP、embedding/output所在stage。模型参数、QKV排列、RoPE、vocab padding、embedding tying、tokenizer/special tokens、dtype/scale必须和HF基准一致。转换成功不等于模型数值已对齐。

forward_step返回输出与loss函数，普通loss元组与带token计数的元组有不同聚合口径；packed/SFT/VLM要明确mask、有效token分母及batch布局。全参训练、PEFT frozen base、optimizer/scheduler/RNG与数据iterator分别有状态所有者。不要把初始化权重、adapter resume与完整训练resume混在一个load字段。

## 6. 生命周期与调用链

recipe→ConfigContainer validate/finalize/runtime update→GlobalState→provider/get_model→Core模型与layer spec→optimizer/data setup→Core forward/backward schedule→train_step/sync/callback/checkpoint。`pretrain`支持进程内restart包装，但已由调用方初始化distributed group时会拒绝该模式，避免重复接管进程组。

排障沿最终配置→provider→Core固定版本→TE/attention/通信实际实现→对应测试。存在ProfilingConfig/Straggler/FaultTolerance字段不表示已经部署可用；parser、条件、扩展加载和执行证据必须同时满足。

## 7. 三项机制专题

- [配方、Provider与权重映射](topics/bridge-provider-conversion.md)：layer spec/PP/MTP、低精度初始化、HF转换及PEFT选择。
- [多并行域通信重叠与内存](topics/bridge-overlap-memory.md)：DP/TP/PP/CP/EP不同约束、延迟wgrad/graph、收益与buffer/资源竞争。
- [完整checkpoint和恢复责任](topics/bridge-checkpoint-recovery.md)：初始化vsresume、reshard/data位置、NVRX/恢复owner、保存性能。

其他模型/backend没有在本轮全部精读；完整源码目录和在线检索可继续追问，不能用三篇专题宣称覆盖所有特性。

## 8. 诊断、精度与回退

训练初始loss异常先核对模型/数据/权重映射和精度，取得首差而非直接换kernel。overlap不生效看最终flags与实际trace；多rank卡住取最后共同step、组/collective/异常和存储状态。转换roundtrip只是权重证据，仍需固定输入logits、梯度、optimizer step与阶段loss；FP8有损反量化或skip项目显式登记。

全新实验把`checkpoint.load=None`、save独立目录，避免common recipe默认目录误续跑。保存阻塞单独计时、验证async完成标记和数据位置，恢复后持续观测loss、step、显存及旧进程残留。NVRX与HCU站点容错的能力/依赖不同，唯一恢复owner由任务确定。

## 9. PR、发布和更新入口

[官方文档](https://docs.nvidia.com/nemo/megatron-bridge/latest/)、[Releases](https://github.com/NVIDIA-NeMo/Megatron-Bridge/releases)、[PR](https://github.com/NVIDIA-NeMo/Megatron-Bridge/pulls)、[固定源码导航](../source-maps/nvidia-nemo-megatron-bridge.md)和[原文](../upstream-docs/nvidia-nemo-megatron-bridge/)各有职责。`wiki-search-pr "问题/机制" --engine bridge`可找未写案例的PR，再读取讨论、head/base、实现和测试；open、merged、released、HCU采用和任务实测分别确认。

[#6140](../prs/NVIDIA-NeMo--Megatron-Bridge/PR-6140.md)说明替换decoder后还需finalize TE precision；[#6406](../prs/NVIDIA-NeMo--Megatron-Bridge/PR-6406.md)说明decentralized provider中MTP最终builder的进程组rank传递问题（本轮仍是open，不能写成main已修）。本轮main从fe8b到53681c的新增#6163只改DeepSeekV4多节点inference示例，不改变本页训练链；模型推理任务仍需另读该例。

更新核对实际Core/TE/Energon版本和HCU父gitlink，同时复核总览、三专题、模型recipe和依赖调用。PR讨论变化可能修正结论，即使文件哈希未变也检查；roadmap若在Issue/Discussion/Project继续在线查，不把采集PR窗口称作全部历史覆盖。

## 固定证据与复核范围

- [README.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/README.md)
- [pyproject.toml](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/pyproject.toml)
- [docs/training/entry-points.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/docs/training/entry-points.md)
- [docs/training/config-container-overview.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/docs/training/config-container-overview.md)
- [src/megatron/bridge/training/config.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/src/megatron/bridge/training/config.py)
- [src/megatron/bridge/training/pretrain.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/src/megatron/bridge/training/pretrain.py)
- [src/megatron/bridge/training/train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/src/megatron/bridge/training/train.py)
- [src/megatron/bridge/models/gpt_provider.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/src/megatron/bridge/models/gpt_provider.py)
- [docs/releases/software-versions.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/docs/releases/software-versions.md)
- [docs/training/checkpointing.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/docs/training/checkpointing.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
