---
id: official-transformer-engine-wiki/cases/rmsnorm-mxfp8-fusion
title: 案例：RMSNorm 与 MXFP8 量化融合的调用、布局和数值边界
engine: transformer-engine
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tests-reviewed
runtime_validated: false
reviewed_on: '2026-10-12'
sources:
- source: nvidia-transformerengine
  path: transformer_engine/common/normalization/rmsnorm/rmsnorm_api.cpp
  commit: 2e959f352c8e2d4b2709e6775867f2c7494656f3
  sha256: 1383ee108b6ad04f51ff14b816f3966875acaac919dff6daa4e33f100d4f037f
- source: nvidia-transformerengine
  path: transformer_engine/common/normalization/rmsnorm/rmsnorm_fwd_mxfp8.cu
  commit: 2e959f352c8e2d4b2709e6775867f2c7494656f3
  sha256: 8910abcd3d930ab1ac47dbebd045f0727d54931f528baf6e778f7abe7fb62c3f
- source: nvidia-transformerengine
  path: tests/pytorch/mxfp8/test_mxfp8_rmsnorm_fwd.py
  commit: 2e959f352c8e2d4b2709e6775867f2c7494656f3
  sha256: 52d1857a9a41e2a21a94957e82f9c4d3f1c82e5a41059c8180fb98f848385b2c
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/csrc/extensions/normalization.cpp
  commit: 2e959f352c8e2d4b2709e6775867f2c7494656f3
  sha256: 63b73d6823b013daf2c29d55ce1aa7be1849b59c43a74d476b15e8defef2d349
pr_sources:
- pr-nvidia--transformerengine-3657
---

# 案例：RMSNorm 与 MXFP8 量化融合的调用、布局和数值边界

## 问题与收益假设

训练中 RMSNorm 后接低精度 GEMM，若先产生全精度归一化中间量，再分别量化 rowwise/columnwise 表示并重排 scale，会产生额外读写和 launch。官方 [PR #3657](https://github.com/NVIDIA/TransformerEngine/pull/3657) 把归一化与 MXFP8 输出组织到同一条实现路径，目标包括直接产生 GEMM 所需 scale 布局。

这里的“融合”不表示整个调用只有一个 kernel。实现先计算每行 rsigma，再按 tile 输出归一化并量化的结果；使用 SM margin 时还可能分块 launch。判断收益应看整段 RMSNorm→量化→scale 重排→GEMM 的时间和字节流量，不能只数 Python 调用。

PR 的独立 review 曾要求补充 profiling，并质疑该 kernel 的速度上限估算。这个讨论不能解释为实测结论，也不能因 PR 已合入就宣称它在所有 shape 上优于 cuDNN；应把 kernel 自身、免去 scale 重排的收益以及后续 GEMM 一并对照。完整讨论见[保留的 PR 来源页](../../upstream/prs/NVIDIA--TransformerEngine/PR-3657.md)。

## 分发与实现链

`pytorch/csrc/extensions/normalization.cpp` 根据 quantizer/输出布局准备 tensor → `nvte_rmsnorm_fwd` 的 `rmsnorm_api.cpp` → `is_supported_by_te_rmsnorm_fwd_mxfp8` → `rmsnorm_fwd_mxfp8` / `launch_rmsnorm_fwd_mxfp8` → rsigma 与 tile 量化 kernel。

MXFP8 输出且实现支持时，默认可以走 TE 路径；显式请求 cuDNN 会影响普通布局的选择。**GEMM-swizzled scale 输出要求 TE 支持**，不满足时会报错，而不是偷偷换成不同布局。源码保留 workspace-query 协议：查询返回一个字节的占位大小，不能由此推断实现需要一整块中间激活。

| 条件 | 源码约束与原因 |
| --- | --- |
| 硬件 | 检查 `is_supported_by_CC_100()`，是 NVIDIA 目标条件，不等于任何 HCU gfx 能力 |
| 行列 | 非空且均为 128 的倍数，并有整数/网格上限；完整 tile 避免 scale padding 歧义 |
| 输入与 gamma | FP32/BF16/FP16；gamma 的 zero-centered 及加一精度约定需要一致 |
| 输出 | E4M3/E5M2 的 rowwise/columnwise 表示，两者同时存在时 dtype 必须一致 |
| scaling | 当前融合输出为 1D block scaling；2D quantization 另走 normalize 后再量化路径 |
| 调度 | SM margin 改变每次 launch 的行块，offset 必须覆盖 data 和两套 scale 布局 |

## 数值不是任意 BF16 中间量参考

测试先校验 `rsigma = rsqrt(mean(x.float()**2)+eps)`，再以 FP32 归一化结果构造 MXFP8 reference。rowwise/columnwise 数据字节、scale 和可选 swizzle 分别比较；若参考先把归一化结果舍入到 BF16，可能改变量化边界，不是同一契约。

`test_rmsnorm_fwd_mxfp8` 覆盖输入 dtype、两种 FP8 输出、zero-centered gamma、GEMM scale 格式；`test_rmsnorm_fwd_mxfp8_sm_margin` 对照全部 SM 与保留到一个 SM 的输出；2D case 明确验证分离的 fallback。它们是测试代码提供的验收设计，本页没有运行或替它们宣布通过。

## HCU 借鉴与上限评估

先查 HCU TE / Flash-Train 是否已有适用融合，冻结 eps、gamma、scale、两向输出及反向保存 rsigma 的契约。将基线的输入读取、中间写回/再读、输出与 scale 字节列出；融合后仍有 rsigma 读取和输出的必要开销，不能按“零中间量、一次读取”高估上限。使用真实 shape 的实测 HBM/计算参考，并检查小矩阵 launch 延迟与调度资源。

通过 baseline Skill 建保守实现，再按 Triton/HIP 优化 Skill 做正确性、profile、上限与迭代。回接模型同时比较 dgrad/wgrad、缓存/重算、显存以及稳定阶段 loss。官方 MXFP8 kernel、PTX 和 scale swizzle 是机制证据，不能直接部署为 HCU 实现。

## 停止与回退

若实际分发不支持目标形状或 recipe，保留原稳定 backend；如果量化/scale 重排的节省被寄存器、occupancy 或后续 GEMM 代价抵消，说明净收益上限并回退。修复 TE 自有归一化契约交 HCU TE；独立通用训练融合按库归属交付，并提供边界测试和原实现对照。

## 固定源码

- [transformer_engine/common/normalization/rmsnorm/rmsnorm_api.cpp](https://github.com/NVIDIA/TransformerEngine/blob/2e959f352c8e2d4b2709e6775867f2c7494656f3/transformer_engine/common/normalization/rmsnorm/rmsnorm_api.cpp)
- [transformer_engine/common/normalization/rmsnorm/rmsnorm_fwd_mxfp8.cu](https://github.com/NVIDIA/TransformerEngine/blob/2e959f352c8e2d4b2709e6775867f2c7494656f3/transformer_engine/common/normalization/rmsnorm/rmsnorm_fwd_mxfp8.cu)
- [tests/pytorch/mxfp8/test_mxfp8_rmsnorm_fwd.py](https://github.com/NVIDIA/TransformerEngine/blob/2e959f352c8e2d4b2709e6775867f2c7494656f3/tests/pytorch/mxfp8/test_mxfp8_rmsnorm_fwd.py)
- [transformer_engine/pytorch/csrc/extensions/normalization.cpp](https://github.com/NVIDIA/TransformerEngine/blob/2e959f352c8e2d4b2709e6775867f2c7494656f3/transformer_engine/pytorch/csrc/extensions/normalization.cpp)

本文为官方源码、接口与测试阅读，未运行这些 NVIDIA 实现，不声称 HCU 支持或获得相同性能。
