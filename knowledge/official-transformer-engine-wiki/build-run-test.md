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
reviewed_on: '2026-10-09'
sources:
- source: nvidia-transformerengine
  path: docs/installation.rst
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: e572fc6ba65d15e9092baa71c3e09e724ad344b52d7c4a28a4e854e58d36093e
- source: nvidia-transformerengine
  path: docs/envvars.rst
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 38ecf02281c2f6f6e0f06d09b6e388c418091b284f203a262e8bcc8ef06b2cc1
- source: nvidia-transformerengine
  path: setup.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 7329a6981de6e6fa50a86971fd914a0a3db2f08b47287694c00e468a59a32dac
- source: nvidia-transformerengine
  path: .gitmodules
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: f59cb931b9c260f59fdf31beaf800a8df536fa50eec9470b381d3bf7b1e62986
- source: nvidia-transformerengine
  path: tests/pytorch/test_numerics.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 2752df5c59a5f9dd2ff5d44c8babe7d1f9bde48931311c4a0f228298c46ec35f
- source: nvidia-transformerengine
  path: tests/pytorch/attention/test_attention_backend_selection.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: e0ee6f26e308ab0481f6bb7a12f88b1a1ffdf4a4a19f9e294ace495cab2de252
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

- [nvidia-transformerengine: docs/installation.rst](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/docs/installation.rst)
- [nvidia-transformerengine: docs/envvars.rst](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/docs/envvars.rst)
- [nvidia-transformerengine: setup.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/setup.py)
- [nvidia-transformerengine: .gitmodules](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/.gitmodules)
- [nvidia-transformerengine: tests/pytorch/test_numerics.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/tests/pytorch/test_numerics.py)
- [nvidia-transformerengine: tests/pytorch/attention/test_attention_backend_selection.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/tests/pytorch/attention/test_attention_backend_selection.py)
- [nvidia-transformerengine-docs: installation](https://docs.nvidia.com/deeplearning/transformer-engine/installation.html)
- [nvidia-transformerengine-docs: environment-variables](https://docs.nvidia.com/deeplearning/transformer-engine/envvars.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码 main、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
