---
id: official-torchtitan-wiki/cases/kimi-attnres-fusion
title: 案例：Kimi Attention Residual 融合很快，模型却未必更快
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
  path: torchtitan_recipes/overrides/kimi_attention_residual.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 3782d82d0a72504e572969d3cdf3310dae6b29949910f131d7a9c4cda1a2ea3a
- source: pytorch-torchtitan
  path: torchtitan/models/kimi_k3/model.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: f90afaa388115abfb172d301c651c4444cba043272dbd43ab486403a8ed0575d
- source: pytorch-torchtitan
  path: torchtitan/models/kimi_k3/flavors.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: d09991c1bd12a012e9e02f3920c9babd2ca76cc044fdf2e9f98db942e479f4ca
- source: pytorch-torchtitan
  path: tests/unit_tests/gpu/recipes/test_kimi_attention_residual_override.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 606950a04de407e9aba9fae1f437f3f885976e4effb5f82b0f9610dec29c0ce2
- source: pytorch-torchtitan
  path: tests/unit_tests/gpu/models/kimi_k3/test_kimi_k3_attention_residual.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: a4e05aeade29b718bf179df8dea3ac14133a5cdff8fe60846852cc30931ad5f6
pr_sources:
- pr-pytorch--torchtitan-5033
---
# 案例：Kimi Attention Residual 融合很快，模型却未必更快

## 瓶颈与实现边界

Kimi K3 Attention Residual 对 residual bank `[T,N,D]` 和可选 partial residual `[T,D]` 做归一化、评分、跨来源 softmax 及加权聚合。eager 路径可能产生多个 kernel 和中间张量。PR #5033 同时提供 local compile 与显式 Triton override，借鉴 FLA AttnRes 算法，并保留其来源/许可说明。

当前入口为 `torchtitan_recipes.overrides.kimi_attention_residual.triton_attention_residual`。源码直接读取模型已有 stride 布局与可选 partial，不先 concat 或大规模转置；kernel 用 FP32 累加/在线 softmax 更新，保存 rstd、logits、logsumexp 等反向所需状态，反向还需正确求输入、projection 和 norm 权重梯度。

这类融合优化的关键不只是少 launch：布局转换、临时张量、稳定 softmax、反向 reduction 与保存张量都在边界内。autotune 参数按维度、来源桶与 partial 条件选择；新 shape/新硬件必须重新确认编译、资源使用和数值。

## 上游独立算子数据

PR 作者报告 H100、BF16、`T_local=2048, N=8, D=7168`、包含 partial 的指定前向+反向测试：

| 实现 | 前向+反向时间 | 增量峰值显存 |
| --- | --- | --- |
| eager | 10.544 ms | 2.980 GiB |
| local compile | 2.470 ms | 1.351 GiB |
| Triton override | 0.723 ms | 0.328 GiB |

上述是作者的特定 shape/NVIDIA 环境数据。本工程未复测，不能直接作为 HCU 上限或预期。

## 为什么仍需端到端验收

同一 PR 的单 H100 debug-model、BF16、2048 tokens、SelectiveAC、关闭 graph 的两组 20-step 实验，按指定稳态窗口报告约：eager 4570 tokens/s、local compile 4795、Triton 4627。虽然独立算子中 Triton 比 local compile 快约 3.41 倍，端到端吞吐却比 local compile 低约 3.5%。

这些数据证明“独立算子最好”不必然是“模型最好”，但仅凭表格不能断言根因就是某种 overlap 或重算。应重采模型 trace，核对调用次数、实际选中的 kernel、保存张量、重算、融合边界、内存压力及测量波动，再决定采用哪条路径。

## 如何复用到 HCU 优化流程

1. 确认目标模型确实调用此模块且占比值得优化；根据真实 T/N/D、partial、dtype、stride、前后向频次建立基线。
2. 先比现有实现、局部编译、已有库融合。需要初始实现时用 baseline Skill，已有 Triton 进入 Triton optimizer；距可达上限仍远且证据支持时再考虑 HIP 实现。
3. 用实际读写量、FP32 reduction/softmax 等工作估计瓶颈；roofline 是有条件的下界/上限，不忽略 reduction、寄存器压力、同步和 launch。
4. 正确性涵盖有/无 partial、不同 N/D、输入及所有权重梯度；对照同 dtype 与高精度 oracle，必要时看误差分布。PR 报告的 FP64/多卡测试作为参考，不冒充本机执行。
5. 回到模型比 step time、峰值、阶段 loss 和正确 backend；保留 local compile/eager 回退。

交付应归到拥有该训练算子/模块的实际工程，并保留参考来源许可。不要为展示融合就自动在所有 recipe 启用 override。

当前测试分别在 `tests/unit_tests/gpu/recipes/test_kimi_attention_residual_override.py` 与 `tests/unit_tests/gpu/models/kimi_k3/test_kimi_k3_attention_residual.py`。前者比较同 dtype 参考与 FP64 golden 的误差、NaN/Inf 分布及梯度，后者检查 local compile 的实际 Triton 生成、前后向与 batch-invariant 性质。测试中的容差公式属于其输入/实现，不能复制为其他模型的通用验收阈值。

## 固定证据与使用边界

本页以官方主线 `65aaaa960698ab5d6e98c874177b41b9c30e9c58` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan_recipes/overrides/kimi_attention_residual.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan_recipes/overrides/kimi_attention_residual.py)
- [torchtitan/models/kimi_k3/model.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/models/kimi_k3/model.py)
- [torchtitan/models/kimi_k3/flavors.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/models/kimi_k3/flavors.py)
- [tests/unit_tests/gpu/recipes/test_kimi_attention_residual_override.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/tests/unit_tests/gpu/recipes/test_kimi_attention_residual_override.py)
- [tests/unit_tests/gpu/models/kimi_k3/test_kimi_k3_attention_residual.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/tests/unit_tests/gpu/models/kimi_k3/test_kimi_k3_attention_residual.py)

- [PR #5033：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5033.md)