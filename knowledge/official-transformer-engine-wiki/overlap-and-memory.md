---
id: official-transformer-engine-wiki/overlap-and-memory
title: TE 并行与显存：Userbuffers、CP、Graph 和 Offload
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
  path: examples/pytorch/comm_gemm_overlap/README.md
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 16d677ac34c025955d7afc08b89aa1d4ca620a888fbb351543fd6b45269dd936
- source: nvidia-transformerengine
  path: examples/pytorch/comm_gemm_overlap/te_layer_with_overlap.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 971222cfc38227dd6d9f2689e751722ea760447373c4058404a6fc536ad7e953
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/attention/dot_product_attention/context_parallel.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 0139c7c5ce185869d733b92dddb3fea2020638a089f17a5ce088e82d733e4160
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/graph.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 8f795d0be87618100ab5b3c6bbb9d11bb1958c3428807ec656b62da5c89209b6
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/cpu_offload.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: a6c238518e1d8813bb665f956185b0dea936aee6d0938933b5539095669e26fd
- source: nvidia-transformerengine
  path: docs/features/other_optimizations/cpu_offloading/cpu_offloading.rst
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: b0eb322d9da8de6d1c85f5af54b1b15bb5d0a37c72de5485e3710f5d4c4809bd
- source: nvidia-transformerengine
  path: docs/examples/advanced_optimizations.ipynb
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 0d5d703679a7d3c16773112e8879879560a945600c168a95b27b22bc44f9a22a
- source: nvidia-transformerengine-docs
  path: advanced-optimizations
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: 6d7c1eff4937a379e6a812783e475f8b10971eda810b532c43db35e81bd1a162
  url: https://docs.nvidia.com/deeplearning/transformer-engine/examples/advanced_optimizations.html
  revision_kind: web-content-fingerprint
---

# TE 并行与显存：Userbuffers、CP、Graph 和 Offload

## TP/SP 通信与计算重叠

官方 `examples/pytorch/comm_gemm_overlap` 展示 TE 模块中通信和 GEMM 的重叠。先读 README 的硬件/软件限制，再读 communicator 初始化、模块参数及 forward/backward。示例依赖 NVIDIA 的互联、multicast/IPC 与连接配置，不可把 `CUDA_DEVICE_MAX_CONNECTIONS=1` 或节点拓扑直接移植到 HCU；`GPU_MAX_HW_QUEUES` 是另一项 runtime 配置，需要独立对照实测。

HCU 侧先确认当前 TE 已支持的 overlap 路径、通信实现和 buffer 生命周期，再设计实验。记录 process group、buffer 字节数、dtype、通信分块、GEMM shape、并发 stream 和同步点。收益看端到端关键等待是否减少，同时关注带宽争用、额外显存、单独 GEMM 被拖慢，以及最慢 rank。

## CP 不是普通序列切片

`context_parallel.py` 处理 attention 的跨 rank 协作。mask、局部/全局序列位置、packed 长度和通信顺序共同构成语义；诊断必须取每个实际并行组的代表性 rank，并保留 collective 上下文。不能只把任意两个 trace 拼起来解释负载均衡。

## Graph 和低精度状态

`graph.py:make_graphed_callables` 除捕获 kernel 以外，还处理训练相关上下文与 FP8 状态。捕获/重放前后检查输入地址与形状、RNG、参数版本、量化副本及梯度存储是否符合约定。把 warmup/编译/capture 分开计时；graph 可能消除 CPU launch 空泡，但不能说明单 kernel 已达到上限。

## CPU offload 的显存与延迟账本

教程及 `cpu_offload.py` 将中间张量搬离设备并安排取回。分析时至少保存：哪些 tensor 可 offload、写入/读取位置、恢复时限、pinned host 内存、总线带宽、额外 stream/event、重算和 graph 的兼容性。平均 allocated 较低仍可能在 backward、checkpoint 或取回叠加时 OOM。

按无 overlap/no offload 基线、单独开启、组合开启做有针对性的对照，记录 peak allocated/reserved 与吞吐、p95 step、正确性。内存压得过满会削弱运行余量；不要为了短时峰值吞吐接受无法稳定保存/恢复的配置。组合变更稳定后再做阶段 loss 回归。

## 来源与版本复核

- [nvidia-transformerengine: examples/pytorch/comm_gemm_overlap/README.md](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/examples/pytorch/comm_gemm_overlap/README.md)
- [nvidia-transformerengine: examples/pytorch/comm_gemm_overlap/te_layer_with_overlap.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/examples/pytorch/comm_gemm_overlap/te_layer_with_overlap.py)
- [nvidia-transformerengine: transformer_engine/pytorch/attention/dot_product_attention/context_parallel.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/attention/dot_product_attention/context_parallel.py)
- [nvidia-transformerengine: transformer_engine/pytorch/graph.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/graph.py)
- [nvidia-transformerengine: transformer_engine/pytorch/cpu_offload.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/cpu_offload.py)
- [nvidia-transformerengine: docs/features/other_optimizations/cpu_offloading/cpu_offloading.rst](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/docs/features/other_optimizations/cpu_offloading/cpu_offloading.rst)
- [nvidia-transformerengine: docs/examples/advanced_optimizations.ipynb](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/docs/examples/advanced_optimizations.ipynb)
- [nvidia-transformerengine-docs: advanced-optimizations](https://docs.nvidia.com/deeplearning/transformer-engine/examples/advanced_optimizations.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码 main、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
