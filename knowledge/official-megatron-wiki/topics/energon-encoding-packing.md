---
id: official-megatron-wiki/topics/energon-encoding-packing
title: Energon：TaskEncoder、Packing 与确定性重放
engine: energon
kind: authored
stages:
- adapt
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected source, official documentation and related PR reading; no HCU runtime
  validation
sources:
- source: nvidia-megatron-energon
  path: docs/source/basic/task_encoder.md
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 0f10499347e02b15f04fbcdac053bccb4640ae205b8951c8bcff718443850164
- source: nvidia-megatron-energon
  path: docs/source/advanced/packing.md
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: 92fea78e4c464f9bca5e44d724aaf4f3b28d98ca6b2fc9a0c269826925afe8fa
- source: nvidia-megatron-energon
  path: src/megatron/energon/task_encoder/base.py
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: d4fce3a940e2a673d3e7a40376f7741799b6c687b1e6ddea7202d66c8e943706
- source: nvidia-megatron-energon
  path: docs/source/advanced/error_handling.md
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: d4484631b352c16fdab3896e7bff9d7c86de0d59962dac00109ca99d2b6a0e78
- source: nvidia-megatron-energon
  path: tests/test_dataset_det.py
  commit: accdabc3983843665a34cd1578c0e82d2403e3a9
  sha256: f0311cad67786f3aa06c040e53e589e453506a0cad7ea2d2a18549cb6d3e914e
---

# Energon：TaskEncoder、Packing 与确定性重放

## 问题与收益

变长样本用固定长度batch时大量padding占用算力/HBM；packing将多个样本组织成有效序列，提高相同token工作量的利用率。Energon负责样本选择/合并，训练消费者负责attention隔离、position/label和loss；只拼接token不是完整的packing实现。

## 调用链和入口

TaskEncoder encode_sample→`select_samples_to_pack`对packing buffer划分groups→`pack_selected_samples`组合每group→`batch`。dataset的packing_buffer_size非零才启用相应流水线；返回样本类型可不同，batch必须匹配。库根据原样本产生restore key，不能由任务随意抹掉所有原始身份。

buffer更大通常增加组合选择，但占host memory、启动等待和恢复重放成本。encoder/tokenizer与packing策略改变会影响长度分布，需固定revision；不要把某个教程buffer值作为所有模型默认。

## Stateless与随机augmentation

为可恢复packing，encoder/pack函数需要真实stateless：同输入和随机状态应给同输出；仅贴decorator并不能证明。随机augmentation用`@stateless(restore_seeds=True)`按sample index恢复seed，重放时过滤/SkipSample也必须一致。否则已消费offset与buffer restore key失配，可能报Unexpected skip sample或默默改变数据目标。

普通迭代默认log并跳过某些样本，而restore的错误策略严格，超过连续错误容限/编程错误会fail；从“训练没崩”推断数据正常不成立。观测skip率、数据类型与有效token分布，故障定位保留原sample/shard信息。

## Mask/label、性能与数值验收

核对每样本ID/有效token不丢不重，segment causal mask、EOS/special tokens、position/RoPE重置、cu-seqlens与ignore/loss mask。若loss按token加权，packing前后分母应对应同一目标；原样本等权目标不能擅自变token等权。

比较未pack/pack的真实数据吞吐、encoderCPU、hostRSS、batch-ready、H2D、kernelshape和稳态step，保持数据量/GBS口径清楚。恢复测试比较中断前后未来batch/augmentation与梯度阶段loss，不用只检查总样本数。

## 回退与更新

异常先重读encoder→pack→batch→训练loss链，退回普通padding/可信数据配方定位最小差异。变更TaskEncoder、dataset schema/混合/shuffle或消费者mask/loss时同时复核[总览](../energon.md)和[恢复专题](energon-recovery-throughput.md)；不是encoder升级后直接复用旧checkpoint状态。

## 固定证据与复核范围

- [docs/source/basic/task_encoder.md](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/docs/source/basic/task_encoder.md)
- [docs/source/advanced/packing.md](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/docs/source/advanced/packing.md)
- [src/megatron/energon/task_encoder/base.py](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/src/megatron/energon/task_encoder/base.py)
- [docs/source/advanced/error_handling.md](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/docs/source/advanced/error_handling.md)
- [tests/test_dataset_det.py](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/tests/test_dataset_det.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
