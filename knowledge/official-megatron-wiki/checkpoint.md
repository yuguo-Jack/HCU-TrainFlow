---
id: official-megatron-wiki/checkpoint
title: Megatron checkpoint：分片、异步完成、数值状态与恢复
engine: megatron
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: reviewed training, parallel, state and backend implementation chains; not
  all models or runtime combinations
sources:
- source: nvidia-megatron-lm
  path: megatron/core/dist_checkpointing/serialization.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 2f3c6b9f11c3919ce6579ef75dd877e351f09c1fc54b8c025f7c95fc4f2fcf57
- source: nvidia-megatron-lm
  path: megatron/training/checkpointing.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: e388d78cd420ee56cafac87bcb33433d3ec247ae5db94f51c53c6ccb5c787c79
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: e436206da1fe3ec5b8b5da8a06e1c8d6a7e08f149a0079107d83f1d68284e469
- source: nvidia-megatron-lm
  path: megatron/core/rerun_state_machine.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 628f9550686505275eddfda7f444ebee51c573f0790d6927027444660f51a5ea
- source: nvidia-megatron-lm
  path: tests/unit_tests/test_checkpointing.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: c7138e82641e94df41ee1ac16f9f4f94553d5ce705716dd2cefb065359989776
- source: nvidia-megatron-lm
  path: tests/unit_tests/dist_checkpointing/test_rerun_state_machine_ckpt.py
  commit: e30d863a6d82a3c45f2d71355dc73fbf5610967b
  sha256: 21689986768bf00506f7437d136bc1072da8bd4dca487d655e77d41af734af05
---

# Megatron checkpoint：分片、异步完成、数值状态与恢复

## 两层职责与数据链

training/checkpointing构造model/optimizer/scheduler、RNG、iteration/consumed samples与可保存loader状态，选择格式/backend；Core serialization处理common/sharded metadata、完整性校验和实际storage策略。resume先定位实际checkpoint格式与版本，不因目录或tracker存在就认定完成。

保存路径：训练状态快照→sharded_state_dict/metadata→storage写入→async finalize（若有）→完成回调/tracker→供恢复选择。加载反向读取格式/配置→分片元数据/strict校验→模型与optimizer布局→RNG/data游标→train循环继续。

## AsyncRequest 不是保存已经完成

Core `save(async_sharded_save=True)`返回待外部调度的AsyncRequest；metadata/integrity finalizers挂在完成链上。拿到request、目录出现或worker已启动都不是最终成功。training维护async队列与save/finalize callbacks，旧请求未完成时新保存/退出的行为需按部署版本核对。

失败诊断保存各rank异常、实际shard列表、metadata/content-version、后台进程与最后完成回调。实际storage可为shared FS/其他后端，权限、容量/带宽、host buffers和后台耗时会影响训练峰值；不要只看device memory。

## State 和布局完整性

Core load的strict和validate-access-integrity控制missing/unexpected keys及shard范围检查；不能为了让恢复成功关掉strict而不解释遗漏。模型当前sharded布局、optimizer参数排序/主状态、tied权重、expert partitions与数据字段必须与checkpoint可转换。

保存并行域TP/PP/EP/DP/CP与模型config/optimizer格式；改变并行布局需受支持的reshard/Bridge转换和小跑验证，不是仅改worldsize。单独加载model做推理可有不同状态需求，完整继续训练必须恢复optimizer/LR和RNG/数据位置。

当前RNG包含Python、NumPy、Torch/device与tensor-parallel tracker，按相应DP/CP等group与key namespace组织。consumed样本/数据游标、成功optimizer updates与iteration分开；乱用某一rank的RNG或保存半步snapshot会导致看似启动成功但loss偏移。

## 数值重跑与 checkpoint

rerun-state-machine和training的checkpoint/exit决策要与model/data/RNG同一次迭代一致；相关unit tests验证状态checkpoint。rerun不是“把程序再跑一次”，需恢复同batch与numerical上下文；控制端超时后先核对原save/load是否还在运行，避免重复写同目录。

验证流程：可信checkpoint短跑建立参考→保存并确认finalize→独立attempt加载→检查参数/optimizer/RNG/data/version→连续推进固定样本并比较loss/grad/LR→需要时受支持扩DP。单看进程出现或step日志增长不足以验收。

## 长稳训练和容错归属

Cluster Manager/站点指定owner负责隔离/重启策略，TrainFlowwatcher采集退出、无进展、recovertimeout和incident；不能再建另一套争抢恢复。先验证恢复checkpoint与可用节点池，再观察连续多步、有效样本、数值与吞吐是否符合预期。

卡住按loader/data→forward/collective→optimizer→checkpoint/asyncwait定位；损坏shard、重复恢复同step、非一致tracker/metadata或数据游标回退保留原证据，选更早已完成可信checkpoint并说明数据回退/重复风险。已发布公共Wiki只保留可复用机制与最终关键结果，逐次恢复log进任务档案。

## 测试与更新

`tests/unit_tests/test_checkpointing.py`与dist-checkpoint/rerun测试提供格式/状态入口；相关case需要实际多rank、storage和backend时保留现场缺口。源码unit pass不证明完整模型转换、异步故障注入或全规模恢复已完成。

training/Core任一save/load、optimizer state schema或consumer数据loader变化，联动本页、[training/loss](training-and-loss.md)、[memory](memory.md)、[Bridge](bridge.md)/[Energon](energon.md)和长稳Skill。release迁移说明、特性PR和最终code一起读，避免只改overview的SHA。

## 固定源码与维护边界

- [megatron/core/dist_checkpointing/serialization.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/dist_checkpointing/serialization.py)
- [megatron/training/checkpointing.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/training/checkpointing.py)
- [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/training/training.py)
- [megatron/core/rerun_state_machine.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/megatron/core/rerun_state_machine.py)
- [tests/unit_tests/test_checkpointing.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/tests/unit_tests/test_checkpointing.py)
- [tests/unit_tests/dist_checkpointing/test_rerun_state_machine_ckpt.py](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/tests/unit_tests/dist_checkpointing/test_rerun_state_machine_ckpt.py)

2026-10-12按上述固定源码/官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。
