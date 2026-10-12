---
id: official-cudnn-frontend-wiki/overview
title: cuDNN Frontend 官方工程：Graph、开放 Kernel 与训练调用链
engine: cudnn-frontend
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-12'
sources:
- source: nvidia-cudnn-frontend
  path: README.md
  commit: 941078f2ce6aa0a45ac5813b81760a19c616732a
  sha256: 4cabe0bbf2a76d4b5bbb1b06eae8d1de73aaf8cddb756e38903b6f62689b9279
- source: nvidia-cudnn-frontend
  path: LICENSING.md
  commit: 941078f2ce6aa0a45ac5813b81760a19c616732a
  sha256: e418507f66706a64e50b52a90888537162462f71b0baa5a2d994618ef3bd541e
- source: nvidia-cudnn-frontend
  path: include/cudnn_frontend/graph_interface.h
  commit: 941078f2ce6aa0a45ac5813b81760a19c616732a
  sha256: f83702970e63af8fdee1648d4d5609b1d61c8338278764ba5829b365a49a7f79
- source: nvidia-cudnn-frontend
  path: python/cudnn/_pygraph.py
  commit: 941078f2ce6aa0a45ac5813b81760a19c616732a
  sha256: 0a143dba0a0aed7eac3227547bfd6e6d362ff6ec6ca60772c440e92c62c556e5
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/overview.md
  commit: 941078f2ce6aa0a45ac5813b81760a19c616732a
  sha256: f73c6109c01248eab4257db24eb2f8074f8d4f0a61c7c934c18d15a5870cd012
- source: nvidia-cudnn-frontend-docs
  path: index
  commit: e231f1ecf1c04ca05f5c5f66898be6f84da14a37fddd16491d733ebb95e321c1
  sha256: a47a30e4a032bce71b2e657c67f5176603afafec2051b51f2dafc7704a674928
  url: https://docs.nvidia.com/deeplearning/cudnn/latest/index.html
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend-docs
  path: open-kernels
  commit: e231f1ecf1c04ca05f5c5f66898be6f84da14a37fddd16491d733ebb95e321c1
  sha256: 93d501a4efe8ce95bbc7abc0ee9e5e410323006364f42dbb77e6bbea189c2de6
  url: https://docs.nvidia.com/deeplearning/cudnn/latest/fe-oss-apis/overview.html
  revision_kind: web-content-fingerprint
---
# cuDNN Frontend 官方工程：Graph、开放 Kernel 与训练调用链

## 工程范围

cuDNN Frontend（常被写成 cudnn-fronted）提供 C++/Python 图接口，也维护一批可阅读的开放 kernel。前者描述计算图、筛选计划并调用执行后端；后者覆盖 SDPA、稀疏 attention、MoE GEMM、量化与归一化融合等特定能力。不能把“Frontend 开源”解释成“全部 cuDNN 后端实现开源”，也不能把它理解成只有传统卷积。

训练中可经 TE fused attention、框架集成、自定义 autograd 或图编译路径调用。NV 模型的一个 op 名可能实际选择不同 engine；接口、后端、编译 kernel 与真实 dispatch 必须分别确认。

## 目录地图

| 位置 | 作用与排查入口 |
| --- | --- |
| `include/cudnn_frontend.h`、`include/cudnn_frontend/` | C++ 图、节点、plan、backend helpers；找 validate、build、execute 和 workspace。 |
| `include/cudnn_frontend/node/` | SDPA、matmul、MoE、Norm 等图节点及参数检查。 |
| `python/cudnn/_pygraph.py` | Python 图和执行后端协调；不能假设所有操作都直接走同一个 C++ plan。 |
| `python/cudnn/gemm/cutedsl/` | dense/grouped/discrete grouped 融合的 API 与设备 kernel。 |
| `python/cudnn/gemm/frost/` | 图分析、融合 IR、planning/heuristics、架构特定编译和 kernel 模板。 |
| `python/cudnn/block_sparse_attention/` 等 | 稀疏 attention 的接口与实现；不同稀疏语义须分别阅读。 |
| `samples/python/`、`samples/cpp/`、`samples/frost/` | 可执行教程、完整构图及训练前反向例子。 |
| `test/python/`、`docs/operations/`、`docs/fe-oss-apis/` | 支持面、正确性、格式、stream 与缓存契约。 |
| `CMakeLists.txt`、`setup.py`、`pyproject.toml`、`LICENSING.md` | 构建和依赖；不同目录许可可能不同，应核对具体文件。 |

## HCU 工作流如何采用

先从 NV 真实调用取得形状、布局、dtype、融合操作序列、反向需要的中间状态及 dispatch，再检查 HCU TE/Flash-Train 最新实现。TE 接口归 TE；通用编译融合与 Frontend 同类需求优先复用 Flash-Train。CuTe DSL/SM100 或 cuDNN engine 的实现方式可作参考，不能直接视作 HCU 可执行代码。

详细入口：[安装与单测](build-run-test.md)、[Graph 与 plan](graph-and-plans.md)、[训练 attention](attention.md)、[开放融合与稀疏算子](open-kernel-fusions.md)、[集成性能案例](cases/host-dispatch-and-cache.md)、[教程与更新](tutorials-and-update.md)。

## 来源与版本复核

- [nvidia-cudnn-frontend: README.md](https://github.com/NVIDIA/cudnn-frontend/blob/941078f2ce6aa0a45ac5813b81760a19c616732a/README.md)
- [nvidia-cudnn-frontend: LICENSING.md](https://github.com/NVIDIA/cudnn-frontend/blob/941078f2ce6aa0a45ac5813b81760a19c616732a/LICENSING.md)
- [nvidia-cudnn-frontend: include/cudnn_frontend/graph_interface.h](https://github.com/NVIDIA/cudnn-frontend/blob/941078f2ce6aa0a45ac5813b81760a19c616732a/include/cudnn_frontend/graph_interface.h)
- [nvidia-cudnn-frontend: python/cudnn/_pygraph.py](https://github.com/NVIDIA/cudnn-frontend/blob/941078f2ce6aa0a45ac5813b81760a19c616732a/python/cudnn/_pygraph.py)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/overview.md](https://github.com/NVIDIA/cudnn-frontend/blob/941078f2ce6aa0a45ac5813b81760a19c616732a/docs/fe-oss-apis/overview.md)
- [nvidia-cudnn-frontend-docs: index](https://docs.nvidia.com/deeplearning/cudnn/latest/index.html)
- [nvidia-cudnn-frontend-docs: open-kernels](https://docs.nvidia.com/deeplearning/cudnn/latest/fe-oss-apis/overview.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## 版本线与当前能力入口

源码专题跟踪官方 `develop` 的固定提交，已发布包、`main` 和官网 `latest` 分开确认。本次核对时 main 仍为 1.31.0 RC，而 develop 继续 1.32.0 开发；不能按分支名字认定 main 包含所有最新机制。运行配方必须固定实际 Frontend、cuDNN backend、CUDA、GPU 和可选 DSL 版本。

[FlexAttention plan 与 autograd](flex-attention-plans.md) 补足可编译稀疏 mask 的执行生命周期；[开放 Kernel](open-kernel-fusions.md) 包含 grouped GEMM、BSA/DSA 的缓冲与精度约束。这些源码结论是候选方法，不构成 HCU 库的支持清单。