---
id: doc-ascend-mindspeed-40bbadfaf334a1809c49
title: Ascend/MindSpeed / docs/zh/features/verl-ckpt-acceleration.md
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
path: docs/zh/features/verl-ckpt-acceleration.md
raw_sha256: bd53bc1a5fc91ceab27ec0317964a09c86a21d0b35e3a79317be74d6129b30fb
sources: []
generated_body_sha256: 27aa474577519e8cec71af256ce53d19193092bc06383ae7528d072b574a42ee
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/verl-ckpt-acceleration.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/verl-ckpt-acceleration.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Verl+Megatron后端后训练加载和保存ckpt时间优化

## 背景与挑战

当前verl+megatron后端后训练场景下，save和load ckpt时间较长，影响训练效率。

## 解决方案

为突破上述问题针对原生megatron和torch的比较耗时严重的部分校验逻辑做了跳过处理，用户可以通过参数控制是否跳过这部分校验加速load和save ckpt。

## 使用场景

* verl+megatron后端进行后训练

## 使用方法

需在训练脚本中加入以下参数，即可开启ckpt load和save加速
`+actor_rollout_ref.actor.megatron.override_transformer_config.ckpt_acceleration=True`

## 使用效果

通过上述方式显著提高了verl+megatron后端load和save ckpt的效率，在qwen3-30b-dapo 16卡 * 2机场景下实测效果如下：
![verl-ckpt-acceleration.png](../figures/verl-ckpt-acceleration.png)
