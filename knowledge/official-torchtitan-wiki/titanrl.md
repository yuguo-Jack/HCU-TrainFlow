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
reviewed_on: '2026-10-12'
coverage: Curated source chains and official evidence at a fixed main commit; not
  all models, backends or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/rl/README.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: ccb29a904363f34a929b2cc28ca4ee423f638352f70ac4202f34f1c06e579d0a
- source: pytorch-torchtitan
  path: torchtitan/rl/train.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 7a6ce29b3feccac7bd9b710b732266a7beab26079d04c8d8efc6701f0b88095e
- source: pytorch-torchtitan
  path: torchtitan/rl/trainer.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 77eea0ae2d0db6b99c65a68db1db7b1844e38be0367d421f776eba2da92f82de
- source: pytorch-torchtitan
  path: torchtitan/rl/generator.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 109291afc2d11a6a0ccc39cd93374c32b9809ba003c82eb9966b9633eb415569
- source: pytorch-torchtitan
  path: torchtitan/rl/distributed/WEIGHT_SYNC.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: f04cf9beb18c900eab1c2aff5d079e1fe4fa4db03fda74286cf72ebd6ff3e669
- source: pytorch-torchtitan
  path: torchtitan/rl/BITWISE_PARITY.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: e2d8599828473b3abd1f7beb8db39606d27870602bbcc21279c072175dac0144
- source: pytorch-torchtitan
  path: torchtitan_recipes/rl/model_configs.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 5ab4c39072e7b2b29addc5a7e5004520c8bfb886ce49e389a73a4810869653b4
- source: pytorch-torchtitan
  path: torchtitan/rl/observability/metrics/README.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 11b5fd3963900a52094028d4b2e35ee4ce1761d4f45d19e902052d1e74e9e1d6
pr_sources:
- pr-pytorch--torchtitan-5107
- pr-pytorch--torchtitan-5268
- pr-pytorch--torchtitan-5280
---

# TitanRL：训练生成协同、权重同步与精度边界

## 组件分工

TitanRL 由 Controller 协调 trainer、generator、rollouter、数据、环境/奖励和 work buffer；以 Monarch 组织进程与任务，使用 TorchStore 等路径同步权重，生成侧可由 vLLM 对接 TorchTitan 模型。训练侧复用 `TrainingEngine`，并非把监督 Trainer 的一轮循环直接改个 loss。

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

训练侧不能把仍会被 optimizer 修改的 GPU tensor view 直接作为已发布快照；共享 pinned buffer 也不能在生成端仍读取时覆盖。等待 GPU event/阻塞 PUT 放到线程中避免卡住 asyncio loop，不代表取消同步。详细源码和上游证据见 [权重同步案例](cases/rl-weight-sync-memory.md)。

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

## 固定证据与使用边界

本页以官方主线 `65aaaa960698ab5d6e98c874177b41b9c30e9c58` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/rl/README.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/rl/README.md)
- [torchtitan/rl/train.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/rl/train.py)
- [torchtitan/rl/trainer.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/rl/trainer.py)
- [torchtitan/rl/generator.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/rl/generator.py)
- [torchtitan/rl/distributed/WEIGHT_SYNC.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/rl/distributed/WEIGHT_SYNC.md)
- [torchtitan/rl/BITWISE_PARITY.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/rl/BITWISE_PARITY.md)
- [torchtitan_recipes/rl/model_configs.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan_recipes/rl/model_configs.py)
- [torchtitan/rl/observability/metrics/README.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/rl/observability/metrics/README.md)

- [PR #5107：描述、review、评论及 diff](../prs/pytorch--torchtitan/PR-5107.md)
- [PR #5268：描述、review、评论及 diff](../prs/pytorch--torchtitan/PR-5268.md)
- [PR #5280：描述、review、评论及 diff](../prs/pytorch--torchtitan/PR-5280.md)
