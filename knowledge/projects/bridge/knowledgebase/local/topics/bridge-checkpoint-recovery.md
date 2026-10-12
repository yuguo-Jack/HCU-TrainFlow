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
reviewed_on: '2026-10-12'
coverage: selected source, official documentation and related PR reading; no HCU runtime
  validation
sources:
- source: nvidia-nemo-megatron-bridge
  path: docs/training/checkpointing.md
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: effe7f073c2edd1ee8340ecc3f16ceba506be520f5f939ffb1c5368dc7eb35b4
- source: nvidia-nemo-megatron-bridge
  path: docs/training/resiliency.md
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: d51d5f1746adef56ac62c96af1df08578f271da91d1fb8f7ae909ef6022d031c
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/pretrain.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 28a0fec822239d825da13838dcb6d86ee4b6ac13a52865bb351dc668e59225bf
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/inprocess_restart.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: fd00ef881babc660f4e3a026bb054632ba7b6fd9d263306f7bfc7bd43aa0451d
- source: nvidia-nemo-megatron-bridge
  path: src/megatron/bridge/training/fault_tolerance.py
  commit: 53681c1aa264b54a1afa320830738382ee2a44f4
  sha256: 93fee2e7048fa582446e64f232c50a7adadc077e2cb67e7a5c463c3dd056c62f
---

# Bridge：完整恢复、数据位置与容错所有权

## 初始化和完整resume是不同入口

`checkpoint.pretrained_checkpoint`用于初始化全模型权重，可指HF或相应nativecheckpoint；它不恢复optimizer/RNG/scheduler/dataloader。`checkpoint.load`用于native完整resume，应指base directory，由tracker/ckpt_step选iteration；HF目录不是完整训练状态。PEFT的frozen base初始化与adapter resume分开，ckpt_step不自动选择pretrained目录下的某次保存。

常见recipe将save/load都指默认路径，旧checkpoint可能让新训练意外resume。新实验应load=None、独立save目录，实际恢复先记录恢复源/step和状态清单。

## 模型reshard不保证数据可任意扩DP

模型和optimizer checkpoint可按所支持format/配置reshard，但Bridge的Energon状态**按DP rank保存**，当前恢复要求相同DP size；model-parallel ranks可共享每DP文件，却在每个rank上restore，因某些模型各rank独立读相同数据。只在writer rank恢复会让其余独立iterator落在不同位置。

数据位置是periodic完整worker状态+消费offset，需要decode→TaskEncoder→packing确定性重放。不能只保存globalstep或认定Energon独立reproducible-scaling条件等于Bridge已实现跨DPstate迁移；详见[Energon专题](../../../../energon/knowledgebase/local/topics/energon-recovery-throughput.md)。缺整个旧generation与缺当前rank文件的处理不同，日志/失败必须说明，不能静默拿新数据称精确resume。

## 保存优化、格式和限制

async_save要求torch_dist等受支持format，Megatron FSDP使用自己的fsdp_dtensor格式，不等同TorchFSDP2。fully_parallel save/load、optimizer reshardable、nonpersistent/local保存是不同选项。async减少暴露写盘但需要真实completion/持久化、host容量与带宽，checkpoint key strictness也可能宽松；成功返回不等于完全相同参数集合。

## 容错接入与恢复owner

NVRX fault tolerance要求其ft_launcher/Slurm及依赖，普通torchrun不自动获得功能。inprocess restart为受限/实验路径，`pretrain`会拒绝用户预先初始化processgroup的组合；straggler检测、local checkpoint、进程重启分属不同职责。官方NCCL/CUDA版本和设备要求不能当作HCU已验证。

实际HCU任务由部署已有Cluster Manager等唯一owner重启/隔离，Agent负责证据与建议。先确认engine是否允许外部relaunch和安全checkpoint，再避免两个owner分别替换进程/机器池。

## 验收、排障与回退

连续运行与save→kill→load比较模型、optimizer、scheduler、RNG、data IDs/effective tokens、loss及多个step，覆盖缓慢/失败存储和异步保存完成前后。恢复后继续监测step/loss/内存，清点旧rank、writer与端口，不能看到“load complete”便退出。

参数不匹配从strictness/key/layout/真实模型结构查起，数据漂移从rank所有权/seed/stateless重放，卡住区分通信初始化、某rank提前错误与storagebarrier。回退可信同步globalcheckpoint或已验证resume组合，代价明确。更新格式/版本/数据provider和恢复接口时联动[总览](../overview/bridge.md)、[Energon](../../../../energon/knowledgebase/local/overview/energon.md)及实际HCUparentgitlink。

## 固定证据与复核范围

- [docs/training/checkpointing.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/docs/training/checkpointing.md)
- [docs/training/resiliency.md](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/docs/training/resiliency.md)
- [src/megatron/bridge/training/pretrain.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/src/megatron/bridge/training/pretrain.py)
- [src/megatron/bridge/training/inprocess_restart.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/src/megatron/bridge/training/inprocess_restart.py)
- [src/megatron/bridge/training/fault_tolerance.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/src/megatron/bridge/training/fault_tolerance.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
