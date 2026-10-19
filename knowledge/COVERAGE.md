---
id: knowledge-coverage
title: 官方 Wiki 内容覆盖与阅读导航
visibility: public
---

# 官方 Wiki 内容覆盖与阅读导航

所有官方仓采用相同的九项内容标准。篇幅随工程规模不同，不能用文件数量、自动采集量或一套空标题代替机制解释。详细路由由 [coverage.json](coverage.json) 保存，CI 检查来源覆盖与链接；事实准确性仍需正文复核。

九项内容：定位与边界、代码目录、安装依赖、运行与测试、数值/状态契约、调用链、性能与显存、诊断恢复、版本/特性 PR。引擎、底层库和优化参考仓至少展开两项具体机制；工具和方法仓按其实际角色解释输入、输出和使用边界。

## 工程与专题

| 工程入口 | 机制精读与导航 |
| --- | --- |
| [Megatron 官方生态：职责、完整阅读路线与版本边界](projects/megatron/knowledgebase/local/overview/overview.md) | [并行域、微批与 rank 采样](projects/megatron/knowledgebase/local/topics/parallelism.md)；[Megatron 显存生命周期：状态分片、重算、offload与Paged Stash](projects/megatron/knowledgebase/local/topics/memory.md)；[Megatron MoE：路由、dispatcher、grouped GEMM与容量控制](projects/megatron/knowledgebase/local/topics/moe.md) |
| [TorchTitan 官方工程：定位、能力边界与阅读路线](projects/torchtitan/knowledgebase/local/overview/overview.md) | [TorchTitan 并行域、容量、重算与显存生命周期](projects/torchtitan/knowledgebase/local/topics/parallelism-and-memory.md)；[TorchTitan 局部编译、融合、异步 TP 与 GraphTrainer](projects/torchtitan/knowledgebase/local/topics/compile-fusion-and-communication.md)；[TitanRL：训练生成协同、权重同步与精度边界](projects/torchtitan/knowledgebase/local/topics/titanrl.md) |
| [Transformer Engine 官方工程：定位、目录与训练调用链](projects/transformer-engine/knowledgebase/local/overview/overview.md) | [TE 低精度训练：recipe、amax、权重缓存与反向状态](projects/transformer-engine/knowledgebase/local/topics/precision-and-cache.md)；[TE 并行与显存：Userbuffers、CP、Graph 和 Offload](projects/transformer-engine/knowledgebase/local/topics/overlap-and-memory.md) |
| [cuDNN Frontend 官方工程：Graph、开放 Kernel 与训练调用链](projects/cudnn-frontend/knowledgebase/local/overview/overview.md) | [cuDNN 开放 Kernel：MoE 融合、FROST 与稀疏 Attention](projects/cudnn-frontend/knowledgebase/local/topics/open-kernel-fusions.md)；[cuDNN Flex Attention：区间 MaskPlan、反向和复用成本](projects/cudnn-frontend/knowledgebase/local/topics/flex-attention-plans.md) |
| [ms-swift：训练入口、数据契约、Megatron 与 GRPO 工程指南](projects/swift/knowledgebase/local/overview/engineering-guide.md) | [ms-swift SFT：packing、序列并行与 loss 归一化](projects/swift/knowledgebase/local/topics/sft-packing-and-loss.md)；[ms-swift Megatron GRPO：权重同步、LoRA 与显存切换](projects/swift/knowledgebase/local/topics/megatron-grpo-weight-lifecycle.md) |
| [LlamaFactory：SFT 工程、两代训练入口与显存优化指南](projects/llamafactory/knowledgebase/local/overview/engineering-guide.md) | [LlamaFactory SFT：packing、attention 与多模态位置契约](projects/llamafactory/knowledgebase/local/topics/sft-packing-and-multimodal.md)；[LlamaFactory v1：Ulysses CP、token 归一化与 chunked linear-CE](projects/llamafactory/knowledgebase/local/topics/v1-cp-and-chunk-loss.md) |
| [DeepSpeed：训练引擎、ZeRO、流水线与恢复工程指南](projects/deepspeed/knowledgebase/local/overview/engineering-guide.md) | [DeepSpeed ZeRO：分片、参数预取与 offload 生命周期](projects/deepspeed/knowledgebase/local/topics/zero-state-lifecycle.md)；[DeepSpeed Pipeline：1F1B、batch、activation 与 checkpoint](projects/deepspeed/knowledgebase/local/topics/pipeline-schedule-and-checkpoint.md) |
| [verl：RL 数据流、训练后端、动态批次与权重同步指南](projects/verl/knowledgebase/local/overview/engineering-guide.md) | [verl：动态批次的硬 token 上限、GRPO 分组与 loss 聚合](projects/verl/knowledgebase/local/topics/dynamic-batch-and-loss.md)；[verl：权重发布、LoRA、KV 显存与持久化恢复](projects/verl/knowledgebase/local/topics/weight-cache-and-checkpoint.md) |
| [Slime：Megatron–SGLang 闭环、数据并行与恢复工程指南](projects/slime/knowledgebase/local/overview/engineering-guide.md) | [Slime：packed CP、策略 loss 与 sample/token 分母](projects/slime/knowledgebase/local/topics/packed-cp-and-policy-loss.md)；[Slime：disk delta 全量基线、版本发布与联合恢复](projects/slime/knowledgebase/local/topics/delta-publication-and-recovery.md) |
| [AReaL：异步 RL、目标归一化、资源调度与恢复工程指南](projects/areal/knowledgebase/local/overview/engineering-guide.md) | [AReaL：token/response/prompt 聚合、packing 与梯度归一化](projects/areal/knowledgebase/local/topics/loss-aggregation-and-packing.md)；[AReaL：异步 admission、权重版本和事务式恢复边界](projects/areal/knowledgebase/local/topics/async-version-and-recovery.md) |
| [SGLang：RL 生成依赖的工程、运行与维护地图](projects/sglang/knowledgebase/local/overview/engineering-guide.md) | [SGLang 显存与 rollout 调度：睡眠、KV、prefix 与数值边界](projects/sglang/knowledgebase/local/topics/memory-and-scheduling.md)；[SGLang 权重同步：会话、混合 dtype 与缓存一致性](projects/sglang/knowledgebase/local/topics/weight-update.md) |
| [vLLM：RL 权重同步、生成与显存交接的工程地图](projects/vllm/knowledgebase/local/overview/engineering-guide.md) | [vLLM sleep、KV 与调度：训练共卡的内存和数值交接](projects/vllm/knowledgebase/local/topics/memory-and-scheduling.md)；[vLLM 权重传输：双端协议、逐层物化与版本提交](projects/vllm/knowledgebase/local/topics/weight-transfer.md) |
| [TraceLens 复用接口与训练补充信息](projects/tracelens/knowledgebase/local/overview/engineering-guide.md) | 入口内列出功能、命令来源、证据与使用边界 |
| [Hyperloom：训练工作流可借鉴的迭代与证据机制](projects/hyperloom/knowledgebase/local/overview/engineering-guide.md) | 入口内列出功能、命令来源、证据与使用边界 |
| [BBuf AI Infra Skills：按问题组织模型优化与 PR 证据](projects/bbuf-skills/knowledgebase/local/overview/engineering-guide.md) | 入口内列出功能、命令来源、证据与使用边界 |
| [AMD Primus：配置、后端补丁、并行与恢复](projects/primus/knowledgebase/local/overview/engineering-guide.md) | [Primus：编译区域、参数 gather 与 TE 通信重叠](projects/primus/knowledgebase/local/topics/primus-compile-overlap.md)；[Primus：按全局层选择重算、MTP 与低精度状态](projects/primus/knowledgebase/local/topics/primus-recompute-memory.md) |
| [MindSpeed 与 MindSpeed-LLM：特性底座、模型训练和恢复](projects/mindspeed/knowledgebase/local/overview/engineering-guide.md) | [MindSpeed：MoE all-to-all 重叠、共享专家与 Zero Memory](projects/mindspeed/knowledgebase/local/topics/mindspeed-moe-overlap-memory.md)；[MindSpeed：Ring、Hybrid 与 KV All-Gather 上下文并行](projects/mindspeed/knowledgebase/local/topics/mindspeed-context-parallel.md)；[MindSpeed-LLM：ChunkLoss 的 Logit 显存、梯度与入口区别](projects/mindspeed/knowledgebase/local/topics/mindspeed-llm-chunk-loss.md)；[MindSpeed-LLM：Replica Optimizer、高可用与弹性恢复](projects/mindspeed/knowledgebase/local/topics/mindspeed-llm-high-availability.md) |
| [LoongForge：两类训练入口、DP 均衡、EP 重叠与状态恢复](projects/loongforge/knowledgebase/local/overview/engineering-guide.md) | [LoongForge：变长/视觉 DP 代价模型与跨 rank 样本均衡](projects/loongforge/knowledgebase/local/topics/loongforge-dp-balance.md)；[LoongForge：跨微批 EP 重叠、延迟 wgrad 与细粒度卸载](projects/loongforge/knowledgebase/local/topics/loongforge-ep-offload.md)；[LoongForge Torch-native：异步保存完成投票与 DCP 恢复](projects/loongforge/knowledgebase/local/topics/loongforge-async-checkpoint.md)；[LoongForge：变量长 ChunkPipe 的序列分块、缓存与数值契约](projects/loongforge/knowledgebase/local/topics/loongforge-chunkpipe-variable-length.md) |
| [Megatron Bridge：配方、Provider、通信与完整训练状态](projects/bridge/knowledgebase/local/overview/bridge.md) | [Bridge：模型配方、Pipeline Provider 与 HF 权重映射](projects/bridge/knowledgebase/local/topics/bridge-provider-conversion.md)；[Bridge：DP/TP/PP/CP/EP 重叠、Graph 与显存取舍](projects/bridge/knowledgebase/local/topics/bridge-overlap-memory.md)；[Bridge：完整恢复、数据位置与容错所有权](projects/bridge/knowledgebase/local/topics/bridge-checkpoint-recovery.md) |
| [Megatron Energon：数据组织、Packing、吞吐与确定性恢复](projects/energon/knowledgebase/local/overview/energon.md) | [Energon：TaskEncoder、Packing 与确定性重放](projects/energon/knowledgebase/local/topics/energon-encoding-packing.md)；[Energon：数据空泡、Snapshot 恢复、Worker 与资源生命周期](projects/energon/knowledgebase/local/topics/energon-recovery-throughput.md) |

## 版本、证据和更新

- 每个机制先定位调用方、实现与测试，再解释收益、代价、限制和回退；安装命令遵循固定版本，不把 NVIDIA/其他平台参数直接映射为 HCU 参数。
- 固定源码 SHA、PR 原文与作者总结分别保存。源码目录清单不表示逐文件阅读，PR 原文也不等于已验证优化案例。
- 更新同仓总览、专题和相关案例；父仓锁定子仓时跟随 gitlink 复核，不用子仓最新主干替代实际依赖。
- 版本、教程或 PR 描述有差异时明确记录证据层次；配置允许、源码调用、上游测试、HCU 实测是不同结论。
- 未完成的分页、API 限流、源码差异和待复核项保留状态，不把未拿到内容写成“没有更新”。

完整标准见 [Wiki 编写规范](../docs/wiki-authoring-standard.md)，相关工作流入口见 [优化参考图谱](../docs/optimization-reference-map.md)。

HCU 仓库知识不纳入上述官方内容覆盖：使用 [HCU 外部联查](catalog/external-knowledge.json)进入大库；本仓维护对应工作流使用契约。
