---
id: official-megatron-wiki/energon
title: Energon：数据吞吐与可恢复样本顺序
engine: energon
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-megatron-energon
  path: README.md
  commit: d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b
  sha256: 6309cd798e11e2f2b47d770eb0d3ebc24a34c1dc474c4ab8d86c7e923bb50b63
- source: nvidia-megatron-energon
  path: src/megatron/energon/loader.py
  commit: d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b
  sha256: aab81de16d65761bf00fc88a16c63c39e4f15118ef9044b4473b5aae913b279b
- source: nvidia-megatron-energon
  path: src/megatron/energon/savable_loader.py
  commit: d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b
  sha256: b94cb91f8ae3d99e45c49303d1acbfb2b6a9f286df1974f74ac3b00fcf4b17c2
- source: nvidia-megatron-energon
  path: src/megatron/energon/task_encoder/base.py
  commit: d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b
  sha256: d4fce3a940e2a673d3e7a40376f7741799b6c687b1e6ddea7202d66c8e943706
---

# Energon：数据吞吐与可恢复样本顺序

## 结构

loader 负责对外加载入口，savable_loader 管理可保存/恢复的 loader 及 worker 状态，task_encoder 定义样本到 batch 的处理接口。CPU 空泡排查时检查这里的读取、解码、packing、预取和 worker，而不是先修改 GPU kernel。

## 数据与精度的联系

固定随机种子不足以保证恢复后的样本流一致；worker 数、DP 拓扑、shuffle 状态、已消费样本和 token packing 都需要记录。长训恢复应保存与模型 checkpoint 一致的数据状态，避免重复/漏样本导致 loss 比较失真。

## 优化方法

分别测原始读取、解码、task encoding、批处理到设备的排队时间。增加 worker 或预取会增加主存、pinned memory 和 CPU 压力；与激活/优化器 offload 同时启用时要联合观察。先记录瓶颈对应的队列，再做小范围对照。

## 验证

比较恢复前后样本 ID 序列、batch token 数与 mask，除了吞吐还检查样本语义。单独 loader benchmark 只能给出局部上限；最终验证真实训练窗口的数据等待和端到端时间。

## 固定源码与更新范围

- [README.md](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/README.md)
- [src/megatron/energon/loader.py](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/src/megatron/energon/loader.py)
- [src/megatron/energon/savable_loader.py](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/src/megatron/energon/savable_loader.py)
- [src/megatron/energon/task_encoder/base.py](https://github.com/NVIDIA/Megatron-Energon/blob/d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b/src/megatron/energon/task_encoder/base.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
