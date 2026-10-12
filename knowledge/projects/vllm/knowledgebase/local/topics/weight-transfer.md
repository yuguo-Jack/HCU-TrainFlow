---
id: engines/vllm/weight-transfer
title: vLLM 权重传输：双端协议、逐层物化与版本提交
engine: vllm
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: reviewed implementation chains and official guides; not all models, backends
  or HCU runtime qualification
sources:
- source: vllm-project-vllm
  path: docs/training/weight_transfer/README.md
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: 0667bf0764bba25629a931ad8c81801517cfc4a478d4b57286cdeb5591e40518
- source: vllm-project-vllm
  path: docs/training/weight_transfer/base.md
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: e127d6cb72b0c6881ec6edbca650032245e1ad3fcd2ecab5fe49bd0c5c11f805
- source: vllm-project-vllm
  path: docs/training/weight_transfer/nccl.md
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: a123a9de8b1a42fa0ef64ef3852c707fdb561b23c6169a4ee19442d02da2c473
- source: vllm-project-vllm
  path: docs/training/weight_transfer/ipc.md
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: 8c191be68ab53aa6fe213a890ca928ea7105228df838eaa2d235e1cdf2a3a597
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/base.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: 9850e67532ab4599c00f89a530c20b6c9fd657edb4517b40c910d4872fe88ad5
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/factory.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: f94d93413002061cfeeea79af68745d589b9b6adbc14b1c08a0525166d010426
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/nccl_engine.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: b5a94c11fc4fa131c79335baa1a05be546a9386561a671c98f9928596716408a
- source: vllm-project-vllm
  path: vllm/config/weight_transfer.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: cd633f19aaa5b9327398a0dcf98f730ef37d388d6e5bd492e98fab434d61c825
- source: vllm-project-vllm
  path: vllm/v1/worker/gpu_worker.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: e970aa29a738aa15cd963d9f9202ca6d3d504e98fd344959fd998e940472a5a0
- source: vllm-project-vllm
  path: tests/v1/worker/test_gpu_worker_weight_transfer.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: aa88face06df5f7e7313211e22845474670e1437218ec99165efce40b25a1a67
---

# vLLM 权重传输：双端协议、逐层物化与版本提交

## 同步不是单向拷贝

RL轮次需要明确训练更新后的参数、每个推理副本安装完成、旧KV处理和policy版本。工程入口见[总览](../overview/engineering-guide.md)。当前weight-transfer系统将source、control-plane client、trainer transport、inference transport分开，各端有独立factory；这方便复用消费者wrapper，也使错误更容易隐藏在端与端之间。

## 从训练 export 到 worker 的链路

`WeightSource.metadata()`给wire name/dtype/full shape，迭代给完整materialized tensor；`VLLMWeightSyncClient`将四个控制调用转给consumer持有的rollout池；`TrainerWeightTransferEngine.send_weights()`协调start→一或多次update及data-plane→finish；worker的engine加载、postprocess和提交version。

HTTP/Ray client必须触达全部replica并等待完成，不能将权重操作当普通load-balanced推理请求。worker测完不证明train source正确；需要同时确认Megatron/Bridge或FSDP export没有错合并QKV、错专家归属、漏tied参数/scales。

## 两个 metadata 通道与 collective

`ModuleSource`读取DTensor全局shape/dtype生成metadata而不allgather；迭代中的`materialize_full_tensor`对DTensor调用`full_tensor()`。自定义source可能需要首次export才能发现shape，此时缓存metadata以免每轮重复全模型gather。

metadata与迭代必须逐项同name、顺序、shape和dtype，每轮新迭代可重复。**所有训练rank**构建engine并同序调用send_weights；rank0仅是sender，其他rank仍参与materialize collective。只让rank0运行可能卡在FSDP/TP/PP/EP的内部gather，而此时网络传权还没开始。

`TrainerInitInfo.rank`显式传入，backend由class常量选择；`WeightTransferConfig`在inference端只选backend。packed、buffer等双端必须一致的wire设置由trainer init握手传达，不应在consumer各端另写不一致默认值。

## 逐层 group 与内存上限

`layerwise_groups`用参数名字中最外层数字索引划分layer，MoE `layers.3...experts.7`按3归组，避免同层专家被拆开；无索引的embedding/final norm等形成独立段。相同layer的名字必须连续，source如果按tensor类别而不是层排列，需先重排。

逐层gather/传输将临时full tensor、receiver staging等限制在layer/group尺度，但不是零副本。错误group可能把整模型放进一个buffer；过细group增加消息和generator/collective开销。分组按真实module依赖选择，不能将一个需要共同post-load的leaf任意跨组。

`held_names()`提供partial ownership时，metadata仍描述全模型，各name至少一个owner，非owner按顺序yield None。官方文档当前限定该模式由sharded-RDT路由支持，broadcast backend不能靠这个hook自动避免全模型传输。RDT/NIXL等须实际安装与平台验证，不能凭factory登记就写可用。

## Transport 选择与并发

| Backend | 典型布局 | 重点风险 |
| --- | --- | --- |
| NCCL dense/packed | 训推分离，所有worker接收 | world/rank offset、packed metadata、receiver与broadcast同时rendezvous |
| IPC | 同设备可共享tensor | 句柄、source storage存活、进程/设备映射与平台支持 |
| sparse NCCL | 明确checkpoint坐标的delta | patch基版本、索引/shape和多轮完整性 |
| sharded RDT | 大MoE、receiver只需自己的slice | partial ownership、layergroup、transport/watchdog、实际NIXL依赖 |
| nccl_m2n | 训练/推理不同shard布局 | reshard plan、每rank范围与consumer正确导出 |
| ModelExpress | immutable version/checkpoint+delta | 额外包、published version和可选测试矩阵 |

NCCL receive与sender broadcast须并发执行；控制RPC若等receiver完成后才开始send，会形成自造死锁。HCU端逐项核对RCCL/IPC/backend实现及版本，官方NCCL通信语义不能直接等同所有HCU transport。

## 版本提交、测试与回退

暂停生成并处理在途请求→start→传输全部group→load/postprocess→finish(版本)→全部副本查证→恢复生成。`/update_weight_version`仅改标签不能代替装载；control回执、参数校验、固定prompt logits/logprob与样本policy版本共同构成证据。

worker测试覆盖double-start、会话外update、rank-local payload选取、LoRA命名和委派；真实distributed测试再验证transport/collective，模型测试覆盖loader和quantization。可选backend缺package时保留skip，不把全局测试绿灯称该backend已验。

OOM/卡住时分别量化export/gather、packing、发送、receive、load/postprocess与barrier，并记录per-layer bytes、峰值、model参数总量和网络数据量。接收端失败或controller timeout先核对原操作状态与每worker版本，保留失败证据，按可信checkpoint/version重建；不假定半轮更新具有整模型事务回滚。

## 固定证据与验证范围

- [docs/training/weight_transfer/README.md](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/docs/training/weight_transfer/README.md)
- [docs/training/weight_transfer/base.md](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/docs/training/weight_transfer/base.md)
- [docs/training/weight_transfer/nccl.md](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/docs/training/weight_transfer/nccl.md)
- [docs/training/weight_transfer/ipc.md](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/docs/training/weight_transfer/ipc.md)
- [vllm/distributed/weight_transfer/base.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/vllm/distributed/weight_transfer/base.py)
- [vllm/distributed/weight_transfer/factory.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/vllm/distributed/weight_transfer/factory.py)
- [vllm/distributed/weight_transfer/nccl_engine.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/vllm/distributed/weight_transfer/nccl_engine.py)
- [vllm/config/weight_transfer.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/vllm/config/weight_transfer.py)
- [vllm/v1/worker/gpu_worker.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/vllm/v1/worker/gpu_worker.py)
- [tests/v1/worker/test_gpu_worker_weight_transfer.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/tests/v1/worker/test_gpu_worker_weight_transfer.py)

本页在 2026-10-12 阅读上述固定源码和教程；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。
