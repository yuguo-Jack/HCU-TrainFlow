---
id: engines/slime
title: Slime：Megatron 训练与生成服务的交替生命周期
engine: slime
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
- source: thudm-slime
  path: train.py
  commit: 0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e
  sha256: 5dfcec6737e53d613e5db94fc20459dd6d58282d17f01bab410868251522fc9d
- source: thudm-slime
  path: slime/ray/rollout.py
  commit: 0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e
  sha256: 36004ae5dcb497601ac84798bcb2b2f4d5b2e911b333fed5e7770b7ec1d46ecb
- source: thudm-slime
  path: slime/ray/actor_group.py
  commit: 0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e
  sha256: ded0c12645992c7ab5c7034a91b418f195a6109dda02c3af0d0548804f39340c
- source: thudm-slime
  path: slime/backends/megatron_utils/actor.py
  commit: 0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e
  sha256: 66a159753c6c3e1c8509b781f301551caf0a27e2dfe5c810dea8003b75b3710d
---

# Slime：Megatron 训练与生成服务的交替生命周期

## 目录与执行责任

`train.py` 是同步训练主循环；`slime/ray/actor_group.py` 管训练 actor 组，`slime/ray/rollout.py` 管 RolloutManager，`slime/backends/megatron_utils/actor.py` 是 Megatron 侧实现。异步方式和 retained serving 需要读对应脚本/状态机，不能把同步循环的因果关系推断成全部模式。

## 本轮源码中的关键顺序

主循环构建 actor/critic 后，先 update_weights，再通知 `training_ready`，之后恢复 KV（若配置 offload）。恢复后的 async producer 在权重安装前保持暂停，避免用旧模型生成新批次。每轮 generate 后可以 offload rollout，再进行 actor/critic 训练。

`training_completed` 释放队列容量，但源码特意注明这不代表模型/optimizer 与数据进度已有持久联合 checkpoint。随后保存 checkpoint、清理训练显存、恢复推理权重存储，暂停 rollout admission，更新权重，再按下一轮需要恢复 admission 和 KV。这些操作的顺序是正确性契约，不应为了 overlap 随意移动。

## 环境、启动和测试

从官方 get_started/advanced 与 examples 确认所选训练模式、模型配置、Ray placement group、Megatron 与 SGLang 版本。HCU 侧优先现有脚本和依赖组合；构建后检查 actor 能初始化、rollout 能服务、两者能同步，再跑完整一次生成→更新→同步→评估。

验证要覆盖首次权重加载、第二次更新、offload/onload、critic-only 起始阶段、checkpoint 恢复和异步重新挂接。开启 `check_weight_update_equal` 的适用检查不能取代训练 loss 或策略一致性回归。测试的数据与模型规模需记录，不能从一个小模型推广所有 EP/PP 布局。

## 优化与显存分析

分别测 rollout 时长分布、actor/critic train、weight sync、KV 恢复、队列等待和保存。`release_train` 与 `offload_train` 改变资源生命周期，应测重建成本、峰值副本和稳定迭代，不只报训练 step。actor/critic 可以存在不同时间线，collective 与资源互斥要结合 placement 实测。

复用 retained serving 可能减少重启开销，但会增加 checkpoint、生成队列和权重版本一致性的复杂度。PR #2444 是阅读重启设计的入口；PR #2442 提醒 disk delta sync 必须尊重 shard index，不能只按文件名猜本轮权重。

## 故障定位

生成停止先看 admission 是否仍暂停、training_ready 是否完成、健康检查和资源释放；训练停止再看 actor Ray future、Megatron rank 栈、网络通信与 GPU 进度。恢复失败核对 restore_plan、checkpoint committed、权重版本和队列水位。不要用重复启动来掩盖仍在运行的旧 actor，也不能由新 Agent 与既有容错同时重启。

## 固定源码与符号导航

| 文件 | 本轮源码中可追查的入口（非全部符号） |
| --- | --- |
| [train.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/train.py) | `train`, `main`, `offload_train` |
| [slime/ray/rollout.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/ray/rollout.py) | `RolloutManager`, `pause_rollout_admission`, `resume_rollout_admission`, `dispose`, `attach_training`, `register_training_actors`, `detach_training`, `training_ready` |
| [slime/ray/actor_group.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/ray/actor_group.py) | `RayTrainGroup`, `async_train`, `save_model`, `update_weights`, `onload`, `offload`, `release`, `create` |
| [slime/backends/megatron_utils/actor.py](https://github.com/THUDM/slime/blob/0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e/slime/backends/megatron_utils/actor.py) | `MegatronTrainRayActor`, `init`, `sleep`, `wake_up`, `fill_routing_replay`, `compute_log_prob`, `train`, `train_critic` |

## 教程、PR 与继续搜索

- [全仓目录和固定文件入口](../source-maps/thudm-slime.md)：没有本地专题时按模块继续读源码。
- [上游教程原文目录](../upstream-docs/thudm-slime/)：保留来源内容，链接相对位置以原站为准。
- [PR #2442：fix(weight-sync): honor checkpoint shard indexes in disk delta sync](../prs/THUDM--slime/PR-2442.md)：正文、review、diff 与 head/base 源码。
- [PR #2444：Support manual Megatron restarts with retained serving](../prs/THUDM--slime/PR-2444.md)：正文、review、diff 与 head/base 源码。

检索示例：`wiki-search "关键符号或问题" --engine slime`。本地结果不足，使用 `wiki-search-pr "简短英文问题词" --engine slime`，再 `wiki-pr OWNER/REPO NUMBER`、`wiki-code OWNER/REPO FULL_SHA PATH` 追实际调用者、被调底层库和测试。普通查阅只写私有缓存。

## 更新和验收边界

运行 `wiki-update PROJECT thudm-slime` 检查完整目录、新文档、PR 讨论与已监测源码；分页或网络失败必须续采。变更后联动本页、同仓专题/案例、调用方与依赖；源码已 merge、软件已发布、HCU 已适配和当前任务已验证分别登记。本页为选定实现的代码阅读和操作建议，没有在 HCU 执行上述测试，也未覆盖所有模型。实际任务的版本、性能、显存、失败尝试和阶段 loss 记录进入私有经验 Wiki。
