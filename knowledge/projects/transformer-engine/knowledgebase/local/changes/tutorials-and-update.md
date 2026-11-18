---
id: official-transformer-engine-wiki/tutorials-and-update
title: TE 官方教程索引与版本更新方法
engine: transformer-engine
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-11-18'
retrieved_on: '2026-11-04'
sources:
- source: nvidia-transformerengine
  path: docs/index.rst
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 1fa7a775a3e47d1cefecca8bc3000db67aa0bd30dbf8b991a7d84bc5ffb70825
- source: nvidia-transformerengine
  path: docs/getting_started/getting_started_pytorch.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: fd8a9c69dcba4a6bd8b9e126a95a4ed26de37f653e6645f6a946ac158626bb01
- source: nvidia-transformerengine
  path: docs/examples/fp8_primer.ipynb
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 05b00252a257326ce76759dce02bf8bb5d5221d45359ea13988f3c90996c108f
- source: nvidia-transformerengine
  path: docs/examples/advanced_optimizations.ipynb
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 0d5d703679a7d3c16773112e8879879560a945600c168a95b27b22bc44f9a22a
- source: nvidia-transformerengine
  path: docs/examples/attention/attention.ipynb
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 055093bf03f8b79cbfc84abad66d282b4de86ab4672ffc402f1c927d2c2b065a
- source: nvidia-transformerengine
  path: docs/examples/op_fuser/op_fuser.rst
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 95497fc7b153ba375d9687e6ce2333bdfee40da6f3653555624c274f9cf5f71d
- source: nvidia-transformerengine
  path: docs/examples/gemm_profiling/gemm_profiling.rst
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 31444db2fe36482719a7262091ea25ae69a95d13f898c19148b0b0efe91c52f2
- source: nvidia-transformerengine
  path: docs/release_notes.md
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 7e0ea32b48936420fa0d70a274917bfa15358a03b2925317a0c29872408f3824
- source: nvidia-transformerengine-docs
  path: getting-started
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: f0038d7e07b46a521e1edf0a94abbf621fd8ae1ba62061eff0318594bb46b191
  url: https://docs.nvidia.com/deeplearning/transformer-engine/getting_started/index.html
  revision_kind: web-content-fingerprint
- source: nvidia-transformerengine-docs
  path: fp8-primer
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: b7b77e739cacb8991383baa93084bb2f12f6385eb34aaace84be6e0d3aac5126
  url: https://docs.nvidia.com/deeplearning/transformer-engine/examples/fp8_primer.html
  revision_kind: web-content-fingerprint
- source: nvidia-transformerengine-docs
  path: advanced-optimizations
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: 6d7c1eff4937a379e6a812783e475f8b10971eda810b532c43db35e81bd1a162
  url: https://docs.nvidia.com/deeplearning/transformer-engine/examples/advanced_optimizations.html
  revision_kind: web-content-fingerprint
- source: nvidia-transformerengine-docs
  path: attention
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: 983e93a50785e09d921be543498398149788383692039e0076b9392f6a106dca
  url: https://docs.nvidia.com/deeplearning/transformer-engine/examples/attention/attention.html
  revision_kind: web-content-fingerprint
- source: nvidia-transformerengine
  path: docs/installation.rst
  commit: 8e89d3ad8b2ce7adb9a8ad4bd5798197db16de8b
  sha256: 86372814c4a1f14ef7be6bbbfd20c707ccd63a0e0bd707cce645b4bf4263fa0e
- source: nvidia-transformerengine
  path: docs/envvars.rst
  commit: 8e89d3ad8b2ce7adb9a8ad4bd5798197db16de8b
  sha256: cc8514ad8c952a78b6a116b4f470dfeb34c035204f98e0d9cce3f9df6b4a8857
- source: nvidia-transformerengine-docs
  path: advanced-optimizations
  commit: 72dfe3c00c835bfb71c36479763bab8eeae6d77778d3365ad380723d9ea62843
  sha256: c977c8d5cc732d9bb29b43914503a926f139746296f0d390a7b185b128ffe16c
- source: nvidia-transformerengine-docs
  path: attention
  commit: 72dfe3c00c835bfb71c36479763bab8eeae6d77778d3365ad380723d9ea62843
  sha256: 601ea62774d0b15f9a0a51cf7af707d63527fdbeec7c8fec98a2a419164c5e25
- source: nvidia-transformerengine-docs
  path: fp8-primer
  commit: 72dfe3c00c835bfb71c36479763bab8eeae6d77778d3365ad380723d9ea62843
  sha256: b249549e2d4c96315a038cf6f869ece7863cacf9993b79aa9ff00c96a9662c8b
- source: nvidia-transformerengine-docs
  path: getting-started
  commit: 72dfe3c00c835bfb71c36479763bab8eeae6d77778d3365ad380723d9ea62843
  sha256: a1004c72da2e072bc652a7e061d7f5bb57b44ecc0cc7d4d4a6f54e76c8b5d0b4
---

# TE 官方教程索引与版本更新方法

## 按问题选择教程

| 问题 | 仓内教程 | 阅读后形成的任务证据 |
| --- | --- | --- |
| 怎样替换普通 Transformer 层 | `docs/getting_started/getting_started_pytorch.py` | 基线、模块映射、参数复制、实际 fwd/bwd；教程尺寸不能当目标模型配置。 |
| 为什么 FP8/FP4 不是简单 cast | `docs/examples/fp8_primer.ipynb` | recipe、格式、scale/amax、设备限制及数值比较方案。 |
| 梯度累积、主梯度和权重缓存 | `docs/examples/advanced_optimizations.ipynb` | microbatch/optimizer 边界、main_grad 管理、缓存失效及峰值内存。 |
| attention 为什么换了 backend | `docs/examples/attention/attention.ipynb` | mask、layout、dtype、版本、支持条件与实际 dispatch。 |
| 想按 NV 粒度融合 | `docs/examples/op_fuser/op_fuser.rst` | 操作序列、fwd/bwd 不同融合、saved tensors 与返回值契约。 |
| 模型内 GEMM 是否太慢 | `docs/examples/gemm_profiling/gemm_profiling.rst` | 本 rank shape、fprop/dgrad/wgrad、预量化与 autocast 计时边界。 |

官网入口为 [TE 文档](https://docs.nvidia.com/deeplearning/transformer-engine/index.html)。本次八个登记官网节点均展示 2.21.0，使用独立网页内容指纹 `72dfe3c0…`；GitHub 最新非预发布为 [v2.21.0](https://github.com/NVIDIA/TransformerEngine/releases/tag/v2.21.0)，发布于2026-11-10。登记的 main 提交仍可能包含该发布之外的功能。引用时优先任务安装版本相应文档，不把滚动官网、主干和 HCU fork 混合成一个已验证环境。

2026-11-04 官方 Releases API 最近10条快照中，最新一项为非预发布 [v2.20.2](https://github.com/NVIDIA/TransformerEngine/releases/tag/v2.20.2)，发布于 2026-10-05；该快照不宣称完整发布历史。它与本次 main 固定提交分别记录，不把 develop/main 新增的融合或缓存机制自动当作该 wheel 已提供的行为。

## 搜索与更新

`wiki-search "FP8 权重缓存 microbatch" --engine transformer-engine` 可命中本库主题；沿页尾固定链接查看详细教程和实现。源码教程（包含 notebook）登记在 `nvidia-transformerengine`，官网 HTML 页面独立登记为 `nvidia-transformerengine-docs`，日常用 `wiki-update` 检查登记范围；只有需要扩展相关文档或深查时才显式 inventory/sync-docs/refresh，详情见项目 [更新协议](../../../../../../docs/wiki.md)。

按变化影响检查 release notes、目录/toctree、新增教程与关键测试；新增关注主题经筛选再登记。普通 PR 联搜发现，形成结论时读取正文、固定实现和必要讨论，不默认补采全部评论或逐仓扩写。量化变化影响 precision/cache、graph、数值基线；attention 变化影响 TE 及 cuDNN 页面；overlap 变化影响训练分析与操作指南。全部相关正文/Skill 复核后才登记已审核版本。

网页采集的 `commit` 字段为兼容回执结构使用内容指纹，并标记 `web-content-fingerprint`；它不是 Git SHA。原始 HTML 和可读文本留在私有工作区。作者说明、URL、哈希和来源锁提交；抓取完成不等于教程已逐条运行。

本次源码 `8e89d3ad8b2c` 的变化集中于安装下限、CuTeDSL 分发诊断、FA4 导入条件、Norm 输出 scale 组织、Grouped MLP 与 Graph/recipe 状态。按这些消费者修订现有页，不把滚动官网、源码主干、已发布 wheel 和 HCU fork 合并成一个版本，也没有执行上游设备测试。

## 来源与版本复核

2026-11-04 复核源码为 `720b25258be3b60f482afff8aef00d4cad88fa16`；docs/index 新增 MoE 专题入口，当时的源码教程主体、安装示例与 RMSNorm-MXFP8 直接实现/测试复用已固定机制。该次官网8个节点仍展示2.20.2；当时核对范围为：安装的 CUDA/cuDNN 与 ABI 约束、权重缓存的 microbatch 合同、attention 支持表和 op-fuser channel 边界分开解释；不能由网页版本号或内容指纹推导 main 的 BF16 融合已发布到 wheel。低精度 helper 的局部测试、后端选择、完整训练质量仍是不同证据，本轮未执行 NVIDIA/HCU 示例或补称 PR 续扫已经完成。

- [nvidia-transformerengine: docs/index.rst](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/index.rst)
- [nvidia-transformerengine: docs/getting_started/getting_started_pytorch.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/getting_started/getting_started_pytorch.py)
- [nvidia-transformerengine: docs/examples/fp8_primer.ipynb](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/examples/fp8_primer.ipynb)
- [nvidia-transformerengine: docs/examples/advanced_optimizations.ipynb](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/examples/advanced_optimizations.ipynb)
- [nvidia-transformerengine: docs/examples/attention/attention.ipynb](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/examples/attention/attention.ipynb)
- [nvidia-transformerengine: docs/examples/op_fuser/op_fuser.rst](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/examples/op_fuser/op_fuser.rst)
- [nvidia-transformerengine: docs/examples/gemm_profiling/gemm_profiling.rst](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/examples/gemm_profiling/gemm_profiling.rst)
- [nvidia-transformerengine: docs/release_notes.md](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/release_notes.md)
- [nvidia-transformerengine-docs: getting-started](https://docs.nvidia.com/deeplearning/transformer-engine/getting_started/index.html)
- [nvidia-transformerengine-docs: fp8-primer](https://docs.nvidia.com/deeplearning/transformer-engine/examples/fp8_primer.html)
- [nvidia-transformerengine-docs: advanced-optimizations](https://docs.nvidia.com/deeplearning/transformer-engine/examples/advanced_optimizations.html)
- [nvidia-transformerengine-docs: attention](https://docs.nvidia.com/deeplearning/transformer-engine/examples/attention/attention.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
