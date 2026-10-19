---
id: official-cudnn-frontend-wiki/graph-and-plans
title: cuDNN Graph、执行计划、Workspace 与动态形状缓存
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
  path: docs/developer/graph-api.mdx
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 70e4a64b5341538895fc178ff027d27ce61e10c051ea5d229b793ad5c9ffa597
- source: nvidia-cudnn-frontend
  path: include/cudnn_frontend/graph_interface.h
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: fe55a7781cf88836bc3e7905b32cf7f18230ec6147c9c3b752c7447efc10d661
- source: nvidia-cudnn-frontend
  path: include/cudnn_frontend/plans.h
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 5117c8558899950fb02c39e558313900fe37962652820a75cabad568bf7d0803
- source: nvidia-cudnn-frontend
  path: include/cudnn_frontend/backend/kernel_cache.h
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 3ec261ac7b819ee1aac540a4227fa343e9677bdb9524457f0944f61e2dc863be
- source: nvidia-cudnn-frontend
  path: python/cudnn/_pygraph.py
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 7b033ce20a300a3a933d0ea67970a123dff21ed7c551fd5e9dfd5728d703587f
- source: nvidia-cudnn-frontend
  path: docs/utilities/dynamic-kernel-cache.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: a179f7f5607256b25a7239f3a9e3954c04402d46db9a6a2953c1417c1941513a
- source: nvidia-cudnn-frontend
  path: docs/utilities/python_graph_and_execution_backends.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: e73978234e7afd4325f2b886ea9c7b9c8051dd0a963d0922bae4ca2e3691179d
- source: nvidia-cudnn-frontend-docs
  path: graph-api
  commit: 935d19c3968895d2890a5e4c651071b2f3ec91666c8b340c44a5064fad19293c
  sha256: 5330d9ae79b7a32d3d557dbe1b0bc4c927a807d1b97d459f6fe6bc9d8c7ddc16
  url: https://docs.nvidia.com/cudnn/developer/graph-api
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend-docs
  path: dynamic-cache
  commit: 935d19c3968895d2890a5e4c651071b2f3ec91666c8b340c44a5064fad19293c
  sha256: a04d09bc60b596cafa2b29a2e5ceff433c14bae3cf6acd457d19a3c09cf409a7
  url: https://docs.nvidia.com/cudnn/utilities/dynamic-kernel-cache
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend
  path: docs/operations/Normalizations.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 270cae42775cde1448aa45d40120efc7a44b196b17dfe94eec8b6c0e8ecb8c4b
- source: nvidia-cudnn-frontend
  path: python/pygraph/norm.cpp
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: a05133d6fcbf06b45f63b5fd5ecfd8978e8b82e36cd576c6e800b522ec6988b5
- source: nvidia-cudnn-frontend
  path: test/python/norm/graph/test_layernorm.py
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: ec724c494c7acb618e231d3443fd3f679a1041b9125dddc354629911520fc960
- source: nvidia-cudnn-frontend
  path: docs/developer/overview.mdx
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 920383cc59860d33321643185b7491445ea9c5135b56e727990a5039eb8b8870
- source: nvidia-cudnn-frontend
  path: python/cudnn/__init__.py
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 81e1159443902bfb9bdcf1bf86accb21e8793a0e214feec81f38fd711e332503
- source: nvidia-cudnn-frontend
  path: test/python/sdpa/frost/test_flashinfer_consumed_surface.py
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 7d5189f6a4d7ab65792c27a40b880b72487f301ff2daf96c5314b1cf3f5a49cc
- source: nvidia-cudnn-frontend
  path: test/python/core/graph/test_graph_native.py
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 83d7968864add5bcabae178686938f2fb95b48edddc5efd130d968319a6d04aa
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

## 当前边界：指针对齐、计划排序与外部消费者

在 `a7269d7607db`，SDPA 的声明 stride 与执行指针有独立对齐校验，默认16字节。C++ graph 在 execute、populate/update CUDA graph 及准备好的 variant-pack 模板中都检查相应地址；legacy Slice 从本次源绑定重新派生地址，不能污染下次调用的 caller map。序列化保存 aligned_operands，新反序列化可继续检查；旧序列化数据缺该字段时不会自动获得这层保护。

dynamic shape 的一般 override 接口仍区分 build 与 execute，但本版 SDPA forward 的 override_strides 不会改变已声明 stride，必须按具体 node 检查，不能拿通用接口说明宣称可以任意换布局。runtime workspace 应按实际 override shape 查询，不能沿用 cache-shape 的旧容量。

autotune callback 可排序/裁剪候选，但当前实现先验证返回的 plan 非空、已构建且不重复，再将 plan 和相关元数据一起重排，candidate 指向新首项。旧 index、workspace、notes 不应脱离排序结果复用；失败回退也要确认实际候选。OSS RMSNorm+SiLU build 失败会取消其候选并尝试 cuDNN plans，两者都失败时保留复合错误，不能把存在 engine 对象当已经构建成功。

FlashInfer 消费的 `selected_engine`、`backend_plan_entries()` 与 native binder 能力名已明确为对外合同。`cudnn.sdpa_capabilities()` 返回当前扩展支持的 capability 名集合，`selected_engine is None` 表示所选 cuDNN backend entry，而不是无计划；backend entries 为空也不能由其他 Python engine 可用来填补。CuTe DSL 的设备感知资格另看 `cutedsl_runtime_available(device_cc)`，仅检查包版本不足以证明目标架构可编译。host-only consumed-surface 测试固定名称和签名，仍不证明设备数值或性能。

## 来源与版本复核

- [nvidia-cudnn-frontend: docs/developer/graph-api.mdx](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/developer/graph-api.mdx)
- [nvidia-cudnn-frontend: include/cudnn_frontend/graph_interface.h](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/include/cudnn_frontend/graph_interface.h)
- [nvidia-cudnn-frontend: include/cudnn_frontend/plans.h](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/include/cudnn_frontend/plans.h)
- [nvidia-cudnn-frontend: include/cudnn_frontend/backend/kernel_cache.h](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/include/cudnn_frontend/backend/kernel_cache.h)
- [nvidia-cudnn-frontend: python/cudnn/_pygraph.py](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/python/cudnn/_pygraph.py)
- [nvidia-cudnn-frontend: docs/utilities/dynamic-kernel-cache.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/utilities/dynamic-kernel-cache.md)
- [nvidia-cudnn-frontend: docs/utilities/python_graph_and_execution_backends.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/utilities/python_graph_and_execution_backends.md)
- [nvidia-cudnn-frontend-docs: graph-api](https://docs.nvidia.com/cudnn/developer/graph-api)
- [nvidia-cudnn-frontend-docs: dynamic-cache](https://docs.nvidia.com/cudnn/utilities/dynamic-kernel-cache)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## Norm 与 ragged 绑定的近期变化

当前 Graph 支持部分 Norm 的可选 scale/bias：不传 scale 时，反向不应伪造 DScale/DBias 输出。Python stats 形状推导已对齐 C++；LayerNorm 的 MEAN/INV_VARIANCE 可依调用方指定的同伴形状重新推导，但冲突的显式形状应拒绝。应先检查 graph.validate 的语义，再查 kernel。

当前 `_variant_pack_uids` 还将 tensor 上附带的 ragged offset 纳入运行时绑定，不能仅枚举 node 的直接输入/输出就认为所有地址齐备。plan 缓存命中不证明绑定的新长度、offset、stream 生命周期正确；调试时一起保存其 dtype、shape、地址归属和内容范围。

补充固定证据：

- [docs/operations/Normalizations.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/operations/Normalizations.md)
- [python/pygraph/norm.cpp](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/python/pygraph/norm.cpp)
- [test/python/norm/graph/test_layernorm.py](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/test/python/norm/graph/test_layernorm.py)

## 本次补充的实现与测试依据

- [nvidia-cudnn-frontend: docs/developer/overview.mdx](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/developer/overview.mdx)
- [nvidia-cudnn-frontend: python/cudnn/__init__.py](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/python/cudnn/__init__.py)
- [nvidia-cudnn-frontend: test/python/sdpa/frost/test_flashinfer_consumed_surface.py](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/test/python/sdpa/frost/test_flashinfer_consumed_surface.py)
- [nvidia-cudnn-frontend: test/python/core/graph/test_graph_native.py](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/test/python/core/graph/test_graph_native.py)
