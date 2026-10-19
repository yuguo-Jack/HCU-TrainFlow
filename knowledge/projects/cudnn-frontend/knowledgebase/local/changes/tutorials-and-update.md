---
id: official-cudnn-frontend-wiki/tutorials-and-update
title: cuDNN Frontend 官方教程、源码实例与更新索引
engine: cudnn-frontend
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-20'
sources:
- source: nvidia-cudnn-frontend
  path: docs/quickstart.mdx
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: b2d16117ddd1956a6b5fe4e231b5a9260dce41f6130b47627e77d2b77e8a378a
- source: nvidia-cudnn-frontend
  path: docs/operations/Attention.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: f82cb49cc719d7d12cfafea238a793918ca2ddf713edde173555acbb6f820b64
- source: nvidia-cudnn-frontend
  path: samples/python/50_sdpa_forward.ipynb
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 5269e5e9a40a4646ec36eaaee478eef6a79cbf252f107c77af8575bc58175f93
- source: nvidia-cudnn-frontend
  path: samples/python/51_sdpa_backward.ipynb
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: e530a489347cc811a7cf67319c48e479e100f32304abca90b6d0777f09032950
- source: nvidia-cudnn-frontend
  path: samples/python/29_rmsnorm.ipynb
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 4f7a127401a32e819c5b0d11b31579f7a7b6480e4cbd056e55cd8d3a7231ee62
- source: nvidia-cudnn-frontend
  path: samples/frost/gemm/06_moe_grouped_matmul_fwd_swiglu.py
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 8fb058957f1f11d2fbc602dc30263fd10deed955b20f2a1f754d0109a86e6b5f
- source: nvidia-cudnn-frontend
  path: docs/utilities/python_graph_and_execution_backends.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: e73978234e7afd4325f2b886ea9c7b9c8051dd0a963d0922bae4ca2e3691179d
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/overview.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 6c347c2a2eee41824bb24e5461ac8248d54b0787ff23f5556a41796267c09d55
- source: nvidia-cudnn-frontend-docs
  path: quickstart
  commit: 935d19c3968895d2890a5e4c651071b2f3ec91666c8b340c44a5064fad19293c
  sha256: a360753931c52ab40d573da739ed74d9d730d7c0063c3634116f89b7075f6c7c
  url: https://docs.nvidia.com/cudnn/quickstart/
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend-docs
  path: attention
  commit: 935d19c3968895d2890a5e4c651071b2f3ec91666c8b340c44a5064fad19293c
  sha256: 99596d620c3471579259610ef4b780d319bb7bfb235ccd2b63e2e27080c328a6
  url: https://docs.nvidia.com/cudnn/operations/Attention
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend-docs
  path: open-kernels
  commit: 935d19c3968895d2890a5e4c651071b2f3ec91666c8b340c44a5064fad19293c
  sha256: e14115ad3751858b10e51100c0ab5f8983a683899cae5bfca3bf1d18e8119a27
  url: https://docs.nvidia.com/cudnn/fe-oss-apis/overview
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

官网使用 [当前 cuDNN 文档入口](https://docs.nvidia.com/cudnn/overview)，旧 deeplearning/cudnn/latest 入口已重定向到新站。本次8个登记节点分别保留新 canonical URL、HTML与文本哈希；这次迁移后的正文不能继续沿用旧站“未变”的判断。教程、固定源码与实际发布版本分别保存；主干新增的 Graph 包装或 FROST 能力须验证其是否进入所用版本。

## 搜索和维护

源码、教程 notebook 与接口文档登记在 `nvidia-cudnn-frontend`；官网正文登记在 `nvidia-cudnn-frontend-docs`。例如 `wiki-search "SDPA stats backward" --engine cudnn-frontend` 和 `wiki-search "grouped GEMM SwiGLU" --engine cudnn-frontend` 可定位对应专题，再读完整原文及固定代码。

更新时分别运行这两个 source 的 `wiki-refresh`，检查 API/支持面、release、代码目录、教程参数及 PR review。新增 kernel 家族按价值补充，而非只把 README 列表拷进 Wiki。源码路径移动要更新注册表与章节引用；抓取失败或未完整阅读时保留 pending review，不误报所有知识已同步。

Graph/plan 变化联动安装和性能案例；SDPA 变化同时复核 TE attention；融合/数值变化联动 HCU 承接边界与优化 Skill。依赖/许可变化核对当前 `LICENSING.md` 和具体文件声明。实际 HCU 运行仍需自己的源码、环境和验证证据。

## 来源与版本复核

- [nvidia-cudnn-frontend: docs/quickstart.mdx](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/quickstart.mdx)
- [nvidia-cudnn-frontend: docs/operations/Attention.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/operations/Attention.md)
- [nvidia-cudnn-frontend: samples/python/50_sdpa_forward.ipynb](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/samples/python/50_sdpa_forward.ipynb)
- [nvidia-cudnn-frontend: samples/python/51_sdpa_backward.ipynb](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/samples/python/51_sdpa_backward.ipynb)
- [nvidia-cudnn-frontend: samples/python/29_rmsnorm.ipynb](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/samples/python/29_rmsnorm.ipynb)
- [nvidia-cudnn-frontend: samples/frost/gemm/06_moe_grouped_matmul_fwd_swiglu.py](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/samples/frost/gemm/06_moe_grouped_matmul_fwd_swiglu.py)
- [nvidia-cudnn-frontend: docs/utilities/python_graph_and_execution_backends.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/utilities/python_graph_and_execution_backends.md)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/overview.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/fe-oss-apis/overview.md)
- [nvidia-cudnn-frontend-docs: quickstart](https://docs.nvidia.com/cudnn/quickstart/)
- [nvidia-cudnn-frontend-docs: attention](https://docs.nvidia.com/cudnn/operations/Attention)
- [nvidia-cudnn-frontend-docs: open-kernels](https://docs.nvidia.com/cudnn/fe-oss-apis/overview)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## 持续跟踪两条版本线

本 Wiki 的新机制基线选择官方 develop，发布兼容性继续查 [Releases](https://github.com/NVIDIA/cudnn-frontend/releases)、main 与部署包。遇到分支切换、reset 或已引用提交不在默认分支祖先链时，先做 compare/版本确认，不能自动把较旧默认分支当作更“新”的事实。网页 latest 另有内容指纹，网页与源码冲突时并列说明适用版本。

当前 Git 机制固定 `a7269d7607db`；新官网 Quick Start 的高级 Graph context、framework integration 的计时边界和 dynamic-cache 的通用说明已交叉检查。SDPA 对 stride override 的具体限制以该 Git 版本节点/实现为准；官网概览保留旧 JAX 别名时，以该版本单项文档与实际 Python 导出为准，不能靠网页迁址认为部署自动升级。FlexAttention 既有 mask plan/autograd 四个登记来源正文未变，继续复用原机制与未现场验证边界。
