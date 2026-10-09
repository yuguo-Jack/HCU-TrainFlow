---
id: engines/verl
title: VERL：训练与 rollout 状态、权重同步和 PPO 优化
engine: verl
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
- source: volcengine-verl
  path: verl/trainer/main_ppo.py
  commit: 5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d
  sha256: 270ffe0d0f5ddbc4e9af8d0f6eece5d11b1a6d6d76166603b5ebac81345dd5cc
- source: volcengine-verl
  path: verl/trainer/ppo/ray_trainer.py
  commit: 5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d
  sha256: eb41f99ccc66976eab14ebe35aa1aa5b7318e02469240ef1569ac4c884c94312
- source: volcengine-verl
  path: verl/workers/engine_workers.py
  commit: 5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d
  sha256: 6614ea551130ec586b3516731240b06451e74fc4533657ae0f3462c0cd59c63c
- source: volcengine-verl
  path: verl/workers/rollout/sglang_rollout/sglang_rollout.py
  commit: 5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d
  sha256: f1603ccbc997867eed5cc7d6d5926a5c9c592c3bb508de6a872f0a65b0de7e38
---

# VERL：训练与 rollout 状态、权重同步和 PPO 优化

## 定位与目录

新规范仓地址为 verl-project/verl。`trainer/main_ppo.py` 启动任务，`trainer/ppo/ray_trainer.py` 管 PPO driver；`workers/engine_workers.py` 包含训练与 actor/rollout/ref worker；`workers/rollout` 是 SGLang/vLLM 等后端。数据、reward、algorithm 和调度不是同一层，训练配置要锁定各组件版本。

## 调用链和数据语义

`RayPPOTrainer.init_workers` 建立角色，`fit` 驱动生成、logprob、reward/advantage 与 actor update。跨阶段保留 response mask、token 数、policy version、old/ref logprob、reward 和优势归一化设置；样本重排、动态 batch、异步 rollout 都可能影响数据归属。需要参考 reward 和 KL 的变化，不能把下降的训练 loss 直接等同 RL 质量提升。

## 权重同步和显存切换

当前 `ActorRolloutRefWorker.update_weights` 用 mode/config 选择 colocated naive 或 checkpoint engine。delta_sharded 由其自己的状态机驱动，不能用普通 per-tensor 路径替代。naive 路径中 rollout 原先应在 sleep 状态；先恢复权重、按需要同步基础权重及 adapter，再 offload trainer，最后恢复 KV cache。

源码明确区分 SGLang sleep level 1 与 vLLM level 1：前者在该 adapter 模式没有释放权重，后者会经过对应 allocator 的权重卸载。因此 resume_weights 不能写成统一的“level1 不必恢复”。恢复 KV 前有跨 trainer rank barrier，目的是等待其他 rank 释放显存；仅本 rank synchronize 不能证明邻居已经腾出空间。

## 安装、运行和回归入口

使用保留的 docs/start、workers、perf、advance、algo 文档和目标 recipe。环境同时检查训练后端、Ray、推理后端和权重传输扩展，不能仅验证 torch import。先跑最小 actor+rollout+reward 闭环，再验证保存恢复、policy version 和数据进度；HCU 分支的脚本/依赖组合优先。

权重同步回归检查 tensor 名称、dtype、shape、tied embedding、LoRA base_sync_done 和接收后 logits/logprob；使用同一 policy version 的固定输入。PR #8064 针对 FP8 同步中的 tied-embedding alias，提示“发送成功”不等于全部接收语义正确。

## 性能分析与故障定位

计时分别覆盖生成 prefill/decode、reward、old/ref logprob、actor forward/backward、同步和资源等待；最终给整个迭代墙钟吞吐。共卡时训练/推理内存切换可能是主瓶颈，分离部署时网络/版本滞后可能成为瓶颈。`free_cache_engine`、memory budget、offload 与并发不能只做单旋钮评估。

Ray 卡住时先看 controller/worker 任务状态、两个 backend 的 rank 栈、权重版本和 collective 顺序，再追 checkpoint engine/SGLang/vLLM 源码。PR #7926 指向独立 rollout 的预算传播问题；配置值要与实际 engine 参数和分配显存相互核验。失败恢复需要确认 actor checkpoint 与生成队列进度的联合边界。

## 固定源码与符号导航

| 文件 | 本轮源码中可追查的入口（非全部符号） |
| --- | --- |
| [verl/trainer/main_ppo.py](https://github.com/verl-project/verl/blob/5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d/verl/trainer/main_ppo.py) | `run_ppo`, `TaskRunnerV1`, `main`, `init_agent_loop_manager`, `run` |
| [verl/trainer/ppo/ray_trainer.py](https://github.com/verl-project/verl/blob/5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d/verl/trainer/ppo/ray_trainer.py) | `apply_kl_penalty`, `compute_response_mask`, `compute_spec_decode_metrics`, `compute_advantage`, `RayPPOTrainer`, `init_workers`, `fit` |
| [verl/workers/engine_workers.py](https://github.com/verl-project/verl/blob/5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d/verl/workers/engine_workers.py) | `TrainingWorker`, `ActorRolloutRefWorker`, `decorator`, `to`, `set_loss_fn`, `reset`, `train_mini_batch`, `train_batch` |
| [verl/workers/rollout/sglang_rollout/sglang_rollout.py](https://github.com/verl-project/verl/blob/5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d/verl/workers/rollout/sglang_rollout/sglang_rollout.py) | `ServerAdapter`, `resume`, `release`, `update_weights`, `wrap_lora_params` |

## 教程、PR 与继续搜索

- [全仓目录和固定文件入口](../source-maps/volcengine-verl.md)：没有本地专题时按模块继续读源码。
- [上游教程原文目录](../upstream-docs/volcengine-verl/)：保留来源内容，链接相对位置以原站为准。
- [PR #7926：[trainer, rollout] fix: honor V1 standalone rollout memory budget](../prs/verl-project--verl/PR-7926.md)：正文、review、diff 与 head/base 源码。
- [PR #8064：[rollout, vllm] fix: drop tied-embedding alias in fp8 weight sync](../prs/verl-project--verl/PR-8064.md)：正文、review、diff 与 head/base 源码。

检索示例：`wiki-search "关键符号或问题" --engine verl`。本地结果不足，使用 `wiki-search-pr "简短英文问题词" --engine verl`，再 `wiki-pr OWNER/REPO NUMBER`、`wiki-code OWNER/REPO FULL_SHA PATH` 追实际调用者、被调底层库和测试。普通查阅只写私有缓存。

## 更新和验收边界

运行 `wiki-update PROJECT volcengine-verl` 检查完整目录、新文档、PR 讨论与已监测源码；分页或网络失败必须续采。变更后联动本页、同仓专题/案例、调用方与依赖；源码已 merge、软件已发布、HCU 已适配和当前任务已验证分别登记。本页为选定实现的代码阅读和操作建议，没有在 HCU 执行上述测试，也未覆盖所有模型。实际任务的版本、性能、显存、失败尝试和阶段 loss 记录进入私有经验 Wiki。
