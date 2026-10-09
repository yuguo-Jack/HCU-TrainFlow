---
id: official-cudnn-frontend-wiki/attention
title: cuDNN SDPA 训练：Forward、Backward、Stats 与布局
engine: cudnn-frontend
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-cudnn-frontend
  path: docs/operations/Attention.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: a74721673ec44fe42148d955bb23c7fadf99f25e7f1efc32317211a09323e872
- source: nvidia-cudnn-frontend
  path: samples/python/50_sdpa_forward.ipynb
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 5269e5e9a40a4646ec36eaaee478eef6a79cbf252f107c77af8575bc58175f93
- source: nvidia-cudnn-frontend
  path: samples/python/51_sdpa_backward.ipynb
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: e530a489347cc811a7cf67319c48e479e100f32304abca90b6d0777f09032950
- source: nvidia-cudnn-frontend
  path: samples/cpp/sdpa/fp16_fwd.cpp
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 9fff38ca56811b429f8cae604a922bef70a68644df8e5c40ec4bf2ea51730384
- source: nvidia-cudnn-frontend
  path: samples/cpp/sdpa/fp16_bwd.cpp
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 62f47b922848b39b6ec9ee07f2dbac8e65b2f46cfffb1e327e9b050a4d9f6bc2
- source: nvidia-cudnn-frontend
  path: include/cudnn_frontend/node/scaled_dot_product_flash_attention.h
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 306f5fa6ef9a674dc796de6878cffba517b448f8d34aea9661c2d6020d16a0f7
- source: nvidia-cudnn-frontend-docs
  path: attention
  commit: e231f1ecf1c04ca05f5c5f66898be6f84da14a37fddd16491d733ebb95e321c1
  sha256: 7279edf4b28c45694ef19209912753f1c2badd3f753d159a99300001158b8844
  url: https://docs.nvidia.com/deeplearning/cudnn/latest/operations/Attention.html
  revision_kind: web-content-fingerprint
---

# cuDNN SDPA 训练：Forward、Backward、Stats 与布局

## 完整训练接口

前向定义 Q/K/V、attention scale、mask、bias、dropout 和输出；训练模式还需要保留反向依赖的 statistics。反向接收同一次 forward 的 Q/K/V、O、stats 与 dO，产生 dQ/dK/dV，某些配置还涉及 bias 梯度。不能用只生成 O 的推理示例替代训练实现。

官方 backward notebook 的 stats 为 FP32，典型逻辑形状为 B×H×S×1；变长和其他接口的实际契约应查对应版本。Python 示例同时展示高级 Graph 包装和显式 pygraph；参数可能用 is_inference 或 generate_stats 表达训练需求，不要跨版本机械替换。

## 布局与 mask 是数值契约

逻辑 BHSD 与物理 BSHD 可通过 stride 表示，同 shape 不代表同布局。GQA/MQA 的 query/KV head 数、Q 与 KV 不等长、packed cu_seqlens、THD、padding、causal 对角方向、sliding window 与 dropout RNG 都会影响结果及支持条件。对齐 NV 时应取得实际调用参数与存储布局，而非从模型名称猜测。

`samples/cpp/sdpa/fp16_bwd.cpp` 明确声明输出和 stats、uid/stride、compute/intermediate dtype，并设置 backward 参数。阅读样例后继续读 graph node 的约束及当前 SDPA 测试。所谓“FlashAttention”描述算法或后端路径，不证明两个库的 mask、scale 与反向细节自动一致。

## HCU 实现与验证

1. 优先查 HCU TE 或 Flash-Train 是否已有同接口/同模式实现，检查当前 branch 与实际 dispatch。
2. 将 reference、HCU baseline 与候选的输入/输出、统计量和 saved tensors 契约冻结；固定 RNG。
3. 对照 fwd、dQ/dK/dV 及必要的其他梯度，覆盖长短序列、head_dim、GQA、边界和所需非连续布局。
4. 独立实测同 shape fwd/bwd，再比较模型内的占比与拖慢情况；布局转换和辅助 kernel 一并计入。
5. 正确性通过后再合入训练阶段，候选稳定时验 loss。不能靠放松阈值掩盖 mask 或 scale 不一致。

forward 与 backward 按序执行时可按两者 workspace 最大需求共享 buffer；如果实际存在 overlap，则必须保证并发安全。stats/saved tensor 还活着时不能过早复用存储。完整显存账本还包括 plan/cache、graph pool 和通信缓冲。

## 来源与版本复核

- [nvidia-cudnn-frontend: docs/operations/Attention.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/operations/Attention.md)
- [nvidia-cudnn-frontend: samples/python/50_sdpa_forward.ipynb](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/samples/python/50_sdpa_forward.ipynb)
- [nvidia-cudnn-frontend: samples/python/51_sdpa_backward.ipynb](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/samples/python/51_sdpa_backward.ipynb)
- [nvidia-cudnn-frontend: samples/cpp/sdpa/fp16_fwd.cpp](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/samples/cpp/sdpa/fp16_fwd.cpp)
- [nvidia-cudnn-frontend: samples/cpp/sdpa/fp16_bwd.cpp](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/samples/cpp/sdpa/fp16_bwd.cpp)
- [nvidia-cudnn-frontend: include/cudnn_frontend/node/scaled_dot_product_flash_attention.h](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/include/cudnn_frontend/node/scaled_dot_product_flash_attention.h)
- [nvidia-cudnn-frontend-docs: attention](https://docs.nvidia.com/deeplearning/cudnn/latest/operations/Attention.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码 main、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
