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
reviewed_on: '2026-11-04'
coverage: frozen source delta and consumer review; unchanged files rechecked; no HCU runtime validation
sources:
- source: ascend-mindspeed
  path: README.md
  commit: c2357e9ae4689cf1791a5f258217cd256ce41ce1
  sha256: f2f0148d8dfbbfae0babf11fb869674846a2f9ad04be763b5718835ed5388378
- source: ascend-mindspeed
  path: docs/en/user-guide/install_guide.md
  commit: c2357e9ae4689cf1791a5f258217cd256ce41ce1
  sha256: fa4261944e07bf3edd1b2c0a4383b2b590ffff5deef8581d4f33c15940cddd52
- source: ascend-mindspeed
  path: docs/en/user-guide/quickstart.md
  commit: c2357e9ae4689cf1791a5f258217cd256ce41ce1
  sha256: d9353c14ad59e1d20b1b3b4f0731db4dcd55036c7de5e546797d7e7eded9887a
- source: ascend-mindspeed
  path: mindspeed/megatron_adaptor.py
  commit: c2357e9ae4689cf1791a5f258217cd256ce41ce1
  sha256: a5dff020efb4e943ee6732f68ca04dfdd90779fca3efb0b044c1b92fda54872c
- source: ascend-mindspeed
  path: docs/en/release_notes_core.md
  commit: c2357e9ae4689cf1791a5f258217cd256ce41ce1
  sha256: bf6691f27e553ebb7c05a6b454eda2cfab77b5d14e8d9072dc28aa903ae82ab6
- source: ascend-mindspeed-llm
  path: README.md
  commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
  sha256: b66e3f126c6540f87736428ee90e4317e1f1a0be6b75163651898fba552798d5
- source: ascend-mindspeed-llm
  path: .gitmodules
  commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
  sha256: fffb397bbe3cff135ea88b649129e53d551b010df5c1d411daef7c2ab8731d57
- source: ascend-mindspeed-llm
  path: docs/en/pytorch/training/install_guide.md
  commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
  sha256: eecb29d55183987e03ffe75d711e75920ede092cf53b7962931c9f6e73335895
- source: ascend-mindspeed-llm
  path: pretrain_gpt.py
  commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
  sha256: 698e53fab74c9ef3de9bf1983c0e37227307a2a625309a39d1485f3fc9636052
- source: ascend-mindspeed-llm
  path: docs/en/release_notes_llm.md
  commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
  sha256: a76914f3af86a077bbeb7bbb6c35fe98b6b243fe686ad2c9fc3bf832a8ed9588
- source: ascend-mindspeed-llm
  path: docs/en/pytorch/features/mcore/mc2.md
  commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
  sha256: 9c62e212a5fa4ff920388fa7a250b750f8fd24c61f9284d1656366db78c39ca8
- source: ascend-mindspeed-llm
  path: mindspeed_llm/training/training.py
  commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
  sha256: a316fa37426f317b02f87d792156618012f6c33b305fcf09ce925a2208d42c77
- source: ascend-mindspeed-llm
  path: mindspeed_llm/tasks/posttrain/lora/trainable.py
  commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
  sha256: 5421e381759eb098a00c2395b7d8a82679e612bf80fd8e4e55822fb197f7390c
- source: ascend-mindspeed-llm
  path: mindspeed_llm/tasks/posttrain/lora/moe/experts.py
  commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
  sha256: 6bd970880e66c6fa9ba624c015aa17c55fcf81f2739180040fb2766537847af2
retrieved_on: '2026-11-04'
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

MindSpeed 的官方安装要求配套 Ascend driver/CANN、Torch/torch_npu 及对应算子库，不能只 `pip install` 后就认为 HCU 可用。2026-11-04 检索的 MindSpeed-LLM 发布说明已列 26.2.0（2026 年 10 月）：Core `26.2.0_core_r0.12.1`、Megatron `core_v0.12.1`、Torch 2.10.0、TorchNPU 26.2.0、CANN 9.2.0、Triton-Ascend 3.6.0、FSDPTurbo 26.2.0、Python 3.12。master 行仍把部分配套写为 in development；安装指南也改用 master / Python 3.12，不能把发布矩阵直接视为任意 master 已验证组合。入口仍以 `MINDSPEED_LLM_VERSION=018` 选择特定路径，默认 `012`；本轮删除了该入口的 optimizer reload monkey-patch import，不代表默认切换到 0.18。

本轮固定独立 Core `c2357e9ae4689cf1791a5f258217cd256ce41ce1`、LLM `f5f84bbbac05be79f883b30629d7f637e6f4649e`。**LLM 父树实际锁定 `3rdparty/MindSpeed@7969e1c6b61c44fdb09d20607561824675bb216f`，URL 指向 GitCode；它不是本轮独立 GitHub Core HEAD。**同树 `3rdparty/Megatron-LM@a845aa7e12b3a117e24c2352b9e3e60bad2e3a17`、`3rdparty/FSDPTurbo@89ec36b37a854926390515c8cc89d099add77f7c` 也保持固定。新安装指南的统一子模块路线先初始化，再对 MindSpeed / FSDPTurbo 执行 `--remote` 并创建源码符号链接；后一条命令会偏离父树 gitlink，源码更新也会立即影响导入。实际部署必须另存解析后的子仓提交、链接目标和 import 路径，不能以父仓冻结证明依赖也冻结。阅读应用运行效果时沿实际依赖，不随手用最新版 Core 替换。

MC2 的本轮官方说明明确：MindSpeed-LLM 默认禁用该路径，文档要求检查 `validate_args_decorator` 中的强制关闭逻辑，单加 `--use-ascend-mc2` 不表示实际启用；部分模型还存在精度风险。MCore MoE 的 MLP 不启用 MC2，文档现明确列出 Ascend 950PR 与 950DT 尚不支持。此处是 Ascend 版本与消费者的限制，不能转换为 HCU 的融合通信能力或通用启动步骤。

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

- [MoE all-to-all overlap 与 Zero Memory](../topics/mindspeed-moe-overlap-memory.md)：不同 dispatcher 的条件、共享专家的隐式配置、重算/显存成本；关联[已有 EP 案例](../cases/mindspeed-ep-constraints.md)。
- [长序列 CP 的分片与交换](../topics/mindspeed-context-parallel.md)：ring、hybrid、KV all-gather 的 head/sequence/group 约束及 mask/RoPE。

MindSpeed-LLM：

- [ChunkLoss 的 logit 显存与归一化](../topics/mindspeed-llm-chunk-loss.md)：分序列计算、前向求局部梯度、MCore/FSDP2 入口区别，避免以节省显存为由改变 loss。
- [高可用与 replica optimizer](../topics/mindspeed-llm-high-availability.md)：状态冗余、额外内存、MindIO/MindCluster 依赖和弹性限制。

## 8. 数值、排障与恢复

MoE 卡住查参数互斥、各 rank token 数、collective 顺序、异步句柄与 expert/grouped GEMM；CP 偏差查 local/global position、mask、packed sequence 和 group；ChunkLoss 偏差查 shift、有效 token、每 chunk 分母和 grad scaling；恢复偏差查 replica/optimizer/RNG/数据与原始并行配置。先用最小合法组合建立数值基线，再添加复杂组合。

高可用 flag 不会自动安装 MindIO 或提供机器池。Ascend 的故障修复和弹性设计是参考；HCU 由任务指定的 Cluster Manager 等唯一恢复负责人执行。诊断取完整 rank 日志/栈和最后共同 step，保持旧可信 checkpoint 和回退配方；不要把“样本被跳过、worker重启了”当作训练质量恢复。

## 9. 发布、PR 与更新入口

分别查两仓 release notes、[Core Releases](https://github.com/Ascend/MindSpeed/releases)、[LLM Releases](https://github.com/Ascend/MindSpeed-LLM/releases)与 [Core PR](https://github.com/Ascend/MindSpeed/pulls)/[LLM PR](https://github.com/Ascend/MindSpeed-LLM/pulls)。源码中也有 GitCode 指向，应按实际维护入口查 Issue/PR；没有本地 PR 来源页不等于没有功能或更新。公开 roadmap/兼容表若不在已收录范围，在线查证，不能从 release 名推演。

[Core 全仓导航](../../upstream/source-map/ascend-mindspeed.md)、[LLM 全仓导航](../../upstream/source-map/ascend-mindspeed-llm.md)和两份官方原文目录提供继续阅读入口。线上问题检索要明确仓库，例如 `wiki-search-pr "alltoall overlap" --repo Ascend/MindSpeed` 或 `--repo Ascend/MindSpeed-LLM`，再追固定代码。

更新分别比较两个来源；LLM 还要核对实际 gitlink、版本选择、模型脚本、参数注册和底层 patch。共同更新本页、四篇专题与 EP 案例，不让“底座说明已更新、应用仍用旧参数”产生矛盾。

本轮保留依据：独立 Core 的 adaptor、CP/MoE 参数校验与所引文档字节不变，LLM 实际三个 gitlink 也未变，故保留 import 顺序、特性约束及跨平台边界。`training.py` 新在 PEFT 包装后调用 `enable_grouped_mlp_lora_parameters(model, LoraParallelGroupedMLP)`，针对 PEFT >=0.21 的 routed-expert adapter 参数冻结问题；补采的 helper 只遍历 `LoraParallelGroupedMLP` 并恢复 `weight1_lora_a/b`、`weight2_lora_a/b` 四个参数的 requires_grad；该模块初始化仍冻结 base weight1/weight2，不能概括为恢复所有专家或所有 PEFT 参数。LoRA 迁移须检查最终 trainable 参数集合与梯度，不能只看模型已包装。HA 文档只有措辞和链接变化，replica optimizer 文件未变，不能由本轮新发布说明推导新增容错覆盖。

2026-11-04 固定 GitHub release API 的 Core/LLM 列表均为空；这只说明该公开端点未返回 release，不说明 GitCode、源码 release notes 或分支没有发布。这里保留源码26.2发布说明与 master 当前实现的区分，不为 GitCode 发布历史补造结论。

## 固定证据与复核范围

- [README.md](https://github.com/Ascend/MindSpeed/blob/c2357e9ae4689cf1791a5f258217cd256ce41ce1/README.md)
- [docs/en/user-guide/install_guide.md](https://github.com/Ascend/MindSpeed/blob/c2357e9ae4689cf1791a5f258217cd256ce41ce1/docs/en/user-guide/install_guide.md)
- [docs/en/user-guide/quickstart.md](https://github.com/Ascend/MindSpeed/blob/c2357e9ae4689cf1791a5f258217cd256ce41ce1/docs/en/user-guide/quickstart.md)
- [mindspeed/megatron_adaptor.py](https://github.com/Ascend/MindSpeed/blob/c2357e9ae4689cf1791a5f258217cd256ce41ce1/mindspeed/megatron_adaptor.py)
- [docs/en/release_notes_core.md](https://github.com/Ascend/MindSpeed/blob/c2357e9ae4689cf1791a5f258217cd256ce41ce1/docs/en/release_notes_core.md)
- [README.md](https://github.com/Ascend/MindSpeed-LLM/blob/f5f84bbbac05be79f883b30629d7f637e6f4649e/README.md)
- [.gitmodules](https://github.com/Ascend/MindSpeed-LLM/blob/f5f84bbbac05be79f883b30629d7f637e6f4649e/.gitmodules)
- [docs/en/pytorch/training/install_guide.md](https://github.com/Ascend/MindSpeed-LLM/blob/f5f84bbbac05be79f883b30629d7f637e6f4649e/docs/en/pytorch/training/install_guide.md)
- [pretrain_gpt.py](https://github.com/Ascend/MindSpeed-LLM/blob/f5f84bbbac05be79f883b30629d7f637e6f4649e/pretrain_gpt.py)
- [docs/en/release_notes_llm.md](https://github.com/Ascend/MindSpeed-LLM/blob/f5f84bbbac05be79f883b30629d7f637e6f4649e/docs/en/release_notes_llm.md)

- [docs/en/pytorch/features/mcore/mc2.md](https://github.com/Ascend/MindSpeed-LLM/blob/f5f84bbbac05be79f883b30629d7f637e6f4649e/docs/en/pytorch/features/mcore/mc2.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
