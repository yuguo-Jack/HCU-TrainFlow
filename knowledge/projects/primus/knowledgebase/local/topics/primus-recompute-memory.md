---
id: ecosystem/topics/primus-recompute-memory
title: Primus：按全局层选择重算、MTP 与低精度状态
engine: primus
kind: authored
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-11-04'
coverage: frozen source delta and consumer review; unchanged files rechecked; no HCU runtime validation
sources:
- source: amd-agi-primus
  path: primus/backends/megatron/patches/recompute_layer_patches.py
  commit: bab82720d72cadbdfbedcc050c9fb49de3b353be
  sha256: 689372168818ec24bc9147b611aac22b99a45b6e183a1dd5492b5337cb9332c5
- source: amd-agi-primus
  path: tests/unit_tests/backends/megatron/test_recompute_layer_patches.py
  commit: bab82720d72cadbdfbedcc050c9fb49de3b353be
  sha256: 1896030ea03bfcca9811065e63738f4fe828638192dca7a2ae912e2b222e1ebb
- source: amd-agi-primus
  path: docs/04-technical-guides/performance-tuning.md
  commit: bab82720d72cadbdfbedcc050c9fb49de3b353be
  sha256: d205b3f40100e272b5f05730ba6532909a09ff62b3c1b917bdb9593f1a80939c
- source: amd-agi-primus
  path: docs/04-technical-guides/checkpoint-management.md
  commit: bab82720d72cadbdfbedcc050c9fb49de3b353be
  sha256: 3038ed40f460556987c6ccf00d8f65deeab82dfccf794ccaedf4352f6ac92c70
- source: amd-agi-primus
  path: primus/backends/megatron/patches/args/rocm_arg_validation.py
  commit: bab82720d72cadbdfbedcc050c9fb49de3b353be
  sha256: e315df8c624f52567641d42ef2a100cfe687ae6ffd5f469a05e5bc1fe0d8ea28
- source: amd-agi-primus
  path: primus/backends/megatron/patches/_source_patch_utils.py
  commit: bab82720d72cadbdfbedcc050c9fb49de3b353be
  sha256: b8d4d892ee84b7c24577cc47ddfba6cbea0f571eeafd9d2916b41affa1b548cb
retrieved_on: '2026-11-04'
---

# Primus：按全局层选择重算、MTP 与低精度状态

## 适用问题：内存余量与重复计算的权衡

全层/全段重算会释放激活但增加 backward 重新 forward 的工作。一些模型只在少数层/微批阶段达到 HBM 峰值，按层选择可以减少为容量支付的计算。决定前先看 worst-rank peak allocated/reserved、活动微批数和激活生命周期；不要只看平均显存，也不要无依据把所有层默认设为重算。

## 入口、约束及代码路径

`recompute_layer_patches.py` 用全局 layer ID 集合选择重算，现按实际 Core 分成两条安装路径：仍有 `TransformerBlock._checkpointed_forward` 时包装旧方法；Core 将该逻辑移出类后，`_install_main_recompute_layer_ids()` 对 `megatron.core.recompute.checkpointed_forward` 做源码替换，并同步重绑 `transformer_block` 中已导入的函数别名。父仓当前 Core gitlink 为 `4b4acac9a1d28ea6829c8d4f566d75698a21249d`，迁移时须同时确认两个引用。未指定层时保留原方法或函数的原控制流；指定时使用 `chunk_runner(layer_idx, layer_idx + 1, use_checkpoint)`，层 ID 加 pipeline offset。`validate_specified_recompute_layers` 仍检查 ID 范围、full granularity、method 和相关并行限制，不能随意和另一种重算 method 拼接。

patch 暂时改变 `TransformerConfig.__post_init__` 检查上下文后再恢复并执行自己的验证，说明它不是一个无状态的循环 if。实际移植要对照当前 Core 配置校验、Pipeline layer offset 和返回值，而不是复制旧函数签名。

## MTP、RNG 和 dtype 契约

MTP 有独立 wrapper，索引接在 decoder 层之后；Pipeline/VPP rank 的 local layer ID 不能直接当 global ID。wrapper 现在检查原签名是否含 `forward_func`：旧 Core 接收外部函数，新 Core 使用 `self._proj_and_transformer_layer`；未选中时按原接口委托。旧 decoder wrapper 对 FP8/FP4 选 TE checkpoint/context，仍有 FP4 TODO；新的模块级路径另在 FP8/FP4 且 hidden states 不需梯度时关闭该层 checkpoint。MTP 只在 FP8 时选 TE，其余走 tensor-parallel checkpoint，不能由 decoder 推导其 FP4 覆盖。保持 RNG、实际 recipe 的 scale/cache、attention mask/packed sequence 和 autograd 依赖，才能保证重算是在同一函数上重复求值。

## 实验与收益范围

先使用未选择层的回退路径验证与原实现相符；再按少数层、跨 PP/VPP、decoder+MTP 扩展。对应单测检查上游函数签名/源码指纹与 selected layer 行为；新增模块级 anchor 唯一性、两个模块引用重绑及幂等安装检查，旧方法消失时旧签名测试会 skip。`patch_function_source` 本身只 assert anchor 存在并做字符串替换，不提供测试中的唯一性保证，Python 优化模式还会移除 assert；不能把这些检查视为运行时硬保证。它们是依赖变化的警报，不是所有训练组合已验证。统计每个候选的峰值显存、重算 GPU 工作、稳态步时、有效 token/s 与 HBM 余量，决定节省是否允许更好的 MB/并行切分。

代价是额外计算、checkpoint launch 和可能减少 overlap 的可重叠窗口。内存已够、关键路径纯计算时更少重算可能更快；OOM 风险高时不能只按速度选择。层数/输入长短变化后旧选择不一定仍覆盖峰值。

先区分激活峰值与 allocator 碎片：当前 Turbo grouped GEMM 的大块主梯度/状态分配可能增加 reserved，新增 allocator 告警/预检并不等于必须多重算。核对 allocated/reserved、真实生效设置与 [总览中的预检边界](../overview/engineering-guide.md#8-数值诊断与恢复)，再决定重算、布局或 allocator 候选；不将几种机制的显存节省简单相加。

## 诊断、回退与维护

错误集中在后半段层时核对 global offset，MTP loss 异常核对额外层和低精度 context，resume 后偏差核对 RNG 与数据位置。完全撤销选择或恢复上游重算路径是明确回退；不要留下 wrapper 但恢复一半配置。上游类方法、模块级 `checkpointed_forward` 或 MTP 签名更新时，同时检查不选层分支、测试指纹、[案例](../cases/primus-layer-recompute.md)和[总览](../overview/engineering-guide.md)。

2026-11-04 检索固定提交 `bab82720d72cadbdfbedcc050c9fb49de3b353be`：重算实现与相邻单测已变化，故修订分派和测试边界；性能调优、checkpoint 文档及 ROCm 参数校验所引原件未变，保留峰值、数值、恢复与回退的验证要求。没有执行上游单测。

## 固定证据与复核范围

- [primus/backends/megatron/patches/recompute_layer_patches.py](https://github.com/AMD-AGI/Primus/blob/bab82720d72cadbdfbedcc050c9fb49de3b353be/primus/backends/megatron/patches/recompute_layer_patches.py)
- [tests/unit_tests/backends/megatron/test_recompute_layer_patches.py](https://github.com/AMD-AGI/Primus/blob/bab82720d72cadbdfbedcc050c9fb49de3b353be/tests/unit_tests/backends/megatron/test_recompute_layer_patches.py)
- [docs/04-technical-guides/performance-tuning.md](https://github.com/AMD-AGI/Primus/blob/bab82720d72cadbdfbedcc050c9fb49de3b353be/docs/04-technical-guides/performance-tuning.md)
- [docs/04-technical-guides/checkpoint-management.md](https://github.com/AMD-AGI/Primus/blob/bab82720d72cadbdfbedcc050c9fb49de3b353be/docs/04-technical-guides/checkpoint-management.md)

- [primus/backends/megatron/patches/args/rocm_arg_validation.py](https://github.com/AMD-AGI/Primus/blob/bab82720d72cadbdfbedcc050c9fb49de3b353be/primus/backends/megatron/patches/args/rocm_arg_validation.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
