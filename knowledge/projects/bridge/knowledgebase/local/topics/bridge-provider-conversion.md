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
reviewed_on: '2026-10-20'
coverage: selected source delta and related discussion review; unchanged evidence reused; no HCU runtime validation
sources:
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/gpt_provider.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 2354707c4c81b5e05c6e62e4613092c26e7271dd17aa293ace75d1bc736abd4f
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/conversion/auto_bridge.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: cabf1fbd8954002d4dd852e80590ff3a9bb0efe2b0615f603b498d0b049abe94
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/recipes/qwen/qwen3.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: a3429fb9d977abdf70f77427702d8772507a951e2979464f2551e6318774d08c
- source: nvidia-nemo-megatron-bridge
  path: tests/unit_tests/recipes/qwen/test_qwen3_recipes.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 17eb662c5f76eea64750db924ffecc880ec5812cfd3759574d69ce78bf53b2f1
- source: nvidia-nemo-megatron-bridge
  path: docs/training/entry-points.md
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: b2adf198c102593158c53b3c5dce1eb118655c54b117b41726bd77ea82d17665
- source: nvidia-nemo-megatron-bridge
  path: docs/training/mixed-precision.md
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 1eaaa5295132b8707a8188fa64b97d668ded87bf426bca03008c78dd9458c926
- source: nvidia-nemo-megatron-bridge
  path: docs/training/peft.md
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 4f5ea38bb3b03f603f0530370168ebad309238dc2b7ade8ab8cbd08ba9ef38d9
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/data/builders/dpo.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 71d0f8a0a5df6ec78a265aba09856091e1a1ea20740f20c28c9ec2bc0dfd700a
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/data/datasets/preference.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 2a65fca150e1e446860ef74cf5dee0d95c8be31f3727b0ae15f4b3a04c6621d0
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/data/datasets/preference_pair.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 9941077df8701925fa67f3e22529e63c9457b6a3e7954c715e75438d382e1aac
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/dpo.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 5dfd8b1be74bf4c640c3bcd40e2b21949911edafef4b4c66e8425fd96c56b050
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/dpo_step.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: b43ac87395326fddb286dc10263e7f4ae34ab89edc9b04914753fd28c69b2339
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/dpo_train.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 45c7e92be9a7c390efbcbaf800569987dc2e66a7877283e0de1250901ddecfb4
- source: nvidia-nemo-megatron-bridge
  path: scripts/dpo/score_reference_logprobs.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: e5aecc44e18c2043c2b528175eb5bb68f0d53eec02c553d39356cd6b21b2e119
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/recipes/qwen/h100/qwen3_moe.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 0336271dd142bccec0246c0798ca4fb45023fb9f807d0f952cbb4d3556824671
- source: nvidia-nemo-megatron-bridge
  path: tests/unit_tests/training/test_dpo.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 8c3ffa19734d18d5534005910de94fae9e4bcdf2bfe19ef099c612486e18514f
- source: nvidia-nemo-megatron-bridge
  path: tests/unit_tests/training/test_dpo_step.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 9357229e0f65ee10123a5afbb362b8dd304e213b38df405c533f2728e24abf99
- source: nvidia-nemo-megatron-bridge
  path: tests/unit_tests/training/test_dpo_train.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 65ba708c63a7f8ca505437ba48312b923009c1c21fe2c67b0a4d65f5a61e15a4
- source: nvidia-nemo-megatron-bridge
  path: tests/unit_tests/models/test_adapter_export.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 92f6a641b9f1980a0da1da3b878768c3ba4e5bde49ac639783e6642194be79cb
---

# Bridge：模型配方、Pipeline Provider 与 HF 权重映射

## 适配问题与配置入口

HF权重可读不意味着Megatron模型结构和训练数学相同。recipe组合provider、batch/seq、并行、optimizer、precision和数据；简写CLI或模型名称只是一层入口。以模型官方config/recipe、真实HCU脚本和resolved ConfigContainer为准，保留模型真实性及任务的初始化/训练阶段。

## Provider到Core/TE

`GPTModelProvider.provide`按pre/post-process、VPP stage、灵活PP布局构建MCoreGPTModel；layer spec可以是ModuleSpec或callable，默认local/TE/TE full layer选择不同模块。`_callable_spec_kwargs`按声明参数传vp_stage与provider自己的PP group rank，避免decentralized场景错误取global MPU。

MTP独立stage可能没有decoder layer，`mtp_block_spec`重新取得decoder spec并调用模型的`mtp_layer_spec_transform`。本次固定 `gpt_provider.py` 的最终 `get_gpt_mtp_block_spec` 调用仍只传 vp_stage，不等同于 [#6406](../../upstream/prs/NVIDIA-NeMo--Megatron-Bridge/PR-6406.md)提出的最终rank传递修复。该讨论提供特定已固定Core的CPU契约回归，不是所有GPU/decentralized组合已通过。

模型替换decoder后，还应确认低精度模块完成初始化。[#6140](../../upstream/prs/NVIDIA-NeMo--Megatron-Bridge/PR-6140.md)针对Qwen3VL replacement重新执行precision finish_init；不能仅检查顶层FP8 flag或TE包存在。

## AutoBridge映射与内存

`AutoBridge.from_hf_pretrained/from_hf_config→to_megatron_provider→get_model`连接模型结构，load/stream/export路径连接参数mapping。核对名称、QKV排列、column/row parallel分片、gated MLP gate/up、vocab padding、embedding tying、RoPE和special tokens；转换还受当前TP/PP/EP及模型family支持限制。

流式权重转换/分rank导出可降低完整权重同时物化的主存/显存峰值，但map/reduce和I/O有代价。没有读实际导出路径就不能估计峰值，更不能为了节省内存改权重dtype后省掉数值回归。PEFT初始化frozen base与adapter的load/save分开，LoRA/DoRA结构和训练参数集合明确。

当前 `export_adapter_ckpt` 按模型 family 的 `USE_MODEL_CONFIG_FOR_CONVERSION` 选择 builder-backed ModelConfig/get_model 或 legacy provider 路线。前者设置 FP32 参数/pipeline 和 CPU 初始化，先装 base weights 再接 LoRA pre-wrap hook；target_modules 改由 model bridge 的映射解释，不能只按参数后缀猜所有家族的 PEFT 名称。text-only 与特殊多模态 processor 的加载也有独立分支。对应 mock 单测能检查选择和字段，真实分片、权重与 logits 仍需往返和训练验证。

## DPO：配对、reference 产物与实际分母

当前新增链为 `DPODatasetConfig/DPODatasetBuilder → PreferencePairDataset → preference_collate_fn → dpo_step.forward_step → dpo_loss`。chosen/rejected 必须保持偶/奇行交错且 pair_id 相同；tokens/labels 和 completion mask 同时位移。不能用普通 SFT 的 batch fetch 丢掉 pair_id、loss_multiplier、ref_logprob_sum、ref_num_tokens 等字段。无效样本保留零权重 stub 来稳定索引，实际 live pairs、stub 比例和有效 token 分别报告。

| 契约 | 当前实现及核验 |
| --- | --- |
| 离线 reference | `score_reference_logprobs.py` 使用同一 dataset builder、tokenizer 和求和函数，输出 pair_id 对齐的 logprob sums/token counts，再写 scoring_metadata。训练要求产物覆盖所有期望 pair_id，重复、缺失或额外 ID 拒绝；验证集另有独立产物。 |
| 配方与 loss | 要求 per-token NLL、`ddp.average_in_collective=False`、CP=1、无 MTP、训练/验证 batch 行数为偶数；一对为两行。PP 可用但按 microbatch 动态宽度交换 shape，不能把参考评分器强制 PP=1 理解成训练只能 PP1。 |
| 梯度与日志 | 逐 pair 对 policy/reference margin 计算 `-logsigmoid(beta × margin)`，乘 loss 权重后求和，可选混入 chosen SFT 项；返回分母为 live pair 数，而非普通 token 数。sum/average logprob 两种设置分别核对，stub 不计有效分母或梯度。 |
| padding 与性能 | pair 行右侧 padding、不做普通 SFT packing；拆分后的 microbatch会裁掉全 padding 尾部并满足 SP 的对齐倍数，scorer 可按长度/token budget 编排。其收益有 CPU 扫描、padding 和通信代价，不代表已测加速。 |

scoring metadata 比较数据源标识、split、tokenizer 名、长度、prompt/tools/template 选项、TP/SP 和 tokenization version；它不自动证明同名权重、数据文件或 tokenizer 内容未变，reference 权重版本与内容指纹仍需另存。EP/ETP 与评分时不同只告警，不能当作跨布局精度已验。产物通过检查后，先用同初态/同 pair 的 policy/reference margin 与梯度验证，再做阶段质量；没有本轮 HCU DPO 实测。

## 测试与精度判断

recipe单测核对模型配置和并行字段，真实转换还需TP/PP边界、共享参数、MTP/多模态模型。roundtrip记录compared/skipped/missing/unexpected、绝对/相对误差和精度；再用固定输入logits、loss、梯度、optimizer step验证训练。量化反量化有损、skipFP8或宽松key策略不能称为bitwise/全模型正确。

## 诊断、回退与更新

模型初建失败先provider/spec与实际Core签名，权重错先mapping/layout，再precision初始化；loss错还要查数据/分母。退回支持的local/TE基础spec、可信HF/native权重和已验配方；不是随意缩dim避开错误。更新provider、Core builder、精度初始化、AutoBridge mapping和recipe时联动[总览](../overview/bridge.md)与checkpoint专题。

## 固定证据与复核范围

- [src/megatron/bridge/models/gpt_provider.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/models/gpt_provider.py)
- [src/megatron/bridge/models/conversion/auto_bridge.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/models/conversion/auto_bridge.py)
- [src/megatron/bridge/recipes/qwen/qwen3.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/recipes/qwen/qwen3.py)
- [tests/unit_tests/recipes/qwen/test_qwen3_recipes.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/tests/unit_tests/recipes/qwen/test_qwen3_recipes.py)
- [docs/training/entry-points.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/docs/training/entry-points.md)
- [docs/training/mixed-precision.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/docs/training/mixed-precision.md)
- [docs/training/peft.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/docs/training/peft.md)

- [src/megatron/bridge/data/builders/dpo.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/data/builders/dpo.py)
- [src/megatron/bridge/data/datasets/preference.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/data/datasets/preference.py)
- [src/megatron/bridge/data/datasets/preference_pair.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/data/datasets/preference_pair.py)
- [src/megatron/bridge/training/dpo.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/training/dpo.py)
- [src/megatron/bridge/training/dpo_step.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/training/dpo_step.py)
- [src/megatron/bridge/training/dpo_train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/training/dpo_train.py)
- [scripts/dpo/score_reference_logprobs.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/scripts/dpo/score_reference_logprobs.py)
- [src/megatron/bridge/recipes/qwen/h100/qwen3_moe.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/recipes/qwen/h100/qwen3_moe.py)
- [tests/unit_tests/training/test_dpo.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/tests/unit_tests/training/test_dpo.py)
- [tests/unit_tests/training/test_dpo_step.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/tests/unit_tests/training/test_dpo_step.py)
- [tests/unit_tests/training/test_dpo_train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/tests/unit_tests/training/test_dpo_train.py)
- [tests/unit_tests/models/test_adapter_export.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/tests/unit_tests/models/test_adapter_export.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
