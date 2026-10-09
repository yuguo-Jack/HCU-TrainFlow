# 参考工程与许可边界

本项目原始代码与原创说明使用 MIT。公开源码 Wiki 是自主组织的阅读说明和固定链接，未将第三方完整源码、文档或 Skill 原文打包进本仓。第三方项目保留自己的许可；安装/复用时检查所用提交的 LICENSE 及附加条款。

- [Hyperloom](https://github.com/yuguo-Jack/Hyperloom)：参考多 Agent 编排、证据和性能流程的组织。
- [BBuf AI-Infra-Auto-Driven-SKILLS](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS)：参考先重现后升级工具的故障分析方法和 profiler 工作流；未复制 Skill/脚本。
- [PolyArch/humanize](https://github.com/PolyArch/humanize)：参考 RLCR 的实施/独立复核、全目标对齐和失败处理；未复制其 hook 或安装全局运行时。
- [humanfia/humanize](https://github.com/humanfia/humanize)：参考独立 flow runtime 中 actor/reviewer 的结构化循环与持久状态；未把该运行时作为 TrainFlow 依赖。
- [TraceLens 上游](https://github.com/AMD-AGI/TraceLens) 与 [HCU fork](https://github.com/yuguo-Jack/TraceLens)：通过 thirdparty 锁定 fork 的提交并记录上游基准，复用完整分析模块与报告 API；主仓不重复发布其源码。
- [Megatron-LM](https://github.com/NVIDIA/Megatron-LM)、[Bridge](https://github.com/NVIDIA-NeMo/Megatron-Bridge)、[Transformer Engine](https://github.com/NVIDIA/TransformerEngine)、[Energon](https://github.com/NVIDIA/Megatron-Energon)：官方训练基准与阅读来源。
- [cuDNN Frontend](https://github.com/NVIDIA/cudnn-frontend)：官方 Graph、SDPA、开放融合 kernel 与教程的阅读来源；注意该仓 LICENSING.md 中不同组件的许可。
- [cuda-optimized-skill](https://github.com/yuguo-Jack/cuda-optimized-skill)：三个 Hygon 算子 Skill 的固定安装源，完整副本只在用户本机的忽略目录或指定安装目录。
- [HCU-Knowledge](https://github.com/yuguo-Jack/HCU-Knowledge)：可选知识检索来源；当前访问权限及材料分发条件由其所有者管理，本项目不授予访问或再分发权限。
- [Primus](https://github.com/AMD-AGI/Primus)、[MindSpeed](https://github.com/Ascend/MindSpeed)、[MindSpeed-LLM](https://github.com/Ascend/MindSpeed-LLM)、[LoongForge](https://github.com/baidu-baige/LoongForge)：优化机制参考。
- 其他来源及固定提交列于 knowledge/sources.json 和 source-lock.json。

HCU/其他产品名称属于各自所有者；本项目不表示上述组织背书。
