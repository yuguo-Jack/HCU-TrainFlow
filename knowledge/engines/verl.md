---
id: engines/verl
title: verl：PPO 训练、rollout 与权重一致性
engine: verl
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: volcengine-verl
  path: README.md
  commit: 704a9f01bda8b9863c02c113547191bf167bc88f
  sha256: ddf49da56b709047d7641c6885c00bb43a68944aa458f03965008978d75a019d
- source: volcengine-verl
  path: verl/trainer/ppo/ray_trainer.py
  commit: 704a9f01bda8b9863c02c113547191bf167bc88f
  sha256: eb41f99ccc66976eab14ebe35aa1aa5b7318e02469240ef1569ac4c884c94312
---

# verl：PPO 训练、rollout 与权重一致性

## 调用地图

`verl/trainer/ppo/ray_trainer.py` 的 RayPPOTrainer 是重要入口：构造 dataloader、初始化 workers、计算 reward/ref/old logprob、更新 actor、保存/加载 checkpoint，并控制 profiling。框架层吞吐必须涵盖 rollout、训练和权重传输，不能只优化一个 actor step。

## 版本和启动

先读取目标 recipe 依赖说明，锁训练后端、SGLang/vLLM 和资源布局。README 对部分 recipe 提供 REQUIRED_VERL/commit 约束；不要把 rolling recipe 与任意旧 wheel 混搭。HCU patch 工程的兼容组合优先，但需要核对实际活跃分支。

## 数值与调度

保留每批 rollout 的 policy version、token、mask、奖励、优势和采样设置。训练与生成异步时，单一训练 loss 无法证明策略数据一致。检查权重同步完成、old/ref logprob 的来源、batch balance 是否改变样本权重和截断语义。

## 优化与排障

分别抓 actor forward/backward、rollout prefill/decode、weight sync、reward 与调度间隙。卡住时对照 Ray task、各 rank stack、collective 顺序和存储队列。失败恢复必须同时考虑 actor checkpoint 与 rollout 在途数据，不能仅重启推理进程。

本轮阅读到 trainer 入口/阶段组织；worker 内部的 FSDP/Megatron 和 rollout 后端应随实际任务继续建专题，不假定所有分支相同。

## 固定源码与更新范围

- [README.md](https://github.com/volcengine/verl/blob/704a9f01bda8b9863c02c113547191bf167bc88f/README.md)
- [verl/trainer/ppo/ray_trainer.py](https://github.com/volcengine/verl/blob/704a9f01bda8b9863c02c113547191bf167bc88f/verl/trainer/ppo/ray_trainer.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
