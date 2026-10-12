---
id: doc-ascend-mindspeed-623a57e27e8944cd7188
title: Ascend/MindSpeed / docs/zh/features/npu_deterministic.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed
commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
path: docs/zh/features/npu_deterministic.md
raw_sha256: de52f93b77fd0e03bfd8d25cf9d9a223f386e2765d04927f284bd20a05cffc50
sources: []
generated_body_sha256: 73e2c3af6c54f2939799dd1c9305a8fad770f7b28a6094f741bba740df6881a7
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/npu_deterministic.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/npu_deterministic.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Ascend 确定性计算

## 背景与挑战

在训练过程中，各类随机因素会导致每次实验的训练过程并不完全一致，进而使得LOSS曲线、性能曲线等无法完全重合。
然而，在重复实验与对比实验中有时需要确定性的计算结果，保证结果的可复现性。

## 解决方案

为满足上述需求，引入了“确定性计算”功能，允许用户通过昇腾(Ascend)芯片确保多次训练结果的一致性，从而帮助性能调优、对照实验等工作。

## 使用场景

需要进行性能对比、特定场景复现时。

## 使用方法

要启用此功能，运行脚本时在脚本中加入`--npu-deterministic`参数即可。

## 使用效果

通过确定性计算功能，可保证同参数下多次实验具有相同的实验结果。
