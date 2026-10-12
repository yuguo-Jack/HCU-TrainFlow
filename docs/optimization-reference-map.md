# 优化参考与修改归属

按当前瓶颈选择参考工程，不按厂商或引擎名称排固定优先级。先读实际 HCU 调用链和配方，再比较官方实现、教程与 PR；同名机制必须核对版本、数值和运行条件。无需为一次优化读完全部工程。

## 从问题选择参考

| 问题 | Wiki 入口 | 重点比较 |
| --- | --- | --- |
| 并行切分、流水调度、MoE 与训练状态 | [Megatron LM/Core](../knowledge/official-megatron-wiki/overview.md)、[Megatron Bridge](../knowledge/official-megatron-wiki/bridge.md) | TP/PP/CP/EP/DP、microbatch、模型配方、参数/优化器/激活生命周期 |
| PyTorch 原生训练、FSDP、compile 与组合优化 | [TorchTitan](../knowledge/official-torchtitan-wiki/overview.md)、[DeepSpeed](../knowledge/engines/deepspeed.md) | 分片/预取、ZeRO/offload、编译边界、通信重叠及实际内存峰值；DeepSpeed 同样是跨引擎机制参考 |
| 激进的 Megatron 优化和新模型实现 | [AMD Primus](../knowledge/ecosystem/primus.md)、[MindSpeed / MindSpeed-LLM](../knowledge/ecosystem/mindspeed.md)、[百度 LoongForge](../knowledge/ecosystem/loongforge.md) | 调度、overlap、重算/offload、融合及补丁基线；借鉴算法，核对设备专用实现 |
| SFT 数据、packing、LoRA、并行与吞吐 | [MS-SWIFT](../knowledge/engines/swift.md)、[LLaMA-Factory](../knowledge/engines/llamafactory.md)、[DeepSpeed](../knowledge/engines/deepspeed.md) | mask/有效 token、batch 语义、训练后端与显存；速度比较保留学习目标 |
| RL 训练生成协同、权重传输与恢复 | [verl](../knowledge/engines/verl.md)、[slime](../knowledge/engines/slime.md)、[AReaL](../knowledge/engines/areal.md)、[TitanRL](../knowledge/official-torchtitan-wiki/titanrl.md) | policy version、采样/更新比、角色共卡/分离、同步窗口及恢复语义 |
| rollout 吞吐、KV cache 与训推切换 | [SGLang](../knowledge/engines/sglang.md)、[vLLM](../knowledge/engines/vllm.md) | 实际 backend 的 sleep、权重加载、调度和显存；不能将推理吞吐直接当训练收益 |
| 低精度、融合、Attention 与图执行 | [Transformer Engine](../knowledge/official-transformer-engine-wiki/overview.md)、[cuDNN Frontend](../knowledge/official-cudnn-frontend-wiki/overview.md) | 前后向、累积精度、缓存失效、workspace 与 dispatch，结合 HCU 已有算子/通信库 |
| 数据供给、确定性与恢复 | [Energon](../knowledge/official-megatron-wiki/energon.md)及目标引擎数据层 | worker 分片、混合、packing、预取及 checkpoint 后的数据连续性 |

每个入口包含官方仓库、教程、固定源码与 PR 路线。共同内容标准见 [Wiki 组织规范](wiki-authoring-standard.md)，全库入口见 [Wiki](../knowledge/README.md)。未收录的机制继续用 `wiki-search-pr` 查官方 PR，再读最终实现、调用者与测试；发布、roadmap、open PR 与当前可用能力分别判断。

## HCU 修改并不限于算子

根因在哪层，就在对应 HCU 工程修复：训练引擎负责配方、调度和接入；TE / Flash-Train / Primus Turbo 负责各自算子；RCCL、rocSHMEM、DeepEP 等负责通信实现；必要时还可涉及数学库、PyTorch、编译器和 Runtime。具体仓、分支选择和验证要求见 [HCU 库联动与修改归属](../skills/hcu-train-analyze-and-optimize/references/hcu-library-integration.md)。

例如 **HCU RCCL** 的已登记源码在 [DTK GitLab / dcutoolkit/deeplearing/rccl](http://42.228.13.241:20080/dcutoolkit/deeplearing/rccl)，使用前通过 HCU-Knowledge 核对当前适用分支；[rccl-test](http://42.228.13.241:20080/dcutoolkit/driverruntime/rccl-test) 是测试工程，AMD/ROCm RCCL 是外部参考，三者不能混用。内部链接需要对应账号权限，不将内部源码复制进公共 Wiki。

修改前确认部署版本、实际加载库与调用关系；采用任务独立 checkout 和构建目录，保留基线与回退。完成库级、模型集成及受影响的阶段数值验证后，向真实归属仓交付 PR。参考工程中的机制不是新环境默认开关，候选以端到端收益和训练质量验收。
