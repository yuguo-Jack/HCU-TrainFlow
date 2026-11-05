---
id: official-torchtitan-wiki/moe-and-low-precision
title: TorchTitan MoE 路由、通信内存与低精度权重生命周期
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
  path: torchtitan/models/common/dist_moe/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 8a08b2adb05e081feaf3116b7acebe509a6e731d66d80f5e3f6333c5231673cf
- source: pytorch-torchtitan
  path: torchtitan/config/transform/dist_moe.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 5e773f089e1be7df5ad2d99b5342a7eed21981c196052902fe9ebe6c2d4e54b0
- source: pytorch-torchtitan
  path: torchtitan/config/transform/token_dispatcher.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: b98f1e2f7ac8a53d65be2dd5d232a3422a70e273e4404cd8907a58170fa158cd
- source: pytorch-torchtitan
  path: torchtitan/quantization/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: c83d0b237d478207891164a49972280f065b7bbd9026ad8fc91cf8aa91d587c9
- source: pytorch-torchtitan
  path: torchtitan/quantization/mxfp8/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 629ffa3730098c8b956e5da4e693e9ce4639fb9f9b544befd201427a0b69b9c7
- source: pytorch-torchtitan
  path: torchtitan/quantization/nvfp4/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 64d5f937a3bc2a280cb7249592fe31521c7dba37d364aa4870b9430f359b8680
- source: pytorch-torchtitan
  path: torchtitan/distributed/REMAT.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 6693c808dafbc202f526f366fe25dd60dc03453966230be810f6907f7b84cff0
- source: pytorch-torchtitan
  path: torchtitan/models/common/moe/moe.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: c2a09e0beffb5298917cf26d866371520c947f12f40ef7a52ddd157c15e5ecdf
- source: pytorch-torchtitan
  path: torchtitan/models/common/aux_loss.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 470459e21209b934f1181a8713d98ce9fc890e1abff7a67f39ff12323d812b97
- source: pytorch-torchtitan
  path: torchtitan/models/common/moe/token_dispatcher.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 1565face09bffc7246f1d9ddc1a1304fe814ade500605df2f66517fd8a270dfa
- source: pytorch-torchtitan
  path: torchtitan/config/transform/freeze_moe_routing.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 985eee889df806f156a8545a93baff4450c0fde0980786a6cdf7ecfcc4c1faa8
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_model_defaults.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 44bf357ff2ddfa185feca23384b2152168c25c0727dcc253f14616e36c6e2427
pr_sources:
- pr-pytorch--torchtitan-5263
- pr-pytorch--torchtitan-5250
---
# TorchTitan MoE 路由、通信内存与低精度权重生命周期

## 先看 MoE 的完整链路

模型 router 产生 expert 选择与权重，dispatcher 发送 token，routed experts 执行 grouped GEMM/激活，combine 恢复输出；shared experts 可能与部分通信交错。分别统计路由不均、dispatch/combine、GEMM、复制/重排和同步，不能把 MoE 全部时间归到 A2A 或 GEMM。

普通 dispatcher、DeepEP 和 Dist-MoE 的布局、scratch、保存激活、反向 replay 与拓扑要求不同。只有实际安装版本及目标硬件支持的路径才进入性能比较；先确认选择器生效，避免 silent fallback。

## Dist-MoE 的归属与硬件边界

TorchTitan 的 DistMoeTransform 保留模型 router 和参数命名/布局，替换 routed experts 并对接外部 `meta-pytorch/dist_moe`。外部路径组织 dispatch、grouped GEMM、激活、scratch 和 combine。所引用说明主要面向 CuTe DSL / SM100+ 的 BF16、异步 MXFP8；不是 HCU 开箱即用通信库。

参数如 w13 `[E,2,F,D]`、w2 `[E,D,F]` 的布局必须与 FSDP、checkpoint 和 optimizer 一致。`inplace_wgrad_accum` 与 eager/GraphTrainer 的兼容性不同，不能只保留数学公式而忽略状态接口。

## 容量不是“平均每卡 token 数”

路由局部 token 数 T、top-k K、EP degree P、每 rank 本地专家数 L 决定最坏接收量可能达到 `T × P × min(K,L)`；理想均衡值约为 `T × K`。实际容量策略必须考虑路由偏斜，不假定平均值就能覆盖峰值。

区分 symmetric communication buffers、设备 scratch、保存激活和可能的 pinned-host/VMM backing；`activation_slot_bytes` 与按 factor 推导的容量不能混设，PP 多微批的 slot 生命周期也影响峰值。此处 Dist-MoE routing factor 是容量假设，不等于自动均衡负载；必须核对所选后端的溢出合同。它不能与下述 HybridEP non-blocking factor 混用，后者在缩小容量后存在明确丢token行为。溢出、回退或重算都会改变性能与数值验收条件。

## MXFP8：量化和缓存由谁管理

官方说明面向 B200/SM100、匹配 TorchAO 与相应 kernel。activation 采用块尺度量化，dense weight 使用支持正反向方向复用的布局；不能用“FP8”概括 scale 粒度、转置方向和保存格式。

FSDP gather BF16 权重后，通过 post-all-gather hook 构造低精度 operand，再由 FSDP 管理释放和复用。`reshard_after_forward=False` 可以跨微批复用；True 会在 backward 再 gather/量化。这里不是任意 module 自建一个永不过期的 weight cache。性能建模要包括量化、scale、重排和重复 gather；checkpoint 仍需明确其高精度状态。

WGRAD 可保存高精度 activation 到 backward 再量化，或保存特定方向的低精度 operand；forward 的因果 token 边界和 backward 的缩放是不同问题。任何融合都需核对 scale 是否跨本不应相互依赖的 token。

## NVFP4：实验状态和回退

NVFP4 依赖 TorchAO prototype 与 Blackwell/CUDA；当前说明要求切分后的 local GEMM 维度满足 kernel 对齐条件，混合 recipe 保留部分敏感层/LM head 为 BF16。官方 CI 和论文试验覆盖有限，不能据此宣称任意模型长训等价。

论文中的“只把 Fprop 切回 BF16，Dgrad/Wgrad 继续 FP4”与当前 TorchTitan 集成的实际能力不同：当前说明不支持这种独立切换。可用的完整 BF16 收尾要从包含模型、优化器、scheduler、data/step 的 checkpoint 接续，并保持训练计划。低精度模型文件可读，不等于恢复了训练状态。

## HCU 借鉴方法

迁移的是路由/状态/布局/复用机制；实际 kernel、通信后端和硬件格式需要寻找 HCU 已有实现。按真实 profile 决定是否优化路由、负载、通信 overlap、通算融合或 grouped GEMM。数学库不达预期时提交实际 rocBLAS/hipBLASLt bench 日志与复现环境，不用抽象模型 shape 代替可 tune 命令。保持与 [TrainFlow 算子流程](../../../../../../docs/practices/performance-methods.md) 一致。

## 当前 dispatcher 与 RL 默认的区别

实现目录已迁到 `models/common/moe/`；`DeepEPTokenDispatcher` 当前使用DeepEP≥2.0的ElasticBuffer。寿命上限 `num_max_tokens_per_rank` 用来预分配，当前输入token数另传；通信remat要求deterministic buffer与相同接收顺序。当前combine在返回前 `sync_combine()`，有v2 API不证明所有等待均已消除。`cuda_graph_compatible=True` 的expand形式仅适用于no_grad生成，训练仍落compact；普通训练Graph支持不能由这个flag推导。

HybridEP 的 `non_blocking_capacity_factor=None` 是有host同步的精确容量、不丢token路线；1.0按当前最坏容量分配，较小正值会使超出permute容量的token被丢弃，GPU overflow_flag可置位。该factor不调整独立预分配的A2A通信buffer。使用非阻塞以满足捕获限制时，必须观测overflow并验证质量，不能因不再发生CPU等待就宣称等价。

RL的 `build_rl_model_configs` 新默认同时作用于trainer和generator：FP32-output LM head，以及冻结MoE router gate、expert bias和移除load-balancing aux loss。`freeze_moe_routing=False` 才保留原router训练；freeze不保证hidden states变化后专家选择不变。此处是RL配方的训练语义，不能传播为预训练的默认或用来掩盖数值不一致；SoftCappedLinear等配方保留明确例外。

## Dispatcher 输入与重算消费者的迁移

当前 dispatcher 接收 bool `routing_map_TE(T,E)`；local/A2A 路径在内部求专家 token counts，DeepEP/HybridEP 则使用各自返回的全局路由量。EP process group 从当前 sparse SPMD mesh 获取，不再依赖旧实例 `ep_mesh`。不能把旧计数 tensor 作为同位置实参传入新接口。

DeepEP/HybridEP 的 dispatch 与 combine 共用 `ep_communication` remat policy，forward handle 与 backward 相配；DeepEP 依赖确定性排序 buffer，HybridEP 依赖保持顺序的 prefix scans。保存/重放选择影响通信次数与生命周期，需连同量化 padding、score dtype、gradients 和专家顺序验证。Dist-MoE 仍要求根 `precision.param_dtype="bfloat16"`；源码中的 backend/硬件限制不会因字段迁移而消失。

## 固定证据与使用边界

本页以官方主线 `485c065cb248863bf2e2c65588becd6d7a8bcf83` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/models/common/dist_moe/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/common/dist_moe/README.md)
- [torchtitan/config/transform/dist_moe.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/transform/dist_moe.py)
- [torchtitan/config/transform/token_dispatcher.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/transform/token_dispatcher.py)
- [torchtitan/quantization/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/quantization/README.md)
- [torchtitan/quantization/mxfp8/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/quantization/mxfp8/README.md)
- [torchtitan/quantization/nvfp4/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/quantization/nvfp4/README.md)
- [torchtitan/distributed/REMAT.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/REMAT.md)

- [PR #5263：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5263.md)
- [PR #5250：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5250.md)

## 当前主线补充：global batch 辅助 loss 与重算副作用

[PR #4772](https://github.com/pytorch/torchtitan/pull/4772) 增加 global batch-wise MoE 辅助 loss。`moe.py` 中 batch-wise 实现跨 DP 和 token-sharding 轴汇总 expert counts，normalized-score 的规约范围不同：DP 的可微贡献仍会由梯度规约组合，不能将两条路径都无区别 all-reduce。

滚动 counts 在各 microbatch 前向累积，保留该次前向的快照，防止后续 microbatch 已运行后 checkpoint replay 读取新的统计。`aux_loss.py` 使用 retained `torch_remat` region，避免重算重复计数/重复通信；optimizer pre-hook 负责 step 边界的累积与清零，metric 再按其 reduce_mesh 和层数归并。

调整 gradient accumulation、PP、CP/EP 或重算时，需要同时核对 routed-token 分母、aux coefficient、主 loss 和梯度，不把统计口径变化当性能回归或收敛改善。global-batch、microbatch-wise 与 aux-loss-free bias 更新是不同机制；模型配方选哪条就验证哪条，不能随意替换。

- [torchtitan/models/common/moe/moe.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/common/moe/moe.py)
- [torchtitan/models/common/aux_loss.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/common/aux_loss.py)

## 本次补充的实现与测试依据

- [torchtitan/models/common/moe/token_dispatcher.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/common/moe/token_dispatcher.py)
- [torchtitan/config/transform/freeze_moe_routing.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/transform/freeze_moe_routing.py)
- [tests/rl/unit_tests/cpu/test_model_defaults.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/rl/unit_tests/cpu/test_model_defaults.py)
