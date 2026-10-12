---
id: engines/llamafactory
title: LlamaFactory：SFT 工程、两代训练入口与显存优化指南
engine: llamafactory
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime
  execution
sources:
- source: hiyouga-llama-factory
  path: README.md
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 2d61d3ee9a0b7a099800b17b0be7a8ef034ed9b08f43cb32bdac17642cc823dd
- source: hiyouga-llama-factory
  path: pyproject.toml
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: d2d044de25f84d319338de30299437ee882650e2a998af50f617bfbb5964becf
- source: hiyouga-llama-factory
  path: examples/README.md
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 23e64b4732392b1f91106f588d0e0ab6f0a46fab5ce02f0a43e952091e208ab5
- source: hiyouga-llama-factory
  path: src/llamafactory/cli.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: d32b69e0b379718a9d0cf7bbf7032e6104f234cf53b13ad9e276a4a3fe7530d8
- source: hiyouga-llama-factory
  path: src/llamafactory/launcher.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 145a72df667f12b9fd59dc4e03cdc017a0e947ef6949fcf8b9bd545c572b43ec
- source: hiyouga-llama-factory
  path: src/llamafactory/train/tuner.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 192ba6c81096ac5fcd075d44ef9e79296558fc935cd941fc38c038432fe00711
- source: hiyouga-llama-factory
  path: src/llamafactory/train/sft/workflow.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: aaa1f92b66c4985fe1c1d47a6c28831a1cd0b107d77e3819c2ea174e37a1384b
- source: hiyouga-llama-factory
  path: src/llamafactory/train/sft/trainer.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 4016aa09576891d53f2f3ee8f0cd21cd0f5c80c8ee1f45ab964a00750253d7c9
- source: hiyouga-llama-factory
  path: src/llamafactory/hparams/parser.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 35616c3337fab6a34d22caced28907bddb5e8d01891826f466fe8db1c3c8813f
- source: hiyouga-llama-factory
  path: src/llamafactory/data/processor/supervised.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: f1b4b8db32179f7471e7c0bf45806533f8cabe8ade98d3a6b427d80a94b959cf
- source: hiyouga-llama-factory
  path: src/llamafactory/data/collator.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: d9c0c4d5583001c9e2f9825de7dbf2f57cd7c724d0b3c70b4e9cd61cda08edb2
- source: hiyouga-llama-factory
  path: src/llamafactory/model/loader.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: ed132ebc37129345f88c882cb928e3ca5294954e4040d4eb7d64324f38022ae9
- source: hiyouga-llama-factory
  path: src/llamafactory/model/adapter.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 27889b4a7a4eaa6c45d96a8cc344aa0c7910ac748256fe9b2e7ca3d10f339834
- source: hiyouga-llama-factory
  path: src/llamafactory/v1/launcher.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: ef8b225d7dfa8c55db98bcaab9b698db069518b379fb5d84abe6c7a5c94f442d
- source: hiyouga-llama-factory
  path: src/llamafactory/v1/trainers/sft_trainer.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 9fe8f9fbde544a0440a836a5a0e7f252ec408671ea27dbe6dc7933200441b00c
- source: hiyouga-llama-factory
  path: src/llamafactory/v1/core/base_trainer.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 6c7102d5196274cfedf7e0137f885be43499a28bf80f3447c29ae8d3db26dc79
- source: hiyouga-llama-factory
  path: src/llamafactory/v1/plugins/trainer_plugins/distributed/deepspeed.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: a2ef30911f43fcdc48ded55a4047eb7e28cca29a70b7e76d797b8b68970208aa
- source: hiyouga-llama-factory
  path: src/llamafactory/v1/core/utils/checkpoint.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: 3b15e7bda28b6d1f4d87fbbadfec0d74ec73df01272eac5d6c44d013b981e33e
- source: hiyouga-llama-factory
  path: tests_v1/plugins/model_plugins/test_chunk_loss.py
  commit: 1fded918ac4723ac9966363f51ed4500866c5d1d
  sha256: ca9e673b2f6fc19c53bb76547e17fb24d6cc18d2f36167cee6fae55e8ef1a20e
---

# LlamaFactory：SFT 工程、两代训练入口与显存优化指南

## 定位与入口边界

LlamaFactory 将模型/tokenizer、数据格式与对话模板、SFT/偏好训练、LoRA/量化和分布式 backend 组织为可配置工程。官方规范仓为 `hiyouga/LlamaFactory`，旧 `hiyouga/LLaMA-Factory` 是别名。当前固定提交 `1fded918ac4723ac9966363f51ed4500866c5d1d` 同时包含 legacy 与 v1，二者的数据对象、trainer、插件和配置字段不同。

`llamafactory.cli:main` 以 **`USE_V1`** 选择 launcher。默认 legacy 链的 `train` 按 stage 分派；v1 的 `sft/train` 进入新 `SFTTrainer`。因此一篇 v1 优化 PR 不能自动证明 legacy YAML 已具有同样功能。先记录实际入口和源码路径，再讨论兼容或性能。

深入专题：

- [SFT 模板、packing 与 attention/位置契约](../topics/sft-packing-and-multimodal.md)。
- [v1 Ulysses CP 与 chunked linear-CE](../topics/v1-cp-and-chunk-loss.md)。

## 工程目录导航

| 位置 | 职责 | 检索/排查入口 |
| --- | --- | --- |
| `cli.py`、`launcher.py`、`v1/launcher.py` | 双入口选择、torchrun/elastic 分派 | 启动到不同代码、rank、有效 env |
| `hparams/`、`v1/config/` | 模型/数据/训练参数解析与组合检查 | stage、cutoff、packing、CP、backend |
| `data/parser.py`、`converter.py`、`loader.py` | 数据集定义、字段转换、读取处理 | dataset_info、列映射、数据缺失 |
| `data/template.py`、`processor/`、`collator.py` | 对话模板、监督 label、packing、VLM/mRoPE | loss mask、跨样本泄漏、RoPE 长度错误 |
| `model/loader.py`、`adapter.py`、`model_utils/` | HF load、PEFT、attention、量化、checkpointing | trainable 参数、扩展选择、加载 OOM |
| `train/sft`、`dpo`、`ppo`、`rm` 等 | legacy 各训练目标及 trainer | 目标函数、reference model、生成评估 |
| `v1/core/{model_engine,data_engine,base_trainer}.py` | v1 渲染/数据、训练和状态 | 实际 batch、step、梯度与保存 |
| `v1/plugins/model_plugins/` | CP、chunk loss、PEFT、kernel 等 | 模型改写的触发和数值/输出限制 |
| `v1/plugins/trainer_plugins/distributed/` | DeepSpeed/FSDP2 等分布式封装 | optimizer step 所有权、参数分片/保存 |
| `examples/`、`tests/`、`tests_v1/` | YAML、legacy/v1 分层回归 | 针对当前入口找配方与测试，避免混用 |

更多文件见 [完整源码目录](../../upstream/source-map/hiyouga-llama-factory.md)。

## 安装与版本依赖

当前 [pyproject.toml](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/pyproject.toml)要求 Python≥3.11，核心约束包含 PyTorch≥2.4、Transformers 4.55.0–5.8.0 且排除 4.57.0/5.6.0，以及 Accelerate/PEFT/TRL 区间。README 的推荐版本表和个别新模型说明可能不同；实际安装优先核对目标 commit 的依赖配置、模型实现要求及已验证 HCU 配方，不能随意用 DISABLE_VERSION_CHECK 代替兼容验收。

源码安装入口为 `python -m pip install -e .`，可选能力按 [README](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/README.md)的对应 requirements 安装。DeepSpeed、attention、量化和 fused kernel 是额外运行能力，导入包后仍需检查设备扩展与真实加载路径。训练场景不因安装了推理量化包就自动具有其训练后向支持。

启动器可根据设备数或 `FORCE_TORCHRUN` 转为 torchrun，多机字段为 `NNODES/NODE_RANK/NPROC_PER_NODE/MASTER_ADDR/MASTER_PORT`。v1 还支持 elastic rendezvous 参数；其 `env/version` 分支当前会报 NotImplementedError，不能在自检中把这些命令列成已实现工具。官方 launcher 默认调整 allocator/NCCL 相关 env，现场要与 HCU 分支/site 配方核对实际有效值。

## 模型、数据与运行配方

legacy 典型入口：`llamafactory-cli train path/to/model_recipe.yaml`；v1 使用 `USE_V1=1` 与 `sft`/对应新配置，或模块入口 `python -m llamafactory.v1.trainers.sft_trainer`。命令用于辨识官方路径，真实 HCU 执行先选兼容环境和已有模型脚本。

配方要记录 model revision、tokenizer/processor、template、finetuning 类型、冻结参数、quantization、precision、cutoff、数据字段转换、`train_on_prompt/mask_history`、packing、batch/accumulation、backend 和 checkpoint。legacy 的 [Qwen3 LoRA ZeRO-3 示例](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/examples/train_lora/qwen3_lora_sft_ds3.yaml)只说明一组字段，不能作为任何模型/设备的默认。

`SupervisedDatasetProcessor` 通过 template 编码多轮 prompt/response；`train_on_prompt` 与 `mask_history` 决定哪些 label 为 IGNORE_INDEX。多模态输入先由 mm plugin 替换/展开；长度截断也会改变实际监督目标。训练前打印一份 input/valid labels，确认处理后的数据，而不是只看原 JSON 字段。

## 调用链与性能机制

legacy：launcher → `run_exp`/参数解析 → `run_sft` → tokenizer/template → dataset → model/adapter → `SFTDataCollatorWith4DAttentionMask` → `CustomSeq2SeqTrainer.train`。attention implementation 与 neat-packing/block-diagonal 配置在 collator 相遇；生成式评估走另一条路径。

v1：launcher → `run_sft` → `DistributedInterface` → `DataEngine/ModelEngine` → `SFTTrainer` → `BaseTrainer.fit`。chunk-loss 在 distributed wrapping 前安装；CP loss 的 shift/shard/汇总由模型插件处理，base loop 再按有效训练 token/DP 和累积窗口缩放。

| 优化机制 | 值得用的情况 | 代价与限制 |
| --- | --- | --- |
| packing/neat packing | 短样本 padding 浪费较大 | 样本隔离、position/mRoPE、FA2/SDPA 路径不同；neat FA2 有 batch/model 限制 |
| v1 CP/Ulysses | 长序列激活需要跨卡分摊 | attention Q/K/V all-to-all、mask 统一、encoder 仍复制；并非所有 tensor 按序列分片 |
| chunked linear-CE | vocabulary logits 成为峰值显存热点 | token 分块重复 launch，FP32 head-grad 累积；要求 plain Linear 与原样 logits 输出 |
| activation checkpointing、ZeRO/FSDP/offload | 权重/激活/optimizer 超限 | 重算/参数 gather/主机 copy，测保存和切换峰值 |
| LoRA/量化 | 训练参数少或权重存储紧张 | 基础权重仍需驻留，merge/导出产生副本；实际 HCU 后端支持独立核验 |

优化先按 trace 定位数据等待、attention、MLP、logits/CE、optimizer、通信或保存，再以原模型语义比较 step 吞吐/有效 token 和峰值显存。CP/chunk loss/梯度累积改变之后同时回归数值，不用更短序列或删评估阶段的吞吐与原任务混比。

## 梯度、保存与恢复

v1 DeepSpeed 通过 Accelerate 的 `DeepSpeedPlugin` 初始化。`backward` 在最后 microbatch 的 sync 边界可能已经调用 engine.step；base trainer 不能再额外执行 optimizer.step。`auto` ZeRO-3 bucket 可从 text config hidden size 填充，VLM 顶层缺 hidden_size 时不能随意猜值。

v1 checkpoint coordinator 和 backend 保存 model/optimizer/trainer state；`save_model`/HF export 与 resume checkpoint 职责不同。DeepSpeed `save_checkpoint` 总保存 Accelerate 状态，按配置额外导出 HF；只留 HF 权重不能据此声明 optimizer/data/RNG 恢复。恢复前确认模型、adapter、分布式布局和当前保存方式兼容。

## 诊断与分层回归

| 症状 | 排查顺序 |
| --- | --- |
| loss 改变/监督目标减少 | 数据列/模板 → label mask/截断 → packing/shift → CP 或 trainer 分母 → 下游算子 |
| RoPE 长度错误 | pad-to-multiple 与 position IDs 长度 → packed/VLM boundaries → 实际 attention backend |
| CP collective 卡住 | 所有 rank mask 分支 → process group/sequence divisibility → all-to-all 与模型 hook |
| 加载/保存 OOM | 权重物化与 adapter merge → ZeRO gather → 保存副本、host memory，而非仅 train peak |
| 两次 optimizer update/梯度异常 | 实际 backend、Accelerate sync boundary、base loop 与 custom optimizer |

回归从模板/processor/collator、单模型输出与梯度、目标 distributed backend、保存/恢复逐级进行。当前官方 [collator tests](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/tests/data/test_collator.py)、[packing tests](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/tests/model/model_utils/test_packing.py)、[v1 chunk loss tests](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/tests_v1/plugins/model_plugins/test_chunk_loss.py)和 [v1 Ulysses tests](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/tests_v1/plugins/model_plugins/test_ulysses_cp.py)给出对应契约；本轮未在 HCU 运行。

## 教程、PR 与更新边界

官方入口：[教程](https://llamafactory.readthedocs.io/en/latest/)、[examples](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/examples/README.md)、[Releases](https://github.com/hiyouga/LlamaFactory/releases)、[Issues/功能规划](https://github.com/hiyouga/LlamaFactory/issues)、[PR](https://github.com/hiyouga/LlamaFactory/pulls)。已收录 [PR #10762](../../upstream/prs/hiyouga--LlamaFactory/PR-10762.md) 涉及 v1 multimodal Ulysses 与 chunk loss，必须和当前最终实现及 tests_v1 一起读。

检索 `wiki-search "Ulysses chunk loss" --engine llamafactory`；本地不足时线上 PR→固定源码。`wiki-update PROJECT hiyouga-llama-factory` 联动 legacy 与 v1、入口 switch、模型/数据/分布式插件、两个专题和相关测试。main、release、HCU 分支与任务已测分别登记；README 的支持表不能代替当前模型/backend 的实际验证。
