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
reviewed_on: '2026-10-12'
coverage: Curated source chains and official evidence at a fixed main commit; not
  all models, backends or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/models/common/dist_moe/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: ae08f8c77d5c44d937b0c82513998e441f534eed53b4b91110656fcb38eee658
- source: pytorch-torchtitan
  path: torchtitan/config/transform/dist_moe.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 76e0ff6a67e72f6fc711ba23d565c435d9f7b837bd3058a0163dfbd275ba271f
- source: pytorch-torchtitan
  path: torchtitan/config/transform/token_dispatcher.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 4031eec7b291f9a955600f931cc22a97152fbefe1978f16ddcc0f5b982fc4baf
- source: pytorch-torchtitan
  path: torchtitan/quantization/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: c83d0b237d478207891164a49972280f065b7bbd9026ad8fc91cf8aa91d587c9
- source: pytorch-torchtitan
  path: torchtitan/quantization/mxfp8/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 629ffa3730098c8b956e5da4e693e9ce4639fb9f9b544befd201427a0b69b9c7
- source: pytorch-torchtitan
  path: torchtitan/quantization/nvfp4/README.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 64d5f937a3bc2a280cb7249592fe31521c7dba37d364aa4870b9430f359b8680
- source: pytorch-torchtitan
  path: torchtitan/distributed/REMAT.md
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 330408f54575d08657fae75ece3890f6f5329eeced1b1d07d43d7f1e9868328b
- source: pytorch-torchtitan
  path: torchtitan/models/common/moe.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: 6cbf29e9670551c5dacc83881bd244ce6b7ac8080533623e8e525325e8fce3ee
- source: pytorch-torchtitan
  path: torchtitan/models/common/aux_loss.py
  commit: b663c1673c00d97864bb32f18029ce5ec40442e2
  sha256: dd2c94fab5210f05537b6eb2449dfd24a969495b0bc8ac22c19ad997ef61ac42
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

区分 symmetric communication buffers、设备 scratch、保存激活和可能的 pinned-host/VMM backing；`activation_slot_bytes` 与按 factor 推导的容量不能混设，PP 多微批的 slot 生命周期也影响峰值。routing factor 是容量假设，不会自动丢弃 token 或替你均衡负载。溢出、回退或重算都会改变性能与数值验收条件。

## MXFP8：量化和缓存由谁管理

官方说明面向 B200/SM100、匹配 TorchAO 与相应 kernel。activation 采用块尺度量化，dense weight 使用支持正反向方向复用的布局；不能用“FP8”概括 scale 粒度、转置方向和保存格式。

FSDP gather BF16 权重后，通过 post-all-gather hook 构造低精度 operand，再由 FSDP 管理释放和复用。`reshard_after_forward=False` 可以跨微批复用；True 会在 backward 再 gather/量化。这里不是任意 module 自建一个永不过期的 weight cache。性能建模要包括量化、scale、重排和重复 gather；checkpoint 仍需明确其高精度状态。

WGRAD 可保存高精度 activation 到 backward 再量化，或保存特定方向的低精度 operand；forward 的因果 token 边界和 backward 的缩放是不同问题。任何融合都需核对 scale 是否跨本不应相互依赖的 token。

## NVFP4：实验状态和回退

NVFP4 依赖 TorchAO prototype 与 Blackwell/CUDA；当前说明要求切分后的 local GEMM 维度满足 kernel 对齐条件，混合 recipe 保留部分敏感层/LM head 为 BF16。官方 CI 和论文试验覆盖有限，不能据此宣称任意模型长训等价。

论文中的“只把 Fprop 切回 BF16，Dgrad/Wgrad 继续 FP4”与当前 TorchTitan 集成的实际能力不同：当前说明不支持这种独立切换。可用的完整 BF16 收尾要从包含模型、优化器、scheduler、data/step 的 checkpoint 接续，并保持训练计划。低精度模型文件可读，不等于恢复了训练状态。

## HCU 借鉴方法

迁移的是路由/状态/布局/复用机制；实际 kernel、通信后端和硬件格式需要寻找 HCU 已有实现。按真实 profile 决定是否优化路由、负载、通信 overlap、通算融合或 grouped GEMM。数学库不达预期时提交实际 rocBLAS/hipBLASLt bench 日志与复现环境，不用抽象模型 shape 代替可 tune 命令。保持与 [TrainFlow 算子流程](../../../../../../docs/practices/performance-methods.md) 一致。

## 固定证据与使用边界

本页以官方主线 `65aaaa960698ab5d6e98c874177b41b9c30e9c58` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/models/common/dist_moe/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/models/common/dist_moe/README.md)
- [torchtitan/config/transform/dist_moe.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/config/transform/dist_moe.py)
- [torchtitan/config/transform/token_dispatcher.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/config/transform/token_dispatcher.py)
- [torchtitan/quantization/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/quantization/README.md)
- [torchtitan/quantization/mxfp8/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/quantization/mxfp8/README.md)
- [torchtitan/quantization/nvfp4/README.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/quantization/nvfp4/README.md)
- [torchtitan/distributed/REMAT.md](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/distributed/REMAT.md)

- [PR #5263：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5263.md)
- [PR #5250：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5250.md)

## 当前主线补充：global batch 辅助 loss 与重算副作用

[PR #4772](https://github.com/pytorch/torchtitan/pull/4772) 增加 global batch-wise MoE 辅助 loss。`moe.py` 中 batch-wise 实现跨 DP 和 token-sharding 轴汇总 expert counts，normalized-score 的规约范围不同：DP 的可微贡献仍会由梯度规约组合，不能将两条路径都无区别 all-reduce。

滚动 counts 在各 microbatch 前向累积，保留该次前向的快照，防止后续 microbatch 已运行后 checkpoint replay 读取新的统计。`aux_loss.py` 使用 retained `torch_remat` region，避免重算重复计数/重复通信；optimizer pre-hook 负责 step 边界的累积与清零，metric 再按其 reduce_mesh 和层数归并。

调整 gradient accumulation、PP、CP/EP 或重算时，需要同时核对 routed-token 分母、aux coefficient、主 loss 和梯度，不把统计口径变化当性能回归或收敛改善。global-batch、microbatch-wise 与 aux-loss-free bias 更新是不同机制；模型配方选哪条就验证哪条，不能随意替换。

- [torchtitan/models/common/moe.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/models/common/moe.py)
- [torchtitan/models/common/aux_loss.py](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/torchtitan/models/common/aux_loss.py)