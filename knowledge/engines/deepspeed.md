---
id: engines/deepspeed
title: DeepSpeed：引擎、ZeRO 生命周期与训练优化
engine: deepspeed
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
- source: deepspeedai-deepspeed
  path: deepspeed/__init__.py
  commit: bc1ad320a9afb516797577924a9983c6d7cd6793
  sha256: 6c7e11d078f34d8b2de619eeccca5931aeddea53fe8852896fcf0bfb747bde04
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage_1_and_2.py
  commit: bc1ad320a9afb516797577924a9983c6d7cd6793
  sha256: aa9556509f8249b9e82f6208297311c69e25eb6e560e64c7670fe3bb928436b3
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage3.py
  commit: bc1ad320a9afb516797577924a9983c6d7cd6793
  sha256: af0f6e3aa14bcdd5f67074e3d13c012760b73eb0a3a5ae19d2c5880bb9bf6a12
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/config.py
  commit: bc1ad320a9afb516797577924a9983c6d7cd6793
  sha256: cf8beb53835f192afdf5a0c8a4b5bbf3fb09d1fdc767a0f46f66b1cdf38c650a
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/engine.py
  commit: bc1ad320a9afb516797577924a9983c6d7cd6793
  sha256: 224d79de472f567b29d4bf9490d6c6d4a42c0a46dcca186c71545648a04f1ca3
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/pipe/engine.py
  commit: bc1ad320a9afb516797577924a9983c6d7cd6793
  sha256: 211edb569ad0dc1c1b830c818a0ea15b64e22986c4840468af73304d825c8ae3
- source: deepspeedai-deepspeed
  path: deepspeed/launcher/runner.py
  commit: bc1ad320a9afb516797577924a9983c6d7cd6793
  sha256: 956d554ea5c9b142ab4bae47c8317cce11f7b23748e09849b7876072c66cf9a0
---

# DeepSpeed：引擎、ZeRO 生命周期与训练优化

## 定位与执行链

`deepspeed.initialize` 建立训练 engine、optimizer、dataloader 和 scheduler 的组合。进入 `DeepSpeedEngine` 后，forward、梯度累积、backward、step 与配置的 ZeRO stage 协作。先区分普通 engine 和 `PipelineEngine`：后者通过自己的 `train_batch` / pipeline schedule 推进，不能将普通 engine 的调用方式机械套过去。

源码目录按层读：`deepspeed/launcher` 处理资源/hostfile/进程启动；`runtime/engine.py` 管生命周期；`runtime/zero` 管状态分片、通信和 offload；`runtime/pipe` 管 PP；`ops` 是编译扩展与设备实现。模型和数据往往由外部工程提供，DeepSpeed 自身的初始化成功并不证明模型 recipe 兼容。

## 安装、运行和测试入口

先查固定提交的 README、`pyproject.toml`/`setup.py` 和 op builder，再采用 HCU 分支已有安装方式；扩展预编译和运行时 JIT 要分别记录实际产物、编译器和目标架构。将解析后的 DeepSpeed JSON 与模型脚本一并锁定，特别检查 batch、梯度累积、precision、ZeRO 和 optimizer 配置。官方完整教程保存在本仓 upstream-docs 对应目录，包括 ZeRO、offload 与通信优化。

首轮验证依次覆盖导入/扩展装载、forward/backward、optimizer step、保存/恢复、所用 stage 的分布式测试；不能用 CPU mock 代替 device op。用于 pipeline 的测试需真实覆盖 microbatch 和进程组。运行入口和测试命令以目标分支 help/CI 为准，不在 Wiki 中假设某组 NVIDIA 构建变量适用于 HCU。

## 配置与内存账本

`DeepSpeedZeroConfig` 明确 stage 1/2/3 分别扩展 optimizer、gradient、parameter 分片。`offload_param` 只对 stage 3 有效，`offload_optimizer` 对 1/2/3 有效。bucket size 的单位是元素，做显存预估时乘对应 dtype 字节数，并计入并行存活的 buffer。`param_persistence_threshold` 减少分片与小消息的代价是常驻显存增大。

`overlap_comm` 使用 validator 决定动态默认值，不能把 None 解读为关闭。stage3 的 prefetch、max live parameters、reuse distance 共同影响峰值驻留；调小显存不能只看训练中 allocated，还要测 allgather、checkpoint、生成切换和重入时峰值。optimizer offload 又引入 CPU RAM、pinned memory、NUMA 和 D2H/H2D 带宽。

## 优化与正确性

从 step trace 分离参数 gather、梯度 reduce、CPU optimizer、offload copy 和计算。通信 overlap 必须核对生产者事件、消费者流、bucket 复用及 allocator 生命周期。新 PR #8632 正是这类故障：关闭 overlap 也不代表不存在异步 offload 的所有权风险。对每次候选保留无 offload/无 overlap 对照，但不要移除已有必要同步来换取表面吞吐。

缩小 bucket 可能减少临时显存，也可能增加消息和启动开销；增大 batch 可能改善算子效率，也会改变训练语义。将系统调参、数值配置变化和算子实现变更分开记录。稳定阶段比较 loss/梯度范数及训练进度；长时 loss 不是每个微调迭代的前置动作。

## 排障顺序

卡住先收集各 rank Python/native stack、最近 collective、分片状态和异步拷贝进度；NaN 先核对输入/缩放/梯度归约与 offload 存储生命周期，再检查 fused optimizer。恢复失败检查 optimizer/master weights、分片拓扑和 checkpoint 格式。配置已弃用的 elastic checkpoint 不应当成当前通用恢复方案；遵循所用版本的 Universal Checkpointing 文档。

## 固定源码与符号导航

| 文件 | 本轮源码中可追查的入口（非全部符号） |
| --- | --- |
| [deepspeed/__init__.py](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/deepspeed/__init__.py) | `set_optimizer_flags`, `resolve_per_head_muon_after_sharding`, `initialize`, `add_config_arguments`, `default_inference_config`, `init_inference`, `tp_model_init` |
| [deepspeed/runtime/zero/stage_1_and_2.py](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/deepspeed/runtime/zero/stage_1_and_2.py) | `input`, `split_half_float_double`, `isclose`, `lcm`, `get_alignment_padding`, `print_rank_msg`, `IPGBucket`, `DeepSpeedZeroOptimizer` |
| [deepspeed/runtime/zero/stage3.py](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/deepspeed/runtime/zero/stage3.py) | `print_rank_0`, `input`, `isclose`, `lcm`, `move_to_cpu`, `unwrap_model_for_generation`, `IPGBucketZ3`, `DeepSpeedZeroOptimizer_Stage3` |
| [deepspeed/runtime/zero/config.py](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/deepspeed/runtime/zero/config.py) | `read_zero_config_deprecated`, `get_zero_config`, `ZeroStageEnum`, `DeepSpeedZeroConfig`, `overlap_comm_valid`, `compute_grad_norm_valid`, `offload_ratio_check`, `elastic_checkpoint_deprecated` |
| [deepspeed/runtime/engine.py](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/deepspeed/runtime/engine.py) | `split_half_float_double_sparse`, `EngineTimers`, `DeepSpeedEngine`, `active_timers`, `supported`, `new_state`, `register_current_graph`, `unregister` |
| [deepspeed/runtime/pipe/engine.py](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/deepspeed/runtime/pipe/engine.py) | `is_even`, `PipelineEngine`, `set_has_attention_mask`, `reset_activation_shape`, `train_batch`, `eval_batch`, `set_train_batch_size`, `is_first_stage` |
| [deepspeed/launcher/runner.py](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/deepspeed/launcher/runner.py) | `parse_args`, `fetch_hostfile`, `parse_node_config`, `parse_node_config_list`, `parse_resource_filter`, `parse_inclusion_exclusion`, `apply_num_nodes_and_gpus`, `encode_world_info` |

## 教程、PR 与继续搜索

- [全仓目录和固定文件入口](../source-maps/deepspeedai-deepspeed.md)：没有本地专题时按模块继续读源码。
- [上游教程原文目录](../upstream-docs/deepspeedai-deepspeed/)：保留来源内容，链接相对位置以原站为准。
- [PR #8534：Deprecate loco zero++](../prs/deepspeedai--DeepSpeed/PR-8534.md)：正文、review、diff 与 head/base 源码。
- [PR #8632：Harden ZeRO-1/2 offload gradient storage lifetime and stream ordering](../prs/deepspeedai--DeepSpeed/PR-8632.md)：正文、review、diff 与 head/base 源码。

检索示例：`wiki-search "关键符号或问题" --engine deepspeed`。本地结果不足，使用 `wiki-search-pr "简短英文问题词" --engine deepspeed`，再 `wiki-pr OWNER/REPO NUMBER`、`wiki-code OWNER/REPO FULL_SHA PATH` 追实际调用者、被调底层库和测试。普通查阅只写私有缓存。

## 更新和验收边界

运行 `wiki-update PROJECT deepspeedai-deepspeed` 检查完整目录、新文档、PR 讨论与已监测源码；分页或网络失败必须续采。变更后联动本页、同仓专题/案例、调用方与依赖；源码已 merge、软件已发布、HCU 已适配和当前任务已验证分别登记。本页为选定实现的代码阅读和操作建议，没有在 HCU 执行上述测试，也未覆盖所有模型。实际任务的版本、性能、显存、失败尝试和阶段 loss 记录进入私有经验 Wiki。
