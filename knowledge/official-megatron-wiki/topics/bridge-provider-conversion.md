---
id: official-megatron-wiki/topics/bridge-provider-conversion
title: Bridge：模型配方、Pipeline Provider 与 HF 权重映射
engine: bridge
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
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/gpt_provider.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 2354707c4c81b5e05c6e62e4613092c26e7271dd17aa293ace75d1bc736abd4f
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/conversion/auto_bridge.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 90c27987d0f0a4c2c3e7a7ee0437c8f9f337dcb28aeb169ff292f47aaaeea975
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/recipes/qwen/qwen3.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: a3429fb9d977abdf70f77427702d8772507a951e2979464f2551e6318774d08c
- source: nvidia-nemo-megatron-bridge
  path: tests/unit_tests/recipes/qwen/test_qwen3_recipes.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 7656ed6c1c56df8355c246e3f243fb8100c296b8ca27315af56d898496edff14
- source: nvidia-nemo-megatron-bridge
  path: docs/training/entry-points.md
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: b2adf198c102593158c53b3c5dce1eb118655c54b117b41726bd77ea82d17665
- source: nvidia-nemo-megatron-bridge
  path: docs/training/mixed-precision.md
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 1eaaa5295132b8707a8188fa64b97d668ded87bf426bca03008c78dd9458c926
- source: nvidia-nemo-megatron-bridge
  path: docs/training/peft.md
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 4f5ea38bb3b03f603f0530370168ebad309238dc2b7ade8ab8cbd08ba9ef38d9
---

# Bridge：模型配方、Pipeline Provider 与 HF 权重映射

## 适配问题与配置入口

HF权重可读不意味着Megatron模型结构和训练数学相同。recipe组合provider、batch/seq、并行、optimizer、precision和数据；简写CLI或模型名称只是一层入口。以模型官方config/recipe、真实HCU脚本和resolved ConfigContainer为准，保留模型真实性及任务的初始化/训练阶段。

## Provider到Core/TE

`GPTModelProvider.provide`按pre/post-process、VPP stage、灵活PP布局构建MCoreGPTModel；layer spec可以是ModuleSpec或callable，默认local/TE/TE full layer选择不同模块。`_callable_spec_kwargs`按声明参数传vp_stage与provider自己的PP group rank，避免decentralized场景错误取global MPU。

MTP独立stage可能没有decoder layer，`mtp_block_spec`重新取得decoder spec并调用模型的`mtp_layer_spec_transform`。本轮最终`get_gpt_mtp_block_spec`调用仍只传vp_stage，不等同于上游[#6406](../../prs/NVIDIA-NeMo--Megatron-Bridge/PR-6406.md)提出的最终rank传递修复。该PR为特定已固定Core的CPU契约回归，不是所有GPU/decentralized组合已通过。

模型替换decoder后，还应确认低精度模块完成初始化。[#6140](../../prs/NVIDIA-NeMo--Megatron-Bridge/PR-6140.md)针对Qwen3VL replacement重新执行precision finish_init；不能仅检查顶层FP8 flag或TE包存在。

## AutoBridge映射与内存

`AutoBridge.from_hf_pretrained/from_hf_config→to_megatron_provider→get_model`连接模型结构，load/stream/export路径连接参数mapping。核对名称、QKV排列、column/row parallel分片、gated MLP gate/up、vocab padding、embedding tying、RoPE和special tokens；转换还受当前TP/PP/EP及模型family支持限制。

流式权重转换/分rank导出可降低完整权重同时物化的主存/显存峰值，但map/reduce和I/O有代价。没有读实际导出路径就不能估计峰值，更不能为了节省内存改权重dtype后省掉数值回归。PEFT初始化frozen base与adapter的load/save分开，LoRA/DoRA结构和训练参数集合明确。

## 测试与精度判断

recipe单测核对模型配置和并行字段，真实转换还需TP/PP边界、共享参数、MTP/多模态模型。roundtrip记录compared/skipped/missing/unexpected、绝对/相对误差和精度；再用固定输入logits、loss、梯度、optimizer step验证训练。量化反量化有损、skipFP8或宽松key策略不能称为bitwise/全模型正确。

## 诊断、回退与更新

模型初建失败先provider/spec与实际Core签名，权重错先mapping/layout，再precision初始化；loss错还要查数据/分母。退回支持的local/TE基础spec、可信HF/native权重和已验配方；不是随意缩dim避开错误。更新provider、Core builder、精度初始化、AutoBridge mapping和recipe时联动[总览](../bridge.md)与checkpoint专题。

## 固定证据与复核范围

- [src/megatron/bridge/models/gpt_provider.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/src/megatron/bridge/models/gpt_provider.py)
- [src/megatron/bridge/models/conversion/auto_bridge.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/src/megatron/bridge/models/conversion/auto_bridge.py)
- [src/megatron/bridge/recipes/qwen/qwen3.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/src/megatron/bridge/recipes/qwen/qwen3.py)
- [tests/unit_tests/recipes/qwen/test_qwen3_recipes.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/tests/unit_tests/recipes/qwen/test_qwen3_recipes.py)
- [docs/training/entry-points.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/docs/training/entry-points.md)
- [docs/training/mixed-precision.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/docs/training/mixed-precision.md)
- [docs/training/peft.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/docs/training/peft.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
