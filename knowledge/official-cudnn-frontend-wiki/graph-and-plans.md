---
id: official-cudnn-frontend-wiki/graph-and-plans
title: cuDNN Graph、执行计划、Workspace 与动态形状缓存
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
  path: docs/developer/graph-api.mdx
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 6bbfc6300243b6ba9234ead990fab86e68b18a185284bf9705c25581d4d5cc4c
- source: nvidia-cudnn-frontend
  path: include/cudnn_frontend/graph_interface.h
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: d46a552b0b5a6368c9eb4792214cc4ecbdf8bb69412554e73562e1ff4251d97b
- source: nvidia-cudnn-frontend
  path: include/cudnn_frontend/plans.h
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 4aa41cbe9a418064ddced15f2ef419429fb68798ef439814157e5a8c8755097f
- source: nvidia-cudnn-frontend
  path: include/cudnn_frontend/backend/kernel_cache.h
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 3ec261ac7b819ee1aac540a4227fa343e9677bdb9524457f0944f61e2dc863be
- source: nvidia-cudnn-frontend
  path: python/cudnn/_pygraph.py
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 85e7e095a0e514931bbac6e71893d316495eeda415502669e43e3903abe25a46
- source: nvidia-cudnn-frontend
  path: docs/utilities/dynamic-kernel-cache.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 37cc57df5fe3b0015647c345d072939e12202a9326aa898f9c93b5b11bf1ed60
- source: nvidia-cudnn-frontend
  path: docs/utilities/python_graph_and_execution_backends.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: de73a4ce7f5532c8aff2f590c5f74200a09b167e18e3c38982fa108a40fe842f
- source: nvidia-cudnn-frontend-docs
  path: graph-api
  commit: e231f1ecf1c04ca05f5c5f66898be6f84da14a37fddd16491d733ebb95e321c1
  sha256: f194099e7d14e105bd0671d30c0599b32df2efc5720174d2a3fc206631a97c5f
  url: https://docs.nvidia.com/deeplearning/cudnn/latest/developer/graph-api.html
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend-docs
  path: dynamic-cache
  commit: e231f1ecf1c04ca05f5c5f66898be6f84da14a37fddd16491d733ebb95e321c1
  sha256: fd673eec1283914ee1e0266e53572dfbd9d2b0f815069a607004d29086bde604
  url: https://docs.nvidia.com/deeplearning/cudnn/latest/utilities/dynamic-kernel-cache.html
  revision_kind: web-content-fingerprint
---

# cuDNN Graph、执行计划、Workspace 与动态形状缓存

## 构建阶段与执行阶段

显式接口常见路径为：定义 tensor 元数据与操作 → validate → build_operation_graph → create_execution_plans → check_support → build_plans → 查询 workspace → 绑定实际地址并 execute。高级 `cudnn.Graph` 包装会代办其中部分步骤，但生命周期仍存在。一个 graph 是数学描述，一个 engine/plan 是具体实现选择，一个 CUDA Graph 又是另一种捕获/重放机制，三者不能混称。

tensor 的 shape、stride、dtype、uid、virtual/output 属性决定图语义；variant pack 绑定运行时存储。计算精度、中间精度和边界 dtype 分开记录。临时 tensor 标为 virtual 可能促成融合，但跨 forward/backward 需要的结果必须保留为可消费的输出。

## plan 选择为什么会影响性能和数值

heuristic A/B 提供候选，fallback 注重可运行性；候选还需 check_support 和构建。可对可用计划做实测选择，但要同时查看 workspace、numerical/behavior notes、determinism 和 runtime compilation。最快计划的归约/降精度方式未必符合当前训练契约。最终保存实际 plan、版本与数值验证证据。

当前 Python `_pygraph.py` 可协调不同执行后端，相关 engine 是否启用、支持哪些图、失败后如何回退，都须核对当前实现。构图成功不是指定 engine 已执行，更不是所有 kernel 已融合成一个。

## 缓存与显存所有权

计划缓存要按真正影响语义和支持面的条件区分，如图结构、形状、stride、dtype、相关选项、设备与库版本。复用 plan 不代表可以复用任意 buffer；执行期间 workspace、输出、saved tensors 与 stream/event 的生命周期要明确。多个并发 stream 不能无同步共享仍在使用的 scratch。

教程区分 build 侧的 dynamic-shape kernel cache 与 execute 侧的 shape override。前者可降低同拓扑图的重复编译成本，后者受实际 plan 的运行时形状支持约束；不能据“支持动态 shape”推导任意长度、stride 或 dtype 均能复用。跨版本反序列化也需验证，而非把缓存当永久二进制接口。

## 故障定位顺序

图验证失败先查 tensor 元数据；无支持计划查 operation 支持面与硬件/版本；build 失败查编译依赖；execute 失败查地址、workspace、stream 与生命周期；性能下降再区分计划变化、重复构建和硬件竞争。保存最小图、输入元数据和首个失败步骤，比只保留最后一个异常更易复现。

## 来源与版本复核

- [nvidia-cudnn-frontend: docs/developer/graph-api.mdx](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/developer/graph-api.mdx)
- [nvidia-cudnn-frontend: include/cudnn_frontend/graph_interface.h](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/include/cudnn_frontend/graph_interface.h)
- [nvidia-cudnn-frontend: include/cudnn_frontend/plans.h](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/include/cudnn_frontend/plans.h)
- [nvidia-cudnn-frontend: include/cudnn_frontend/backend/kernel_cache.h](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/include/cudnn_frontend/backend/kernel_cache.h)
- [nvidia-cudnn-frontend: python/cudnn/_pygraph.py](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/python/cudnn/_pygraph.py)
- [nvidia-cudnn-frontend: docs/utilities/dynamic-kernel-cache.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/utilities/dynamic-kernel-cache.md)
- [nvidia-cudnn-frontend: docs/utilities/python_graph_and_execution_backends.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/utilities/python_graph_and_execution_backends.md)
- [nvidia-cudnn-frontend-docs: graph-api](https://docs.nvidia.com/deeplearning/cudnn/latest/developer/graph-api.html)
- [nvidia-cudnn-frontend-docs: dynamic-cache](https://docs.nvidia.com/deeplearning/cudnn/latest/utilities/dynamic-kernel-cache.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码 main、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
