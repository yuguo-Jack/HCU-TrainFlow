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
reviewed_on: '2026-11-04'
coverage: reviewed implementation chains and official guides; not all models, backends
  or HCU runtime qualification
sources:
- source: vllm-project-vllm
  path: docs/training/weight_transfer/README.md
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: f99e82bb5c95f9e3353d8e27d64ee8d2ab48a05f9ecd270e5334bcbb697dbdc7
- source: vllm-project-vllm
  path: docs/training/weight_transfer/base.md
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: befc4b02a9839213dbde4393ba6730510ecd3e1de397fcabeb61fdfe8a98aaf1
- source: vllm-project-vllm
  path: docs/training/weight_transfer/nccl.md
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: ac863b4183ed7f3e6dd1cc365070162ebfba739a31bc422edaea97f8af98da91
- source: vllm-project-vllm
  path: docs/training/weight_transfer/ipc.md
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 67d977b79d936886c30312a48c7457202e6acaf385a8bf693f56314e3687d2fd
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/base.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 483e5d894d8c76898dfbd9851d5d71a02ff4775d4bc98e9110da2079e82049f6
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/factory.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: f94d93413002061cfeeea79af68745d589b9b6adbc14b1c08a0525166d010426
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/nccl_engine.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 28c3c1abbd3f2c264965ebbaf67c8292888dbcb4cfdf2a2a741831da11a14965
- source: vllm-project-vllm
  path: vllm/config/weight_transfer.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: cd633f19aaa5b9327398a0dcf98f730ef37d388d6e5bd492e98fab434d61c825
- source: vllm-project-vllm
  path: vllm/v1/worker/gpu_worker.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: a60f9d8c4935eb8e8949ea706a5922aae5df711c32599236319e6b145ad404da
- source: vllm-project-vllm
  path: tests/v1/worker/test_gpu_worker_weight_transfer.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 6207d97b7673c913ab8210b9723c97675058b998e42a6942617742ff797573ff
- source: vllm-project-vllm
  path: docs/training/weight_transfer/m2n.md
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: c158fe7883ca0e20cef9a8a1e8d5cf0252c621ff0489af3bf7e0726eb8d71c27
- source: vllm-project-vllm
  path: tests/distributed/test_weight_transfer_m2n.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: c055cc2308f8489228cc2b39693766ccacd385eb406718b58e8f9753d0dc7be1
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/m2n_common.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: ee82a9ee1dd81fee9cfaf4a58b658948f99979299c84254439a30bd14fa5bbea
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/m2n_engine.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: e58cd48641eedac5eba49da25577e9e85eb63b1769486923de12228712eb5728
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/m2n_trainer.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 32a81809f00334a738a4f90d6795abdff3dc30a82221e34d991019444f0b8722
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/nccl_common.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 810fec408ffaee61fbcc9a1e3fee7654d706ef869a54ebd3113262189bf7157c
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/sharded_rdt_engine.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: eb6e69688023ba67e499463967eaa67d0f5d2510cb1dd72b500c59f5ba4ec5c2
- source: vllm-project-vllm
  path: docs/training/weight_transfer/sharded_rdt.md
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 8d8e0626ca7e59dccb80cae82a9ef3db9ec89dfaa1f9ef867202951ec695d3ab
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/sharded_rdt_common.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: c67ef046b62b3bf60493b805cf39a542350e14b0a49f47151258cfede6002665
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/sharded_rdt_trainer.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 9a08f0d91be0bddecd15776e691ad6afc3a2e09286d16f401b4cbc1cbba47836
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/sharded_rdt_fake.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: ee11164e17b5f2793252ce77741b8b94e0583046abf896a590131b2008d1fbb9
- source: vllm-project-vllm
  path: vllm/distributed/weight_transfer/m2n_layout.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 133025922445c66c74cd0e18706f7fa216752e886d0820b943467a4530d814fa
---

# vLLM 权重传输：双端协议、逐层物化与版本提交

## 同步不是单向拷贝

RL轮次需要明确训练更新后的参数、每个推理副本安装完成、旧KV处理和policy版本。工程入口见[总览](../overview/engineering-guide.md)。当前weight-transfer系统将source、control-plane client、trainer transport、inference transport分开，各端有独立factory；这方便复用消费者wrapper，也使错误更容易隐藏在端与端之间。

## 从训练 export 到 worker 的链路

`WeightSource.metadata` 声明 wire name/dtype/full shape、参数 owners 和分片布局；`iter_full()` 提供拥有参数的完整张量，`iter_local()` 提供本地分片。`VLLMWeightSyncClient` 将初始化、start/update/finish 及 shutdown 控制调用转给 consumer 持有的 rollout 池；`TrainerWeightTransferEngine.send_weights()` 协调 start→一或多次 update 及 data-plane→finish；worker 的 engine 加载、postprocess；消费者再查证版本，不能把底层传输完成当作业务版本已正确发布。

HTTP/Ray client必须触达全部replica并等待完成，不能将权重操作当普通load-balanced推理请求。worker测完不证明train source正确；需要同时确认Megatron/Bridge或FSDP export没有错合并QKV、错专家归属、漏tied参数/scales。

## 两个 metadata 通道与 collective

当前 `metadata` 必须实现为 `functools.cached_property`，子类若仍写成 `metadata()` 或普通 property 会在定义时被拒绝。各训练 rank 保存相同的全模型有序 `ParamMeta`；其中 `owners` 是拥有该参数的全局训练 rank，`mesh_shape` 和 `placements` 描述其布局。元数据只声明，不应隐式传输；模型应先完成分片，再首次读取并冻结 metadata。旧的 `held_names()` 和独立 `M2NWeightSource` / `DTensorModuleSource` 接口已由这套声明取代，不能混用旧消费者。

`ModuleSource` 读取 DTensor 的全局 shape/dtype 和 device mesh；`iter_full()` 对各自拥有的 DTensor 调用 `full_tensor()`，`iter_local()` 通常取 `to_local()`。无法按普通 Shard/Replicate 表达的布局（如 Partial）被声明为 replicated，local 路线也会 gather；不能无条件宣称使用它就没有完整张量。`ModuleSource` 不自动为只持有局部模块的 PP rank 构造相同全模型 metadata，这类消费者须提供正确的自定义 source。

两个迭代模式分别实现，不自动互相推导；每个 rank 只按 metadata 顺序 yield 自己的 `owned_names(rank)`，name/dtype/full 或 local shape 必须匹配。**所有训练 rank** 构建 engine 并并发、同序调用 send_weights，参数的全部 owner 参与相应 gather；M2N 则每个 rank 参与全部 reshard。只让 rank0 运行仍可能在数据发送前就卡在训练内部 collective。

`TrainerInitInfo.rank`显式传入，backend由class常量选择；`WeightTransferConfig`在inference端只选backend。packed、buffer等双端必须一致的wire设置由trainer init握手传达，不应在consumer各端另写不一致默认值。

## 逐层 group 与内存上限

`layerwise_groups` 用参数名字中最外层数字索引划分 layer，MoE `layers.3...experts.7` 按3归组，避免同层专家被拆开；无索引的 embedding/final norm 等形成独立段。sharded-RDT 当前校验展开后的 group 顺序与 metadata 完全一致，因此同层名字在它的 metadata 中须连续；不满足时由该 source 调整顺序。dense NCCL/M2N 不共同要求逐层连续，不能把 RDT 的分组约束推广到所有 `WeightSource`。

逐层gather/传输将临时full tensor、receiver staging等限制在layer/group尺度，但不是零副本。错误group可能把整模型放进一个buffer；过细group增加消息和generator/collective开销。分组按真实module依赖选择，不能将一个需要共同post-load的leaf任意跨组。

部分 ownership 现在通过各 `ParamMeta.owners` 声明；非 owner 不 yield 该参数。sharded-RDT 从相同 metadata 构造路由，并在初始化时校验各 producer 的 metadata 摘要；dense NCCL 也支持满足约束的多 broadcaster。两种协议的发送职责和内存代价不同，不能靠换一个 hook 等价迁移。RDT/NIXL 等须实际安装与平台验证，不能凭 factory 登记就写可用。

## Transport 选择与并发

| Backend | 典型布局 | 重点风险 |
| --- | --- | --- |
| NCCL dense/packed | 训推分离，所有 worker 接收，可有多个 first-owner broadcaster | broadcaster 映射、world/rank offset、packed metadata、receiver 与 broadcast 同时 rendezvous |
| IPC | 同设备可共享tensor | 句柄、source storage存活、进程/设备映射与平台支持 |
| sparse NCCL | 明确checkpoint坐标的delta | patch基版本、索引/shape和多轮完整性 |
| sharded RDT | 大MoE、receiver只需自己的slice | partial ownership、layergroup、transport/watchdog、实际NIXL依赖 |
| nccl_m2n | 训练/推理不同shard布局 | reshard plan、每rank范围与consumer正确导出 |
| ModelExpress | immutable version/checkpoint+delta | 额外包、published version和可选测试矩阵 |

NCCL receive与sender broadcast须并发执行；控制RPC若等receiver完成后才开始send，会形成自造死锁。HCU端逐项核对RCCL/IPC/backend实现及版本，官方NCCL通信语义不能直接等同所有HCU transport。

分区 source 的参数由各自 first owner 广播，transfer group 前部容纳这些 broadcaster（总是包括 rank0），随后才是推理 workers；其他 broadcaster 在别人的轮次也接收并丢弃数据，以维持 collective 顺序。每个 rank 所拥有参数必须共享同一 first owner，rank0 若拥有参数还须是其 first owner，初始化会拒绝不满足的声明。任一 broadcaster 中途失败可能使其余参与者持续阻塞，须核销并重建训练/推理传输状态，不能在原通信组盲目重发。

NCCL receiver 按 target/draft 和 `src` 分别缓存参数列表。首轮、重新初始化后或 names/dtypes/shapes/顺序变化时必须发送完整列表；后续全空列表表示复用原缓存，首次为空并不验证成功加载了模型。trainer engine 以最近成功轮次 metadata 决定复用，手写 HTTP payload 须承担同一协议校验。

## M2N：本地分片与直接落参的边界

`nccl_m2n` 消费统一 `WeightSource` 的 `ParamMeta` 和 `iter_local()`，不再使用独立 source 子类。每个参数须由全部训练 rank 按 rank 顺序拥有，支持 1D/2D mesh 及 Replicate/Shard；PP 等分区 owners 在初始化即被拒绝。Partial 不能直接作为 shard 发送，`ModuleSource` 会改为 replicated 并 gather。自定义 source 必须显式描述布局并提供匹配的本地张量。source/destination 及有序参数计划在初始化时固定并交换摘要，不能每轮静默换布局。

接收端只有未量化且 PP=1 才尝试直接写活参数，还须逐项通过真实名字、dtype、连续存储、loader 身份和声明分片维度校验。shape 相等不够：未知/缺失/wrapped/partial loader、packed 或 transformed 元数据、GPT2 模型级变换等走 full-tensor fallback，再调用模型 `load_weights`。同一 module 有已解析的 fallback 参数时，其直接路径兄弟也降级，避免 layerwise finalization 用旧存储覆盖新值。fallback 的完整张量在接收端形成，训练端仍发送本地分片；收益要按日志中的 **direct byte coverage**、实际网络字节和峰值判断，不能数参数个数。

训练各 rank 同序 reshard，rank0 的接收控制调用与数据面并发；正常路径等待 update、finish 及 round outcome/ACK。发送前同步 producer stream，Torch buffer 用 record_stream 或保留 owner 到最终同步；裸指针的设备、布局和存活期由调用方保证。固定实现要求额外 nccl-extensions/nccl4py 与兼容 NCCL（指南为 >=2.30.5），这些不是默认安装依赖，也不证明 RCCL/HCU 支持。读取了 destination 单元用例和部分分布式测试入口，本轮未运行这些设备测试。

## Sharded RDT：静态 loader 计划与完成边界

此路线在初始化阶段把模型置于 meta，通过 `FakeRDTTensor` 运行真实 loader，记录允许的 view/slice 操作到 `copy_` sink，并保存目标 shape/stride/offset。真正读数据、算术、`.to()`/`.float()`/`.item()`、bool-mask 或 `.data` 等不在支持范围；broadcasting copy 被拒绝。plan 构建时，实际发生 copy 却未完整 bake 的 live name 抛错，没有运行中自动回退到普通 loader。每轮复用静态计划，不能据此推断任意模型或任意后续名字变更都能支持。

receiver 只 pull 所需 slice，但 producer 仍按 group gather/export；`ParamMeta.owners` 解决 ownership，不消除训练内部 collective。下一次 gather 前，只有未释放 group 超过 lookahead 时才阻塞等待 credit；credit 要在所有 live consumer 的 free signal 到齐后释放，驻留上限是 `gather_lookahead + 1` 个 group，而单个大 embedding/group 仍可能很大。receive/serve ring 还占额外缓冲与 NIXL 注册资源，不包含在推理 KV 的 `gpu_memory_utilization` 预算内。

`update_weights` 路线会把 scatter/量化交给后台队列；成功返回的 `finish_weight_update` 才表明 drain 已等待 process/quant 队列、stream 和 pending free RPC，避免迟到 credit 污染下一轮。process 错误可能在 free RPC 排空前抛出，失败后不能直接复用 credit 开新轮。shutdown 会记录 drain 异常并限时 join 线程，因此 shutdown 返回不能补作 finish 成功证据。`live_consumer_ids` 必须由所有训练 rank 使用相同集合；降级只改变本轮 live 数，原 provisioning geometry 仍冻结，不自动提供重分片或版本事务恢复。

当前指南要求 Ray >=2.56、NIXL、Ray executor 及训推分离，并拒绝 EPLB。参数名字与 group 必须覆盖同一 leaf 的依赖，完整发布仍检查全部副本、后处理、版本和新 policy 的 logits。这里核对的是固定实现的选择与完成语义；未执行 RDMA、Ray 或 HCU 集成验证。

## 版本提交、测试与回退

当前 HTTP 路线允许 trainer 不安装 vLLM，但消费者仍须遵守同一初始化、collective、分块和存储完成契约。NCCL 初始化需要 trainer 与接收端并发进入通信组，并按协议参加初始 warmup collective；同步接收 RPC 与发送数据会制造死锁。shutdown 只释放传输通道，可以保留推理服务。

Packed NCCL 在超过阈值后闭合 chunk，跨阈值 tensor 仍在本块；packed IPC 在下一 tensor 将溢出前闭合，单 tensor 超 buffer 直接失败。不能共享一个凭直觉编写的 chunk splitter。发送存储须一直保留到消费者完成，协议接口存在也不代表目标平台已实现相应 IPC 或通信路径。

官方文档明确：update 失败可留下部分已加载参数，health 仍200，随后 finish 被拒绝。恢复生成前应从可信完整参数重新执行 start→全部 update→finish 并检查每个副本；不能继续半轮、只补最后一块或只写 version。GPU worker 还在 draft 更新期间处理共享的未量化 LM head 与量化副本，finish 后重新派生副本，失败时恢复相应 head 状态；target/draft、scale 和缓存需单独回归。

worker 当前在 start 可能移动权重之前就登记 target/draft 的 incomplete 标记，只有该对象成功 finish 才清除；一次失败不能靠更新另一对象来核销。update 异常会结束活动会话并保留 incomplete，finish 异常则须区分 direct-reload 等路径，不能假设所有 backend 都已结束会话或都允许直接重试。临时 KV 借用在收尾释放不等于参数已恢复，成功 target finish 后还会重置 LoRA 状态；失败后先核对实际状态，再决定完整重载或重建。

暂停生成并处理在途请求→start→传输全部group→load/postprocess→finish(版本)→全部副本查证→恢复生成。`/update_weight_version`仅改标签不能代替装载；control回执、参数校验、固定prompt logits/logprob与样本policy版本共同构成证据。

worker测试覆盖double-start、会话外update、rank-local payload选取、LoRA命名和委派；真实distributed测试再验证transport/collective，模型测试覆盖loader和quantization。可选backend缺package时保留skip，不把全局测试绿灯称该backend已验。

OOM/卡住时分别量化export/gather、packing、发送、receive、load/postprocess与barrier，并记录per-layer bytes、峰值、model参数总量和网络数据量。接收端失败或controller timeout先核对原操作状态与每worker版本，保留失败证据，按可信checkpoint/version重建；不假定半轮更新具有整模型事务回滚。

## 固定证据与验证范围

- [docs/training/weight_transfer/README.md](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/docs/training/weight_transfer/README.md)
- [docs/training/weight_transfer/base.md](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/docs/training/weight_transfer/base.md)
- [docs/training/weight_transfer/nccl.md](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/docs/training/weight_transfer/nccl.md)
- [docs/training/weight_transfer/ipc.md](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/docs/training/weight_transfer/ipc.md)
- [vllm/distributed/weight_transfer/base.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/distributed/weight_transfer/base.py)
- [vllm/distributed/weight_transfer/factory.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/distributed/weight_transfer/factory.py)
- [vllm/distributed/weight_transfer/nccl_engine.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/distributed/weight_transfer/nccl_engine.py)
- [vllm/config/weight_transfer.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/config/weight_transfer.py)
- [vllm/v1/worker/gpu_worker.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/v1/worker/gpu_worker.py)
- [tests/v1/worker/test_gpu_worker_weight_transfer.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/tests/v1/worker/test_gpu_worker_weight_transfer.py)

- [docs/training/weight_transfer/m2n.md](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/docs/training/weight_transfer/m2n.md)
- [tests/distributed/test_weight_transfer_m2n.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/tests/distributed/test_weight_transfer_m2n.py)
- [vllm/distributed/weight_transfer/m2n_common.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/distributed/weight_transfer/m2n_common.py)
- [vllm/distributed/weight_transfer/m2n_engine.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/distributed/weight_transfer/m2n_engine.py)
- [vllm/distributed/weight_transfer/m2n_trainer.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/distributed/weight_transfer/m2n_trainer.py)
- [vllm/distributed/weight_transfer/nccl_common.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/distributed/weight_transfer/nccl_common.py)
- [vllm/distributed/weight_transfer/sharded_rdt_engine.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/distributed/weight_transfer/sharded_rdt_engine.py)
- [docs/training/weight_transfer/sharded_rdt.md](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/docs/training/weight_transfer/sharded_rdt.md)
- [vllm/distributed/weight_transfer/sharded_rdt_common.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/distributed/weight_transfer/sharded_rdt_common.py)
- [vllm/distributed/weight_transfer/sharded_rdt_trainer.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/distributed/weight_transfer/sharded_rdt_trainer.py)
- [vllm/distributed/weight_transfer/sharded_rdt_fake.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/distributed/weight_transfer/sharded_rdt_fake.py)
- [vllm/distributed/weight_transfer/m2n_layout.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/distributed/weight_transfer/m2n_layout.py)

本页在 2026-11-04 按具体机制阅读上述固定源码和教程（大型 engine/trainer/test 文件为选段追踪，非逐文件全读）；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。
