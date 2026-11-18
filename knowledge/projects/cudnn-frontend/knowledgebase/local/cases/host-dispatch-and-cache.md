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
reviewed_on: '2026-11-18'
retrieved_on: '2026-11-04'
sources:
- source: nvidia-cudnn-frontend
  path: docs/utilities/framework_integration_performance.md
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 5388a0c7c13fcf6f5471fc5d05b1ddcaac7b9f7fd366cd34ab9b71da9b49c476
- source: nvidia-cudnn-frontend
  path: docs/utilities/dynamic-kernel-cache.md
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: a179f7f5607256b25a7239f3a9e3954c04402d46db9a6a2953c1417c1941513a
- source: nvidia-cudnn-frontend
  path: docs/utilities/cuda-graphs.md
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 60b3177f256d50028b2ca562ece2881693d9ee3f403f81c68d06b75cc2f88a42
- source: nvidia-cudnn-frontend
  path: python/cudnn/_pygraph.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 99738780798d18ea38c5870b4a60ab5aa180638e0ef4d875d4920708819e5f5c
- source: nvidia-cudnn-frontend-docs
  path: framework-integration
  commit: 62596f777aca773f340569b88fbd42c5fcd807249e8a188810cd38297d19cab9
  sha256: cd69f580a94aa1728385008ada47166fc77421373d45f7bedd0fd9b5b106ebc2
  url: https://docs.nvidia.com/cudnn/utilities/framework_integration_performance/
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend
  path: python/cudnn/_pygraph.py
  commit: 623ad8ff498acdaa860fbc8191d2afeaea90e400
  sha256: bf17e14d6250b2c85107308d4ee885877ce10fb2d458389754f2af5204d99126
- source: nvidia-cudnn-frontend
  path: python/cudnn/gemm/frost/graph_analyzer.py
  commit: 623ad8ff498acdaa860fbc8191d2afeaea90e400
  sha256: fd02f3c6c1c384491be9ac592f9fe4b6d1508bbf18b4699d2de947d7faaad0c9
- source: nvidia-cudnn-frontend
  path: docs/utilities/python_graph_and_execution_backends.md
  commit: 623ad8ff498acdaa860fbc8191d2afeaea90e400
  sha256: 71ea0a2933a86945fdafe771e0c37b4f5fbb958722bce80b2868bed0d9e1707b
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

## 当前缓存命中仍需复核的条件

固定 `623ad8ff498a` 后，Frontend recipe 和编译制品采用不同失效边界：旧 engine/config 不再准入时完整重新 planning，不能改 ID 继续复用。最终 plan 的 behavior note 决定 packed Stats stride override 是否可用，engine 名不能代替能力检查。计时还应保留本次 workspace 容量、Handle 所在设备/stream 及实际绑定；已有 cache 或 Graph 对象不证明这些条件正确。

FROST GEMM 的辅助张量现在保留原存储及逐 consumer 的逻辑 IndexMap，只有全部使用都满足旧 per-K 条件才采用旧辅助 ABI。相同 shape 不足以忽略广播、view、方向与舍入；比较 host 优化时把构图/编译和稳态执行分开，避免缓存了不兼容的语义。

## 验收与回退

通过条件是数据/梯度契约不变、模型空泡和墙钟改善、缓存与峰值显存可控；单个 microbenchmark 提速不够。遇到 shape/版本/stream 不匹配，应退回已验证路径或重建正确缓存项，并记录原因。该机制可供 HCU TE/Flash-Train 的 Python/C++ 封装优化参考，具体实现仍看目标分支。

当前计划的 index 只有在同一已构建候选排序内才有意义；autotune 裁剪/重排后必须同时更新 workspace/notes/候选映射，不能拿旧的最优 index 继续执行。FlashInfer 已消费的 engine 名和 binder capability 也属真实接口边界，不能以“private 拼写”随意重命名。见[Graph 合同](../topics/graph-and-plans.md#当前边界指针对齐计划排序与外部消费者)。

当前 Python 执行入口新增有界的 ordered-binding 元数据缓存，缓存 schema 不保留调用方 buffer；它降低 host 包装成本，不能替调用方延长 tensor 寿命。backend direct population、retention NONE 和 Python plan 序列化分别减少不同阶段成本，准入和所有权也不同；按[Graph 生命周期](../topics/graph-and-plans.md#缓存与显存所有权)分别验证后再组合，不能用单次 warm-cache replay 替代冷启动或并发正确性。

新官网同样区分 eager 包装时间、captured workload 的 replay GPU interval 与 profiler 的单 kernel 时间；CUDA event 的窗口可包含 host 提交空泡，Graph replay 仍包含图内调度，不是纯 kernel 指令时间。复用输出/variant pack 仍须按实际 device/stream/参数版本和消费者寿命验证，不能从来源单次微秒数字推导 HCU 固定开销。

## 来源与版本复核

- [nvidia-cudnn-frontend: docs/utilities/framework_integration_performance.md](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/docs/utilities/framework_integration_performance.md)
- [nvidia-cudnn-frontend: docs/utilities/dynamic-kernel-cache.md](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/docs/utilities/dynamic-kernel-cache.md)
- [nvidia-cudnn-frontend: docs/utilities/cuda-graphs.md](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/docs/utilities/cuda-graphs.md)
- [nvidia-cudnn-frontend: python/cudnn/_pygraph.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/cudnn/_pygraph.py)
- [nvidia-cudnn-frontend-docs: framework-integration](https://docs.nvidia.com/cudnn/utilities/framework_integration_performance/)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## 2026-11-18 固定依据

- [python/cudnn/_pygraph.py](https://github.com/NVIDIA/cudnn-frontend/blob/623ad8ff498acdaa860fbc8191d2afeaea90e400/python/cudnn/_pygraph.py)
- [python/cudnn/gemm/frost/graph_analyzer.py](https://github.com/NVIDIA/cudnn-frontend/blob/623ad8ff498acdaa860fbc8191d2afeaea90e400/python/cudnn/gemm/frost/graph_analyzer.py)
- [docs/utilities/python_graph_and_execution_backends.md](https://github.com/NVIDIA/cudnn-frontend/blob/623ad8ff498acdaa860fbc8191d2afeaea90e400/docs/utilities/python_graph_and_execution_backends.md)
