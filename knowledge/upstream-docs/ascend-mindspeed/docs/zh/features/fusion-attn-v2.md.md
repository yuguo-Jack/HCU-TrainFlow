---
id: doc-ascend-mindspeed-0fd0dbe3e98d7cd12e17
title: Ascend/MindSpeed / docs/zh/features/fusion-attn-v2.md
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
path: docs/zh/features/fusion-attn-v2.md
raw_sha256: a4b07121770ed57ca2a1d2eb921c75cd2214db59aec851045774c1f8b88c2263
sources: []
generated_body_sha256: 0f227c4029edd25b23fb455169b947ee40cbed46ecd7a309a2b1f59ffc0fb96a
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/features/fusion-attn-v2.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/features/fusion-attn-v2.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# fusion_attention_v2

## 使用场景

本方法为FlashAttention的V2版本，对V1版本进行了一定功能拓展，当前仅支持特定场景如[ALiBi位置编码](./alibi.md)，默认关闭。

其它场景原则上与V1版本无差异，不建议主动开启。算子说明详情见[接口说明](../ops/fusion_attention.md)。

## 使用方法

设置`--use-fusion-attn-v2`即可调用该算法。

## 使用效果

基础效果等同于FlashAttention，特定场景如[ALiBi位置编码](./alibi.md)需手动开启。
