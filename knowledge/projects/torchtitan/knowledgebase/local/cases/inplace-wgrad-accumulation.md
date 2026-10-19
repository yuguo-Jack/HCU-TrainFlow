---
id: official-torchtitan-wiki/cases/inplace-wgrad-accumulation
title: 案例：TorchTitan WGRAD 原地累积的显存收益与梯度所有权
engine: torchtitan
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-20'
coverage: Curated source chains and official evidence at a fixed main commit; not all models, backends
  or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/models/common/linear/inplace_wgrad_accum.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: b1086699045a0c753df637460512eede4448772ba78c17c23f7863c9987df467
- source: pytorch-torchtitan
  path: torchtitan/models/common/linear/linear.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 6fa01212bbaa44502862b3aba0b16e1955a77a09cbda6ff304839836a42834f0
- source: pytorch-torchtitan
  path: torchtitan/models/common/linear/async_linear.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 9ea047214c1b0991e9dac6183b95f26b6e18bd2d3796761ab7472a429b02aa93
- source: pytorch-torchtitan
  path: torchtitan/distributed/pipeline_parallel.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 1da335028a5e6360ecdcbe554ea0711b43cba0949c10ac912ebd22a7534ec751
- source: pytorch-torchtitan
  path: torchtitan/experiments/graph_trainer/tests/test_inplace_wgrad_accum_config.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: e2939367a48d17d4f73c2cc5cbc08bf426d13f05681a5a7a49b8ba73bb4f5a92
- source: pytorch-torchtitan
  path: tests/unit_tests/cpu/models/common/test_inplace_wgrad_accum.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: bcc6eed8715c641b527105560918284e40a032dd1cce97af4d5bcb97a42cd811
- source: pytorch-torchtitan
  path: tests/unit_tests/gpu/models/common/test_linear_inplace_wgrad_accum.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 999896227598f0af578966cb1b968f34a45e8b25dadd16568d26055a1600c35e
pr_sources:
- pr-pytorch--torchtitan-5137
- pr-pytorch--torchtitan-5250
---
# 案例：TorchTitan WGRAD 原地累积的显存收益与梯度所有权

## 问题与优化目标

梯度累积中，Linear backward 常先生成完整 dW 临时张量，再由 AccumulateGrad 加入 `weight.grad`。大 LM head 的 `[vocab,D]` 梯度会造成一次额外的高带宽读写和显存峰值。PR #5137 先优化 HiMidLo LM head，#5250 扩展到 BF16 Linear 及相关路径；这是同一类生命周期优化，并非所有 Linear 后端都可直接套用。

## 为什么这样改、代码怎么走

当前调用链：`Linear.Config.inplace_wgrad_accum` → `models/common/linear/linear.py::_LinearFunction` → 同包 `inplace_wgrad_accum.py` helper → GEMM累加到已有gradient buffer → autograd重新接管该buffer。旧顶层common/linear.py/helper路径已迁移。

helper 处理已有 `.grad` 时，需要在写入后清空参数上的旧引用，再将同一 buffer 返回给 AccumulateGrad，防止 autograd 把它再加一次变成自我翻倍。没有已有梯度时正常计算首个梯度；开关开启却遇到非叶子参数或编译/追踪时，helper 会主动报错，需要由调用路径明确关闭功能。不能仅把 `addmm` 的 out 指到 `.grad`，也不能把这些拒绝条件描述成自动静默回退。

BF16 路径在累积阶段使用GEMM accumulator和原有buffer，改变“每microbatch先舍入再相加”的位置。本固定开发线还改变了首个梯度：若 `weight.grad_dtype` 比输入更宽，首个GEMM直接以该dtype写出；grad_dtype为None或与输入相同才沿普通mm路径。FSDP FP32 reduce dtype下首步也可能区别于先BF16再upcast，因此PR #5250历史首步bitwise结论不能当当前全部路径的承诺。autocast、NVFP4、Async TP等组合仍按当前拒绝/禁用条件核对。

## PP 与 Graph 的失败条件

ZeroBubble 类 schedule 可分开求 dInput 与 dWeight，使用 `autograd.grad` 而不经过常规 AccumulateGrad 重新挂接 `.grad`。这与上面的所有权协议冲突；`pipeline_parallel.py` 会按 schedule 关闭不支持的原地累积，GraphTrainer 的追踪路径也有相应禁用测试。

验证矩阵至少覆盖：无累积/多 microbatch、已有/空 `.grad`、普通 backward/分离 backward、PP schedule、FSDP 分片、eager/compile/graph，以及 fp32/bf16 所选实现。直接去掉禁用条件会有梯度丢失或重复的风险。

## 上游证据与可迁移边界

#5137 作者在 H100、Qwen3-8B LM head、chunk size 2 的测试中报告约 11.98→9.19 ms、峰值 3.54→1.22 GiB；其指定测试的梯度对齐结论不能外推到 #5250 的所有 BF16 累积路径。本轮只核查 PR、review 和固定源码，没有复测这些数字。

HCU 的借鉴点是减少大 dW 临时量和重复显存读写，同时保留 autograd/PP/optimizer 状态协议。应先看真实 profile 中该路径占比，再用同 shape、dtype、布局及累积次数做独立 benchmark，统计实际 bytes/峰值和可达带宽。若数学库 GEMM 本身已高效，收益可能主要来自少一次内存访问；若不是，再提供可复现 bench 日志开展库层优化。

## 正确性、性能与回退

先比较每 microbatch 的 dW、最终累计梯度、参数更新与 optimizer 状态，再做阶段 loss。失败时关闭本功能或退到受支持 schedule，不为了保留收益切换优化器或放宽精度标准。最后必须测模型稳态和显存 headroom，记录此改动是否让 microbatch 或并行方案获得新的可用空间。

当前测试入口：CPU `tests/unit_tests/cpu/models/common/test_inplace_wgrad_accum.py` 覆盖 leaf/tracing 拒绝、running grad 和 split-backward 禁用；GPU `tests/unit_tests/gpu/models/common/test_linear_inplace_wgrad_accum.py` 现单独检查首个GEMM返回FP32及最终grad逐位等于FP32-output mm，另覆盖BF16 WGRAD到FP32 running grad、stacked projections与双卡FSDP多microbatch；GraphTrainer 另有配置禁用回归。这里只核对测试内容，未执行这些上游 GPU 测试。

## 固定证据与使用边界

本页以官方主线 `a242475253433725f10f39c18f5ccbfdf188e097` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/models/common/linear/inplace_wgrad_accum.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/models/common/linear/inplace_wgrad_accum.py)
- [torchtitan/models/common/linear/linear.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/models/common/linear/linear.py)
- [torchtitan/models/common/linear/async_linear.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/models/common/linear/async_linear.py)
- [torchtitan/distributed/pipeline_parallel.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/pipeline_parallel.py)
- [torchtitan/experiments/graph_trainer/tests/test_inplace_wgrad_accum_config.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/experiments/graph_trainer/tests/test_inplace_wgrad_accum_config.py)
- [tests/unit_tests/cpu/models/common/test_inplace_wgrad_accum.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/unit_tests/cpu/models/common/test_inplace_wgrad_accum.py)
- [tests/unit_tests/gpu/models/common/test_linear_inplace_wgrad_accum.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/unit_tests/gpu/models/common/test_linear_inplace_wgrad_accum.py)

- [PR #5137：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5137.md)
- [PR #5250：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5250.md)