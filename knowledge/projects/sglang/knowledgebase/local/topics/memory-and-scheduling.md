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
reviewed_on: '2026-10-12'
coverage: reviewed implementation chains and official guides; not all models, backends
  or HCU runtime qualification
sources:
- source: sgl-project-sglang
  path: docs/docs/advanced_features/sglang_for_rl.mdx
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 751d2c54c7cc87780a7e9005a76930f73a562c6cf4d9db1574bef4eafaeecd76
- source: sgl-project-sglang
  path: docs/docs/advanced_features/session_radix_cache.mdx
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 0b50a3e5b8b5e97d3ce035801d18183ce1fa06dba9f6644f9c0f75bc0bf748cd
- source: sgl-project-sglang
  path: docs/docs/advanced_features/hicache_design.mdx
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: ea9e7896aeeba4f648c3484b382780ce735bba74e0a74dd5403bf7a0438305b5
- source: sgl-project-sglang
  path: docs/docs/basic_usage/sampling_params.mdx
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: e3bd51e0d6d8ddcdf805fa275a40dac150cdd16f5fd7fdbb425f9330eb52e84e
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 8ebda29ff526cf61826ff8b2a6c907ad4d9cce3d580401a300b00308bbeedc67
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler_components/weight_updater.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 7e2f08d8c1ca67965261208f51bab17d0ab0bfd5b87a009d9dbd97fc381542e4
- source: sgl-project-sglang
  path: python/sglang/srt/utils/torch_memory_saver_adapter.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 139937ef272be19ddc48e0c5024d7860fa74f7321b4479694c234408b4c60f12
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/radix_cache.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: ec21c72ccc38cd053ffbccf88d50a66342ede1764fb4b8dd338919d5e3c0922b
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/memory_pool.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 049dc7f6f1f4c4fef32f0721b54808246e5f5842c1914849125d2f92cb4a20f7
- source: sgl-project-sglang
  path: test/registered/rl/test_multi_instance_release_memory_occupation.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 3f746be087e1ee08cdb7287ed12cb3e3016dec9551f321c382bc2a4de4aabbc8
---

# SGLang 显存与 rollout 调度：睡眠、KV、prefix 与数值边界

## 共卡训练的资源问题

生成服务峰值由权重、KV、图池、attention/MoE workspace和接收buffer组成。训练optimizer、激活和通信同卡驻留时，两个各自能跑的组件合起来可能OOM。先识别当前consumer是共卡轮换、独立训推设备还是异步重叠；不同布局分别决定release、refit和调度，不能采用同一个内存比例。

## release/resume 的真实调用链

Engine/API控制请求→Scheduler→`SchedulerWeightUpdaterManager.release_memory_occupation`→`TorchMemorySaverAdapter.pause(tag)`；恢复走adapter.resume并恢复模型静态buffer。release要求`is_fully_idle`，paused时可以按实现忽略waiting，但仍需保证实际在途执行结束。它不是强制杀掉GPU任务的接口。

源码当前处理`kv_cache`、`weights`和`cuda_graph`等memory tags；教程表格主要列weights/KV，选用tag仍以实际fork和`io_struct`约束为准。权重release会导出模型named_buffers静态状态，resume后恢复，TP CPU组barrier与device synchronization参与交接；这解释了“仅参数回来了”仍可能缺scale/RoPE等状态。

`TorchMemorySaverAdapter.create(enable=True)`在所需package缺失时抛导入错误；未启用时选择Noop adapter，pause/resume不会节省显存。必须看实际adapter与前后占用，不能看到API返回就写内存验收通过。当前weight-cache共享模式会显式禁止释放/恢复weights，避免IPC peers引用已释放storage；这种场景应选择兼容部署，不绕过断言。

## 调度、partial rollout 与空泡

Scheduler组装prefill/decode batch，CPU接收、tokenization、模型执行和输出推进组成完整链。`pause_generation(in_place)`保留在途状态，retract路径让请求退回可恢复队列；partial rollout适合异步RL控制，但旧policy产生的tokens/logprob及恢复后的版本必须由consumer追踪。

优化时记录prompt/response长度分布、batch token、每副本waiting/running、prefill/decode占比、首token/末token尾延迟、取消/重算率和policy staleness。大量等待可能来自rollout副本不均、最长response、weight-sync barrier或CPU调度；以同shape kernel和单独生成基准分清实现落后与争用。不同并行域的所有重要rank都要有比较窗口。

## Radix prefix 和层次缓存

`RadixCache`按token前缀组织节点，`RadixKey`还带extra_key/cache_salt等隔离信息。节点`lock_ref`保护活跃使用，evict只针对可回收叶子并更新可用KV。缓存命中减少重复prefill计算，但缓存驻留会挤占新请求空间；显存不随请求结束立即归零可能是设计内的prefix保留。

长上下文和重复prompt可参考HiCache层次缓存：GPU/host/可选外部存储之间移动KV，收益依赖命中和传输时延；不能用冷cache与热cache混合测“kernel提升”。相同token前缀不保证跨权重版本可复用；release或refit后的flush、请求引用和session状态需联动。

传统dense-attention KV估算可用层数×真实KV-head数×head-dim×token容量×K/V×dtypebytes，并结合TP分片；MLA、滑窗、SSM/混合attention和量化KV需要各自布局/状态模型，不能统一乘总attention-head。缓存、图池与workspace不同owner独立计账。

## 数值与恢复验证

固定sampling参数和prompt token后，对照sleep前后、两轮refit前后logits或logprob，再比较随机生成统计。temperature/top-p/stop/eos/logprob定义与训练teacher-forcing路径不同，不能只用greedy token相等来证明RL loss输入等价。

使用多实例release-memory测试核对进程不退出、显存实际下降、重新恢复后的生成与多实例互不污染；覆盖缓存、量化静态buffer和图模式。失败时记录哪个tag、哪个rank、物理/reserved/allocated的真实占用，不将allocator reserved当全部泄漏。

卡住按control request→TP barrier→memory adapter→device event→scheduler重新推进定位；OOM按在途请求、KV、weights/receiver副本、图池、host backup检查。回退保留无sleep、无层次cache或已验证模式，并限定相同policy版本重新建立KV。场景依赖HCU fork、DTK虚拟内存与图支持，官方CUDA/AMD平台测试不代表HCU全部支持。

## 固定证据与验证范围

- [docs/docs/advanced_features/sglang_for_rl.mdx](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/docs/docs/advanced_features/sglang_for_rl.mdx)
- [docs/docs/advanced_features/session_radix_cache.mdx](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/docs/docs/advanced_features/session_radix_cache.mdx)
- [docs/docs/advanced_features/hicache_design.mdx](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/docs/docs/advanced_features/hicache_design.mdx)
- [docs/docs/basic_usage/sampling_params.mdx](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/docs/docs/basic_usage/sampling_params.mdx)
- [python/sglang/srt/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/sglang/srt/managers/scheduler.py)
- [python/sglang/srt/managers/scheduler_components/weight_updater.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/sglang/srt/managers/scheduler_components/weight_updater.py)
- [python/sglang/srt/utils/torch_memory_saver_adapter.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/sglang/srt/utils/torch_memory_saver_adapter.py)
- [python/sglang/srt/mem_cache/radix_cache.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/sglang/srt/mem_cache/radix_cache.py)
- [python/sglang/srt/mem_cache/memory_pool.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/sglang/srt/mem_cache/memory_pool.py)
- [test/registered/rl/test_multi_instance_release_memory_occupation.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/test/registered/rl/test_multi_instance_release_memory_occupation.py)

本页在 2026-10-12 阅读上述固定源码和教程；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。
