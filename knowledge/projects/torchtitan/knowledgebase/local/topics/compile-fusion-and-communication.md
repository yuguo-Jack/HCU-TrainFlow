---
id: official-torchtitan-wiki/compile-fusion-and-communication
title: TorchTitan 局部编译、融合、异步 TP 与 GraphTrainer
engine: torchtitan
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-11-04'
retrieved_on: '2026-11-04'
coverage: Curated source chains and official evidence at a fixed main commit; not all models, backends
  or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/config/OVERRIDE.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: ea807062ffbc1e4267bff8c91730aca37a454091b16b25ada20adc07d784bf22
- source: pytorch-torchtitan
  path: torchtitan/config/transform/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 605a14077539325cb66eb17f52939bd35ed2d97e78f80fa547d6aec1cb53b78a
- source: pytorch-torchtitan
  path: torchtitan/models/common/linear/async_linear.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 9ea047214c1b0991e9dac6183b95f26b6e18bd2d3796761ab7472a429b02aa93
- source: pytorch-torchtitan
  path: torchtitan/config/transform/async_tensor_parallel.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: de2728f836c2dd7285c41f7870abf891ba43878b87fb3beb477f778146b22981
- source: pytorch-torchtitan
  path: torchtitan/distributed/accelerator_graph.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: dec500ca70df82c8c8388b41e49970cd9dbbdd2a1c287217c4783827b576e9d5
- source: pytorch-torchtitan
  path: torchtitan/experiments/graph_trainer/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 07a1d1b4186e5da6b36aee368898fdbb9c05a430c8446d9987402838be5af5bb
- source: pytorch-torchtitan
  path: torchtitan/distributed/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: c04da512eb9e4a9159e3f3751b9e1074239aa13906d3d67b9d9be632c3b61b59
- source: pytorch-torchtitan
  path: torchtitan_recipes/overrides/kimi_attention_residual.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 3782d82d0a72504e572969d3cdf3310dae6b29949910f131d7a9c4cda1a2ea3a
- source: pytorch-torchtitan
  path: torchtitan/components/validator.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 1a00109d1d0d95438d872d9606f0721bb70e58f638773bbd9f0f7d442b221d94
- source: pytorch-torchtitan
  path: torchtitan/config/configs.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 3465866709813651cc91114c4a006a5cc3c05d6069e9f04200e68d10c91c3659
- source: pytorch-torchtitan
  path: torchtitan/distributed/utils.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 11910a1dcf3c54cec3896998e21222ae4c3053901fdaf6d89670dd722108da7f
- source: pytorch-torchtitan
  path: tests/unit_tests/cpu/distributed/test_ulysses_nccl.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 15560eecdd367a339531a56f23cf408c551fe22ef1305f00db826ad1820d061b
- source: pytorch-torchtitan
  path: tests/unit_tests/cpu/distributed/test_accelerator_graph.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: c82151d5510605ef66fc54d9e495b6f21d07835a012a596643c6e407130a0311
- source: pytorch-torchtitan
  path: tests/unit_tests/cpu/config/test_accelerator_graph_validation_config.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 7d977863b969fd7aa978e8547254a0d2801efdb8a04d1888f6eab144032a265f
- source: pytorch-torchtitan
  path: tests/unit_tests/gpu/distributed/test_accelerator_graph_group_replay.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 51e4321f5da4c13c9eed6e4f4eeb0c0dac62908baceb8f229a52f2fe737fcfaa
- source: pytorch-torchtitan
  path: tests/unit_tests/gpu/distributed/test_accelerator_graph_train_eval.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 54b93fbd526c7f233c020a4f033cb203fd6bbc338eb2b6595f177998fa2ab086
- source: pytorch-torchtitan
  path: tests/unit_tests/cpu/test_trainer.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: b9681edfc274190ede7dcbba70a8bc82b814b51d4facf3618feb3c6961e0891d
- source: pytorch-torchtitan
  path: torchtitan/distributed/fsdp.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: ae80b4bd15521159e1041142726e9717c3d952399b273889e5fca11caa221e81
- source: pytorch-torchtitan
  path: torchtitan/distributed/ACCELERATOR_GRAPH.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 1b0f90f324a3338082f6001ee88ffccc31c35dfc9626cb2bde59557f514c98ea
- source: pytorch-torchtitan
  path: torchtitan/distributed/local_compile.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 258d7980f3a28c310d0fb1a31319c4124677de921de573d6fd22878879a96f93
- source: pytorch-torchtitan
  path: torchtitan/training_engine.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 2ffe06874d3a03ccc91d407f1bc91d5f2beaa9c746738dd3a3646f1c800a798f
- source: pytorch-torchtitan
  path: torchtitan/distributed/pipeline_parallel.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 21f503def70b1cb570be163729cacd4fd6c0ccb27d376c4ed1c15323495cb5bb

pr_sources:
- pr-pytorch--torchtitan-5033
- pr-pytorch--torchtitan-5250
- pr-pytorch--torchtitan-5263
---
# TorchTitan 局部编译、融合、异步 TP 与 GraphTrainer

## 先确认实际执行路径

区分普通 eager、模型标记的 local compile region、显式 kernel override、GraphTrainer 的图编译，以及 CUDA graph capture/replay。它们解决的问题、精度影响和依赖不同，不能笼统记录为“开启 compile”。普通 Trainer 的当前 local compile 不能照搬旧版 per-block 全模型编译教程；以模型声明的 region 和所选 recipe 为准。

用 profiler 确认 host 调度、launch 间隙、kernel 数量、graph breaks、编译次数和重编；对低收益、已经充分利用硬件的路径不重复编译实验。修改前保存有效配置及稳定基线。

## 可复用的优化选择

| 现象 | 候选方法 | 必须同时确认 |
| --- | --- | --- |
| 大量点算子/小 kernel、launch 或中间张量开销 | local compile 或已有融合 override | 前后向数值、生成代码、保存张量和端到端收益 |
| TP GEMM 与通信串行、尺寸足够 | AsyncTensorParallelTransform / Async Linear | 对称显存与后端能力、布局、真正 overlap、额外暂存 |
| PP/FSDP 参数通信暴露 | 调整预取/驻留/schedule | headroom、依赖、collective 次数、rank 不均衡 |
| MoE dispatch/combine 占比高 | 可用 dispatcher、负载平衡、通信计算交错 | token 分布、路由精度、scratch、重算与同步位置 |
| Host launch 成本高且形状稳定 | graph capture 或图编译 | 支持检测、输入状态、梯度 buffer、动态形状与内存池 |

## Async TP：计算/通信融合不是一个环境变量

`AsyncAllGatherLinear` 将 all-gather 与 matmul 对接，`AsyncLinearReduceScatter` 将 matmul 与 reduce-scatter 对接。其 backward、输入保存与布局转换共同决定内存流量；例如按 K shard 保存输入，可以避免保留完整 gathered 输入的倍增开销。应检查实际调用的 fused collective op 和 symmetric-memory 实现，不仅看模块名字。

该路径与原地 WGRAD 不完全兼容；当前转换显式关闭相应 flag，不能把两个开关都开就假定收益相加。前向/反向分别提取 local shape 和通信字节，比较隔离测试与模型内表现，按关键路径收益决定是否使用。

官方 README 中针对 CUDA 的连接数建议不是 HCU 默认参数。HCU 上的 `GPU_MAX_HW_QUEUES`、RCCL/网络/stream 配置需通过 HCU-Knowledge 和实际 runtime 源码确认，再有控制地测量；不能机械翻译 NVIDIA 环境变量。

## CUDA graph 与梯度状态

当前 `accelerator_graphs_supported()` 在 CUDA device 路径显式拒绝 `torch.version.hip is not None`，ROCm 路径返回 False；非 CUDA 路径还探测 `torch.accelerator.Graph()` 是否可用。对 HCU 必须检查实际分发；不能因配置写了 cuda_graph 就说已捕获执行，也不能把取消这个判断当作完整移植。

捕获后的 replay 不会重新执行 Python 中给 `param.grad` 赋值的逻辑。若捕获后 `zero_grad(set_to_none=True)` 清掉引用，replay 的写入 buffer 仍在，但 optimizer 可能看到 None；无条件 `set_to_none=False` 又可能改变内存成本。应理解 wrapper 对 capture 创建梯度、复用 buffer 和 zero_grad 的生命周期处理，并验证实际参数确实更新。

## GraphTrainer 是独立实验路径

GraphTrainer 捕获/变换前后向图，具有自己的 compiler pass、内存策略、数值变化开关、GraphPP 与 EP overlap 路线。`numerics_changing_optim` 不能当作免费提速；应先明确改变了什么归约或算子实现，做局部和阶段精度验证。

GraphPP 可以构造 stage-local 前后向、FSDP unshard/reduce、分离 dI/dW 和部分交错图；当前 README 仍明确不加载precompile artifacts，EP-overlap注释与GraphPP的组合还有限制。graph级CUDA-graph/annotation passes已移出内建pass pipeline，custom caller可显式调用 `construct_cuda_graph_passes`；默认由client包住完整前后向捕获，不应继续靠禁用旧 `cuda_graph_pass` 名字控制默认行为。普通Trainer与GraphTrainer的支持分别核对。

## LocalCompileConfig 与 capture 的可见副作用

`model.local_compile: LocalCompileConfig` 通过 `.apply()` 绑定 `regions`，未知区域直接报错；命名区域强制 `fullgraph=True`，batch-invariant 模式拒绝不兼容区域。`_compile` 默认走 Torch Inductor，也允许外部子类覆盖。空 regions 关闭选定命名区域，但 always-compiled helpers 仍会重新绑定，不能将空列表当作全进程完全 eager。

训练/optimizer wrapper 的 warmup 是真实调用，默认两次；eval warmup 默认一次完整验证并保留 RNG/buffer 更新。capture 记录后立即 replay 一次才完成该调用，不应再重复 update。Graph 输出由共享 pool 持有，下一次 replay/其他共享图可能覆盖；需要长期保存的调用方应复制。结构化 args/kwargs 与 BlockMask 元数据、tensor metadata 和梯度参与集必须符合固定输入规范。调试阶段对齐验证调度/RNG和实际参数更新，不能仅比较裸 replay 时长。

## 与 TrainFlow 优化循环衔接

先按端到端关键路径决定 CPU bubble、通信或计算的优先级。计算热点累计覆盖目标工作量后，逐项建立 shape/dtype/bytes/FLOPs 与实测上限；能复用现有算子/通信库就复用，缺失部分在合适库内实现。需要初始融合基线时衔接 baseline Skill，再进入 Triton/HIP 优化 Skill；算子提速必须回到模型验证。具体反例见 [Attention Residual](../cases/kimi-attnres-fusion.md)。

DeepEP deferred-epilogue overlap（PR #5263）于 2026-11-04 官方 API 核对仍 open，head `d5e59c25e0900889fe19c2c3c7120273719c4373`、base `448b9c8be41abc7fcbd5ccc768242b8865d4347b`。当前主干已有 ElasticBuffer 机制，候选则要求 DeepEP v2.5 EPBuffer，把 shared experts 放到 dispatch launch 与 counts materialize 之间；默认关闭，Kimi 自定义 MoE/Dist-MoE 拒绝。它不消除 CPU counts 等待或使 compact training Graph 可用，不能由“使用 v2”推导已合入、通用提速或 HCU 验证。

## 共享 Graph pool、逐组 replay 与 PP 输入链

当前 `accelerator_graph_manager` 统一持有pool、capture stream和wrappers。启用eval capture时，先将训练/optimizer capture gate关闭，允许eager warmup；eval先捕获后再开放其他wrapper。即使尚未到常规validation周期也可能有额外warmup/eval，短跑耗时不能直接视为稳态。捕获前的 `prepare_for_capture` 在图外准备可能CPU同步的PP metadata；FSDP grouped eval结束需清理pending forwards并reshard，避免norm/lm_head共享group把权重或状态留在pool之外。关闭资源先等待checkpoint/Dist-MoE，再teardown graphs。

`accelerator_graph_per_microbatch_group` 捕获一个均匀group，不能与defer-FSDP-gradient-reduction共用。各replay分别归约/reshard，HSDP也每group执行replica all-reduce，区别于eager在最后group只归约一次；归约次数和舍入均可能变化。它要求相同输入结构、metadata与梯度参与参数集合，不是任意动态batch Graph。

**旧结构缺口已修复，运行验证仍有范围**：当前 `prepare_for_capture` 解包四项（含 `loss_kwarg_mbs`），并把首个 microbatch 的 loss kwargs 与全局 token 分母合并后交给 PP metadata 初始化。CPU `test_engine_prepares_pp_metadata_before_accelerator_graph` 现覆盖真实四项结构、advantages 与分母。旧提交三项/四项不一致不再作为当前 blocker；这些源代码和模拟测试仍不能证明本轮未运行的 GPU/PP/HCU 组合通过。

## Ulysses 的特定通信修复门禁

`configure_nccl_for_ulysses` 在分布式初始化前检查模型类型、device/backend和NCCL版本：命中Ulysses、device_type="cuda"且非fake类通信后端、NCCL<2.32.3时将 `NCCL_GRAPH_REGISTER=0`，即使用户原来设1也会记录覆盖。fake/real_pp_fake_spmd等路径或修复后版本跳过。此为特定partial-IPC导入问题的修复，不是通用性能默认；HCU/RCCL兼容接口的版本报告和实现需另核，不能仅因变量名相近直接搬用。

## 固定证据与使用边界

本页以官方主线 `485c065cb248863bf2e2c65588becd6d7a8bcf83` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/config/OVERRIDE.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/OVERRIDE.md)
- [torchtitan/config/transform/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/transform/README.md)
- [torchtitan/models/common/linear/async_linear.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/common/linear/async_linear.py)
- [torchtitan/config/transform/async_tensor_parallel.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/transform/async_tensor_parallel.py)
- [torchtitan/distributed/accelerator_graph.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/accelerator_graph.py)
- [torchtitan/experiments/graph_trainer/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/experiments/graph_trainer/README.md)
- [torchtitan/distributed/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/README.md)
- [torchtitan_recipes/overrides/kimi_attention_residual.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan_recipes/overrides/kimi_attention_residual.py)

- [PR #5033：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5033.md)
- [PR #5250：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5250.md)
- [PR #5263：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5263.md)

## 本次补充的实现与测试依据

- [torchtitan/components/validator.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/components/validator.py)
- [torchtitan/config/configs.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/configs.py)
- [torchtitan/distributed/utils.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/utils.py)
- [tests/unit_tests/cpu/distributed/test_ulysses_nccl.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/unit_tests/cpu/distributed/test_ulysses_nccl.py)
- [tests/unit_tests/cpu/distributed/test_accelerator_graph.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/unit_tests/cpu/distributed/test_accelerator_graph.py)
- [tests/unit_tests/cpu/config/test_accelerator_graph_validation_config.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/unit_tests/cpu/config/test_accelerator_graph_validation_config.py)
- [tests/unit_tests/gpu/distributed/test_accelerator_graph_group_replay.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/unit_tests/gpu/distributed/test_accelerator_graph_group_replay.py)
- [tests/unit_tests/gpu/distributed/test_accelerator_graph_train_eval.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/unit_tests/gpu/distributed/test_accelerator_graph_train_eval.py)
- [tests/unit_tests/cpu/test_trainer.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/unit_tests/cpu/test_trainer.py)
- [torchtitan/distributed/fsdp.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/fsdp.py)

- [torchtitan/distributed/ACCELERATOR_GRAPH.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/ACCELERATOR_GRAPH.md)

- [torchtitan/distributed/local_compile.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/local_compile.py)

- [torchtitan/training_engine.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/training_engine.py)

- [torchtitan/distributed/pipeline_parallel.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/pipeline_parallel.py)
