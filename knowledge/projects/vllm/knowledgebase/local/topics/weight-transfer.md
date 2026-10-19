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
reviewed_on: '2026-10-20'
coverage: reviewed implementation chains and official guides; not all models, backends
  or HCU runtime qualification
sources:
- source: vllm-project-vllm
  path: docs/training/weight_transfer/README.md
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: a307f0cf03d6b2581c43ac745a872b7b0d4df4c08b8a2e843633abf0351a35be
- source: vllm-project-vllm
  path: docs/training/weight_transfer/base.md
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: e127d6cb72b0c6881ec6edbca650032245e1ad3fcd2ecab5fe49bd0c5c11f805
- source: vllm-project-vllm
  path: docs/training/weight_transfer/nccl.md
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: 06e3008879ca778a1a6c2782d75305bcceefd812887e460c9319eaa7f29739f9
- source: vllm-project-vllm
  path: docs/training/weight_transfer/ipc.md
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: 32f452e9546a50cecc1069a2457b4b3be696ca9d7e633f6f92eda58e02078f51
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/base.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: 9850e67532ab4599c00f89a530c20b6c9fd657edb4517b40c910d4872fe88ad5
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/factory.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: f94d93413002061cfeeea79af68745d589b9b6adbc14b1c08a0525166d010426
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/nccl_engine.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: b5a94c11fc4fa131c79335baa1a05be546a9386561a671c98f9928596716408a
- source: vllm-project-vllm
  path: vllm/config/weight_transfer.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: cd633f19aaa5b9327398a0dcf98f730ef37d388d6e5bd492e98fab434d61c825
- source: vllm-project-vllm
  path: vllm/v1/worker/gpu_worker.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: b401a1e0579df877f16184cb2850f4ddf034bb60f9877500e324fd586a563e20
- source: vllm-project-vllm
  path: tests/v1/worker/test_gpu_worker_weight_transfer.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: 4d4b4779e4f0fcfac6ff29df30584b32722ca243f6faf74d46ddbd432c34e33e
- source: vllm-project-vllm
  path: docs/training/weight_transfer/m2n.md
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: 664b7d70cf8e7e7ac218377c56b9185ca4e791ee3ac2f2cf468a9ca559502992
- source: vllm-project-vllm
  path: tests/distributed/test_weight_transfer_m2n.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: e2ef8e95d3aeb301fd6919d5f775486dfdf28e897442022a5e817f65a0e8c3f4
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/m2n_common.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: 07cf30321552788ae2af07282296b26796082cb4c1b5b3b81a3e8f841168b29e
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/m2n_engine.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: 5c79d845eaef59140b3f90d5e2ebf4f613a12e8a6047a453a740df57ab780308
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/m2n_source.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: 3913c89c52149b3cf8bc2695ee05f170833a03aa0213846c51b6f76ca5ef6a33
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/m2n_trainer.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: 315e578d2ea43e0027abd7f3ca4c614140cbd6012b019bf08a38450b41e87a3f
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/nccl_common.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: 129d3dedcebcea3cdace793db761ca33db580d61da74984086fbd20b51b2c700
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/sharded_rdt_engine.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: dffb79d6a815d139eb118c66c3f11fea7335df1300e1a4af7dd08aafb305a205
- source: vllm-project-vllm
  path: docs/training/weight_transfer/sharded_rdt.md
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: 2ae5f7667f5dcabd638b98abed9b1766bf31c39d094c5457a42dffe13d2c5c2d
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/sharded_rdt_common.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: c67ef046b62b3bf60493b805cf39a542350e14b0a49f47151258cfede6002665
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/sharded_rdt_trainer.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: afa7cb656fd14c59069a77156a28f7da3b3a04ea4e04ce63f522f7a96c32d604
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/sharded_rdt_fake.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: ee11164e17b5f2793252ce77741b8b94e0583046abf896a590131b2008d1fbb9
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/m2n_layout.py
  commit: bde4d001130e5112d984ba99f0546e22c09e1a89
  sha256: 133025922445c66c74cd0e18706f7fa216752e886d0820b943467a4530d814fa
---

# vLLM 权重传输：双端协议、逐层物化与版本提交

## 同步不是单向拷贝

RL轮次需要明确训练更新后的参数、每个推理副本安装完成、旧KV处理和policy版本。工程入口见[总览](../overview/engineering-guide.md)。当前weight-transfer系统将source、control-plane client、trainer transport、inference transport分开，各端有独立factory；这方便复用消费者wrapper，也使错误更容易隐藏在端与端之间。

## 从训练 export 到 worker 的链路

`WeightSource.metadata()`给wire name/dtype/full shape；普通 `ModuleSource` 迭代给完整 materialized tensor，M2N 专用 source 则给本地分片。`VLLMWeightSyncClient`将初始化、start/update/finish 及 shutdown 控制调用转给 consumer 持有的 rollout 池；`TrainerWeightTransferEngine.send_weights()`协调start→一或多次update及data-plane→finish；worker 的 engine 加载、postprocess；消费者再查证版本，不能把底层传输完成当作业务版本已正确发布。

HTTP/Ray client必须触达全部replica并等待完成，不能将权重操作当普通load-balanced推理请求。worker测完不证明train source正确；需要同时确认Megatron/Bridge或FSDP export没有错合并QKV、错专家归属、漏tied参数/scales。

## 两个 metadata 通道与 collective

`ModuleSource`读取DTensor全局shape/dtype生成metadata而不allgather；迭代中的`materialize_full_tensor`对DTensor调用`full_tensor()`。自定义source可能需要首次export才能发现shape，此时缓存metadata以免每轮重复全模型gather。

metadata 与迭代必须逐项同 name、顺序和 dtype，普通 source 的 shape 是完整 tensor，M2N source 则按声明布局验证 local shape；每轮新迭代可重复。**所有训练 rank** 构建 engine 并同序调用 send_weights；broadcast 的 rank0 是 sender，其他 rank 仍参与 materialize collective；M2N 则各 rank 同序参与 reshard。只让rank0运行可能卡在FSDP/TP/PP/EP的内部gather，而此时网络传权还没开始。

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

## M2N：本地分片与直接落参的边界

`nccl_m2n` 使用独立的 `M2NWeightSource`：metadata 还声明每个参数的 source mesh/placement，迭代返回本地 buffer；`DTensorModuleSource` 调用 `to_local()`，不走普通 source 的 `full_tensor()`。没有 mesh 的 tensor 按 replicated 看待，隐式分片需自定义 source 明确声明。当前只接受连续的训练 rank 范围、1D/2D mesh 与 Replicate/Shard，拒绝 Partial。source/destination 及有序参数计划在初始化时固定并交换摘要，不能每轮静默换布局。

接收端只有未量化且 PP=1 才尝试直接写活参数，还须逐项通过真实名字、dtype、连续存储、loader 身份和声明分片维度校验。shape 相等不够：未知/缺失/wrapped/partial loader、packed 或 transformed 元数据、GPT2 模型级变换等走 full-tensor fallback，再调用模型 `load_weights`。同一 module 有已解析的 fallback 参数时，其直接路径兄弟也降级，避免 layerwise finalization 用旧存储覆盖新值。fallback 的完整张量在接收端形成，训练端仍发送本地分片；收益要按日志中的 **direct byte coverage**、实际网络字节和峰值判断，不能数参数个数。

训练各 rank 同序 reshard，rank0 的接收控制调用与数据面并发；正常路径等待 update、finish 及 round outcome/ACK。发送前同步 producer stream，Torch buffer 用 record_stream 或保留 owner 到最终同步；裸指针的设备、布局和存活期由调用方保证。固定实现要求额外 nccl-extensions/nccl4py 与兼容 NCCL（指南为 >=2.30.5），这些不是默认安装依赖，也不证明 RCCL/HCU 支持。读取了 destination 单元用例和部分分布式测试入口，本轮未运行这些设备测试。

## Sharded RDT：静态 loader 计划与完成边界

此路线在初始化阶段把模型置于 meta，通过 `FakeRDTTensor` 运行真实 loader，记录允许的 view/slice 操作到 `copy_` sink，并保存目标 shape/stride/offset。真正读数据、算术、`.to()`/`.float()`/`.item()`、bool-mask 或 `.data` 等不在支持范围；broadcasting copy 被拒绝。plan 构建时，实际发生 copy 却未完整 bake 的 live name 抛错，没有运行中自动回退到普通 loader。每轮复用静态计划，不能据此推断任意模型或任意后续名字变更都能支持。

receiver 只 pull 所需 slice，但 producer 仍按 group gather/export；`held_names()` 解决 ownership，不消除训练内部 collective。下一次 gather 前，只有未释放 group 超过 lookahead 时才阻塞等待 credit；credit 要在所有 live consumer 的 free signal 到齐后释放，驻留上限是 `gather_lookahead + 1` 个 group，而单个大 embedding/group 仍可能很大。receive/serve ring 还占额外缓冲与 NIXL 注册资源，不包含在推理 KV 的 `gpu_memory_utilization` 预算内。

`update_weights` 路线会把 scatter/量化交给后台队列；成功返回的 `finish_weight_update` 才表明 drain 已等待 process/quant 队列、stream 和 pending free RPC，避免迟到 credit 污染下一轮。process 错误可能在 free RPC 排空前抛出，失败后不能直接复用 credit 开新轮。shutdown 会记录 drain 异常并限时 join 线程，因此 shutdown 返回不能补作 finish 成功证据。`live_consumer_ids` 必须由所有训练 rank 使用相同集合；降级只改变本轮 live 数，原 provisioning geometry 仍冻结，不自动提供重分片或版本事务恢复。

当前指南要求 Ray >=2.56、NIXL、Ray executor 及训推分离，并拒绝 EPLB。参数名字与 group 必须覆盖同一 leaf 的依赖，完整发布仍检查全部副本、后处理、版本和新 policy 的 logits。这里核对的是固定实现的选择与完成语义；未执行 RDMA、Ray 或 HCU 集成验证。

## 版本提交、测试与回退

当前 HTTP 路线允许 trainer 不安装 vLLM，但消费者仍须遵守同一初始化、collective、分块和存储完成契约。NCCL 初始化需要 trainer 与接收端并发进入通信组，并按协议参加初始 warmup collective；同步接收 RPC 与发送数据会制造死锁。shutdown 只释放传输通道，可以保留推理服务。

Packed NCCL 在超过阈值后闭合 chunk，跨阈值 tensor 仍在本块；packed IPC 在下一 tensor 将溢出前闭合，单 tensor 超 buffer 直接失败。不能共享一个凭直觉编写的 chunk splitter。发送存储须一直保留到消费者完成，协议接口存在也不代表目标平台已实现相应 IPC 或通信路径。

官方文档明确：update 失败可留下部分已加载参数，health 仍200，随后 finish 被拒绝。恢复生成前应从可信完整参数重新执行 start→全部 update→finish 并检查每个副本；不能继续半轮、只补最后一块或只写 version。GPU worker 还在 draft 更新期间处理共享的未量化 LM head 与量化副本，finish 后重新派生副本，失败时恢复相应 head 状态；target/draft、scale 和缓存需单独回归。

暂停生成并处理在途请求→start→传输全部group→load/postprocess→finish(版本)→全部副本查证→恢复生成。`/update_weight_version`仅改标签不能代替装载；control回执、参数校验、固定prompt logits/logprob与样本policy版本共同构成证据。

worker测试覆盖double-start、会话外update、rank-local payload选取、LoRA命名和委派；真实distributed测试再验证transport/collective，模型测试覆盖loader和quantization。可选backend缺package时保留skip，不把全局测试绿灯称该backend已验。

OOM/卡住时分别量化export/gather、packing、发送、receive、load/postprocess与barrier，并记录per-layer bytes、峰值、model参数总量和网络数据量。接收端失败或controller timeout先核对原操作状态与每worker版本，保留失败证据，按可信checkpoint/version重建；不假定半轮更新具有整模型事务回滚。

## 固定证据与验证范围

- [docs/training/weight_transfer/README.md](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/docs/training/weight_transfer/README.md)
- [docs/training/weight_transfer/base.md](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/docs/training/weight_transfer/base.md)
- [docs/training/weight_transfer/nccl.md](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/docs/training/weight_transfer/nccl.md)
- [docs/training/weight_transfer/ipc.md](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/docs/training/weight_transfer/ipc.md)
- [vllm/distributed/weight_transfer/base.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/distributed/weight_transfer/base.py)
- [vllm/distributed/weight_transfer/factory.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/distributed/weight_transfer/factory.py)
- [vllm/distributed/weight_transfer/nccl_engine.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/distributed/weight_transfer/nccl_engine.py)
- [vllm/config/weight_transfer.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/config/weight_transfer.py)
- [vllm/v1/worker/gpu_worker.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/v1/worker/gpu_worker.py)
- [tests/v1/worker/test_gpu_worker_weight_transfer.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/tests/v1/worker/test_gpu_worker_weight_transfer.py)

- [docs/training/weight_transfer/m2n.md](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/docs/training/weight_transfer/m2n.md)
- [tests/distributed/test_weight_transfer_m2n.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/tests/distributed/test_weight_transfer_m2n.py)
- [vllm/distributed/weight_transfer/m2n_common.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/distributed/weight_transfer/m2n_common.py)
- [vllm/distributed/weight_transfer/m2n_engine.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/distributed/weight_transfer/m2n_engine.py)
- [vllm/distributed/weight_transfer/m2n_source.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/distributed/weight_transfer/m2n_source.py)
- [vllm/distributed/weight_transfer/m2n_trainer.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/distributed/weight_transfer/m2n_trainer.py)
- [vllm/distributed/weight_transfer/nccl_common.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/distributed/weight_transfer/nccl_common.py)
- [vllm/distributed/weight_transfer/sharded_rdt_engine.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/distributed/weight_transfer/sharded_rdt_engine.py)
- [docs/training/weight_transfer/sharded_rdt.md](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/docs/training/weight_transfer/sharded_rdt.md)
- [vllm/distributed/weight_transfer/sharded_rdt_common.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/distributed/weight_transfer/sharded_rdt_common.py)
- [vllm/distributed/weight_transfer/sharded_rdt_trainer.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/distributed/weight_transfer/sharded_rdt_trainer.py)
- [vllm/distributed/weight_transfer/sharded_rdt_fake.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/distributed/weight_transfer/sharded_rdt_fake.py)
- [vllm/distributed/weight_transfer/m2n_layout.py](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/vllm/distributed/weight_transfer/m2n_layout.py)

本页在 2026-10-20 按具体机制阅读上述固定源码和教程（大型 engine/trainer/test 文件为选段追踪，非逐文件全读）；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。
