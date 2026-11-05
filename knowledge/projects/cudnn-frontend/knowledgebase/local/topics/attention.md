---
id: official-cudnn-frontend-wiki/attention
title: cuDNN SDPA 训练：Forward、Backward、Stats 与布局
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
  path: docs/operations/Attention.md
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: d5bdab36ababaa8bd6dd58b72e6e5c1d46da70f3fbaa87902d693c75ce7d62d0
- source: nvidia-cudnn-frontend
  path: samples/python/50_sdpa_forward.ipynb
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 5269e5e9a40a4646ec36eaaee478eef6a79cbf252f107c77af8575bc58175f93
- source: nvidia-cudnn-frontend
  path: samples/python/51_sdpa_backward.ipynb
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: e530a489347cc811a7cf67319c48e479e100f32304abca90b6d0777f09032950
- source: nvidia-cudnn-frontend
  path: samples/cpp/sdpa/fp16_fwd.cpp
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 9fff38ca56811b429f8cae604a922bef70a68644df8e5c40ec4bf2ea51730384
- source: nvidia-cudnn-frontend
  path: samples/cpp/sdpa/fp16_bwd.cpp
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 62f47b922848b39b6ec9ee07f2dbac8e65b2f46cfffb1e327e9b050a4d9f6bc2
- source: nvidia-cudnn-frontend
  path: include/cudnn_frontend/node/scaled_dot_product_flash_attention.h
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 60c7612d76aac30412aaab47c024c1d21a5dd02b246e86ddc011886fc5ecd2d9
- source: nvidia-cudnn-frontend-docs
  path: attention
  commit: 62596f777aca773f340569b88fbd42c5fcd807249e8a188810cd38297d19cab9
  sha256: f768a9f63d014d2e96a65a25f01953f2d6c74e0e14dc39c751b4badbeb4ba73e
  url: https://docs.nvidia.com/cudnn/operations/Attention
  revision_kind: web-content-fingerprint
- source: nvidia-cudnn-frontend
  path: python/cudnn/sdpa/frost/SUPPORT_MATRIX_TRACKER.md
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 343333d056ad6ac4716b06ee250f3ced564276bb9474091161f8eff7c365e5fd
- source: nvidia-cudnn-frontend
  path: test/python/sdpa/frost/test_sdpa_split_combine_sm100.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 16c57ee9b324b8aec6348754d97a9eab1225395d7035bce5e834a4ca3869a59a
- source: nvidia-cudnn-frontend
  path: test/python/sdpa/frost/test_sdpa_fwd_decode_d256_sm107.py
  commit: f88a1ef2a35bc405967691dd798eb062298fcd9a
  sha256: 1e0ebc2ac4d9d2a870c206c6cb75dfa3b75f4c67e6ad4cd53a196b8ceaa7c0cb
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

## 当前 score、mask 与格式边界

`a7269d7607db` 文档明确 `attn_scale=None` 降为1.0，不自动生成 `1/sqrt(d)`。新增 `score_max` / `score_sum_exp` 为自然单位的每行 FP32 side output，满足 `stats = score_max + ln(score_sum_exp)`；sink 作为额外列参与。`stats_use_log2` 只改 stats 的输出约定，backward 仍要求自然对数 stats。空有效行按本实现约定 O=0、stats/max=-inf、sum=0；仅有 sink 时保留 sink 的质量。不能把另一库有限 mask 的 uniform-V 结果当同一种空行语义。

Python engines 的 `kv_mask` 与普通 bias 分开：Boolean false 真正排除 key，浮点值则加到 scores；全部为有限 `-1e9` 的行与 Boolean 全掩码不等价。该输入没有 cuDNN backend 字段；本固定开发线的支持矩阵已同时包含 SM107 和 SM100/SM103 小 head-dim forward tile 的特定 bias/kv_mask 路线，须继续核对 dtype、tile、长度和 support/dispatch，不能将旧教程的 SM107 范围当作当前全部实现。其他配置应明确 unsupported，不能静默丢 mask。score side output 目前限 SM100/SM103 与 SM107 的 f16/bf16 d128 prefill 资格：dense、unsplit、unpaged、2-CTA tile；不从接口参数存在推导所有训练反向支持。

FP8 `Amax_S` 已标为弃用，声明它为输出会排除 FROST FP8 选择；其值描述 softmax probabilities，不是 pre-softmax logits。源码文档根据 dropout/自定义 mask 给出 scale_s 的边界推导，不能把无 dropout 的448直接搬到所有模式，也不能将来源平台上的局部代价推成模型收益。Q/K/V/O 及反向张量的 stride/指针对齐检查见[Graph 专题](graph-and-plans.md#当前边界指针对齐计划排序与外部消费者)。

## 来源与版本复核

- [nvidia-cudnn-frontend: docs/operations/Attention.md](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/docs/operations/Attention.md)
- [nvidia-cudnn-frontend: samples/python/50_sdpa_forward.ipynb](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/samples/python/50_sdpa_forward.ipynb)
- [nvidia-cudnn-frontend: samples/python/51_sdpa_backward.ipynb](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/samples/python/51_sdpa_backward.ipynb)
- [nvidia-cudnn-frontend: samples/cpp/sdpa/fp16_fwd.cpp](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/samples/cpp/sdpa/fp16_fwd.cpp)
- [nvidia-cudnn-frontend: samples/cpp/sdpa/fp16_bwd.cpp](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/samples/cpp/sdpa/fp16_bwd.cpp)
- [nvidia-cudnn-frontend: include/cudnn_frontend/node/scaled_dot_product_flash_attention.h](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/include/cudnn_frontend/node/scaled_dot_product_flash_attention.h)
- [nvidia-cudnn-frontend-docs: attention](https://docs.nvidia.com/cudnn/operations/Attention)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## FROST 新实现与训练边界

当前 unified forward 的 compute_data_type 独立于 Q/K/V/O 存储类型：继承图设置，均未设置时为 FLOAT。cuDNN≥9.29 的头文件与实际 backend 才接受新属性通路；当前 backend 仍在 descriptor finalization 拒绝 HALF 请求，不能把参数可传解释为已有 FP16 累加 kernel。softmax/stats 仍为 FP32，composite 和 backward 不由此改变。

开发线扩充了 SM107 的 decode/PackGQA/split-KV 选择；某些 gate 融合在 split combine 的 FP32 合并值上完成一次舍入。Stats 保持独立于 gate，Amax_O 仍描述图中 gate 之前的值。这类接口/数值细节比 kernel 名相同更重要。paged、ragged、sink、动态 shape 的支持组合须以当前支持矩阵和实际 support/dispatch 为准，不能把某条 decode 路径的扩展直接用于训练 backward。

SM100/SM103 half-precision sink + split 路线先生成不含 sink 的 partials，再由 combine 将 sink 折入一次。有效但 keyless 的 Q 行输出 O=0、LSE=sink；超过 `seq_len_q` 的 padded Q 行仍为 O=0、LSE=-inf。两种行的 partials 可能相同，因此 combine 还须绑定 Q lengths；不能仅靠 partial LSE 推断 padding。`test_pointer_combine_sink_keeps_padded_query_rows_dead` 覆盖 lean、serial、decode combine 形式。这不扩大 quantized、gated 或 SM107 sink+split 的支持范围。

训练侧 `f88a1ef2a35b` 已将 `sdpa_bwd_sm100_d128` 与 d256 列为默认候选，仍按图条件排序，不能沿用旧 opt-in 结论，也不能由默认候选推导必选。d128 的 accumulation/recompute 分别有资格；THD 的 FP16/BF16 MHA 和 BF16 GQA/MQA 当前可在 cc10.0/10.3、公开 CuTeDSL≥4.8、正且可用 FP32 表示的 scale 等条件下准入，其他形状/模式仍须查当行矩阵。THD 各端口 origins、空序列和输出容量同属合同；workspace 和 launch 数按实际实现查询，不沿用其他 head-dim 的零 scratch 假设。

前向还扩展独立物理 origins 与混合 KV 存储：部分 D128 half Q/O 路线可直接读取 E4M3/E5M2 K/V，并在片上转换，不等于整段 FP8 attention；D192/V128、精确 Q/K576–V512 及 paged/split 各有单独资格。split partials 与最终 O/Stats 的布局、sink 只折入一次、自然对数与 log2 Stats 的转换均须随实际消费者核对。矩阵增加资格不自动改变所有 heuristic，也不自动扩展训练 backward。

另见 [FlexAttention plan 与 autograd](flex-attention-plans.md)；它的 interval-mask API 与通用任意 score modifier 不是同一支持面。

补充固定证据：

- [python/cudnn/sdpa/frost/SUPPORT_MATRIX_TRACKER.md](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/python/cudnn/sdpa/frost/SUPPORT_MATRIX_TRACKER.md)
- [test/python/sdpa/frost/test_sdpa_split_combine_sm100.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/test/python/sdpa/frost/test_sdpa_split_combine_sm100.py)
- [test/python/sdpa/frost/test_sdpa_fwd_decode_d256_sm107.py](https://github.com/NVIDIA/cudnn-frontend/blob/f88a1ef2a35bc405967691dd798eb062298fcd9a/test/python/sdpa/frost/test_sdpa_fwd_decode_d256_sm107.py)
