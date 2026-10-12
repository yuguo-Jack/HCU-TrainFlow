---
id: engines/swift/topics/megatron-grpo-weight-lifecycle
title: ms-swift Megatron GRPO：权重同步、LoRA 与显存切换
engine: swift
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime
  execution
sources:
- source: modelscope-ms-swift
  path: swift/megatron/trainers/rollout_mixin.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: c77710d5f900e455a8873f2a5495bdf57d7bd6628a6c2a54bed61b798272886d
- source: modelscope-ms-swift
  path: swift/megatron/trainers/grpo_trainer.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: 34ec4b21ec0e33b2920d1b3712e86abccf594f08cce055417ec723ea7b38378b
- source: modelscope-ms-swift
  path: swift/megatron/trainers/base.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: a5e44bee709f375c7768f1eb864ec1cef04b06c7cb4f3dd9252b19be2427ccbd
- source: modelscope-ms-swift
  path: swift/megatron/arguments/megatron_args.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: ee5b040132967d6520efea1ed2eeed92fb45fc1b552a734652d1935e5a979230
- source: modelscope-ms-swift
  path: docs/source_en/BestPractices/GRPO.md
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: b30430aabc0579c26cabaa79dea9e0be5c5c54898cc28c1eb63ff3a47b2a082d
- source: modelscope-ms-swift
  path: tests/train/test_vllm_weight_sync.py
  commit: 409170095f24b45b8945715341504d99b70a2bc0
  sha256: c2ea7e3e682623d839fc5eb31fee97c659ee984811a5dfaa6777be97c7afd3d2
---

# ms-swift Megatron GRPO：权重同步、LoRA 与显存切换

## 问题和适用范围

共卡训练与 rollout 的峰值显存常由切换过程决定：训练 optimizer 尚未卸载时已经唤醒 KV，或更新后仍使用旧 prefix cache，都可能使单独可运行的两边组合失败。分离部署则更关注传输和策略版本。本文追 `MegatronRolloutMixin` 的 vLLM 路径，不能推广为 SGLang/其他 backend 相同 sleep 语义。

总览见 [ms-swift](../overview/engineering-guide.md)，源码固定于 `409170095f24b45b8945715341504d99b70a2bc0`。相关配置和算法见 [GRPO 官方说明](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/docs/source_en/BestPractices/GRPO.md)。

## 入口、参数与状态

`MegatronGRPOTrainer` 组织生成、reward、advantage、old/ref logprob 和训练 batch，rollout mixin 管生成 backend 和同步；Core 的 model/optimizer 生命周期由 base trainer 管。至少锁定以下组合：

| 输入/状态 | 用途 |
| --- | --- |
| `vllm_mode`、推理 TP/服务布局 | colocate 与 server 的同步/缓存调用不同 |
| `sleep_level`、`offload_model`、`offload_optimizer`、`offload_bridge` | 权重/KV/训练状态/导出缓存的驻留位置 |
| `tuner_type`、`rollout_enable_lora`、`base_sync_done` | 首次全量、adapter-only、merge/unmerge |
| `_step`、`_last_loaded_step` | 当前生成权重是否已经安装 |
| global/generation batch、steps_per_generation、num_generations | prompt-group、训练累计与策略重用边界 |

`megatron_args.py` 对 generation/global batch 和每设备 rollout prompt/microbatch 做整除检查；修改吞吐参数前确认样本组/重用次数没有变成新的算法。policy version、response mask 和训练 old logprob 必须和收到的权重一致。

## 一次生成的顺序与显存峰值

[`_generate_completions`](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/swift/megatron/trainers/rollout_mixin.py)先 preprocess samples，计算 `needs_weight_sync = 当前 step 不等于上次装载 step 或 sleep_level==2`，再按以下顺序运行：

1. colocated engine 在 sleep 且需要同步时，先唤醒 weights；有 tags 接口时只恢复 weights，避免过早物化 KV。
2. 通过 `_move_model_to_vllm` 安装当前模型/adapter，成功后更新 `_last_loaded_step`。
3. 进入 `offload_context`，按配置将 wrapped/reference model 与 optimizer 移到 CPU。
4. 在 context 内按 engine 实际状态唤醒 KV，随后执行一次或多轮 rollout；tags API 支持与否由实际函数签名判断。
5. finally 将 vLLM 再 sleep；失败时处理 sleep 错误仍保留原异常，随后 context 的 finally 恢复训练 model/optimizer。

该顺序解释了为什么不能把全部 wake-up 提前、将 offload 当成只有一个 flag，或认为 “生成异常” 后无需检查训练状态。测量要覆盖 weights wake-up、桥接导出、训练卸载、KV 恢复和再次训练，包含 allocator reserve/碎片、host RAM 与 pinned buffer。

## 全量同步与 LoRA 路径

`_move_model_to_vllm` 满足以下任一条件时走全量：tuner 不是纯 `lora`、尚未 base sync、sleep level 2、未启用 rollout LoRA；其余走 adapter-only。

全量路径中，未采用推理 LoRA adapter 的训练会先 merge，导出后在 finally unmerge；开启纯 LoRA 的 rollout adapter 模式先导出 base，完成后继续 adapter 同步。`lora_llm` 仍通过 dense merged 权重，不应误按纯 LoRA adapter-only 推断。后续 adapter sync 的前提是基础权重仍可靠驻留。

同步后 `_reset_vllm_cache` 重置 prefix cache；达到所检版本条件还重置 encoder cache。旧 cache 对应旧权重，发送 tensor 成功不能替代缓存一致性。server 模式的同步与重置由相应主进程/client 发起，colocate 直接调用 engine；单节点成功不能推断其他 TP/DP worker 全部完成。

## 优化判断：瓶颈归因后再改变实现

将整轮墙钟拆为 rollout、reward、old/ref logprob、actor update、weight sync、offload/copy、队列等待。全量导出占大头且基础权重稳定的纯 LoRA 才值得评估 adapter-only；共卡 OOM 才评估更激进 sleep/offload，但必须计入复制和恢复开销。

Rollout TP 和训练 TP/PP/EP 不同会引入 reshape/collective/CPU 导出；进一步追 bridge/export 实际实现和所加载模型，不能通过“权重字节数/网卡峰值”包办同步上限。低精度训练/生成同时存在时核对量化 scale、tied weights、层命名和缓存，不只比较 dtype。

## 验证、诊断和回退

固定输入与策略版本下比较同步前后名称、shape、dtype、logits/logprob；验证首次全量、第二次更新、adapter-only、level2 后再次全量、merge/unmerge、服务端失败与 rollout 抛异常。检查 optimizer 和 reference model 是否重新加载，避免下一轮在已卸载状态上运行。

共卡 OOM 先定位峰值发生的具体切换，再减 concurrency/KV 或启用合适 offload；训练/生成不一致先确认 `_last_loaded_step`、base-sync 状态、缓存与各 rank，同一份固定权重重复验证。卡住时检查 client/server、TP collective、同步导出和待完成 async future，再读实际 vLLM/bridge 依赖版本。

无 sleep/offload、小批量全量同步是诊断对照，不是默认最终方案。未知 tags/sleep API 需要先核对兼容性，不能删除必要同步来提高表面速度。官方权重同步测试见 [test_vllm_weight_sync.py](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/tests/train/test_vllm_weight_sync.py)；本页没有在 HCU 验证这些组合。

## 更新联动

同步复核 rollout mixin、GRPO trainer、Core/base trainer、参数校验与推理版本；如果某个 sleep、LoRA、encoder cache 或导出 PR 变化，工程总览和本专题一起更新。搜索关键词：`base_sync_done`、`sleep_level weights kv_cache`、`rollout logprob weight sync`、`offload bridge`。保留 merged、released、HCU patch 和任务已测四种状态。
