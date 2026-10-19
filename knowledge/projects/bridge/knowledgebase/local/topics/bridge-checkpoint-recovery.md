---
id: official-megatron-wiki/topics/bridge-checkpoint-recovery
title: Bridge：完整恢复、数据位置与容错所有权
engine: bridge
kind: authored
stages:
- fault-tolerance
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-20'
coverage: selected source delta and related discussion review; unchanged evidence reused; no HCU runtime validation
sources:
- source: nvidia-nemo-megatron-bridge
  path: docs/training/checkpointing.md
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: effe7f073c2edd1ee8340ecc3f16ceba506be520f5f939ffb1c5368dc7eb35b4
- source: nvidia-nemo-megatron-bridge
  path: docs/training/resiliency.md
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: d51d5f1746adef56ac62c96af1df08578f271da91d1fb8f7ae909ef6022d031c
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/pretrain.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 28a0fec822239d825da13838dcb6d86ee4b6ac13a52865bb351dc668e59225bf
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/inprocess_restart.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: fd00ef881babc660f4e3a026bb054632ba7b6fd9d263306f7bfc7bd43aa0451d
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/fault_tolerance.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 93fee2e7048fa582446e64f232c50a7adadc077e2cb67e7a5c463c3dd056c62f
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/conversion/auto_bridge.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: cabf1fbd8954002d4dd852e80590ff3a9bb0efe2b0615f603b498d0b049abe94
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/models/hf_pretrained/state.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 0729aa811936cc1f6caa02cbe54f3d9d74cd6173464bb03555a6341d54a0c849
- source: nvidia-nemo-megatron-bridge
  path: tests/unit_tests/models/test_hf_pretrained_state.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 4ca046d0358201e7fdc33bba25477057c4f81f958c724c890d2476e45ced70ff
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/data/datasets/preference.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 2a65fca150e1e446860ef74cf5dee0d95c8be31f3727b0ae15f4b3a04c6621d0
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/dpo_train.py
  commit: 2b1c8ccd7285cfd09b82afd523859dbe04d754e4
  sha256: 45c7e92be9a7c390efbcbaf800569987dc2e66a7877283e0de1250901ddecfb4
---

# Bridge：完整恢复、数据位置与容错所有权

## 初始化和完整resume是不同入口

`checkpoint.pretrained_checkpoint`用于初始化全模型权重，可指HF或相应nativecheckpoint；它不恢复optimizer/RNG/scheduler/dataloader。`checkpoint.load`用于native完整resume，应指base directory，由tracker/ckpt_step选iteration；HF目录不是完整训练状态。PEFT的frozen base初始化与adapter resume分开，ckpt_step不自动选择pretrained目录下的某次保存。

常见recipe将save/load都指默认路径，旧checkpoint可能让新训练意外resume。新实验应load=None、独立save目录，实际恢复先记录恢复源/step和状态清单。

HF 权重导出又是另一条契约。当前 `save_hf_weights` 先枚举输出目录旧的标准 safetensors/index 及索引引用 shard，写入新产物并获得实际 saved filenames 后，由 rank0 清理未被重写的旧权重文件；否则从分片改成单文件时，遗留 index 可能使加载器仍读旧权重。`StateSource.save_generator` 的索引以本次实际写出的文件/key 构建，并在报告 saver 错误前排空分布式 tensor generator。相关讨论见 [#6408](../../upstream/prs/NVIDIA-NeMo--Megatron-Bridge/PR-6408.md)；以本页固定源码为准，不把讨论中的状态直接当采用情况。

该讨论提供 H200 上一层 BF16 Qwen2 的 load→export→reload，以及只撤销清理的对照：它针对复用目录时从多分片变为单文件的静默旧权重问题，不证明生产频率、多 rank 转换、完整训练恢复或 HCU 数值已通过。

这不是任意目录的清理许可，也不是原子替换/完整训练 resume 保证。只处理实现识别的权重集合、保留无关文件与链接目标；应覆盖分片↔单文件、partial strictness、已有 index、写入失败和重新加载实际参数。不能仅看本次文件生成成功便断言读取的就是新权重。

## 模型reshard不保证数据可任意扩DP

模型和optimizer checkpoint可按所支持format/配置reshard，但Bridge的Energon状态**按DP rank保存**，当前恢复要求相同DP size；model-parallel ranks可共享每DP文件，却在每个rank上restore，因某些模型各rank独立读相同数据。只在writer rank恢复会让其余独立iterator落在不同位置。

数据位置是periodic完整worker状态+消费offset，需要decode→TaskEncoder→packing确定性重放。不能只保存globalstep或认定Energon独立reproducible-scaling条件等于Bridge已实现跨DPstate迁移；详见[Energon专题](../../../../energon/knowledgebase/local/topics/energon-recovery-throughput.md)。缺整个旧generation与缺当前rank文件的处理不同，日志/失败必须说明，不能静默拿新数据称精确resume。

DPO loader 的 consumed_samples、GBS/MBS 用行数表示，在 loader 内除二换成 pair 数；恢复时必须为偶数并满足 DP×microbatch 整除。reference-logprob 产物是额外的输入身份，需保存其内容/评分配置和原样本 pair_id 映射。重新评分或改 tokenizer/template/截断后不能将旧 margin/loss 曲线当作相同目标的恢复；详见 [DPO 数据契约](bridge-provider-conversion.md#dpo配对reference-产物与实际分母)。

## 保存优化、格式和限制

async_save要求torch_dist等受支持format，Megatron FSDP使用自己的fsdp_dtensor格式，不等同TorchFSDP2。fully_parallel save/load、optimizer reshardable、nonpersistent/local保存是不同选项。async减少暴露写盘但需要真实completion/持久化、host容量与带宽，checkpoint key strictness也可能宽松；成功返回不等于完全相同参数集合。

## 容错接入与恢复owner

NVRX fault tolerance要求其ft_launcher/Slurm及依赖，普通torchrun不自动获得功能。inprocess restart为受限/实验路径，`pretrain`会拒绝用户预先初始化processgroup的组合；straggler检测、local checkpoint、进程重启分属不同职责。官方NCCL/CUDA版本和设备要求不能当作HCU已验证。

实际HCU任务由部署已有Cluster Manager等唯一owner重启/隔离，Agent负责证据与建议。先确认engine是否允许外部relaunch和安全checkpoint，再避免两个owner分别替换进程/机器池。

## 验收、排障与回退

连续运行与save→kill→load比较模型、optimizer、scheduler、RNG、data IDs/effective tokens、loss及多个step，覆盖缓慢/失败存储和异步保存完成前后。恢复后继续监测step/loss/内存，清点旧rank、writer与端口，不能看到“load complete”便退出。

参数不匹配从strictness/key/layout/真实模型结构查起，数据漂移从rank所有权/seed/stateless重放，卡住区分通信初始化、某rank提前错误与storagebarrier。回退可信同步globalcheckpoint或已验证resume组合，代价明确。更新格式/版本/数据provider和恢复接口时联动[总览](../overview/bridge.md)、[Energon](../../../../energon/knowledgebase/local/overview/energon.md)及实际HCUparentgitlink。

## 固定证据与复核范围

- [docs/training/checkpointing.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/docs/training/checkpointing.md)
- [docs/training/resiliency.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/docs/training/resiliency.md)
- [src/megatron/bridge/training/pretrain.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/training/pretrain.py)
- [src/megatron/bridge/training/inprocess_restart.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/training/inprocess_restart.py)
- [src/megatron/bridge/training/fault_tolerance.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/training/fault_tolerance.py)

- [src/megatron/bridge/models/conversion/auto_bridge.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/models/conversion/auto_bridge.py)
- [src/megatron/bridge/models/hf_pretrained/state.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/models/hf_pretrained/state.py)
- [tests/unit_tests/models/test_hf_pretrained_state.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/tests/unit_tests/models/test_hf_pretrained_state.py)
- [src/megatron/bridge/data/datasets/preference.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/data/datasets/preference.py)
- [src/megatron/bridge/training/dpo_train.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/2b1c8ccd7285cfd09b82afd523859dbe04d754e4/src/megatron/bridge/training/dpo_train.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
