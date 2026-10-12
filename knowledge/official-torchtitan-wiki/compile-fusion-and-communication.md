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
reviewed_on: '2026-10-12'
coverage: Curated source chains and official evidence at a fixed main commit; not
  all models, backends or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/config/OVERRIDE.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: e300303059959a1d608c0aea248259fbf01a215021dc2a04f05f599dffd9d9d3
- source: pytorch-torchtitan
  path: torchtitan/config/transform/README.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: d24fa16f2b8cef0aed3a4f601d55ec88f5a22b44572c00c0e411d8933ed5bcef
- source: pytorch-torchtitan
  path: torchtitan/models/common/async_linear.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 7e4212aaa3a0ad55eeaa9f76e40199cf5ef1324cd1687bea267c8ab2898432ea
- source: pytorch-torchtitan
  path: torchtitan/config/transform/async_tensor_parallel.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: d8695578b569e0232d9f44d1bd6190851318ce7a2b1f1261c7868d2009003be0
- source: pytorch-torchtitan
  path: torchtitan/distributed/cuda_graph.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 54e3ae358d4f2b1a1dd95cb25b56af36cabca604881f0e2df65044d1e3f101d2
- source: pytorch-torchtitan
  path: torchtitan/experiments/graph_trainer/README.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: d10ff4000251b9ea00f8156e0c3387cfe481d56250d87b402d72251cb7ce6c28
- source: pytorch-torchtitan
  path: torchtitan/distributed/README.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 92cfc9a282f2afbd4975f8a769a854bd7fcce444f85011206835db414bc9cbe0
- source: pytorch-torchtitan
  path: torchtitan_recipes/overrides/kimi_attention_residual.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 3782d82d0a72504e572969d3cdf3310dae6b29949910f131d7a9c4cda1a2ea3a
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

`AsyncAllGatherLinear` 将 all-gather 与 matmul 对接，`AsyncReduceScatterLinear` 将 matmul 与 reduce-scatter 对接。其 backward、输入保存与布局转换共同决定内存流量；例如按 K shard 保存输入，可以避免保留完整 gathered 输入的倍增开销。应检查实际调用的 fused collective op 和 symmetric-memory 实现，不仅看模块名字。

该路径与原地 WGRAD 不完全兼容；当前转换显式关闭相应 flag，不能把两个开关都开就假定收益相加。前向/反向分别提取 local shape 和通信字节，比较隔离测试与模型内表现，按关键路径收益决定是否使用。

官方 README 中针对 CUDA 的连接数建议不是 HCU 默认参数。HCU 上的 `GPU_MAX_HW_QUEUES`、RCCL/网络/stream 配置需通过 HCU-Knowledge 和实际 runtime 源码确认，再有控制地测量；不能机械翻译 NVIDIA 环境变量。

## CUDA graph 与梯度状态

当前 `cuda_graphs_supported()` 明确要求 `torch.version.hip is None`，ROCm 路径返回 False。对 HCU 必须检查实际分发；不能因配置写了 cuda_graph 就说已捕获执行，也不能把取消这个判断当作完整移植。

捕获后的 replay 不会重新执行 Python 中给 `param.grad` 赋值的逻辑。若捕获后 `zero_grad(set_to_none=True)` 清掉引用，replay 的写入 buffer 仍在，但 optimizer 可能看到 None；无条件 `set_to_none=False` 又可能改变内存成本。应理解 wrapper 对 capture 创建梯度、复用 buffer 和 zero_grad 的生命周期处理，并验证实际参数确实更新。

## GraphTrainer 是独立实验路径

GraphTrainer 捕获/变换前后向图，具有自己的 compiler pass、内存策略、数值变化开关、GraphPP 与 EP overlap 路线。`numerics_changing_optim` 不能当作免费提速；应先明确改变了什么归约或算子实现，做局部和阶段精度验证。

GraphPP 可以构造 stage-local 前后向、FSDP unshard/reduce、分离 dI/dW 和部分交错图；当前 README 也明确 precompile artifact、CUDA graph steady-state 与 EP overlap 组合存在后续工作。普通 Trainer 的某项支持不能推导为 GraphTrainer 同样支持，反之亦然。

## 与 TrainFlow 优化循环衔接

先按端到端关键路径决定 CPU bubble、通信或计算的优先级。计算热点累计覆盖目标工作量后，逐项建立 shape/dtype/bytes/FLOPs 与实测上限；能复用现有算子/通信库就复用，缺失部分在合适库内实现。需要初始融合基线时衔接 baseline Skill，再进入 Triton/HIP 优化 Skill；算子提速必须回到模型验证。具体反例见 [Attention Residual](cases/kimi-attnres-fusion.md)。

尚未合入的 DeepEP deferred-epilogue overlap（PR #5263）保留为研究线索：依赖新版 API、仍有 CPU counts 等待、限定 MoE 路径，不能宣称已在当前主线普遍开启。

## 固定证据与使用边界

本页以官方主线 `65aaaa960698ab5d6e98c874177b41b9c30e9c58` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/config/OVERRIDE.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/config/OVERRIDE.md)
- [torchtitan/config/transform/README.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/config/transform/README.md)
- [torchtitan/models/common/async_linear.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/models/common/async_linear.py)
- [torchtitan/config/transform/async_tensor_parallel.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/config/transform/async_tensor_parallel.py)
- [torchtitan/distributed/cuda_graph.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/distributed/cuda_graph.py)
- [torchtitan/experiments/graph_trainer/README.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/experiments/graph_trainer/README.md)
- [torchtitan/distributed/README.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/distributed/README.md)
- [torchtitan_recipes/overrides/kimi_attention_residual.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan_recipes/overrides/kimi_attention_residual.py)

- [PR #5033：描述、review、评论及 diff](../prs/pytorch--torchtitan/PR-5033.md)
- [PR #5250：描述、review、评论及 diff](../prs/pytorch--torchtitan/PR-5250.md)
- [PR #5263：描述、review、评论及 diff](../prs/pytorch--torchtitan/PR-5263.md)
