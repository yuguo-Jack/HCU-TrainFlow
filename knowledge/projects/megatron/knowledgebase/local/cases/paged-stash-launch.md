---
id: official-megatron-wiki/cases/paged-stash-launch
title: Paged Stash copy/pop：launch 粒度、带宽与 PR 描述漂移
engine: megatron
kind: authored
stages:
- optimize
review_level: pr-diff-and-selected-source-reading
runtime_validated: false
pr_sources:
- pr-nvidia--megatron-lm-7897
sources:
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/ops/paged_stash.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: dba859b82cd90179fc8e45bf3c55ecef10a7432a6d968df4b30c66768efd6de4
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/paged_stash.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 950b8c72253b90e8b6936a5aa8532120bd8e056f6cc88807efa4c818d88d4efc
- source: nvidia-megatron-lm
  path: tests/unit_tests/transformer/moe/test_paged_stashing.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 7928d461548b0d33cc0d488d5f164d73bd1aa301a9f73069e4f289fba9e6de8d
reviewed_on: '2026-10-12'
---

# Paged Stash copy/pop：launch 粒度、带宽与 PR 描述漂移

## 问题与边界

[PR #7897 完整来源页](../../upstream/prs/NVIDIA--Megatron-LM/PR-7897.md) 针对 MoE paged-stash 的 Triton copy/pop。宽激活需要搬运大量数据，原先固定的每 program 工作量和 program 数量未能在报告所用 GPU 上充分利用带宽。该问题不同于 stash 容量不足、路由 skew 或 CPU spill：这些路径可能同时影响时间，但优化手段不同。

PR 作者报告过 NV 硬件上的局部加速；这些数值是上游报告，TrainFlow 未复现，也不能直接作为 HCU 性能目标。端到端收益取决于 copy/pop 是否在关键路径、是否与其他 kernel 争用带宽，以及占 step 的比例。

## 为什么必须继续读最终代码

PR 的原始描述写过“增加两个 TransformerConfig 选项”。但本次保留的最终 diff 和 head 文档写明**没有这两个配置项**：`paged_stash_reset` 根据设备 capability 选择 launch 大小，特定设备使用更宽配置，其他设备保留原默认。

因此不能从 description 生成不存在的命令行参数。PR 来源页同时保存原文、review 和最终文件；应用时以目标版本完整源码及调用条件为准。这个例子也是在线搜到 PR 后必须追代码的直接理由。

## 实现位置与数据流

1. `moe/ops/paged_stash.py` 定义默认 launch 常量与 copy/pop kernel。
2. `PagedTensor.offload_to_stash`、`reload_from_stash` 接收 block_size/max_blocks，决定 grid 和 Triton BLOCK_SIZE。
3. `PagedStashManager` 保留选定参数，stash/reload 两条路径都下传。
4. `paged_stash_reset` 在开启路径选择设备配置；关闭时不应进行无意义的 device 查询。
5. page free list、有效 token 数、masked tail、host spill 与 stream 同步仍保持原有语义。

head/base 固定链接和完整 patch 位于来源页。进一步分析 HCU 实现时应读取对应分支的 Triton kernel、caller 和测试，不能直接移植 NVIDIA capability 判断。

## 测试和优化实验

新增测试覆盖两组 launch 参数、uint8/bfloat16、多种 hidden size、尾部 mask、行数超过 program 数、被打乱的 free list，以及 stash→reload 的 bit-exact round trip。还有设备选择和关闭功能时不查询 device 的测试。

HCU 实验建议按实际 token×hidden、dtype、page size 采样，分别测 copy、pop、成对生命周期与训练中时间；检查 overflow/spill 和额外同步。带宽分母需明确有效读写字节及 metadata，不能直接用输入大小除以整段耗时与 copy benchmark 混比。

## 适用、失败与回退

适用于已确认 stash copy/pop 是有价值热点的任务。更大的 block/program 不保证所有 shape 更快，可能增加资源压力或带宽争用。保留原 launch 参数作对照，先局部正确性和性能回归，再观察 MoE/PP 完整生命周期，组合稳定后做阶段 loss。

更新时一起检查 stash 专题、MoE/内存总览、配置文档、copy/pop 测试与调用方。PR 已合入不表示部署分支已包含；固定 head 也不是最新 main 的替代品。

## 当前主干复核：案例仍有实现依据

2026-10-12 固定主干仍保留 copy/pop 参数传递与设备选择，`paged_stash_reset` 对 capability `(10,7)` 选 4096/8192，其他设备选默认 1024/2048；disabled 路径在设备查询前返回。对应单测覆盖设备选择、关闭时不查询和两套 launch 的 bit-exact round trip。因此本案例继续适用于解释当前官方实现，PR 原始 head/review 仍作为历史改因证据保留。

该判断是 NVIDIA capability 规则，不能映射成 HCU gfx 支持/最优 launch 的结论。当前 docs 与配置对 stash backend 的描述还存在范围差异，读 [MoE](../topics/moe.md)/[显存](../topics/memory.md) 的当前配置约束后，再沿实际 HCU fork 的 kernel/stream/stash 生命周期验证；本轮没有执行这组 GPU 测试。

- [megatron/core/transformer/moe/ops/paged_stash.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/transformer/moe/ops/paged_stash.py)
- [megatron/core/transformer/moe/paged_stash.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/transformer/moe/paged_stash.py)
- [tests/unit_tests/transformer/moe/test_paged_stashing.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/tests/unit_tests/transformer/moe/test_paged_stashing.py)
