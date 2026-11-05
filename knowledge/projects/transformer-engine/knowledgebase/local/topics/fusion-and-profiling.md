---
id: official-transformer-engine-wiki/fusion-and-profiling
title: TE 融合与形状级分析：OperationFuser 和 GEMM 教程
engine: transformer-engine
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
- source: nvidia-transformerengine
  path: docs/examples/op_fuser/op_fuser.rst
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 95497fc7b153ba375d9687e6ce2333bdfee40da6f3653555624c274f9cf5f71d
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/ops/fuser.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: db2aad0d18bc881e8887d54eb582ee646d4a487584e4d0b83ea76fdc3064adf4
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/ops/sequential.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: ebb47e64acc5cad6b267437f6e751850827a4b9ac66f5c40e4515e6edb850c73
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/module/layernorm_mlp.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 10c26a70ea6f8a29d257df8d22d326cd604ff33024684da2d726b7189185fb55
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/module/grouped_linear.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 81285c46ceb62f2b01fe4331ca6c74de18f0ccc1f81085d5d6509b00b98ac9ce
- source: nvidia-transformerengine
  path: docs/examples/gemm_profiling/gemm_profiling.rst
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 31444db2fe36482719a7262091ea25ae69a95d13f898c19148b0b0efe91c52f2
- source: nvidia-transformerengine
  path: benchmarks/gemm/benchmark_gemm.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 365eb2888a4dbc293efd454dd26cad604fb4bf44bb7e3ef019eb0364065beef2
- source: nvidia-transformerengine-docs
  path: op-fuser
  commit: 7d26f4a31e4eae8c11f1eadb6a5deee3f2123b88ac0397752c1fe8d1d2a41878
  sha256: d9fd4f69b46d8609a88c27365f6a809f8b4e3290120485df51d2accd6e711a38
  url: https://docs.nvidia.com/deeplearning/transformer-engine/examples/op_fuser/op_fuser.html
  revision_kind: web-content-fingerprint
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/ops/basic/grouped_linear.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: d8a8dacdc5c192408a93258968e96dbd178a208b5e9c95ffcc44e5f3ed9e2823
- source: nvidia-transformerengine
  path: tests/pytorch/test_grouped_mlp.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: fd23ca189afa3771c15706d8b5f52cf01955b2c0c9dadc945938afe5ab75577f
- source: nvidia-transformerengine
  path: docs/envvars.rst
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 5a2bc2206a8602f90ba8ca3aa00c921f23caa5795baa3149953bad5767f4b99a
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/ops/fused/grouped_mlp.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 4d60a9a3c400a27f1f4243e8bd76fe39ec2e99da753d2b878943685e42a8ffc1
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/quantization.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 99bc9f487e38d5b1f43f8ec5a2c4b252af9ef4f8f0e75443d8fee32fce90a08b
---
# TE 融合与形状级分析：OperationFuser 和 GEMM 教程

## 两种组织方式

TE 的模块式接口如 LayerNormMLP 将多个操作封装在一个类中；`te.ops.Sequential` 与 `FusibleOperation` 则允许从较小操作组合，由 `OperationFuser` 尝试匹配 forward/backward 融合。两者都要查看实际 kernel 和 saved tensors，不能根据 Python 层数量估算融合粒度。

阅读 `ops/fuser.py` 的注册与匹配、`sequential.py` 的组合，再对应模块实现。量化、通信、bias、activation、残差及 gradient accumulation 改变融合条件；forward 融合与 backward 融合分别登记。HCU 已有 TE/Flash-Train 能力优先复用，避免另写一套只适用当前模型的独立算子。

## Grouped MLP 的当前准入与参数重置

在 `eb3c860a4d33`，GroupedLinear→scaled activation→GroupedLinear 的融合先检查真实操作序列和 recipe，再探测设备/后端，避免无关 `Sequential` 在 tracing 时触发能力查询。MXFP8 的反向仍要求 E4M3，HYBRID/E5M2 不准入；NVFP4 的 graph-safe grouped quantization 要求 RHT，CustomRecipe 需明确启用对应能力。前后两个 ops.GroupedLinear 声明的 `split_alignment` 都须被256整除，不满足则告警跳过融合。

`NVTE_CUTEDSL_FUSED_GROUPED_MLP` 已弃用：兼容读取会将 split alignment 覆盖为256并告警；当前接入应显式声明实际分片对齐，不能只设环境变量当作数据已满足条件。native GroupedTensor 的单参数权重/偏置还受设备、dtype、recipe 和功能组合约束，不能在不支持时静默拆回离散参数。`Sequential.reset_parameters()` 会清 `_module_groups` 再逐模块重置，避免 fuser 持有已经被替换的旧参数。

当前 `test_grouped_mlp.py` 在相同 basic ops/quantizer wiring 下分别保留 fusion on/off 路线，并检查前后向实际融合；只有吞吐或模块名相同不够。单 group 与冻结参数的新增边界见[权重布局案例](../cases/grouped-mlp-weight-layout.md)。

2026-11-04 的普通 GroupedLinear 将 `split_alignment` 默认改为 None：按实际 recipe/设备解析为块缩放128、Hopper current-scaling 16、其他1；GPU offset 生成同时校验每个 split，捕获后重放也不能靠虚报对齐绕过。block-scaled 融合仍要求实际256对齐，MXFP8 canonical-layout 则按 cuDNN wrapper 的能力标志选择，不能沿用旧 kernel-facing view。

新 `GroupedMLP_CuTeGEMMGLUBf16` 是独立未量化路线：仅 recipe=None、BF16 权重/计算、受支持 GLU 和匹配的 SM10.x（minor<7），并探测 cuDNN Frontend 版本及 canonical-layout 能力。每专家和总 token 对齐均为256；FC1 scale_bias、不匹配的分布式权重组合、部分确定性梯度要求均有拒绝条件。当前 matcher 尚直接对 `split_alignment` 取模，未像 block-scaled 路线先解析 None；静态调用链显示匹配窗口在能力门通过后可能因省略该参数而失败。接入时显式声明真实对齐，保留默认参数的准入回归待验证，不将此源码观察写成本轮 GPU 重现。

分布式权重还需保存该次 forward 的 quantizer：backward 重新 gather BF16 shard 后按所保存 recipe 量化，不能从已被后续 forward 替换的 live op 读取。wgrad 的 dtype、外部 main_grad alias、独立结果与 reduce-scatter 分别核对；延后 wgrad 已改为跨 tied 参数和 microbatch 累加，不能覆盖前一贡献。

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

- [nvidia-transformerengine: docs/examples/op_fuser/op_fuser.rst](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/examples/op_fuser/op_fuser.rst)
- [nvidia-transformerengine: transformer_engine/pytorch/ops/fuser.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/ops/fuser.py)
- [nvidia-transformerengine: transformer_engine/pytorch/ops/sequential.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/ops/sequential.py)
- [nvidia-transformerengine: transformer_engine/pytorch/module/layernorm_mlp.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/module/layernorm_mlp.py)
- [nvidia-transformerengine: transformer_engine/pytorch/module/grouped_linear.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/module/grouped_linear.py)
- [nvidia-transformerengine: docs/examples/gemm_profiling/gemm_profiling.rst](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/examples/gemm_profiling/gemm_profiling.rst)
- [nvidia-transformerengine: benchmarks/gemm/benchmark_gemm.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/benchmarks/gemm/benchmark_gemm.py)
- [nvidia-transformerengine-docs: op-fuser](https://docs.nvidia.com/deeplearning/transformer-engine/examples/op_fuser/op_fuser.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## 本次补充的实现与测试依据

- [nvidia-transformerengine: transformer_engine/pytorch/ops/basic/grouped_linear.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/ops/basic/grouped_linear.py)
- [nvidia-transformerengine: tests/pytorch/test_grouped_mlp.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/tests/pytorch/test_grouped_mlp.py)
- [nvidia-transformerengine: docs/envvars.rst](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/envvars.rst)

- [transformer_engine/pytorch/ops/fused/grouped_mlp.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/ops/fused/grouped_mlp.py)

- [transformer_engine/pytorch/quantization.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/quantization.py)
