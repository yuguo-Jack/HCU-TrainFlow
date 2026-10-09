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
reviewed_on: '2026-10-09'
sources:
- source: nvidia-transformerengine
  path: README.rst
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 7ec335c82227680e55c8047d90db0e99a87d0c10d3d6d43d7b54d54e2d5f9e0a
- source: nvidia-transformerengine
  path: .gitmodules
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: f59cb931b9c260f59fdf31beaf800a8df536fa50eec9470b381d3bf7b1e62986
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/module/linear.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: a7b63f31f9607c71f71c0a93e3e90239194d63601b72aab7875dd5b57c75617e
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/attention/dot_product_attention/dot_product_attention.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 967c475fa391f5d7748a9ea8f8cb5da7a109ed5efdb291174cd10ab63a55b201
- source: nvidia-transformerengine
  path: transformer_engine/common/recipe/__init__.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 086710097a7df57c68c281dd520a3e559817ffec8b44906eac98a399061e7586
- source: nvidia-transformerengine-docs
  path: index
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: ba77831cd3aa9167b13990ef74473abf53a57d33b604e39bd4f25ebae8b9e2ad
  url: https://docs.nvidia.com/deeplearning/transformer-engine/index.html
  revision_kind: web-content-fingerprint
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

- [安装、测试与环境](build-run-test.md)
- [低精度与缓存](precision-and-cache.md)
- [attention 与 cuDNN 链路](attention.md)
- [并行 overlap、graph 与显存](overlap-and-memory.md)
- [融合与 GEMM 建模](fusion-and-profiling.md)
- [官方教程与更新](tutorials-and-update.md)

## 来源与版本复核

- [nvidia-transformerengine: README.rst](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/README.rst)
- [nvidia-transformerengine: .gitmodules](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/.gitmodules)
- [nvidia-transformerengine: transformer_engine/pytorch/module/linear.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/module/linear.py)
- [nvidia-transformerengine: transformer_engine/pytorch/attention/dot_product_attention/dot_product_attention.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/attention/dot_product_attention/dot_product_attention.py)
- [nvidia-transformerengine: transformer_engine/common/recipe/__init__.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/common/recipe/__init__.py)
- [nvidia-transformerengine-docs: index](https://docs.nvidia.com/deeplearning/transformer-engine/index.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码 main、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
