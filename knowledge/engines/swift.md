---
id: engines/swift
title: ms-swift：多入口训练、Megatron 与 RL 数值链
engine: swift
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
- source: modelscope-ms-swift
  path: swift/cli/main.py
  commit: 22249748429ce7e8516640e35cbe997e572a233a
  sha256: fcc9f982a76102f792139c65de3b211b4af2c633801e7f0807996ac77dfcba88
- source: modelscope-ms-swift
  path: swift/cli/_megatron/main.py
  commit: 22249748429ce7e8516640e35cbe997e572a233a
  sha256: e1a89aee02857b246054b9ae232804b99670fa54545c2d9f22e78153bbc0d55f
- source: modelscope-ms-swift
  path: swift/megatron/trainers/base.py
  commit: 22249748429ce7e8516640e35cbe997e572a233a
  sha256: a5e44bee709f375c7768f1eb864ec1cef04b06c7cb4f3dd9252b19be2427ccbd
- source: modelscope-ms-swift
  path: swift/megatron/trainers/trainer.py
  commit: 22249748429ce7e8516640e35cbe997e572a233a
  sha256: b7efa15ead7a4f049495c4a0639c27edf6b99bddf9795c47c178a555cbcbf6dc
- source: modelscope-ms-swift
  path: swift/megatron/trainers/grpo_trainer.py
  commit: 22249748429ce7e8516640e35cbe997e572a233a
  sha256: 34ec4b21ec0e33b2920d1b3712e86abccf594f08cce055417ec723ea7b38378b
- source: modelscope-ms-swift
  path: swift/megatron/trainers/rollout_mixin.py
  commit: 22249748429ce7e8516640e35cbe997e572a233a
  sha256: c77710d5f900e455a8873f2a5495bdf57d7bd6628a6c2a54bed61b798272886d
---

# ms-swift：多入口训练、Megatron 与 RL 数值链

## 定位与目录

`swift/cli/main.py` 管常规命令、YAML 与 torchrun 参数，`swift/cli/_megatron/main.py` 提供 Megatron 入口。`swift/megatron/trainers` 包含公共训练生命周期、SFT trainer、GRPO trainer 和 rollout mixin。选择 backend 是第一步：相同模型通过普通训练、Megatron 和 RL 的执行链并不相同，不能只记录“使用 swift”。

## 调用链与可追查符号

`BaseMegatronTrainer` 负责 prepare_model、optimizer/scheduler、setup_training、run_train_step、train、evaluate 和 checkpoint。`MegatronTrainer.forward_step` 进入模型，`loss_func` 组织用于训练和日志的值。GRPO 的 forward_step、loss_func、rollout batch 与 `MegatronRolloutMixin` 共同决定训练/推理切换。

本轮 `MegatronTrainer.loss_func` 先把 output 转 float，用 `labels != -100` 构造 mask；可选 loss_scale 改变加权项，统计返回 local loss sum、local token count 与 logging metrics。日志用的 DP reduce 延后到 logging event，以免每 microbatch 引入全局同步。解释 loss 变化必须核对分子、分母及 logging 周期，不把显示频率改变当成优化后的数值漂移。

## 安装、运行与验证入口

官方 GetStarted、Megatron-SWIFT、GRPO 教程已作为独立原文保留。按当前 recipe 检查 Transformers、Core、TE 和 rollout engine 的版本；采用 HCU patch 工程适用的模型脚本及环境变量，再对照上游解析结果。首先确认启动的是哪个 CLI/module、是否 torchrun、多机地址与各并行组。

回归至少覆盖模板/packing、SFT loss、LoRA merge/unmerge、checkpoint 和目标训练 backend。GRPO 增加 reward、采样、old/ref logprob、mask、policy version 的一致性；不能只看一个标量 loss。训练参数/代码变更保留独立差异，组合稳定后安排阶段验证。

## 优化方向

用 `run_train_step` 与 `forward_step` 的实际 trace 对齐 Core schedule，分析 TP/EP/PP、grad sync、数据加载和日志同步。RL 额外拆 rollout、模型/optimizer offload、权重同步和生成服务。对于 CP、packing、动态 batch 和 fractional loss weight，先确认有效 token 与样本权重语义，避免调参改善吞吐却改变目标函数。

显存账本包含训练权重/master/optimizer、rollout 权重、KV cache、LoRA 临时 merge 副本及通信 buffer；检查切换高水位而非只采稳态。遇到 loss/梯度异常追 trainer 到 Core/TE 和实际 HCU 底层实现；新增 fused 实现优先复用既有 HCU TE/Flash-Train。

## 诊断与更新

checkpoint 导出失败时先核对 content_metadata 中是否混入 process group 等不可序列化对象（PR #10242）；loss 权重解释可追 PR #10188 及更新后的教程。更新时同时看普通 CLI、Megatron trainer、rollout mixin，不能只读入口 README。HCU 启动命令依赖变化记录待现场验证，源文件和 PR 可以先完成离线维护。

## 固定源码与符号导航

| 文件 | 本轮源码中可追查的入口（非全部符号） |
| --- | --- |
| [swift/cli/main.py](https://github.com/modelscope/ms-swift/blob/22249748429ce7e8516640e35cbe997e572a233a/swift/cli/main.py) | `use_torchrun`, `parse_yaml_args`, `get_torchrun_args`, `cli_main` |
| [swift/cli/_megatron/main.py](https://github.com/modelscope/ms-swift/blob/22249748429ce7e8516640e35cbe997e572a233a/swift/cli/_megatron/main.py) | `cli_main` |
| [swift/megatron/trainers/base.py](https://github.com/modelscope/ms-swift/blob/22249748429ce7e8516640e35cbe997e572a233a/swift/megatron/trainers/base.py) | `BaseMegatronTrainer`, `call_event`, `on_log`, `prepare_model`, `get_optimizer_and_scheduler`, `cyclic_iter`, `merge_lora_adapters`, `unmerge_lora_adapters` |
| [swift/megatron/trainers/trainer.py](https://github.com/modelscope/ms-swift/blob/22249748429ce7e8516640e35cbe997e572a233a/swift/megatron/trainers/trainer.py) | `MegatronTrainer`, `seq_cls_loss_func`, `loss_func`, `forward_step` |
| [swift/megatron/trainers/grpo_trainer.py](https://github.com/modelscope/ms-swift/blob/22249748429ce7e8516640e35cbe997e572a233a/swift/megatron/trainers/grpo_trainer.py) | `MegatronGRPOTrainer`, `prepare_model`, `train`, `on_policy`, `forward_step`, `loss_func`, `resample_encode_failed_inputs`, `get_num_iters_per_step` |
| [swift/megatron/trainers/rollout_mixin.py](https://github.com/modelscope/ms-swift/blob/22249748429ce7e8516640e35cbe997e572a233a/swift/megatron/trainers/rollout_mixin.py) | `create_rollout_group`, `MegatronRolloutMixin`, `load_teacher_model_context`, `samples2requests`, `offload_context` |

## 教程、PR 与继续搜索

- [全仓目录和固定文件入口](../source-maps/modelscope-ms-swift.md)：没有本地专题时按模块继续读源码。
- [上游教程原文目录](../upstream-docs/modelscope-ms-swift/)：保留来源内容，链接相对位置以原站为准。
- [PR #10188：docs: clarify configuration for fractional loss weights](../prs/modelscope--ms-swift/PR-10188.md)：正文、review、diff 与 head/base 源码。
- [PR #10242：[bugfix] drop dp_cp_group from content_metadata when saving mcore checkpoint](../prs/modelscope--ms-swift/PR-10242.md)：正文、review、diff 与 head/base 源码。

检索示例：`wiki-search "关键符号或问题" --engine swift`。本地结果不足，使用 `wiki-search-pr "简短英文问题词" --engine swift`，再 `wiki-pr OWNER/REPO NUMBER`、`wiki-code OWNER/REPO FULL_SHA PATH` 追实际调用者、被调底层库和测试。普通查阅只写私有缓存。

## 更新和验收边界

运行 `wiki-update PROJECT modelscope-ms-swift` 检查完整目录、新文档、PR 讨论与已监测源码；分页或网络失败必须续采。变更后联动本页、同仓专题/案例、调用方与依赖；源码已 merge、软件已发布、HCU 已适配和当前任务已验证分别登记。本页为选定实现的代码阅读和操作建议，没有在 HCU 执行上述测试，也未覆盖所有模型。实际任务的版本、性能、显存、失败尝试和阶段 loss 记录进入私有经验 Wiki。
