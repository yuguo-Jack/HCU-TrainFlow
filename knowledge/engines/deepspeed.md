---
id: engines/deepspeed
title: DeepSpeed：训练引擎、ZeRO、流水线与恢复工程指南
engine: deepspeed
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime
  execution
sources:
- source: deepspeedai-deepspeed
  path: README.md
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: e2f2dad685784770f1cd1fe72ba3be22788864ddf9234a899b75fb7dbdd15151
- source: deepspeedai-deepspeed
  path: setup.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: d694bc8b1cd23e50c79763dab76cc08461cd963aa6e4e5b6b31d9f18f359ed53
- source: deepspeedai-deepspeed
  path: deepspeed/__init__.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 6c7e11d078f34d8b2de619eeccca5931aeddea53fe8852896fcf0bfb747bde04
- source: deepspeedai-deepspeed
  path: accelerator/real_accelerator.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 4a049cae92751d065cfb6f613647fa57e75953f69bcd9239f82690d7b5fbd39a
- source: deepspeedai-deepspeed
  path: op_builder/builder.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 91af4033fdf95b016ce7fe5588c6c3658fa2ab3b8f20a97839e476d04b5f58d0
- source: deepspeedai-deepspeed
  path: deepspeed/launcher/runner.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 956d554ea5c9b142ab4bae47c8317cce11f7b23748e09849b7876072c66cf9a0
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/engine.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 2ff52b1d128f42e49b9a01d2b95b18bd83285af60db4ce01baaa5c078c5920ca
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/config.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: cf8beb53835f192afdf5a0c8a4b5bbf3fb09d1fdc767a0f46f66b1cdf38c650a
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage_1_and_2.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: aa9556509f8249b9e82f6208297311c69e25eb6e560e64c7670fe3bb928436b3
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage3.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: ccee95e1b4c7d43cb3523bc94a793411dafe15bd23c3cb7c348cb093168c7d42
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/partitioned_param_coordinator.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: a52014bb6bb754ba315c9f58eb6d5ee52781e7da154f939c7d0c70eb9cbf5e2a
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/pipe/engine.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 211edb569ad0dc1c1b830c818a0ea15b64e22986c4840468af73304d825c8ae3
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/pipe/schedule.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 52aae5310aa18183d093149dd12cb20b02e6a8143e906bd32cf4fcdb96542a6b
- source: deepspeedai-deepspeed
  path: docs/_tutorials/advanced-install.md
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: e930e94bd72c37c14613e76fc5bdc09c6f3d72543e69dfe4eb2c119196e708e0
- source: deepspeedai-deepspeed
  path: docs/_tutorials/getting-started.md
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 8494b298115871b4d5d2b0e72132123bcfb703768678ca726d51cc62b6c4c05e
- source: deepspeedai-deepspeed
  path: docs/_tutorials/universal-checkpointing.md
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 61d4c532cc607d6d9283d36ffa83ea35da606ff4de9d7a9bc59625a88c5fe0ce
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_config.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 3e240d16f1581bc1e8db115f211bcfb2f395d58e39b0a43ef7fa3e6c4bfb8545
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_stale_handle_wait.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: a06caf747dd654b3cda2559cb8de569ac7769d690a6bd2bd30f20134e4e78f73
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_shared_loss_gradient.py
  commit: 1c862f7df93f0345b977c67f5408d967b94bf4ae
  sha256: 176f5b6bc78164896e65077b8fea71661b2c1d8b076ff2563962aa32506c8c20
---

# DeepSpeed：训练引擎、ZeRO、流水线与恢复工程指南

## 1. 定位与使用边界

DeepSpeed 接管模型训练的梯度累积、优化器、分布式状态和部分执行调度，既是其他引擎的后端，也是可以直接集成的训练引擎。它通常不替调用方决定 tokenizer、模型结构、样本 mask 或任务 loss。训练入口成功并不代表模型配方正确。

本页依据官方 master 的固定源码，HCU 执行时仍以已验证的 HCU 分支、Torch/DTK 和扩展为准。CUDA Accelerator 这个类名不等于硬件只能是 NVIDIA，也不构成 HCU 支持承诺；确认实际 `get_accelerator()`、`torch.version.hip`、编译产物和加载路径。官方源码用于比较机制与版本差异。

## 2. 工程目录和问题入口

| 目录或文件 | 职责与阅读方向 |
| --- | --- |
| [`deepspeed/__init__.py`](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/deepspeed/__init__.py) | `initialize` 组装 engine、optimizer、dataloader、scheduler；区分普通模型与 `PipelineModule` |
| `deepspeed/launcher/runner.py` | hostfile、资源过滤、环境传递及多机 launcher；启动数量异常从这里查 |
| `deepspeed/runtime/engine.py` | forward、backward、accumulation boundary、step、checkpoint；调用方与引擎的状态所有权 |
| `runtime/zero/stage_1_and_2.py`、`stage3.py` | 状态分片、梯度归约、optimizer/offload；实际瓶颈不能只从 JSON 判断 |
| `runtime/zero/partition_parameters.py`、`partitioned_param_coordinator.py` | 参数分片状态、按需 gather、trace、prefetch 和释放 |
| `runtime/pipe/engine.py`、`schedule.py` | PP 的 `train_batch`、1F1B、send/recv 与同步梯度 |
| `runtime/activation_checkpointing`、`runtime/swap_tensor` | activation 重算和 NVMe 状态交换；先核对所选路径是否真的使用 |
| `accelerator/`、`op_builder/`、`csrc/` | 设备抽象、JIT/预编译扩展、底层 kernel；导入成功后继续确认 op 装载 |
| `tests/unit/runtime/zero`、`tests/unit/runtime/pipe` | 分片/共享梯度/PP 的回归入口；分布式 fixture 和设备依赖是测试契约的一部分 |
| `docs/_tutorials`、`docs/_blogs` | 运行教程与特性说明；原文和当前源码可能处于不同演进阶段 |

## 3. 安装、依赖和扩展确认

[安装教程](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/docs/_tutorials/advanced-install.md)区分安装时预编译和首次使用时 JIT。官方最小源码安装可用 `python -m pip install .`；需要预编译时先装匹配 Torch，再只开启所需 `DS_BUILD_*`。`DS_BUILD_OPS=1` 是尝试所有兼容 op，不能把它当成 HCU 上全部可用的保证。

`ds_report` / `python -m deepspeed.env_report` 检查环境、兼容和已装 op；继续执行任务真正使用的 optimizer/attention op。只看报告不等于通过运行测试。JIT 缓存通过 `TORCH_EXTENSIONS_DIR` 置于本任务映射目录，并按 Python、Torch、DTK/编译器、gfx 分隔，避免别的环境留下的二进制误加载。

[`op_builder/builder.py`](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/op_builder/builder.py)负责兼容检查、构建/加载和 ROCm 检测；[`accelerator/real_accelerator.py`](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/accelerator/real_accelerator.py)负责 accelerator 选择。官方 `DS_ACCELERATOR` 可选值里没有 `hcu`，不要凭硬件名称发明环境变量值。HCU 仓库若增加或替换设备路径，联查 HCU-Knowledge 和该分支源码。

## 4. 运行与分层验收

[Getting Started](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/docs/_tutorials/getting-started.md)给出 `deepspeed.initialize` 和 launcher/JSON 配置。普通 engine 的基本循环是 `loss = engine(batch)`、`engine.backward(loss)`、`engine.step()`；engine 内部处理 accumulation boundary，调用方不能再次独立 `optimizer.step()` 或重复缩放 loss。Pipeline 模型使用自己的 `engine.train_batch(data_iter=...)`，见专题。

保留解析后的 JSON、调用方模型脚本、启动环境、实际 engine/optimizer 类。核对

`global batch = per-device micro batch × gradient accumulation × DP world size`。

这里的 DP 不是混合并行的总 world size。不要为了通过 assert 随意改变序列长度、模型维度或有效样本数量。初测依次验证扩展装载 → 单步 forward/backward/step → 所选 ZeRO/PP 的多 rank → 保存恢复并继续一步；吞吐测量剔除编译/初始化，记录有效 token 而不仅是 padding token。

## 5. 模型、数据与数值契约

DeepSpeed 接收调用方产生的 loss；label shift、ignore mask、token/sample 加权、MoE router 辅助 loss 的定义在调用方。`initialize` 返回组合对象并不验证这些语义。FP16 的 loss scaling、BF16 梯度累积、FP32 master/state 和 clip/norm 配置分别记录；共享图、多 engine 或 reentrant checkpoint 场景还需核对每条 backward 分支只缩放一次。

[`test_zero_shared_loss_gradient.py`](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/tests/unit/runtime/zero/test_zero_shared_loss_gradient.py)用手工参考梯度检查 engine/module 共享 loss、两个 engine 管理的 backward、reentrant checkpoint 等路径，是比单纯观察训练 loss 更直接的局部回归入口。它不替代模型阶段 loss 验证。

## 6. 从配置到执行的调用链

`deepspeed.initialize` → 解析配置/初始化进程组 → `DeepSpeedEngine` 或 `PipelineEngine` → 配置基础 optimizer/precision wrapper → 相应 ZeRO optimizer → hooks、bucket 和分片存储 → 通信/设备扩展。

ZeRO-3 的 module hooks 进一步进入 coordinator：按当前模块获取参数、等待必须的 gather、按完整 trace 预取后续参数、在生命周期允许时释放。数据依赖决定通信和显存是否可以重叠，不能由“已设置 overlap”推导出实际隐藏了通信。

## 7. 性能和显存的两个核心专题

- [ZeRO 状态生命周期、prefetch 与 offload](deepspeed/topics/zero-state-lifecycle.md)：stage 选择、常驻/临时状态、参数 trace 与异步存储所有权。
- [Pipeline 1F1B、batch 和 checkpoint 恢复](deepspeed/topics/pipeline-schedule-and-checkpoint.md)：PP bubble、activation 驻留、ZeRO 兼容及 Universal 格式。

分析时把计算、参数 gather、梯度 reduce、CPU optimizer、D2H/H2D、NVMe I/O 和主机调度拆开。bucket 的单位是元素，需要乘 dtype 字节数，再计入同时存活的 buffer；不是把一个 bucket 作为全部峰值。微批增大改善 kernel 效率但提高 activation 峰值；分片/重算/offload 降显存也分别增加通信、计算或 I/O。

默认 `overlap_comm=None` 经 validator 解析为 **stage 3 开启、其他 stage 关闭**。`stage3_param_persistence_threshold`、max-live/reuse-distance、prefetch bucket 和 leaf/module granularity 共同作用，调参以实际等待和峰值为依据。PP/ZeRO 的兼容按所用 engine 判断，不能把外部引擎的组合经验套到官方 `PipelineEngine`。

## 8. 诊断、恢复和回退

| 症状 | 优先证据和复核 |
| --- | --- |
| 首步 JIT 失败/第二个环境加载失败 | op builder 日志、编译器和目标 gfx、扩展路径/ABI；隔离任务缓存后重建所需 op |
| rank 卡在 gather/reduce | 各 rank stack、最近 collective、coordinator trace、参数状态/leaf hooks，核对所有 rank 顺序一致 |
| offload 后 NaN/偶发错误 | 梯度生产流、归约流、CPU staging buffer、异步 copy 的存储生命周期；关 overlap 的对照仍不能排除 offload 本身的异步问题 |
| 显存峰值不符合估算 | allgather 临时副本、persist 参数、activation/recompute、save/generation 的全权重 gather |
| 恢复后 loss 或进度跳变 | optimizer/master weights、scheduler、计数和 RNG/数据位置；只加载模型权重不是完整恢复 |

保存和加载属于分布式操作，参与 rank 必须遵守 engine 格式和相同调用顺序。ZeRO-3 保存后的完整权重导出、分片 checkpoint 续训与 Universal 转换是三件事。`elastic_checkpoint` 的旧 ZeRO-3 功能已弃用；不能凭名称推断可随意换拓扑。[Universal 教程](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/docs/_tutorials/universal-checkpointing.md)说明受支持模型布局和 AutoTP/AutoEP 元数据的转换约束。

## 9. Release、PR、继续搜索和更新

[官方教程](https://www.deepspeed.ai/tutorials/) · [文档](https://deepspeed.readthedocs.io/en/latest/) · [Releases](https://github.com/deepspeedai/DeepSpeed/releases) · [开放/已合并 PR](https://github.com/deepspeedai/DeepSpeed/pulls)。固定源码完整目录见[source map](../source-maps/deepspeedai-deepspeed.md)，教程原文见[本地来源](../upstream-docs/deepspeedai-deepspeed/)。这些入口不表示所有历史特性均已精读，也未在本轮确认一份统一长期 roadmap。

现有 [PR #8534：弃用 LoCo ZeRO++](../prs/deepspeedai--DeepSpeed/PR-8534.md) 和 [PR #8632：offload 梯度存储/stream 修复](../prs/deepspeedai--DeepSpeed/PR-8632.md)应与当前实现一起读。尚未收录的问题用 `wiki-search-pr "offload gradient storage" --engine deepspeed`，再取 PR 正文、review、最终 diff 与 `wiki-code` 固定源码。

更新配置、coordinator、precision/backward 或 checkpoint 时，同时复核总览、两专题、相关案例及调用方（Swift/LlamaFactory 等）。分别登记源码合入、发布版本、HCU 适配和任务实测。本轮是固定源码/官方测试阅读，没有执行 HCU 分布式测试；结论不覆盖全部 op、所有混合并行或历史模型配方。
