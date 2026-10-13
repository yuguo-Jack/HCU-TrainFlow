# 第三方工程、参考来源与许可说明

TrainFlow 原创代码和原创说明使用 [MIT](LICENSE)。本页列出直接依赖、工作流方法参考、Wiki 来源及现场联动工程；这些角色可以重叠，列入参考不表示安装其运行时或已完成 HCU 验证。

Wiki 的 `knowledge/projects/*/knowledgebase/upstream/` 保留所选上游文档、PR 描述与讨论，`knowledge/evidence/prs/` 保留 PR 原件；`local/` 是 TrainFlow 整理的阅读说明。第三方内容保留原作者、来源和适用许可，不随本项目改授 MIT。详见 [知识材料声明与许可副本](thirdparty/KNOWLEDGE-NOTICES.md)；代码或文档中的文件级声明仍须保留。

## 1. 安装与运行依赖

完整第三方 checkout 在本机忽略目录或已绑定的独立目录中，不随 TrainFlow 主仓重复分发。固定提交及安装方式见 [依赖清单](thirdparty/manifest.json)和[安装说明](thirdparty/README.md)；Python 包依赖另见 [pyproject.toml](pyproject.toml)。

| 工程 | 在 TrainFlow 中的作用 |
| --- | --- |
| [TraceLens 上游](https://github.com/AMD-AGI/TraceLens) / [HCU fork](https://github.com/yuguo-Jack/TraceLens) | 必需分析组件；复用报告、Graph、Roofline/效率、Replay、Agent 和 profiler 分析能力。锁定 HCU fork 及对应上游基准；具体支持范围见 [TraceLens 集成](docs/tracelens-analysis.md) |
| [cuda-optimized-skill](https://github.com/yuguo-Jack/cuda-optimized-skill) | 必需的三个 Hygon HIP/Triton 算子 Skill 安装源 |
| [HCU-Knowledge](https://github.com/yuguo-Jack/HCU-Knowledge) / [内部 GitLab 镜像](http://42.228.13.241:10068/dcutoolkit/deeplearing/hcu-knowledge) | 必需领域知识检索来源；访问权限和材料分发条件由其所有者管理，TrainFlow 不授予额外访问或再分发权限 |
| [KernelWiki](https://github.com/mit-han-lab/KernelWiki) | 可选 NVIDIA 算子知识、PR 和源码参考 Skill；按固定提交安装并保留其 MIT LICENSE |

## 2. 工作流方法参考

以下工程提供方法与组织思路，不作为另一套必须安装的编排运行时。性能方法的固定来源、采用范围和训练场景调整见 [性能方法与参考来源](docs/practices/performance-methods.md)。其中已登记的 Wiki 文档仍按上面的来源层规则保留。

| 工程 | 参考内容 |
| --- | --- |
| [Hyperloom 上游](https://github.com/AMD-AGI/Hyperloom) / [用户 fork](https://github.com/yuguo-Jack/Hyperloom) | 多 Agent 编排、证据刷新、热点到源码的交接、候选与最佳实现管理，以及 TraceLens 调用方式 |
| [GEAK](https://github.com/AMD-AGI/GEAK) | 端到端与算子优化衔接、真实 dispatch、逐 shape 分析、包装开销、组合回归与停滞处理 |
| [BBuf AI-Infra-Auto-Driven-SKILLS](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS) | profiler 调用映射、热点/重叠/融合分析、先保存证据再复现和升级工具的故障定位方法 |
| [hygonpilot-skills](http://42.228.13.241:10068/qianyj/hygonpilot-skills)（内部） | Torch 原生训练的框架、通信与 Inductor 分支，冷启动/稳态区分、按收益路由和最佳版本回退；独立整理方法，未导入其知识目录或打包私有源码 |
| [Multica](https://github.com/multica-ai/multica) | 负责人拆解派发、运行中消息、结果回流与投递回执；未复制其代码。其 LICENSE 含附加条件，使用时以所用版本原文为准 |
| [PolyArch/humanize](https://github.com/PolyArch/humanize) | RLCR 的实施与独立复核、全目标对齐及失败处理；未复制其 hook 或安装全局运行时 |
| [humanfia/humanize](https://github.com/humanfia/humanize) | actor/reviewer 结构化循环与持久状态；未引入该运行时 |

## 3. 官方 Wiki 与优化机制来源

下表与[知识来源清单](knowledge/sources.json)及[项目导航](knowledge/projects/README.md)对应。TraceLens、Hyperloom、BBuf 的来源已在前两节列出。各来源固定提交和网页基线见 [source-lock.json](knowledge/source-lock.json)，逐篇原始链接保留在 Wiki 中。

| 工程或官方文档 | 阅读与参考范围 |
| --- | --- |
| [Megatron-LM / Core](https://github.com/NVIDIA/Megatron-LM) | 模型、并行调度、训练状态、性能与数值契约；另联查 [Core 官方指南](https://docs.nvidia.com/megatron-core/developer-guide/latest/index.html) |
| [Megatron Bridge](https://github.com/NVIDIA-NeMo/Megatron-Bridge) | 模型转换、配方与训练接入 |
| [Megatron Energon](https://github.com/NVIDIA/Megatron-Energon) | 数据管线、packing、分片与恢复 |
| [TorchTitan](https://github.com/pytorch/torchtitan) | Torch 原生分布式训练、compile、并行与低精度优化 |
| [DeepSpeed](https://github.com/deepspeedai/DeepSpeed) | ZeRO、offload、流水、显存与训练恢复 |
| [MS-SWIFT](https://github.com/modelscope/ms-swift) | SFT、Megatron 接入、GRPO 与数据/权重生命周期 |
| [LLaMA-Factory](https://github.com/hiyouga/LlamaFactory) | 多模态 SFT、LoRA、训练入口与 loss |
| [verl](https://github.com/verl-project/verl) | RL 调度、策略更新、训推权重与 checkpoint |
| [slime](https://github.com/THUDM/slime) | rollout、Megatron 训练、权重同步与恢复 |
| [AReaL](https://github.com/areal-project/AReaL) | 异步 rollout、策略版本与训练一致性 |
| [SGLang](https://github.com/sgl-project/sglang) | rollout 后端、调度、显存、权重更新与 cache |
| [vLLM](https://github.com/vllm-project/vllm) | rollout 后端、分布式权重、sleep/wake 与 KV 生命周期 |
| [AMD Primus](https://github.com/AMD-AGI/Primus) | 训练后端及 Primus-LM 配套机制、版本锁、重算、compile 与 overlap |
| [MindSpeed](https://github.com/Ascend/MindSpeed) / [MindSpeed-LLM](https://github.com/Ascend/MindSpeed-LLM) | 并行、MoE、流水、显存机制与模型配方 |
| [LoongForge](https://github.com/baidu-baige/LoongForge) / [Loong-Megatron](https://github.com/baidu-baige/Loong-Megatron) | 模型适配、EP overlap、offload 及父工程固定子仓实现 |
| [Transformer Engine](https://github.com/NVIDIA/TransformerEngine) / [官方教程](https://docs.nvidia.com/deeplearning/transformer-engine/) | 低精度、融合算子、attention、缓存与前后向 |
| [cuDNN Frontend](https://github.com/NVIDIA/cudnn-frontend) / [官方教程](https://docs.nvidia.com/deeplearning/cudnn/latest/) | Graph、plan、SDPA、开放融合 kernel 与数值契约；组件许可见该仓 LICENSING.md 和文件级声明 |

官方工程用于语义、实现和优化思路查证，其 NVIDIA、AMD 或其他平台的能力不自动等于 HCU 分支已支持。按问题选择来源见 [优化参考图谱](docs/optimization-reference-map.md)。

## 4. HCU 现场工具与工程联动

这些工程按具体环境和问题调用，不是安装 TrainFlow 时统一部署或替换的依赖；其项目 Wiki 由 HCU-Knowledge 维护。内部仓需要本人读取权限。

| 工程范围 | 作用与现有入口 |
| --- | --- |
| [Cluster Manager](https://github.com/HYGON-AI/cluster-manager-das)，含 hcu-envcheck 等子工程 | 环境检查、筛机、故障诊断与既有容错；见[外部知识入口](knowledge/catalog/external/cluster-manager.md) |
| [HCU Train Simulator](https://github.com/HYGON-AI/hcu-train-simulator) | 模型容量、并行配置与资源预算；见[外部知识入口](knowledge/catalog/external/train-simulator.md) |
| HCU Probe、Primus Safe | 分别用于数值诊断和适用部署下的容错；见[精度诊断](docs/practices/model-accuracy-diagnosis.md)与[故障证据来源](skills/hcu-train-scale-and-stability/references/evidence-sources.md) |
| HCU 训练/推理引擎，Transformer Engine、Flash-Train、Primus Turbo 等算子库 | 现场适配、既有实现复用与修改交付；仓库、分支和归属见[库联动指南](skills/hcu-train-analyze-and-optimize/references/hcu-library-integration.md) |
| HCU RCCL、rccl-test、rocSHMEM、DeepEP、UCCL、UltraEP、MoonEP、MORI、Flux | 集合通信测试、MoE 通信及通算融合；具体入口同见[库联动指南](skills/hcu-train-analyze-and-optimize/references/hcu-library-integration.md)，不能用 AMD 上游替代 HCU 实际仓 |
| HCU rocBLAS、hipBLASLt、CK、PyTorch、AICC/DCC 与 Galaxy Runtime | 数学库调优及必要的底层定位/隔离构建；通过 HCU-Knowledge 确认实际源码、版本和权限 |

## 5. 声明与维护

- 保留的第三方材料及许可副本统一列于 [KNOWLEDGE-NOTICES.md](thirdparty/KNOWLEDGE-NOTICES.md)，包括文档专用许可和历史归属。下载、参考、集成和再分发分别核对所用版本的条件。
- 新增依赖、方法参考或 Wiki 来源时，同步本页相应条目与原有清单；保留第三方材料时同步来源链接及许可/NOTICE。具体命令和分支只在对应集成文档维护，本页不再复制一份。
- HCU 及其他产品名称属于各自所有者；本项目不表示上述组织背书。
