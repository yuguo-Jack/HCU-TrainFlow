---
id: official-transformer-engine-wiki/build-run-test
title: TE 安装、运行、单测与 HCU 环境接入
engine: transformer-engine
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-20'
sources:
- source: nvidia-transformerengine
  path: docs/installation.rst
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: e572fc6ba65d15e9092baa71c3e09e724ad344b52d7c4a28a4e854e58d36093e
- source: nvidia-transformerengine
  path: docs/envvars.rst
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 7d0f440d41ba1122259bbc2d5daaf7892fd0e87de1fa17a79c2f185b1c8adf2d
- source: nvidia-transformerengine
  path: setup.py
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 7329a6981de6e6fa50a86971fd914a0a3db2f08b47287694c00e468a59a32dac
- source: nvidia-transformerengine
  path: .gitmodules
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: f59cb931b9c260f59fdf31beaf800a8df536fa50eec9470b381d3bf7b1e62986
- source: nvidia-transformerengine
  path: tests/pytorch/test_numerics.py
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 2752df5c59a5f9dd2ff5d44c8babe7d1f9bde48931311c4a0f228298c46ec35f
- source: nvidia-transformerengine
  path: tests/pytorch/attention/test_attention_backend_selection.py
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 351675d17a4fa6dabca0a0540c4b6c28ec6aa67bd9d78c207fee478a98d9ad90
- source: nvidia-transformerengine-docs
  path: installation
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: 7148d69a967a9a721afa6aae01a2bf9e385426a62db39f7476ca9eb381294aae
  url: https://docs.nvidia.com/deeplearning/transformer-engine/installation.html
  revision_kind: web-content-fingerprint
- source: nvidia-transformerengine-docs
  path: environment-variables
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: 271080d66a4ab1c3fb529a4cd1368163f6de97da1cf195eadbbda4296df76af7
  url: https://docs.nvidia.com/deeplearning/transformer-engine/envvars.html
  revision_kind: web-content-fingerprint
- source: nvidia-transformerengine
  path: transformer_engine/common/cast/mxfp8/group_quantize_mxfp8.cuh
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 81b878962638eb81c571a5930e2b856f82299a40b6e5fb0040df97d2a6a30c9e
- source: nvidia-transformerengine
  path: tests/cpp/operator/test_swizzle.cu
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 3d9909e1dc3729afbf6667169bf9e89a26f1a982afd822b44dd82da881c18d59
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/ops/basic/grouped_linear.py
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: eee951ca3e44e2569e87fb093dd9bd13278af19c5b5beff680023c0e71341143
---

# TE 安装、运行、单测与 HCU 环境接入

## 环境与构建边界

官方安装教程面向 NVIDIA：CUDA、驱动、cuDNN、框架扩展需匹配。训练工作流不要为了查 Wiki 在本地主控安装 CUDA/TE，也不要用 NVIDIA wheel 覆盖 HCU 环境已有的 TE。先查实际模型环境中 TE 来自镜像、wheel 还是源码编译，并核对模块路径及动态库解析。

官方源码参考安装步骤为：选择具体 tag/commit，按该提交初始化所需 submodule，再按 `docs/installation.rst` 构建；PyTorch 路径的示例安装形式为 `python -m pip install --no-build-isolation '.[pytorch]'`。它需要已经满足构建依赖的 NVIDIA 环境。HCU 运行使用 HCU 工程对应脚本，保留其 DTK、编译器、通信库和框架配置。

## 安装证据清单

记录 TE 提交/包版本、框架版本、编译器、所加载共享库、目标架构、cuDNN 或 HCU 对应依赖、子仓 gitlink。官方 `NVTE_FRAMEWORK`、`NVTE_CUDA_ARCHS`、NVRTC/fast-math 等选项各有作用域；当前分支是否支持、是在构建时还是运行时读取，都须查源码。fast-math 涉及精度，不能当无副作用的安装加速选项。

构建错误先分 Python 扩展、C++ ABI、头文件、链接库与目标 ISA；导入成功之后仍核对实际设备分发。旧 build/cache 导致加载另一份库时，先定位缓存与 import 路径，再在明确工作目录重建，避免删除共享环境内容。

## 测试递进

| 层次 | 操作与验收 |
| --- | --- |
| 导入与单模块 | 在已授权目标环境用实际解释器导入，运行小 Linear/Norm；保存版本和实际调用。 |
| 数值回归 | 参考 `tests/pytorch/test_numerics.py` 的模块/精度参数，比较输出、dgrad、wgrad 和参数更新。 |
| 后端选择 | 阅读 `tests/pytorch/attention/test_attention_backend_selection.py`，核对特性组合会选择或拒绝什么实现。 |
| 层级融合 | 同 shape、layout、mask、RNG、recipe 比较未融合参考与 TE，确认 saved tensors 与反向完整。 |
| 训练集成 | 多 microbatch、重算、graph、checkpoint 和对应并行域回归；阶段候选稳定后验 loss。 |

在 NVIDIA 配套环境可先运行 `python -m pytest --collect-only -q tests/pytorch/test_numerics.py` 查看当前版本用例，再选择匹配模型的测试。收集成功、skip 或 fallback 不代表算子通过；HCU 分支的测试入口可能不同，必须从其脚本核实。没有 NV 环境仍可用独立高精度参考与 HCU 已验证基线建立局部证据。

## 来源与版本复核

当前 grouped fusion 的旧环境门禁已改为 ops.GroupedLinear 显式 `split_alignment` 合同，单 grouped 参数也不再由旧环境变量授权；设备/recipe/native GroupedTensor 能力仍是独立门禁。升级时同时看[融合专题](../topics/fusion-and-profiling.md)与 [attention 选择条件](../topics/attention.md)，不能因旧变量消失就推断新路径无约束。测试存在和 host monkeypatch 选择测试都不替代实际 GPU 数值回归。

- [nvidia-transformerengine: docs/installation.rst](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/docs/installation.rst)
- [nvidia-transformerengine: docs/envvars.rst](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/docs/envvars.rst)
- [nvidia-transformerengine: setup.py](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/setup.py)
- [nvidia-transformerengine: .gitmodules](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/.gitmodules)
- [nvidia-transformerengine: tests/pytorch/test_numerics.py](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/tests/pytorch/test_numerics.py)
- [nvidia-transformerengine: tests/pytorch/attention/test_attention_backend_selection.py](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/tests/pytorch/attention/test_attention_backend_selection.py)
- [nvidia-transformerengine-docs: installation](https://docs.nvidia.com/deeplearning/transformer-engine/installation.html)
- [nvidia-transformerengine-docs: environment-variables](https://docs.nvidia.com/deeplearning/transformer-engine/envvars.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## 量化布局开关的版本核对

当前官方新增 `NVTE_MXFP8_PER_TILE_SWIZZLE`，作用于 MXFP8 tile scale 的排列/量化路径；它不是 HCU 通用调优环境变量。测试需核对 GEMM 消费的 swizzled scale 与 rowwise/columnwise 输出契约，不能只比较 logical shape。遇到切换后数值或性能变化，先回到实际 dispatcher 与 quantizer，再决定是否存在额外重排或 fallback；本轮没有测量其 HCU 收益。

补充固定证据：

- [transformer_engine/common/cast/mxfp8/group_quantize_mxfp8.cuh](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/transformer_engine/common/cast/mxfp8/group_quantize_mxfp8.cuh)
- [tests/cpp/operator/test_swizzle.cu](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/tests/cpp/operator/test_swizzle.cu)

## 本次补充的实现与测试依据

- [nvidia-transformerengine: transformer_engine/pytorch/ops/basic/grouped_linear.py](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/transformer_engine/pytorch/ops/basic/grouped_linear.py)
