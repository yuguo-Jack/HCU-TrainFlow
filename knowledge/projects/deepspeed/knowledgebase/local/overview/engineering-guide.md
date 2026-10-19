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
reviewed_on: '2026-10-20'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime execution
sources:
- source: deepspeedai-deepspeed
  path: README.md
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 5cc9ec8143564f0d56764b9c09fdc6086a8c6fac0e42d5130666605815e60ac7
- source: deepspeedai-deepspeed
  path: setup.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: d694bc8b1cd23e50c79763dab76cc08461cd963aa6e4e5b6b31d9f18f359ed53
- source: deepspeedai-deepspeed
  path: deepspeed/__init__.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 83eb6faeb39bea741a292b507fc6755fcc9c5dff9ceb3a2e4805ebf9c9e31b75
- source: deepspeedai-deepspeed
  path: accelerator/real_accelerator.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 0f38b4a2ec94aa013b8238d2bced80e20f4f26005df8fab08e34575c9a9acc6c
- source: deepspeedai-deepspeed
  path: op_builder/builder.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 737f9a00e86a97e4b8a45a0f1055d9bafe3ad3288ed056751b7c8b51ac64aa5d
- source: deepspeedai-deepspeed
  path: deepspeed/launcher/runner.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 956d554ea5c9b142ab4bae47c8317cce11f7b23748e09849b7876072c66cf9a0
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/engine.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: e35eaa313874d2b3bd5bc9169dad35405819df2dfb1e7abdffa0c2f03db36c75
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/config.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: cf8beb53835f192afdf5a0c8a4b5bbf3fb09d1fdc767a0f46f66b1cdf38c650a
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage_1_and_2.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 752235af95d0de6f5fe6322b13409c736abe9d0c77be24f85d87489cc41489cb
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage3.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 4ff3fdb4cbabaddfeaa866e43785b49a69cdfe35db4e0ceda6f1b432b6fbf9d7
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/partitioned_param_coordinator.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: a43fd966c88dc3699f5b18e2bfe51fac222e79365664addce9ed485d617a78d0
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/pipe/engine.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 211edb569ad0dc1c1b830c818a0ea15b64e22986c4840468af73304d825c8ae3
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/pipe/schedule.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 52aae5310aa18183d093149dd12cb20b02e6a8143e906bd32cf4fcdb96542a6b
- source: deepspeedai-deepspeed
  path: docs/_tutorials/advanced-install.md
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: e930e94bd72c37c14613e76fc5bdc09c6f3d72543e69dfe4eb2c119196e708e0
- source: deepspeedai-deepspeed
  path: docs/_tutorials/getting-started.md
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 8494b298115871b4d5d2b0e72132123bcfb703768678ca726d51cc62b6c4c05e
- source: deepspeedai-deepspeed
  path: docs/_tutorials/universal-checkpointing.md
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 61d4c532cc607d6d9283d36ffa83ea35da606ff4de9d7a9bc59625a88c5fe0ce
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_config.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 3e240d16f1581bc1e8db115f211bcfb2f395d58e39b0a43ef7fa3e6c4bfb8545
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_stale_handle_wait.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: a06caf747dd654b3cda2559cb8de569ac7769d690a6bd2bd30f20134e4e78f73
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_shared_loss_gradient.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 176f5b6bc78164896e65077b8fea71661b2c1d8b076ff2563962aa32506c8c20
- source: deepspeedai-deepspeed
  path: accelerator/cuda_accelerator.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 84b4f5325f4d82f616652e7b9d9624f4ce811ee0f30cb0c32468ae08a33a75ad
- source: deepspeedai-deepspeed
  path: op_builder/__init__.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 1c9d345354ab8625c37ed4c8abd939859a7e0ae44f6791963b241eaea802db55
- source: deepspeedai-deepspeed
  path: op_builder/cpu/__init__.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 2b3440e0715bd58e1411081168d26b5ff546a169e13734fdc438668083f90d44
- source: deepspeedai-deepspeed
  path: deepspeed/ops/adam/cpu_adam.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 634fc0da21d455e20c187a9eb7f9668de961764e433c2d5da8f0da285282ffac
- source: deepspeedai-deepspeed
  path: deepspeed/sequence/cross_entropy.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: eeb4a00ac6fe239d37345e874d6072ad084f4216fb02a273f1145fd5865105fc
- source: deepspeedai-deepspeed
  path: deepspeed/sequence/linear_cross_entropy.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: 4b063fa6e59b875b0014f734d99a710cea9f38acc3307c1ba60e1272d3922d12
- source: deepspeedai-deepspeed
  path: deepspeed/sequence/vocab_parallel_ops.py
  commit: 0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c
  sha256: c643ffd927d7229427d73965e6ad7b39dad2d65fcd5c20a048de30f64822f51c
---

# DeepSpeed：训练引擎、ZeRO、流水线与恢复工程指南

## 1. 定位与使用边界

DeepSpeed 接管模型训练的梯度累积、优化器、分布式状态和部分执行调度，既是其他引擎的后端，也是可以直接集成的训练引擎。它通常不替调用方决定 tokenizer、模型结构、样本 mask 或任务 loss。训练入口成功并不代表模型配方正确。

本页依据官方 master 的固定源码，HCU 执行时仍以已验证的 HCU 分支、Torch/DTK 和扩展为准。CUDA Accelerator 这个类名不等于硬件只能是 NVIDIA，也不构成 HCU 支持承诺；确认实际 `get_accelerator()`、`torch.version.hip`、编译产物和加载路径。官方源码用于比较机制与版本差异。

## 2. 工程目录和问题入口

| 目录或文件 | 职责与阅读方向 |
| --- | --- |
| [`deepspeed/__init__.py`](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/deepspeed/__init__.py) | `initialize` 组装 engine、optimizer、dataloader、scheduler；区分普通模型与 `PipelineModule` |
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

[安装教程](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/docs/_tutorials/advanced-install.md)区分安装时预编译和首次使用时 JIT。官方最小源码安装可用 `python -m pip install .`；需要预编译时先装匹配 Torch，再只开启所需 `DS_BUILD_*`。`DS_BUILD_OPS=1` 是尝试所有兼容 op，不能把它当成 HCU 上全部可用的保证。

`ds_report` / `python -m deepspeed.env_report` 检查环境、兼容和已装 op；继续执行任务真正使用的 optimizer/attention op。只看报告不等于通过运行测试。JIT 缓存通过 `TORCH_EXTENSIONS_DIR` 置于本任务映射目录，并按 Python、Torch、DTK/编译器、gfx 分隔，避免别的环境留下的二进制误加载。

[`op_builder/builder.py`](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/op_builder/builder.py)负责兼容检查、构建/加载和 ROCm 检测；[`accelerator/real_accelerator.py`](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/accelerator/real_accelerator.py)负责 accelerator 选择。官方 `DS_ACCELERATOR` 可选值里没有 `hcu`，不要凭硬件名称发明环境变量值。HCU 仓库若增加或替换设备路径，联查 HCU-Knowledge 和该分支源码。

当前 import 路径将 Triton、Muon 和部分 compiler/op builder 探测延后到首次使用，不能用 `import deepspeed` 的耗时或成功替代实际 op 验收。`HAS_TRITON` 是懒读取属性，ROCm 路径仍明确返回 False，范围是未经 ROCm 验证的 DeepSpeed Triton inference kernels，不表示 ROCm/HCU 的 Triton 编译器本身不可用。新增 klxpu accelerator 的自动探测也不提供 `DS_ACCELERATOR=hcu`；记录最终选中的对象与加载模块。

CPUAdam/CPUAdagrad/CPULion 的 builder 已集中到 `op_builder/cpu/`。CUDA accelerator 的 class table 仍显式映射这些公开 builder 名称，CPU optimizer 继续从 `deepspeed.ops.op_builder` 取得 builder 后真实 `load()`；旧顶层源码路径的删除不表示 ZeRO CPU offload 被移除。CPUAdam 构建/装载失败会显式抛出 RuntimeError，应检查实际编译和模块路径，不能用 `import deepspeed` 成功代替这一步。

## 4. 运行与分层验收

[Getting Started](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/docs/_tutorials/getting-started.md)给出 `deepspeed.initialize` 和 launcher/JSON 配置。普通 engine 的基本循环是 `loss = engine(batch)`、`engine.backward(loss)`、`engine.step()`；engine 内部处理 accumulation boundary，调用方不能再次独立 `optimizer.step()` 或重复缩放 loss。Pipeline 模型使用自己的 `engine.train_batch(data_iter=...)`，见专题。

保留解析后的 JSON、调用方模型脚本、启动环境、实际 engine/optimizer 类。核对

`global batch = per-device micro batch × gradient accumulation × DP world size`。

这里的 DP 不是混合并行的总 world size。不要为了通过 assert 随意改变序列长度、模型维度或有效样本数量。初测依次验证扩展装载 → 单步 forward/backward/step → 所选 ZeRO/PP 的多 rank → 保存恢复并继续一步；吞吐测量剔除编译/初始化，记录有效 token 而不仅是 padding token。

## 5. 模型、数据与数值契约

DeepSpeed 接收调用方产生的 loss；label shift、ignore mask、token/sample 加权、MoE router 辅助 loss 的定义在调用方。`initialize` 返回组合对象并不验证这些语义。FP16 的 loss scaling、BF16 梯度累积、FP32 master/state 和 clip/norm 配置分别记录；共享图、多 engine 或 reentrant checkpoint 场景还需核对每条 backward 分支只缩放一次。

[`test_zero_shared_loss_gradient.py`](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/tests/unit/runtime/zero/test_zero_shared_loss_gradient.py)用手工参考梯度检查 engine/module 共享 loss、两个 engine 管理的 backward、reentrant checkpoint 等路径，是比单纯观察训练 loss 更直接的局部回归入口。它不替代模型阶段 loss 验证。

AutoTP 的词表切分是需要另查的 loss 所有权边界：当前 HF `tp_plan` 含 `embedding_rowwise` 且 embedding 与输出 head tied 时，`vocab_parallel_lm_head=None` 也可能自动启用 no-gather head；显式关闭、兼容性检查或 DeepCompile 限制会改变选择。`finalize_autotp` 发现 `VocabParallelLinear` 后通过 `configure_vocab_parallel_loss` 替换模型 `loss_function`。因此应检查最终 head、输出是否仍为完整词表，以及实际 loss hook，不能假定初始化前后只是参数被切片。

安装的 `VocabParallelCausalLMLoss` 在未给 `shift_labels` 时完成 causal shift；按实际 TP shard 固定缓存词表元数据，不可跨 teacher/student 或变更 shard 复用同一实例。Ulysses engine 已按有效 token 计数聚合时，该 loss 的 `sp_group` 保持 None，避免再归约一次。Liger backend 还要求真实 TP group、等宽词表分片和支持 Triton 的 accelerator等条件；这些分发条件不满足会走 Torch，条件满足但缺 Liger 包则显式报 ImportError。其 kernel 只支持一次一阶 backward，retained graph/高阶梯度需用 Torch 路径；未因包可导入而获得 HCU 资格。

新增 `vocab_parallel_linear_cross_entropy` 则是独立的 hidden/weight/target 接口，当前 AutoTP causal-loss hook 没有调用它；它不替调用方 shift labels。实现前向按 token 行分块、反向按词表列块重算 logits，hidden 梯度用 FP32 累加/TP 归约；仍有最终参数梯度与临时 GEMM 成本，不能把“未物化完整 logits”推为模型峰值或吞吐必改善。另有 vocabulary-parallel logprob/entropy/KL 返回逐 token 结果，mask 和目标归约仍归调用方；TP 各 rank 应反传相同 loss，teacher 需要停止梯度时显式 detach。这些是新 API 的适用合同，本页没有替任务启用它们或执行设备回归。

## 6. 从配置到执行的调用链

`deepspeed.initialize` → 解析配置/初始化进程组 → `DeepSpeedEngine` 或 `PipelineEngine` → 配置基础 optimizer/precision wrapper → 相应 ZeRO optimizer → hooks、bucket 和分片存储 → 通信/设备扩展。

ZeRO-3 的 module hooks 进一步进入 coordinator：按当前模块获取参数、等待必须的 gather、按完整 trace 预取后续参数、在生命周期允许时释放。数据依赖决定通信和显存是否可以重叠，不能由“已设置 overlap”推导出实际隐藏了通信。

## 7. 性能和显存的两个核心专题

- [ZeRO 状态生命周期、prefetch 与 offload](../topics/zero-state-lifecycle.md)：stage 选择、常驻/临时状态、参数 trace 与异步存储所有权。
- [Pipeline 1F1B、batch 和 checkpoint 恢复](../topics/pipeline-schedule-and-checkpoint.md)：PP bubble、activation 驻留、ZeRO 兼容及 Universal 格式。

分析时把计算、参数 gather、梯度 reduce、CPU optimizer、D2H/H2D、NVMe I/O 和主机调度拆开。bucket 的单位是元素，需要乘 dtype 字节数，再计入同时存活的 buffer；不是把一个 bucket 作为全部峰值。微批增大改善 kernel 效率但提高 activation 峰值；分片/重算/offload 降显存也分别增加通信、计算或 I/O。

默认 `overlap_comm=None` 经 validator 解析为 **stage 3 开启、其他 stage 关闭**。`stage3_param_persistence_threshold`、max-live/reuse-distance、prefetch bucket 和 leaf/module granularity 共同作用，调参以实际等待和峰值为依据。PP/ZeRO 的兼容按所用 engine 判断，不能把外部引擎的组合经验套到官方 `PipelineEngine`。

本轮 ZeRO-1/2 的 FP32 累积链有重要修订：低精度参数的梯度不应在归约后先截断回 BF16 再累积。当前实现保留 FP32 collective 结果并写入 owned local FP32 partition，动态 offload/reload 也重建共享 views；见[ZeRO 专题](../topics/zero-state-lifecycle.md)。`grad_accum_dtype`、通信 dtype 和参数 dtype 是三个边界，配置写成 FP32 不足以证明整条链保留了精度。

## 8. 诊断、恢复和回退

| 症状 | 优先证据和复核 |
| --- | --- |
| 首步 JIT 失败/第二个环境加载失败 | op builder 日志、编译器和目标 gfx、扩展路径/ABI；隔离任务缓存后重建所需 op |
| rank 卡在 gather/reduce | 各 rank stack、最近 collective、coordinator trace、参数状态/leaf hooks，核对所有 rank 顺序一致 |
| offload 后 NaN/偶发错误 | 梯度生产流、归约流、CPU staging buffer、异步 copy 的存储生命周期；关 overlap 的对照仍不能排除 offload 本身的异步问题 |
| 显存峰值不符合估算 | allgather 临时副本、persist 参数、activation/recompute、save/generation 的全权重 gather |
| 恢复后 loss 或进度跳变 | optimizer/master weights、scheduler、计数和 RNG/数据位置；只加载模型权重不是完整恢复 |

保存和加载属于分布式操作，参与 rank 必须遵守 engine 格式和相同调用顺序。ZeRO-3 保存后的完整权重导出、分片 checkpoint 续训与 Universal 转换是三件事。`elastic_checkpoint` 的旧 ZeRO-3 功能已弃用；不能凭名称推断可随意换拓扑。[Universal 教程](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/docs/_tutorials/universal-checkpointing.md)说明受支持模型布局和 AutoTP/AutoEP 元数据的转换约束。

## 9. Release、PR、继续搜索和更新

[官方教程](https://www.deepspeed.ai/tutorials/) · [文档](https://deepspeed.readthedocs.io/en/latest/) · [Releases](https://github.com/deepspeedai/DeepSpeed/releases) · [开放/已合并 PR](https://github.com/deepspeedai/DeepSpeed/pulls)。固定源码完整目录见[source map](../../upstream/source-map/deepspeedai-deepspeed.md)，教程原文见[本地来源](../../upstream/docs/deepspeedai-deepspeed)。这些入口不表示所有历史特性均已精读，也未在本轮确认一份统一长期 roadmap。

现有 [PR #8534：弃用 LoCo ZeRO++](../../upstream/prs/deepspeedai--DeepSpeed/PR-8534.md) 和 [PR #8632：offload 梯度存储/stream 修复](../../upstream/prs/deepspeedai--DeepSpeed/PR-8632.md)应与当前实现一起读。尚未收录的问题用 `wiki-search-pr "offload gradient storage" --engine deepspeed`，再取 PR 正文、review、最终 diff 与 `wiki-code` 固定源码。

更新配置、coordinator、precision/backward 或 checkpoint 时，同时复核总览、两专题、相关案例及调用方（Swift/LlamaFactory 等）。分别登记源码合入、发布版本、HCU 适配和任务实测。本轮是固定源码/官方测试阅读，没有执行 HCU 分布式测试；结论不覆盖全部 op、所有混合并行或历史模型配方。


## 本轮补充固定证据


- [accelerator/cuda_accelerator.py](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/accelerator/cuda_accelerator.py)
- [op_builder/__init__.py](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/op_builder/__init__.py)
- [op_builder/cpu/__init__.py](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/op_builder/cpu/__init__.py)
- [deepspeed/ops/adam/cpu_adam.py](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/deepspeed/ops/adam/cpu_adam.py)
- [deepspeed/sequence/cross_entropy.py](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/deepspeed/sequence/cross_entropy.py)
- [deepspeed/sequence/linear_cross_entropy.py](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/deepspeed/sequence/linear_cross_entropy.py)
- [deepspeed/sequence/vocab_parallel_ops.py](https://github.com/deepspeedai/DeepSpeed/blob/0eb3a8bcc6d9a8775478e5377482c4bf2dd23c1c/deepspeed/sequence/vocab_parallel_ops.py)
