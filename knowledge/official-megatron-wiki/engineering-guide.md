---
id: official-megatron-wiki/engineering-guide
title: Megatron LM/Core：从训练入口到并行、MoE 与内存的工程地图
engine: megatron
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
coverage: selected implementation chain, not all models or backends
sources:
- source: nvidia-megatron-lm
  path: pretrain_gpt.py
  commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
  sha256: a21cb1d38e5aa722ccdf51d5885e077681e30f02c4699dd279127695c6ab1fa0
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
  sha256: 90d9939598927d85a9aebfa4e277de30b69a4f71a425f9db78fafddfb51d60f6
- source: nvidia-megatron-lm
  path: megatron/training/arguments.py
  commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
  sha256: a6a17536d6cd4c66f956651b519d5e96b84c088133543f99ae90798a49b8899f
- source: nvidia-megatron-lm
  path: megatron/core/distributed/distributed_data_parallel.py
  commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
  sha256: a19f8e1300dd8c7b294d1d52defe22ecb6e9c79fbcbae61a41dc5bf0de460f67
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/distrib_optimizer.py
  commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
  sha256: 892589f868b77a8f209bbcc8861521e7e71ddd46665b3dee38871aa580523389
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/token_dispatcher.py
  commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
  sha256: b26e7f458f30fce12469eff4c7fec8f2644f5de0d788537d4f765aec68ae3f53
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/paged_stash.py
  commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
  sha256: 950b8c72253b90e8b6936a5aa8532120bd8e056f6cc88807efa4c818d88d4efc
- source: nvidia-megatron-lm
  path: megatron/core/extensions/transformer_engine.py
  commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
  sha256: e320b84291f9040f0a83071a17d5c533ac41b08e036cbfd767dea22e6baf4335
- source: nvidia-megatron-lm
  path: megatron/core/pipeline_parallel/schedules.py
  commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
  sha256: 3719d850b8822e221f30472881b8802b8f88ce02167856130fae97849d1d91ee
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
  sha256: 7fc7af4f3f6fe67a6a1d7f9a7df63c5eaf245bc2cb686ff09a0adc58292daa6a
---

# Megatron LM/Core：从训练入口到并行、MoE 与内存的工程地图

## LM、Core 与生态边界

Megatron-LM 仓同时包含训练入口/应用层和 `megatron/core`。`pretrain_gpt.py` 连接模型与 batch/forward/loss，`megatron/training` 管参数、初始化、训练循环和日志，Core 提供模型层、并行 schedule、分布式 optimizer 等。Bridge 是独立仓的配方/转换入口，Energon 管数据，TE 连接高性能模块与低精度，cuDNN Frontend 等是进一步下游；版本必须分别锁定。

## 目录与调用顺序

先读 pretrain_gpt 的 model provider 和 forward_step，再追 training.training 的训练生命周期；随后根据问题进入 `core/pipeline_parallel/schedules.py`、`core/distributed/distributed_data_parallel.py`、`core/optimizer/distrib_optimizer.py`。MoE 路由/传输在 `core/transformer/moe`，TE adapter 在 `core/extensions/transformer_engine.py`，配置在 TransformerConfig 与训练 arguments 两层。

检查一个开关的完整链条：命令行解析→校验与配置转换→模块实例化→真实分支→底层调用→trace。仅 argparse 有字段或源码中出现某名字不能证明当前模型使用了它。源码地图覆盖全部路径，新模型/算子不在专题时可以直接定位。

## 构建、运行和测试入口

本地保存官方 README、core quickstart、GPT3/RL examples、user-guide/features 和部分测试指南。安装时区分 Core 包和 LM 完整训练工程，确认 PyTorch、TE、编译扩展与实际 HCU patch 的版本组合。执行采用当前 HCU 主仓适用脚本；官方配方用于核对模型和训练语义，平台变量以 HCU 实现与现场为准。

最小任务先检查模型 shape、数据/分词/seed、精度、并行拓扑和 optimizer。模型过大时只减少层数，其余模型参数保留，记录该缩模边界。运行前选对应 unit/functional tests，运行后检查 optimizer step、保存恢复和原始 loss 基线。低精度、MoE 与 fused kernels 需要局部误差及确定性/容差契约。

## 系统性能分析次序

先确认代表性 rank：每个实际 TP/PP/DP/CP/EP 组至少两个可比较 rank，并保留组成员、时间窗口和时钟对齐依据。分析 CPU 数据/launch 空泡、PP schedule、EP token 偏斜、DP 梯度同步、参数 gather、日志/保存与主机内存，不能对任意两个 rank 的 trace 直接下并行域结论。

overlap 看端到端关键路径、显存和算子被争用拖慢的程度；通信原始时长之和不等于墙钟贡献。`GPU_MAX_HW_QUEUES` 按 HCU runtime 实际版本与实验调整，不等同 NVIDIA 的 connection 环境变量。compile/graph 的编译、捕获、热身与重放时间分开记录。

## 算子、融合与效率上限

建立覆盖累计 ≥90% 端到端热点的 op/kernel 清单，其中非通信算子记录真实 shape、dtype、layout、次数、FLOPs/bytes 假设、实测时间及效率。HBM 或计算上限需使用本环境可达基准，注明算子融合导致的流量复用、缓存和并发条件。与同 shape 独立单测比较，再判断是实现落后还是训练中争用。

融合对照应沿 Core→TE/AI 编译/cuDNN 的实际调用，保持接口和数值边界；HCU 先复用 TE/Flash-Train 已有实现。GEMM 数学库调用要保存真实 sizes 与调优条件，不能把 NV tensor core 峰值直接用于 HCU roofline。独立算子可以并行分析/开发，共享设备测量和集成 loss 回归统一安排。

## MoE、Paged Stash 与数值

token_dispatcher 与 EP routing 决定各 rank workload、传输和 grouped GEMM。paged_stash 管特定 saved tensors 的页式存储/恢复和调度，并非通用“把所有激活搬到 CPU”。`on_save_for_backward` 对带 grouped_tensor_scale_inv 等状态的张量走特殊路径；capture/captured、PP schedule、pack/unpack stream 和 buffer capacity 共同决定行为。

需要跟踪真实 token skew、CUDA/host stash 容量、page metadata、overflow/host spill 和重跑策略；局部 copy 正确仍不代表整个 backward 生命周期正确。新案例 PR #7897 展示了 description 与最终实现不一致的例子：初稿提可配置 launch，最终按设备选择固定值，必须读最终 diff/head。

## 诊断、版本和更新

卡住先定位最后推进的 rank/phase，再检查 collective 顺序、PP P2P、数据加载与异步事件。OOM 分别记录 allocated/reserved、临时 allgather、低精度权重缓存、optimizer、stash 与 checkpoint 高水位；梯度异常沿 loss mask/reduction/scale→模块→kernel 追踪。

官方 dev、main、release 和 HCU patch 分支可能差异很大；PR merged 还要核对目标 branch 和运行依赖。参考 AMD Primus、华为 MindSpeed/MindSpeed-LLM、百度 LoongForge 时记录依赖、算法前提和采用/退役条件；官方合入等价改进后再经验证退役本地补丁。路线图只是候选方向，不能自动视为已提供能力。

## 固定源码与符号导航

| 文件 | 本轮源码中可追查的入口（非全部符号） |
| --- | --- |
| [pretrain_gpt.py](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/pretrain_gpt.py) | `get_batch`, `loss_func`, `forward_step`, `is_dataset_built_on_rank`, `core_gpt_dataset_config_from_args`, `train_valid_test_datasets_provider`, `get_embedding_ranks` |
| [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/megatron/training/training.py) | `set_startup_timestamps`, `destroy_global_state`, `print_datetime`, `update_seqlen_stats_from_cu_seqlens`, `set_seqlen_stats_in_iteration`, `consume_seqlen_stats_in_iteration`, `num_floating_point_operations`, `get_start_time_from_progress_log` |
| [megatron/training/arguments.py](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/megatron/training/arguments.py) | `add_megatron_arguments`, `parse_and_validate_args`, `parse_args`, `validate_model_config_args_from_heterogeneous_config`, `no_rope_freq_type`, `compress_ratios_type`, `moe_freq_type`, `la_freq_type` |
| [megatron/core/distributed/distributed_data_parallel.py](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/megatron/core/distributed/distributed_data_parallel.py) | `DistributedDataParallel`, `enable_forward_pre_hook`, `disable_forward_pre_hook`, `no_sync`, `start_param_sync`, `reset_param_sync_dispatch_state`, `start_grad_sync`, `finish_grad_sync` |
| [megatron/core/optimizer/distrib_optimizer.py](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/megatron/core/optimizer/distrib_optimizer.py) | `get_legacy_grad_dtypes`, `Range`, `DistributedOptimizer`, `normalize`, `compute_full_param_layout`, `get_grad_stats_parallel_group`, `optimizer_state_keys`, `state_dict` |
| [megatron/core/transformer/moe/token_dispatcher.py](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/megatron/core/transformer/moe/token_dispatcher.py) | `MoETokenDispatcher`, `MoEAllGatherTokenDispatcher`, `MoEAlltoAllTokenDispatcher`, `nccl_ep_release_context`, `MoEFlexTokenDispatcher`, `dispatch_preprocess`, `token_dispatch`, `dispatch_postprocess` |
| [megatron/core/transformer/moe/paged_stash.py](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/megatron/core/transformer/moe/paged_stash.py) | `PagedStashBuffer`, `PagedTensor`, `PipelinePreScheduleFunction`, `PipelinePostScheduleFunction`, `PagedStashManager`, `PagedStashContext`, `paged_stash_group_start`, `get_paged_stash_context` |
| [megatron/core/extensions/transformer_engine.py](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/megatron/core/extensions/transformer_engine.py) | `TransformerEngineConfigType`, `TEQuantizationRecipe`, `TEQuantizationParams`, `condition_init_method`, `split_te_layernorm_column_parallel_linear`, `TENorm`, `TELinear`, `TELayerNormColumnParallelLinear` |
| [megatron/core/pipeline_parallel/schedules.py](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/megatron/core/pipeline_parallel/schedules.py) | `get_forward_backward_func`, `deallocate_output_tensor`, `custom_backward`, `get_tensor_device`, `forward_step_calc_loss`, `forward_step`, `backward_step`, `backward_step_multimodule` |
| [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/megatron/core/transformer/transformer_config.py) | `TransformerConfig`, `MLATransformerConfig`, `from_config` |

## 教程、PR 与继续搜索

- [全仓目录和固定文件入口](../source-maps/nvidia-megatron-lm.md)：没有本地专题时按模块继续读源码。
- [上游教程原文目录](../upstream-docs/nvidia-megatron-lm/)：保留来源内容，链接相对位置以原站为准。
- [PR #6878：Mxfp8 refit bounded memory](../prs/NVIDIA--Megatron-LM/PR-6878.md)：正文、review、diff 与 head/base 源码。
- [PR #7534：[dev] docs: add combined 1F1B MoE A2A overlap guide](../prs/NVIDIA--Megatron-LM/PR-7534.md)：正文、review、diff 与 head/base 源码。
- [PR #7897：Widen paged-stash copy/pop kernel launches](../prs/NVIDIA--Megatron-LM/PR-7897.md)：正文、review、diff 与 head/base 源码。
- [PR #7942：Declare the residual on the pre-MLP norm of the fused MLA spec](../prs/NVIDIA--Megatron-LM/PR-7942.md)：正文、review、diff 与 head/base 源码。

检索示例：`wiki-search "关键符号或问题" --engine megatron`。本地结果不足，使用 `wiki-search-pr "简短英文问题词" --engine megatron`，再 `wiki-pr OWNER/REPO NUMBER`、`wiki-code OWNER/REPO FULL_SHA PATH` 追实际调用者、被调底层库和测试。普通查阅只写私有缓存。

## 更新和验收边界

运行 `wiki-update PROJECT nvidia-megatron-lm` 检查完整目录、新文档、PR 讨论与已监测源码；分页或网络失败必须续采。变更后联动本页、同仓专题/案例、调用方与依赖；源码已 merge、软件已发布、HCU 已适配和当前任务已验证分别登记。本页为选定实现的代码阅读和操作建议，没有在 HCU 执行上述测试，也未覆盖所有模型。实际任务的版本、性能、显存、失败尝试和阶段 loss 记录进入私有经验 Wiki。
