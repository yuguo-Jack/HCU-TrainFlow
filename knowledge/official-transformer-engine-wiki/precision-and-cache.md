---
id: official-transformer-engine-wiki/precision-and-cache
title: TE 低精度训练：recipe、amax、权重缓存与反向状态
engine: transformer-engine
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-transformerengine
  path: transformer_engine/common/recipe/__init__.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 086710097a7df57c68c281dd520a3e559817ffec8b44906eac98a399061e7586
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/quantization.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: d8f2cd4fa72d8343eaca912cad0d89c4f39ff5828849cda3904c640aa587a943
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/fp8.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 54a2967ad103ddcffcaf7a1d10e7d9fcfa3a290772d9239c416fff391349f3a1
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/module/base.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: be890a1c51dba21de4f22f126060191f572c51b37f803e9eb2a7d9f7f8a67d22
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/module/linear.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: a7b63f31f9607c71f71c0a93e3e90239194d63601b72aab7875dd5b57c75617e
- source: nvidia-transformerengine
  path: docs/examples/advanced_optimizations.ipynb
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 0d5d703679a7d3c16773112e8879879560a945600c168a95b27b22bc44f9a22a
- source: nvidia-transformerengine
  path: docs/features/low_precision_training/fp8_delayed_scaling/fp8_delayed_scaling.rst
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: e3930744fe783fa2311224d3d746cf15a10c3cee7fc46a9a27e4c6e8f99671d4
- source: nvidia-transformerengine-docs
  path: fp8-primer
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: b7b77e739cacb8991383baa93084bb2f12f6385eb34aaace84be6e0d3aac5126
  url: https://docs.nvidia.com/deeplearning/transformer-engine/examples/fp8_primer.html
  revision_kind: web-content-fingerprint
- source: nvidia-transformerengine-docs
  path: advanced-optimizations
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: 6d7c1eff4937a379e6a812783e475f8b10971eda810b532c43db35e81bd1a162
  url: https://docs.nvidia.com/deeplearning/transformer-engine/examples/advanced_optimizations.html
  revision_kind: web-content-fingerprint
---

# TE 低精度训练：recipe、amax、权重缓存与反向状态

## 先区分三个层次

参数的主副本、kernel 使用的量化副本、梯度/优化器状态不必同 dtype。仅看到输出 BF16，不能推断 GEMM 没用 FP8；仅开启 autocast，也不能证明权重常驻为量化格式。当前官方 `pytorch/fp8.py` 已标注为兼容旧内部导入的弃用入口，新的机制阅读以 `quantization.py` 和 recipe 为主，HCU 是否同步该变化要单独核对。

## recipe 与数据流

| recipe 类 | 阅读重点与迁移约束 |
| --- | --- |
| `DelayedScaling` | 使用历史 amax 选 scale，当前量化结果再更新历史；检查历史长度、更新时点、归约 group 与重算行为。 |
| `Float8CurrentScaling` | 根据当前 tensor 计算 scale；把 amax 计算与量化成本一起纳入测量。 |
| `Float8BlockScaling`、`MXFP8BlockScaling` | 按块的 scale、行列表示、转置与 GEMM 消费布局；不能仅改一个 dtype。 |
| `NVFP4BlockScaling`、`CustomRecipe` | 格式、缩放及可配置量化逻辑有架构限制；HCU 需先确认实现能力与数值契约。 |

从模块 forward 的输入/权重 quantizer 到 GEMM、saved tensor，再到 backward 的 grad_output、dgrad、wgrad quantizer逐项画出数据生命周期。量化布局转换、amax/scale 更新和跨 rank 同步可能带来额外 kernel/collective；这些也属于端到端开销。

## 案例：梯度累积周期内复用低精度权重

**瓶颈**：多个 microbatch 使用同一份未更新权重，重复量化增加带宽和 launch 开销。

**官方机制**：教程在累积周期的第一个 microbatch 传 `is_first_microbatch=True`，后续传 False；沿 `module/linear.py` 的 weight workspace 和 `module/base.py` 的缓存处理查实际复用路径。它依赖训练调度告诉模块何时权重发生更新。

**适用条件**：同一参数版本、兼容 recipe/布局与当前模块实现。优化器更新、重新加载 checkpoint、参数 gather、offload 或 graph 改变存储时，不能默认旧副本仍有效。主权重不变也不意味着 amax 历史不变，官方教程明确提醒启用缓存可能不逐位等价。

**验证步骤**：连续两个以上 microbatch 比较缓存开关；观察 cast/transpose 数量、缓存显存、输出及 dgrad/wgrad；跨 optimizer step 再比较，随后验证重算、checkpoint 和阶段 loss。不能只测一个 forward，也不能把长期 False 当作最快固定设置。

**回退**：恢复原模块的每次量化策略及相同数值基线，并确认没有残留缓存/graph 状态。若收益小于噪声或显存代价抵消收益，则保留原实现。

## 精度诊断

固定输入、RNG、mask、归约方式和初始权重，从首个发生偏差的层开始检查 scale/amax、饱和、舍入、cast 与累积精度。启用 FP32 主梯度融合时检查 `main_grad` 的分配、累加和清零时点。每轮做局部回归；较长 loss 在稳定的优化阶段验收，符合训练工作流原约定。

## 来源与版本复核

- [nvidia-transformerengine: transformer_engine/common/recipe/__init__.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/common/recipe/__init__.py)
- [nvidia-transformerengine: transformer_engine/pytorch/quantization.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/quantization.py)
- [nvidia-transformerengine: transformer_engine/pytorch/fp8.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/fp8.py)
- [nvidia-transformerengine: transformer_engine/pytorch/module/base.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/module/base.py)
- [nvidia-transformerengine: transformer_engine/pytorch/module/linear.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/module/linear.py)
- [nvidia-transformerengine: docs/examples/advanced_optimizations.ipynb](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/docs/examples/advanced_optimizations.ipynb)
- [nvidia-transformerengine: docs/features/low_precision_training/fp8_delayed_scaling/fp8_delayed_scaling.rst](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/docs/features/low_precision_training/fp8_delayed_scaling/fp8_delayed_scaling.rst)
- [nvidia-transformerengine-docs: fp8-primer](https://docs.nvidia.com/deeplearning/transformer-engine/examples/fp8_primer.html)
- [nvidia-transformerengine-docs: advanced-optimizations](https://docs.nvidia.com/deeplearning/transformer-engine/examples/advanced_optimizations.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码 main、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
