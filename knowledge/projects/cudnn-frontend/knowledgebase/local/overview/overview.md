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
reviewed_on: '2026-10-20'
sources:
- source: nvidia-cudnn-frontend
  path: README.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: f4e2131aeab9f5f6697805b9546aef78544370a6950a5c046ff3637b066ed4fa
- source: nvidia-cudnn-frontend
  path: LICENSING.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: e418507f66706a64e50b52a90888537162462f71b0baa5a2d994618ef3bd541e
- source: nvidia-cudnn-frontend
  path: include/cudnn_frontend/graph_interface.h
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: fe55a7781cf88836bc3e7905b32cf7f18230ec6147c9c3b752c7447efc10d661
- source: nvidia-cudnn-frontend
  path: python/cudnn/_pygraph.py
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 7b033ce20a300a3a933d0ea67970a123dff21ed7c551fd5e9dfd5728d703587f
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/overview.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 6c347c2a2eee41824bb24e5461ac8248d54b0787ff23f5556a41796267c09d55
- source: nvidia-cudnn-frontend-docs
  path: index
  commit: 935d19c3968895d2890a5e4c651071b2f3ec91666c8b340c44a5064fad19293c
  sha256: 2ebf746b83ef6a0c55e90b194684d6d7e879c798cc53f4f69d1040a279c55643
  url: https://docs.nvidia.com/cudnn/overview
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend-docs
  path: open-kernels
  commit: 935d19c3968895d2890a5e4c651071b2f3ec91666c8b340c44a5064fad19293c
  sha256: e14115ad3751858b10e51100c0ab5f8983a683899cae5bfca3bf1d18e8119a27
  url: https://docs.nvidia.com/cudnn/fe-oss-apis/overview
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

详细入口：[安装与单测](../guides/build-run-test.md)、[Graph 与 plan](../topics/graph-and-plans.md)、[训练 attention](../topics/attention.md)、[开放融合与稀疏算子](../topics/open-kernel-fusions.md)、[集成性能案例](../cases/host-dispatch-and-cache.md)、[教程与更新](../changes/tutorials-and-update.md)。

## 来源与版本复核

- [nvidia-cudnn-frontend: README.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/README.md)
- [nvidia-cudnn-frontend: LICENSING.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/LICENSING.md)
- [nvidia-cudnn-frontend: include/cudnn_frontend/graph_interface.h](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/include/cudnn_frontend/graph_interface.h)
- [nvidia-cudnn-frontend: python/cudnn/_pygraph.py](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/python/cudnn/_pygraph.py)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/overview.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/fe-oss-apis/overview.md)
- [nvidia-cudnn-frontend-docs: index](https://docs.nvidia.com/cudnn/overview)
- [nvidia-cudnn-frontend-docs: open-kernels](https://docs.nvidia.com/cudnn/fe-oss-apis/overview)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## 版本线与当前能力入口

源码专题跟踪官方 `develop@a7269d7607db343fb099dabf6d8fef47f4a2498c`，CMake 项目版本为1.32.0；已发布包、`main` 和官网滚动版本另行确认，不能按分支名字认定它们包含相同机制。运行配方必须固定实际 Frontend、cuDNN backend、CUDA、GPU 和可选 DSL 版本。

[FlexAttention plan 与 autograd](../topics/flex-attention-plans.md) 补足可编译稀疏 mask 的执行生命周期；[开放 Kernel](../topics/open-kernel-fusions.md) 包含 grouped GEMM、BSA/DSA 的缓冲与精度约束。这些源码结论是候选方法，不构成 HCU 库的支持清单。

当前更新的重点是 nanobind 构建、SDPA 地址/stride 校验、plan/metadata 一起排序、FlashInfer 对外能力查询和 DSA 确定性/预编译生命周期。官方文档已迁到 `docs.nvidia.com/cudnn/`；新高层 `with cudnn.Graph` 与旧显式入口按版本说明，某些网页比本固定源码保留更旧的 JAX 别名，不将官网与源码拼成一套调用。
