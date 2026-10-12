---
id: doc-ascend-mindspeed-3aef6de927f9bbddd437
title: Ascend/MindSpeed / docs/zh/features/norm-recompute.md
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
path: docs/zh/features/norm-recompute.md
raw_sha256: a77e6298686e3a7ceabf9db21187d2d6be497492259c922eafe42bd3448b5447
sources: []
generated_body_sha256: 5a323f08fcd86e877efd45a762f7604b9a5b0e05e40e80dbdd0ae61baeb06625
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/norm-recompute.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/norm-recompute.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Norm重计算

## 背景与挑战

大模型训练过程中，往往会面临显存不足的问题。

## 解决方案

类似于激活函数重计算，本特性支持了Norm层的重计算，运用激活函数重计算特性中的checkpoint机制，对Norm层进行重计算处理。具体细节请参见文献[Accelerating the Training of Large Language Models using Efficient Activation Rematerialization and Optimal Hybrid Parallelism](https://www.usenix.org/conference/atc24/presentation/yuan)。

## 使用场景

主要用于训练场景，用户内存不足或要进一步节省内存时。

## 使用方法

需在训练脚本中加入以下参数配置：

```bash
--recompute-norm  # 开启Norm重计算
--recompute-norm-num-layers ${num}   # num表示Norm重计算的层数
```

> [!NOTE]
>
> * Norm重计算特性仅支持mcore分支，不支持legacy分支，即仅支持在开启`--use-mcore-models`时，通过`--recompute-norm`开启。
> * Norm重计算兼容激活函数重计算、全重计算同时开启。
>   * 同时开启时，仅支持`--recompute-method`设置为block。
>   * 同时开启时，将按照指定的全重计算和Norm重计算的层数做各自类型的重计算，即不会有一层既做全重计算又做Norm重计算。
> * 执行优先级是先计算全重计算层，后Norm重计算层。

## 使用效果

开启后可节省RMSNorm/LayerNorm层的输出激活内存，并且由于Norm计算速度较快，重计算后对整体性能影响较小。对于开启TP及SP的场景，由于该激活内存在TP域内已进行切分，开启后效果不明显，对于未使用TP及SP的模型可考虑使用。
