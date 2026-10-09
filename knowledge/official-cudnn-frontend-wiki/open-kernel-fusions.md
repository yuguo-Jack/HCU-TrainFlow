---
id: official-cudnn-frontend-wiki/open-kernel-fusions
title: cuDNN 开放 Kernel：MoE 融合、FROST 与稀疏 Attention
engine: cudnn-frontend
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/overview.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: fe44382f85fcc487b15acc31eb2d8d5685cd3f7e3657ffedb0753dba22738a02
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/gemm_fusions/grouped_gemm_swiglu.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 2cc6d6ef146c7a1ad732eb1baea43f30cc777db15cf63691bdeb86707834d559
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/gemm_fusions/grouped_gemm_dswiglu.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 29242dda32d88a535311f3496574405bc32c53b3cc765f24c56b0871cb8cab00
- source: nvidia-cudnn-frontend
  path: python/cudnn/gemm/cutedsl/grouped/swiglu/api.py
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: a97c652e10269febd9f9cff12c1cbe66d65ab0ee0979b6751523108501c0e790
- source: nvidia-cudnn-frontend
  path: python/cudnn/gemm/cutedsl/grouped/glu/_blockscaled_api.py
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 4bb7bb8991984fcb7d9d2d00ede8937db96d3ffdfa54337fe4f332e9fcc8c42d
- source: nvidia-cudnn-frontend
  path: python/cudnn/gemm/frost/engine.py
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 8804aefd033b0419b3b300e2304922d04668bfdf0aceefec972e38967ec011fa
- source: nvidia-cudnn-frontend
  path: python/cudnn/gemm/frost/graph_analyzer.py
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: d92a46ce14c54ffe90a9ea73ea212e9297c52d750d2cc9280fc867a51a9b68b3
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/bsa.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: f41f49444dc4644b06e0ea9920d88d667f18243a064af320ab46bbcfcc8fb706
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/dsa.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 6e8ce8f97bcb70c877ca3da91b565318568df887d650f1320e56a765134fbd11
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/nsa.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 8f3ee3863f9c80992e63e8ee7fa770d18eb08e430acaace04870cabc22873ce4
- source: nvidia-cudnn-frontend
  path: python/cudnn/block_sparse_attention/api.py
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: f482f0a47f7882f64dd60e13f6bc056fdf55a21cc0a43f914b867da45b66010c
- source: nvidia-cudnn-frontend-docs
  path: open-kernels
  commit: e231f1ecf1c04ca05f5c5f66898be6f84da14a37fddd16491d733ebb95e321c1
  sha256: 93d501a4efe8ce95bbc7abc0ee9e5e410323006364f42dbb77e6bbea189c2de6
  url: https://docs.nvidia.com/deeplearning/cudnn/latest/fe-oss-apis/overview.html
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend-docs
  path: sparse-attention
  commit: e231f1ecf1c04ca05f5c5f66898be6f84da14a37fddd16491d733ebb95e321c1
  sha256: 09602d6746dbebf71601cb542d5f0559cbdda631e082aa3ba19dcfd1bc1da01f
  url: https://docs.nvidia.com/deeplearning/cudnn/latest/fe-oss-apis/bsa.html
  revision_kind: web-content-fingerprint
---

# cuDNN 开放 Kernel：MoE 融合、FROST 与稀疏 Attention

## 两类开放入口

Frontend OSS 提供直接调用的融合 kernel API；部分操作有自动管理输出/编译缓存的 wrapper，也有 check_support、compile、execute 的显式生命周期。新 Python 图还可选择开放执行 engine，例如 FROST 的图分析、planning 和架构专用编译模板。两类调用不必有相同的缓存键、autograd 或支持面。

## 案例：Grouped GEMM + SwiGLU + 量化

**问题**：MoE 中 GEMM、激活、gating 和后续量化分离，会增加中间张量读写及 launch；各专家 token 数不均又影响调度效率。

**源码入口**：`grouped/swiglu/api.py` 当前继承统一的 block-scaled GLU API，通过 activation 选择 SwiGLU。继续读 `grouped/glu/_blockscaled_api.py`，核对输入验证、support、compile/execute 以及真实 kernel。不能因为文件名含 SwiGLU 就认定独立实现仍在该文件。

**需要对齐的条件**：每专家 M、padded_offsets、权重布局、scale factor 存储、alpha、路由概率、激活排列与输出量化。官方该教程中的 gate/value 以特定列块配对，并非任意模型的前半/后半拼法；D 的行列量化表示、scale 和中间 C 可能供反向或后继 GEMM 使用。

**为什么不是只少一个激活 kernel**：融合把 GEMM 结果直接用于 epilogue，可能同时输出 backward 需要的中间量和后续低精度表示。比较性能必须包含重排、padding、量化和保留中间结果的成本。Fwd 快但 wgrad/dgrad 或显存代价变大，不能作为训练净收益。

**HCU 路线**：先查 Flash-Train/TE 与数学库现有能力；冻结接口和数值，复用算法与融合边界，由 Hygon HIP/Triton Skill 实现目标架构版本。SM100、CuTe DSL、scale swizzle 等设备细节不直接照搬。回归专家数、极不均 token、空专家、边界及多精度，最后做模型阶段 loss。

## 稀疏 attention 不能只按名称归类

| 家族 | 需要明确的语义 |
| --- | --- |
| BSA | 每个 query block 的 KV block 列表，块内有效长度及跨所选块的 softmax；官方标记 experimental。 |
| NSA | 包含特定路由/selection 等管线，不能等同于任意 block sparse；逐组件核对 token 与 block 元数据。 |
| DSA | 模型相关稀疏选择与索引语义，读当前 API、mask、布局和对应反向支持，不能直接套 BSA reference。 |

采用前先确认 forward/backward、训练模式、dtype、head_dim、稀疏元数据与 determinism 的支持状态。先做相同稀疏模式的高精度参考，再比较收益。新模型的 kernel 可能仅支持部分架构或阶段；README 列出功能不等于 HCU 已适配或具备完整训练反向。

## 来源与版本复核

- [nvidia-cudnn-frontend: docs/fe-oss-apis/overview.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/fe-oss-apis/overview.md)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/gemm_fusions/grouped_gemm_swiglu.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/fe-oss-apis/gemm_fusions/grouped_gemm_swiglu.md)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/gemm_fusions/grouped_gemm_dswiglu.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/fe-oss-apis/gemm_fusions/grouped_gemm_dswiglu.md)
- [nvidia-cudnn-frontend: python/cudnn/gemm/cutedsl/grouped/swiglu/api.py](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/python/cudnn/gemm/cutedsl/grouped/swiglu/api.py)
- [nvidia-cudnn-frontend: python/cudnn/gemm/cutedsl/grouped/glu/_blockscaled_api.py](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/python/cudnn/gemm/cutedsl/grouped/glu/_blockscaled_api.py)
- [nvidia-cudnn-frontend: python/cudnn/gemm/frost/engine.py](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/python/cudnn/gemm/frost/engine.py)
- [nvidia-cudnn-frontend: python/cudnn/gemm/frost/graph_analyzer.py](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/python/cudnn/gemm/frost/graph_analyzer.py)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/bsa.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/fe-oss-apis/bsa.md)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/dsa.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/fe-oss-apis/dsa.md)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/nsa.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/fe-oss-apis/nsa.md)
- [nvidia-cudnn-frontend: python/cudnn/block_sparse_attention/api.py](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/python/cudnn/block_sparse_attention/api.py)
- [nvidia-cudnn-frontend-docs: open-kernels](https://docs.nvidia.com/deeplearning/cudnn/latest/fe-oss-apis/overview.html)
- [nvidia-cudnn-frontend-docs: sparse-attention](https://docs.nvidia.com/deeplearning/cudnn/latest/fe-oss-apis/bsa.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码 main、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
