---
id: doc-baidu-baige-loongforge-e5c9678e050e64964f22
title: baidu-baige/LoongForge / docs/source_zh/features/fp8_communication.md
engine: loongforge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: baidu-baige/LoongForge
commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
path: docs/source_zh/features/fp8_communication.md
raw_sha256: 022bd765adf4ab169bdc56d93a67057829eef452a480a2018a6fb15ab92a8a43
sources: []
generated_body_sha256: 6a07c883995f93091db5a712794b55863891a2e16af4a7c2209a1784fe207329
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source_zh/features/fp8_communication.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source_zh/features/fp8_communication.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# FP8 通信

LoongForge 为 embodied 训练栈提供两项可选的 FP8 通信优化。二者都通过用 FP8 E4M3 代替 BF16/FP32 来压缩跨卡通信量，且都**只改变通信精度**——forward / backward 计算不受影响，也都不会把权重、激活或 GEMM 转为 FP8（那是独立的端到端 [FP8 训练](fp8_training.md) 功能）。

按并行策略二选一；它们作用于不同的 collective，不同时使用。

| | [FSDP2 Delta-FP8 Param AllGather](delta_fp8_allgather.md) | [DDP FP8 Grad AllReduce](fp8_grad_comm_hook.md) |
| --- | --- | --- |
| 并行策略 | FSDP2 | DDP |
| 压缩对象 | 参数 AllGather | 梯度 all-reduce |
| 方法 | 相对持久 BF16 参考的按 block FP8 差值 | FP8 AllToAll → 本地 FP32 reduce → FP8 AllGather |
| 启用方式 | `--fsdp-delta-fp8-allgather` | `--ddp-comm-hook fp8_a2a_allgather_hook` |

通信路径支持本身并不保证对每个模型都数值/性能适用。在新配方中采用前，请对同一模型的 BF16/FP32 baseline 校验 loss、单步时间和峰值显存。

```{toctree}
:maxdepth: 1

delta_fp8_allgather.md
fp8_grad_comm_hook.md
```
