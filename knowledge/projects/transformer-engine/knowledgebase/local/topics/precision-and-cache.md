---
id: official-transformer-engine-wiki/precision-and-cache
title: TE 低精度训练：recipe、amax、权重缓存与反向状态
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
  path: transformer_engine/common/recipe/__init__.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 5a310fcc898d08283309d10fc768a7dd1b879a73fab73b342488dfb79131b10f
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/quantization.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 99bc9f487e38d5b1f43f8ec5a2c4b252af9ef4f8f0e75443d8fee32fce90a08b
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/fp8.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 54a2967ad103ddcffcaf7a1d10e7d9fcfa3a290772d9239c416fff391349f3a1
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/module/base.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 1be555cd755c77e4ce9dd4d4cfdd37d5a88d3f5c3dcd536e0856a1a0ac0a17b7
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/module/linear.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: e9252b8c18270c17ea700c4417fa0314de19905eac4da63051fa6743765b2781
- source: nvidia-transformerengine
  path: docs/examples/advanced_optimizations.ipynb
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 0d5d703679a7d3c16773112e8879879560a945600c168a95b27b22bc44f9a22a
- source: nvidia-transformerengine
  path: docs/features/low_precision_training/fp8_delayed_scaling/fp8_delayed_scaling.rst
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: e3930744fe783fa2311224d3d746cf15a10c3cee7fc46a9a27e4c6e8f99671d4
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
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/module/layernorm_mlp.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: 10c26a70ea6f8a29d257df8d22d326cd604ff33024684da2d726b7189185fb55
- source: nvidia-transformerengine
  path: transformer_engine/pytorch/ops/fuser.py
  commit: 720b25258be3b60f482afff8aef00d4cad88fa16
  sha256: db2aad0d18bc881e8887d54eb582ee646d4a487584e4d0b83ea76fdc3064adf4
---
# TE 低精度训练：recipe、amax、权重缓存与反向状态

## 先区分三个层次

参数的主副本、kernel 使用的量化副本、梯度/优化器状态不必同 dtype。仅看到输出 BF16，不能推断 GEMM 没用 FP8；仅开启 autocast，也不能证明权重常驻为量化格式。当前官方 `pytorch/fp8.py` 已标注为兼容旧内部导入的弃用入口，新的机制阅读以 `quantization.py` 和 recipe 为主，HCU 是否同步该变化要单独核对。

## recipe 与数据流

| recipe 类 | 阅读重点与迁移约束 |
| --- | --- |
| `DelayedScaling` | 使用历史 amax 选 scale，当前量化结果再更新历史；检查历史长度、更新时点、归约 group 与重算行为。 |
| `Float8CurrentScaling` | 根据当前 tensor 计算 scale；把 amax 计算与量化成本一起纳入测量。 |
| `Float8BlockScaling`、`MXFP8BlockScaling` | 按块的 scale、行列表示、转置与 GEMM 消费布局；不能仅改一个 dtype。 |
| `NVFP4BlockScaling`、`CustomRecipe` | 格式、缩放及可配置量化逻辑有架构限制；HCU 需先确认实现能力与数值契约。 |

从模块 forward 的输入/权重 quantizer 到 GEMM、saved tensor，再到 backward 的 grad_output、dgrad、wgrad quantizer逐项画出数据生命周期。量化布局转换、amax/scale 更新和跨 rank 同步可能带来额外 kernel/collective；这些也属于端到端开销。

## 案例：梯度累积周期内复用低精度权重

**瓶颈**：多个 microbatch 使用同一份未更新权重，重复量化增加带宽和 launch 开销。

**官方机制**：教程在累积周期的第一个 microbatch 传 `is_first_microbatch=True`，后续传 False；沿 `module/linear.py` 的 weight workspace 和 `module/base.py` 的缓存处理查实际复用路径。它依赖训练调度告诉模块何时权重发生更新。

**适用条件**：同一参数版本、兼容 recipe/布局与当前模块实现。优化器更新、重新加载 checkpoint、参数 gather、offload 或 graph 改变存储时，不能默认旧副本仍有效。主权重不变也不意味着 amax 历史不变，官方教程明确提醒启用缓存可能不逐位等价。

**验证步骤**：连续两个以上 microbatch 比较缓存开关；观察 cast/transpose 数量、缓存显存、输出及 dgrad/wgrad；跨 optimizer step 再比较，随后验证重算、checkpoint 和阶段 loss。不能只测一个 forward，也不能把长期 False 当作最快固定设置。

**回退**：恢复原模块的每次量化策略及相同数值基线，并确认没有残留缓存/graph 状态。若收益小于噪声或显存代价抵消收益，则保留原实现。

当前 `720b25258be3` 的 Linear 编译路径已允许 CPU `is_first_microbatch` 控制的 FP8 cache：首个 microbatch 新建并替换副本，后续复用；GPU tensor 控制的 skip-update 与 `fuse_wgrad_accumulation=True` 仍不能据此进入该 functional 路径。`reduce-overhead` 模式要求在每个 minibatch 前调用 `torch.compiler.cudagraph_mark_step_begin()`，保住该 minibatch 内各 microbatch 共用的副本；不要每个 microbatch 重设边界。

recipe 本身也是缓存身份。`Recipe.__repr__` 现在包含新增的公开属性并在增删/改值时失效，OperationFuser 用 recipe 字符串和首个反向 op 边界选择计划。当前 Blackwell 及后续架构以 MXFP8 模拟 FP8 block scaling，三个量化角色均要求 power-of-2 scales；关闭该条件会被支持检查拒绝，不能仅凭 recipe 类名沿用旧缓存。

## 主梯度 dummy 的存储与设备

当前 `get_dummy_wgrad` 的普通缓存将当前 CUDA device 纳入 key，避免同 shape/dtype 的不同设备拿到同一 dummy。`zero_out_wgrad` 要求真实清零；另有参数属性 `zero_tensor_dummy_wgrad` 可请求无底层 storage 的 ZeroTensor，让同一权重在一次 backward 被多次使用时减少无意义的 dummy 加法。两者不是主梯度本身；实际 GEMM/主梯度累加和 hook 标志仍须正确执行。

`Linear`、`LayerNormMLP` 与 GroupedLinear 的结束路径要一起看，不能将 dummy 返回值当作 optimizer 消费的真实 wgrad。缓存优化仍需覆盖复用权重、多 microbatch、跨设备和 zero-out；当前源码改动不等于这些组合已在目标 HCU 上执行。

## 精度诊断

固定输入、RNG、mask、归约方式和初始权重，从首个发生偏差的层开始检查 scale/amax、饱和、舍入、cast 与累积精度。启用 FP32 主梯度融合时检查 `main_grad` 的分配、累加和清零时点。每轮做局部回归；较长 loss 在稳定的优化阶段验收，符合训练工作流原约定。

## 来源与版本复核

- [nvidia-transformerengine: transformer_engine/common/recipe/__init__.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/common/recipe/__init__.py)
- [nvidia-transformerengine: transformer_engine/pytorch/quantization.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/quantization.py)
- [nvidia-transformerengine: transformer_engine/pytorch/fp8.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/fp8.py)
- [nvidia-transformerengine: transformer_engine/pytorch/module/base.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/module/base.py)
- [nvidia-transformerengine: transformer_engine/pytorch/module/linear.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/module/linear.py)
- [nvidia-transformerengine: docs/examples/advanced_optimizations.ipynb](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/examples/advanced_optimizations.ipynb)
- [nvidia-transformerengine: docs/features/low_precision_training/fp8_delayed_scaling/fp8_delayed_scaling.rst](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/docs/features/low_precision_training/fp8_delayed_scaling/fp8_delayed_scaling.rst)
- [nvidia-transformerengine-docs: fp8-primer](https://docs.nvidia.com/deeplearning/transformer-engine/examples/fp8_primer.html)
- [nvidia-transformerengine-docs: advanced-optimizations](https://docs.nvidia.com/deeplearning/transformer-engine/examples/advanced_optimizations.html)

本文根据列出的固定源码和教程整理。官网内容指纹与 Git 提交分别记录；官网最新、源码分支、已发布 wheel 和实际 HCU 分支不是同一个版本。以上为源码/教程阅读与 HCU 适配建议，未在 HCU 上执行这些 NVIDIA 示例或宣称性能、loss 验证通过。更新时同时复核本页、同库总览、相关案例及 Skill。

## 本次补充的实现与测试依据

- [nvidia-transformerengine: transformer_engine/pytorch/module/layernorm_mlp.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/module/layernorm_mlp.py)

- [transformer_engine/pytorch/ops/fuser.py](https://github.com/NVIDIA/TransformerEngine/blob/720b25258be3b60f482afff8aef00d4cad88fa16/transformer_engine/pytorch/ops/fuser.py)
