---
id: official-transformer-engine-wiki/cases/grouped-mlp-weight-layout
title: 案例：单 group NVFP4 MLP 的权重视图为什么不能照搬 MXFP8
engine: transformer-engine
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tests-reviewed
runtime_validated: false
reviewed_on: '2026-10-20'
sources:
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/ops/fused/grouped_mlp.py
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 213bc372954fe0b142ccf360476524f8389ab63749574e4560bdbd4f28c7574c
- source: nvidia-transformerengine
  path: tests/pytorch/test_grouped_mlp.py
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 09685ac90c632b46ad5eafb3642ab97484b9ceddc09bd80171ea1064ae0ca6c2
pr_sources:
- pr-nvidia--transformerengine-3662
---

# 案例：单 group NVFP4 MLP 的权重视图为什么不能照搬 MXFP8

## 问题与修复动机

官方 [PR #3662](https://github.com/NVIDIA/TransformerEngine/pull/3662) 修复 single-group fused grouped MLP 的 NVFP4 weight views。MoE 在单专家/group 的快速路径仍要保留 packed data、logical K 与 scale 布局；group 数为一并不意味着任意 dense GEMM 视图都等价。

## 前后向调用链

在 `grouped_mlp.py` 的 `fuser_forward`，FC1 的 scale 视图使用实际 `fc1_weight_k` 而非直接套原 weight shape 的第二维。`fuser_backward` 中 FC2 dactivation 使用 columnwise 权重；NVFP4 的这份数据已经物理转置，不能再沿 MXFP8 的 reshape/permute 路线解释。

新 NVFP4 路径调用 `_convert_to_cudnn_grouped_gemm_tensor_format`，显式传入 logical K、有效 M/N、数据/scale dtype 与 `sf_swizzled=True`。MXFP8 分支保留自己的数据和 scale permutation。消费者最终是 cuDNN grouped GEMM 融合入口，必须同时核对这两个工程的格式契约。

## 为什么会影响优化判断

single-group fast path 可能在小规模验证或专家偏斜后出现。如果只测多 group BF16 前向，能避开此问题；“融合快且 shape 相同”仍不能证明反向用了正确的 packed 权重。比较时区分逻辑维度、物理字节、padding、scale tile，以及 fwd/dgrad/wgrad 对权重的不同视图。

## 验证矩阵与诊断

- group=1 与多 group，NVFP4/MXFP8/BF16 可用路径分别测，不把 recipe 名称当可互换布局。
- 单独验证 FC1/FC2 前向、dactivation、输入梯度、weight gradient，再测完整 MLP 与优化器 step。
- 在对应测试中追参数化的 shape、activation 和数值容差；检查实际调用 backend，跳过不算通过。
- 出现 shape/view 错误先查逻辑 K 与 scale storage，出现 silent mismatch 则找第一个差异 tensor，而不是一开始调宽 loss 容差。

## 冻结权重与 no_grad 的单 group 路径

`eb3c860a4d33` 进一步修正 FC2 的 dense single-group 选择：需要 weight gradient 时仍检查 columnwise activation data/scale；冻结权重或 no_grad 不需要该保存量，应允许 dense 路径，不能因 columnwise 缺失误入 grouped cuBLAS。这个判断保留原 packed 权重视图合同，没有把 NVFP4 与 MXFP8 合成同一种格式。

新测试分别覆盖 frozen_weights（仍对输入反传）和 no_grad，参数无梯度，同时核验实际 fused op。reference 先恢复指定的 GLU 交错布局；测试只用宽松 sanity 容差，不是全部权重梯度、完整模型 loss 或任意 shape 的精度承诺。接入时还需满足[融合准入与 split alignment](../topics/fusion-and-profiling.md#grouped-mlp-的当前准入与参数重置)，显式检查 fusion on/off 的消费者。

## HCU 迁移与回退

借鉴的是“低精度格式、前后向视图与 group 快速路径一起验收”，不是要求 HCU 支持 NVFP4。先看 HCU TE/Primus Turbo 的实际 dtype、layout 和数学库接口；新融合必须沿用其约定。无法证明跨 group/反向正确时关闭该融合并保留原模块，只有局部回归与模型阶段数值合格后保留性能候选。

## 固定源码

- [transformer_engine/pytorch/ops/fused/grouped_mlp.py](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/transformer_engine/pytorch/ops/fused/grouped_mlp.py)
- [tests/pytorch/test_grouped_mlp.py](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/tests/pytorch/test_grouped_mlp.py)

本文为官方源码、接口与测试阅读，未运行这些 NVIDIA 实现，不声称 HCU 支持或获得相同性能。
