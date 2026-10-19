---
id: engines/areal
title: AReaL：异步 RL、目标归一化、资源调度与恢复工程指南
engine: areal
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-20'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime execution
sources:
- source: inclusionai-areal
  path: README.md
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: ed1b3db840b6e56ede09fadb18f11894900cef42c76d4b5f1558786d6ffdd3b6
- source: inclusionai-areal
  path: pyproject.toml
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 8ef977590d481b44f418cc26bcaf24ffe91a6578b2a75f073823d8eeac91fd2b
- source: inclusionai-areal
  path: areal/v2/cli/main.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 2ea94d87a08a03165481cb0125b48f0c49ebf9aefafddde38173918fbb8db85b
- source: inclusionai-areal
  path: areal/v2/cli/cli.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: f8e7609425659b31dc39c6d59e45b1fdfacbe6ad2a8d593fdee5f4dfd0a95894
- source: inclusionai-areal
  path: examples/math/gsm8k_rl.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 9fbdf33f0cc289809097f2b270e09b0194750b3ba8d328fed302bb9dd2a98596
- source: inclusionai-areal
  path: examples/math/gsm8k_grpo.yaml
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: b4f13b0307f4dea393fd5400a810e7fa4c6941507b54539eea0c75a27b6cc66a
- source: inclusionai-areal
  path: docs/en/tutorial/quickstart.md
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: f92e909bff175a2589618286cb1bd6b88ddec754ac8f5d4041ad5d696c6a04c0
- source: inclusionai-areal
  path: docs/en/reference/alloc_mode.md
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: e2b4698c64ed6ff1c24e1f96dad2fcc004ddc427c9d14afc514f1749a80e6450
- source: inclusionai-areal
  path: areal/api/cli_args.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 3c2ab3e451a4c31b8afe08befefb23728e682ce57df5401b383cc3847778fe5e
- source: inclusionai-areal
  path: areal/api/engine_api.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: f19ea4759d64415f9fcc071c2fee604def1bfb13ddc2d26736b10ff2804875ce
- source: inclusionai-areal
  path: areal/api/workflow_api.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 1c375889fef9e76751411dd8b978c84d9cbcada033e81c38497bf00926054726
- source: inclusionai-areal
  path: areal/workflow/rlvr.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 8a47ab22d204a6d3f9588d050f098e3fa890f115126a387c89e6dd1ee6bb346c
- source: inclusionai-areal
  path: areal/trainer/rl_trainer.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 4944385f9cee00ce3585198e576d27d1ee8ddc38fae27f8080aceda98a067721
- source: inclusionai-areal
  path: areal/trainer/ppo/actor.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: c4b60120edf0427f86789e536ef53513dcba040c7c5645e23d861a45b125e088
- source: inclusionai-areal
  path: areal/trainer/ppo/loss_reduction.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: ec6332da715249fb9dd985962536578222fd611268044c96ab72668fd16c306f
- source: inclusionai-areal
  path: areal/utils/functional/loss_aggregation.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 030f9089f557d837bac5301f267f9685857b7e29c08a682d45f460e130313ed3
- source: inclusionai-areal
  path: areal/engine/core/train_engine.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: a24f263445ea85ffdc63dfebcbbee7536b3401e93e45cfe6f1a979be6724d66f
- source: inclusionai-areal
  path: areal/engine/megatron_engine.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 6f817b52dea9bdf7aa040f290b8a0894a4a6b5dd01488781d31cb5a6d9acf9e9
- source: inclusionai-areal
  path: areal/infra/staleness_manager.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: ade1bd484e86d666421716159d6a675ca010c5b5acb8fca05f989389c7f4269d
- source: inclusionai-areal
  path: areal/utils/recover.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: d5d8da8aae237f4c20af742b01c1d7d11779f3f760e1a587fa601ff327452f49
- source: inclusionai-areal
  path: docs/en/best_practices/handling_oom.md
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: e34642af9dbfffcc7b66b5c8dff37c3f5fa7074971f3d89e4b27402da38e62fb
- source: inclusionai-areal
  path: docs/en/best_practices/debugging.md
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 2541f86dfa7eff31951c10bad33c6f2285295b0011b3517b43e6218bd1895267
- source: inclusionai-areal
  path: docs/en/best_practices/perf_profiling.md
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 0e7ec8e721be15f9bcbf7927822e32bf2cc9123237b3a038fef07b0c5f37d010
- source: inclusionai-areal
  path: docs/en/version_history.md
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 9b816fd9908f49644253dcd673de79821674d2f6041030ca6f06c8efff058f6d
- source: inclusionai-areal
  path: tests/test_staleness_manager.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 0b6164520fd63f158d122b6f47dd4659a14982e29b02b74aba04acc57c2afeb8
- source: inclusionai-areal
  path: tests/test_prompt_mean_actor.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 0ecb5c5e733dfd7055f012dc49567abd9350b9b63a489dbfc0ff4678f2d62142
- source: inclusionai-areal
  path: tests/test_recover.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 3f7ba10cf826025ea39e28fe2ebb96375089177ab93e2bf4b0ded33d1476932a
- source: inclusionai-areal
  path: tests/test_rollout_version_race.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 7a8cdfaf8694a43b9b19f5dab429d07a91d6390313f72a9d8b2b3c6a3e98631e
- source: inclusionai-areal
  path: areal/v2/weight_update/gateway/app.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 4466ce0e81b39282b470b7c0991546c7db317ce2a0ceaef04ad7f56d5ffa8632
- source: inclusionai-areal
  path: areal/v2/weight_update/controller/controller.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 6a3037239a0ce0528e1f35356b7aba62517ca7705609f106a10afa6a175a6079
- source: inclusionai-areal
  path: areal/v2/training_service/controller/controller.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: dcc52ae17612e969d15e9379949e5645a109bb4a31790667a24b0b8f8204281f
- source: inclusionai-areal
  path: areal/engine/awex/plugins/sglang_plugin.py
  commit: 3b93679888e9f4929f6f155f13c6a286a62dfd72
  sha256: 372a82de53692a9b7fe4f7b83a099e8265eaa781c07f79b6618e3edbe19f5a2a
pr_sources:
- pr-areal-project--areal-1546
---

# AReaL 工程指南

## 1. 定位与版本边界

AReaL 将 rollout、reward/agent 工作流、PPO/GRPO 更新和资源调度分开，使生成与训练能够异步推进；训练端可用 FSDP 或 Megatron，推理端可用 SGLang/vLLM。主要优化对象除了训练 kernel，还包括生成尾延迟、样本版本、权重交接、共享显存和 reward 等待。

本页固定官方 `3b936798`，包声明为 **2.1.0**；来源登记 ID `inclusionai-areal` 保留兼容，官方工程目前使用 `areal-project/AReaL`。HCU patch 工程是另一条版本线。先用 HCU-Knowledge 确认真实主仓、基础提交、推理依赖和模型脚本，再联查本页；不能将最新官方依赖覆盖进旧 HCU 环境后认为已经完成升级。

本轮阅读了配置、真实 recipe、训练/rollout 控制和选定测试，**没有执行 HCU 运行、性能或恢复测试**。

## 2. 工程目录与问题入口

| 路径 | 职责 | 从什么问题进入 |
| --- | --- | --- |
| `examples/math/gsm8k_rl.py` / `gsm8k_grpo.yaml` | `PPOTrainer` 入口、资源与角色配方 | 跑通基线、核对训练和采样规模 |
| `areal/api/cli_args.py` | 配置 dataclass、默认值、校验 | 参数是否存在、覆盖是否生效 |
| `areal/trainer/rl_trainer.py` | rollout → update → 权重发布 → save/eval 的时序 | 步时、交接显存峰值、版本未推进 |
| `areal/trainer/ppo/actor.py` / `loss_reduction.py` | 优势处理、优化步划分、policy loss | loss 缩放或 packing 后梯度改变 |
| `areal/engine/` | FSDP/Megatron/推理实现、底层调用 | 单算子、并行、checkpoint 格式 |
| `areal/infra/controller/` / `workflow_executor.py` | worker RPC、任务队列、推理控制 | 排队、代理服务、远端 worker 失联 |
| `areal/infra/staleness_manager.py` | 版本和并发约束下的 admission | rollout 堆积、训练端等待、恢复后突发提交 |
| `areal/workflow/` | RLVR、agent、多轮任务与 reward | 数据构造、行为 logp/版本、奖励异常 |
| `areal/utils/recover.py` / `checkpoint_pointer.py` | 恢复信息、已完成 checkpoint 选择 | 保存未完成、恢复错步或权重未同步 |
| `areal/v2/` | CLI、gateway 和新控制器实现 | v1/v2 功能差异；不能仅看顶层 API |

每个角色可以处于独立进程；只查主控日志不能证明远端加载了同一版本。来源文件导航在[固定源码地图](../../upstream/source-map/inclusionai-areal.md)。

## 3. 安装、依赖与加载确认

固定版本要求 Python `>=3.11,<3.13`、Torch `>=2.9.1,<2.11`，Transformers 的允许范围也已进入 5.x；以[实际 pyproject](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/pyproject.toml)为准。CUDA/Megatron、SGLang、vLLM extras 带有各自的平台和版本限制，不能把所有 extras 一次装入 HCU 镜像；HCU 已支持的引擎、扩展和 build 配方优先。

在选定的可运行环境中从固定 checkout 安装所需模块，再检查 `areal.__file__`、distribution 版本、Torch HIP 标识、推理服务实际版本和 worker import 路径。`areal` console script 指向 `areal.v2.cli.main:cli`，它转交 v2 CLI；训练 recipe 的 Python 脚本入口与此不是同一个命令层。

配置文件和 CLI override 由 `load_expr_config` 解释，新增字段与修改已有字段需要按实际解析规则处理。跨节点共享 `cluster.fileroot`、name resolve 路径和模型/数据目录，并把目录约束到任务工作空间；官方 `/tmp` 示例不是本集群的可复用共享路径。

## 4. 官方运行入口与分层测试

固定版本的[GSM8K 脚本](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/examples/math/gsm8k_rl.py)加载 `GRPOConfig`、tokenizer、训练/验证 dataset，再通过 `PPOTrainer.train` 调用 `areal.workflow.openai.math_agent.MathAgent`。旧的 RLVR 直连示例与这个真实入口需要分别核对，不能用文档旧片段推断当前 agent 路由。

```bash
python examples/math/gsm8k_rl.py --config examples/math/gsm8k_grpo.yaml \
  scheduler.type=local experiment_name=baseline trial_name=run0
```

这是官方命令入口示意；现场应替换模型、数据、共享目录及已支持的 HCU backend。原 YAML 采用 8 卡、actor FSDP d4 与 rollout SGLang d4，`scheduler.type` 留空等 CLI 覆盖；它不代表任意环境都可直接运行。先记录角色 placement、卡数、worker 环境、reward 入口和可见数据，再确认生成结果、有效 loss token、训练梯度、版本和 checkpoint 均推进。

| 层级 | 选定测试 | 能验证的边界 |
| --- | --- | --- |
| 目标函数 | `tests/test_prompt_mean_loss.py`、`test_prompt_mean_actor.py` | padded/packed、优化步拆分、固定参数下 loss/梯度等价 |
| 异步状态 | `tests/test_staleness_manager.py`、`test_rollout_version_race.py` | admission 计数与请求实际使用的版本 |
| 恢复协议 | `tests/test_recover.py` | 指针发布时序、失败不开放 colocated 请求、v2 明确拒绝 |
| 现场集成 | 官方短 recipe + 真实训练/推理依赖 | 设备 kernel、通信、服务交接与完整恢复；本页未实测 |

## 5. 模型、数据与数值契约

模型 config/tokenizer、chat template、thinking 规则和 sampling temperature 必须在训练与推理中一致。`train_dataset.batch_size` 的 prompt 数、`gconfig.n_samples` 的每 prompt 回答数、`ppo_n_minibatches` 的 optimizer step 划分和 `mb_spec` 的执行 microbatch 是四个概念，不能混成一个 global batch。资源 backend 字符串 `d/p/t` 是角色并行配置，也不是这些数据计数的替代品。

RLVR 工作流返回 token、attention/loss mask、reward、行为 logp 和 token 版本，prompt 与 padding 不参与 policy loss。当前 recipe 走 MathAgent 的 session 工作流，实际数据转换还要追该入口。检查行为策略、proximal 近似、当前策略的区别；改变 `loss_aggregation` 会改变不同长度回答的权重，属于算法/数值变更，不是纯吞吐开关。

## 6. 主调用链与底层依赖

```text
recipe / load_expr_config → PPOTrainer / RLTrainer
  → rollout controller / agent workflow → reward 与训练 trajectory
  → actor/ref/critic 的 logp、advantage → actor.ppo_update
  → prepare_policy_gradient_batch → optimizer-step split → engine.train_batch
  → rollout.pause → actor.update_weights → 各角色 set_version
  → save/eval/offload → 恢复生成和 admission
```

AWEX v1 colocated 是重要例外：当前先保存训练状态，再转移权重，以免推理恢复后的显存与保存瞬态叠加。`maybe_wait_for_staging` 位于修改 actor 参数之前；它保护异步 checkpoint 的参数快照。底层性能和数值仍应追到 Megatron/TE、FSDP/Torch、SGLang/vLLM 的**实际依赖提交**。

v2 的权重更新成功语义需要单独验收：gateway 传输失败可返回 HTTP 200 的 `status="error"`，当前 GatewayTrainController 未检查该业务状态就继续 generation，上层还可能推进版本。函数返回或 HTTP 成功不足以确认实际安装，详见[版本与恢复专题](../topics/async-version-and-recovery.md#2-权重发布与暂停协议)。AWEX colocate plugin 同时限制已核对的 SGLang 版本并拒绝不兼容的 allocator 配置，不能直接采用 SGLang 最新主干覆盖当前消费者。

## 7. 性能与显存：机制、代价和选择

1. **Packing + objective-aware normalization**：短回答减少 padding，但 loss 的单位可以是 token、response 或 prompt，必须连同 engine 权重一起改变；[目标与 packing 专题](../topics/loss-aggregation-and-packing.md)解释跨 microbatch/DP 的计数，避免吞吐变快而训练目标被换掉。
2. **Async + staleness admission**：增加并发可能提高推理利用率，却增加版本差和队列驻留；调节 concurrency、consumer batch 与 max head offpolicyness，联合看 accepted/rejected、版本差和 trainer 等待，不能仅看 requests/s。[版本与恢复专题](../topics/async-version-and-recovery.md)给出实际计数公式。
3. **训练/推理显存交接**：记录参数、optimizer、activation、KV/graph 和转移暂存峰值。Megatron 通过 `stage_batch_for_engine` 将完整 batch 放 CPU、只流式搬运当前 microbatch；收益是减小 GPU 同时驻留，代价是 H2D/CPU 开销。不能只把局部变量重绑定，否则 RPC 参数容器仍可能持有整批 GPU tensor。

Profiler 应同时抓 train/rollout/reward/weight-update；官方 `perf_tracer` 的作用域和 `memory_profiler.profile_steps` 可定位时序和显存阶段，再接 Torch profiler、TraceLens 与 HCU 的工具。上游以 CUDA 名称暴露的接口要按安装的 HCU Torch 能力验证。

当前 engine 除原 scalar mean 契约外，还接受具名 loss 分子与独立 normalizer；不能把旧 scalar mean 直接装进 dict，两者缩放公式不同。[目标专题](../topics/loss-aggregation-and-packing.md)补充静态 schema、分数/空 mass 与 transport-only rank 的限制。优势计算现由 `resolve_advantage_fn`/结果校验组织，修改 advantage registry、mask 或 reward plugin 同样属于算法变更。

本轮还引入 Megatron/SGLang 的 R3 router replay：actor 单独接收 rollout 的 `routed_experts` 与 `r3_routing_valid`，reference/critic/teacher 仍应使用自己的路由。它需要实际 MoE 层布局、top-k、PP/VPP/CP 与 router 发现一致，不能由存在 Moonlight 示例推定所有 MoE/HCU 后端可用。SGLang 图像 token 传输也只在占位符 runs 与图像数量匹配时压缩，训练端原 token IDs 仍要保持，避免二次展开改变 logp 对齐。

## 8. 精度、故障与恢复的排查顺序

先固定输入、采样/随机种子、mask、logp 对齐、目标归一化和参数版本，再比较 loss/梯度/更新。出现 PPO 数值变化时检查 reward normalization、prox_logp_method、importance sampling、rejection mask；不先归因于 HCU kernel。

卡住时沿 **主控 → RPC → 队列/容量 → 推理服务暂停状态 → 更新权重通信** 排查。权重交接 OOM 则检查保存先后、actor/critic offload 与 KV/graph 暂存，不能只压低静态内存比例。恢复要求训练参数/optimizer、数据游标、step 和 rollout 权重版本共同对应；HF 导出不等于可继续训练的恢复 checkpoint。

当前 `RecoverHandler` 对 GatewayTrainController（`_version=v2`）仍明确拒绝恢复；actor/rollout 控制器版本要匹配。既有容错工具负责作业重启，AReaL 的 checkpoint 恢复不会自动修复节点或保证服务自动重建。启用前必须做现场失败注入与恢复质量验证。

FSDP 当前在 `with_optim=True` 的 DCP/HF 训练保存中增加 `lr_scheduler.pt`；旧 checkpoint 缺此文件仍可读，但只告警并保留当前 scheduler，不能声称精确恢复学习率轨迹。模型单独加载不恢复 scheduler。恢复验收需固定 scheduler 配置与总训练步数，详见[恢复专题](../topics/async-version-and-recovery.md)。

## 9. Release、特性 PR 与更新

查看[官方文档](https://areal-project.github.io/AReaL/)、[release](https://github.com/areal-project/AReaL/releases)、[PR](https://github.com/areal-project/AReaL/pulls)和[版本历史](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/docs/en/version_history.md)。历史页保留 legacy `realhf` 的里程碑，不能据此推断当前 `areal`/v2 支持范围。本轮尚未确认独立的正式 roadmap 文件，路线以官方发布/讨论中可追溯内容为准。

当前提交合入[可配置 loss aggregation #1546](https://github.com/areal-project/AReaL/pull/1546)；本页读的是最终实现与测试，PR 顶层描述/review 在 PR 来源层查。更新 recipe、loss reduction、staleness、权重传输或恢复时，同步复核两专题、总览、HCU 对应分支和 TrainFlow 的精度/长稳验收；不能只更新时间戳。

已有来源入口保留：[VLM SFT response loss mask #1679](../../upstream/prs/areal-project--AReaL/PR-1679.md)、[VLM CPU 广播与 microbatch 内存 #1697](../../upstream/prs/areal-project--AReaL/PR-1697.md)。它们用于继续联查多模态实现；本页两个新专题聚焦 RL 目标与恢复，没有声称覆盖全部 VLM 模型路径。


## 本轮补充固定证据


- [areal/v2/weight_update/gateway/app.py](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/areal/v2/weight_update/gateway/app.py)
- [areal/v2/weight_update/controller/controller.py](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/areal/v2/weight_update/controller/controller.py)
- [areal/v2/training_service/controller/controller.py](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/areal/v2/training_service/controller/controller.py)
- [areal/engine/awex/plugins/sglang_plugin.py](https://github.com/areal-project/AReaL/blob/3b93679888e9f4929f6f155f13c6a286a62dfd72/areal/engine/awex/plugins/sglang_plugin.py)
