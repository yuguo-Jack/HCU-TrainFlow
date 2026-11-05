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
reviewed_on: '2026-11-04'
coverage: frozen source delta and consumer review; unchanged files rechecked; no HCU runtime validation
sources:
- source: nvidia-megatron-lm
  path: megatron/core/dist_checkpointing/serialization.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 5820472782a469830ce6d1f107fb473dd65f7a4c76c56c2c5265eb619e83893f
- source: nvidia-megatron-lm
  path: megatron/training/checkpointing.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 93a3ff24c7024dc17a79ed18e7a9db624171c61910adc438723b93a33eda2726
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 1cfba3a404c97febc4c2e40895467372e6ab540006dc6a6e22fbc547087a5b75
- source: nvidia-megatron-lm
  path: megatron/core/rerun_state_machine.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 0098ceed9a9cedfc0fba53aab75aefad8fe8ea8d10711da70965f55500401c03
- source: nvidia-megatron-lm
  path: tests/unit_tests/test_checkpointing.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 9facaac5bab4b3e4f12a6a7a5dd14570d3dd8bcabdb88439d1b03dd13c5c7691
- source: nvidia-megatron-lm
  path: tests/unit_tests/dist_checkpointing/test_rerun_state_machine_ckpt.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 21689986768bf00506f7437d136bc1072da8bd4dca487d655e77d41af734af05
- source: nvidia-megatron-lm
  path: megatron/training/ckpt/glu_checkpointing.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: ae5abc38caa095a75f26eee25decbe4c645b1536c8fa52fb42d70986bc74bb04
- source: nvidia-megatron-lm
  path: tests/unit_tests/dist_checkpointing/test_stream_ckpt_dequant.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 524d95fa70cf959e07959ede7b67dd4dd4086fa58a296f62caee411b16bffd00
- source: nvidia-megatron-lm
  path: tests/unit_tests/training/test_glu_checkpoint_loading_numerics.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 2f9e5b2e19bce5cfd182372582f8e88f1df3775c02dc4ba6afe24ba2719467dc
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/distrib_optimizer.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 748f6f665109a99ae9b13cd90c6cb179afb855906bdf75f1442064a0c11e20a9
- source: nvidia-megatron-lm
  path: megatron/core/optimizer/optimizer_config.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: f83b46a8a901bb7c792076544e2fefda3b76830ef2d971ecb976f0ac557fbc67
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/megakernel/mok/backend.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 63326a8898483e2b31a00b190004d7b8a470da350e4658e71282fadea3c541fd
- source: nvidia-megatron-lm
  path: megatron/core/transformer/moe/router.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 19222feee0fca608353117cca63ba9b51160d720bb3f58ede7f2a25843ce3f4f
- source: nvidia-megatron-lm
  path: megatron/core/distributed/finalize_model_grads.py
  commit: 21334a44ede0b8497d1770d0b80bc115e777bd00
  sha256: 6dac52af3f531447c4dfd96bca03b0607cb0fe509c5108890e90812c3bdf190a
retrieved_on: '2026-11-04'
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

## 当前映射与加载路径的限制

混合 FP32 与 FP16/BF16 参数组的 optimizer 索引现按实际 main-parameter 顺序排列，而非按梯度 buffer 的遇到顺序。DP-reshardable 保存保留 bucket 内 padding、排除仅供 DP 均分的尾 padding。旧 #7336 修复之前生成的错误映射 checkpoint 不会被新 loader 自动修好，需独立检查 moment/master 的参数归属与下一次更新，shape 相同仍可能错配。

`stream_ckpt_dequant` 是推理权重加载路径：逐目标张量使用高精度 scratch 后原地量化，避免同时保留全部高精度副本；不接受带 optimizer 的续训，也拒绝依赖尚未恢复 scale/history 的 DelayedScaling。它不是通用训练恢复省内存开关。对应测试比较量化 codes，并明确 scale padding 的不可复现部分，不能改写为任意量化元数据逐位相同。

GLU FC1 模型权重按连续 gate/up 行保存，optimizer 仍保持运行布局。仅加载模型时可转换部分布局；恢复 optimizer 时先校验 interleave 与 TP 布局，拒绝不兼容组合，不能只转模型再声称完整状态已转换。

保存前对 TrainState 作独立快照；local checkpoint 可内嵌 train_state_metadata，全局/legacy 路径可有 sidecar。加载优先相应 TrainState/latest state，缺失时才走旧字段；核对实际采用的 iteration/consumed samples 来源。`on_saved` 在同步 barrier 后或其异步 checkpoint 请求 finalize 后触发，标记该 backend 完成契约；这不额外证明文件系统 fsync、掉电持久性或独立恢复成功。含 logits flush 时，原有部分成功回调先被转移到 logits 请求，但随后追加的 `on_saved` 仍留在 checkpoint 请求上，不能据它推断 logits 也已完成；消费者须检查自己依赖的完成链。旧保存点清理只允许 `0 < previous < current` 且不在保留间隔，恢复到早步不能因此删除目录中较新的保存点。

当前 checkpoint 元数据从 `cfg.optimizer` 判定 DistOpt/LayerWise；inference container 没有 optimizer section 时只保留共享元数据。batch/RNG 比较优先 saved config 对应 section，缺字段才回退旧 args；scheduler override 从当前 cfg 重新施加 LR bounds。`override_ckpt_iteration` 使用当前 global batch 重算 consumed samples，遇旧 checkpoint batch 不同会告警，不能当原运行同数据位置恢复。

DP-reshardable 的纯尾 padding rank 现在允许无 bucket state，但若空 shard 仍相交有效 payload 会失败；旧 mixed-FP32/main-param 顺序映射和 GLU 模型/optimizer 不同布局的保护仍保留。idle rerun shard 为 strict load 生成请求后不恢复为活跃 rerun；不能因为 strict key 存在就重复执行已完成 batch。

logits-only progress tracker 的 owner 已改为末 PP stage 上 TP0/CP0/DP0，而非 is_last_rank，保证其 finalize 跟随真正写 logits 的请求；普通 checkpoint 的 `on_saved` 与 logits 完成链仍需分别检查。train loop 新增后台 saver 失效检查，但 completion/恢复验证不能仅靠目录或日志。本轮 serialization、rerun 状态实现、GLU 与 stream-dequant 数值测试原件未变，故保留 strict、异步完成、推理-only dequant 和布局限制。

MOK backend 仅在 backend、原生权重布局与模型/并行配置保持相同时提供 regular/distributed save-resume 契约；baseline↔MOK、single↔non-single、GLU interleave 或 legacy 转换明确不在集成范围。其别名参数不另存，加载后清 derived weight/grad-descriptor cache。QB 的 scope/bin 数在重建 router 前恢复：global scope 保存 expert_bias/bin_bounds，histogram 为临时量，不能据模型 tensor shape 相同就换 estimator 续训。

## 数值重跑与 checkpoint

rerun-state-machine和training的checkpoint/exit决策要与model/data/RNG同一次迭代一致；相关unit tests验证状态checkpoint。rerun不是“把程序再跑一次”，需恢复同batch与numerical上下文；控制端超时后先核对原save/load是否还在运行，避免重复写同目录。

验证流程：可信checkpoint短跑建立参考→保存并确认finalize→独立attempt加载→检查参数/optimizer/RNG/data/version→连续推进固定样本并比较loss/grad/LR→需要时受支持扩DP。单看进程出现或step日志增长不足以验收。

## 长稳训练和容错归属

Cluster Manager/站点指定owner负责隔离/重启策略，TrainFlowwatcher采集退出、无进展、recovertimeout和incident；不能再建另一套争抢恢复。先验证恢复checkpoint与可用节点池，再观察连续多步、有效样本、数值与吞吐是否符合预期。

卡住按loader/data→forward/collective→optimizer→checkpoint/asyncwait定位；损坏shard、重复恢复同step、非一致tracker/metadata或数据游标回退保留原证据，选更早已完成可信checkpoint并说明数据回退/重复风险。已发布公共Wiki只保留可复用机制与最终关键结果，逐次恢复log进任务档案。

## 测试与更新

`tests/unit_tests/test_checkpointing.py`与dist-checkpoint/rerun测试提供格式/状态入口；相关case需要实际多rank、storage和backend时保留现场缺口。源码unit pass不证明完整模型转换、异步故障注入或全规模恢复已完成。

training/Core任一save/load、optimizer state schema或consumer数据loader变化，联动本页、[training/loss](training-and-loss.md)、[memory](memory.md)、[Bridge](../../../../bridge/knowledgebase/local/overview/bridge.md)/[Energon](../../../../energon/knowledgebase/local/overview/energon.md)和长稳Skill。release迁移说明、特性PR和最终code一起读，避免只改overview的SHA。

## 固定源码与维护边界

- [megatron/core/dist_checkpointing/serialization.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/dist_checkpointing/serialization.py)
- [megatron/training/checkpointing.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/training/checkpointing.py)
- [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/training/training.py)
- [megatron/core/rerun_state_machine.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/megatron/core/rerun_state_machine.py)
- [tests/unit_tests/test_checkpointing.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/tests/unit_tests/test_checkpointing.py)
- [tests/unit_tests/dist_checkpointing/test_rerun_state_machine_ckpt.py](https://github.com/NVIDIA/Megatron-LM/blob/21334a44ede0b8497d1770d0b80bc115e777bd00/tests/unit_tests/dist_checkpointing/test_rerun_state_machine_ckpt.py)

2026-11-04按上述固定源码、实际消费者与官方教程复核。源码机制、上游测试和HCU现场验收分别记录；本轮没有执行GPU训练或填造性能/loss结果。更新需同时核对同仓总览、相关专题/案例、消费者与Skill，发布/主干/开发PR/实际HCU依赖不得混作同一个版本。
