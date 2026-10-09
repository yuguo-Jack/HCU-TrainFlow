---
id: official-transformer-engine-wiki/attention
title: TE Attention：后端选择、cuDNN 调用与训练精度契约
engine: transformer-engine
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/attention/dot_product_attention/dot_product_attention.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 967c475fa391f5d7748a9ea8f8cb5da7a109ed5efdb291174cd10ab63a55b201
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/attention/dot_product_attention/utils.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 0e80d5f14a933de26e564e823eb86c1000221425f30832f0e4967ae95e2d48ed
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/attention/dot_product_attention/backends.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 97f332b619f1c710e84ec8799561da8eb0e8ddff34d608d6504c513718168492
- source: nvidia-transformerengine
  path: transformer_engine/common/fused_attn/fused_attn_f16_arbitrary_seqlen.cu
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 7b75f80511848e748e593182fd5f370915683399e60c79b53b4df62d7e81e600
- source: nvidia-transformerengine
  path: tests/pytorch/attention/test_attention_backend_selection.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: e0ee6f26e308ab0481f6bb7a12f88b1a1ffdf4a4a19f9e294ace495cab2de252
- source: nvidia-transformerengine
  path: docs/examples/attention/attention.ipynb
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 055093bf03f8b79cbfc84abad66d282b4de86ab4672ffc402f1c927d2c2b065a
- source: nvidia-transformerengine-docs
  path: attention
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: 983e93a50785e09d921be543498398149788383692039e0076b9392f6a106dca
  url: https://docs.nvidia.com/deeplearning/transformer-engine/examples/attention/attention.html
  revision_kind: web-content-fingerprint
---

# TE Attention：后端选择、cuDNN 调用与训练精度契约

## 调用链与选择条件

`DotProductAttention` 汇集模型参数，`utils.py:get_attention_backend` 依据运行条件筛选后端，`backends.py` 包装实际 FlashAttention、FusedAttention 和 unfused 路径。cuDNN fused attention 的底层可沿 `common/fused_attn/fused_attn_f16_arbitrary_seqlen.cu` 查看构图和执行。当前源码还允许插件替换部分选择/实现入口；实际 dispatch 必须从安装分支和 trace 验证。

后端选择受架构、cuDNN/flash-attn 版本、dtype、head_dim、布局、Q/KV 长度、mask/bias/dropout、训练反向、CP 以及 determinism 影响。`NVTE_FLASH_ATTN`、`NVTE_FUSED_ATTN`、`NVTE_UNFUSED_ATTN` 是官方选择开关，但设置为 1 不保证该后端可用。HCU 分支是否保留同名开关、如何解释，需查其实现。

## 训练问题对应的源码入口

| 现象 | 优先检查 |
| --- | --- |
| 明明开启 fused 但 kernel 数很多 | selector 排除条件、fallback、额外布局转换及 dropout/bias 分支。 |
| forward 对，backward 错 | O、softmax statistics、RNG、scale、causal alignment、cu_seqlens 是否对应同一次 forward。 |
| 长序列或变长模型失效 | THD/BSHD/SBHD 实际物理 stride、packed offsets、Q/KV 长度与支持矩阵。 |
| CP 后吞吐或 loss 异常 | `context_parallel.py`、通信 group、分块与 mask 边界，以及 RNG/重算一致性。 |
| 版本升级后性能下降 | selector、后端支持条件、计划/workspace 和 kernel 的版本变化，不能只比较 API 名。 |

## 对齐 NV 融合时保存什么

保存实际 shape、QKV 排列、GQA/MQA、mask 含义及方向、bias、dropout 概率/RNG、scale、输入/累积/output dtype、需要保留给 backward 的结果。HCU 接口尽量兼容现有模型调用；性能分析同时记录 fwd/bwd、布局转换及辅助 kernel，而非只看一个 attention kernel。

HCU TE 能承接的接口先复用或补齐该仓；通用编译/cuDNN Frontend 的融合需求先查 Flash-Train 最新实现。详细的 graph、SDPA statistics、plan/workspace 说明见 [cuDNN Frontend attention](../official-cudnn-frontend-wiki/attention.md)。backend 前向可运行并不能替代梯度、阶段 loss 和真实模型验证。

## 来源与版本复核

- [nvidia-transformerengine: transformer_engine/pytorch/attention/dot_product_attention/dot_product_attention.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/attention/dot_product_attention/dot_product_attention.py)
- [nvidia-transformerengine: transformer_engine/pytorch/attention/dot_product_attention/utils.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/attention/dot_product_attention/utils.py)
- [nvidia-transformerengine: transformer_engine/pytorch/attention/dot_product_attention/backends.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/attention/dot_product_attention/backends.py)
- [nvidia-transformerengine: transformer_engine/common/fused_attn/fused_attn_f16_arbitrary_seqlen.cu](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/common/fused_attn/fused_attn_f16_arbitrary_seqlen.cu)
- [nvidia-transformerengine: tests/pytorch/attention/test_attention_backend_selection.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/tests/pytorch/attention/test_attention_backend_selection.py)
- [nvidia-transformerengine: docs/examples/attention/attention.ipynb](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/docs/examples/attention/attention.ipynb)
- [nvidia-transformerengine-docs: attention](https://docs.nvidia.com/deeplearning/transformer-engine/examples/attention/attention.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码 main、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
