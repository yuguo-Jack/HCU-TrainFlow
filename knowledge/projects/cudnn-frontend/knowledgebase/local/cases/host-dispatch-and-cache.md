---
id: official-cudnn-frontend-wiki/cases/host-dispatch-and-cache
title: 案例：cuDNN Kernel 不慢，模型却被构图和 Host 调度拖慢
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
  path: docs/utilities/framework_integration_performance.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 5388a0c7c13fcf6f5471fc5d05b1ddcaac7b9f7fd366cd34ab9b71da9b49c476
- source: nvidia-cudnn-frontend
  path: docs/utilities/dynamic-kernel-cache.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: a179f7f5607256b25a7239f3a9e3954c04402d46db9a6a2953c1417c1941513a
- source: nvidia-cudnn-frontend
  path: docs/utilities/cuda-graphs.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 60b3177f256d50028b2ca562ece2881693d9ee3f403f81c68d06b75cc2f88a42
- source: nvidia-cudnn-frontend
  path: python/cudnn/_pygraph.py
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 7b033ce20a300a3a933d0ea67970a123dff21ed7c551fd5e9dfd5728d703587f
- source: nvidia-cudnn-frontend-docs
  path: framework-integration
  commit: 935d19c3968895d2890a5e4c651071b2f3ec91666c8b340c44a5064fad19293c
  sha256: cd69f580a94aa1728385008ada47166fc77421373d45f7bedd0fd9b5b106ebc2
  url: https://docs.nvidia.com/cudnn/utilities/framework_integration_performance/
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

当前计划的 index 只有在同一已构建候选排序内才有意义；autotune 裁剪/重排后必须同时更新 workspace/notes/候选映射，不能拿旧的最优 index 继续执行。FlashInfer 已消费的 engine 名和 binder capability 也属真实接口边界，不能以“private 拼写”随意重命名。见[Graph 合同](../topics/graph-and-plans.md#当前边界指针对齐计划排序与外部消费者)。

新官网同样区分 eager 包装时间、captured workload 的 replay GPU interval 与 profiler 的单 kernel 时间；CUDA event 的窗口可包含 host 提交空泡，Graph replay 仍包含图内调度，不是纯 kernel 指令时间。复用输出/variant pack 仍须按实际 device/stream/参数版本和消费者寿命验证，不能从来源单次微秒数字推导 HCU 固定开销。

## 来源与版本复核

- [nvidia-cudnn-frontend: docs/utilities/framework_integration_performance.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/utilities/framework_integration_performance.md)
- [nvidia-cudnn-frontend: docs/utilities/dynamic-kernel-cache.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/utilities/dynamic-kernel-cache.md)
- [nvidia-cudnn-frontend: docs/utilities/cuda-graphs.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/utilities/cuda-graphs.md)
- [nvidia-cudnn-frontend: python/cudnn/_pygraph.py](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/python/cudnn/_pygraph.py)
- [nvidia-cudnn-frontend-docs: framework-integration](https://docs.nvidia.com/cudnn/utilities/framework_integration_performance/)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
