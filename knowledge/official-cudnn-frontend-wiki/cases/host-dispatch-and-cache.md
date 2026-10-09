---
id: official-cudnn-frontend-wiki/cases/host-dispatch-and-cache
title: 案例：cuDNN Kernel 不慢，模型却被构图和 Host 调度拖慢
engine: cudnn-frontend
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-cudnn-frontend
  path: docs/utilities/framework_integration_performance.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 5388a0c7c13fcf6f5471fc5d05b1ddcaac7b9f7fd366cd34ab9b71da9b49c476
- source: nvidia-cudnn-frontend
  path: docs/utilities/dynamic-kernel-cache.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 37cc57df5fe3b0015647c345d072939e12202a9326aa898f9c93b5b11bf1ed60
- source: nvidia-cudnn-frontend
  path: docs/utilities/cuda-graphs.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 60b3177f256d50028b2ca562ece2881693d9ee3f403f81c68d06b75cc2f88a42
- source: nvidia-cudnn-frontend
  path: python/cudnn/_pygraph.py
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 85e7e095a0e514931bbac6e71893d316495eeda415502669e43e3903abe25a46
- source: nvidia-cudnn-frontend-docs
  path: framework-integration
  commit: e231f1ecf1c04ca05f5c5f66898be6f84da14a37fddd16491d733ebb95e321c1
  sha256: 4f17ba1dfc434d4edf15b0770b06403a947cc6cc084f98ece33db61aab33cdc3
  url: https://docs.nvidia.com/deeplearning/cudnn/latest/utilities/framework_integration_performance.html
  revision_kind: web-content-fingerprint
---

# 案例：cuDNN Kernel 不慢，模型却被构图和 Host 调度拖慢

## 症状与假设

独立同 shape kernel 表现正常，模型中却出现较多 GPU 空泡；逐算子 Python 封装每次都构图、创建 plan、设置 stream、分配输出或整理地址映射。此时更换 kernel 可能收效很小，应先把 host 和设备计时分开。

## 官方案例给出的检查线索

检查图/plan 是否按稳定元数据复用；是否每次都重新选择计划；是否反复设置未变的 stream；variant pack 与输出 buffer 能否安全复用；权重转置能否用 stride/view 表达，而非每次物化 contiguous copy。上述各项都须结合实际调用链验证，不能把全局共享 buffer 或忽略 stream 变化当作优化。

当前官方指南给出 pinned plan 的 `execute_plan_at_index` 路径，但 API 与索引约定受版本影响。只有经过正确性验证和适用条件固定的 plan 才能复用。该页中具体计时来自 NV 平台，不作为 HCU 的预期值。

## 可复查的实验步骤

1. 冻结形状、布局、dtype、设备、软件和数值 reference，采完整稳态 trace。
2. 分别测构建/编译、首次执行、常态 execute、模型端到端，保存 CPU 包装耗时与 GPU 空泡。
3. 一次修改一个明确瓶颈：计划缓存、避免冗余 stream 操作、减少 Python 对象/分配、去掉无必要的物化转置。
4. 回归动态 shape、并发 stream、参数更新和 checkpoint；检查复用缓存是否错误共享或无界增长。
5. 若使用 graph 捕获，再测固定地址/RNG/工作区和重放正确性；独立 kernel 计时与真实训练吞吐分别报告。

## 验收与回退

通过条件是数据/梯度契约不变、模型空泡和墙钟改善、缓存与峰值显存可控；单个 microbenchmark 提速不够。遇到 shape/版本/stream 不匹配，应退回已验证路径或重建正确缓存项，并记录原因。该机制可供 HCU TE/Flash-Train 的 Python/C++ 封装优化参考，具体实现仍看目标分支。

## 来源与版本复核

- [nvidia-cudnn-frontend: docs/utilities/framework_integration_performance.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/utilities/framework_integration_performance.md)
- [nvidia-cudnn-frontend: docs/utilities/dynamic-kernel-cache.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/utilities/dynamic-kernel-cache.md)
- [nvidia-cudnn-frontend: docs/utilities/cuda-graphs.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/utilities/cuda-graphs.md)
- [nvidia-cudnn-frontend: python/cudnn/_pygraph.py](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/python/cudnn/_pygraph.py)
- [nvidia-cudnn-frontend-docs: framework-integration](https://docs.nvidia.com/deeplearning/cudnn/latest/utilities/framework_integration_performance.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码 main、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
