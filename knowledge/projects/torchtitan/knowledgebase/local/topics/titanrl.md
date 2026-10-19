---
id: official-torchtitan-wiki/titanrl
title: TitanRL：训练生成协同、权重同步与精度边界
engine: torchtitan
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-20'
coverage: Curated source chains and official evidence at a fixed main commit; not all models, backends
  or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/rl/train.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 63d83a8ee812a76d4d04abbff5d4a5821074a703145757ebf4904a2cdc551a78
- source: pytorch-torchtitan
  path: torchtitan/rl/trainer/trainer.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 35f0171826f745ea5c82458b176831e2e5ced1969ac352d5f60092fc4ad0b65c
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 5f4cdb46330683cb8bd2a65d764662712972fb8989afe35a9b9dfbe5e3270209
- source: pytorch-torchtitan
  path: torchtitan/rl/BITWISE_PARITY.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 00e77fab6806fa0986f1f4b16ca3769ceee98f7959ea76680fd8ba81d064fce0
- source: pytorch-torchtitan
  path: torchtitan_recipes/rl/model_configs.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: d62f1526bb38cb195554426f9f19d7f688f7f0c84c52ec8e905159709e1499e8
- source: pytorch-torchtitan
  path: torchtitan/rl/observability/metrics/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: df9c8957b9048a9739c617c6d339fd21efd3eb3606e416415f5b3c3f777b0885
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/generator.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: aecf95576c0710a68846850e63703b928fa41f5e426232a36069a0b3b424175e
- source: pytorch-torchtitan
  path: torchtitan/rl/controller/controller.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 4999b903e21b90140bff9e34fdb1900b5cd0206841f299983b4eb4d73700320b
- source: pytorch-torchtitan
  path: torchtitan/rl/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 62fde87475bed82db694353ac5892caaa9162c3ca854d7182353f6bcb486970b
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/system.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 7733d646cda32114febac5a669f9beb12be8445c864d8b540bc908f240e1650a
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/system.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 99f940aa2efdf924cf99838de83266d752fe2f9a3e39a75b34dac5e3e06c0345
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/trainer.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: b4a8bb1ad4f405986e28fd3fb241263be51490a687cd8fafd54a45896373246f
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/generator.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: d31019f3f348144f2f7e0542b49cdc2618f1d869f0822b708f5a85a3c75ed016
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/engine_loop.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 9c4679f1923f8d2f0a946b8576bccec5a810bf54e3996cc5c0af385341222a15
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/dispatcher.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 568ab88ca0d0846154661364c43e713eab388489679650fa5c80da90f73b442c
- source: pytorch-torchtitan
  path: torchtitan/config/transform/freeze_moe_routing.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 985eee889df806f156a8545a93baff4450c0fde0980786a6cdf7ecfcc4c1faa8
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_model_defaults.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: ca915722651a4aed4548ff74bf7f272b691c0753943bea56613d48b949798db3
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_engine_loop.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 91c705347bd99eba806630029e387c4f369e5e8fed7e76a989af8014b9bfe43d
pr_sources:
- pr-pytorch--torchtitan-5107
- pr-pytorch--torchtitan-5268
- pr-pytorch--torchtitan-5280
---
# TitanRL：训练生成协同、权重同步与精度边界

## 组件分工

TitanRL 由 Controller 协调 trainer、generator、rollouter、数据、环境/奖励和 work buffer；经 ActorSystem 组织进程与任务，默认实现为Monarch，使用TorchStore传输model state dict，生成侧由可配置engine（当前默认vLLM）对接TorchTitan模型。训练侧复用 `TrainingEngine`，并非把监督 Trainer 的一轮循环直接改个 loss。

trainer 与 generator 各自有并行配置、资源和模型 Config；`build_rl_model_configs` 一类构造器分别建立布局。可以布局不同，但模型语义、参数映射和权重版本必须一致。RL 安装/启动由其独立入口和脚本负责，不能用普通 `run_train.sh` 的默认预训练配置假定已经启动全部组件。

## 同步与异步的可观测语义

`target_offpolicy_steps=0` 对应同步策略；正值允许一定策略滞后。队列深度、windowed FIFO 与慢 rollout 会影响样本年龄，不应只看平均生成 throughput。需要保存 rollout 使用的 policy version、trainer 更新 step、生成器已应用版本、队列等待、token 长度分布和奖励/优势统计。

`windowed_fifo_batches` 的有限窗口可限制批次拖尾与策略滞后，但也改变吞吐与调度。调参需要同时观察训练有效利用、生成端 KV/显存、样本年龄和训练质量，不能把更快收集旧策略样本当作无条件收益。

## 权重同步时间线

```text
optimizer N 完成
  → trainer 将该版本权重复制/转换到稳定的 pinned CPU snapshot
  → TorchStore 发布与 generator 获取/应用
  → generator 开始使用明确的版本生成
下一轮 forward/backward 可在满足数据依赖时 overlap
  → optimizer N+1 修改原权重前等待上次 staging/push 的必要边界
  → 重用同步 buffer/key 前等待上次 pull 完成
```

训练侧不能把仍会被 optimizer 修改的 GPU tensor view 直接作为已发布快照；共享 pinned buffer 也不能在生成端仍读取时覆盖。等待 GPU event/阻塞 PUT 放到线程中避免卡住 asyncio loop，不代表取消同步。详细源码和上游证据见 [权重同步案例](../cases/rl-weight-sync-memory.md)。

## Trainer / generator 数值一致性

官方 bitwise parity 方法包含 batch-invariant 配置、确定性策略、匹配 TP/序列布局、计算与主权重 dtype、相同 attention/logprob 处理。某些设置限定 NVIDIA FlashAttention、collective 算法或 TF32 行为，不能直接作为 HCU 的环境配方。

排查顺序：相同 checkpoint 和 policy version → 相同 token/mask/position → logits/selected logprob → 前向 backend 与 dtype → TP/SP/CP 分布 → sampling/reward/advantage → 训练更新。batch-invariant 与严格确定性可能有性能代价；保留用于定位的严格模式，再决定正式训练需要的容差与性能配置。

没有 NVIDIA 环境时，仍可在同一 HCU 上比较 trainer 与 generator、保守 eager 与优化后端、固定 batch 与变 batch，找第一个不同的 tensor；有 NVIDIA 环境也需同语义和版本，不能直接比较两个不同默认配置。

## 支持范围与诊断

当前官方 RL 支持表中的许多结果只是两步 debug 验证。不能从某模型的预训练支持推导 RL 支持，也不能把计划中的 Kimi/DeepSeek 路线写成已可用。高价值入口：

| 现象 | 主要证据 |
| --- | --- |
| 首次 sync OOM | trainer 临时 cast、pinned CPU snapshot、generator FSDP group、KV cache 预算 |
| 同步卡住或偶发旧权重 | push/pull future、权重版本、buffer/key 复用、远端 worker 异常 |
| 生成很快训练仍空闲 | rollout 长尾、队列/backpressure、奖励服务、不同角色资源占用 |
| loss/reward/logprob 漂移 | policy age、数据处理、数值配置、KL/优势与采样参数 |
| 恢复后重复数据/版本错位 | Controller、数据队列与模型/optimizer checkpoint 的一致性 |

移植时复用 HCU 已有 RL/推理引擎能力，必要时读底层库对应分支；不要因为官方采用某个 NVIDIA kernel 就重写整个 RL 系统。

## 当前角色配置、输入传输与数值默认

`Controller.Config.actor_system` 默认构造MonarchActorSystem，负责provision、spawn和stop；领域服务不直接依赖Monarch，trainer handles按DP列组织，generator通过router访问。launcher自有hosts时传入预建actor system。默认实现的TorchStore storage与trainer mesh同置，并为每个trainer/generator rank初始化client；移植需同时满足handle调用约定、进程生命周期、DP列分发和传输所有权，不能仅替换class名字。

`build_rl_model_configs` 当前默认给trainer和generator都设FP32-output LM head，并冻结router gate/expert bias、去掉aux load-balancing loss，保持对齐。它改变可训练参数/优化器状态与目标，不只改变计算速度；显式关闭任一默认时两侧一起复核。某些SoftCappedLinear配方不能应用同样head converter，测试保留例外。vLLM config转换还要保留YaRN scale、首个full-attention选择和sharding；相同模型名不足以保证logprob一致。

RDMA microbatch是数据传输优化，和TorchStore模型快照不是同一路径。未开lazy preprocessing时，RDMA tensor仍会全部先读完再前后向，不能宣称已overlap。当前Controller拒绝RDMA+PP；RL Trainer另拒绝CP>1，因为per-token loss kwargs尚未相应切分。lazy preprocessing要求关闭CUDA graphs且无SDC replay；逐group Graph有不同的归约与metadata要求，见[编译通信](compile-fusion-and-communication.md)。RL optimizer-step边界由 `async_loop.num_prompts_per_train_step` 控制，普通 `training.num_tokens_per_train_step` 会被忽略并警告。

## 固定证据与使用边界

本页以官方主线 `a242475253433725f10f39c18f5ccbfdf188e097` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/rl/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/README.md)
- [torchtitan/rl/train.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/train.py)
- [torchtitan/rl/trainer/trainer.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/trainer/trainer.py)
- [torchtitan/rl/generator/generator.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/generator/generator.py)
- [torchtitan/rl/actors/monarch/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/actors/monarch/README.md)
- [torchtitan/rl/BITWISE_PARITY.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/BITWISE_PARITY.md)
- [torchtitan_recipes/rl/model_configs.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan_recipes/rl/model_configs.py)
- [torchtitan/rl/observability/metrics/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/observability/metrics/README.md)

- [PR #5107：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5107.md)
- [PR #5268：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5268.md)
- [PR #5280：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5280.md)

## 当前请求失败与模型版本等待

PR #5182 引入的单请求失败边界在本固定代码中移到 `generator/engine_loop.py` 与 `generator/dispatcher.py`：engine admission的rejected请求回送相应错误，其他请求继续；loop异常则失败outstanding、排队load/generate与后续调用，并释放engine资源。`wait_engine_loop`让controller观察loop异常；旧 `_rank0_drain_results` 的私有回调/TODO不能继续作为当前源码入口。CPU `test_request_rejected_at_admission_fails_alone` 与 `test_crash_fails_outstanding_and_queued_calls_and_later_calls` 分别覆盖两种边界，仍不替代真实多rank故障测试。

`load_model_state_dict(version)` 排队等待引擎在step间应用；同一批load请求可合并到最高version，再统一完成reply。Controller等待push与所有generator pull完成后才释放下一批rollout group，早完成的generator仍可能等待慢者。session affinity释放、drain与模型版本等待属于不同依赖，不能把合理等待当死锁而任意重路由。

当前启动输出参数为 `--output-dir`，资产和角色配置由recipe提供。升级要同时核对Controller、ActorSystem、Generator engine与配方；以上为固定源码和上游测试阅读，未进行新的RL现场恢复实验。

## 本次补充的实现与测试依据

- [torchtitan/rl/actors/system.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/actors/system.py)
- [torchtitan/rl/actors/monarch/system.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/actors/monarch/system.py)
- [torchtitan/rl/actors/monarch/trainer.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/actors/monarch/trainer.py)
- [torchtitan/rl/actors/monarch/generator.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/actors/monarch/generator.py)
- [torchtitan/rl/generator/engine_loop.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/generator/engine_loop.py)
- [torchtitan/rl/generator/dispatcher.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/generator/dispatcher.py)
- [torchtitan/config/transform/freeze_moe_routing.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/config/transform/freeze_moe_routing.py)
- [tests/rl/unit_tests/cpu/test_model_defaults.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/rl/unit_tests/cpu/test_model_defaults.py)
- [tests/rl/unit_tests/cpu/test_engine_loop.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/rl/unit_tests/cpu/test_engine_loop.py)
