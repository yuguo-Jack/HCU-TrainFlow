---
id: official-torchtitan-wiki/training-and-numerics
title: TorchTitan 训练循环、有效 token、优化器与数值诊断
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
  path: torchtitan/trainer.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: e7a7162304a1741cfa86ef7969d7619f985f2263f9aace617bdc6955185c41f4
- source: pytorch-torchtitan
  path: torchtitan/training_engine.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 9c6293218d8c0a6ea50e3e1ac060d8a78b6df8eae4156009f7868016f7b6cdfd
- source: pytorch-torchtitan
  path: torchtitan/components/optim/optim.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 64d864818e84d702cc4e517773cf153f2c4e74356d36987e40ae7a397b44845c
- source: pytorch-torchtitan
  path: torchtitan/components/optim/optimizer.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 8ab40fd78a9f1c8509db8bd71b418bd2aeba3a57ba0666f5ec4de89e4aee8f4b
- source: pytorch-torchtitan
  path: torchtitan/components/optim/BF16_OPTIMIZER_STATES.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 4f0d88ff7b4b6149e86988f451b2698b6446ebf57b22fcb27f45d4ef671ac549
- source: pytorch-torchtitan
  path: torchtitan/distributed/fsdp.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 572effd3ae6d6d0e65c436cac17fbeecbd0927a1c41eaa166bb98884da0b6377
- source: pytorch-torchtitan
  path: torchtitan/rl/BITWISE_PARITY.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: e2d8599828473b3abd1f7beb8db39606d27870602bbcc21279c072175dac0144
pr_sources:
- pr-pytorch--torchtitan-5250
- pr-pytorch--torchtitan-5137
---

# TorchTitan 训练循环、有效 token、优化器与数值诊断

## 调用链与职责

`train.main` 加载 Config 并构建 Trainer；监督训练由 `Trainer.train` 进行 checkpoint 加载、逐步训练、保存、验证与 profiler 推进。`Trainer.train_step` 组织 microbatch groups 和有效 token，调用 `TrainingEngine.forward_backward`，然后 `optim_step`，最后计算日志指标。`TrainingEngine` 统一模型/优化器/状态接口，RL 在另一个循环里复用它。

因此 loss 错误可能来自数据与 token 分母，吞吐下降可能来自 checkpoint/validation，梯度丢失可能来自 graph 或原地累积。只比较模型 forward 不足以解释整个训练步骤。

## Token 预算与归一化

令每 DP rank 的 microbatch token 预算为 `Tmicro`，PP microbatch 数为 `Npp`，DP degree 为 `Ddp`，则一个 accumulation 单元对应 `Tmicro × Npp × Ddp` 的配置 token 预算。`num_tokens_per_train_step` 必须与该单位相容，Trainer 由它计算梯度累积次数；实际参与 loss 的 token 还要扣除 mask/padding。

`loss_token_counts` 与 MoE `routing_token_counts` 分开统计。Trainer 汇总有效 loss token，再给引擎计算对应缩放；日志以 token 加权归约，不应变成各 rank 平均 loss 的简单平均。该实现把 FSDP gradient divide factor 设为 1，以配合显式 loss 归一化；移植时再除一次 DP 会改变梯度。

检查顺序：同输入和 mask → 每 rank token 数 → 全局有效分母 → microbatch/累积/CP 分配 → loss reduction → 反向缩放 → optimizer update。SFT、变长或 RL 场景尤其不能仅检查最终一个 loss 标量。

## 优化器步骤与状态

`Optim` 负责 clip grad norm、跨域非有限检查、参数更新与 scheduler。当前更新前要求 loss 和 grad norm 为有限值；遇到 NaN/Inf 应保留第一个异常的层、rank、输入和状态，不能靠把日志中的 NaN 隐去或扩大容差继续。

核对参数 pattern 的归属、foreach/fused 实际分发、Muon 与 AdamW 的职责、step 计数、LR、weight decay、累积和 zero_grad。graph replay、原地 WGRAD 或分离 dInput/dWeight 的 PP schedule 都会影响 `.grad` 的所有权；见 [WGRAD 案例](cases/inplace-wgrad-accumulation.md)。

BF16 optimizer states 将 Adam/AdamW moment 与模型计算精度解耦：参数/主权重、前向计算、通信归约、moment dtype 分别记录。官方方案要求匹配的 fused optimizer，通过 hook 创建/恢复 BF16 moments；加载时仍可能出现临时 FP32 峰值。它不意味着所有 optimizer 都能直接改成 BF16 状态。

## 优化后的精度验证

1. 固定源码、依赖、配置、初始权重、数据及 RNG，先确认参考本身稳定。
2. 检查局部前向、输入梯度、权重梯度；低精度融合应对照同 dtype 实现，必要时追加高精度 oracle。不要把高精度更近直接当作与原训练相同。
3. 检查一次 optimizer update 后参数与状态，再验证多 microbatch、多个 DP/TP/CP/EP/PP 组合的真实通信。
4. 采用短回归筛查和阶段性 loss/质量验证；不为每次低风险局部修改重复长训，但归约次序、优化器、量化或数据语义改变不能仅用几步无 NaN 放行。
5. 没有 NVIDIA 对照时，使用同 HCU 环境保守实现/关闭融合前的固定基线、逐层 tensor 与状态比较；有对照时还需同模型、同数据、同训练语义，不能把不同引擎默认差异归咎于硬件。

源代码、上游 golden、作者在某 GPU 的测试与本任务 HCU 验证分别记录。修改 golden 必须有机制解释和证据，不为通过测试直接接受更大的误差。

## 常见定位入口

| 现象 | 优先核查 |
| --- | --- |
| DP/packing 一变 loss 就变 | 有效 token 分母、mask、重复缩放、数据顺序 |
| 首步一致，累积后偏离 | WGRAD 舍入位置、zero_grad、累积次数、dropout/recompute RNG |
| loss 正常但参数不动 | `.grad` 是否丢失、optimizer pattern、graph replay、有限检查 |
| checkpoint 恢复后突变 | optimizer/scheduler/step/RNG/数据游标，以及导出是否 model-only |
| RL trainer/generator logprob 不同 | policy 版本、TP/attention/序列布局、计算 dtype、采样与批次不变性 |

工作流中的 HCU Probe、阶段 loss 及上层精度诊断见 [模型精度排查](../../docs/practices/model-accuracy-diagnosis.md)。

## 固定证据与使用边界

本页以官方主线 `65aaaa960698ab5d6e98c874177b41b9c30e9c58` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/trainer.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/trainer.py)
- [torchtitan/training_engine.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/training_engine.py)
- [torchtitan/components/optim/optim.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/components/optim/optim.py)
- [torchtitan/components/optim/optimizer.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/components/optim/optimizer.py)
- [torchtitan/components/optim/BF16_OPTIMIZER_STATES.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/components/optim/BF16_OPTIMIZER_STATES.md)
- [torchtitan/distributed/fsdp.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/distributed/fsdp.py)
- [torchtitan/rl/BITWISE_PARITY.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/rl/BITWISE_PARITY.md)

- [PR #5250：描述、review、评论及 diff](../prs/pytorch--torchtitan/PR-5250.md)
- [PR #5137：描述、review、评论及 diff](../prs/pytorch--torchtitan/PR-5137.md)
