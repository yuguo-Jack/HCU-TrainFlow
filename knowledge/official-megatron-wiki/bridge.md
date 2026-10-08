---
id: official-megatron-wiki/bridge
title: Megatron Bridge：配方、模型转换与训练配置
engine: bridge
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-nemo-megatron-bridge
  path: README.md
  commit: 4778c23cc495adc78536be95f23964b13abfddb4
  sha256: 07f79fce9d8263da0e5b50e7c91ee25582da66c8af8ae1a07d0a1687c3b5354b
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/config.py
  commit: 4778c23cc495adc78536be95f23964b13abfddb4
  sha256: b4057ebe292c3e744784193dab85dbd019c85caa9524fea900526b6d016e6956
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/pretrain.py
  commit: 4778c23cc495adc78536be95f23964b13abfddb4
  sha256: 28a0fec822239d825da13838dcb6d86ee4b6ac13a52865bb351dc668e59225bf
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/gpt_provider.py
  commit: 4778c23cc495adc78536be95f23964b13abfddb4
  sha256: 2bf0ffcdaca932a83e5a141b0af982fc453c321076af620405931c9c7ba0d77f
- source: nvidia-nemo-megatron-bridge
  path: docs/training/communication-overlap.md
  commit: 4778c23cc495adc78536be95f23964b13abfddb4
  sha256: 859943b891cd2eefe537fe433c40e7a7ba0fcca702f6ecf44ccf1f9075e4ddde
---

# Megatron Bridge：配方、模型转换与训练配置

## 目录与调用

`src/megatron/bridge/models` 包含 provider 与模型接入；`training/config.py` 汇总配置，`training/pretrain.py` 驱动 pretrain 生命周期；finetune 另有入口。配方、权重转换和 Core 训练实现分层阅读，避免将转换成功视为训练语义一致。

## 适配检查

转换记录 tensor 名称、分片轴、QKV 排列、GQA/MQA、embedding tying、RoPE、特殊 token 以及精度。先做转换前后 forward，再验证梯度和短训练。SFT 另外对齐 loss mask、packing 和 tokenizer 模板。

## overlap 配置边界

Bridge 的 CommOverlapConfig 与 model 配置共同决定 TP/DP/PP/CP/EP 路径。当前通信指南明确提示多种特性存在组合限制。配置值、下传 Core 参数、TE 支持与实际 trace 四处应相互对应；silent disable 不能算候选覆盖。

## 安装和运行

读取本提交 pyproject 及 recipe 依赖，采用与 Core/TE 匹配的环境。先构造并打印解析后的配置，再在任务分配资源内运行官方对应模型示例。运行命令应由当前 recipe 生成并锁定，而不是用一个覆盖所有模型的固定命令。

## 更新

Bridge 与 LM 独立跟踪 ref/commit。配置字段重命名、provider 输出或 checkpoint 转换改变，会同时影响 prepare、optimize 和恢复指南，不能只更新 Wiki 总览。

## 固定源码与更新范围

- [README.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/4778c23cc495adc78536be95f23964b13abfddb4/README.md)
- [src/megatron/bridge/training/config.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/4778c23cc495adc78536be95f23964b13abfddb4/src/megatron/bridge/training/config.py)
- [src/megatron/bridge/training/pretrain.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/4778c23cc495adc78536be95f23964b13abfddb4/src/megatron/bridge/training/pretrain.py)
- [src/megatron/bridge/models/gpt_provider.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/4778c23cc495adc78536be95f23964b13abfddb4/src/megatron/bridge/models/gpt_provider.py)
- [docs/training/communication-overlap.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/4778c23cc495adc78536be95f23964b13abfddb4/docs/training/communication-overlap.md)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
