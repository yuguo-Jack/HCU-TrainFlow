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
reviewed_on: '2026-11-18'
retrieved_on: '2026-11-04'
sources:
- source: nvidia-transformerengine
  path: docs/installation.rst
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: e572fc6ba65d15e9092baa71c3e09e724ad344b52d7c4a28a4e854e58d36093e
- source: nvidia-transformerengine
  path: docs/envvars.rst
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 5a2bc2206a8602f90ba8ca3aa00c921f23caa5795baa3149953bad5767f4b99a
- source: nvidia-transformerengine
  path: setup.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 7329a6981de6e6fa50a86971fd914a0a3db2f08b47287694c00e468a59a32dac
- source: nvidia-transformerengine
  path: .gitmodules
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: f59cb931b9c260f59fdf31beaf800a8df536fa50eec9470b381d3bf7b1e62986
- source: nvidia-transformerengine
  path: tests/pytorch/test_numerics.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 2752df5c59a5f9dd2ff5d44c8babe7d1f9bde48931311c4a0f228298c46ec35f
- source: nvidia-transformerengine
  path: tests/pytorch/attention/test_attention_backend_selection.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
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
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 81b878962638eb81c571a5930e2b856f82299a40b6e5fb0040df97d2a6a30c9e
- source: nvidia-transformerengine
  path: tests/cpp/operator/test_swizzle.cu
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 33b698937e4b45d4b3dbbd62b647c1b8d5f6707729221c5d5be5901865f7b2f9
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/ops/basic/grouped_linear.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: d8a8dacdc5c192408a93258968e96dbd178a208b5e9c95ffcc44e5f3ed9e2823
- source: nvidia-transformerengine
  path: docs/installation.rst
  commit: 8e89d3ad8b2ce7adb9a8ad4bd5798197db16de8b
  sha256: 86372814c4a1f14ef7be6bbbfd20c707ccd63a0e0bd707cce645b4bf4263fa0e
- source: nvidia-transformerengine
  path: docs/envvars.rst
  commit: 8e89d3ad8b2ce7adb9a8ad4bd5798197db16de8b
  sha256: cc8514ad8c952a78b6a116b4f470dfeb34c035204f98e0d9cce3f9df6b4a8857
- source: nvidia-transformerengine
  path: tests/pytorch/attention/test_attention_backend_selection.py
  commit: 8e89d3ad8b2ce7adb9a8ad4bd5798197db16de8b
  sha256: 45bdbad3fcf424a0344cdf926cddfda0a8908530e482f72c38e26198b406d56f
- source: nvidia-transformerengine-docs
  path: environment-variables
  commit: 72dfe3c00c835bfb71c36479763bab8eeae6d77778d3365ad380723d9ea62843
  sha256: 48987109228001ee0c9a3c7bfbf44764a3913476a58b5b3eb24add35f140acf6
- source: nvidia-transformerengine-docs
  path: installation
  commit: 72dfe3c00c835bfb71c36479763bab8eeae6d77778d3365ad380723d9ea62843
  sha256: b7e910d5d655fb7af9f95d848f5314d6e93a4adec822665d6f503de9ee85ed17
---

# TE 安装、运行、单测与 HCU 环境接入

## 环境与构建边界

官方安装教程面向 NVIDIA：CUDA、驱动、cuDNN、框架扩展需匹配。训练工作流不要为了查 Wiki 在本地主控安装 CUDA/TE，也不要用 NVIDIA wheel 覆盖 HCU 环境已有的 TE。先查实际模型环境中 TE 来自镜像、wheel 还是源码编译，并核对模块路径及动态库解析。

官方源码参考安装步骤为：选择具体 tag/commit，按该提交初始化所需 submodule，再按 `docs/installation.rst` 构建；PyTorch 路径的示例安装形式为 `python -m pip install --no-build-isolation '.[pytorch]'`。它需要已经满足构建依赖的 NVIDIA 环境。HCU 运行使用 HCU 工程对应脚本，保留其 DTK、编译器、通信库和框架配置。

## 当前官方依赖与分发诊断

固定 `8e89d3ad8b2c` 的安装文档要求 cuDNN Frontend≥1.31.0、PyTorch≥2.8，JAX 路线≥0.5.3；它们是该 NVIDIA 版本的条件，HCU 仍按自身分支、镜像和 ABI 核对，不自动替换已有训练依赖。

CuTeDSL 路线要求构建时启用且满足 `apache-tvm-ffi`、`nvidia-cutlass-dsl>=4.8.0` 与 Python 条件。旧 `NVTE_WARN_IF_CUTEDSL_BACKEND_NOT_CHOSEN` 已由 `NVTE_REPORT_IF_CUTEDSL_BACKEND_NOT_CHOSEN=WARN|ERROR` 取代，只在启用 CuTeDSL 时生效：WARN 保留说明后回退，ERROR 拒绝该回退。诊断变量不能证明已实际命中目标 kernel，也不能直接作为 HCU 环境变量清单。

官网2.21.0的环境变量页仍展示旧 `NVTE_WARN_IF_CUTEDSL_BACKEND_NOT_CHOSEN`，而所选 main `8e89d3ad8b2c` 已采用上述 REPORT 变量；官网安装页与主干的新依赖下限也分别记录。按实际安装版本选择说明，不能混用网页发行版本和开发树的开关。

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

2026-11-04 的源码仍保留原安装和测试入口；新增的 `te_device_type()` 路由不等于所有设备后端已可用。`NVTE_CUDNN_MXFP8_NORM_OUTPUT_IN_INPUT_DTYPE` 仅在 cuDNN≥9.25 时允许归一化的虚拟输出沿用 FP16/BF16 输入类型，以匹配该融合 engine；默认仍为 FP32。它改变中间舍入点，应随实际 norm→量化→GEMM 数值验证，不能当无精度影响的安装开关。

当前 grouped fusion 的旧环境门禁已改为 ops.GroupedLinear 显式 `split_alignment` 合同，单 grouped 参数也不再由旧环境变量授权；设备/recipe/native GroupedTensor 能力仍是独立门禁。升级时同时看[融合专题](../topics/fusion-and-profiling.md)与 [attention 选择条件](../topics/attention.md)，不能因旧变量消失就推断新路径无约束。测试存在和 host monkeypatch 选择测试都不替代实际 GPU 数值回归。

- [nvidia-transformerengine: docs/installation.rst](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/installation.rst)
- [nvidia-transformerengine: docs/envvars.rst](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/envvars.rst)
- [nvidia-transformerengine: setup.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/setup.py)
- [nvidia-transformerengine: .gitmodules](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/.gitmodules)
- [nvidia-transformerengine: tests/pytorch/test_numerics.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/tests/pytorch/test_numerics.py)
- [nvidia-transformerengine: tests/pytorch/attention/test_attention_backend_selection.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/tests/pytorch/attention/test_attention_backend_selection.py)
- [nvidia-transformerengine-docs: installation](https://docs.nvidia.com/deeplearning/transformer-engine/installation.html)
- [nvidia-transformerengine-docs: environment-variables](https://docs.nvidia.com/deeplearning/transformer-engine/envvars.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## 量化布局开关的版本核对

当前官方新增 `NVTE_MXFP8_PER_TILE_SWIZZLE`，作用于 MXFP8 tile scale 的排列/量化路径；它不是 HCU 通用调优环境变量。测试需核对 GEMM 消费的 swizzled scale 与 rowwise/columnwise 输出契约，不能只比较 logical shape。遇到切换后数值或性能变化，先回到实际 dispatcher 与 quantizer，再决定是否存在额外重排或 fallback；本轮没有测量其 HCU 收益。

补充固定证据：

- [transformer_engine/common/cast/mxfp8/group_quantize_mxfp8.cuh](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/common/cast/mxfp8/group_quantize_mxfp8.cuh)
- [tests/cpp/operator/test_swizzle.cu](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/tests/cpp/operator/test_swizzle.cu)

## 本次补充的实现与测试依据

- [nvidia-transformerengine: transformer_engine/pytorch/ops/basic/grouped_linear.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/ops/basic/grouped_linear.py)
