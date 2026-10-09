---
id: engines/llamafactory
title: LlamaFactory：SFT 数据语义、后端与显存优化
engine: llamafactory
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
coverage: selected implementation chain, not all models or backends
sources:
- source: hiyouga-llama-factory
  path: src/llamafactory/launcher.py
  commit: ce9dc9e072f80fa3abe0989d4ab90da25f083438
  sha256: 145a72df667f12b9fd59dc4e03cdc017a0e947ef6949fcf8b9bd545c572b43ec
- source: hiyouga-llama-factory
  path: src/llamafactory/train/sft/workflow.py
  commit: ce9dc9e072f80fa3abe0989d4ab90da25f083438
  sha256: aaa1f92b66c4985fe1c1d47a6c28831a1cd0b107d77e3819c2ea174e37a1384b
- source: hiyouga-llama-factory
  path: src/llamafactory/hparams/parser.py
  commit: ce9dc9e072f80fa3abe0989d4ab90da25f083438
  sha256: 35616c3337fab6a34d22caced28907bddb5e8d01891826f466fe8db1c3c8813f
- source: hiyouga-llama-factory
  path: src/llamafactory/train/sft/trainer.py
  commit: ce9dc9e072f80fa3abe0989d4ab90da25f083438
  sha256: 4016aa09576891d53f2f3ee8f0cd21cd0f5c80c8ee1f45ab964a00750253d7c9
- source: hiyouga-llama-factory
  path: tests/train/test_sft_trainer.py
  commit: ce9dc9e072f80fa3abe0989d4ab90da25f083438
  sha256: e49ad1ef3241eb34fd8bacad0273ab97279abdf44cf86a1b8f175f289fd16750
- source: hiyouga-llama-factory
  path: examples/train_lora/qwen3_lora_sft_ds3.yaml
  commit: ce9dc9e072f80fa3abe0989d4ab90da25f083438
  sha256: b18c6f2a61e4251e01277aeff6949f32a0562e56c4a81c8bd1bf01ed08647d0e
- source: hiyouga-llama-factory
  path: src/llamafactory/train/tuner.py
  commit: ce9dc9e072f80fa3abe0989d4ab90da25f083438
  sha256: 192ba6c81096ac5fcd075d44ef9e79296558fc935cd941fc38c038432fe00711
---

# LlamaFactory：SFT 数据语义、后端与显存优化

## 定位与目录

CLI 位于 `src/llamafactory/launcher.py`，参数解析在 `hparams`，训练阶段分派在 `train/tuner.py`，SFT 位于 `train/sft`。模型加载、模板和数据处理是独立层；`examples` 提供训练 YAML，`tests` 承担相应契约检查。官方仓已由 hiyouga/LLaMA-Factory 迁移到 hiyouga/LlamaFactory；旧引用保留历史意义，更新使用规范地址。

## SFT 调用链与 loss 契约

`run_sft` 先加载 tokenizer、修正 template，再生成 dataset，随后加载 model。`SFTDataCollatorWith4DAttentionMask` 接收 loss padding、packing、block diagonal attention 与实际 attention implementation；最后构造 `CustomSeq2SeqTrainer`。这说明模板、标签掩码和 attention backend 会共同影响结果，不能只验证一个 attention kernel 的前向误差。

`ignore_pad_token_for_loss` 决定 label padding，`neat_packing` 和 attention mask 决定样本边界。吞吐要同时给 processed tokens 与 effective tokens，防止 padding 增多看起来更快。生成式评估与训练 loss 有不同代码路径；prediction 的 padding_side 切换不应混同训练行为。

## 安装、启动与回归

从当前 README/依赖配置确认 Transformers、PEFT、DeepSpeed、attention 扩展的组合，优先用 HCU 工程现成环境和启动 YAML。`examples/train_lora/qwen3_lora_sft_ds3.yaml` 是本轮保留的具体入口示例：用来核对字段及 backend 关系，不直接作为任意模型的可执行配方。实际启动前保存解析参数、数据模板、tokenizer、模型 revision 和 backend 选择。

`tests/train/test_sft_trainer.py` 在本轮快照覆盖包括数据 shuffle 的行为；它不是全套精度证明。任务回归应补 template/tokenization、collator mask、LoRA trainable 参数集合、单步更新、保存加载和阶段 loss。缩 layer 时保留 hidden/head/sequence 等其余模型结构条件，单独标记与完整模型的区别。

## 性能与内存方向

按数据处理、H2D、attention、MLP、optimizer、保存分层归因。packing 的收益不能通过改变 label 有效范围取得；activation checkpointing 增加重算，ZeRO/offload 可能让计算等待主机。LoRA 还应计入基础权重、adapter、optimizer 和 merge/unmerge 的瞬时副本。官方 PR #10762 涉及 Ulysses CP 和 chunk loss，属于进一步读当前实现、测试与支持条件的入口，不表示旧版 CLI 已具备全部功能。

## 常见问题和边界

loss 异常先看模板、IGNORE_INDEX、label shift、packing 和有效 token 分母，再追 trainer 的 loss hook 和下游实现；OOM 要区分加载、训练、评估生成和保存阶段。不要仅通过关掉评估或减少序列长度消除问题后宣称同任务优化。仓内新旧实现可能并存，PR 的 v1 路径不能假定自动覆盖 legacy SFT 入口。

## 固定源码与符号导航

| 文件 | 本轮源码中可追查的入口（非全部符号） |
| --- | --- |
| [src/llamafactory/launcher.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/launcher.py) | `launch` |
| [src/llamafactory/train/sft/workflow.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/sft/workflow.py) | `run_sft` |
| [src/llamafactory/hparams/parser.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/hparams/parser.py) | `read_args`, `get_ray_args`, `get_train_args`, `get_infer_args`, `get_eval_args` |
| [src/llamafactory/train/sft/trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/sft/trainer.py) | `CustomSeq2SeqTrainer`, `create_optimizer`, `create_scheduler`, `compute_loss`, `prediction_step`, `save_predictions` |
| [tests/train/test_sft_trainer.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/tests/train/test_sft_trainer.py) | `DataCollatorWithVerbose`, `test_shuffle` |
| [examples/train_lora/qwen3_lora_sft_ds3.yaml](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/examples/train_lora/qwen3_lora_sft_ds3.yaml) |  |
| [src/llamafactory/train/tuner.py](https://github.com/hiyouga/LlamaFactory/blob/ce9dc9e072f80fa3abe0989d4ab90da25f083438/src/llamafactory/train/tuner.py) | `run_exp`, `export_model`, `Worker` |

## 教程、PR 与继续搜索

- [全仓目录和固定文件入口](../source-maps/hiyouga-llama-factory.md)：没有本地专题时按模块继续读源码。
- [上游教程原文目录](../upstream-docs/hiyouga-llama-factory/)：保留来源内容，链接相对位置以原站为准。
- [PR #10762：[v1] Support multimodal Ulysses CP and memory-efficient chunk loss for SFT](../prs/hiyouga--LlamaFactory/PR-10762.md)：正文、review、diff 与 head/base 源码。

检索示例：`wiki-search "关键符号或问题" --engine llamafactory`。本地结果不足，使用 `wiki-search-pr "简短英文问题词" --engine llamafactory`，再 `wiki-pr OWNER/REPO NUMBER`、`wiki-code OWNER/REPO FULL_SHA PATH` 追实际调用者、被调底层库和测试。普通查阅只写私有缓存。

## 更新和验收边界

运行 `wiki-update PROJECT hiyouga-llama-factory` 检查完整目录、新文档、PR 讨论与已监测源码；分页或网络失败必须续采。变更后联动本页、同仓专题/案例、调用方与依赖；源码已 merge、软件已发布、HCU 已适配和当前任务已验证分别登记。本页为选定实现的代码阅读和操作建议，没有在 HCU 执行上述测试，也未覆盖所有模型。实际任务的版本、性能、显存、失败尝试和阶段 loss 记录进入私有经验 Wiki。
