---
id: official-megatron-wiki/bridge
title: Megatron Bridge：模型入口、配置传播与训练生命周期
engine: bridge
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
coverage: selected implementation chain, not all models or backends
sources:
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/config.py
  commit: 34ddd53b0e023d93f107f29b7dc61f9c5dd76a57
  sha256: cedbd47d180cc282c808b69c311b4fc36860104446e887b20b84dab54321bced
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/train.py
  commit: 34ddd53b0e023d93f107f29b7dc61f9c5dd76a57
  sha256: d2d85394c84a2f374de8d0b623c30c8f554bbb728d95de77687e54a26e6593f4
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/pretrain.py
  commit: 34ddd53b0e023d93f107f29b7dc61f9c5dd76a57
  sha256: 28a0fec822239d825da13838dcb6d86ee4b6ac13a52865bb351dc668e59225bf
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/gpt_provider.py
  commit: 34ddd53b0e023d93f107f29b7dc61f9c5dd76a57
  sha256: 18b4bf503a17481c678c4be32159320dc4e3466e844e55f946c0e11b91671148
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/conversion/auto_bridge.py
  commit: 34ddd53b0e023d93f107f29b7dc61f9c5dd76a57
  sha256: 434ffc88e7f68d5f63ec63e827113c114239a1102e6d7536aab1642412126d96
---

# Megatron Bridge：模型入口、配置传播与训练生命周期

## 生态位置与目录

Bridge 连接模型配方、HF 权重/配置与 Megatron Core 训练。`models/gpt_provider.py` 决定如何提供模型和 layer spec，`models/conversion/auto_bridge.py` 处理转换，`training/config.py` 汇总训练/并行/optimizer/保存/日志等配置，`training/pretrain.py` 初始化生命周期，`training/train.py` 执行 step 和持续训练。`recipes`、examples 与 docs 是使用入口；底层 schedule 和 TE kernel 仍需追到依赖版本。

## 调用和状态管理

`pretrain(config, forward_step_func, callbacks)` 先做 runtime_config_update，创建 GlobalState，再归一化 callback。正常路径进入 `_pretrain`；inprocess restart 路径包裹执行并接管 process group 生命周期。源码在用户已经初始化 process group 时拒绝该 restart 模式。这是具体约束：不能同时让外部容错、自建通信初始化和 Bridge 内部重启各自拥有恢复责任。

`ConfigContainer.validate` 与各配置 finalize 影响最终运行值，日志应保留解析及自动修正后的配置。ProfilingConfig、CheckpointConfig、StragglerDetection 和 FaultToleranceConfig 是不同职责，不应把存在配置字段视为现场功能已经部署。

## 模型和权重转换

AutoBridge 提供从 HF config/pretrained 建立映射、导入/导出权重及 checkpoint 的入口。`to_megatron_provider` 与 `get_model` 连接 provider；`stream_weights_hf_to_megatron`、iter_local_hf_params 和量化导出任务是继续追查逐层内存与布局的切入点。逐项记录名称、QKV 排列、分片轴、embedding tying、RoPE、special tokens 与 dtype/scale。

成功转换只说明完成所执行的转换步骤。回归应比较固定输入 logits、loss、梯度及一个 optimizer step；量化转换额外检查 recipe 和权重缓存。PR #6140 提醒 decoder replacement 后还需 finalize TE precision；PR #6343 则涉及 checkpoint embedding keys 的保留，二者都不能只看 tensor 数量是否相同。

## 安装、运行、测试

以目标提交 pyproject、官方 docs/training、配方与 examples 为准锁定 Core/TE；HCU 使用对应 patch 工程的安装和启动链。先构建配置并验证 provider，再在最小可行并行组执行短训练。检查 save→load 后的模型、optimizer、scheduler、RNG 和数据位置；多机恢复需要真实进程组和存储条件。

调用方可注入 forward_step_func，因此数据格式、loss mask 与返回契约不是 Bridge 自动替任务保证的。SFT/多模态模型尤其要核对转换前后的模板、packing 和 loss 分母。运行脚本记录来源、平台改动及最终环境，不能直接套用 NV 启动变量。

## 性能和显存

在 train_step 中对齐 Core schedule、optimizer、sync 与 callback/日志开销。通信 overlap 需要配置传递、下游支持与 trace 三者一致；checkpoint 转换/导出中的完整权重物化需要峰值显存/主存证据。HF 导出用于 rollout 时，继续联查 vLLM/VERL 的逐层传输，避免每次导出整模型驻留。

编译、graph capture、热身、稳定训练和保存分开计时。开关被自动关闭或走 fallback 必须记录；提高吞吐的组合仍须按阶段验 loss。排障从 ConfigContainer→provider→Core→TE/底层实现一路追踪，保留每层具体 SHA 和接口条件。

## 固定源码与符号导航

| 文件 | 本轮源码中可追查的入口（非全部符号） |
| --- | --- |
| [src/megatron/bridge/training/config.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/34ddd53b0e023d93f107f29b7dc61f9c5dd76a57/src/megatron/bridge/training/config.py) | `DistributedDataParallelConfig`, `OptimizerConfig`, `DistributedInitConfig`, `RerunStateMachineConfig`, `OptimizerConfigOverrideProviderContext`, `OptimizerConfigOverrideProvider`, `GPTDatasetConfig`, `GPTFIMDatasetConfig` |
| [src/megatron/bridge/training/train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/34ddd53b0e023d93f107f29b7dc61f9c5dd76a57/src/megatron/bridge/training/train.py) | `train`, `train_step`, `maybe_synchronize_training_step`, `maybe_report_stragglers`, `maybe_check_weight_hash_across_dp_replicas`, `maybe_run_manual_gc`, `should_disable_forward_pre_hook`, `enable_forward_pre_hook` |
| [src/megatron/bridge/training/pretrain.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/34ddd53b0e023d93f107f29b7dc61f9c5dd76a57/src/megatron/bridge/training/pretrain.py) | `pretrain` |
| [src/megatron/bridge/models/gpt_provider.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/34ddd53b0e023d93f107f29b7dc61f9c5dd76a57/src/megatron/bridge/models/gpt_provider.py) | `transformer_engine_layer_spec`, `transformer_engine_full_layer_spec`, `local_layer_spec`, `modelopt_transformer_layer_spec`, `default_layer_spec`, `GPTModelProvider`, `mtp_block_spec`, `provide` |
| [src/megatron/bridge/models/conversion/auto_bridge.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/34ddd53b0e023d93f107f29b7dc61f9c5dd76a57/src/megatron/bridge/models/conversion/auto_bridge.py) | `AutoBridge`, `list_supported_models`, `supports`, `from_auto_config`, `from_hf_config`, `from_hf_pretrained`, `can_handle`, `load_hf_weights` |

## 教程、PR 与继续搜索

- [全仓目录和固定文件入口](../source-maps/nvidia-nemo-megatron-bridge.md)：没有本地专题时按模块继续读源码。
- [上游教程原文目录](../upstream-docs/nvidia-nemo-megatron-bridge/)：保留来源内容，链接相对位置以原站为准。
- [PR #6140：Fix(qwen3vl): finalize TE precision after decoder replacement](../prs/NVIDIA-NeMo--Megatron-Bridge/PR-6140.md)：正文、review、diff 与 head/base 源码。
- [PR #6343：fix(ckpt): preserve NemotronH checkpoint embedding keys](../prs/NVIDIA-NeMo--Megatron-Bridge/PR-6343.md)：正文、review、diff 与 head/base 源码。

检索示例：`wiki-search "关键符号或问题" --engine bridge`。本地结果不足，使用 `wiki-search-pr "简短英文问题词" --engine bridge`，再 `wiki-pr OWNER/REPO NUMBER`、`wiki-code OWNER/REPO FULL_SHA PATH` 追实际调用者、被调底层库和测试。普通查阅只写私有缓存。

## 更新和验收边界

运行 `wiki-update PROJECT nvidia-nemo-megatron-bridge` 检查完整目录、新文档、PR 讨论与已监测源码；分页或网络失败必须续采。变更后联动本页、同仓专题/案例、调用方与依赖；源码已 merge、软件已发布、HCU 已适配和当前任务已验证分别登记。本页为选定实现的代码阅读和操作建议，没有在 HCU 执行上述测试，也未覆盖所有模型。实际任务的版本、性能、显存、失败尝试和阶段 loss 记录进入私有经验 Wiki。
