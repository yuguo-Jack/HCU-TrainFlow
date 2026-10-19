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
reviewed_on: '2026-10-20'
coverage: Curated source chains and official evidence at a fixed main commit; not all models, backends
  or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/config/OVERRIDE.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 8bd415ea0af50c5b4f7ad407c22afeea9ca63c22c2c6139b89f11311f55c46b6
- source: pytorch-torchtitan
  path: torchtitan/config/transform/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 31ccfda7c1c338a215dc1221b34b5a850d3cf4b5b2d6317191fdf7d1768a54d3
- source: pytorch-torchtitan
  path: torchtitan/models/common/linear/async_linear.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 9ea047214c1b0991e9dac6183b95f26b6e18bd2d3796761ab7472a429b02aa93
- source: pytorch-torchtitan
  path: torchtitan/config/transform/async_tensor_parallel.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: de2728f836c2dd7285c41f7870abf891ba43878b87fb3beb477f778146b22981
- source: pytorch-torchtitan
  path: torchtitan/distributed/cuda_graph.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 29822760e2d35f6e816ae0b9655483b0ac366ff2a111bfc208bf6440e0b326b7
- source: pytorch-torchtitan
  path: torchtitan/experiments/graph_trainer/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: ac6e1d723cec7e2de987f504c26b7a24cae27c48a5bb9a6991e6b3ec4e3cd89d
- source: pytorch-torchtitan
  path: torchtitan/distributed/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 0f091154d9ad220ef32ad01b62d3ea1a422840689bc4b9f5d8200c62e83c3124
- source: pytorch-torchtitan
  path: torchtitan_recipes/overrides/kimi_attention_residual.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 3782d82d0a72504e572969d3cdf3310dae6b29949910f131d7a9c4cda1a2ea3a
- source: pytorch-torchtitan
  path: torchtitan/components/validator.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 27c768929bb3a4514a559b87fc6485228f26080925ceccd3e2725fc4fb43f8b6
- source: pytorch-torchtitan
  path: torchtitan/config/configs.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: aaf73beb7efb044ac1978b3edb43b48db256ccd708660880d947bc70e9be3a2c
- source: pytorch-torchtitan
  path: torchtitan/distributed/utils.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 980a95f17891bd4e294d07d38379d536811cf06894d624ad4c85a3f5a6328b93
- source: pytorch-torchtitan
  path: tests/unit_tests/cpu/distributed/test_ulysses_nccl.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: e7341599ca4b560261b8ccdd675f5f24bbbf114ad7391aea684baed1f1ebb9a2
- source: pytorch-torchtitan
  path: tests/unit_tests/cpu/distributed/test_cuda_graph.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 267c8ec14069fc267ad1a057068d5a93159dc77bd714084816a6904ba3376a02
- source: pytorch-torchtitan
  path: tests/unit_tests/cpu/config/test_cuda_graph_validation_config.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: d2057481c7cdb41456fdfb0dac6075f68d60983868d13ba0c16acf21996e3895
- source: pytorch-torchtitan
  path: tests/unit_tests/gpu/distributed/test_cuda_graph_group_replay.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: cc25d22175181694f5bb5082ecf4acb46192eba8551ab6eaa9151208e1c02812
- source: pytorch-torchtitan
  path: tests/unit_tests/gpu/distributed/test_cuda_graph_train_eval.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 5fb3a96180d8fd4ca6f9d3bdf6ac74204d80f2a9279a7e44e640e901074e6de3
- source: pytorch-torchtitan
  path: tests/unit_tests/cpu/test_trainer.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 1882d21356427492dcfc7c160f842e6f18fe813fa565066e8b420741139d9d6b
- source: pytorch-torchtitan
  path: torchtitan/distributed/fsdp.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 397ee700761af56345048cb0e7ba5b120bbc2b57a94e02aebb1c4c8499b8846a
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

当前 `cuda_graphs_supported()` 明确要求 `torch.version.hip is None`，ROCm 路径返回 False。对 HCU 必须检查实际分发；不能因配置写了 cuda_graph 就说已捕获执行，也不能把取消这个判断当作完整移植。

捕获后的 replay 不会重新执行 Python 中给 `param.grad` 赋值的逻辑。若捕获后 `zero_grad(set_to_none=True)` 清掉引用，replay 的写入 buffer 仍在，但 optimizer 可能看到 None；无条件 `set_to_none=False` 又可能改变内存成本。应理解 wrapper 对 capture 创建梯度、复用 buffer 和 zero_grad 的生命周期处理，并验证实际参数确实更新。

## GraphTrainer 是独立实验路径

GraphTrainer 捕获/变换前后向图，具有自己的 compiler pass、内存策略、数值变化开关、GraphPP 与 EP overlap 路线。`numerics_changing_optim` 不能当作免费提速；应先明确改变了什么归约或算子实现，做局部和阶段精度验证。

GraphPP 可以构造 stage-local 前后向、FSDP unshard/reduce、分离 dI/dW 和部分交错图；当前 README 仍明确不加载precompile artifacts，EP-overlap注释与GraphPP的组合还有限制。graph级CUDA-graph/annotation passes已移出内建pass pipeline，custom caller可显式调用 `construct_cuda_graph_passes`；默认由client包住完整前后向捕获，不应继续靠禁用旧 `cuda_graph_pass` 名字控制默认行为。普通Trainer与GraphTrainer的支持分别核对。

## 与 TrainFlow 优化循环衔接

先按端到端关键路径决定 CPU bubble、通信或计算的优先级。计算热点累计覆盖目标工作量后，逐项建立 shape/dtype/bytes/FLOPs 与实测上限；能复用现有算子/通信库就复用，缺失部分在合适库内实现。需要初始融合基线时衔接 baseline Skill，再进入 Triton/HIP 优化 Skill；算子提速必须回到模型验证。具体反例见 [Attention Residual](../cases/kimi-attnres-fusion.md)。

DeepEP deferred-epilogue overlap（PR #5263）于2026-10-20官方API复核仍open。当前主干已有ElasticBuffer机制，具体该PR的deferred overlap仍须按其固定head/base和实际调用者区分；不能由“使用v2”推导该候选已合入或CPU counts等待已经消失。

## 共享 Graph pool、逐组 replay 与 PP 输入链

当前 `cuda_graph_manager` 统一持有pool、capture stream和wrappers。启用eval capture时，先将训练/optimizer capture gate关闭，允许eager warmup；eval先捕获后再开放其他wrapper。即使尚未到常规validation周期也可能有额外warmup/eval，短跑耗时不能直接视为稳态。捕获前的 `prepare_for_capture` 在图外准备可能CPU同步的PP metadata；FSDP grouped eval结束需清理pending forwards并reshard，避免norm/lm_head共享group把权重或状态留在pool之外。关闭资源先等待checkpoint/Dist-MoE，再teardown graphs。

`cuda_graph_per_microbatch_group` 捕获一个均匀group，不能与defer-FSDP-gradient-reduction共用。各replay分别归约/reshard，HSDP也每group执行replica all-reduce，区别于eager在最后group只归约一次；归约次数和舍入均可能变化。它要求相同输入结构、metadata与梯度参与参数集合，不是任意动态batch Graph。

**固定提交的待解决结构问题**：`TrainingEngine._preprocess_microbatch_group` 的PP返回值已为四项（含 `loss_kwarg_mbs`），而 `_initialize_forward_backward` 内的 `prepare_for_capture` 仍解包三项。`test_engine_prepares_pp_metadata_before_cuda_graph` 也手造三项输入；GPU shared-pool PP测试直接包schedule，没有走完整engine预处理链。源码观察表明真实四项输入进入首次PP capture有解包失败风险；本轮未运行该组合。解决并补齐覆盖前，采用已验证的eager配置，不因旧PP+validation禁止已移除而宣布该链可用。

## Ulysses 的特定通信修复门禁

`configure_nccl_for_ulysses` 在分布式初始化前检查模型类型、device/backend和NCCL版本：命中Ulysses、device_type="cuda"且非fake类通信后端、NCCL<2.32.3时将 `NCCL_GRAPH_REGISTER=0`，即使用户原来设1也会记录覆盖。fake/real_pp_fake_spmd等路径或修复后版本跳过。此为特定partial-IPC导入问题的修复，不是通用性能默认；HCU/RCCL兼容接口的版本报告和实现需另核，不能仅因变量名相近直接搬用。

## 固定证据与使用边界

本页以官方主线 `a242475253433725f10f39c18f5ccbfdf188e097` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/config/OVERRIDE.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/config/OVERRIDE.md)
- [torchtitan/config/transform/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/config/transform/README.md)
- [torchtitan/models/common/linear/async_linear.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/models/common/linear/async_linear.py)
- [torchtitan/config/transform/async_tensor_parallel.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/config/transform/async_tensor_parallel.py)
- [torchtitan/distributed/cuda_graph.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/cuda_graph.py)
- [torchtitan/experiments/graph_trainer/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/experiments/graph_trainer/README.md)
- [torchtitan/distributed/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/README.md)
- [torchtitan_recipes/overrides/kimi_attention_residual.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan_recipes/overrides/kimi_attention_residual.py)

- [PR #5033：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5033.md)
- [PR #5250：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5250.md)
- [PR #5263：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5263.md)

## 本次补充的实现与测试依据

- [torchtitan/components/validator.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/components/validator.py)
- [torchtitan/config/configs.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/config/configs.py)
- [torchtitan/distributed/utils.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/utils.py)
- [tests/unit_tests/cpu/distributed/test_ulysses_nccl.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/unit_tests/cpu/distributed/test_ulysses_nccl.py)
- [tests/unit_tests/cpu/distributed/test_cuda_graph.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/unit_tests/cpu/distributed/test_cuda_graph.py)
- [tests/unit_tests/cpu/config/test_cuda_graph_validation_config.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/unit_tests/cpu/config/test_cuda_graph_validation_config.py)
- [tests/unit_tests/gpu/distributed/test_cuda_graph_group_replay.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/unit_tests/gpu/distributed/test_cuda_graph_group_replay.py)
- [tests/unit_tests/gpu/distributed/test_cuda_graph_train_eval.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/unit_tests/gpu/distributed/test_cuda_graph_train_eval.py)
- [tests/unit_tests/cpu/test_trainer.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/unit_tests/cpu/test_trainer.py)
- [torchtitan/distributed/fsdp.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/fsdp.py)
