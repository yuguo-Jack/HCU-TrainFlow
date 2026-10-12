---
id: official-megatron-wiki/transformer-engine
title: Megatron Core→Transformer Engine：配置、融合、低精度与HCU接口
engine: megatron
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: reviewed training, parallel, state and backend implementation chains; not
  all models or runtime combinations
sources:
- source: nvidia-megatron-lm
  path: megatron/core/extensions/transformer_engine.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 6ee4807baa38389691e5ecf19472ee933f2ac5b6fe51b3e3cf26539388b77bf4
- source: nvidia-megatron-lm
  path: megatron/core/models/gpt/gpt_layer_specs.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 9e153c7f3d3a671f1bd9b84023bfe0f14711fe942c4c0df3dc1dec288100c4af
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 36ebc84d850af5653d6f17aa2147f61b79f82b7a05422b8d0eba8943bafb0f87
- source: nvidia-megatron-lm
  path: tests/unit_tests/transformer/test_multi_latent_attention.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 3df4c807086cc0e770c7fb3c07225f5cb9580756de9708d8509fffbfccd34b69
---

# Megatron Core→Transformer Engine：配置、融合、低精度与HCU接口

## 本页的职责

独立TE资料见[官方TE总览](../official-transformer-engine-wiki/overview.md)、[精度缓存](../official-transformer-engine-wiki/precision-and-cache.md)、[attention](../official-transformer-engine-wiki/attention.md)与[教程/更新](../official-transformer-engine-wiki/tutorials-and-update.md)。本页聚焦Core怎样调用TE、哪些语义必须在HCU实现保持，避免重复介绍整个TE库。

## 从 spec 到实际模块

GPT layer spec根据模型与config选择norm、linear、attention/MoE等具体模块，Core的`extensions/transformer_engine.py`将partition、return-bias/residual、parallel-group、初始化和quantization参数交TE。模块内部再选择真正GEMM/attention/backward和compiled kernel。TE安装成功或use-TE flag为true不证明所有子模块都走同一融合路径。

`TELinear`/`TELayerNormColumnParallelLinear`、TEGroupedLinear及attention wrappers分别承接Core shape/layout和并行契约。某layernorm-linear为融合模块时，其状态/精度、bias和saved tensors与拆成两个module不同；拆分或替换应保留权重views、并行标记、quant state和接口返回值。

## Low-precision recipe 和缓存

Core当前有TEQuantizationRecipe/Params，区分training/evaluation recipe、tensorwise/blockwise/MXFP8、FP4/custom及model-init参数；不合法组合显式报错。fp8 dtype只描述存储的一部分，实际scale、quantizer、amax history、累积和通信精度须继续进TE实现。

first-microbatch跟踪控制权重cache复用；optimizer更新后cache失效/重建、eval/save、recompute和graph重放都要保持正确。更新、量化、分片、tied/expert参数不能仅用输出tensor.dtype判定。

某些API有兼容import/fallback，实际TE版本/符号与调用者条件需要同时记录；官方TE最新接口与HCUfork支持分开锁，不为了导入成功静默改一条不等价数值路径。

## 融合粒度和通信重叠

对照实际NV spec/kernel：输入/输出layout、mask/bias、activation/residual、saved state、RNG、dgrad/wgrad与cast/reduction边界。TE user-buffer/parallel overlap要核对HCU实际实现，不把NV连接数变量当GPU_MAX_HW_QUEUES配置。

[MLA residual案例](cases/mla-residual-norm.md)说明pre-MLP norm缺`has_residual=True`会使配置已开但融合backward没有进入。验证既看module的returns-residual属性，也比较outputs/input-grads/param-grads和真实trace；源码属性正确不代替kernel执行证据。

## HCU复用与交付

已有HCU TE能力优先复用；通用training fusion/AI编译/cuDNN等需求查Flash-Train已实现功能，PrimusTurbo与消费者接入亦按真实版本参考。缺口按接口owner集中补实现，训练引擎保留调用/配置与测试，底层库接收其负责kernel/ABI/数值改动。

先用baseline-generator明确语义/布局并建立保守正确初版，再用HIP或Triton optimizer按热点、同shape性能、roofline/bottleneck、prof/ISA推进。初步融合不意味着优化已完成；估计的局部上限和模型内关键路径决定下一轮优先级。

## 测试、失败与更新

局部比较包含前向、反向、梯度累积、更新后cache与quant state、图/重算路径，覆盖真实多shape/空专家/尾部和数值极端；稳定阶段再验loss。平台版本缺TE特性时明确fallback/回退是否语义可接受，不能用skip当通过。

更新TE/Core任一接口、recipe、module spec或backend selection时联动本页、独立TE Wiki、MoE/overlap/memory及算子Skill。官方PR merged、HCUport与现有任务通过分开写；底层实现有疑点直接读对应实际branch，不仅搜索教程。

## 固定源码与维护边界

- [megatron/core/extensions/transformer_engine.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/extensions/transformer_engine.py)
- [megatron/core/models/gpt/gpt_layer_specs.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/models/gpt/gpt_layer_specs.py)
- [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/transformer/transformer_config.py)
- [tests/unit_tests/transformer/test_multi_latent_attention.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/tests/unit_tests/transformer/test_multi_latent_attention.py)

2026-10-12按上述固定源码/官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。
