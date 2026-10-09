---
id: official-transformer-engine-wiki/fusion-and-profiling
title: TE 融合与形状级分析：OperationFuser 和 GEMM 教程
engine: transformer-engine
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-transformerengine
  path: docs/examples/op_fuser/op_fuser.rst
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 95497fc7b153ba375d9687e6ce2333bdfee40da6f3653555624c274f9cf5f71d
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/ops/fuser.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: c7dda3b60819734a9a03f2e03d80731937e35d5d42bc1c7150c52694e14fc536
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/ops/sequential.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: af744cf91b0a6632df9fc1e63b25df0ebcd57a914a9080b74d35cc07883d0a91
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/module/layernorm_mlp.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 762c24279fc290e28aa274a4550b1c7f2dd63671f37a889dc3be802bc5b2511c
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/module/grouped_linear.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 18018750d7fcaab0ff8bbbda29350a4845c6ba1065339b1e503eaeba927a46da
- source: nvidia-transformerengine
  path: docs/examples/gemm_profiling/gemm_profiling.rst
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 31444db2fe36482719a7262091ea25ae69a95d13f898c19148b0b0efe91c52f2
- source: nvidia-transformerengine
  path: benchmarks/gemm/benchmark_gemm.py
  commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
  sha256: 365eb2888a4dbc293efd454dd26cad604fb4bf44bb7e3ef019eb0364065beef2
- source: nvidia-transformerengine-docs
  path: op-fuser
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: d9fd4f69b46d8609a88c27365f6a809f8b4e3290120485df51d2accd6e711a38
  url: https://docs.nvidia.com/deeplearning/transformer-engine/examples/op_fuser/op_fuser.html
  revision_kind: web-content-fingerprint
---

# TE 融合与形状级分析：OperationFuser 和 GEMM 教程

## 两种组织方式

TE 的模块式接口如 LayerNormMLP 将多个操作封装在一个类中；`te.ops.Sequential` 与 `FusibleOperation` 则允许从较小操作组合，由 `OperationFuser` 尝试匹配 forward/backward 融合。两者都要查看实际 kernel 和 saved tensors，不能根据 Python 层数量估算融合粒度。

阅读 `ops/fuser.py` 的注册与匹配、`sequential.py` 的组合，再对应模块实现。量化、通信、bias、activation、残差及 gradient accumulation 改变融合条件；forward 融合与 backward 融合分别登记。HCU 已有 TE/Flash-Train 能力优先复用，避免另写一套只适用当前模型的独立算子。

## 官方 GEMM profiling 教程怎么用

官方 `benchmarks/gemm/benchmark_gemm.py` 可以从模型配置推导 GEMM，并分别测 fprop、dgrad、wgrad 的形状与精度模式。教程默认 autocast 场景会包含量化成本，这和只测预量化 GEMM 的数值不能直接比较。官方脚本适用于它支持的 NVIDIA 环境；HCU 可复用建模方法和 shape，测量入口使用 HCU 对应工程。

训练 trace 提供的是当前 rank 的局部工作负载。TP/EP 切分、packing、padding、MoE 实际专家 token 分布都会改变 M/N/K；不能用全模型 hidden size 和全局 batch 直接替代本 rank shape。先捕获真实输入，再用教程的分析方法补充预估与检查。

## 与 TrainFlow 热点评估联动

1. 用集成 TraceLens 获取 CPU op、kernel、输入形状和 overlap 线索，并核对实际采样窗口。
2. 在累计覆盖至少 90% 端到端时间的热点集合中，为每个非通信 op 建模；CPU/等待缺口保留。
3. GEMM 分别记录算法 FLOPs、量化/转置/输出的字节量、匹配精度峰值及可达独立实测。Grouped GEMM 记录每专家 M 和 padding，attention 不简化成一个 GEMM。
4. 将 kernel 时间、整个 TE 调用时间、模型墙钟分开；缓存/融合可减少辅助工作，但也可能增加存活张量和峰值显存。
5. 发现实现差距才交给三个 Hygon 算子 Skill，完成局部数值和多 shape 回归后回到训练阶段 loss 验证。

不要拿文档的 H100/B200 示例速度当 HCU 峰值，也不要把单独 GEMM 提速相加当模型收益。优先级由实际占比、可达上限、实现成本和数值风险共同决定。

## 来源与版本复核

- [nvidia-transformerengine: docs/examples/op_fuser/op_fuser.rst](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/docs/examples/op_fuser/op_fuser.rst)
- [nvidia-transformerengine: transformer_engine/pytorch/ops/fuser.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/ops/fuser.py)
- [nvidia-transformerengine: transformer_engine/pytorch/ops/sequential.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/ops/sequential.py)
- [nvidia-transformerengine: transformer_engine/pytorch/module/layernorm_mlp.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/module/layernorm_mlp.py)
- [nvidia-transformerengine: transformer_engine/pytorch/module/grouped_linear.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/transformer_engine/pytorch/module/grouped_linear.py)
- [nvidia-transformerengine: docs/examples/gemm_profiling/gemm_profiling.rst](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/docs/examples/gemm_profiling/gemm_profiling.rst)
- [nvidia-transformerengine: benchmarks/gemm/benchmark_gemm.py](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/benchmarks/gemm/benchmark_gemm.py)
- [nvidia-transformerengine-docs: op-fuser](https://docs.nvidia.com/deeplearning/transformer-engine/examples/op_fuser/op_fuser.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码 main、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。
