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
reviewed_on: '2026-10-20'
coverage: selected source, official documentation and related PR reading; no HCU runtime validation
sources:
- source: nvidia-megatron-energon
  path: docs/source/basic/task_encoder.md
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: 0f10499347e02b15f04fbcdac053bccb4640ae205b8951c8bcff718443850164
- source: nvidia-megatron-energon
  path: docs/source/advanced/packing.md
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: 92fea78e4c464f9bca5e44d724aaf4f3b28d98ca6b2fc9a0c269826925afe8fa
- source: nvidia-megatron-energon
  path: src/megatron/energon/task_encoder/base.py
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: 12bc1e83104e970b21fc2f4e7327de71b7131c19c3910d204709d111f70b58fc
- source: nvidia-megatron-energon
  path: docs/source/advanced/error_handling.md
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: d4484631b352c16fdab3896e7bff9d7c86de0d59962dac00109ca99d2b6a0e78
- source: nvidia-megatron-energon
  path: tests/test_dataset_det.py
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: a398a538af98ddb31748edf0307ba2e13f91102806410f2c2dcdc6e31dfc8a8e
- source: nvidia-megatron-energon
  path: src/megatron/energon/tags.py
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: 0f31d0b8b389b32fa3c20e4bcd11f1b5c8979d395318b3988a36fffc2fbe282d
- source: nvidia-megatron-energon
  path: src/megatron/energon/recipe/loader.py
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: cf94d91caa1fb6416626ef7477f337a32b0af05ad13dacb57d671af7a53393a0
- source: nvidia-megatron-energon
  path: docs/source/basic/recipe.md
  commit: bcfd8f5e245034830e7157f11f9ac0971c02e9cb
  sha256: 5fed272cbe8dcc57c3767ab8e43214578ad2325c8d5314d32073eb5d84f97f71
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

## Recipe 与 tags 迁移不等于数据语义不变

当前 TaskEncoder 从 `recipe.loader_interface` 取得已加载数据，`Batch` 通过 `SampleTagsAlias` 提供兼容。`canonicalize_tag_kwargs` 把旧 `__subflavors__` 转为 `__tags__`，`resolve_tags`/别名构造器在新旧参数同时出现时抛 `ValueError`，不是按优先级静默选择。规范 dataclass 字段已是 `__tags__`，只反射旧字段名的下游 collator/序列化代码需要检查；`derive_from` 与 `_batch` 保持 tags 元数据，旧 cooker 的字典访问另有兼容处理。

Recipe 接替 MetadatasetV2 的公开配置入口，旧名称是弃用别名；不能把此兼容推广到已移除的 v1、joined reader 或旧 checkpoint。迁移验证应覆盖旧/新关键字、两者同时给出的拒绝、cooker 按 tags 路由、多样本 batch 的元数据与实际 tensor/mask/label。`test_tags_backward_compatibility` 是上游这一兼容范围的固定测试依据，本轮未执行；自定义 TaskEncoder、recipe/blend 或 tokenizer 改动仍要重验训练数值。

## Mask/label、性能与数值验收

核对每样本ID/有效token不丢不重，segment causal mask、EOS/special tokens、position/RoPE重置、cu-seqlens与ignore/loss mask。若loss按token加权，packing前后分母应对应同一目标；原样本等权目标不能擅自变token等权。

比较未pack/pack的真实数据吞吐、encoderCPU、hostRSS、batch-ready、H2D、kernelshape和稳态step，保持数据量/GBS口径清楚。恢复测试比较中断前后未来batch/augmentation与梯度阶段loss，不用只检查总样本数。

## 回退与更新

异常先重读encoder→pack→batch→训练loss链，退回普通padding/可信数据配方定位最小差异。变更TaskEncoder、dataset schema/混合/shuffle或消费者mask/loss时同时复核[总览](../overview/energon.md)和[恢复专题](energon-recovery-throughput.md)；不是encoder升级后直接复用旧checkpoint状态。

## 固定证据与复核范围

- [docs/source/basic/task_encoder.md](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/docs/source/basic/task_encoder.md)
- [docs/source/advanced/packing.md](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/docs/source/advanced/packing.md)
- [src/megatron/energon/task_encoder/base.py](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/src/megatron/energon/task_encoder/base.py)
- [docs/source/advanced/error_handling.md](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/docs/source/advanced/error_handling.md)
- [tests/test_dataset_det.py](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/tests/test_dataset_det.py)

- [src/megatron/energon/tags.py](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/src/megatron/energon/tags.py)
- [src/megatron/energon/recipe/loader.py](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/src/megatron/energon/recipe/loader.py)
- [docs/source/basic/recipe.md](https://github.com/NVIDIA/Megatron-Energon/blob/bcfd8f5e245034830e7157f11f9ac0971c02e9cb/docs/source/basic/recipe.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
