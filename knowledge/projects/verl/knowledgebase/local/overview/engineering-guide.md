---
id: engines/verl
title: verl：RL 数据流、训练后端、动态批次与权重同步指南
engine: verl
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
- source: volcengine-verl
  path: README.md
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: ddf49da56b709047d7641c6885c00bb43a68944aa458f03965008978d75a019d
- source: volcengine-verl
  path: pyproject.toml
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: 0be004554c671c42b612f050788366027e8e7197e0705b1b87d4f436cbc6af79
- source: volcengine-verl
  path: setup.py
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: 87bbccbcffac8bf9f203443bf9fba9f62ddf84c0333401d834624d86b3c175d4
- source: volcengine-verl
  path: verl/trainer/main_ppo.py
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: 270ffe0d0f5ddbc4e9af8d0f6eece5d11b1a6d6d76166603b5ebac81345dd5cc
- source: volcengine-verl
  path: verl/trainer/ppo/ray_trainer.py
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: eb41f99ccc66976eab14ebe35aa1aa5b7318e02469240ef1569ac4c884c94312
- source: volcengine-verl
  path: verl/trainer/ppo/core_algos.py
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: 369b614f239f237a04a38a40b1877cd6fd14aa7bd5f9ff4fe4d7758b682a6948
- source: volcengine-verl
  path: verl/workers/engine_workers.py
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: 781e4384762cc26c264e0baefddc6e9126472cac690d184660a37ba1200ef2c2
- source: volcengine-verl
  path: verl/workers/config/actor.py
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: d7631944b186f162b897022c9fac8b2f0ede7f8bb6cba4276d98e5d5033fd60b
- source: volcengine-verl
  path: verl/workers/config/rollout.py
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: a1fde638501c9cd69c1711cd1b4aa75241daaa171133f070ad89a5833c20f05d
- source: volcengine-verl
  path: verl/workers/engine/base.py
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: c3d0f88e32f8fe044bf7c4d249dfc4cfcee66ccc89b9850d971798b1b20f6a92
- source: volcengine-verl
  path: verl/workers/engine/megatron/transformer_impl.py
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: b43b266774c25924d0326ff0693b1a0db7614032b1061ae108926366b3de570e
- source: volcengine-verl
  path: verl/workers/engine/fsdp/transformer_impl.py
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: 717b595c729469bde375234710b967e5b4a8d39ba93419f7b2a380f080483842
- source: volcengine-verl
  path: verl/utils/seqlen_balancing.py
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: f0536d757a8c8eb1a15d63e7174a8995ebbf180481845576f1817ee6020b4902
- source: volcengine-verl
  path: docs/start/install.rst
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: 0892c67e9d35372a6c1ecd477463851b992f13fb673c75916fbd9ca2c99130ad
- source: volcengine-verl
  path: docs/perf/best_practices.rst
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: 37ede8da2d9efbc564bc9cb9f37e9d2f5a273e8eadb360b90e85166ebc1473cd
- source: volcengine-verl
  path: docs/perf/perf_tuning.rst
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: ef61c873077ca83d096eead93515b7221d92addbbed67b988d1e5385d093fc49
- source: volcengine-verl
  path: docs/perf/torch_profiling.md
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: c1925e1edfba630c25a048f219365d6aed183eab4eb9befc84baab86a857263f
- source: volcengine-verl
  path: tests/utils/test_seqlen_balancing.py
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: 658fb094f2edb2fe6914ded167e4b18aba3543d5b5410a93a2816622a7b9c48d
- source: volcengine-verl
  path: tests/trainer/ppo/test_rollout_corr_integration.py
  commit: 2035f58dcb06d8cad4caee107b30f4045d724367
  sha256: 3d8c1a1471043a5cbe03cf010c0b2e3dff293370c79b2273aa70a02261bdd759
---

# verl：RL 数据流、训练后端、动态批次与权重同步指南

## 1. 定位和版本边界

verl 将 rollout、reward、reference/value、advantage 与 actor 更新表达成分布式数据流，并接入 FSDP/FSDP2、Megatron 等训练和 vLLM/SGLang 等生成后端。优化对象是整个 RL 迭代的关键路径，训练 kernel 高效不代表生成、调度和权重发布同样高效。

本页固定官方 `verl-project/verl` main；旧 `volcengine` 的来源 ID 为兼容保留。HCU 的 verl-das 可能采用 **父补丁仓 + third_party/verl 固定子模块**，以 HCU-Knowledge 确认实际 gitlink、注入入口和依赖版本，不能把本页 main 直接替换当前主体，也不套用顶层 `pip install -e .`。本轮没有 HCU 训练运行。

## 2. 工程地图

| 入口 | 职责、下一层 |
| --- | --- |
| [`verl/trainer/main_ppo.py`](https://github.com/verl-project/verl/blob/2035f58dcb06d8cad4caee107b30f4045d724367/verl/trainer/main_ppo.py) | Hydra 配置、Ray driver、TaskRunner、资源/角色选择 |
| `trainer/ppo/ray_trainer.py` | `RayPPOTrainer.fit`、rollout/训练编排、负载平衡、save/load |
| `trainer/ppo/core_algos.py` | advantage/policy loss 注册、GRPO、聚合分母；从算法名继续到函数 |
| `trainer/config/`、`workers/config/` | YAML 组合与 dataclass 校验；实际解析值比脚本覆盖项更可靠 |
| `workers/engine_workers.py` | TrainingWorker、ActorRolloutRefWorker、训练/推理与权重更新的 RPC |
| `workers/engine/` | BaseEngine、FSDP/Megatron 等模型构建、训练、参数导出与 checkpoint |
| `workers/rollout/` | replica、SGLang/vLLM 生命周期、服务和缓存 |
| `utils/seqlen_balancing.py` | token 上限、工作量估算、微批重排与原位置恢复 |
| `utils/checkpoint/`、`checkpoint_engine/` | 持久化训练状态与分离式传权重；职责不同 |
| `examples/data_preprocess/`、`examples/*_trainer/` | 数据转换与 PPO/GRPO 等可运行 recipe |
| `recipe` 子模块、`verl/experimental/` | recipe 生态和实验功能；其版本/成熟度不等同主线 |
| `tests/trainer/ppo`、`tests/utils`、`tests/workers` | CPU 算法/配置测试与设备/分布式回归 |

## 3. 安装和依赖

[官方安装](https://github.com/verl-project/verl/blob/2035f58dcb06d8cad4caee107b30f4045d724367/docs/start/install.rst)和当前 [`pyproject.toml`](https://github.com/verl-project/verl/blob/2035f58dcb06d8cad4caee107b30f4045d724367/pyproject.toml)一起读。Python 范围为 `>=3.10,<3.13`，构建使用 setuptools；GPU 后端 extras 对 Torch、推理引擎、TE/Apex、FlashAttention 等有各自组合约束。当前 main 的统一依赖方案包含 CUDA 导向的软件包/轮子，不应直接安装来覆盖 HCU 镜像已有栈。

在官方匹配环境中可按所选 backend 安装源码及所需 extra；HCU 中先确认 HCU 仓是否完整 Python 包、是否通过子模块和 patch 注入、镜像里已有的包，以及实际 import 路径。记录 model checkpoint、tokenizer、Torch/DTK、Megatron/Bridge、rollout 引擎、通信库和 gitlink。`requirements` 中的浮动 Git main 仍需记录解析 SHA。

README 说明 `recipe` 已迁到独立 `verl-project/verl-recipe`，需要时 `git submodule update --init --recursive recipe`；不是自动把所有 recipe 安装到 Python 环境。TaskRunner 的 Ray runtime_env 与本地 shell 不必相同，核对 worker 内的最终变量、依赖路径和可见卡。

## 4. 启动、配置和测试

官方从 `examples/ppo_trainer/`、`examples/grpo_trainer/` 的具体模型脚本进入 `python -m verl.trainer.main_ppo`；填齐数据/模型路径、trainer 节点/卡数和 actor/rollout backend。模型、算法、数据与角色并行度组成一套配方，不能从多个示例拼出一个未经验证的组合。

基础参数分别控制：`data.train_batch_size` 的 prompt 数，`rollout.n` 的每 prompt response 数，`actor.ppo_mini_batch_size` 的更新 mini batch，固定 micro batch 或动态 token budget，训练 TP/PP/CP/EP 和 rollout TP。并行组中的卡数不都算独立样本。

分层验证：配置 dataclass/算法测试 → 多 rank 单次 actor 前反向 → rollout/权重同步闭环 → 数步 loss/reward/KL 有限及保存恢复 → 稳态性能。CPU 测试可以确认 mask/分母/配置，不证明 HCU kernel、collective 或 Ray 设备分配通过。

## 5. 模型和训练数据契约

数据预处理生成的 prompt/message、data_source/reward 选择、tokenizer/chat template、长度截断和采样参数都影响 RL 目标。生成后保留 input/response、attention/response mask、reward、UID/group、behavior logprob 与训练重算 logprob。变长重排必须保留这些字段及回原顺序映射。

同一 prompt 的多个 response 用 group index/UID 关联。GRPO outcome advantage 的 group mean/std 与 `n=1` 的特殊路径不同。`loss_agg_mode` 的 token mean、sequence mean、token sum 是不同目标/尺度，不是可以无代价互换的性能参数。teacher/ref/critic 为可选角色，不能假设每个 GRPO 都有 critic。

## 6. 核心调用链

`main_ppo`/TaskRunner → 创建资源池与 worker → `RayPPOTrainer.fit` 恢复状态并初次同步权重 → 生成 response → reward/old/ref logprob 和可选 value → rollout correction/advantage → critic 与 actor 更新 → checkpoint/权重发布 → 下一批生成。

训练 driver 通过 `TrainingWorker.train_mini_batch/train_batch` 进入 BaseEngine 对应后端；Megatron 到 MCore forward/backward schedule，FSDP 到其 model/autograd。rollout 的概率是行为策略；重算的 old probability 是固定 proximal anchor；本次 optimizer 更新的当前概率又是另一份。`bypass_mode` 省重算但改变两策略/三策略与校正流程，需要数值验证。

## 7. 性能、并行与内存专题

- [动态 micro batch、负载平衡与 loss 分母](../topics/dynamic-batch-and-loss.md)：硬 token budget、DP/VPP 调度、GRPO grouping、统计/梯度一致性。
- [训练到 rollout 的权重、缓存与恢复](../topics/weight-cache-and-checkpoint.md)：naive/分离 backend、LoRA、权重/KV 内存峰值和持久化 checkpoint。

先按[性能教程](https://github.com/verl-project/verl/blob/2035f58dcb06d8cad4caee107b30f4045d724367/docs/perf/perf_tuning.rst)分开测 actor、old/ref logprob、critic、rollout prefill/decode、reward、权重传输和保存。动态批次/去 padding、并行重切、重算/offload、融合实现、推理缓存分别有约束；教程中的 NVIDIA 测量或建议不是 HCU 标称。

[`MegatronEngine`](https://github.com/verl-project/verl/blob/2035f58dcb06d8cad4caee107b30f4045d724367/verl/workers/engine/megatron/transformer_impl.py)的 dynamic CP 目前要求 DP×CP 为至少2的偶数、remove-padding；不支持 pad_to_length、多模态/value model、VPP、FP8/蒸馏等所列组合。fused linear-CE 要 uniform finite temperature。不能为减少显存把这些支持门控跳过。当前 actor schema 也包含 TorchTitan/VeOmni 等后端，不表示本页已读完每个 backend。

## 8. 精度、排障与恢复

| 问题 | 先查证 |
| --- | --- |
| actor loss 在变长批次后改变 | response mask、UID、有效 token/sequence 分母和 DP 缩放；再查后端归约 |
| rollout/prox logprob 不一致 | 同一 tokenizer、temperature、采样/attention、参数版本、是否重算/校正 |
| 共卡同步 OOM | sleep level、SGLang/vLLM 差异、先weights后KV、各 rank offload/同步完成 |
| GPU 空闲但 RL 迭代慢 | Ray RPC、reward、生成长尾、old/ref前向、同步与I/O，按role展开trace |
| HCU patch 未生效 | 父仓/子提交、注入文件、目标对象 identity、worker真实导入模块 |
| 保存目录存在但恢复找不到 | async_save完成协议、latest tracker、actor/critic分片与data.pt |

[Torch profiling](https://github.com/verl-project/verl/blob/2035f58dcb06d8cad4caee107b30f4045d724367/docs/perf/torch_profiling.md)应记录 rank/role/step；当前 TrainingWorker 在 mini batch 内推进 profiler schedule，不能把调度单位无条件当成整个 RL outer iteration。各并行域选择代表 rank，联查真实后端代码和 TraceLens。

## 9. 官方教程、PR 和维护范围

[官方文档](https://verl.readthedocs.io/en/latest/) · [模型/后端能力](https://verl.readthedocs.io/en/latest/models/supported.html) · [Releases](https://github.com/verl-project/verl/releases) · [PR](https://github.com/verl-project/verl/pulls) · [recipe](https://github.com/verl-project/verl-recipe)。README 的 News/Issue 链接提供特性入口，未查证一个固定统一 roadmap 时不虚构发布计划。

本地 [source map](../../upstream/source-map/volcengine-verl.md) 和[官方原文](../../upstream/docs/volcengine-verl)用于继续定位。问题无本地答案时 `wiki-search-pr "dynamic batch max token" --engine verl`，读取正文/review/diff 后查相同 commit 的训练调用者和测试；PR有用不代表已进入当前 HCU gitlink。

更新 main 或 HCU gitlink 后同时复核总览、专题、对应案例、配置 schema、backend 与 patch 签名。当前精读核心 PPO/GRPO、动态批次、Megatron 部分门控、weight sync/checkpoint；SFT/多模态/蒸馏与所有实验算法/推理 backend 尚未全量审阅，亦没有本轮 HCU实测。
