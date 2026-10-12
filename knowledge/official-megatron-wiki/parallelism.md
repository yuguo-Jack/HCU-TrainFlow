---
id: official-megatron-wiki/parallelism
title: 并行域、微批与 rank 采样
engine: megatron
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
sources:
- source: nvidia-megatron-lm
  path: megatron/core/parallel_state.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 414ecaf3b1891e8d621e5ec86a80af9d2d313d4393ac11e83832ff4bf7257dd2
- source: nvidia-megatron-lm
  path: docs/user-guide/parallelism-guide.md
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 8fe555b69e65abd543acc633c23f1b33491d6b0266a7b6c9848dd997222e674d
- source: nvidia-megatron-lm
  path: megatron/core/pipeline_parallel/schedules.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 3719d850b8822e221f30472881b8802b8f88ce02167856130fae97849d1d91ee
- source: nvidia-megatron-lm
  path: megatron/training/arguments.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: eca958faeab77e1df81073998ea07aa3cc8a5884f96f6182782d620942139bd2
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 36ebc84d850af5653d6f17aa2147f61b79f82b7a05422b8d0eba8943bafb0f87
- source: nvidia-megatron-lm
  path: docs/user-guide/features/pipeline_parallel_layout.md
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: a8f23d24f026a955abe527e45bd83fde707e967110a9ad868cc72c4a1e265c5f
kind: authored
---

# 并行域、微批与 rank 采样

## 需要显式建模的拓扑

TP、PP、DP、CP、EP 和 expert tensor parallel 不应只登记几个整数。保存每个实际 process group 的成员、节点和设备映射；EP 可能与其他维度共享或重组 rank。不能直接按 world size 除某几个参数猜测所有组。

`profile-plan` 接收实际 groups 和可抓取 ranks，每个非单例组至少选两个成员。PP 关注首尾及不平衡 stage，EP 关注负载明显不同成员。两 rank 是最低观测要求，collective 全组分析或跨节点偏斜可能需要全组。

## 调参推理

**并行切分是系统调参的优先项。** 在深入单个 kernel 前，结合目标卡数、实际互联、单卡可用显存和 HCU 工程已支持的配方，确定可行布局，再以短跑与端到端 profile 迭代。目标是在显存余量内提高有效吞吐；显存占得更多或切得更细并不一定更快。

- 联合比较 DP/状态分片、TP/SP、PP/虚拟流水与层分配、长序列 CP、MoE 的 EP/expert TP，并配合 microbatch、梯度累积、选择性重算和必要的 offload。受约束的组合一起变更并说明原因；不机械照搬 NV 的并行度或互联域。
- 估算最吃紧 rank 的参数、梯度、优化器、激活与临时/通信 buffer；短跑核对峰值 allocated/reserved、设备实际占用，以及初始化、optimizer、graph 和保存恢复峰值。余量按模型、动态 shape 和现场波动决定，不设统一填满比例；估算器的覆盖范围与遗漏要记录。
- 对照表保存布局、微批/累积、重算/分片、峰值与余量、profiler-off step time/tokens/s、通信及 PP 空泡。过度切分可能让 GEMM 变小、通信增多；较大微批也会挤占 overlap buffer 或触发额外重算，最终按实测权衡。
- 固定模型、数据、序列长度、有效全局 batch/token、精度和优化器语义；调整微批或 DP 时同步检查累积步数、样本消费和学习率 schedule。每轮做局部正确性，布局稳定后按原流程做阶段 loss。改变布局后重新采实际组和算子 shape，旧热点/效率结论仅作参考。

已有官方参考：[Megatron 并行策略原文](../upstream-docs/nvidia-megatron-lm/docs/user-guide/parallelism-guide.md.md)、[Bridge 性能调优指南](../upstream-docs/nvidia-nemo-megatron-bridge/docs/performance-guide.md.md)、[Bridge 显存估算教程](../upstream-docs/nvidia-nemo-megatron-bridge/docs/training/memory-estimator.md.md)，以及 [Megatron Core 开发指南入口](https://docs.nvidia.com/megatron-core/developer-guide/latest/index.html)。这些是官方机制与规划依据，支持组合、参数名称和估算假设仍要与目标 HCU 分支核对。

全局 batch、microbatch 和梯度累积必须满足当前 schedule 与 DP 的关系；packing、动态 batch 或变长场景应记录真实 token 数。缩层代理保留模型其他维度，不能为了跑通同时缩 seq 或专家数再拿其耗时外推。

PP 空泡由调度、微批和 stage 工作量共同决定；EP token 不均可能使最慢 rank 限制整个步。分别记录各 rank phase 的计算、通信和等待，先解释时间线，再决定改并行度还是算子实现。

## 真实 group、batch 与 PP/VPP 约束

`parallel_state.initialize_model_parallel` 分别构造普通 decoder 的 rank 生成器和 expert rank 生成器；普通 DP 和 expert DP 的成员/大小可能不同。标准、不启用 GTP-weight-remat 的 decoder 布局可先检查 `world_size = TP × PP × CP × DP`，专家布局另核对 expert TP/EP/expert DP；**不要把 EP 再乘进同一个 world size 公式**。新 GTP-remat 等轴开启后按源码的 `model_size`/rank 生成器计算，不能沿用简化式。

固定长度、标准梯度累积下，`global_batch = micro_batch × DP × num_microbatches`；这里 DP 是本模型实际复制域，CP 拆序列而不直接增加独立样本数，EP 也不作为额外样本倍数。ramp-up、step batch schedule、GTP-remat、packing/SFT 和动态 token batching 分别追当前 calculator、实际消费计数与 loss 归一化。不能只让数字相等而改变有效 token 和学习率语义。

PP 不只按层数均分：embedding、attention/MLP/MoE、MTP 和末端 loss 的时间/显存不同。官方 `--pipeline-model-parallel-layout` 用 `E/t/m/L` 表示这些阶段，`|` 分 stage、`*` 重复，并允许空 stage；它标为 experimental。读实际 layout 解析与 schedule，检查 VPP chunk、每轮 microbatch 组、P2P 和模块特殊处理，不能用简单 PP 数字解释所有空泡。

先将能装下的布局与 worst-rank 峰值列出，再比较 profiler-off 有效吞吐和同域等待。`overlap_p2p_comm` 与批量 P2P 等组合有配置约束；改布局后回到 [overlap](overlap.md) 检查互斥项与 [loss](training-and-loss.md) 检查缩放。这里只解释固定官方机制，HCU 组合支持需独立验收。

## 验证

改变拓扑后重新构造 context；旧 trace/环境检查/质量报告仍保留，但不能为新配置放行。DP/TP/EP collective 单测的数据量与 dtype 应来自真实模型，机内与机间测试不能互相替代。

## 固定源码与更新范围

- [megatron/core/parallel_state.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/parallel_state.py)
- [docs/user-guide/parallelism-guide.md](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/docs/user-guide/parallelism-guide.md)
- [megatron/core/pipeline_parallel/schedules.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/pipeline_parallel/schedules.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
