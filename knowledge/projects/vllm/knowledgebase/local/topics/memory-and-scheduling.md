---
id: engines/vllm/memory-and-scheduling
title: vLLM sleep、KV 与调度：训练共卡的内存和数值交接
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
  path: docs/features/sleep_mode.md
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 7f8d19a6a7eeea565a9339bae555b6deb36c5f02087342087b4b1de85dfb0342
- source: vllm-project-vllm
  path: docs/design/hybrid_kv_cache_manager.md
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: f42303bb084b577e899f4165e1bf8f48cb2f464f2ece52f07d362d664b983d2b
- source: vllm-project-vllm
  path: vllm/device_allocator/sleep_mode_backend.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 4c90c6aa44b50dc5bbdd6b09d1e6a91d56d3481a109a8d7f8cc351927401196b
- source: vllm-project-vllm
  path: vllm/v1/worker/gpu_worker.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: a60f9d8c4935eb8e8949ea706a5922aae5df711c32599236319e6b145ad404da
- source: vllm-project-vllm
  path: vllm/v1/core/kv_cache_manager.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 62c24c6c5143c7b1dcd7831180dcd1e0285d258e7ddf4d6c67e071f0a9077d05
- source: vllm-project-vllm
  path: vllm/v1/core/sched/scheduler.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 6fa70af3d7c7eeddea72a794a79e96d1de4ae0e1d982b64b0891071dfdc79dee
- source: vllm-project-vllm
  path: vllm/config/scheduler.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 69aaaef2a78e889b5e1e0e0dd8180455f8c6d368f6663c43d634417b816fea28
- source: vllm-project-vllm
  path: tests/v1/worker/test_sleep_mode_backend.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 65eefb257fd2412f202934fb836f809c1af628f5e8e1622bf005ad78234e8540
- source: vllm-project-vllm
  path: tests/model_executor/test_sleep_mode_tensor_ownership.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: ce09e53cd474b9da712bb3ae602998a140dfbf8938bfef7de2252ff6ffaab509
- source: vllm-project-vllm
  path: examples/rl/rlhf_async_new_apis.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: b422474b8ae8d7d6b5e7fb52fb5e7ba50bbd48c79be76f1b856502cfe0fe1fae
- source: vllm-project-vllm
  path: vllm/v1/executor/cuda_checkpoint_executor.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: f409c6914fe1385e5a832f69a111cd72048ee6a3e195743506b932294e43fc43
- source: vllm-project-vllm
  path: tests/v1/executor/test_cuda_checkpoint_executor.py
  commit: 25e7c5728d834335288d080e1c36810fa111d4da
  sha256: 84a5e9a1204e182d3943e5890ac55699d5ac71aed0dac7c5e8f6e6b79800eb89
---

# vLLM sleep、KV 与调度：训练共卡的内存和数值交接

## 资源所有权与端到端目标

共卡RL应同时核对训练参数/optimizer/激活、推理weights/KV、图池、communicator、workspace和权重更新副本。最终目标是RL迭代吞吐及可接受policy staleness，不是单看sleep释放百分比或decode token/s。sleep不会替消费者保存optimizer、数据游标或整个分布式训练。

## Sleep 状态和分 tag 恢复

公共LLM/API→engine/executor→`gpu_worker.sleep/wake_up`→`SleepModeBackendFactory`→实际allocator。当前默认`cumem`封装平台allocator；factory还暴露communicator、graph、compiled artifact、durable-storage能力查询。接口存在不代表各能力均由默认backend保证，源码注释里的CRIU/durable规划不等于已有可用实现。

`sleep_mode_backend` 可选择由插件登记的 backend；未登记名称可能到首次使用（如 sleep）才报错，启动成功不是资格检查。CUDA graph offload 和 KV-only discard 另有能力要求，选择一个 backend 名称不能同时满足这些前提。

| 状态 | weights/KV行为 | 适用与代价 |
| --- | --- | --- |
| level1 | weights备份host、KV丢弃 | 之后运行同版本；必须有host容量与D2H/H2D预算 |
| level2 | 丢弃weights与KV，保留所需静态buffer | 之后安装新policy或reload；醒来未load前不可生成 |
| 部分wake | 先`tags=["weights"]`，更新后`tags=["kv_cache"]` | 减少接收weights与KV同时驻留的峰值；确认所有组件状态 |
| KV-only discard | completed pause且resident资源满足后释放KV | weights保留，恢复后需要重算KV；backend需支持selective discard |

level2的冻结参数保留选项按运行时parameter-name glob匹配，不按checkpoint名字或requires_grad自动过滤；trainer须同时省略这些updates，loader/postprocess不能换掉其storage。冻结draft/scale等保留是否正确需结合模型owner，不将其作为所有RL默认。

## 图池、通信与平台限制

默认sleep不意味着所有graph/communicator显存都释放。`sleep_mode_offload_cudagraph`按文档要求default cumem、CUDA/ROCm与实际graph池，付出pinned-host备份及copy；池外graph executable仍可能驻留。恢复同地址/comm handles是否有效需真实backend回归。

`enable_nccl_comm_suspend`是实验性选项，官方要求NCCL≥2.29.7，旧库保留buffers并warning。HCU不能仅因提供RCCL就自动启用，必须核对相应API/symbol、fork和运行测试。官方ROCm sleep还受`VLLM_ROCM_SLEEP_MEM_CHUNK_SIZE`影响，大chunk更少操作但可能更易OOM，当前教程默认256MB；HCU取值需匹配DTK和测量，不能照搬AMD结论。

官方新增实验性 `CUDACheckpointExecutor`，在普通 level1 sleep 后保存剩余 CUDA 进程状态；它要求 Linux/NVIDIA、V2 runner、cumem、专用 worker 及受限的单节点 TP，拒绝外部 KV/权重传输等组合，并不提供训练 checkpoint 或模型切换。源码在失败时终止 worker，避免部分 rank 恢复后继续服务；部分 tag wake 也须先恢复整个 CUDA 进程。它与默认 allocator 的 graph-pool offload 是不同机制，不能扩写成 HCU、任意通信库或生产长稳已经支持。

## Token 预算、抢占与异步在途

V1 scheduler按token预算、request状态与KV可用blocks推进。`max_num_batched_tokens`、`max_num_seqs`、model长度与chunked prefill改变每步输入，需同时看prefill/decode、队列和内存；microbenchmark不能代表RL真实长度分布。

新增 `max_num_inflight_kv_loads` 限制异步 KV load 持有的 slots：计算 load 进行中、已完成但等待运行，以及尚未结束的 aborted loads。显式设置后可在 running batch 满时提前发起受支持的异步 load；默认 `None` 保持原来的发起时机。它不扩大实际 running batch 或 graph 容量，也不消除等候请求占用的 KV，需测首 token、尾延迟和驻留峰值，不能只把传输重叠视为净收益。

KV不足时preemption/recompute会增加工作。异步调度包含inflight/stale output与延后block-free，未完成GPU写入前复用block会污染新请求；不能通过去同步“优化等待”而破坏ownership。睡眠/权重更新须与pause完成和request处理对齐，HTTP已响应与所有设备工作结束分别核对。

吞吐曲线应包含最长response/slow replica、preempt次数、recomputed tokens、prefix hit、weight-sync等待、policy staleness与训练步时。训练更快但rollout重算/传权更慢可能没有端到端收益。

## 混合 KV 模型

当前 `prefill_schedule_interval=N` 覆盖所有 prefill，包括已接纳长 prompt 的后续 chunks；间隔步完全留给 decode。长 prompt 完成 prefill 可能需要接近 N 倍调度步，选择该参数时同时看首 token、decode 和 RL 尾延迟，不能仅按 DP 单步均衡判断。

GPU worker 在 sleep/discard KV 前注销 KV-transfer connector 的 cache registration，恢复 KV tag 后再注册；只恢复 weights 不应提前暴露旧 KV 地址。allocator 返回不自动完成外部 connector 的存储所有权，远端 KV transfer 与 sleep 切换需独立验证。初始化也提前创建 matmul/biased-linear handle 再采集基线，避免遗漏底层库直接申请的内存；HCU 分配行为另查。

full attention保存全历史；sliding-window仅需有效窗口，SSM/混合模型还含独立state。官方hybrid-KV设计文档明确它基于历史提交并可能变动，源码当前`KVCacheManager`/coordinator/spec为最终依据。

估算不能一律总层数×序列长度：需按真实KV group、head/dim/dtype、TP分片、window、state和padding/page开销分别算。不同attention类型组的页大小约束会引入padding；文档的group page size与单层`KVCacheSpec.page_size_bytes`不是一个数量。

prefix cache是有效模型版本下的已有计算，不等于任意weight update之后仍有效。refit/wake后清理旧KV及相关connector状态，remote-KV异步失败/转移仍需协调。缓存命中和warmup与冷启动分开测。

## 数值、诊断与回退

当前混合 Mamba/full-attention 文档已说明 block-boundary Mamba state prefix caching，仍需核对具体模型、block size 和 state；不能推广到任意 token 位置恢复。cascade attention 则已移除，`KVCacheManager.get_num_common_prefix_blocks` 仅为外部 scheduler 保留接口、固定返回各组0；不能从这个0推断整个 prefix cache 没有命中，或继续按旧 cascade 机制解释收益。

固定token输入对比sleep前后、分tag恢复后及两轮weight更新后的logits/logprob；覆盖量化scale、buffers、frozen weights、draft/target和所有replica。生成token随机不同不必然错误，rank间参数/scale不同、旧KV和错误mask必须定位。

OOM看device实际占用、allocator allocated/reserved、host backup、KV预算、图池和receiver/gather临时峰值；卡住看pause/inflight→每worker状态→communicator与collective→allocator恢复→首次推理。单个`is_sleeping`值不证明全部resource恢复就绪。

worker sleep-backend与tensor-ownership测试是状态/接口回归，真实模型、多rank、HCUallocator/通信需现场验证。失败回退到已验证backend、禁用实验comm/graph offload或训推分离，恢复可信policy与KV后再开放生成；不要只重启进程并沿用不一致的样本版本。

## 固定证据与验证范围

- [docs/features/sleep_mode.md](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/docs/features/sleep_mode.md)
- [docs/design/hybrid_kv_cache_manager.md](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/docs/design/hybrid_kv_cache_manager.md)
- [vllm/device_allocator/sleep_mode_backend.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/device_allocator/sleep_mode_backend.py)
- [vllm/v1/worker/gpu_worker.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/v1/worker/gpu_worker.py)
- [vllm/v1/core/kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/v1/core/kv_cache_manager.py)
- [vllm/v1/core/sched/scheduler.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/v1/core/sched/scheduler.py)
- [vllm/config/scheduler.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/config/scheduler.py)
- [tests/v1/worker/test_sleep_mode_backend.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/tests/v1/worker/test_sleep_mode_backend.py)
- [tests/model_executor/test_sleep_mode_tensor_ownership.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/tests/model_executor/test_sleep_mode_tensor_ownership.py)
- [examples/rl/rlhf_async_new_apis.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/examples/rl/rlhf_async_new_apis.py)

本页在 2026-11-04 阅读上述固定源码和教程；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。

- [vllm/v1/executor/cuda_checkpoint_executor.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/vllm/v1/executor/cuda_checkpoint_executor.py)

- [tests/v1/executor/test_cuda_checkpoint_executor.py](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/tests/v1/executor/test_cuda_checkpoint_executor.py)
