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
reviewed_on: '2026-10-20'
coverage: reviewed training, parallel, state and backend implementation chains; not
  all models or runtime combinations
sources:
- source: nvidia-megatron-lm
  path: megatron/core/extensions/transformer_engine.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 402dd8cf540b17fac15f0f77fba603acaa5fb4f6d9493536ff6550719f0bda47
- source: nvidia-megatron-lm
  path: megatron/core/models/gpt/gpt_layer_specs.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 9e153c7f3d3a671f1bd9b84023bfe0f14711fe942c4c0df3dc1dec288100c4af
- source: nvidia-megatron-lm
  path: megatron/core/transformer/transformer_config.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: ec8de7059bf8d6c78663384a489794d0712eaa1b81685ad0339e2c77cb9e32e3
- source: nvidia-megatron-lm
  path: tests/unit_tests/transformer/test_multi_latent_attention.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 062766158e7bf127e0d2971c0caae021e4b0651fd58ee3ebba90fb2a535195ab
- source: nvidia-megatron-lm
  path: megatron/core/transformer/multi_latent_attention.py
  commit: e8a302ac5bfeb98c6701020cc6cba977d05ab1d4
  sha256: 0cb02e328f77eeabb0131fb12b2eef13d565eeb8d2f795b5a6f16359cba24503
---

# Megatron Core→Transformer Engine：配置、融合、低精度与HCU接口

## 本页的职责

独立TE资料见[官方TE总览](../../../../transformer-engine/knowledgebase/local/overview/overview.md)、[精度缓存](../../../../transformer-engine/knowledgebase/local/topics/precision-and-cache.md)、[attention](../../../../transformer-engine/knowledgebase/local/topics/attention.md)与[教程/更新](../../../../transformer-engine/knowledgebase/local/changes/tutorials-and-update.md)。本页聚焦Core怎样调用TE、哪些语义必须在HCU实现保持，避免重复介绍整个TE库。

## 从 spec 到实际模块

GPT layer spec根据模型与config选择norm、linear、attention/MoE等具体模块，Core的`extensions/transformer_engine.py`将partition、return-bias/residual、parallel-group、初始化和quantization参数交TE。模块内部再选择真正GEMM/attention/backward和compiled kernel。TE安装成功或use-TE flag为true不证明所有子模块都走同一融合路径。

`TELinear`/`TELayerNormColumnParallelLinear`、TEGroupedLinear及attention wrappers分别承接Core shape/layout和并行契约。某layernorm-linear为融合模块时，其状态/精度、bias和saved tensors与拆成两个module不同；拆分或替换应保留权重views、并行标记、quant state和接口返回值。

## Low-precision recipe 和缓存

Core当前有TEQuantizationRecipe/Params，区分training/evaluation recipe、tensorwise/blockwise/MXFP8、FP4/custom及model-init参数；不合法组合显式报错。fp8 dtype只描述存储的一部分，实际scale、quantizer、amax history、累积和通信精度须继续进TE实现。

first-microbatch跟踪控制权重cache复用；optimizer更新后cache失效/重建、eval/save、recompute和graph重放都要保持正确。更新、量化、分片、tied/expert参数不能仅用输出tensor.dtype判定。

某些API有兼容import/fallback，实际TE版本/符号与调用者条件需要同时记录；官方TE最新接口与HCUfork支持分开锁，不为了导入成功静默改一条不等价数值路径。

## 融合粒度和通信重叠

对照实际NV spec/kernel：输入/输出layout、mask/bias、activation/residual、saved state、RNG、dgrad/wgrad与cast/reduction边界。TE user-buffer/parallel overlap要核对HCU实际实现，不把NV连接数变量当GPU_MAX_HW_QUEUES配置。

[MLA residual案例](../cases/mla-residual-norm.md)说明pre-MLP norm缺`has_residual=True`会使配置已开但融合backward没有进入。验证既看module的returns-residual属性，也比较outputs/input-grads/param-grads和真实trace；源码属性正确不代替kernel执行证据。

## 当前 adapter 的新增消费条件

虚拟专家给 TEGroupedLinear 增加 runtime slot，但 checkpoint/初始化仍只拥有真实专家，且禁用 first-microbatch 权重量化缓存复用。不要按运行 GEMM 数量推断模型参数数或保存布局。

MTP 与主头共享权重时设置 `zero_tensor_dummy_wgrad`，由支持该属性的 TE 返回可免费相加的 ZeroTensor dummy；真正的 wgrad 仍已累积到 main_grad。旧 TE 可能忽略属性，不能把 dummy 当真实梯度或宣称所有版本均消除了额外 add。

MLA 新增 KV RoPE+MXFP8 量化融合，与已有 residual norm 修复是不同机制。当前路径要求 MXFP8 DPA、零 dropout 和支持的 CUDA 架构/布局；TP/CP>1、THD、FP16、相关重算、eval 或禁用对应 FP8 backward 时走未融合路径。检查配置前置报错、运行 fallback 和实际 kernel 三层，不将 fallback 单测算为融合路径通过。

## HCU复用与交付

已有HCU TE能力优先复用；通用training fusion/AI编译/cuDNN等需求查Flash-Train已实现功能，PrimusTurbo与消费者接入亦按真实版本参考。缺口按接口owner集中补实现，训练引擎保留调用/配置与测试，底层库接收其负责kernel/ABI/数值改动。

先用baseline-generator明确语义/布局并建立保守正确初版，再用HIP或Triton optimizer按热点、同shape性能、roofline/bottleneck、prof/ISA推进。初步融合不意味着优化已完成；估计的局部上限和模型内关键路径决定下一轮优先级。

## 测试、失败与更新

局部比较包含前向、反向、梯度累积、更新后cache与quant state、图/重算路径，覆盖真实多shape/空专家/尾部和数值极端；稳定阶段再验loss。平台版本缺TE特性时明确fallback/回退是否语义可接受，不能用skip当通过。

更新TE/Core任一接口、recipe、module spec或backend selection时联动本页、独立TE Wiki、MoE/overlap/memory及算子Skill。官方PR merged、HCUport与现有任务通过分开写；底层实现有疑点直接读对应实际branch，不仅搜索教程。

## 固定源码与维护边界

- [megatron/core/extensions/transformer_engine.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/core/extensions/transformer_engine.py)
- [megatron/core/models/gpt/gpt_layer_specs.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/core/models/gpt/gpt_layer_specs.py)
- [megatron/core/transformer/transformer_config.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/megatron/core/transformer/transformer_config.py)
- [tests/unit_tests/transformer/test_multi_latent_attention.py](https://github.com/NVIDIA/Megatron-LM/blob/e8a302ac5bfeb98c6701020cc6cba977d05ab1d4/tests/unit_tests/transformer/test_multi_latent_attention.py)

2026-10-20按上述固定源码/官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。