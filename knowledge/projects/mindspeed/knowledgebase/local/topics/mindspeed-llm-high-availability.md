---
id: ecosystem/topics/mindspeed-llm-high-availability
title: MindSpeed-LLM：Replica Optimizer、高可用与弹性恢复
engine: mindspeed
kind: authored
stages:
- fault-tolerance
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-20'
coverage: selected source, official documentation and related PR reading; no HCU runtime validation
sources:
- source: ascend-mindspeed-llm
  path: docs/en/pytorch/features/mcore/high_availability.md
  commit: 5a8ea03b12066067f39b1771782d12db236267ef
  sha256: a8d47b4b928372aedc48a08798f11ccad2d6273c51166b578e93ae1f517d7fc6
- source: ascend-mindspeed-llm
  path: mindspeed_llm/core/high_availability/tft_replica_optimizer.py
  commit: 5a8ea03b12066067f39b1771782d12db236267ef
  sha256: a323eab370c55231c87a2b2be00808efb70a8a3cf4f2dcb9230fe922400671e6
- source: ascend-mindspeed-llm
  path: pretrain_gpt.py
  commit: 5a8ea03b12066067f39b1771782d12db236267ef
  sha256: 57022768d4b4b396cda2de61a1638733fe37767736a7dce0592a560bbac2c9fb
- source: ascend-mindspeed-llm
  path: mindspeed_llm/training/training.py
  commit: 5a8ea03b12066067f39b1771782d12db236267ef
  sha256: 4b0d387be430c0e4521db48950cd8554647ed2b52eafd71fc79a70cc4ea09599
---

# MindSpeed-LLM：Replica Optimizer、高可用与弹性恢复

## 职责与外部依赖

高可用旨在设备/进程故障后恢复 optimizer/训练状态，减少整作业从远端 checkpoint 重新拉起的代价。MindSpeed-LLM集成的 MindIO TTP wheel、MindCluster 等是实际部署依赖；`--enable-high-availability` 不是自动搭建集群容错。Ascend设备故障修复接口不能直接移到HCU。

## Replica optimizer与内存成本

`tft_replica_optimizer.py` 在DP域维护分布式优化器状态的冗余，将状态放入互为备份的DP组织，使单份状态丢失后可恢复。冗余占内存和通信，不能当成“免费容错”。文档列出的参数字节模型示例：半精度参数/梯度时 distributed 为 `4+16/DP`，replica为 `4+32/DP`；FP32梯度组合对应 `6+12/DP` 与 `6+24/DP`。这是特定状态模型，不是完整模型峰值HBM估计，激活/临时buffer仍另算。

## 入口、约束与状态所有权

训练参数控制enable-high-availability、hbmfault repair、worker reboot、distributedopt-no-replica、elastic training等；官方文档注明 HIGH_AVAILABILITY 环境值会覆盖CLI，实际配置须同时核对。恢复协调、替换worker和DP拓扑由部署集成接管；训练loop负责对应safe-point/state，不能在任意autograd时刻恢复optimizer。

当前文档的弹性限制包括支持的DP/TP/PP组合、DP及DP_CP>1、与customFSDP/reusefp32param互斥；部分缩扩流程不能重复任意缩放，只允许回到原始规模。这些是此实现限制，不能概括为任意Megatron/FSDP或HCU支持。数据位置、global batch、scheduler和RNG如何保持同一训练目标，需和具体配置共同确认。

## 验证与故障定位

先做常规save→load验证，再在受控故障中观察发现→停止旧rank→状态恢复→重建通信组→持续step/loss。记录失败rank、最后共同step、恢复checkpoint/replica身份、丢失工作量和恢复时间；仅看到重启日志不表示状态完整或没有旧进程残留。

检查恢复后参数/optimizer step、scheduler、RNG、样本/有效token与数值趋势，带精度/GradScaler状态。卡住先区分某rank仍旧group、外部TTP未连接、复制状态未到safe-point或数据/存储阻塞；不要叠加另一个恢复owner反复重启。

## HCU借鉴与回退

HCU任务以既有Cluster Manager等单一恢复系统为主，可以参考冗余状态、safe-point和弹性验收方法；不能把NPU flag或MindIO修复命令当HCU支持证明。未部署相关依赖时恢复到已验证的checkpoint+调度器/站点容错，预留最坏rank内存与节点池。更新时联动[总览](../overview/engineering-guide.md)、版本配对、optimizer和对应部署文档，不只改一个启动flag。

## 固定证据与复核范围

- [docs/en/pytorch/features/mcore/high_availability.md](https://github.com/Ascend/MindSpeed-LLM/blob/5a8ea03b12066067f39b1771782d12db236267ef/docs/en/pytorch/features/mcore/high_availability.md)
- [mindspeed_llm/core/high_availability/tft_replica_optimizer.py](https://github.com/Ascend/MindSpeed-LLM/blob/5a8ea03b12066067f39b1771782d12db236267ef/mindspeed_llm/core/high_availability/tft_replica_optimizer.py)
- [pretrain_gpt.py](https://github.com/Ascend/MindSpeed-LLM/blob/5a8ea03b12066067f39b1771782d12db236267ef/pretrain_gpt.py)
- [mindspeed_llm/training/training.py](https://github.com/Ascend/MindSpeed-LLM/blob/5a8ea03b12066067f39b1771782d12db236267ef/mindspeed_llm/training/training.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
