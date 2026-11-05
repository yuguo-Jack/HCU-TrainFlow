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
reviewed_on: '2026-11-04'
coverage: reviewed implementation chains and official guides; not all models, backends or HCU runtime qualification
sources:
- source: sgl-project-sglang
  path: docs/docs/advanced_features/sglang_for_rl.mdx
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 68ed10e2b44ce57413380df288feb3dc0b1f8a6b650589cf6ba97a340566b20f
- source: sgl-project-sglang
  path: docs/docs/advanced_features/session_radix_cache.mdx
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 0b50a3e5b8b5e97d3ce035801d18183ce1fa06dba9f6644f9c0f75bc0bf748cd
- source: sgl-project-sglang
  path: docs/docs/advanced_features/hicache_design.mdx
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: ae39e8f6086a763f32d34debbf879db58cbae6397514121bbaecf200bae51e8b
- source: sgl-project-sglang
  path: docs/docs/basic_usage/sampling_params.mdx
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: e3bd51e0d6d8ddcdf805fa275a40dac150cdd16f5fd7fdbb425f9330eb52e84e
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: d6158d7d4271ef93991e69965f101a183b63f33baa041468cf83355a24d474f0
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler_components/weight_updater.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 2e65bb16c08c45f126666e2109d8fdf3139e37fccc9b889a6e4f4692bd8b1032
- source: sgl-project-sglang
  path: python/sglang/srt/utils/torch_memory_saver_adapter.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 139937ef272be19ddc48e0c5024d7860fa74f7321b4479694c234408b4c60f12
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/radix_cache.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 7ab514985b18b9a799f5f02190820168080b47bb81d2dd1754448bc8e6c824c5
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/memory_pool.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: ea1e9bc0c261fe0b129a33c22d5a2ce9b872762b38647fb3d43bb2c7992e76ef
- source: sgl-project-sglang
  path: test/registered/rl/test_multi_instance_release_memory_occupation.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: af97eca5bb9d28fc5cbe5312054c6f6f90fd3928317e8c06b3bb594849cb4a9d
- source: sgl-project-sglang
  path: python/sglang/srt/model_executor/model_runner_components/load_model_utils.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: b0692d6490bf0cde214a99173320cfc03748a8f53795dc36fce7fe2f053fc238
- source: sgl-project-sglang
  path: python/sglang/srt/weight_cache/ipc_loader.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 36b3e6d1cd3fe4a8ac8f2bc0fe7d796947136a7aee59ad801ca3fcdc3abcc237
- source: sgl-project-sglang
  path: python/sglang/srt/weight_cache/protocol.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: d42733448d27904f0fdfedb37fc190f3739fd77decec22b396738bc516bf38fb
- source: sgl-project-sglang
  path: test/registered/unit/model_loader/test_weight_cache_protocol.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 0c9278784590e6929a01877d1f621d644f5458901a3bcea98162c8c5247a12df
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/allocator/base.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 12047207f6112562861e6fa086377714a349e2818817ac9e61c0321aea388ee4
- source: sgl-project-sglang
  path: python/sglang/srt/managers/schedule_policy.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 9918505c8ba291f781a516a9bdc62cc836570fcdfca8e41066591296c97e043e
- source: sgl-project-sglang
  path: python/sglang/srt/managers/schedule_batch.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 38fab79d64ca54870ab2308b525187beeecb74c405ef38359b8f2928123597cd
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/kv/state_storage.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: c44140a10cd83422753090d5c1b45628d2a8de5d92fccc2d657de5ae2124b255
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/kv/router.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 4ae69633da6f617a676c0d25c53a3d7ead01d77cf697e40ee4379f377ca883b5
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/kv/alloc/id_space.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: b1448cb7588ef5c6fdd28dd422808411d5259b00c6efe984dd95b7920fa455a9
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/kv/memory/views.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 36d759c15e5046be3e19d5ca1a44db49d2201e2dc753bec7ad8ab46383f53b4e
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/hicache_storage.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 8122dcd8c12c9416f7b4329215df735f0d87809fe6065093c213df3df4744f34
- source: sgl-project-sglang
  path: test/registered/unit/mem_cache/test_kv_layer_router.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 48fc3130fbecf6e32f9a442046c8680c7177be8d2d9b1fd14b65d0e7ef312f75
- source: sgl-project-sglang
  path: test/registered/unit/mem_cache/test_kv_layer_router_parts.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 78f882d079b06c35582252dd44f86d6aa3b5d696b1097a77b5b8b049ba2a74ac
---

# SGLang 显存与 rollout 调度：睡眠、KV、prefix 与数值边界

## 共卡训练的资源问题

生成服务峰值由权重、KV、图池、attention/MoE workspace和接收buffer组成。训练optimizer、激活和通信同卡驻留时，两个各自能跑的组件合起来可能OOM。先识别当前consumer是共卡轮换、独立训推设备还是异步重叠；不同布局分别决定release、refit和调度，不能采用同一个内存比例。

## release/resume 的真实调用链

Engine/API控制请求→Scheduler→`SchedulerWeightUpdaterManager.release_memory_occupation`→`TorchMemorySaverAdapter.pause(tag)`；恢复走adapter.resume并恢复模型静态buffer。release 要求 `is_fully_idle`；paused 时可按实现忽略普通 waiting，但持有 KV 的等待请求仍会阻止 idle。还要排空 running/last batch、overlap result queue、PP microbatch、PD receiver、decode offload 以及 HiCache loadback/prefetch/write-back 等实际工作。health-check 的空闲判据与这里不同；健康探针成功或 pause 标志不能证明可释放内存。

源码当前处理`kv_cache`、`weights`和`cuda_graph`等memory tags；教程表格主要列weights/KV，选用tag仍以实际fork和`io_struct`约束为准。manager 当前显式备份/恢复的是 target runner 的 named_buffers，并非所有 target/draft 状态的统一快照。TP CPU组barrier与device synchronization参与交接；“仅参数回来了”仍可能缺scale/RoPE或其他角色的状态。

`TorchMemorySaverAdapter.create(enable=True)`在所需package缺失时抛导入错误；未启用时选择Noop adapter，pause/resume不会节省显存。必须看实际adapter与前后占用，不能看到API返回就写内存验收通过。当前weight-cache共享模式会显式禁止释放/恢复weights，避免IPC peers引用已释放storage；这种场景应选择兼容部署，不绕过断言。

tag 操作不是原子事务：release 先记录 offload tags，可能已暂停/flush KV 后才遇到 weights 门禁；resume 先移除记录并恢复 graph，再检查 weights。因此失败不能解释为“所有 tag 都没动过”。保存每个 tag 的实际完成点，再由既有恢复 owner 处理，不能盲目重放默认全量 tags。在线 refit 还可能因派生权重缓存被拒绝，参见 [加载门禁](weight-update.md#在线更新的门禁与派生权重)；单独 flush 旧 KV 不解除该限制。

## 共享权重与sleep的边界

当 `weight_cache_mode` 非 off 时，加载配置切到 `IPC_CACHE`；成功路径把 daemon 已处理的权重映射给 client，并在模型上保留 tensor 和 transport 引用。加载 helper 在这种模式下关闭 weights CPU backup。它与复制一份参数后各自训练/睡眠的布局不同，不能将共享 storage 计作每个进程可独立回收的权重。

该 loader 在接触 daemon 前检查量化白名单：当前仅未量化和有 block-size 配置的 FP8 分支通过，不包括 per-tensor FP8 或任意其他量化。映射时校验已有参数/buffer 的 shape/dtype，残留 meta tensor 会报错，并避免重复量化 postprocess；这些检查不等同所有模型、并行组合和 HCU 平台的数值验收。

client 仅在 daemon 确实缺席时允许磁盘 fallback；连接拒绝、配置不匹配或传输失败都报错，daemon 模式也不允许缺席后另载一份权重。共享成功后，若 daemon 提供有效 PID，watchdog 在其死亡时终止 client，避免悬空权重继续生成；缺 PID 时仅告警并跳过监测，不能宣称该保护必然生效。恢复需重建可信映射和版本，不把进程仍存活或普通 weight-update RPC 当作 daemon 故障的原地回滚。

## 调度、partial rollout 与空泡

Scheduler 组装 prefill/decode batch，CPU 接收、tokenization、模型执行和输出推进组成完整链。当前请求显式登记已启动和已处理的 inflight step；只观察 waiting/running 数量不足以覆盖 overlap。`pause_generation(in_place)` 保留在途状态；retract 路线先处理 overlap、offload 和 PD decode 握手，再将可重启请求交给 continue 的重新 bootstrap。

PD prefill 的未完成 mid-chunk 请求当前仍因 KV sender 生命周期被保留，源码明确留下跨更新旧 prefix 的 TODO。因此 partial rollout 的 tokens/logprob、prompt KV spans 和更新后版本要由 consumer 关联；不能把 retract 当成所有模式都完成了旧 KV 清理。

优化时记录prompt/response长度分布、batch token、每副本waiting/running、prefill/decode占比、首token/末token尾延迟、取消/重算率和policy staleness。大量等待可能来自rollout副本不均、最长response、weight-sync barrier或CPU调度；以同shape kernel和单独生成基准分清实现落后与争用。不同并行域的所有重要rank都要有比较窗口。

## Radix prefix 和层次缓存

`RadixCache`按token前缀组织节点，`RadixKey`还带extra_key/cache_salt等隔离信息。节点`lock_ref`保护活跃使用，evict只针对可回收叶子并更新可用KV。缓存命中减少重复prefill计算，但缓存驻留会挤占新请求空间；显存不随请求结束立即归零可能是设计内的prefix保留。

长上下文和重复prompt可参考HiCache层次缓存：GPU/host/可选外部存储之间移动KV，收益依赖命中和传输时延；不能用冷cache与热cache混合测“kernel提升”。相同token前缀不保证跨权重版本可复用；release或refit后的flush、请求引用和session状态需联动。

传统dense-attention KV估算可用层数×真实KV-head数×head-dim×token容量×K/V×dtypebytes，并结合TP分片；MLA、滑窗、SSM/混合attention和量化KV需要各自布局/状态模型，不能统一乘总attention-head。缓存、图池与workspace不同owner独立计账。

HiCache 的外部 L3 router 现在可从 `/get_hicache_l3_cache_layout` 和 startup/server info 获取实际存储 suffix、pool 和 hit policy。`merge_l3_layouts` 要求同 PP stage 的副本一致，收齐全部 PP stage 后合并且 `pp_rank=null`；缺 stage、缺元数据或回复不一致会返回 `enabled=false` 和原因。外部 router 必须拒绝将显式 disabled 当成可推断布局；只有字段整体缺席才表示旧 engine 可走其兼容协议。当前文档限定可导出布局的模型/池组合，不能根据全模型同一 token hash 推定 MHA、分片 auxiliary 或任意量化格式可复用。

存储插件注册按 anchor pool→所有初始 v2 host pools→一次 `on_host_pools_registered()` 完成；后续动态 sidecar 只走 v2，不能重复完成初始化。该 hook 抛错应让 attach 失败。各辅助池有自己的 all-pages、trailing-pages 或 block-groups 命中语义，不能仅按主 KV 的最大 hit 决定恢复前缀。

## typed pool 描述与请求容量

当前 KV pool 为已迁移的 host/HiCache 消费者提供 `get_device_pool_infos`，声明持久 buffer、model layer IDs、KV layout、scale layout 和真实 dtype。MHA 的 K/V head dimension 可以不同；page-major 与 NHD 的描述转换、MXFP8 interleaved scale 及 hybrid 子池的 model-layer 映射都不能靠原 tensor rank 猜。未实现 provider 会明确拒绝；但只承载 recurrent state、而 token KV 已路由到子池的 wrapper 可以合法返回空描述。消费者应沿 router/声明选择池，不能把空 tuple 一概解释成失败后静默退回旧布局；这不是所有格式已经迁移的承诺。

容量判断经 allocator 的 `create_prefill_budget` / `check_decode_capacity` 和 `memory_budget` 的 state-slot 成本分派；窗口能力通过 `has_window_pool` 表达，不能继续按旧 pool 类名分支。原 `allocator/unified_hybrid_swa.py` 已不在当前固定树，本页不沿用该旧文件为当前共享 byte envelope 实现背书。空闲 KV slot、物理字节、state slot、request row 和 memory-saver tag 是不同资源，独立计数不能直接相加。

请求表当前只保存 ID，recurrent/Mamba、short-conv 和 n-gram 状态由 `StateStorage` 管理。acquire 保留已有 slots，后续分配不足时仅回收本轮新分配的 state/tracking slots；不能顺手释放调用前持有的状态。release 只在有效 ping-pong 选择下保留缓存，clear 还要清 checkpoint slot pool，不能只清 radix 树。

`KVLayerRouter` 把模型 layer ID 映射到 typed view 和本地 `view_layer_id`；token KV、state 与 n-gram part 分开，state 的 loadback wait 只有 host 栈启用分层恢复后才发生。out-of-loop 拷贝等待该 part 的最后本地层，无该 part 的 PP stage 不应等待不存在的层。`IdSpace` 将逻辑 slot 与可搬移的物理 row 分开，DCP 写入还含 owner 与 sink-row 规则；自定义 kernel 不能绕过 write/read 转换或用 raw request ID 当物理地址。

Scheduler 的 admission 同时受 pipeline request budget、空闲 req-to-token rows、已持有 rows 和承诺给 beam members 的 rows 约束。持续 chunk 持有自己的 row，不能再次算成全新请求而阻塞回收；waiting 候选前还要检查本轮 prefill token budget 是否已耗尽。看似“还有 KV”并不表示有可接纳 request slot，也不能把重用 row 的请求算作新增容量。观察慢 batch 时同时保存 held/free rows、beam、chunk、PP 与 token budget，避免只放大 max-running-requests。

本轮 admission 还需预留 host loadback 的 gather scratch 后才能排队 H2D；prefix 改变后要重新核对 reserve，避免发起无可消费 workspace 的 loadback。DCP 的逻辑 page padding、recurrent state 的 chunk 对齐与计算 token 预算分别计数；最终 chunk 和中间 chunk 的对齐要求也不同。`calc_priority` 返回新的排序列表，调用者须使用返回值，不能假定 waiting queue 被原地排序。

普通 MHA 的 K/V 合并分配快路显式排除 HIP 和 torch.compile；typed-view 迁移并不等于 HIP 也使用该 fused storage。对应 layer-router 单测检查复合池的指针/模型层映射、MLA 写入不改全局 layer ID、window 能力；part-router 测试检查分层等待和无 state 层的 stage。这些是已阅读的上游测试合同，未在本机执行。

## 数值与恢复验证

固定sampling参数和prompt token后，对照sleep前后、两轮refit前后logits或logprob，再比较随机生成统计。temperature/top-p/stop/eos/logprob定义与训练teacher-forcing路径不同，不能只用greedy token相等来证明RL loss输入等价。

多实例 release-memory 测试在当前源码中仍将 AMD CI 显式禁用，并注明 torch_memory_saver 的 ROCm 不兼容；不能将 suite 注册或教程视为 HCU sleep 已通过。现场具备所选 adapter 时，核对进程不退出、显存实际下降、重新恢复后的生成与多实例互不污染；覆盖缓存、量化静态buffer和图模式。失败时记录哪个tag、哪个rank、物理/reserved/allocated的真实占用，不将allocator reserved当全部泄漏。

卡住按control request→TP barrier→memory adapter→device event→scheduler重新推进定位；OOM按在途请求、KV、weights/receiver副本、图池、host backup检查。回退保留无sleep、无层次cache或已验证模式，并限定相同policy版本重新建立KV。场景依赖HCU fork、DTK虚拟内存与图支持，官方CUDA/AMD平台测试不代表HCU全部支持。

## 固定证据与验证范围

- [docs/docs/advanced_features/sglang_for_rl.mdx](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/docs/docs/advanced_features/sglang_for_rl.mdx)
- [docs/docs/advanced_features/session_radix_cache.mdx](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/docs/docs/advanced_features/session_radix_cache.mdx)
- [docs/docs/advanced_features/hicache_design.mdx](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/docs/docs/advanced_features/hicache_design.mdx)
- [docs/docs/basic_usage/sampling_params.mdx](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/docs/docs/basic_usage/sampling_params.mdx)
- [python/sglang/srt/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/managers/scheduler.py)
- [python/sglang/srt/managers/scheduler_components/weight_updater.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/managers/scheduler_components/weight_updater.py)
- [python/sglang/srt/utils/torch_memory_saver_adapter.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/utils/torch_memory_saver_adapter.py)
- [python/sglang/srt/mem_cache/radix_cache.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/mem_cache/radix_cache.py)
- [python/sglang/srt/mem_cache/memory_pool.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/mem_cache/memory_pool.py)
- [test/registered/rl/test_multi_instance_release_memory_occupation.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/test/registered/rl/test_multi_instance_release_memory_occupation.py)

- [python/sglang/srt/model_executor/model_runner_components/load_model_utils.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/model_executor/model_runner_components/load_model_utils.py)
- [python/sglang/srt/weight_cache/ipc_loader.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/weight_cache/ipc_loader.py)
- [python/sglang/srt/weight_cache/protocol.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/weight_cache/protocol.py)
- [test/registered/unit/model_loader/test_weight_cache_protocol.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/test/registered/unit/model_loader/test_weight_cache_protocol.py)
- [python/sglang/srt/mem_cache/allocator/base.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/mem_cache/allocator/base.py)
- [python/sglang/srt/managers/schedule_policy.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/managers/schedule_policy.py)
- [python/sglang/srt/managers/schedule_batch.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/managers/schedule_batch.py)

- [python/sglang/srt/mem_cache/kv/state_storage.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/mem_cache/kv/state_storage.py)
- [python/sglang/srt/mem_cache/kv/router.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/mem_cache/kv/router.py)
- [python/sglang/srt/mem_cache/kv/alloc/id_space.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/mem_cache/kv/alloc/id_space.py)
- [python/sglang/srt/mem_cache/kv/memory/views.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/mem_cache/kv/memory/views.py)
- [python/sglang/srt/mem_cache/hicache_storage.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/mem_cache/hicache_storage.py)
- [test/registered/unit/mem_cache/test_kv_layer_router.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/test/registered/unit/mem_cache/test_kv_layer_router.py)
- [test/registered/unit/mem_cache/test_kv_layer_router_parts.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/test/registered/unit/mem_cache/test_kv_layer_router_parts.py)


本页在 2026-11-04 复核上述固定源码、教程与两项 router 测试合同；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。
