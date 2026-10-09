---
id: engines/areal
title: AReaL：异步训练接口、权重版本与 loss 权重
engine: areal
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
- source: inclusionai-areal
  path: areal/api/engine_api.py
  commit: 01de0a83e17cb12c918fc791466138ddbd4168c9
  sha256: cdb62bfa612af7a25afad155440fb9220cef5e9d80f3a0b3fb9d4ce923160fea
- source: inclusionai-areal
  path: areal/api/workflow_api.py
  commit: 01de0a83e17cb12c918fc791466138ddbd4168c9
  sha256: 1c375889fef9e76751411dd8b978c84d9cbcada033e81c38497bf00926054726
- source: inclusionai-areal
  path: areal/engine/megatron_engine.py
  commit: 01de0a83e17cb12c918fc791466138ddbd4168c9
  sha256: 3be5842287b29009321903fde0a622335c68de16060daf9be220da4bbf71d91a
- source: inclusionai-areal
  path: areal/engine/core/train_engine.py
  commit: 01de0a83e17cb12c918fc791466138ddbd4168c9
  sha256: 426e1725004f5108153e19ead99a1b7c75ae39ebdc8224ec5b18269378b6b087
- source: inclusionai-areal
  path: areal/engine/awex/memory_saver.py
  commit: 01de0a83e17cb12c918fc791466138ddbd4168c9
  sha256: 161c3547d949db44274c08c8a7a68a3af6c55a29772373f236f56bc576f0e57c
- source: inclusionai-areal
  path: areal/engine/fsdp_engine.py
  commit: 01de0a83e17cb12c918fc791466138ddbd4168c9
  sha256: 6bb97153acb8233bd95d2f6d8a77d67de78d8317e4603a7224375e83ed8461db
- source: inclusionai-areal
  path: areal/engine/sglang_remote.py
  commit: 01de0a83e17cb12c918fc791466138ddbd4168c9
  sha256: 514a071bc5860d239b5618bd8adc3b2df530dc9a75b13b54c8275bef154c9c58
---

# AReaL：异步训练接口、权重版本与 loss 权重

## 定位与源码布局

当前规范仓为 areal-project/AReaL。`api/engine_api.py` 分离 TrainEngine 与 InferenceEngine，`api/workflow_api.py` 定义 rollout/agent workflow；`engine/fsdp_engine.py`、`megatron_engine.py` 是训练实现，`sglang_remote.py` 是生成后端，`engine/core/train_engine.py` 汇总部分 batch/loss 通用处理。

## 接口链与版本

TrainEngine 提供 prepare_batch、train_batch、forward_backward_batch、save/load、set_version/get_version 与 offload/onload；InferenceEngine 有 submit/wait、rollout_batch、权重更新与暂停恢复。异步调度时必须把样本、policy version、checkpoint、训练 step 关联起来。接口存在并不意味着所有 backend 支持同一选项；以具体实现为准。

## loss 与 padding

`compute_microbatch_loss_weight` 对 transport-only dummy batch 返回零，不调用实际 objective；普通 batch 才调用 loss_weight_fn。`compute_total_loss_weight`、microbatch 切分和聚合共同决定梯度归一化。改变 batching/流水线时要确认占位数据没有参与有效 token 分母、loss 或指标。PR #1679 的 VLM response mask 修正是数值检查的直接入口。

## 权重传输与内存

`SGLangBackend.build_distributed_weight_update_requests` 在本轮快照明确拒绝 LoRA 分布式更新，提示使用 disk mode；不能因普通参数同步成功就将该限制删除。请求传递 names、dtypes、shapes、group_name，并要求中止在途请求，进一步应核对服务端的执行状态。

FSDP 与 Megatron 各自实现 offload/onload、device stats 和 perf tracer。AWEX memory saver 的 hook 模式修补是额外生命周期层；选择高并发前检查 allocator、权重驻留和推理占用峰值。PR #1697 涉及 VLM CPU broadcast 与 microbatch 内存，迁移时应保留多模态 batch 语义，而不是仅比较 copy 字节数。

## 安装、运行和验证

先读 docs/en 的 tutorials、reference、algorithms 和目标 workflow，选择 FSDP/Megatron 与具体 inference backend 的兼容组合。现场采用 HCU 工程已有 recipe；检查 launcher、分布式进程组及后端探活。最小回归包括生成、训练更新、再次生成、权重版本推进和 checkpoint 恢复。

数值回归涵盖 mask、有效 token 权重、dummy transport、变长响应、reward/KL、old/ref logprob 和 policy lag。性能拆开 submit→queue→generate→return→train→sync，并关注 p95、在途数量和落后版本，而不是只报每秒采样数。

## 诊断和变更联动

卡住时收集等待中的 workflow、engine future、通信组、推理服务请求和版本水位；OOM 区分 CPU broadcast、完整权重物化、微批 padding 与设备缓存。变更 engine_api 后必须同时检查具体后端、控制器、测试及 Wiki，不能只以抽象方法签名仍存在判定兼容。

## 固定源码与符号导航

| 文件 | 本轮源码中可追查的入口（非全部符号） |
| --- | --- |
| [areal/api/engine_api.py](https://github.com/areal-project/AReaL/blob/01de0a83e17cb12c918fc791466138ddbd4168c9/areal/api/engine_api.py) | `TrainEngine`, `InferenceEngine`, `create_process_group`, `initialize`, `data_parallel_group`, `data_parallel_rank`, `data_parallel_world_size`, `current_data_parallel_head` |
| [areal/api/workflow_api.py](https://github.com/areal-project/AReaL/blob/01de0a83e17cb12c918fc791466138ddbd4168c9/areal/api/workflow_api.py) | `RolloutWorkflow`, `AgentWorkflow`, `arun_episode`, `run` |
| [areal/engine/megatron_engine.py](https://github.com/areal-project/AReaL/blob/01de0a83e17cb12c918fc791466138ddbd4168c9/areal/engine/megatron_engine.py) | `MegatronEngine`, `MegatronScoringEngine`, `MegatronPPOActor`, `MegatronPPOCritic`, `MegatronLMEngine`, `MegatronRWEngine`, `MegatronDPOEngine`, `forward` |
| [areal/engine/core/train_engine.py](https://github.com/areal-project/AReaL/blob/01de0a83e17cb12c918fc791466138ddbd4168c9/areal/engine/core/train_engine.py) | `compute_microbatch_loss_weight`, `compute_total_loss_weight`, `stage_batch_for_engine`, `aggregate_eval_losses`, `reorder_and_pad_outputs` |
| [areal/engine/awex/memory_saver.py](https://github.com/areal-project/AReaL/blob/01de0a83e17cb12c918fc791466138ddbd4168c9/areal/engine/awex/memory_saver.py) | `patch_tms_hook_mode`, `safe_setter` |
| [areal/engine/fsdp_engine.py](https://github.com/areal-project/AReaL/blob/01de0a83e17cb12c918fc791466138ddbd4168c9/areal/engine/fsdp_engine.py) | `FSDPTrainContext`, `FSDPEngine`, `FSDPPPOActor`, `FSDPPPOCritic`, `FSDPLMEngine`, `FSDPRWEngine`, `FSDPDPOEngine`, `to_dict` |
| [areal/engine/sglang_remote.py](https://github.com/areal-project/AReaL/blob/01de0a83e17cb12c918fc791466138ddbd4168c9/areal/engine/sglang_remote.py) | `SGLangBackend`, `RemoteSGLangEngine`, `build_server_env`, `build_generation_request`, `parse_generation_response`, `build_score_request`, `parse_score_response`, `build_disk_weight_update_requests` |

## 教程、PR 与继续搜索

- [全仓目录和固定文件入口](../source-maps/inclusionai-areal.md)：没有本地专题时按模块继续读源码。
- [上游教程原文目录](../upstream-docs/inclusionai-areal/)：保留来源内容，链接相对位置以原站为准。
- [PR #1679：fix(dataset): align VLM SFT loss masks with responses](../prs/areal-project--AReaL/PR-1679.md)：正文、review、diff 与 head/base 源码。
- [PR #1697：perf: reduce VLM CPU broadcast and microbatch memory overhead](../prs/areal-project--AReaL/PR-1697.md)：正文、review、diff 与 head/base 源码。

检索示例：`wiki-search "关键符号或问题" --engine areal`。本地结果不足，使用 `wiki-search-pr "简短英文问题词" --engine areal`，再 `wiki-pr OWNER/REPO NUMBER`、`wiki-code OWNER/REPO FULL_SHA PATH` 追实际调用者、被调底层库和测试。普通查阅只写私有缓存。

## 更新和验收边界

运行 `wiki-update PROJECT inclusionai-areal` 检查完整目录、新文档、PR 讨论与已监测源码；分页或网络失败必须续采。变更后联动本页、同仓专题/案例、调用方与依赖；源码已 merge、软件已发布、HCU 已适配和当前任务已验证分别登记。本页为选定实现的代码阅读和操作建议，没有在 HCU 执行上述测试，也未覆盖所有模型。实际任务的版本、性能、显存、失败尝试和阶段 loss 记录进入私有经验 Wiki。
