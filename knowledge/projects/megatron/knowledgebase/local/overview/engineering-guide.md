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
reviewed_on: '2026-11-04'
coverage: frozen source delta and consumer review; unchanged files rechecked; no HCU runtime validation
sources:
- source: nvidia-megatron-lm
  path: pretrain_gpt.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 37bff81772b4cff0548d94876e9699a66276af578b3902c5bef13fbb5b7af612
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 1cfba3a404c97febc4c2e40895467372e6ab540006dc6a6e22fbc547087a5b75
- source: nvidia-megatron-lm
  path: megatron/training/arguments.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 91ec8ceb30b9af6d1bad58256e965e5b1f6cbf70ef120f450b09e570b2f44cce
- source: nvidia-megatron-lm
  path: megatron/core/distributed/distributed_data_parallel.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: e270ae12b06c1b93d0340d6df43f0d6dc1372ed9592663533518a35d23197137
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/distrib_optimizer.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 748f6f665109a99ae9b13cd90c6cb179afb855906bdf75f1442064a0c11e20a9
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/token_dispatcher.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: ca4155cb32939839a14219cb14c38fa0abd0b28bdfe9546a383d5f3039c5608b
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/paged_stash.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: c120b2e7ce96baf76be69b5a3a7944a584c406fd4c093c56e71b5be6e0313e53
- source: nvidia-megatron-lm
  path: megatron/core/extensions/transformer_engine.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: ab48dd0b062fa44b816205ae9e8491a8785e1c934d2b88cefb3ee0768b6df7b1
- source: nvidia-megatron-lm
  path: megatron/core/pipeline_parallel/schedules.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 69c5f81b5ec764d5feb1812d152ff592af5291b6b577061841a8b140798cfdd0
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 39f34cb0f9005ad53b4d318346a7b6bbb88931a19d5f868805a42e83dd1eece6
- source: nvidia-megatron-lm
  path: megatron/training/argument_utils.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 3a71f13e18b312c4cf2e8a6830e225dfd855d9836b01f1a183a9c11af114d622
- source: nvidia-megatron-lm
  path: megatron/training/config/container.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 4965eeb1ad25b950348a29557799fd920f1c2207544c83992eb22e537a8758b2
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/ops/paged_stash.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: dba859b82cd90179fc8e45bf3c55ecef10a7432a6d968df4b30c66768efd6de4
- source: nvidia-megatron-lm
  path: megatron/training/config/dataset_config.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: ad183c58c35e91b065577d0f3fdb5ef89fbf6282a4e6de1fad1950926c8b030d
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/optimizer_config.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: f83b46a8a901bb7c792076544e2fefda3b76830ef2d971ecb976f0ac557fbc67
retrieved_on: '2026-11-04'
---

# Megatron LM/Core：从训练入口到并行、MoE 与内存的工程地图

## LM、Core 与生态边界

Megatron-LM 仓同时包含训练入口/应用层和 `megatron/core`。`pretrain_gpt.py` 连接模型与 batch/forward/loss，`megatron/training` 管参数、初始化、训练循环和日志，Core 提供模型层、并行 schedule、分布式 optimizer 等。Bridge 是独立仓的配方/转换入口，Energon 管数据，TE 连接高性能模块与低精度，cuDNN Frontend 等是进一步下游；版本必须分别锁定。

## 目录与调用顺序

先读 `pretrain_gpt.py` 的 `model_provider`/`forward_step`，再追 training.training 的训练生命周期；随后根据问题进入 `core/pipeline_parallel/schedules.py`、`core/distributed/distributed_data_parallel.py`、`core/optimizer/distrib_optimizer.py`。MoE 路由/传输在 `core/transformer/moe`，TE adapter 在 `core/extensions/transformer_engine.py`，配置在 TransformerConfig 与训练 arguments 两层。

检查一个开关的完整链条：命令行解析→校验与配置转换→模块实例化→真实分支→底层调用→trace。仅 argparse 有字段或源码中出现某名字不能证明当前模型使用了它。源码地图覆盖全部路径，新模型/算子不在专题时可以直接定位。

## 构建、运行和测试入口

本地保存官方 README、core quickstart、GPT3/RL examples、user-guide/features 和部分测试指南。安装时区分 Core 包和 LM 完整训练工程，确认 PyTorch、TE、编译扩展与实际 HCU patch 的版本组合。执行采用当前 HCU 主仓适用脚本；官方配方用于核对模型和训练语义，平台变量以 HCU 实现与现场为准。

最小任务先检查模型 shape、数据/分词/seed、精度、并行拓扑和 optimizer。先评估完整模型的可行并行布局与容量；确需代理时优先只减少层数，保留其余模型参数并记录边界。运行前选对应 unit/functional tests，运行后检查 optimizer step、保存恢复和原始 loss 基线。低精度、MoE 与 fused kernels 需要局部误差及确定性/容差契约。

## 系统性能分析次序

先确认代表性 rank：每个实际 TP/PP/DP/CP/EP 组至少两个可比较 rank，并保留组成员、时间窗口和时钟对齐依据。分析 CPU 数据/launch 空泡、PP schedule、EP token 偏斜、DP 梯度同步、参数 gather、日志/保存与主机内存，不能对任意两个 rank 的 trace 直接下并行域结论。

overlap 看端到端关键路径、显存和算子被争用拖慢的程度；通信原始时长之和不等于墙钟贡献。`GPU_MAX_HW_QUEUES` 按 HCU runtime 实际版本与实验调整，不等同 NVIDIA 的 connection 环境变量。compile/graph 的编译、捕获、热身与重放时间分开记录。

## 算子、融合与效率上限

建立覆盖累计 ≥90% 端到端热点的 op/kernel 清单，其中非通信算子记录真实 shape、dtype、layout、次数、FLOPs/bytes 假设、实测时间及效率。HBM 或计算上限需使用本环境可达基准，注明算子融合导致的流量复用、缓存和并发条件。与同 shape 独立单测比较，再判断是实现落后还是训练中争用。

融合对照应沿 Core→TE/AI 编译/cuDNN 的实际调用，保持接口和数值边界；HCU 先复用 TE/Flash-Train 已有实现。GEMM 数学库调用要保存真实 sizes 与调优条件，不能把 NV tensor core 峰值直接用于 HCU roofline。独立算子可以并行分析/开发，共享设备测量和集成 loss 回归统一安排。

## MoE、Paged Stash 与数值

token_dispatcher 与 EP routing 决定各 rank workload、传输和 grouped GEMM。paged_stash 管特定 saved tensors 的页式存储/恢复和调度，并非通用“把所有激活搬到 CPU”。`on_save_for_backward` 通过 TE GroupedTensor 标记识别受管张量，并在接管前排除 CheckpointWithoutOutput 所拥有的 storage；capture/captured、PP schedule、pack/unpack stream 和 buffer capacity 共同决定行为。

需要跟踪真实 token skew、设备/host stash 容量、page metadata、overflow/host spill 和重跑策略；局部 copy 正确仍不代表整个 backward 生命周期正确。新案例 PR #7897 展示了 description 与最终实现不一致的例子：初稿提可配置 launch，最终按设备选择固定值，必须读最终 diff/head。

## 诊断、版本和更新

卡住先定位最后推进的 rank/phase，再检查 collective 顺序、PP P2P、数据加载与异步事件。OOM 分别记录 allocated/reserved、临时 allgather、低精度权重缓存、optimizer、stash 与 checkpoint 高水位；梯度异常沿 loss mask/reduction/scale→模块→kernel 追踪。

官方 dev、main、release 和 HCU patch 分支可能差异很大；PR merged 还要核对目标 branch 和运行依赖。参考 AMD Primus、华为 MindSpeed/MindSpeed-LLM、百度 LoongForge 时记录依赖、算法前提和采用/退役条件；官方合入等价改进后再经验证退役本地补丁。路线图只是候选方向，不能自动视为已提供能力。

## 当前主干的三类状态边界

配置容器定稿、`TrainState` 运行进度与 checkpoint 持久化是三层状态。当前循环从 `get_train_state()` 读取 iteration、consumed/skipped samples、验证进度与累计 FLOPs；旧 `args` 上同名字段不再是可靠消费点。恢复后的吞吐使用独立的 resume 基准，见[训练/loss](../topics/training-and-loss.md)与[保存恢复](../topics/checkpoint.md)。

新 GTP 布局将权重分片/复制和独立序列分配分开；mHC 的部分 PP/VPP 支持已落到 P2P 残差宽度，不能继续把 PP>1 一概判为不支持，也不能推成所有 mHC/MTP/EP-overlap 组合可用。MoonEP 虚拟专家、梯度池卸载与低精度缓存各有所有权和互斥条件，详见[并行](../topics/parallelism.md)、[MoE](../topics/moe.md)与[显存](../topics/memory.md)。

本轮主干将 batch/horizon、optimizer/scheduler 和 GPT 数据的消费继续迁入配置 section；解析层删除旧检查不等于取消约束，应追 `PretrainConfigContainer.validate/finalize` 与 `OptimizerConfig.validate_run/validate_model`。FGO 新固定 pinned buffer、EP overlap 的受限 full recompute，以及 NCCL EP 的 packed-token 上界分别改变容量与调度条件，详见专题；这些 CUDA/TE 代码均未在 HCU 执行。原性能分析次序、算子覆盖和所有权分账继续适用，因为新机制仍通过这些模块/streams/buffers 形成关键路径。

## 本轮接口复核与阅读路线

当前 main 将训练配置组织为 `ConfigContainerBase`/`PretrainConfigContainer` 等 typed 容器，`argument_utils.py` 连接 CLI、dataclass 和配置转换，`training.py` 从 `cfg` 消费参数。检查部署版本的解析、校验、转换与实际构造，不能只在旧 `args` 或某篇教程找到同名参数。这里是官方 main 行为，不要求 HCU 较旧 release 改成同一接口。

HCU 适配仓还可能通过独立补丁包、submodule 或插件连接上游：将 HCU 父仓、各 gitlink/基础包、TE/通信/算子扩展分别固定，检查被替换符号与实际 import 路径。若源码迁移了模块，或活跃分支撤回旧优化，应重新检查能力及回退路径；历史案例仍可解释思想，但不能据此继续执行已经删除的开关。

| 内容维度 | 详细入口 |
| --- | --- |
| 工程职责和完整目录 | [总览](overview.md)、[源码地图](source-map.md) |
| 安装、运行、模型/数据与测试 | [构建运行测试](../guides/build-run-test.md)、[训练/loss](../topics/training-and-loss.md) |
| 并行、显存与通信实现 | [并行](../topics/parallelism.md)、[overlap](../topics/overlap.md)、[显存](../topics/memory.md)、[MoE](../topics/moe.md) |
| TE 调用和算子数值契约 | [Core→TE](../topics/transformer-engine.md)、[MLA 案例](../cases/mla-residual-norm.md) |
| 性能采样与诊断 | [profiling](../topics/profiling.md)、[checkpoint/恢复](../topics/checkpoint.md) |
| Release/roadmap/PR 与更新 | [总览版本入口](overview.md)、本页 PR 与检索入口 |

## 固定源码与符号导航

| 文件 | 本轮源码中可追查的入口（非全部符号） |
| --- | --- |
| [pretrain_gpt.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/pretrain_gpt.py) | `get_batch`, `loss_func`, `forward_step`, `is_dataset_built_on_rank`, `core_gpt_dataset_config_from_args`, `train_valid_test_datasets_provider`, `get_embedding_ranks` |
| [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/training/training.py) | `set_startup_timestamps`, `destroy_global_state`, `print_datetime`, `update_seqlen_stats_from_cu_seqlens`, `set_seqlen_stats_in_iteration`, `consume_seqlen_stats_in_iteration`, `num_floating_point_operations`, `_get_start_time_from_progress_log`, `train_step`, `is_batch_size_transition` |
| [megatron/training/arguments.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/training/arguments.py) | `add_megatron_arguments`, `parse_and_validate_args`, `parse_args`, `validate_model_config_args_from_heterogeneous_config`, `no_rope_freq_type`, `compress_ratios_type`, `moe_freq_type`, `la_freq_type` |
| [megatron/core/distributed/distributed_data_parallel.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/distributed/distributed_data_parallel.py) | `DistributedDataParallel`, `enable_forward_pre_hook`, `disable_forward_pre_hook`, `no_sync`, `start_param_sync`, `reset_param_sync_dispatch_state`, `start_grad_sync`, `finish_grad_sync` |
| [megatron/core/optimizer/distrib_optimizer.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/optimizer/distrib_optimizer.py) | `get_legacy_grad_dtypes`, `Range`, `DistributedOptimizer`, `normalize`, `compute_full_param_layout`, `get_grad_stats_parallel_group`, `optimizer_state_keys`, `state_dict` |
| [megatron/core/transformer/moe/token_dispatcher.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/transformer/moe/token_dispatcher.py) | `MoETokenDispatcher`, `MoEAllGatherTokenDispatcher`, `MoEAlltoAllTokenDispatcher`, `nccl_ep_release_context`, `MoEFlexTokenDispatcher`, `dispatch_preprocess`, `token_dispatch`, `dispatch_postprocess` |
| [megatron/core/transformer/moe/paged_stash.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/transformer/moe/paged_stash.py) | `PagedStashBuffer`, `PagedTensor`, `PipelinePreScheduleFunction`, `PipelinePostScheduleFunction`, `PagedStashManager`, `PagedStashContext`, `paged_stash_group_start`, `get_paged_stash_context` |
| [megatron/core/extensions/transformer_engine.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/extensions/transformer_engine.py) | `TransformerEngineConfigType`, `TEQuantizationRecipe`, `TEQuantizationParams`, `condition_init_method`, `split_te_layernorm_column_parallel_linear`, `TENorm`, `TELinear`, `TELayerNormColumnParallelLinear` |
| [megatron/core/pipeline_parallel/schedules.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/pipeline_parallel/schedules.py) | `get_forward_backward_func`, `deallocate_output_tensor`, `custom_backward`, `get_tensor_device`, `forward_step_calc_loss`, `forward_step`, `backward_step`, `backward_step_multimodule` |
| [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/transformer/transformer_config.py) | `TransformerConfig`, `MLATransformerConfig`, `from_config` |

## 教程、PR 与继续搜索

- [全仓目录和固定文件入口](../../upstream/source-map/nvidia-megatron-lm.md)：没有本地专题时按模块继续读源码。
- [上游教程原文目录](../../upstream/docs/nvidia-megatron-lm)：保留来源内容，链接相对位置以原站为准。
- [PR #6878：Mxfp8 refit bounded memory](../../upstream/prs/NVIDIA--Megatron-LM/PR-6878.md)：正文、review、diff 与 head/base 源码。
- [PR #7534：[dev] docs: add combined 1F1B MoE A2A overlap guide](../../upstream/prs/NVIDIA--Megatron-LM/PR-7534.md)：正文、review、diff 与 head/base 源码。
- [PR #7897：Widen paged-stash copy/pop kernel launches](../../upstream/prs/NVIDIA--Megatron-LM/PR-7897.md)：正文、review、diff 与 head/base 源码。
- [PR #7942：Declare the residual on the pre-MLP norm of the fused MLA spec](../../upstream/prs/NVIDIA--Megatron-LM/PR-7942.md)：正文、review、diff 与 head/base 源码。

检索示例：`wiki-search "关键符号或问题" --engine megatron`。本地结果不足，使用 `wiki-search-pr "简短英文问题词" --engine megatron`，再 `wiki-pr OWNER/REPO NUMBER`、`wiki-code OWNER/REPO FULL_SHA PATH` 追实际调用者、被调底层库和测试。普通查阅只写私有缓存。

## 更新和验收边界

运行 `wiki-update PROJECT nvidia-megatron-lm` 检查完整目录、新文档、PR 讨论与已监测源码；分页或网络失败必须续采。变更后联动本页、同仓专题/案例、调用方与依赖；源码已 merge、软件已发布、HCU 已适配和当前任务已验证分别登记。本页为选定实现的代码阅读和操作建议，没有在 HCU 执行上述测试，也未覆盖所有模型。实际任务的版本、性能、显存、失败尝试和阶段 loss 记录进入私有经验 Wiki。