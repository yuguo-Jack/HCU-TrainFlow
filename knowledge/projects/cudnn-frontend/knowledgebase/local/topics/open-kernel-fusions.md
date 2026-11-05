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
reviewed_on: '2026-11-04'
retrieved_on: '2026-11-04'
sources:
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/overview.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 6c347c2a2eee41824bb24e5461ac8248d54b0787ff23f5556a41796267c09d55
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/gemm_fusions/grouped_gemm_swiglu.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: d929ea8a0cc8b5b2e133d3622ee39153d6c542ac511dbda9c99a21d6a03eb8f2
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/gemm_fusions/grouped_gemm_dswiglu.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: a97ce0e2aa903673d5ebaea87604b5d1ea46065ce862457cebfad52f8894ef53
- source: nvidia-cudnn-frontend
  path: python/cudnn/gemm/cutedsl/grouped/swiglu/api.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 6b9f3ef7b115e67cd4caeb8c247c438a3263a5b7ced54d8214551b51b21cb51c
- source: nvidia-cudnn-frontend
  path: python/cudnn/gemm/cutedsl/grouped/glu/_blockscaled_api.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: dfb9429444bfc4cbcd769986ee13f67e7f79adeb66af85b85561ce1cb157ca1d
- source: nvidia-cudnn-frontend
  path: python/cudnn/gemm/frost/engine.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 4cebb51cc79df5c1d750c39840aca508602d6d973d2885326e2c223c7642e88c
- source: nvidia-cudnn-frontend
  path: python/cudnn/gemm/frost/graph_analyzer.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: e92c20c5b819d141c5b6b534824f64951901c783f2c16626d1ac723c4e5ff4cc
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/bsa.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 1a417c5a32db2d573e2c1d6f0e18843b4c6040ddeab0246f68d9cf73efbaa76b
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/dsa.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: d17c869a4b6f6b9f2ab45a0d6254df80f14cc8b06a8b5b8e9a7af0432678bfe2
- source: nvidia-cudnn-frontend
  path: docs/fe-oss-apis/nsa.md
  commit: a7269d7607db343fb099dabf6d8fef47f4a2498c
  sha256: 8f3ee3863f9c80992e63e8ee7fa770d18eb08e430acaace04870cabc22873ce4
- source: nvidia-cudnn-frontend
  path: python/cudnn/block_sparse_attention/api.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: a2f414f6ba96691b44322792b6d6245e5ca1ab62083fe0d8cf29eb9c3b647e94
- source: nvidia-cudnn-frontend-docs
  path: open-kernels
  commit: 62596f777aca773f340569b88fbd42c5fcd807249e8a188810cd38297d19cab9
  sha256: e29e6fdef3be07b400a22661fd07e0078870bad0b4e09cb3e4df5e373f37888f
  url: https://docs.nvidia.com/cudnn/fe-oss-apis/overview
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend-docs
  path: sparse-attention
  commit: 62596f777aca773f340569b88fbd42c5fcd807249e8a188810cd38297d19cab9
  sha256: 0d9cc92b2e7b7918b7973c67b2c27b11ade120b4d03794030910c37214a2ec37
  url: https://docs.nvidia.com/cudnn/fe-oss-apis/bsa
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend
  path: python/cudnn/deepseek_sparse_attention/indexer_top_k/api.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 23094df9b2a8475f456f747957f0f48835280608685da1aa1128ac71fd0e0177
- source: nvidia-cudnn-frontend
  path: python/cudnn/deepseek_sparse_attention/indexer_backward/api.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 41809c353ed0f7cff66c6cf74dd42d7435c0058946bc910c4e1ec4f425005c2e
- source: nvidia-cudnn-frontend
  path: python/cudnn/deepseek_sparse_attention/sparse_attention_backward/api.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: a7aa0afe4439cb47151af9f90284b4b85bf894761176c9b6d5ec0f2dcdb660e5
- source: nvidia-cudnn-frontend
  path: python/cudnn/_pygraph.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 99738780798d18ea38c5870b4a60ab5aa180638e0ef4d875d4920708819e5f5c
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

- [nvidia-cudnn-frontend: docs/fe-oss-apis/overview.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/fe-oss-apis/overview.md)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/gemm_fusions/grouped_gemm_swiglu.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/fe-oss-apis/gemm_fusions/grouped_gemm_swiglu.md)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/gemm_fusions/grouped_gemm_dswiglu.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/fe-oss-apis/gemm_fusions/grouped_gemm_dswiglu.md)
- [nvidia-cudnn-frontend: python/cudnn/gemm/cutedsl/grouped/swiglu/api.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/cudnn/gemm/cutedsl/grouped/swiglu/api.py)
- [nvidia-cudnn-frontend: python/cudnn/gemm/cutedsl/grouped/glu/_blockscaled_api.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/cudnn/gemm/cutedsl/grouped/glu/_blockscaled_api.py)
- [nvidia-cudnn-frontend: python/cudnn/gemm/frost/engine.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/cudnn/gemm/frost/engine.py)
- [nvidia-cudnn-frontend: python/cudnn/gemm/frost/graph_analyzer.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/cudnn/gemm/frost/graph_analyzer.py)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/bsa.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/fe-oss-apis/bsa.md)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/dsa.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/fe-oss-apis/dsa.md)
- [nvidia-cudnn-frontend: docs/fe-oss-apis/nsa.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/docs/fe-oss-apis/nsa.md)
- [nvidia-cudnn-frontend: python/cudnn/block_sparse_attention/api.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/cudnn/block_sparse_attention/api.py)
- [nvidia-cudnn-frontend-docs: open-kernels](https://docs.nvidia.com/cudnn/fe-oss-apis/overview)
- [nvidia-cudnn-frontend-docs: sparse-attention](https://docs.nvidia.com/cudnn/fe-oss-apis/bsa)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## 开发线新增的接口约束

- Grouped MXFP8 SwiGLU 的 JAX 入口归入统一 GLU，`discrete_col_sfd=True` 可按专家组织列 scale；不是所有 GLU/dGLU/wgrad 后端都支持 JAX。forward 尾部超过 `padded_offsets[-1]` 的行未定义；backward 只对原子累加所需 dprob 清零，不能把 padding 当零值参与 loss 或校验。接口提供显式反向不等于自动注册 `jax.grad`。
- BSA Sage FP8 仍为 **forward-only**，输入 BF16、内部量化、输出 BF16，不返回 LSE、没有训练反向。当前 SM90、SM100/SM103、SM120 均有 native blk128，另保留各自 blk64 路线；SM100/SM103 blk128 才允许显式 split-KV，SM120 blk128 才可选择每 token K scale。量化粒度会改变数值，块尺寸/原件更新不扩大训练反向。
- DSA Sparse Attention Backward 的 plan 强调 caller-owned 输出和 workspace：该 API 的所有后端要求传入 dq/dkv/d_sink；高层 wrapper 才负责可选分配。当前该 API 的 prepared SM100 路线在 `compile()` 依据无 storage 元数据准备实际 artifact，execute 不再 JIT；SM90 保留首执行编译。scratch 每次执行仍须初始化，输入/输出/live workspace 不得重叠，并发执行必须使用独立写出和 scratch；有 plan 不等于允许共享可写缓冲。Indexer Backward 是另一条编译链，不能套用此处首执行结论。
- DSA Indexer 的 score 输出可为带 padding 行 stride 的视图；原始 plan 不自动 repack，便利 wrapper 对非连续输入可能额外复制。top-k 输出与 scratch 由调用方持有。比较模型与单测时计入 wrapper 的 copy、初始化和首轮编译；真实 stream、graph 捕获及并发生命周期需要单独验证。

这些约束来自当前 develop 的 BSA/DSA 和 grouped GEMM 文档及已列 API；未在本轮运行 NVIDIA 或 HCU 算子。性能目标仍由真实 shape、前后向完整字节量、layout 与实测上限决定。

## 确定性、空行与包装器的增量复核

DSA standalone Top-K 的 `deterministic=True` 同时固定所选集合和返回槽位，默认 tie policy 下小源索引优先，最后按本地索引升序组织结果；它不是按 score 降序输出。普通模式输出顺序仍未指定，正负零的 radix key 和 NaN 行为要按原合同看。`next_n` 形成的空行现在写 -1 indices / -inf values，不能沿用“输出保留旧内容”的旧假设。class API 校验32字节 input/scratch 对齐及非重叠，wrapper 对 storage-offset 输入可能复制；TVM-FFI launch 后仍需记录真实消费 stream 的存储寿命。

Indexer backward 的 deterministic 路径使用固定 owner 的 FP32 dK planes 和固定顺序归并，compile-time plane 数也是数值关联顺序的一部分；改变 plane 数不保证逐位一致。该请求有架构/形状门禁，不能失败后静默退成 atomic 路线。普通与 deterministic 都在写 attn_score 前校验运行时签名和 workspace，deterministic 还在清零 planes 前拒绝 live scratch 与各 operand 的重叠；复用一个 scratch 的执行不能并发。执行会覆盖 attn_score、保留 index_score。高层 wrapper 省略输出仍会分配，warmup 后要显式传齐输出/workspace 才能按其 Graph 契约捕获。

BSA 的 BF16 自动 split 策略采用 host-visible 元数据，性能假设是 Q 邻域近似均匀随机且较少重叠；高度局部/共享邻域需用相同 mask 比较显式 split，不能由 shape/density 相同推导相同性能。workspace 预算会限制自动选择，而显式超预算会拒绝；该假设不改变稀疏数学语义，也不扩大 Sage FP8 的 forward-only 边界。

当前 BSA KPage 把部分有效的16行 KV page 汇入 MMA tile。`kpage=True` 当次建布局会同步 host，应把固定稀疏图的布局建设放出稳态；稀疏图变化则重新计入成本。其 BF16 backward 支持 GQA，但要求 blk128、padding 行 dO=0，blk64 KPage 仅 forward；它不接收普通路线的 pack_gqa/kv_splits/CLC 调度参数。

IndexerBackward 已移除 `backend="sm100_v2"` 选择器；SM90 要求 H64，受支持的 SM100-family 路线限定 H32/H64、D128、128倍数 top-k 和正有限 scale，deterministic 仍是 request-or-fail。SM100 普通 BF16 dK 的私有 FP32 scratch 使用列置换并由尾部 cast 恢复，不能把该 scratch 当最终梯度；d_weights 只接受 BF16，不能假装输出 FP32 就获得 FP32 精度。

SparseAttentionBackward 的 deterministic relay 另支持 SM90；`deterministic_relay_cluster_size` 为计划期选择，改变 scratch 和固定归并，不能在 execute/replay 时切换。SM90 仍需一次 eager warmup，之后固定地址的无分配执行才可捕获。Grouped GLU 的设备门禁现在检查 tcgen05，明确排除 cc12.x；SwiGLU wrapper cache 加入设备身份，多 GPU 不应误复用同一编译对象。

当前源码将 canonical MXFP8 JAX 的 grouped SwiGLU/dSwiGLU 转到明确 wrapper 或 unified `grouped_gemm_glu_jax_sm100` / `grouped_gemm_dglu_jax_sm100`，旧 `cudnn.jax.*` / `cudnn.torch.*` 对应别名已移除。官网某些概览仍保留旧别名说明，应按本固定代码版本与单项 API 文档核对。统一 GLU/dGLU/wgrad 的 JAX 支持继续有精度、scale、输出与架构约束，显式反向 helper 不自动等于完整 autodiff 注册。

源码还新增 Mamba-2 Python graph node、forward/backward/summary 入口，区别于带 erase 的 GDN；当前官方说明指定其 FROST engine 与 chunk/state-checkpoint 合同。这里只作为新模型机制入口，不由 node 注册推导原有稀疏 attention 或 HCU 已支持，完整数值/状态移植需追具体 engine 与测试。

## 本次补充的实现与测试依据

- [nvidia-cudnn-frontend: python/cudnn/deepseek_sparse_attention/indexer_top_k/api.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/cudnn/deepseek_sparse_attention/indexer_top_k/api.py)
- [nvidia-cudnn-frontend: python/cudnn/deepseek_sparse_attention/indexer_backward/api.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/cudnn/deepseek_sparse_attention/indexer_backward/api.py)
- [nvidia-cudnn-frontend: python/cudnn/deepseek_sparse_attention/sparse_attention_backward/api.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/cudnn/deepseek_sparse_attention/sparse_attention_backward/api.py)
- [nvidia-cudnn-frontend: python/cudnn/_pygraph.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/cudnn/_pygraph.py)
