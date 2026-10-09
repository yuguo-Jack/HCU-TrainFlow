---
id: official-cudnn-frontend-wiki/tutorials-and-update
title: cuDNN Frontend 官方教程、源码实例与更新索引
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
  path: docs/quickstart.mdx
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 93ed00e9f0f26ad5a4f31971b226ffaef47477e435e61cc66e4f9f9b47c456ea
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
  path: samples/python/29_rmsnorm.ipynb
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 4f7a127401a32e819c5b0d11b31579f7a7b6480e4cbd056e55cd8d3a7231ee62
- source: nvidia-cudnn-frontend
  path: samples/frost/gemm/06_moe_grouped_matmul_fwd_swiglu.py
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: 8fb058957f1f11d2fbc602dc30263fd10deed955b20f2a1f754d0109a86e6b5f
- source: nvidia-cudnn-frontend
  path: docs/utilities/python_graph_and_execution_backends.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: de73a4ce7f5532c8aff2f590c5f74200a09b167e18e3c38982fa108a40fe842f
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/overview.md
  commit: eae67e3b9f78bac93cf19b0569effa01f760e1e8
  sha256: fe44382f85fcc487b15acc31eb2d8d5685cd3f7e3657ffedb0753dba22738a02
- source: nvidia-cudnn-frontend-docs
  path: quickstart
  commit: e231f1ecf1c04ca05f5c5f66898be6f84da14a37fddd16491d733ebb95e321c1
  sha256: efb405e71ec606566ab443881a1101611dbc8a64b45cb487a6c421efd2c1a1c4
  url: https://docs.nvidia.com/deeplearning/cudnn/latest/quickstart.html
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend-docs
  path: attention
  commit: e231f1ecf1c04ca05f5c5f66898be6f84da14a37fddd16491d733ebb95e321c1
  sha256: 7279edf4b28c45694ef19209912753f1c2badd3f753d159a99300001158b8844
  url: https://docs.nvidia.com/deeplearning/cudnn/latest/operations/Attention.html
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend-docs
  path: open-kernels
  commit: e231f1ecf1c04ca05f5c5f66898be6f84da14a37fddd16491d733ebb95e321c1
  sha256: 93d501a4efe8ce95bbc7abc0ee9e5e410323006364f42dbb77e6bbea189c2de6
  url: https://docs.nvidia.com/deeplearning/cudnn/latest/fe-oss-apis/overview.html
  revision_kind: web-content-fingerprint
---

# cuDNN Frontend 官方教程、源码实例与更新索引

## 任务到教程的导航

| 任务 | 官方入口 | 重点产物 |
| --- | --- | --- |
| 初次集成图接口 | `docs/quickstart.mdx`、C++ samples | tensor 元数据、输出标记、build/execute、baseline 比较。 |
| SDPA 训练 | Python 50/51 notebook、`samples/cpp/sdpa/` | fwd/bwd、stats、布局、mask、RNG 与工作区。 |
| 归一化融合 | `samples/python/29_rmsnorm.ipynb` 及 Norm samples | eps、归约轴、gamma 约定、cast/累积与梯度。 |
| MoE GEMM/激活融合 | `samples/frost/gemm/06_moe_grouped_matmul_fwd_swiglu.py`、FE-OSS GEMM 教程 | 专家分组、融合边界、输出及数值 reference；fwd 示例不证明 bwd 已接入。 |
| CPU overhead 与 cache | utilities 的 framework integration / dynamic cache / CUDA graphs | 分阶段计时、plan 生命周期、stream 和缓存失效。 |
| 新稀疏 attention | BSA/NSA/DSA 文档与同目录 API/test | 稀疏元数据与训练支持；区分实验能力。 |

官网使用 [当前 cuDNN 文档入口](https://docs.nvidia.com/deeplearning/cudnn/latest/)，旧 frontend/latest 会重定向。教程、最新主干与实际发布版本分别保存；主干新增的 Graph 包装或 FROST 能力须验证其是否进入所用版本。

## 搜索和维护

源码、教程 notebook 与接口文档登记在 `nvidia-cudnn-frontend`；官网正文登记在 `nvidia-cudnn-frontend-docs`。例如 `wiki-search "SDPA stats backward" --engine cudnn-frontend` 和 `wiki-search "grouped GEMM SwiGLU" --engine cudnn-frontend` 可定位对应专题，再读完整原文及固定代码。

更新时分别运行这两个 source 的 `wiki-refresh`，检查 API/支持面、release、代码目录、教程参数及 PR review。新增 kernel 家族按价值补充，而非只把 README 列表拷进 Wiki。源码路径移动要更新注册表与章节引用；抓取失败或未完整阅读时保留 pending review，不误报所有知识已同步。

Graph/plan 变化联动安装和性能案例；SDPA 变化同时复核 TE attention；融合/数值变化联动 HCU 承接边界与优化 Skill。依赖/许可变化核对当前 `LICENSING.md` 和具体文件声明。实际 HCU 运行仍需自己的源码、环境和验证证据。

## 来源与版本复核

- [nvidia-cudnn-frontend: docs/quickstart.mdx](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/quickstart.mdx)
- [nvidia-cudnn-frontend: docs/operations/Attention.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/operations/Attention.md)
- [nvidia-cudnn-frontend: samples/python/50_sdpa_forward.ipynb](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/samples/python/50_sdpa_forward.ipynb)
- [nvidia-cudnn-frontend: samples/python/51_sdpa_backward.ipynb](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/samples/python/51_sdpa_backward.ipynb)
- [nvidia-cudnn-frontend: samples/python/29_rmsnorm.ipynb](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/samples/python/29_rmsnorm.ipynb)
- [nvidia-cudnn-frontend: samples/frost/gemm/06_moe_grouped_matmul_fwd_swiglu.py](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/samples/frost/gemm/06_moe_grouped_matmul_fwd_swiglu.py)
- [nvidia-cudnn-frontend: docs/utilities/python_graph_and_execution_backends.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/utilities/python_graph_and_execution_backends.md)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/overview.md](https://github.com/NVIDIA/cudnn-frontend/blob/eae67e3b9f78bac93cf19b0569effa01f760e1e8/docs/fe-oss-apis/overview.md)
- [nvidia-cudnn-frontend-docs: quickstart](https://docs.nvidia.com/deeplearning/cudnn/latest/quickstart.html)
- [nvidia-cudnn-frontend-docs: attention](https://docs.nvidia.com/deeplearning/cudnn/latest/operations/Attention.html)
- [nvidia-cudnn-frontend-docs: open-kernels](https://docs.nvidia.com/deeplearning/cudnn/latest/fe-oss-apis/overview.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码 main、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
