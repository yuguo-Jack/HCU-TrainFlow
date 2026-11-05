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
reviewed_on: '2026-11-04'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime execution
sources:
- source: deepspeedai-deepspeed
  path: README.md
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 452cb0816f31b3997e50ea97a88c3ebd6456cdcdd1b36ac079b378a66350edb5
- source: deepspeedai-deepspeed
  path: setup.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: d694bc8b1cd23e50c79763dab76cc08461cd963aa6e4e5b6b31d9f18f359ed53
- source: deepspeedai-deepspeed
  path: deepspeed/__init__.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 83eb6faeb39bea741a292b507fc6755fcc9c5dff9ceb3a2e4805ebf9c9e31b75
- source: deepspeedai-deepspeed
  path: accelerator/real_accelerator.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 0f38b4a2ec94aa013b8238d2bced80e20f4f26005df8fab08e34575c9a9acc6c
- source: deepspeedai-deepspeed
  path: op_builder/builder.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: c9187f68fb91e42a9774a7e4a5c23303bdee1e42e3e90497cf619eb7a19f1e9e
- source: deepspeedai-deepspeed
  path: deepspeed/launcher/runner.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 956d554ea5c9b142ab4bae47c8317cce11f7b23748e09849b7876072c66cf9a0
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/engine.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: cd28c8d864e789c07cbcb80c6275e885fd8f409d90497084e0376935fcb10204
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/config.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 982bc8974c4a70665f1450dd96f843454626eb95aeebe5887305ac6e48548743
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage_1_and_2.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 0dd8a8c856a90e2aa0dae70d8d03f961d1b346800fdcabbf8e29ed149aec8bd8
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/stage3.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 64f3afdbacb757b0d8c0a9c08a4b6b6958b0bcbf597fd2eebd5a5c47821701cd
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/zero/partitioned_param_coordinator.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: a43fd966c88dc3699f5b18e2bfe51fac222e79365664addce9ed485d617a78d0
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/pipe/engine.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 74fe2ff16f84ad51ac3f85be5a85938c9fa482c076df29f4edb22e7d24be7cc8
- source: deepspeedai-deepspeed
  path: deepspeed/runtime/pipe/schedule.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 52aae5310aa18183d093149dd12cb20b02e6a8143e906bd32cf4fcdb96542a6b
- source: deepspeedai-deepspeed
  path: docs/_tutorials/advanced-install.md
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: e930e94bd72c37c14613e76fc5bdc09c6f3d72543e69dfe4eb2c119196e708e0
- source: deepspeedai-deepspeed
  path: docs/_tutorials/getting-started.md
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: c5df6860cecad9a8f1840e921ea460570d5c37bd140d39542760bc9d4e1bad01
- source: deepspeedai-deepspeed
  path: docs/_tutorials/universal-checkpointing.md
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 61d4c532cc607d6d9283d36ffa83ea35da606ff4de9d7a9bc59625a88c5fe0ce
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_config.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 3e240d16f1581bc1e8db115f211bcfb2f395d58e39b0a43ef7fa3e6c4bfb8545
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_stale_handle_wait.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 76b5a3cbeda906e00e3565c00fb2a0b5026d8dee43550f1af1f4acd453326565
- source: deepspeedai-deepspeed
  path: tests/unit/runtime/zero/test_zero_shared_loss_gradient.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 176f5b6bc78164896e65077b8fea71661b2c1d8b076ff2563962aa32506c8c20
- source: deepspeedai-deepspeed
  path: accelerator/cuda_accelerator.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: c5a48eb38f24922cd7e0cb7dc46ed1fb240151db99200e46f019603a83bfca83
- source: deepspeedai-deepspeed
  path: op_builder/__init__.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 1c9d345354ab8625c37ed4c8abd939859a7e0ae44f6791963b241eaea802db55
- source: deepspeedai-deepspeed
  path: op_builder/cpu/__init__.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 2b3440e0715bd58e1411081168d26b5ff546a169e13734fdc438668083f90d44
- source: deepspeedai-deepspeed
  path: deepspeed/ops/adam/cpu_adam.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 634fc0da21d455e20c187a9eb7f9668de961764e433c2d5da8f0da285282ffac
- source: deepspeedai-deepspeed
  path: deepspeed/sequence/cross_entropy.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: f923a14fa1910efe4f18776faaf87c355d18d9791387bdacc75ceb4ac9af2fee
- source: deepspeedai-deepspeed
  path: deepspeed/sequence/linear_cross_entropy.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 1d5ec07ea8d1b6a62a8b4083fa19419ae1d45da8389a644e656e10574ac16087
- source: deepspeedai-deepspeed
  path: deepspeed/sequence/vocab_parallel_ops.py
  commit: d8241a9ba266405e1a58fadf19e24b2370f6d7fa
  sha256: 6e1dd4cfb9d6442a238d026f9f01f16407cb830b8082351d4843ce18a6f3d749
---

# DeepSpeed：训练引擎、ZeRO、流水线与恢复工程指南

## 1. 定位与使用边界

DeepSpeed 接管模型训练的梯度累积、优化器、分布式状态和部分执行调度，既是其他引擎的后端，也是可以直接集成的训练引擎。它通常不替调用方决定 tokenizer、模型结构、样本 mask 或任务 loss。训练入口成功并不代表模型配方正确。

2026-11-04 复核官方 master 固定 `d8241a9ba266405e1a58fadf19e24b2370f6d7fa`，HCU 执行时仍以已验证的 HCU 分支、Torch/DTK 和扩展为准。CUDA Accelerator 这个类名不等于硬件只能是 NVIDIA，也不构成 HCU 支持承诺；确认实际 `get_accelerator()`、`torch.version.hip`、编译产物和加载路径。官方源码用于比较机制与版本差异。

## 2. 工程目录和问题入口

| 目录或文件 | 职责与阅读方向 |
| --- | --- |
| [`deepspeed/__init__.py`](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/deepspeed/__init__.py) | `initialize` 组装 engine、optimizer、dataloader、scheduler；区分普通模型与 `PipelineModule` |
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

[安装教程](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/docs/_tutorials/advanced-install.md)区分安装时预编译和首次使用时 JIT。官方最小源码安装可用 `python -m pip install .`；需要预编译时先装匹配 Torch，再只开启所需 `DS_BUILD_*`。`DS_BUILD_OPS=1` 是尝试所有兼容 op，不能把它当成 HCU 上全部可用的保证。

`ds_report` / `python -m deepspeed.env_report` 检查环境、兼容和已装 op；继续执行任务真正使用的 optimizer/attention op。只看报告不等于通过运行测试。JIT 缓存通过 `TORCH_EXTENSIONS_DIR` 置于本任务映射目录，并按 Python、Torch、DTK/编译器、gfx 分隔，避免别的环境留下的二进制误加载。

[`op_builder/builder.py`](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/op_builder/builder.py)负责兼容检查、构建/加载和 ROCm 检测；[`accelerator/real_accelerator.py`](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/accelerator/real_accelerator.py)负责 accelerator 选择。官方 `DS_ACCELERATOR` 可选值里没有 `hcu`，不要凭硬件名称发明环境变量值。HCU 仓库若增加或替换设备路径，联查 HCU-Knowledge 和该分支源码。

当前 import 路径将 Triton、Muon 和部分 compiler/op builder 探测延后到首次使用，不能用 `import deepspeed` 的耗时或成功替代实际 op 验收。`HAS_TRITON` 是懒读取属性，ROCm 路径仍明确返回 False，范围是未经 ROCm 验证的 DeepSpeed Triton inference kernels，不表示 ROCm/HCU 的 Triton 编译器本身不可用。新增 klxpu accelerator 的自动探测也不提供 `DS_ACCELERATOR=hcu`；记录最终选中的对象与加载模块。

CPUAdam/CPUAdagrad/CPULion 的 builder 已集中到 `op_builder/cpu/`。CUDA accelerator 的 class table 仍显式映射这些公开 builder 名称，CPU optimizer 继续从 `deepspeed.ops.op_builder` 取得 builder 后真实 `load()`；旧顶层源码路径的删除不表示 ZeRO CPU offload 被移除。CPUAdam 构建/装载失败会显式抛出 RuntimeError，应检查实际编译和模块路径，不能用 `import deepspeed` 成功代替这一步。

当前 CPU builder 对 RISC-V 架构名做大小写/下划线归一，并只在明确V版本或kernel HWCAP证明时启用 RVV；裸ISA字母v不够，避免把draft V当V1.0。这是CPU编译分支，不改变HCU gfx/设备扩展门禁。CUDA accelerator的具名NVTX域改走顶层 `nvtx.push_range/pop_range`，也不等于HCU已有相同profiler事件。

## 4. 运行与分层验收

[Getting Started](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/docs/_tutorials/getting-started.md)给出 `deepspeed.initialize` 和 launcher/JSON 配置。普通 engine 的基本循环是 `loss = engine(batch)`、`engine.backward(loss)`、`engine.step()`；engine 内部处理 accumulation boundary，调用方不能再次独立 `optimizer.step()` 或重复缩放 loss。Pipeline 模型使用自己的 `engine.train_batch(data_iter=...)`，见专题。

保留解析后的 JSON、调用方模型脚本、启动环境、实际 engine/optimizer 类。核对

`global batch = per-device micro batch × gradient accumulation × DP world size`。

这里的 DP 不是混合并行的总 world size。不要为了通过 assert 随意改变序列长度、模型维度或有效样本数量。初测依次验证扩展装载 → 单步 forward/backward/step → 所选 ZeRO/PP 的多 rank → 保存恢复并继续一步；吞吐测量剔除编译/初始化，记录有效 token 而不仅是 padding token。

## 5. 模型、数据与数值契约

DeepSpeed 接收调用方产生的 loss；label shift、ignore mask、token/sample 加权、MoE router 辅助 loss 的定义在调用方。`initialize` 返回组合对象并不验证这些语义。FP16 的 loss scaling、BF16 梯度累积、FP32 master/state 和 clip/norm 配置分别记录；共享图、多 engine 或 reentrant checkpoint 场景还需核对每条 backward 分支只缩放一次。

[`test_zero_shared_loss_gradient.py`](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/tests/unit/runtime/zero/test_zero_shared_loss_gradient.py)用手工参考梯度检查 engine/module 共享 loss、两个 engine 管理的 backward、reentrant checkpoint 等路径，是比单纯观察训练 loss 更直接的局部回归入口。它不替代模型阶段 loss 验证。

AutoTP 的词表切分是需要另查的 loss 所有权边界：当前 HF `tp_plan` 含 `embedding_rowwise` 且 embedding 与输出 head tied 时，`vocab_parallel_lm_head=None` 也可能自动启用 no-gather head；显式关闭、兼容性检查或 DeepCompile 限制会改变选择。`finalize_autotp` 发现 `VocabParallelLinear` 后通过 `configure_vocab_parallel_loss` 替换模型 `loss_function`。因此应检查最终 head、输出是否仍为完整词表，以及实际 loss hook，不能假定初始化前后只是参数被切片。

安装的 `VocabParallelCausalLMLoss` 在未给 `shift_labels` 时完成 causal shift；按实际 TP shard 固定缓存词表元数据，不可跨 teacher/student 或变更 shard 复用同一实例。Ulysses engine 已按有效 token 计数聚合时，该 loss 的 `sp_group` 保持 None，避免再归约一次。Liger backend 还要求真实 TP group、等宽词表分片和支持 Triton 的 accelerator等条件；这些分发条件不满足会走 Torch，条件满足但缺 Liger 包则显式报 ImportError。其 kernel 只支持一次一阶 backward，retained graph/高阶梯度需用 Torch 路径；未因包可导入而获得 HCU 资格。

`vocab_parallel_ce_backend='fused_linear'` 现在已接入 AutoTP causal-loss hook：训练forward带labels时，head捕获hidden并返回词表维为0的占位logits，安装的loss完成shift并调用 `vocab_parallel_linear_cross_entropy`；eval或不带labels时仍返回普通rank-local logits。调用方自己从 `outputs.logits` 计算loss会违背这条合同。底层独立hidden/weight/target API仍不替调用方shift；其forward在GEMM前压缩ignore targets、默认chunk至少256行（不超过实际有效行数），backward按词表块重算，省去完整logits但保留hidden/head-grad和临时GEMM。

Engine显式拒绝 fused_linear+ZeRO-3（head forward结束后权重已释放）及DeepCompile autotp pass；softcap或非单位logit scale也会拒绝，不能靠空logits旁路这些变换。AutoTP初始化时冻结的replicated参数若后来unfreeze，当前backward prologue会失败，要求在initialize前决定requires_grad，避免缺TP归约后各rank漂移。

vocabulary-parallel logprob/entropy/KL 仍返回逐token结果，mask和目标归约归调用方；当前按 `HAS_TRITON && is_triton_supported && on_accelerator` 分发融合Triton，否则使用有界行块eager。全-inf分布返回NaN而梯度置零等边界不能靠选择新kernel改变；源码分发和上游性能注释不构成HCU正确性/收益证据。

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

保存和加载属于分布式操作，参与 rank 必须遵守 engine 格式和相同调用顺序。ZeRO-3 保存后的完整权重导出、分片 checkpoint 续训与 Universal 转换是三件事。`elastic_checkpoint` 的旧 ZeRO-3 功能已弃用；不能凭名称推断可随意换拓扑。[Universal 教程](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/docs/_tutorials/universal-checkpointing.md)说明受支持模型布局和 AutoTP/AutoEP 元数据的转换约束。

当前 `Engine.load_checkpoint` 将 `load_from_fp32_weights` 配置标为弃用并忽略：完整ZeRO加载即使 `load_optimizer_states=False` 仍恢复保存的FP32 master，只重置optimizer状态；缺失分片直接报错。`load_module_only=True` 在ZeRO-1/2从模型重建master（Universal先从FP32读模型），ZeRO-3仍读FP32。NVMe关闭optimizer恢复时只拷FP32 swap文件，不再整目录复制旧moments。普通native checkpoint改变DP数仅允许 **elastic ZeRO-1/2的FP32权重且不载optimizer**，其余使用受支持Universal转换；详见[恢复专题](../topics/pipeline-schedule-and-checkpoint.md)。

观测也要使用同版定义：engine wall-clock snapshots/monitor及Pipeline吞吐现在调用 `elapsed_total`，而非旧 `elapsed`。记录timer scope和累计窗口再比历史日志；`deterministic_mode` 会在初始化调用determinism配置，不代表所有collective/kernel已经逐位可复现。

## 9. Release、PR、继续搜索和更新

[官方教程](https://www.deepspeed.ai/tutorials/) · [文档](https://deepspeed.readthedocs.io/en/latest/) · [Releases](https://github.com/deepspeedai/DeepSpeed/releases) · [开放/已合并 PR](https://github.com/deepspeedai/DeepSpeed/pulls)。固定源码完整目录见[source map](../../upstream/source-map/deepspeedai-deepspeed.md)，教程原文见[本地来源](../../upstream/docs/deepspeedai-deepspeed)。这些入口不表示所有历史特性均已精读，也未在本轮确认一份统一长期 roadmap。

现有 [PR #8534：弃用 LoCo ZeRO++](../../upstream/prs/deepspeedai--DeepSpeed/PR-8534.md) 和 [PR #8632：offload 梯度存储/stream 修复](../../upstream/prs/deepspeedai--DeepSpeed/PR-8632.md)应与当前实现一起读。尚未收录的问题用 `wiki-search-pr "offload gradient storage" --engine deepspeed`，再取 PR 正文、review、最终 diff 与 `wiki-code` 固定源码。

更新配置、coordinator、precision/backward 或 checkpoint 时，同时复核总览、两专题、相关案例及调用方（Swift/LlamaFactory 等）。分别登记源码合入、发布版本、HCU 适配和任务实测。本轮是固定源码/官方测试阅读，没有执行 HCU 分布式测试；结论不覆盖全部 op、所有混合并行或历史模型配方。


## 本轮补充固定证据


- [accelerator/cuda_accelerator.py](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/accelerator/cuda_accelerator.py)
- [op_builder/__init__.py](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/op_builder/__init__.py)
- [op_builder/cpu/__init__.py](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/op_builder/cpu/__init__.py)
- [deepspeed/ops/adam/cpu_adam.py](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/deepspeed/ops/adam/cpu_adam.py)
- [deepspeed/sequence/cross_entropy.py](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/deepspeed/sequence/cross_entropy.py)
- [deepspeed/sequence/linear_cross_entropy.py](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/deepspeed/sequence/linear_cross_entropy.py)
- [deepspeed/sequence/vocab_parallel_ops.py](https://github.com/deepspeedai/DeepSpeed/blob/d8241a9ba266405e1a58fadf19e24b2370f6d7fa/deepspeed/sequence/vocab_parallel_ops.py)
