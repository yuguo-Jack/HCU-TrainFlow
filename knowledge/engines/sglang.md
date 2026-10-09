---
id: engines/sglang
title: SGLang：训练配套的生成、权重更新与显存回收
engine: sglang
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
coverage: selected implementation chain, not all models or backends
sources:
- source: sgl-project-sglang
  path: python/sglang/srt/weight_sync/tensor_bucket.py
  commit: bd2d73daa5afda6bcad8d479a834f2e70bbe9569
  sha256: fc50064ea51c338262394ff0b7a849100e7c46761099e27a4478e9db0ea08cc2
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler.py
  commit: bd2d73daa5afda6bcad8d479a834f2e70bbe9569
  sha256: c53aa309f68083f6bac08350453fcb9615667268d05fb6af0c74a534bbd6c4f6
- source: sgl-project-sglang
  path: test/registered/rl/test_update_weights_from_distributed.py
  commit: bd2d73daa5afda6bcad8d479a834f2e70bbe9569
  sha256: 0c06da440fd0de2b7250cd17ff6f47506eb22e4341d651fb8d49fdd9d1a2643e
- source: sgl-project-sglang
  path: test/registered/rl/test_multi_instance_release_memory_occupation.py
  commit: bd2d73daa5afda6bcad8d479a834f2e70bbe9569
  sha256: 3f746be087e1ee08cdb7287ed12cb3e3016dec9551f321c382bc2a4de4aabbc8
- source: sgl-project-sglang
  path: python/sglang/srt/server_args.py
  commit: bd2d73daa5afda6bcad8d479a834f2e70bbe9569
  sha256: 06e1912f52dcfbc360b532a4e3d71cc4388cffd59ee9bc6fe58c7d5251f72ae3
---

# SGLang：训练配套的生成、权重更新与显存回收

## 使用范围与目录

这里关注 RL 训练依赖的生成服务，完整推理调优另按任务展开。`python/sglang/srt/managers/scheduler.py` 管调度，`server_args.py` 管参数，`weight_sync` 组织权重传输，`test/registered/rl` 提供训练集成测试。文档目录当前是 `docs/docs/.../*.mdx`；更新不能仍按旧 rst 路径扫描而漏掉新教程。

## 权重 bucket 的具体实现

`FlattenedTensorBucket` 把多个 tensor 展平后按 uint8 组织，并保存每个 tensor 的 name、shape、dtype、start/end 和 numel；重建时按元数据切片、view(dtype)、reshape。这里传输索引基于字节视图，不能拿原 dtype 元素数替换 byte offset。原始参数不可遗漏、重复或错误重排。

重建 tensor 可能共享 flat buffer 的存储；异步传输完成、目标权重消费完毕之前不能释放或复用 buffer。优化聚合粒度同时考虑临时显存、消息数、dtype 对齐与拷贝；不要用一个均匀 dtype 小例子的成功覆盖真实混合 dtype 模型。

## 运行与回归

从 `sglang_for_rl` 及实际 RL 工程的 SGLang 适配器核对启动选项、服务端版本和权重更新协议。HCU 需要支持的后端及工程脚本；官方 NVIDIA server_args 不是平台独立推荐值。运行验收包含首轮生成、权重更新后生成、并发请求排空、内存释放/恢复，以及多实例共享设备。

`test_update_weights_from_distributed.py` 和 `test_multi_instance_release_memory_occupation.py` 提供具体回归入口，实际执行仍需对应集群和后端。记录测试覆盖的 TP、quantization、LoRA 和设备数；传输成功后还需检查 logits 或固定输入的生成一致性。

## 性能与内存问题

把 prefill、decode、排队、权重同步、KV 分配、sleep/resume 分开。同步时固定模型与 policy version，比较单独服务和训练并发时的吞吐、延迟及峰值；通信/计算争用、临时接收 buffer 和 allocator 状态都可能使模型中表现差于单测。

PR #39265 讨论从 metadata 直接分配 packed 接收 buffer，可作为减少临时内存与组装开销的进一步源码入口。是否适用于所用训练引擎要继续追发送侧、接收侧与测试；不能只抄 receiver 一端。

## 诊断顺序

服务没有响应时先分清调度队列、GPU 执行、健康检查与权重更新互斥；loss/logprob 异常时核对权重版本、量化 scale、tied parameters、sampling 和 mask。内存未下降不一定是泄漏，应区分 allocated/reserved、KV 与权重驻留、异步流和多个服务实例。将故障窗口保存在私有经验库，并链接到训练端的同次迭代。

## 固定源码与符号导航

| 文件 | 本轮源码中可追查的入口（非全部符号） |
| --- | --- |
| [python/sglang/srt/weight_sync/tensor_bucket.py](https://github.com/sgl-project/sglang/blob/bd2d73daa5afda6bcad8d479a834f2e70bbe9569/python/sglang/srt/weight_sync/tensor_bucket.py) | `FlattenedTensorMetadata`, `FlattenedTensorBucket`, `get_flattened_tensor`, `get_metadata`, `reconstruct_tensors` |
| [python/sglang/srt/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/bd2d73daa5afda6bcad8d479a834f2e70bbe9569/python/sglang/srt/managers/scheduler.py) | `Scheduler`, `dispatch_event_loop`, `resolve_spawn_dp_rank`, `configure_scheduler_process`, `run_scheduler_process`, `SchedulerMlxOverlapMixin`, `init_startup_timing_begin`, `init_startup_timing_summary` |
| [test/registered/rl/test_update_weights_from_distributed.py](https://github.com/sgl-project/sglang/blob/bd2d73daa5afda6bcad8d479a834f2e70bbe9569/test/registered/rl/test_update_weights_from_distributed.py) | `verify_params_close`, `verify_params_not_close`, `init_process`, `init_process_hf`, `init_process_sgl`, `assert_tied_weights`, `test_update_weights_from_distributed`, `TestUpdateWeightsFromDistributed` |
| [test/registered/rl/test_multi_instance_release_memory_occupation.py](https://github.com/sgl-project/sglang/blob/bd2d73daa5afda6bcad8d479a834f2e70bbe9569/test/registered/rl/test_multi_instance_release_memory_occupation.py) | `EngineWrapper`, `get_gpu_memory_mb`, `assert_memory_decreased`, `assert_memory_increased`, `TestMultiInstanceReleaseMemoryOccupation`, `update_weights_from_tensor`, `release_memory_occupation`, `resume_memory_occupation` |
| [python/sglang/srt/server_args.py](https://github.com/sgl-project/sglang/blob/bd2d73daa5afda6bcad8d479a834f2e70bbe9569/python/sglang/srt/server_args.py) | `ServerArgs`, `resolve_encoder_transfer_backend`, `compute_world_size`, `m3_fp8_attn_gemm_enabled`, `set_global_server_args_for_scheduler`, `set_global_server_args_for_tokenizer`, `get_global_server_args`, `prepare_server_args` |

## 教程、PR 与继续搜索

- [全仓目录和固定文件入口](../source-maps/sgl-project-sglang.md)：没有本地专题时按模块继续读源码。
- [上游教程原文目录](../upstream-docs/sgl-project-sglang/)：保留来源内容，链接相对位置以原站为准。
- [PR #39265：[sglang-miles] Allocate packed weight receive buffers directly from metadata](../prs/sgl-project--sglang/PR-39265.md)：正文、review、diff 与 head/base 源码。

检索示例：`wiki-search "关键符号或问题" --engine sglang`。本地结果不足，使用 `wiki-search-pr "简短英文问题词" --engine sglang`，再 `wiki-pr OWNER/REPO NUMBER`、`wiki-code OWNER/REPO FULL_SHA PATH` 追实际调用者、被调底层库和测试。普通查阅只写私有缓存。

## 更新和验收边界

运行 `wiki-update PROJECT sgl-project-sglang` 检查完整目录、新文档、PR 讨论与已监测源码；分页或网络失败必须续采。变更后联动本页、同仓专题/案例、调用方与依赖；源码已 merge、软件已发布、HCU 已适配和当前任务已验证分别登记。本页为选定实现的代码阅读和操作建议，没有在 HCU 执行上述测试，也未覆盖所有模型。实际任务的版本、性能、显存、失败尝试和阶段 loss 记录进入私有经验 Wiki。
