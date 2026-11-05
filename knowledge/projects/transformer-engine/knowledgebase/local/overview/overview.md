---
id: official-transformer-engine-wiki/overview
title: Transformer Engine 官方工程：定位、目录与训练调用链
engine: transformer-engine
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-11-04'
retrieved_on: '2026-11-04'
sources:
- source: nvidia-transformerengine
  path: README.rst
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 7ec335c82227680e55c8047d90db0e99a87d0c10d3d6d43d7b54d54e2d5f9e0a
- source: nvidia-transformerengine
  path: .gitmodules
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: f59cb931b9c260f59fdf31beaf800a8df536fa50eec9470b381d3bf7b1e62986
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/module/linear.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: e9252b8c18270c17ea700c4417fa0314de19905eac4da63051fa6743765b2781
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/attention/dot_product_attention/dot_product_attention.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: a53e5b2a34344a195ce950f1f7556a527bb7932fbc9102efa7cd74af3ef6bcd9
- source: nvidia-transformerengine
  path: transformer_engine/common/recipe/__init__.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 5a310fcc898d08283309d10fc768a7dd1b879a73fab73b342488dfb79131b10f
- source: nvidia-transformerengine-docs
  path: index
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: ba77831cd3aa9167b13990ef74473abf53a57d33b604e39bd4f25ebae8b9e2ad
  url: https://docs.nvidia.com/deeplearning/transformer-engine/index.html
  revision_kind: web-content-fingerprint
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/module/grouped_linear.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 81285c46ceb62f2b01fe4331ca6c74de18f0ccc1f81085d5d6509b00b98ac9ce
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/attention/dot_product_attention/utils.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: a014f57a3600d9c1156d91d6e426bb4ee8fbe0418b1776dbea89be98fcc73be3
---
# Transformer Engine 官方工程：定位、目录与训练调用链

## 为什么训练工作流要单独维护 TE

TE 不仅是 FP8 开关。训练引擎把 Linear、归一化、MLP、attention、低精度状态和部分并行通信交给它；一次 Python 调用内部可能包含多个 kernel、数据重排与通信。性能变化或 loss 异常应追到实际 module、autograd 状态和底层分发，不能停在 Megatron 配置项。

官方工程以 NVIDIA 软件/硬件为目标，提供 PyTorch、JAX 及公共底层接口。本 Wiki 重点跟踪大模型 PyTorch 训练路径；JAX 入口可从官方文档扩展，未宣称逐接口覆盖。HCU 任务仍优先采用当前 HCU TE 分支已有的安装和运行方式。

## 目录导航

| 目录/文件 | 用途与适合回答的问题 |
| --- | --- |
| `transformer_engine/pytorch/module/` | Linear、LayerNormLinear/MLP、GroupedLinear 等模块；从 forward/backward、参数与梯度所有权看融合边界。 |
| `pytorch/quantization.py`、`common/recipe/`、`pytorch/tensor/` | 量化上下文、amax/scale、格式与存储布局；排查 recipe、缓存和保存恢复。 |
| `pytorch/attention/dot_product_attention/` | attention 入口、后端选择、实际实现及 context parallel；核对 fused/flash/unfused 分发。 |
| `pytorch/ops/` | 可组合算子与 OperationFuser；forward/backward 的融合组合。 |
| `pytorch/graph.py`、`cpu_offload.py`、`distributed.py` | graph 捕获、激活生命周期、分布式包装；与训练调度一起阅读。 |
| `transformer_engine/common/` | GEMM、归一化、量化、fused attention 等底层实现；设备特定路径不能视作 HCU 直接可用。 |
| `docs/`、`examples/pytorch/`、`benchmarks/gemm/`、`tests/pytorch/` | 官方教程、运行配方、独立 shape 测量与数值/后端回归。 |
| `.gitmodules`、`setup.py`、`build_tools/` | 构建入口与依赖锁；CUTLASS、googletest、NCCL 扩展的 gitlink 要随所选提交核对。 |

## 从模型到证据的路径

1. 在 Megatron layer spec/TE wrapper 或其他引擎替换层中确认实际实例化的 TE 类。
2. 从模块 forward 追 quantizer、权重 workspace、布局、process group 和 saved tensors。
3. 查看 backward 的 dgrad/wgrad、主梯度累积、额外通信与量化更新。
4. 对照 trace 中真正发出的 kernel、collective 与实际 shape；类名相同不证明使用同一种融合。
5. 回到固定提交的底层实现和测试解释差异，建立局部正确性、显存与端到端收益证据。

## 阅读入口

- [安装、测试与环境](../guides/build-run-test.md)
- [低精度与缓存](../topics/precision-and-cache.md)
- [attention 与 cuDNN 链路](../topics/attention.md)
- [并行 overlap、graph 与显存](../topics/overlap-and-memory.md)
- [融合与 GEMM 建模](../topics/fusion-and-profiling.md)
- [官方教程与更新](../changes/tutorials-and-update.md)

## 来源与版本复核

当前机制复核固定官方 main `720b25258be3b60f482afff8aef00d4cad88fa16`，原件采集与语义复核日期为2026-11-04。GroupedLinear 的模块接口、ops-fuser、分布式权重与低精度存储仍须分别追踪；本版新增 BF16 grouped MLP、按 recipe 内容区分的融合缓存，以及延后 wgrad/Graph 累加修正，不能只沿旧大函数行号查实现。attention 新增 Hopper FA4 的 Quack/CUTLASS DSL 组合拒绝条件；RMSNorm-MXFP8 既有 column-only 包装缺口仍保留，详见专题和案例。

- [nvidia-transformerengine: README.rst](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/README.rst)
- [nvidia-transformerengine: .gitmodules](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/.gitmodules)
- [nvidia-transformerengine: transformer_engine/pytorch/module/linear.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/module/linear.py)
- [nvidia-transformerengine: transformer_engine/pytorch/attention/dot_product_attention/dot_product_attention.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/attention/dot_product_attention/dot_product_attention.py)
- [nvidia-transformerengine: transformer_engine/common/recipe/__init__.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/common/recipe/__init__.py)
- [nvidia-transformerengine-docs: index](https://docs.nvidia.com/deeplearning/transformer-engine/index.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## 新增精读路线

- [RMSNorm→MXFP8 融合](../cases/rmsnorm-mxfp8-fusion.md)：分发条件、两向量化布局、FP32 reference、workspace、上限估计及当前 Python column-only 入口缺口。
- [Grouped MLP 低精度权重布局](../cases/grouped-mlp-weight-layout.md)：NVFP4 单 group 的物理转置与逻辑形状、MXFP8 独立表示、前后向回归。

二者供发现融合和精度问题时按需联查；现有 HCU TE/Flash-Train 能力仍通过 HCU-Knowledge 与实际依赖分支确认。

## 本次补充的实现与测试依据

- [nvidia-transformerengine: transformer_engine/pytorch/module/grouped_linear.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/module/grouped_linear.py)
- [nvidia-transformerengine: transformer_engine/pytorch/attention/dot_product_attention/utils.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/attention/dot_product_attention/utils.py)
