---
id: engines/swift
title: MS-SWIFT：SFT、Megatron 接口与 RL 阅读入口
engine: swift
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: modelscope-ms-swift
  path: README.md
  commit: 0bd7b0aa1d3f1f0fdd8642ae19578420f578d9e1
  sha256: 4cf3ac10fe15d52a4bbf6886e1d158e10b202f04980a0be3e4050a33ba9fc942
- source: modelscope-ms-swift
  path: setup.py
  commit: 0bd7b0aa1d3f1f0fdd8642ae19578420f578d9e1
  sha256: 1a7fe144134dff38afa385c749c201d88827cea7692ba4007e58f9ccfd379275
---

# MS-SWIFT：SFT、Megatron 接口与 RL 阅读入口

## 组织与运行入口

仓库 `swift/` 是实现，`examples/` 和 `docs/` 是配方与说明，`tests/` 提供回归，`requirements/` 表达不同依赖组合。当前 README 区分主干 4.x 与 3.x release 分支，任务不能仅记录“安装了 swift”。官方 `swift sft`、`swift rlhf` 是两个重要入口；Megatron-SWIFT 又有不同训练后端。

## 适配顺序

先锁模型/模板/tokenizer 和数据格式，确认 padding、packing、loss mask、LoRA 或全参训练；再检查目标后端和 accelerator。保留 recipe 的解析配置与 import 路径。官方安装命令会引入平台相关依赖，HCU 使用经过匹配的 PyTorch/DTK 环境逐项核对，不能照搬 CUDA wheel。

## 性能与正确性

小模型 SFT 可能受数据处理或短 kernel 启动影响，先测真实 token 吞吐和阶段时间；Megatron 后端可沿官方 Megatron Wiki 深挖。LoRA 的低 rank GEMM、融合 optimizer、packing 与 compile 都需记录实际 shape。RL 还要测 rollout、权重同步、训练与 reward 各阶段及 idle。

## 交付及现有覆盖

本版提供官方 README/安装入口的内容级导航和训练契约，尚未完成每个模型/模板的源码专题。开始具体任务后由 Wiki update 补该模型数据编码、loss 与后端调用链；不能把入口登记解释成全引擎 HCU 适配已完成。

## 固定源码与更新范围

- [README.md](https://github.com/modelscope/ms-swift/blob/0bd7b0aa1d3f1f0fdd8642ae19578420f578d9e1/README.md)
- [setup.py](https://github.com/modelscope/ms-swift/blob/0bd7b0aa1d3f1f0fdd8642ae19578420f578d9e1/setup.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
