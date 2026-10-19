---
id: ecosystem/topics/loongforge-chunkpipe-variable-length
title: LoongForge：变量长 ChunkPipe 的位置、缓存与梯度归一化
engine: loongforge
kind: authored
stages:
- adapt
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-20'
coverage: selected source delta and related discussion review; unchanged evidence reused; no HCU runtime validation
sources:
- source: baidu-baige-loongforge
  path: .gitmodules
  commit: 15504e1bb7d948bd3900d17ed35fe5cd4bc50d3c
  sha256: b5aca9eaf884dfde53b152fc6000eff8a8c793339b659411f6e79292bf68b2ed
- source: baidu-loong-megatron
  path: megatron/core/transformer/transformer_config.py
  commit: cfcdede99642303b1dff0464b77a7df50ef6e4ea
  sha256: 1ddc625ba2d9304b535c88279d2db9a47796eaeb3617bad9a6e6674386a69d74
- source: baidu-loong-megatron
  path: megatron/core/rerun_state_machine.py
  commit: cfcdede99642303b1dff0464b77a7df50ef6e4ea
  sha256: 73ad61a5b68cbf84bb329c63d12c95cb229659263824fbed04aa5ef15aa8de88
- source: baidu-loong-megatron
  path: megatron/core/transformer/multi_latent_attention.py
  commit: cfcdede99642303b1dff0464b77a7df50ef6e4ea
  sha256: 8e0d86ceb46bd8961f5223660b69b65b3748cbc403280e353ff4ecb01688d2d2
- source: baidu-loong-megatron
  path: megatron/core/transformer/multi_token_prediction.py
  commit: cfcdede99642303b1dff0464b77a7df50ef6e4ea
  sha256: c457ee5ba673f226c7eeca6edc99f5250f1a1b33db474a56adb16d960743c28d
- source: baidu-loong-megatron
  path: megatron/training/arguments.py
  commit: cfcdede99642303b1dff0464b77a7df50ef6e4ea
  sha256: 8d3fbb2dc5c7a9b27983095682c54a37976b41b4a1c0f323df2b185df4c9a65c
- source: baidu-loong-megatron
  path: megatron/training/training.py
  commit: cfcdede99642303b1dff0464b77a7df50ef6e4ea
  sha256: 9c83ff76f873422a85cef327467c4fffe94b9ba88f2a43a94498c27d152f7702
- source: baidu-loong-megatron
  path: megatron/training/utils.py
  commit: cfcdede99642303b1dff0464b77a7df50ef6e4ea
  sha256: d4323db501330f50f12951c09dd324060879b676aa299bbd36ef6aad66d9be02
---

# LoongForge：变量长 ChunkPipe 的位置、缓存与梯度归一化

## 问题与固定父子版本

ChunkPipe 将一条序列拆成多个 chunk 推进模型计算；它与独立样本的 microbatch 累积、[跨微批 EP overlap](loongforge-ep-offload.md)和激活卸载分别有状态与数值契约。分块长短改变后，固定 `chunk_index * chunksize`、等宽 KV 槽读写和逐 chunk 平均 loss 都可能失真，不能仅改变输入切片就认为模型语义未变。

本文固定 LoongForge 父仓 `15504e1bb7d948bd3900d17ed35fe5cd4bc50d3c` 的实际 Loong-Megatron gitlink `cfcdede99642303b1dff0464b77a7df50ef6e4ea`，对照旧子提交 `64c279afb879229cff12fb293624e3691990403f`。本次读取的是配置、iterator、MLA/MTP 与训练数据消费者的真实差异，没有以子仓最新 HEAD 替代父锁，也没有 HCU 实测性能数据。

## 配置如何传到实际张量

`training/arguments.py` 在启用 ChunkPipe 后展开两种输入：`--chunksize` 形成等长表；`--chunk-sizes` 显式给每块 token 数。校验生成 `chunk_sizes`、前缀和 `cu_chunks`、`max_chunk_size` 和块数；变长模式的兼容标量 chunksize 取最大值，不能继续把它当每块真实长度。

`training.py` 将长度表交给 `ChunkDataIterator`；后者对序列轴按相邻 prefix-sum 边界切 tokens/labels 等字段，并核对实际序列总长。`training/utils.py` 先广播当前 chunk 的真实宽度，让非 source TP rank 分配匹配接收 buffer；不只改变 rank0 的 view。长度不等时还启用 variable-sequence-length P2P，避免 PP 双方沿用固定 shape。

## 必须同时满足的边界

| 条件 | 当前固定实现的约束及原因 |
| --- | --- |
| 长度与调度 | 显式表非空、正数且总和等于 seq_length；预训练块数需能被 PP 整除。未显式表时保留等长路径。 |
| SFT | 当前拒绝在 SFT 传 `--chunk-sizes`，因为其 collator 仍按标量 chunksize 做等宽 padding，不能用不同元数据声称已产生变量宽度；应按受支持的 uniform SFT 路线。 |
| loss | 不等长块要求 calculate-per-token-loss；按每块自己的 token 数先求平均会让短块 token 获得更大梯度权重。模型主 loss、MTP/辅助项的归一化需在目标配方再核对，正常 loss 外观不足以证明梯度正确。 |
| Graph | 不等长块要求 cuda_graph_impl=none；固定形状捕获不能直接重用到变化的激活宽度。等长路径也仍受其他 Graph 条件限制。 |
| TP/SP | MLA 且 TP>1 要求 sequence parallel；启用 SP 时每块长度需被 TP 整除，否则缓存分片/序列 scatter 不一致。这些检查不证明所有 CP、精度和后端组合均支持。 |

## MLA 缓存、位置与 MTP

`multi_latent_attention.py` 按 `max_chunk_size` 给每个缓存槽保留固定 stride，写入按当前 tensor 实长，读取旧块只取其真实长度；总历史长度与 RoPE offset 改用 `cu_chunks`，causal mask 的对角偏移也来自当前块起点。变长减少尾块计算不自动等于同比节省 KV 槽容量：仍按最大块预留、缓存槽数和 TP 布局计峰值，并检查是否读到尚未写入的 padding。

`multi_token_prediction.py` 的 bridge-token 预处理会延长输入；embedding 前必须裁到当前块实际长度，而非最大 chunksize，否则短块残留额外 token，可能使 SP reduce-scatter 不整除。这里的 MTP 修复不取消 EP、checkpoint、低精度或模型特定 MTP 的其他约束。

## 验证、性能与回退

先用原 uniform 路径校验回退，再在相同完整序列/初态下比较不同分块的有效 token、位置/causal mask、logits、输入/参数梯度和一次 optimizer 更新。覆盖首末短块、TP source/接收 rank、PP shape 协商、MLA 缓存循环复用、MTP bridge token、非法总长/整除、SFT/Graph 拒绝路径与保存恢复。这里列的是应执行矩阵，本轮未运行这些设备测试，不把参数校验或源码注释当数值通过。

性能保持相同训练语义，记录实际块宽、padding、缓存峰值、通信形状协商、step wall clock 和有效 token/s；分块改变调度/缓存/计算量，不能只统计最快块或只报减小的张量。回退为已验证等长 ChunkPipe 或完整普通路径，同时恢复其位置表、缓存和 loss 口径，不能只删一个长度参数而保留另一套状态。

更新时同时检查父 gitlink、arguments/config、ChunkDataIterator、MLA/MTP、TP batch broadcast、PP schedule 与对应测试。其他模型/indexer、所有低精度与多并行组合未在本页全面审计；进一步采用仍需实际 HCU 调用、梯度及阶段质量证据。

## 固定源码

- [.gitmodules](https://github.com/baidu-baige/LoongForge/blob/15504e1bb7d948bd3900d17ed35fe5cd4bc50d3c/.gitmodules)
- [megatron/core/transformer/transformer_config.py](https://github.com/baidu-baige/Loong-Megatron/blob/cfcdede99642303b1dff0464b77a7df50ef6e4ea/megatron/core/transformer/transformer_config.py)
- [megatron/core/rerun_state_machine.py](https://github.com/baidu-baige/Loong-Megatron/blob/cfcdede99642303b1dff0464b77a7df50ef6e4ea/megatron/core/rerun_state_machine.py)
- [megatron/core/transformer/multi_latent_attention.py](https://github.com/baidu-baige/Loong-Megatron/blob/cfcdede99642303b1dff0464b77a7df50ef6e4ea/megatron/core/transformer/multi_latent_attention.py)
- [megatron/core/transformer/multi_token_prediction.py](https://github.com/baidu-baige/Loong-Megatron/blob/cfcdede99642303b1dff0464b77a7df50ef6e4ea/megatron/core/transformer/multi_token_prediction.py)
- [megatron/training/arguments.py](https://github.com/baidu-baige/Loong-Megatron/blob/cfcdede99642303b1dff0464b77a7df50ef6e4ea/megatron/training/arguments.py)
- [megatron/training/training.py](https://github.com/baidu-baige/Loong-Megatron/blob/cfcdede99642303b1dff0464b77a7df50ef6e4ea/megatron/training/training.py)
- [megatron/training/utils.py](https://github.com/baidu-baige/Loong-Megatron/blob/cfcdede99642303b1dff0464b77a7df50ef6e4ea/megatron/training/utils.py)
