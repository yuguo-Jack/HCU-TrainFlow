---
id: official-torchtitan-wiki/training-and-numerics
title: TorchTitan 训练循环、有效 token、优化器与数值诊断
engine: torchtitan
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-11-04'
retrieved_on: '2026-11-04'
coverage: Curated source chains and official evidence at a fixed main commit; not all models, backends
  or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/trainer.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 1e03e753238c07818a9b238b9264001cd3223528e5d18e4316eb88be14175135
- source: pytorch-torchtitan
  path: torchtitan/training_engine.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 2ffe06874d3a03ccc91d407f1bc91d5f2beaa9c746738dd3a3646f1c800a798f
- source: pytorch-torchtitan
  path: torchtitan/components/optim/optim.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: b93bb590ff7c7eec2d1bd9c2668ad668bf3bee1e944fbe6b0e0415b2474e154b
- source: pytorch-torchtitan
  path: torchtitan/components/optim/optimizer.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 6c7d17ccb890fca4c6e39df353ea1fff160e04d31a25e909a7e26bc8c29d1b35
- source: pytorch-torchtitan
  path: torchtitan/components/optim/BF16_OPTIMIZER_STATES.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 70caaed9c8fe066019fa8404dc2d3827582e865ecc3fb7f6a7459b751d71e4cb
- source: pytorch-torchtitan
  path: torchtitan/distributed/fsdp.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: ae80b4bd15521159e1041142726e9717c3d952399b273889e5fca11caa221e81
- source: pytorch-torchtitan
  path: torchtitan/rl/BITWISE_PARITY.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 830da7e6052e07ab5a9cc302436dc1ece1d97955a4fa28b66ec8e9833e2f3ac7
- source: pytorch-torchtitan
  path: torchtitan/config/configs.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 3465866709813651cc91114c4a006a5cc3c05d6069e9f04200e68d10c91c3659
- source: pytorch-torchtitan
  path: tests/unit_tests/cpu/test_trainer.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: b9681edfc274190ede7dcbba70a8bc82b814b51d4facf3618feb3c6961e0891d
- source: pytorch-torchtitan
  path: tests/unit_tests/gpu/models/common/test_linear_inplace_wgrad_accum.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 999896227598f0af578966cb1b968f34a45e8b25dadd16568d26055a1600c35e
- source: pytorch-torchtitan
  path: torchtitan/models/base/module.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 68d6ed42a6b0b95baba44774bb119123ffbe7c63217248b60e5a479ab4ed7e5f
- source: pytorch-torchtitan
  path: torchtitan/components/checkpointer/base.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 2bd520490169c93d8c4a3d1a70054a96ffb1082db67cab68f007d21a242ba38d
- source: pytorch-torchtitan
  path: torchtitan/rl/trainer/trainer.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: f52d1d78a769b06bc511dc638486626592d0f0bdbd249d14a2f8df4107d0c3b3
- source: pytorch-torchtitan
  path: torchtitan/distributed/utils.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 11910a1dcf3c54cec3896998e21222ae4c3053901fdaf6d89670dd722108da7f

pr_sources:
- pr-pytorch--torchtitan-5250
- pr-pytorch--torchtitan-5137
---
# TorchTitan 训练循环、有效 token、优化器与数值诊断

## 调用链与职责

`train.main` 加载 Config 并构建 Trainer；监督训练由 `Trainer.train` 进行 checkpoint 加载、逐步训练、保存、验证与 profiler 推进。`Trainer.train_step` 组织 microbatch groups 和有效 token，调用 `TrainingEngine.forward_backward`，然后 `optim_step`，最后计算日志指标。`TrainingEngine` 统一模型/优化器/状态接口，RL 在另一个循环里复用它。

因此 loss 错误可能来自数据与 token 分母，吞吐下降可能来自 checkpoint/validation，梯度丢失可能来自 graph 或原地累积。只比较模型 forward 不足以解释整个训练步骤。

## 精度配置与受保护参数

根 `PrecisionConfig.dtype` 默认 FP32，描述参数/梯度/优化器状态的基础 dtype；`param_dtype` 默认 BF16，供 FSDP mixed precision 或适用的 autocast 使用；`reduce_dtype` 默认 FP32，适用范围由实际 FSDP 路径决定。BF16 optimizer moments 是另一项实现选择，不能由根字段推断每个状态 tensor 的最终 dtype。

`Module.Config.preserve_dtype_params` 指定本模块自己的参数名，构造时拒绝未知名；`named_preserve_dtype_params()` 在使用时查实际参数。FSDP mixed-precision policy、checkpoint export 和 RL transfer 分别消费它，保留比目标更宽的参数精度。不能只在模型初始化保留 FP32，而在导出/同步时又悄悄降精度。

## Token 预算与归一化

令每 DP rank 的 microbatch token 预算为 `Tmicro`，PP microbatch 数为 `Npp`，DP degree 为 `Ddp`，则一个 accumulation 单元对应 `Tmicro × Npp × Ddp` 的配置 token 预算。`num_tokens_per_train_step` 必须与该单位相容，Trainer 由它计算梯度累积次数；实际参与 loss 的 token 还要扣除 mask/padding。

`loss_token_counts` 与 MoE `routing_token_counts` 分开统计。Trainer 汇总有效 loss token，再给引擎计算对应缩放；日志以 token 加权归约，不应变成各 rank 平均 loss 的简单平均。该实现把 FSDP gradient divide factor 设为 1，以配合显式 loss 归一化；移植时再除一次 DP 会改变梯度。

检查顺序：同输入和 mask → 每 rank token 数 → 全局有效分母 → microbatch/累积/CP 分配 → loss reduction → 反向缩放 → optimizer update。SFT、变长或 RL 场景尤其不能仅检查最终一个 loss 标量。

## 优化器步骤与状态

`Optim` 负责 clip grad norm、跨域非有限检查、参数更新与 scheduler。当前更新前要求 loss 和 grad norm 为有限值；遇到 NaN/Inf 应保留第一个异常的层、rank、输入和状态，不能靠把日志中的 NaN 隐去或扩大容差继续。

核对参数 pattern 的归属、foreach/fused 实际分发、Muon 与 AdamW 的职责、step 计数、LR、weight decay、累积和 zero_grad。graph replay、原地 WGRAD 或分离 dInput/dWeight 的 PP schedule 都会影响 `.grad` 的所有权；见 [WGRAD 案例](../cases/inplace-wgrad-accumulation.md)。

BF16 optimizer states 将 Adam/AdamW moment 与模型计算精度解耦：参数/主权重、前向计算、通信归约、moment dtype 分别记录。官方方案要求匹配的 fused optimizer，通过 hook 创建/恢复 BF16 moments；加载时仍可能出现临时 FP32 峰值。它不意味着所有 optimizer 都能直接改成 BF16 状态。

## 优化后的精度验证

1. 固定源码、依赖、配置、初始权重、数据及 RNG，先确认参考本身稳定。
2. 检查局部前向、输入梯度、权重梯度；低精度融合应对照同 dtype 实现，必要时追加高精度 oracle。不要把高精度更近直接当作与原训练相同。
3. 检查一次 optimizer update 后参数与状态，再验证多 microbatch、多个 DP/TP/CP/EP/PP 组合的真实通信。
4. 采用短回归筛查和阶段性 loss/质量验证；不为每次低风险局部修改重复长训，但归约次序、优化器、量化或数据语义改变不能仅用几步无 NaN 放行。
5. 没有 NVIDIA 对照时，使用同 HCU 环境保守实现/关闭融合前的固定基线、逐层 tensor 与状态比较；有对照时还需同模型、同数据、同训练语义，不能把不同引擎默认差异归咎于硬件。

源代码、上游 golden、作者在某 GPU 的测试与本任务 HCU 验证分别记录。修改 golden 必须有机制解释和证据，不为通过测试直接接受更大的误差。

## 常见定位入口

| 现象 | 优先核查 |
| --- | --- |
| DP/packing 一变 loss 就变 | 有效 token 分母、mask、重复缩放、数据顺序 |
| 首步一致，累积后偏离 | WGRAD 舍入位置、zero_grad、累积次数、dropout/recompute RNG |
| loss 正常但参数不动 | `.grad` 是否丢失、optimizer pattern、graph replay、有限检查 |
| checkpoint 恢复后突变 | optimizer/scheduler/step/RNG/数据游标，以及导出是否 model-only |
| RL trainer/generator logprob 不同 | policy 版本、TP/attention/序列布局、计算 dtype、采样与批次不变性 |

工作流中的 HCU Probe、阶段 loss 及上层精度诊断见 [模型精度排查](../../../../../../docs/practices/model-accuracy-diagnosis.md)。

## PP loss 接口与首轮状态

`ForwardBackwardResult.loss_metrics` 当前按 `[microbatch group][microbatch]` 嵌套；PP为每个 microbatch 单独传 loss kwargs（如advantages）与 metrics dict，非最后stage没有有效 loss metrics。pipeline 元数据初始化可能先调用一次 loss，wrapper对目标 metrics执行clear/update，不能把探测调用再累计进正式日志。自定义 loss/监控消费者若仍按每组一个dict读取会混淆统计。

全局 routing-token counts 在 `preprocess_inputs` 中传入模型，不再依赖引擎事后修改特定 kwargs；loss-token 与 routing-token 分母仍分别计算。惰性预处理把每组输入/掩码临近前后向才物化，不能据此重算或改变全局分母。

首个 WGRAD 也有精度变化：有更宽的 `weight.grad_dtype` 时，当前 Linear 直接让 GEMM输出该 dtype，跳过先舍入到 BF16再由autograd转FP32；`test_first_wgrad_is_produced_in_grad_dtype` 单独检查这一点。历史PR的首步bitwise结论不能覆盖这次变化，详见[案例](../cases/inplace-wgrad-accumulation.md)。

每个新 `Optim` 实例第一次 `step()` 在更新图外通过当前 `device_module` 等待已初始化设备工作，再释放未使用的缓存；CPU 模型不会因此初始化尚未使用的 CUDA/XPU context，为NCCL外部分配让出空间；恢复到非零step也执行。它不释放live tensor/Graph pool、不减小通信buffer，也不能解决此前forward/backward或后续分配失败；性能基线应把这次首轮等待单列。

## Clip 接口与 DistMuon 通信的独立约束

`Optim.Config.gradient_clipper` 可替换 optimizer-owned clip 实现；默认调用 `dist_utils.clip_grad_norm_(foreach=True, pp_mesh=...)`。返回值必须是每 rank 等价的、裁剪前全局 L2 norm 的本地零维 tensor，保留 NaN/Inf，不能被改写为 clip coefficient 或 scratch。有限值检查和参数更新仍消费该返回值；scheduler/EMA 在捕获的 update 之外推进。

`DistMuon.Config.ns_device="accelerator"` 只将 Newton–Schulz 矩阵计算临时搬到当前加速器；host-offload 参数、momentum、梯度和 rank exchange 仍留在原存储位置。`max_nccl_ctas_for_comms<=0` 默认关闭；正值为匹配 bucket 的 shard mesh 建资源独立的 NCCL child communicator，不改变 FSDP 原 communicator，但新增固定 workspace，较少 CTA 也可能降低带宽。非 NCCL 拒绝、fake 仅警告，不能以 fake 检查证明节省真实通信内存；HCU/RCCL 适用性需单独验证。

## 固定证据与使用边界

本页以官方主线 `485c065cb248863bf2e2c65588becd6d7a8bcf83` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/trainer.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/trainer.py)
- [torchtitan/training_engine.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/training_engine.py)
- [torchtitan/components/optim/optim.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/components/optim/optim.py)
- [torchtitan/components/optim/optimizer.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/components/optim/optimizer.py)
- [torchtitan/components/optim/BF16_OPTIMIZER_STATES.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/components/optim/BF16_OPTIMIZER_STATES.md)
- [torchtitan/distributed/fsdp.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/fsdp.py)
- [torchtitan/rl/BITWISE_PARITY.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/BITWISE_PARITY.md)

- [PR #5250：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5250.md)
- [PR #5137：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5137.md)

## 本次补充的实现与测试依据

- [torchtitan/config/configs.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/configs.py)
- [tests/unit_tests/cpu/test_trainer.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/unit_tests/cpu/test_trainer.py)
- [tests/unit_tests/gpu/models/common/test_linear_inplace_wgrad_accum.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/unit_tests/gpu/models/common/test_linear_inplace_wgrad_accum.py)

- [torchtitan/models/base/module.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/models/base/module.py)

- [torchtitan/components/checkpointer/base.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/components/checkpointer/base.py)

- [torchtitan/rl/trainer/trainer.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/trainer/trainer.py)

- [torchtitan/distributed/utils.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/utils.py)
