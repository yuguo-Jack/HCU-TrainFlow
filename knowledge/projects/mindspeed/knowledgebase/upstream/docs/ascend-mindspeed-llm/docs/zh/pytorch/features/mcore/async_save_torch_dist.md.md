---
id: doc-ascend-mindspeed-llm-256fc4d72195db4b048f
title: Ascend/MindSpeed-LLM / docs/zh/pytorch/features/mcore/async_save_torch_dist.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: 2fed626696175480ae1ab3342a94017301a25209
path: docs/zh/pytorch/features/mcore/async_save_torch_dist.md
raw_sha256: d0d40202b299e36e97b16cd67411951bf6fc4331a38aacadca62f2b71254567c
sources: []
generated_body_sha256: cbe33ca6fe13ea50d540b40474cf90a8f464a6f4a79229c7fc96df89f6db955f
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/zh/pytorch/features/mcore/async_save_torch_dist.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/zh/pytorch/features/mcore/async_save_torch_dist.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Async Save Torch Dist

## 使用场景

### 问题描述

在大规模训练中，checkpoint 保存通常会带来明显的训练停顿。
如果每次保存都阻塞训练主流程，吞吐会受到影响。

MindSpeed-LLM 基于 Megatron 分布式 checkpoint 语义，提供 `torch_dist` 格式的异步保存能力：主流程仅负责发起保存请求，后台执行分片写盘，训练可继续推进。

### 特性介绍

【核心能力】

本特性提供 `torch_dist` 格式 checkpoint 的异步保存能力：

- 主训练流程只负责构建并提交保存请求；
- 分片写盘在后台执行；
- 训练可继续推进，减少 checkpoint 带来的训练停顿。

【保存格式与保存方式】

当前 checkpoint 仅支持 `torch` 与 `torch_dist` 两种格式。
只有 `torch_dist` 格式下才支持异步保存。`torch` 格式只支持同步保存，会阻塞训练主流程。同时，`torch_dist` 还支持同步保存模式。
即 `torch_dist` 格式支持两种保存模式：

- 异步保存：主流程仅负责构建并提交保存请求，不阻塞训练主流程；
- 同步保存：主流程在保存完成后，才会继续执行后续训练步骤。

异步保存的时候会增加 CPU 占用，大规模模型和频繁保存场景建议走同步保存。

【异步保存流程】

开启 `--async-save` 后：

- 保存阶段通过 `schedule_async_save` 提交异步请求；
- checkpoint tracker 更新与 one_logger 成功事件放在 finalize 回调执行；
- 训练结束统一调用 `maybe_finalize_async_save(blocking=True, terminate=True)` 收敛未完成请求。

## 使用约束

【异步保存格式约束】

- `--async-save` 仅支持最终 checkpoint 格式为 `torch_dist`；
- 若处于 legacy `torch` 或其他分布式格式，将触发不支持的模式检查。

【使用场景约束】
本特性仅适用于预训练场景：

- 支持将权重以 `torch_dist` 格式异步保存；
- 保存后的权重可直接用于推理，或加载后继续预训练；
- 暂不支持 LoRA、微调、SFT 等下游任务。
