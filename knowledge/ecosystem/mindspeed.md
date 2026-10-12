---
id: ecosystem/mindspeed
title: MindSpeed 与 MindSpeed-LLM：特性底座、模型训练和恢复
engine: mindspeed
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
- source: ascend-mindspeed
  path: README.md
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: 10c6731705c141a7f72921b1ec77fbb498adb617d4a2639c7831209b26bbea34
- source: ascend-mindspeed
  path: docs/en/user-guide/install_guide.md
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: fa4261944e07bf3edd1b2c0a4383b2b590ffff5deef8581d4f33c15940cddd52
- source: ascend-mindspeed
  path: docs/en/user-guide/quickstart.md
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: d9353c14ad59e1d20b1b3b4f0731db4dcd55036c7de5e546797d7e7eded9887a
- source: ascend-mindspeed
  path: mindspeed/megatron_adaptor.py
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: a5dff020efb4e943ee6732f68ca04dfdd90779fca3efb0b044c1b92fda54872c
- source: ascend-mindspeed
  path: docs/en/release_notes_core.md
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: bf6691f27e553ebb7c05a6b454eda2cfab77b5d14e8d9072dc28aa903ae82ab6
- source: ascend-mindspeed-llm
  path: README.md
  commit: 2fed626696175480ae1ab3342a94017301a25209
  sha256: d430843594ba4a40132b49fa856e57f10d03e2e06d0a9563fd716ee95f8c2b7b
- source: ascend-mindspeed-llm
  path: .gitmodules
  commit: 2fed626696175480ae1ab3342a94017301a25209
  sha256: fffb397bbe3cff135ea88b649129e53d551b010df5c1d411daef7c2ab8731d57
- source: ascend-mindspeed-llm
  path: docs/en/pytorch/training/install_guide.md
  commit: 2fed626696175480ae1ab3342a94017301a25209
  sha256: 6332075f7b8d7da01d50db00c72a585b971ea75381421c6c61fd5a6818ff450f
- source: ascend-mindspeed-llm
  path: pretrain_gpt.py
  commit: 2fed626696175480ae1ab3342a94017301a25209
  sha256: 57022768d4b4b396cda2de61a1638733fe37767736a7dce0592a560bbac2c9fb
- source: ascend-mindspeed-llm
  path: docs/en/release_notes_llm.md
  commit: 2fed626696175480ae1ab3342a94017301a25209
  sha256: 9c555edc576f5658b40648d4b5a15e3a3d093bfcdedd2fd676d90b648092a921
---

# MindSpeed 与 MindSpeed-LLM：特性底座、模型训练和恢复

## 1. 两个实际工程与职责边界

**MindSpeed** 是 Ascend 训练加速/适配的底座，向 Megatron 特性管理、MoE、CP、重算和算子接口注入实现；**MindSpeed-LLM** 是使用这套能力的模型训练应用，提供预训练/SFT、模型脚本、数据、MCore/FSDP2 等训练后端和恢复集成。它们不是同一仓的两个名字，LLM 新模型不表示独立 Core 的所有功能同时更新。

HCU 可以参考其并行算法、通信调度、显存取舍和训练组织，但 CANN、torch_npu、HCCL、ATB、MindIO 等平台接口不能当作 HCU 命令。要先查实际 HCU Core/TE/通信/容错实现有无等价功能，再决定迁移哪些调度或算法。

## 2. 目录职责与问题路径

| 工程 | 路径 | 从什么问题进入 |
| --- | --- | --- |
| MindSpeed | `mindspeed/megatron_adaptor.py` | import 时何时打补丁、是否早于 Megatron import、是否重复注册 |
| MindSpeed | `mindspeed/features_manager/` | 参数、互斥、pre-patch/patch、等级；先查验证再进入实际替换模块 |
| MindSpeed | `mindspeed/core/transformer/moe/moe_feature/overlap/` | dispatcher→专家 MLP→combine 的前反向与异步依赖 |
| MindSpeed | `mindspeed/core/context_parallel/` 及 attention 模块 | CP group、数据分片、mask/RoPE 与 ring/KV 交换 |
| MindSpeed | `docs/en/features/`、`tests/` | 特性说明和机制测试，按 backend 与版本确认适用性 |
| MindSpeed-LLM | `pretrain_gpt.py`、`mindspeed_llm/training/` | MCore 模型 provider、forward/loss、optimizer、训练循环 |
| MindSpeed-LLM | `mindspeed_llm/features_manager/`、`tasks/megatron_adaptor_v2.py` | 应用特性与底座 patch 的叠加顺序 |
| MindSpeed-LLM | `mindspeed_llm/fsdp2/{models,features,train}/` | Torch/FSDP2 模型、loss 与 trainer，不能默认走 MCore 同一参数链 |
| MindSpeed-LLM | `mindspeed_llm/core/high_availability/` | replica optimizer、外部 MindIO TTP 与恢复状态 |
| MindSpeed-LLM | `examples/`、`configs/`、`tests/`、`docs/en/pytorch/` | 模型官方脚本、版本安装、预训练/SFT、测试与诊断 |

## 3. 安装、发布配对与 gitlink

MindSpeed 的官方安装要求配套 Ascend driver/CANN、Torch/torch_npu 及对应算子库，不能只 `pip install` 后就认为 HCU 可用。MindSpeed-LLM 的已发布安装指南列出 MindSpeed `26.1.0_core_r0.12.1`、Megatron `core_v0.12.1` 等配对；这是发布指南，与当前 master 代码树应分别核对。最新入口已经存在 `MINDSPEED_LLM_VERSION=018` 与默认 `012` 的分支，不把文件存在当成默认使用0.18。

本轮固定独立 Core `241431d43e02a89556d2d2b3eacc7e24448adee5`、LLM `2fed626696175480ae1ab3342a94017301a25209`。**LLM 父树实际锁定 `3rdparty/MindSpeed@7969e1c6b61c44fdb09d20607561824675bb216f`，URL 指向 GitCode；它不是本轮独立 GitHub Core HEAD。**同树 `3rdparty/Megatron-LM@a845aa7e12b3a117e24c2352b9e3e60bad2e3a17`，还含 FSDPTurbo 依赖。阅读应用运行效果时沿这组依赖，不能随手用最新版 Core 替换。

安装检查包含递归 submodule、环境脚本、实际 import 路径、C++/NPU 扩展和目标硬件。HCU 移植按现场 DTK/Torch/库构建链重做匹配，NPU 自动转换或 wheel 不是 HCU 等价实现。

## 4. 运行与分层验证

MindSpeed quickstart 要在 `import torch` 之后、Megatron import 之前引入 `mindspeed.megatron_adaptor`。其 import 会 `patch_features()`：解析参数→pre-patches→正式 patches；放错 import 顺序会让已经绑定的符号未被替换。异常排查首先确认各 rank 是否使用同样依赖和 feature 配置。

MindSpeed-LLM 先选该模型的官方 `examples` 脚本、训练阶段与 backend。`pretrain_gpt.py` 引入自己的 adaptor，在 model_provider 中选择 local/TE layer spec、MTP 等结构，再进入对应训练实现；FSDP2 则通过自己的 model factory 和 trainer，配置不能跨入口乱套。记录最终模型结构、dtype、数据、并行组、effective config 与 patch 日志。

验证从参数/非法组合单测、局部 forward/backward、短训练到多 rank 恢复。应能证明 dispatcher、grouped GEMM、CP 和 optimizer 实际走了所选路径；被自动修正、跳过、fallback 或测试 skip 均单列。模型跑通不能代替 attention/mask、router/辅助 loss、有效 token 分母和恢复状态的验收。

## 5. 模型、数据和状态契约

MindSpeed Core 特性会同时修改模块、模型并行初始化与 batch 分片。CP 不仅改变 attention kernel，还可能改变 causal mask、RoPE position、packed sequence 与 token ownership；MoE 必须保持专家分配、gate 权重、共享专家、dispatch/combine 逆关系和 dgrad/wgrad。HCU 实现应逐项对照消费者契约。

LLM 应用负责结构和数据语义：模型参数、MTP、tokenizer、预训练/指令数据、label shift、ignore index、loss mask、梯度累计、checkpoint 中模型/optimizer/RNG/数据位置。MCore 与 FSDP2 的 loss/状态所有权有差别；相同 flag 名不等于相同作用。

## 6. 实际调用链

底座链为 adaptor import→`MindSpeedFeaturesManager`→feature 参数校验→注册替换→MoELayer/MLP/attention/group 初始化→底层 Ascend 实现及 collective。应用链为模型脚本→LLM adaptor→模型 provider 或 FSDP2 model factory→训练 forward/loss/optimizer→底座特性与平台库。查“为什么参数被开启/禁止”先看 feature；查“何时真正通信/释放”再看 core 与测试。

## 7. 分别深入两项机制

MindSpeed Core：

- [MoE all-to-all overlap 与 Zero Memory](topics/mindspeed-moe-overlap-memory.md)：不同 dispatcher 的条件、共享专家的隐式配置、重算/显存成本；关联[已有 EP 案例](cases/mindspeed-ep-constraints.md)。
- [长序列 CP 的分片与交换](topics/mindspeed-context-parallel.md)：ring、hybrid、KV all-gather 的 head/sequence/group 约束及 mask/RoPE。

MindSpeed-LLM：

- [ChunkLoss 的 logit 显存与归一化](topics/mindspeed-llm-chunk-loss.md)：分序列计算、前向求局部梯度、MCore/FSDP2 入口区别，避免以节省显存为由改变 loss。
- [高可用与 replica optimizer](topics/mindspeed-llm-high-availability.md)：状态冗余、额外内存、MindIO/MindCluster 依赖和弹性限制。

## 8. 数值、排障与恢复

MoE 卡住查参数互斥、各 rank token 数、collective 顺序、异步句柄与 expert/grouped GEMM；CP 偏差查 local/global position、mask、packed sequence 和 group；ChunkLoss 偏差查 shift、有效 token、每 chunk 分母和 grad scaling；恢复偏差查 replica/optimizer/RNG/数据与原始并行配置。先用最小合法组合建立数值基线，再添加复杂组合。

高可用 flag 不会自动安装 MindIO 或提供机器池。Ascend 的故障修复和弹性设计是参考；HCU 由任务指定的 Cluster Manager 等唯一恢复负责人执行。诊断取完整 rank 日志/栈和最后共同 step，保持旧可信 checkpoint 和回退配方；不要把“样本被跳过、worker重启了”当作训练质量恢复。

## 9. 发布、PR 与更新入口

分别查两仓 release notes、[Core Releases](https://github.com/Ascend/MindSpeed/releases)、[LLM Releases](https://github.com/Ascend/MindSpeed-LLM/releases)与 [Core PR](https://github.com/Ascend/MindSpeed/pulls)/[LLM PR](https://github.com/Ascend/MindSpeed-LLM/pulls)。源码中也有 GitCode 指向，应按实际维护入口查 Issue/PR；没有本地 PR 来源页不等于没有功能或更新。公开 roadmap/兼容表若不在已收录范围，在线查证，不能从 release 名推演。

[Core 全仓导航](../source-maps/ascend-mindspeed.md)、[LLM 全仓导航](../source-maps/ascend-mindspeed-llm.md)和两份官方原文目录提供继续阅读入口。线上问题检索要明确仓库，例如 `wiki-search-pr "alltoall overlap" --repo Ascend/MindSpeed` 或 `--repo Ascend/MindSpeed-LLM`，再追固定代码。

更新分别比较两个来源；LLM 还要核对实际 gitlink、版本选择、模型脚本、参数注册和底层 patch。共同更新本页、四篇专题与 EP 案例，不让“底座说明已更新、应用仍用旧参数”产生矛盾。

## 固定证据与复核范围

- [README.md](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/README.md)
- [docs/en/user-guide/install_guide.md](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/user-guide/install_guide.md)
- [docs/en/user-guide/quickstart.md](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/user-guide/quickstart.md)
- [mindspeed/megatron_adaptor.py](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/mindspeed/megatron_adaptor.py)
- [docs/en/release_notes_core.md](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/release_notes_core.md)
- [README.md](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/README.md)
- [.gitmodules](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/.gitmodules)
- [docs/en/pytorch/training/install_guide.md](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/training/install_guide.md)
- [pretrain_gpt.py](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/pretrain_gpt.py)
- [docs/en/release_notes_llm.md](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/release_notes_llm.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
