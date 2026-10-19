---
id: engines/sglang/memory-and-scheduling
title: SGLang 显存与 rollout 调度：睡眠、KV、prefix 与数值边界
engine: sglang
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-20'
coverage: reviewed implementation chains and official guides; not all models, backends or HCU runtime qualification
sources:
- source: sgl-project-sglang
  path: docs/docs/advanced_features/sglang_for_rl.mdx
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 751d2c54c7cc87780a7e9005a76930f73a562c6cf4d9db1574bef4eafaeecd76
- source: sgl-project-sglang
  path: docs/docs/advanced_features/session_radix_cache.mdx
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 0b50a3e5b8b5e97d3ce035801d18183ce1fa06dba9f6644f9c0f75bc0bf748cd
- source: sgl-project-sglang
  path: docs/docs/advanced_features/hicache_design.mdx
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: ea9e7896aeeba4f648c3484b382780ce735bba74e0a74dd5403bf7a0438305b5
- source: sgl-project-sglang
  path: docs/docs/basic_usage/sampling_params.mdx
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: e3bd51e0d6d8ddcdf805fa275a40dac150cdd16f5fd7fdbb425f9330eb52e84e
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: fc96ed4b680fdf55621a5397f844cfd4cbd30213f44eec8a888b7cce75cafe60
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler_components/weight_updater.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 7e2f08d8c1ca67965261208f51bab17d0ab0bfd5b87a009d9dbd97fc381542e4
- source: sgl-project-sglang
  path: python/sglang/srt/utils/torch_memory_saver_adapter.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 139937ef272be19ddc48e0c5024d7860fa74f7321b4479694c234408b4c60f12
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/radix_cache.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: eea7015fcf678167ac7296b08c8dc568ccbe42a4bb106da23b33a7c59debec01
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/memory_pool.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: f5b306efdaeb5c59ebad99032246014bba39a50bd7cb37f48ea488e201a53d5b
- source: sgl-project-sglang
  path: test/registered/rl/test_multi_instance_release_memory_occupation.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 3f746be087e1ee08cdb7287ed12cb3e3016dec9551f321c382bc2a4de4aabbc8
- source: sgl-project-sglang
  path: python/sglang/srt/model_executor/model_runner_components/load_model_utils.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: a96385e26e8e1c55d973c10e0b7ea63ad5c2ea2542ff2e3ecec93326ae4b6ae2
- source: sgl-project-sglang
  path: python/sglang/srt/weight_cache/ipc_loader.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 14487b4d00cd47e2000821c77969afb879a4e19a1257e3a846b0bfec897f8c44
- source: sgl-project-sglang
  path: python/sglang/srt/weight_cache/protocol.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: d42733448d27904f0fdfedb37fc190f3739fd77decec22b396738bc516bf38fb
- source: sgl-project-sglang
  path: test/registered/unit/model_loader/test_weight_cache_protocol.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 0c9278784590e6929a01877d1f621d644f5458901a3bcea98162c8c5247a12df
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/allocator/base.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 17c07a9ab32c62932048d3579e620eaa2e2558b03b828df152b2ee953c4bfe32
- source: sgl-project-sglang
  path: python/sglang/srt/managers/schedule_policy.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: 28f57c7a6ef21f386d9083f24cbc4077280dd31e7abbc94667c904f9365aec68
- source: sgl-project-sglang
  path: python/sglang/srt/managers/schedule_batch.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: b4097d82650ad48ac13e4a5b7cdedb8fadcef4e5716e738dd4bd88602abe8fbd
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/allocator/unified_hybrid_swa.py
  commit: 8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043
  sha256: c1aff672bcbc95d4d9054a599d10984f370f5449fe61b2efa2c5ce124e1f93bf
---

# SGLang 显存与 rollout 调度：睡眠、KV、prefix 与数值边界

## 共卡训练的资源问题

生成服务峰值由权重、KV、图池、attention/MoE workspace和接收buffer组成。训练optimizer、激活和通信同卡驻留时，两个各自能跑的组件合起来可能OOM。先识别当前consumer是共卡轮换、独立训推设备还是异步重叠；不同布局分别决定release、refit和调度，不能采用同一个内存比例。

## release/resume 的真实调用链

Engine/API控制请求→Scheduler→`SchedulerWeightUpdaterManager.release_memory_occupation`→`TorchMemorySaverAdapter.pause(tag)`；恢复走adapter.resume并恢复模型静态buffer。release要求`is_fully_idle`，paused时可以按实现忽略waiting，但仍需保证实际在途执行结束。它不是强制杀掉GPU任务的接口。

源码当前处理`kv_cache`、`weights`和`cuda_graph`等memory tags；教程表格主要列weights/KV，选用tag仍以实际fork和`io_struct`约束为准。manager 当前显式备份/恢复的是 target runner 的 named_buffers，并非所有 target/draft 状态的统一快照。TP CPU组barrier与device synchronization参与交接；“仅参数回来了”仍可能缺scale/RoPE或其他角色的状态。

`TorchMemorySaverAdapter.create(enable=True)`在所需package缺失时抛导入错误；未启用时选择Noop adapter，pause/resume不会节省显存。必须看实际adapter与前后占用，不能看到API返回就写内存验收通过。当前weight-cache共享模式会显式禁止释放/恢复weights，避免IPC peers引用已释放storage；这种场景应选择兼容部署，不绕过断言。

tag 操作不是原子事务：release 先记录 offload tags，可能已暂停/flush KV 后才遇到 weights 门禁；resume 先移除记录并恢复 graph，再检查 weights。因此失败不能解释为“所有 tag 都没动过”。保存每个 tag 的实际完成点，再由既有恢复 owner 处理，不能盲目重放默认全量 tags。在线 refit 还可能因派生权重缓存被拒绝，参见 [加载门禁](weight-update.md#在线更新的门禁与派生权重)；单独 flush 旧 KV 不解除该限制。

## 共享权重与sleep的边界

当 `weight_cache_mode` 非 off 时，加载配置切到 `IPC_CACHE`；成功路径把 daemon 已处理的权重映射给 client，并在模型上保留 tensor 和 transport 引用。加载 helper 在这种模式下关闭 weights CPU backup。它与复制一份参数后各自训练/睡眠的布局不同，不能将共享 storage 计作每个进程可独立回收的权重。

该 loader 在接触 daemon 前检查量化白名单：当前仅未量化和有 block-size 配置的 FP8 分支通过，不包括 per-tensor FP8 或任意其他量化。映射时校验已有参数/buffer 的 shape/dtype，残留 meta tensor 会报错，并避免重复量化 postprocess；这些检查不等同所有模型、并行组合和 HCU 平台的数值验收。

client 仅在 daemon 确实缺席时允许磁盘 fallback；连接拒绝、配置不匹配或传输失败都报错，daemon 模式也不允许缺席后另载一份权重。共享成功后，若 daemon 提供有效 PID，watchdog 在其死亡时终止 client，避免悬空权重继续生成；缺 PID 时仅告警并跳过监测，不能宣称该保护必然生效。恢复需重建可信映射和版本，不把进程仍存活或普通 weight-update RPC 当作 daemon 故障的原地回滚。

## 调度、partial rollout 与空泡

Scheduler组装prefill/decode batch，CPU接收、tokenization、模型执行和输出推进组成完整链。`pause_generation(in_place)`保留在途状态，retract路径让请求退回可恢复队列；partial rollout适合异步RL控制，但旧policy产生的tokens/logprob及恢复后的版本必须由consumer追踪。

优化时记录prompt/response长度分布、batch token、每副本waiting/running、prefill/decode占比、首token/末token尾延迟、取消/重算率和policy staleness。大量等待可能来自rollout副本不均、最长response、weight-sync barrier或CPU调度；以同shape kernel和单独生成基准分清实现落后与争用。不同并行域的所有重要rank都要有比较窗口。

## Radix prefix 和层次缓存

`RadixCache`按token前缀组织节点，`RadixKey`还带extra_key/cache_salt等隔离信息。节点`lock_ref`保护活跃使用，evict只针对可回收叶子并更新可用KV。缓存命中减少重复prefill计算，但缓存驻留会挤占新请求空间；显存不随请求结束立即归零可能是设计内的prefix保留。

长上下文和重复prompt可参考HiCache层次缓存：GPU/host/可选外部存储之间移动KV，收益依赖命中和传输时延；不能用冷cache与热cache混合测“kernel提升”。相同token前缀不保证跨权重版本可复用；release或refit后的flush、请求引用和session状态需联动。

传统dense-attention KV估算可用层数×真实KV-head数×head-dim×token容量×K/V×dtypebytes，并结合TP分片；MLA、滑窗、SSM/混合attention和量化KV需要各自布局/状态模型，不能统一乘总attention-head。缓存、图池与workspace不同owner独立计账。

## typed pool 描述与请求容量

当前 KV pool 为已迁移的 host/HiCache 消费者提供 `get_device_pool_infos`，声明持久 buffer、model layer IDs、KV layout、scale layout 和真实 dtype。MHA 的 K/V head dimension 可以不同；page-major 与 NHD 的描述转换、MXFP8 interleaved scale 及 hybrid 子池的 model-layer 映射都不能靠原 tensor rank 猜。未实现 provider 会明确拒绝，源码也要求消费者不能用异常或空描述来静默选择旧路径；这不是所有格式已经迁移的承诺。

容量判断也经实际 allocator 分派：prefill 使用 `create_prefill_budget` 和请求额外 reserve，decode 调用 `check_decode_capacity` 后再决定 retract。选择统一 FULL/SWA allocator 时，两侧竞争共享 byte envelope，独立的 full/SWA token 余量不能直接相加作为可用容量。空闲 KV slot、物理字节回收、请求 row 和 memory-saver tag 是不同层次；新 allocator 的剩余压缩、跨池搬移和所有格式组合仍需按实际采用路径继续审查。

Scheduler 的 admission 同时受 pipeline request budget、空闲 req-to-token rows、已持有 rows 和承诺给 beam members 的 rows 约束。持续 chunk 持有自己的 row，不能再次算成全新请求而阻塞回收；waiting 候选前还要检查本轮 prefill token budget 是否已耗尽。看似“还有 KV”并不表示有可接纳 request slot，也不能把重用 row 的请求算作新增容量。观察慢 batch 时同时保存 held/free rows、beam、chunk、PP 与 token budget，避免只放大 max-running-requests。

## 数值与恢复验证

固定sampling参数和prompt token后，对照sleep前后、两轮refit前后logits或logprob，再比较随机生成统计。temperature/top-p/stop/eos/logprob定义与训练teacher-forcing路径不同，不能只用greedy token相等来证明RL loss输入等价。

使用多实例release-memory测试核对进程不退出、显存实际下降、重新恢复后的生成与多实例互不污染；覆盖缓存、量化静态buffer和图模式。失败时记录哪个tag、哪个rank、物理/reserved/allocated的真实占用，不将allocator reserved当全部泄漏。

卡住按control request→TP barrier→memory adapter→device event→scheduler重新推进定位；OOM按在途请求、KV、weights/receiver副本、图池、host backup检查。回退保留无sleep、无层次cache或已验证模式，并限定相同policy版本重新建立KV。场景依赖HCU fork、DTK虚拟内存与图支持，官方CUDA/AMD平台测试不代表HCU全部支持。

## 固定证据与验证范围

- [docs/docs/advanced_features/sglang_for_rl.mdx](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/docs/docs/advanced_features/sglang_for_rl.mdx)
- [docs/docs/advanced_features/session_radix_cache.mdx](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/docs/docs/advanced_features/session_radix_cache.mdx)
- [docs/docs/advanced_features/hicache_design.mdx](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/docs/docs/advanced_features/hicache_design.mdx)
- [docs/docs/basic_usage/sampling_params.mdx](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/docs/docs/basic_usage/sampling_params.mdx)
- [python/sglang/srt/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/managers/scheduler.py)
- [python/sglang/srt/managers/scheduler_components/weight_updater.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/managers/scheduler_components/weight_updater.py)
- [python/sglang/srt/utils/torch_memory_saver_adapter.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/utils/torch_memory_saver_adapter.py)
- [python/sglang/srt/mem_cache/radix_cache.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/mem_cache/radix_cache.py)
- [python/sglang/srt/mem_cache/memory_pool.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/mem_cache/memory_pool.py)
- [test/registered/rl/test_multi_instance_release_memory_occupation.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/test/registered/rl/test_multi_instance_release_memory_occupation.py)

- [python/sglang/srt/model_executor/model_runner_components/load_model_utils.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/model_executor/model_runner_components/load_model_utils.py)
- [python/sglang/srt/weight_cache/ipc_loader.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/weight_cache/ipc_loader.py)
- [python/sglang/srt/weight_cache/protocol.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/weight_cache/protocol.py)
- [test/registered/unit/model_loader/test_weight_cache_protocol.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/test/registered/unit/model_loader/test_weight_cache_protocol.py)
- [python/sglang/srt/mem_cache/allocator/base.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/mem_cache/allocator/base.py)
- [python/sglang/srt/managers/schedule_policy.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/managers/schedule_policy.py)
- [python/sglang/srt/managers/schedule_batch.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/managers/schedule_batch.py)
- [python/sglang/srt/mem_cache/allocator/unified_hybrid_swa.py](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/python/sglang/srt/mem_cache/allocator/unified_hybrid_swa.py)

本页在 2026-10-20 阅读上述固定源码和教程；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。
