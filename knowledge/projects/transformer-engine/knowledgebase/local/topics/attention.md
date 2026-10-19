---
id: official-transformer-engine-wiki/attention
title: TE Attention：后端选择、cuDNN 调用与训练精度契约
engine: transformer-engine
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-20'
sources:
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/attention/dot_product_attention/dot_product_attention.py
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 967c475fa391f5d7748a9ea8f8cb5da7a109ed5efdb291174cd10ab63a55b201
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/attention/dot_product_attention/utils.py
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: a5d1abbcf7f9353c43f7fed7dbdc7780edd273c88b6c51b51e2e88ecacee2877
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/attention/dot_product_attention/backends.py
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 427fec57c9b8017590e262bb8a4efd7918ef758a218dbf155f784c446fcd9426
- source: nvidia-transformerengine
  path: transformer_engine/common/fused_attn/fused_attn_f16_arbitrary_seqlen.cu
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 7b75f80511848e748e593182fd5f370915683399e60c79b53b4df62d7e81e600
- source: nvidia-transformerengine
  path: tests/pytorch/attention/test_attention_backend_selection.py
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 351675d17a4fa6dabca0a0540c4b6c28ec6aa67bd9d78c207fee478a98d9ad90
- source: nvidia-transformerengine
  path: docs/examples/attention/attention.ipynb
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 055093bf03f8b79cbfc84abad66d282b4de86ab4672ffc402f1c927d2c2b065a
- source: nvidia-transformerengine-docs
  path: attention
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: 983e93a50785e09d921be543498398149788383692039e0076b9392f6a106dca
  url: https://docs.nvidia.com/deeplearning/transformer-engine/examples/attention/attention.html
  revision_kind: web-content-fingerprint
- source: nvidia-transformerengine
  path: transformer_engine/common/fused_rope/fused_mla_kv_rope_mxfp8.cu
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 3cf446a2dfa59c457822d64b5923d8bc897538819e9da89a26120bf2952ef272
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/csrc/extensions/apply_rope.cpp
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 937ae0f8c6c2032c8943e59957b2715a0c0062ccee234e60b04972fd98f24aa1
- source: nvidia-transformerengine
  path: tests/pytorch/attention/test_fused_mla.py
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: 9cfb37a1e346c013c89130925382f3f01a121c1de886f7a4c6c50542195c2e92
- source: nvidia-transformerengine
  path: tests/pytorch/attention/test_attention.py
  commit: eb3c860a4d3394b7eb5e21dba3021fa10782a52e
  sha256: f2dda7c79a38bdc4fb5b6b9ff9b2e523bfa64a6e3ee68af0751c16522b2c8b2d
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

HCU TE 能承接的接口先复用或补齐该仓；通用编译/cuDNN Frontend 的融合需求先查 Flash-Train 最新实现。详细的 graph、SDPA statistics、plan/workspace 说明见 [cuDNN Frontend attention](../../../../cudnn-frontend/knowledgebase/local/topics/attention.md)。backend 前向可运行并不能替代梯度、阶段 loss 和真实模型验证。

## 当前 FA4 分派与窗口语义

官方 `eb3c860a4d33` 将 FA2 的兼容上界更新为 `<2.8.5`；FA4 的建议组合则是 `flash-attn-4==4.0.0b33` 与 CUTLASS DSL 4.8.0。它们是该 NVIDIA 分支的依赖条件，不能据此升级 HCU 环境。

FA4 对 SM100/SM110、QK/V head_dim 均为256、且实际传 `seqused_q/k` 的 THD 路径按方向检查版本：forward 至少 b31，backward 至少 b33。THD all-gather 总会传该元数据，其他 THD 路径由 `pad_between_seqs` 决定。确定性且需要 backward 时，SM12x 和上述 D256 路径会排除 FA4；`eval()` 不会自动关闭 autograd。选择测试覆盖 compact/padding/all-gather、版本和前后向，而不是只验训练标志。

FA4 wrapper 只把 TE 的无界窗口 sentinel `-1` 转为 None，保留 `-8` 等其他负 offset；后者可表达空窗口，不能统一归为无界。FA2/FA3 继续原 sentinel。FA4 仍通过 `no_torch_dynamo` 保持 eager island，不把可导入解释成整图编译路径。

## MLA 的 KV/RoPE/MXFP8 融合入口

新增工具函数 `fused_mla_kv_rope_mxfp8` 沿 utils → PyTorch `apply_rope.cpp` → `nvte_fused_mla_kv_rope_mxfp8` → CUDA kernel，把 KV split、共享 key RoPE 与 row/column MXFP8 量化连接起来，省去 BF16 K/V 中间写回和重读。它返回原 SBHD 逻辑形状、尚未 BHSD-permute/GEMM-swizzle 的两个 MXFP8Tensor；不能直接替换要求另一 scale 布局的消费者，也不能由函数存在推断 DPA 已自动采用。

当前契约固定 DeepSeek-V3 的128维 non-RoPE key、64维 RoPE、128维 value，SM10.0+、BF16 KV/K-RoPE、偶数 heads；Python 包装要求序列长为128倍数。cos/sin 同为 BF16 或 FP32，K-RoPE 可为投影切片但需满足实际 stride/对齐。输出需两向 E4M3、非2D量化与 compact scales。源码按 Megatron MLA 的中间舍入点实现旋转，不能用单纯 FP32 等价代数替代 reference。

`test_fused_mla.py` 比较两套数据与两套 scale 的逐字节结果，覆盖 strided/contiguous K-RoPE、较长旋转表、零块/大值/NaN/Inf、非法形状、2D quantizer 拒绝和非当前设备。它提供局部量化融合的验收设计，尚不构成完整 MLA autograd、模型训练或本次硬件通过证据。

## 来源与版本复核

- [nvidia-transformerengine: transformer_engine/pytorch/attention/dot_product_attention/dot_product_attention.py](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/transformer_engine/pytorch/attention/dot_product_attention/dot_product_attention.py)
- [nvidia-transformerengine: transformer_engine/pytorch/attention/dot_product_attention/utils.py](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/transformer_engine/pytorch/attention/dot_product_attention/utils.py)
- [nvidia-transformerengine: transformer_engine/pytorch/attention/dot_product_attention/backends.py](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/transformer_engine/pytorch/attention/dot_product_attention/backends.py)
- [nvidia-transformerengine: transformer_engine/common/fused_attn/fused_attn_f16_arbitrary_seqlen.cu](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/transformer_engine/common/fused_attn/fused_attn_f16_arbitrary_seqlen.cu)
- [nvidia-transformerengine: tests/pytorch/attention/test_attention_backend_selection.py](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/tests/pytorch/attention/test_attention_backend_selection.py)
- [nvidia-transformerengine: docs/examples/attention/attention.ipynb](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/docs/examples/attention/attention.ipynb)
- [nvidia-transformerengine-docs: attention](https://docs.nvidia.com/deeplearning/transformer-engine/examples/attention/attention.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## 本次补充的实现与测试依据

- [nvidia-transformerengine: transformer_engine/common/fused_rope/fused_mla_kv_rope_mxfp8.cu](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/transformer_engine/common/fused_rope/fused_mla_kv_rope_mxfp8.cu)
- [nvidia-transformerengine: transformer_engine/pytorch/csrc/extensions/apply_rope.cpp](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/transformer_engine/pytorch/csrc/extensions/apply_rope.cpp)
- [nvidia-transformerengine: tests/pytorch/attention/test_fused_mla.py](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/tests/pytorch/attention/test_fused_mla.py)
- [nvidia-transformerengine: tests/pytorch/attention/test_attention.py](https://github.com/NVIDIA/TransformerEngine/blob/eb3c860a4d3394b7eb5e21dba3021fa10782a52e/tests/pytorch/attention/test_attention.py)
