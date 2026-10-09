---
id: official-megatron-wiki/transformer-engine
title: Transformer Engine：精度、融合与 HCU 承接边界
engine: transformer-engine
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-transformerengine
  path: README.rst
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 7ec335c82227680e55c8047d90db0e99a87d0c10d3d6d43d7b54d54e2d5f9e0a
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/fp8.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 54a2967ad103ddcffcaf7a1d10e7d9fcfa3a290772d9239c416fff391349f3a1
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/quantization.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: d8f2cd4fa72d8343eaca912cad0d89c4f39ff5828849cda3904c640aa587a943
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/module/linear.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: a7b63f31f9607c71f71c0a93e3e90239194d63601b72aab7875dd5b57c75617e
---

# Transformer Engine：精度、融合与 HCU 承接边界

## 阅读层次

TE 的独立详细知识库已建立：[工程总览与源码导航](../official-transformer-engine-wiki/overview.md)、[低精度和权重缓存](../official-transformer-engine-wiki/precision-and-cache.md)、[attention 后端](../official-transformer-engine-wiki/attention.md)、[官方教程](../official-transformer-engine-wiki/tutorials-and-update.md)。本页保留 Megatron 与 HCU 承接关系的入口。

从 PyTorch module/linear 的 forward/backward/autograd 状态开始，进入 quantization 管理，再定位 C++/CUDA 底层实现；当前官方 `pytorch/fp8.py` 已标注为弃用的兼容入口，新机制以 `quantization.py` 为准。记录模块接口、训练/推理分支、参数 dtype、累积 dtype、scale 与缓存所有权。低精度参数格式不能用输出 tensor dtype 单独概括。

## 融合对齐契约

NV 的一条融合调用在 HCU 侧可由多个 kernel 暂时实现，但需要显式差距表：输入输出布局、mask、bias、activation、残差、saved tensors、RNG、dgrad/wgrad 和 precision。优化时既比较整体数值，也检查 kernel 内 cast 和 reduction 顺序，防止“短 loss 看着差不多”掩盖误差放大。

已有 HCU Transformer Engine 能力优先复用；TE 接口缺口向对应工程提交集中、可维护的改动。通用编译融合、cuDNN frontend 等训练算子需求优先检查 Flash-Train 最新分支已有实现，再决定是否新增。PR 附真实 dispatch、正确性、多 shape、反向、阶段 loss 以及 profiler-off 性能证据。

## 风险

低精度权重缓存要在参数更新后失效，graph/recompute 可能重用状态。平台缺少官方依赖时不应静默回到另一条语义或精度路径。移植优化不等同于把 NVIDIA 汇编或 CU/SM 参数改名。

## 固定源码与更新范围

- [README.rst](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/README.rst)
- [transformer_engine/pytorch/fp8.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/fp8.py)
- [transformer_engine/pytorch/quantization.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/quantization.py)
- [transformer_engine/pytorch/module/linear.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/module/linear.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
