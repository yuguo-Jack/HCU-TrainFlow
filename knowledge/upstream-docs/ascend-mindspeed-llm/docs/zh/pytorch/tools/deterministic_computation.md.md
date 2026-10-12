---
id: doc-ascend-mindspeed-llm-2ab9bead7095a65ebb4f
title: Ascend/MindSpeed-LLM / docs/zh/pytorch/tools/deterministic_computation.md
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
path: docs/zh/pytorch/tools/deterministic_computation.md
raw_sha256: f0b19fde7a10bd8fe3243aa54438d30a3b19f45365e3058a5c4aad5b73a03e40
sources: []
generated_body_sha256: 8edc3c3ab7ff24f00ab9568f6fa16e6b4e3cfed1ac82932c94e1ae4bc7e73fda
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/zh/pytorch/tools/deterministic_computation.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/zh/pytorch/tools/deterministic_computation.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Ascend 确定性计算

## 使用场景

在训练过程中，各类随机因素会使得每次实验的训练过程并不完全一致，从而影响其LOSS曲线、性能曲线等无法完全重合。
然而，在重复实验与对比实验中有时需要确定性的计算结果，保证结果的可复现性。
为满足上述需求，引入了"确定性计算"功能，允许用户通过昇腾(Ascend)芯片确保多次训练结果的一致性，从而帮助性能调优、对照实验等工作。

## 使用方法

要启用此功能，在脚本中加入`--npu-deterministic`，并配置环境变量`export HCCL_DETERMINISTIC=true`。seed默认为1234，也可自行设定

## 使用效果

通过确定性计算功能，可保证同参数下多次实验具有相同的实验结果。

> 如果配置 HCCL_LOGIC_SUPERPOD_ID，集群通过 RoCE 通信时，集群拓扑关系发生变化，集合通信也会产生不同行为，通信算法的逻辑有区别，两者确定性方案不统一。
