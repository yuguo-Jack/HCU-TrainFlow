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
reviewed_on: '2026-11-18'
coverage: fixed source delta and actual consumer review; historical pins retained; no HCU runtime validation
sources:
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/gpt_provider.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 2354707c4c81b5e05c6e62e4613092c26e7271dd17aa293ace75d1bc736abd4f
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/conversion/auto_bridge.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 1634f53dfb7f086f73c467d980553a4483663cf61f48738d2103cff5319dd465
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/recipes/qwen/qwen3.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: a3429fb9d977abdf70f77427702d8772507a951e2979464f2551e6318774d08c
- source: nvidia-nemo-megatron-bridge
  path: tests/unit_tests/recipes/qwen/test_qwen3_recipes.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 17eb662c5f76eea64750db924ffecc880ec5812cfd3759574d69ce78bf53b2f1
- source: nvidia-nemo-megatron-bridge
  path: docs/training/entry-points.md
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: b2adf198c102593158c53b3c5dce1eb118655c54b117b41726bd77ea82d17665
- source: nvidia-nemo-megatron-bridge
  path: docs/training/mixed-precision.md
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 1eaaa5295132b8707a8188fa64b97d668ded87bf426bca03008c78dd9458c926
- source: nvidia-nemo-megatron-bridge
  path: docs/training/peft.md
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 4f5ea38bb3b03f603f0530370168ebad309238dc2b7ade8ab8cbd08ba9ef38d9
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/data/builders/dpo.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 71d0f8a0a5df6ec78a265aba09856091e1a1ea20740f20c28c9ec2bc0dfd700a
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/data/datasets/preference.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 2a65fca150e1e446860ef74cf5dee0d95c8be31f3727b0ae15f4b3a04c6621d0
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/data/datasets/preference_pair.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 9941077df8701925fa67f3e22529e63c9457b6a3e7954c715e75438d382e1aac
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/dpo.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 5dfd8b1be74bf4c640c3bcd40e2b21949911edafef4b4c66e8425fd96c56b050
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/dpo_step.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: b43ac87395326fddb286dc10263e7f4ae34ab89edc9b04914753fd28c69b2339
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/dpo_train.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 45c7e92be9a7c390efbcbaf800569987dc2e66a7877283e0de1250901ddecfb4
- source: nvidia-nemo-megatron-bridge
  path: scripts/dpo/score_reference_logprobs.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: e5aecc44e18c2043c2b528175eb5bb68f0d53eec02c553d39356cd6b21b2e119
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/recipes/qwen/h100/qwen3_moe.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: ff301c834676c0a4400d5e4d2bf5d099e78c10239b4791c6e8f985885b165835
- source: nvidia-nemo-megatron-bridge
  path: tests/unit_tests/training/test_dpo.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 8c3ffa19734d18d5534005910de94fae9e4bcdf2bfe19ef099c612486e18514f
- source: nvidia-nemo-megatron-bridge
  path: tests/unit_tests/training/test_dpo_step.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 9357229e0f65ee10123a5afbb362b8dd304e213b38df405c533f2728e24abf99
- source: nvidia-nemo-megatron-bridge
  path: tests/unit_tests/training/test_dpo_train.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 65ba708c63a7f8ca505437ba48312b923009c1c21fe2c67b0a4d65f5a61e15a4
- source: nvidia-nemo-megatron-bridge
  path: tests/unit_tests/models/test_adapter_export.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: 1cc29a148c9e232cb0ef6b40341988cf6f00f826f4e70078942ef1626e0e633f
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/conversion/modelopt_utils.py
  commit: 41af2dcf0dfd83c8933f588bb871b7f56dbd4368
  sha256: ecd7a9ceeaaf9161f3348921e82b4b0a64705d74e8b2064425cf2be58620612c
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/gpt_provider.py
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: da3c92f65431864e3079e09167dbcdb96e911731e0bff73d82795894977fd625
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/conversion/auto_bridge.py
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: 1cb276ce0f744b9124585b1a4d0042bf64057b315ad137a3f8602b3df4a8f3c1
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/conversion/modelopt_utils.py
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: 7eadcfe00408dd17f9758cac41ce940daf333dc4f620da32572470e3a6aae0f4
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/hf_pretrained/state.py
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: 1f52430a39ee3716d4be960f5be93814c83c5618931e27d280069670b03e352b
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/conversion/utils.py
  commit: 11d8b349d2daff3523bb9655b04f4ad33a9e9ea9
  sha256: 026e4a053606654a60059b72d2ed82c3877b2176995aeb47bfc0cbab293f9c3d
retrieved_on: '2026-11-18'
---

# Bridge：模型配方、Pipeline Provider 与 HF 权重映射

## 适配问题与配置入口

HF权重可读不意味着Megatron模型结构和训练数学相同。recipe组合provider、batch/seq、并行、optimizer、precision和数据；简写CLI或模型名称只是一层入口。以模型官方config/recipe、真实HCU脚本和resolved ConfigContainer为准，保留模型真实性及任务的初始化/训练阶段。

## Provider到Core/TE

`GPTModelProvider.provide`按pre/post-process、VPP stage、灵活PP布局构建MCoreGPTModel；layer spec可以是ModuleSpec或callable，默认local/TE/TE full layer选择不同模块。`_callable_spec_kwargs`按声明参数传vp_stage与provider自己的PP group rank，避免decentralized场景错误取global MPU。

MTP 独立 stage 可能没有 decoder layer，`mtp_block_spec` 仍重新取得 decoder spec 并调用 `mtp_layer_spec_transform`。固定 `11d8b349` 已新增显式 `pp_rank`，传到 callable spec 和最终 `get_gpt_mtp_block_spec`；旧 `41af2dcf` 尚缺最终 rank 传递的判断已过时。显式 rank 优先于 provider 的组，未显式给 callable 时才从 `_pg_collection.pp` 推导。普通 `provide` 的 MTP 调用仍未显式传该参数；无 MPU 的其他 builder 必须核对自己的调用点和所属 rank，不能把默认 None 当正确 rank。[#6406](../../upstream/prs/NVIDIA-NeMo--Megatron-Bridge/PR-6406.md)的旧 CPU 讨论范围也不等于所有 GPU/HCU 组合已通过。Provider 删除本地 `moe_grouped_gemm=False` 覆盖后继承所选 Core 默认值，升级要看最终 spec，不保留旧默认假设。

模型替换decoder后，还应确认低精度模块完成初始化。[#6140](../../upstream/prs/NVIDIA-NeMo--Megatron-Bridge/PR-6140.md)针对Qwen3VL replacement重新执行precision finish_init；不能仅检查顶层FP8 flag或TE包存在。

## AutoBridge映射与内存

`AutoBridge.from_hf_pretrained/from_hf_config` 之后应区分 legacy `to_megatron_provider` 与 builder-backed `get_model_config→get_model/build_distributed_models`；当前 H100 Qwen3 MoE recipe 已改走后一条，不能把 provider 对象字段当作所有模型的统一接口。load/stream/export 路径连接参数 mapping。核对名称、QKV排列、column/row parallel分片、gated MLP gate/up、vocab padding、embedding tying、RoPE和special tokens；转换还受当前TP/PP/EP及模型family支持限制。

流式权重转换/分rank导出可降低完整权重同时物化的主存/显存峰值，但map/reduce和I/O有代价。没有读实际导出路径就不能估计峰值，更不能为了节省内存改权重dtype后省掉数值回归。PEFT初始化frozen base与adapter的load/save分开，LoRA/DoRA结构和训练参数集合明确。

当前 `export_adapter_ckpt` 按模型 family 的 `USE_MODEL_CONFIG_FOR_CONVERSION` 选择 builder-backed ModelConfig/get_model 或 legacy provider 路线。前者设置 FP32 参数/pipeline 和 CPU 初始化，先装 base weights 再接 LoRA pre-wrap hook；target_modules 改由 model bridge 的映射解释，不能只按参数后缀猜所有家族的 PEFT 名称。text-only 与特殊多模态 processor 的加载也有独立分支。对应 mock 单测能检查选择和字段，真实分片、权重与 logits 仍需往返和训练验证。

## HF config、忽略集合与重复读取

`AutoBridge.from_auto_config` 在按 reference keys 投影之后，调用 `carry_rope_into_rope_parameters` 搬运 Megatron 的 RoPE 值，避免新版 Transformers 的 reference rope_parameters 覆盖模型差异。实际 helper 只改含 `rope_theta` 的平面字典；不同 scaling type 会替换旧 scaling 项、保留模型本身的 RoPE 参数，相等配置保持原样。按 attention type 嵌套的 rope_parameters 和不含该结构的配置原样返回，不能推导所有多模态/嵌套 RoPE 已解决。仍须比较合成 config、固定输入 logits 与数值。

普通 HF export 可由 model bridge hook 声明精确 `ignored_source_keys`，与 prefix/suffix 一起过滤预期源布局；它表达共享参数副本等有意不产出的 key，不是随意忽略 missing tensors 的许可。plain dtype 导出的可配 suffix 也校验为非空字符串 tuple。source map 原本不存在与“原有 key 全被过滤”走不同分支，后者不会把意外 tensor 当任意新模型导出，严格模式先排空 generator 再协调失败。

StateSource 的小张量只在重复读取时克隆入 cache，首读仅登记；复用 handle 的后续读在必要时用 fresh safe_open，避免调用方原地改写污染下次 refit。返回 cache 时仍 clone，相关开关和实际 source/shard 身份需记录。这是读权重的缓存策略，不改变权重正确性要求，也不保证所有转换路径为恒定内存。

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

2026-11-04 复核固定 `41af2dcf0dfd83c8933f588bb871b7f56dbd4368`，新增 adapter 导出内存/collective 契约：`save_hf_adapter` 的每个 rank 必须完整驱动 gather generator，仅 rank0 clone/保留完整 adapter 并写文件；rank0 转换/写入失败通过 status broadcast 通知其他 ranks。新增 mock 单测覆盖非零 rank 不留权重、不写文件、空导出和写入错误传播，不构成真实 TP/PP/EP 集群回归。共享 outer factor 的 serving layout 与 PEFT-loadable 展开形式仍不同。

ModelOpt 导出现在先 `build_hf_modelopt_export_plan`，再消费 prepared tasks；grouped API 要求各 rank 同序消费（含空组和 StopIteration），本地消费者完成后才进入下一组。它拒绝 unmerged adapters 和定制 HF export override；旧 quant_mode 参数式调用不能直接当作现接口。普通 HF 导出还区分真实量化状态 sidecars 与 plain weight dtype，config-only 路线会在 rank0 收集完整 CPU state，不能把所有路径都称为恒定内存 streaming。

未变依据：Qwen3 基础 recipe/测试、DPO 成对数据、reference 评分和 step/loss 原件仍支持原目标/分母约束。Provider、HF StateSource 与量化导出这次确有变化，不再沿用其“字节未变”结论；历史证据保留各自 commit，当前父 Core 锁也独立于其他官方 Core HEAD。

当前 `ModelOptExportPlan` 除 tasks/config/spec 还记录 `traced_rows`。定制映射可通过自己的 megatron_to_hf 对整数行列标签转换来证明完整行选择，只有该约束满足才能重用对应量化状态；维度置换、非整行布局及不支持拓扑仍拒绝，不能继续笼统称所有定制 QKV/Mamba 都不可导出。QKVG、concatenated QKV、GDN 各按自身布局拆分，GDN gate 保持未量化。量化 linear 输出必须是受支持的 `.weight`，KV/output 等无法带出的 quantizer 仍需显式检查。

grouped expert 新增的例外是 `oai_mxfp4_export` 的 OpenAI weight-only MXFP4：要求对应 experts 的量化/spec 一致，不允许部分 experts 留 BF16，且该格式的其他层保持 BF16；导出 `_blocks/_scales` 与匹配 config。一般 grouped HF experts 或任意 FP4 格式并未因此全部支持。plan prepare 仍检查 recipe/spec 没有改变，TP/EP 同序 collective 和当前权重布局不可省略；这里没有执行真实多 rank 量化导出。

## 2026-11-18 固定消费者

- [src/megatron/bridge/models/gpt_provider.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/src/megatron/bridge/models/gpt_provider.py)
- [src/megatron/bridge/models/conversion/auto_bridge.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/src/megatron/bridge/models/conversion/auto_bridge.py)
- [src/megatron/bridge/models/conversion/modelopt_utils.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/src/megatron/bridge/models/conversion/modelopt_utils.py)
- [src/megatron/bridge/models/hf_pretrained/state.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/src/megatron/bridge/models/hf_pretrained/state.py)
- [src/megatron/bridge/models/conversion/utils.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/11d8b349d2daff3523bb9655b04f4ad33a9e9ea9/src/megatron/bridge/models/conversion/utils.py)

## 固定证据与复核范围

- [src/megatron/bridge/models/gpt_provider.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/models/gpt_provider.py)
- [src/megatron/bridge/models/conversion/auto_bridge.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/models/conversion/auto_bridge.py)
- [src/megatron/bridge/recipes/qwen/qwen3.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/recipes/qwen/qwen3.py)
- [tests/unit_tests/recipes/qwen/test_qwen3_recipes.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/tests/unit_tests/recipes/qwen/test_qwen3_recipes.py)
- [docs/training/entry-points.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/docs/training/entry-points.md)
- [docs/training/mixed-precision.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/docs/training/mixed-precision.md)
- [docs/training/peft.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/docs/training/peft.md)

- [src/megatron/bridge/data/builders/dpo.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/data/builders/dpo.py)
- [src/megatron/bridge/data/datasets/preference.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/data/datasets/preference.py)
- [src/megatron/bridge/data/datasets/preference_pair.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/data/datasets/preference_pair.py)
- [src/megatron/bridge/training/dpo.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/training/dpo.py)
- [src/megatron/bridge/training/dpo_step.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/training/dpo_step.py)
- [src/megatron/bridge/training/dpo_train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/training/dpo_train.py)
- [scripts/dpo/score_reference_logprobs.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/scripts/dpo/score_reference_logprobs.py)
- [src/megatron/bridge/recipes/qwen/h100/qwen3_moe.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/src/megatron/bridge/recipes/qwen/h100/qwen3_moe.py)
- [tests/unit_tests/training/test_dpo.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/tests/unit_tests/training/test_dpo.py)
- [tests/unit_tests/training/test_dpo_step.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/tests/unit_tests/training/test_dpo_step.py)
- [tests/unit_tests/training/test_dpo_train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/tests/unit_tests/training/test_dpo_train.py)
- [tests/unit_tests/models/test_adapter_export.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/41af2dcf0dfd83c8933f588bb871b7f56dbd4368/tests/unit_tests/models/test_adapter_export.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
