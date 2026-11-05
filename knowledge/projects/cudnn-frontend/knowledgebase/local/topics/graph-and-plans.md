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
reviewed_on: '2026-11-04'
retrieved_on: '2026-11-04'
sources:
- source: nvidia-cudnn-frontend
  path: docs/developer/graph-api.mdx
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 70e4a64b5341538895fc178ff027d27ce61e10c051ea5d229b793ad5c9ffa597
- source: nvidia-cudnn-frontend
  path: include/cudnn_frontend/graph_interface.h
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: ccbf7ef8e59ad7db33dfde5fb0926e7cbfe768690a4e95ed538b1276835cf9e0
- source: nvidia-cudnn-frontend
  path: include/cudnn_frontend/plans.h
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: c48eea291766af3ac73c83dc5e35e391663a2244f036d0059d5b1ccbd76c4f44
- source: nvidia-cudnn-frontend
  path: include/cudnn_frontend/backend/kernel_cache.h
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 3ec261ac7b819ee1aac540a4227fa343e9677bdb9524457f0944f61e2dc863be
- source: nvidia-cudnn-frontend
  path: python/cudnn/_pygraph.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 99738780798d18ea38c5870b4a60ab5aa180638e0ef4d875d4920708819e5f5c
- source: nvidia-cudnn-frontend
  path: docs/utilities/dynamic-kernel-cache.md
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: a179f7f5607256b25a7239f3a9e3954c04402d46db9a6a2953c1417c1941513a
- source: nvidia-cudnn-frontend
  path: docs/utilities/python_graph_and_execution_backends.md
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 041561bad1b5dfc70aa930d9617045c59a9983ebc2412b1979b6f3084cd24f98
- source: nvidia-cudnn-frontend-docs
  path: graph-api
  commit: 62596f777aca773f340569b88fbd42c5fcd807249e8a188810cd38297d19cab9
  sha256: 7e2b3c0e0c3d40fd841f823308af5e101f0e122020942ea4ab9564e94fa20d3b
  url: https://docs.nvidia.com/cudnn/developer/graph-api
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend-docs
  path: dynamic-cache
  commit: 62596f777aca773f340569b88fbd42c5fcd807249e8a188810cd38297d19cab9
  sha256: 481446d36f4d782142608a553f8af939f3a758967a8c98f53c103e9b3efdfeb8
  url: https://docs.nvidia.com/cudnn/utilities/dynamic-kernel-cache
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend
  path: docs/operations/Normalizations.md
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: c56d2980195384db8250f31d1ca3141be6815c1e3ae20a5ac5e4909778127eb8
- source: nvidia-cudnn-frontend
  path: python/pygraph/norm.cpp
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: a05133d6fcbf06b45f63b5fd5ecfd8978e8b82e36cd576c6e800b522ec6988b5
- source: nvidia-cudnn-frontend
  path: test/python/norm/graph/test_layernorm.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 91423a247181ac8f7ccf528b0135f3661571803489ffb9f54a8dc39520fe90da
- source: nvidia-cudnn-frontend
  path: docs/developer/overview.mdx
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 920383cc59860d33321643185b7491445ea9c5135b56e727990a5039eb8b8870
- source: nvidia-cudnn-frontend
  path: python/cudnn/__init__.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: da22296651440287ad82d13cca464243f9d5fac69793d806bc456ea013e07eea
- source: nvidia-cudnn-frontend
  path: test/python/sdpa/frost/test_flashinfer_consumed_surface.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 7d5189f6a4d7ab65792c27a40b880b72487f301ff2daf96c5314b1cf3f5a49cc
- source: nvidia-cudnn-frontend
  path: test/python/core/graph/test_graph_native.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 7ebdaceb2f26927deb00d4eeac923fbab89167f5d301f45fc7a98ff2e3feae17
---

# cuDNN Graph、执行计划、Workspace 与动态形状缓存

## 构建阶段与执行阶段

显式接口常见路径为：定义 tensor 元数据与操作 → validate → build_operation_graph → create_execution_plans → check_support → build_plans → 查询 workspace → 绑定实际地址并 execute。高级 `cudnn.Graph` 包装会代办其中部分步骤，但生命周期仍存在。一个 graph 是数学描述，一个 engine/plan 是具体实现选择，一个 CUDA Graph 又是另一种捕获/重放机制，三者不能混称。

tensor 的 shape、stride、dtype、uid、virtual/output 属性决定图语义；variant pack 绑定运行时存储。计算精度、中间精度和边界 dtype 分开记录。临时 tensor 标为 virtual 可能促成融合，但跨 forward/backward 需要的结果必须保留为可消费的输出。

## plan 选择为什么会影响性能和数值

heuristic A/B 提供候选，fallback 注重可运行性；候选还需 check_support 和构建。可对可用计划做实测选择，但要同时查看 workspace、numerical/behavior notes、determinism 和 runtime compilation。最快计划的归约/降精度方式未必符合当前训练契约。最终保存实际 plan、版本与数值验证证据。

当前 Python `_pygraph.py` 可协调不同执行后端，相关 engine 是否启用、支持哪些图、失败后如何回退，都须核对当前实现。构图成功不是指定 engine 已执行，更不是所有 kernel 已融合成一个。

## 缓存与显存所有权

当前 CUDA Graph 默认 `PER_GRAPH` retention 持有 plan、kernel code 与 host-copy 数据，捕获后即使原 Graph 被销毁仍保留所需资源。选择 `NONE` 会把责任交给调用方：所有关联 graph、clone 和 graph exec 完成并销毁前，plan/host-copy 数据都须存活且不变；单保留 Graph 对象但重新 build/deserialize 同样会替换资源。cuDNN≥9.28 会一起应用 backend retention 设置，9.27 仅能去掉 Frontend 引用。性能收益需单独测量，不能默认关闭引用。

新 `populate_cuda_graph_direct` 仅用于已选 cuDNN backend plan、空的调用方图，以及没有 Frontend memcpy/memset 节点的计划；资格不等于 workspace=0。它必须与 `update_cuda_graph_direct` 配对；旧 populate/update 继续配对，不能猜拓扑混用。Python engine 路线应捕获 execute，不由这个 backend 专用接口推导同等支持。

计划缓存要按真正影响语义和支持面的条件区分，如图结构、形状、stride、dtype、相关选项、设备与库版本。复用 plan 不代表可以复用任意 buffer；执行期间 workspace、输出、saved tensors 与 stream/event 的生命周期要明确。多个并发 stream 不能无同步共享仍在使用的 scratch。

教程区分 build 侧的 dynamic-shape kernel cache 与 execute 侧的 shape override。前者可降低同拓扑图的重复编译成本，后者受实际 plan 的运行时形状支持约束；不能据“支持动态 shape”推导任意长度、stride 或 dtype 均能复用。跨版本反序列化也需验证，而非把缓存当永久二进制接口。

当前 Python engine 的 serialize 保存图 IR、engine 身份/knobs，以及可选编译缓存原件；不能精确表示的 callback/框架对象会被拒绝，build 时绑定的实际 tensor 不随 blob 保存。deserialize 只在编译环境 manifest 完全一致时 seed kernel，否则重新编译，`enforce_precompiled=True` 则拒绝回编译；C++ Graph 不读取这种 `CUDNN_FE_PYPLAN` 格式。新缓存冷启动去重依赖 POSIX advisory lock，不支持锁时继续编译；使用中的 `.locks` inode 不应删除。

官网的 backend 默认 kernel cache 另按设备维护并使用 LRU，与上述 Python 编译制品缓存不是同一层；传入 custom cache 时，容量/生命周期策略也不同。缓存命中不能替代输出地址、长度及 stream 生命周期校验。

## 故障定位顺序

图验证失败先查 tensor 元数据；无支持计划查 operation 支持面与硬件/版本；build 失败查编译依赖；execute 失败查地址、workspace、stream 与生命周期；性能下降再区分计划变化、重复构建和硬件竞争。保存最小图、输入元数据和首个失败步骤，比只保留最后一个异常更易复现。

## 当前边界：指针对齐、计划排序与外部消费者

在 `a7269d7607db`，SDPA 的声明 stride 与执行指针有独立对齐校验，默认16字节。C++ graph 在 execute、populate/update CUDA graph 及准备好的 variant-pack 模板中都检查相应地址；legacy Slice 从本次源绑定重新派生地址，不能污染下次调用的 caller map。序列化保存 aligned_operands，新反序列化可继续检查；旧序列化数据缺该字段时不会自动获得这层保护。

dynamic shape 的一般 override 接口仍区分 build 与 execute，但本版 SDPA forward 的 override_strides 不会改变已声明 stride，必须按具体 node 检查，不能拿通用接口说明宣称可以任意换布局。runtime workspace 应按实际 override shape 查询，不能沿用 cache-shape 的旧容量。

autotune callback 可排序/裁剪候选，但当前实现先验证返回的 plan 非空、已构建且不重复，再将 plan 和相关元数据一起重排，candidate 指向新首项。旧 index、workspace、notes 不应脱离排序结果复用；失败回退也要确认实际候选。OSS RMSNorm+SiLU build 失败会取消其候选并尝试 cuDNN plans，两者都失败时保留复合错误，不能把存在 engine 对象当已经构建成功。

FlashInfer 消费的 `selected_engine`、`backend_plan_entries()` 与 native binder 能力名已明确为对外合同。`cudnn.sdpa_capabilities()` 返回当前扩展支持的 capability 名集合，`selected_engine is None` 表示所选 cuDNN backend entry，而不是无计划；backend entries 为空也不能由其他 Python engine 可用来填补。CuTe DSL 的设备感知资格另看 `cutedsl_runtime_available(device_cc)`，仅检查包版本不足以证明目标架构可编译。host-only consumed-surface 测试固定名称和签名，仍不证明设备数值或性能。

## 来源与版本复核

- [nvidia-cudnn-frontend: docs/developer/graph-api.mdx](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/docs/developer/graph-api.mdx)
- [nvidia-cudnn-frontend: include/cudnn_frontend/graph_interface.h](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/include/cudnn_frontend/graph_interface.h)
- [nvidia-cudnn-frontend: include/cudnn_frontend/plans.h](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/include/cudnn_frontend/plans.h)
- [nvidia-cudnn-frontend: include/cudnn_frontend/backend/kernel_cache.h](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/include/cudnn_frontend/backend/kernel_cache.h)
- [nvidia-cudnn-frontend: python/cudnn/_pygraph.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/cudnn/_pygraph.py)
- [nvidia-cudnn-frontend: docs/utilities/dynamic-kernel-cache.md](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/docs/utilities/dynamic-kernel-cache.md)
- [nvidia-cudnn-frontend: docs/utilities/python_graph_and_execution_backends.md](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/docs/utilities/python_graph_and_execution_backends.md)
- [nvidia-cudnn-frontend-docs: graph-api](https://docs.nvidia.com/cudnn/developer/graph-api)
- [nvidia-cudnn-frontend-docs: dynamic-cache](https://docs.nvidia.com/cudnn/utilities/dynamic-kernel-cache)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## Norm 与 ragged 绑定的近期变化

当前 Graph 支持部分 Norm 的可选 scale/bias：不传 scale 时，反向不应伪造 DScale/DBias 输出。Python stats 形状推导已对齐 C++；LayerNorm 的 MEAN/INV_VARIANCE 可依调用方指定的同伴形状重新推导，但冲突的显式形状应拒绝。应先检查 graph.validate 的语义，再查 kernel。

当前 `_variant_pack_uids` 还将 tensor 上附带的 ragged offset 纳入运行时绑定，不能仅枚举 node 的直接输入/输出就认为所有地址齐备。plan 缓存命中不证明绑定的新长度、offset、stream 生命周期正确；调试时一起保存其 dtype、shape、地址归属和内容范围。

补充固定证据：

- [docs/operations/Normalizations.md](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/docs/operations/Normalizations.md)
- [python/pygraph/norm.cpp](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/pygraph/norm.cpp)
- [test/python/norm/graph/test_layernorm.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/test/python/norm/graph/test_layernorm.py)

## 本次补充的实现与测试依据

- [nvidia-cudnn-frontend: docs/developer/overview.mdx](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/docs/developer/overview.mdx)
- [nvidia-cudnn-frontend: python/cudnn/__init__.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/cudnn/__init__.py)
- [nvidia-cudnn-frontend: test/python/sdpa/frost/test_flashinfer_consumed_surface.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/test/python/sdpa/frost/test_flashinfer_consumed_surface.py)
- [nvidia-cudnn-frontend: test/python/core/graph/test_graph_native.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/test/python/core/graph/test_graph_native.py)
