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
reviewed_on: '2026-10-12'
coverage: reviewed implementation chains and official guides; not all models, backends
  or HCU runtime qualification
sources:
- source: vllm-project-vllm
  path: docs/features/sleep_mode.md
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: 85bd01f925e1ad92c80ac023214ec1a1dd7d431fc8ae03ba4ee214cfb8ab13de
- source: vllm-project-vllm
  path: docs/design/hybrid_kv_cache_manager.md
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: 5a3138f8d3fddc44d69f7782510c0c97b394ee073bb743cae34bfbf281985b4a
- source: vllm-project-vllm
  path: vllm/device_allocator/sleep_mode_backend.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: 4c90c6aa44b50dc5bbdd6b09d1e6a91d56d3481a109a8d7f8cc351927401196b
- source: vllm-project-vllm
  path: vllm/v1/worker/gpu_worker.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: e970aa29a738aa15cd963d9f9202ca6d3d504e98fd344959fd998e940472a5a0
- source: vllm-project-vllm
  path: vllm/v1/core/kv_cache_manager.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: 940d4cba8c5ad2c5f2d209beddbac97c812e83302266dc8e38f8e4b8683dccd1
- source: vllm-project-vllm
  path: vllm/v1/core/sched/scheduler.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: d546a324891860fbaeb2d82a85b2a7970825972cac7c8f7327d84632fa53d04d
- source: vllm-project-vllm
  path: vllm/config/scheduler.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: 2fb86b1572a4925be59f304d13b4f6ec03d496b67a7c4abbb976ecda2232839a
- source: vllm-project-vllm
  path: tests/v1/worker/test_sleep_mode_backend.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: 80cbeef15c516e2dcf936987117b2a8e392405ec4f627e1ea1cb2870e3fdad8e
- source: vllm-project-vllm
  path: tests/model_executor/test_sleep_mode_tensor_ownership.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: be4d7b31c31e75d048b66a99849be15cff8de4c93bcdc1c6f5dced53afddbfd1
- source: vllm-project-vllm
  path: examples/rl/rlhf_async_new_apis.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: b422474b8ae8d7d6b5e7fb52fb5e7ba50bbd48c79be76f1b856502cfe0fe1fae
---

# vLLM sleep、KV 与调度：训练共卡的内存和数值交接

## 资源所有权与端到端目标

共卡RL应同时核对训练参数/optimizer/激活、推理weights/KV、图池、communicator、workspace和权重更新副本。最终目标是RL迭代吞吐及可接受policy staleness，不是单看sleep释放百分比或decode token/s。sleep不会替消费者保存optimizer、数据游标或整个分布式训练。

## Sleep 状态和分 tag 恢复

公共LLM/API→engine/executor→`gpu_worker.sleep/wake_up`→`SleepModeBackendFactory`→实际allocator。当前默认`cumem`封装平台allocator；factory还暴露communicator、graph、compiled artifact、durable-storage能力查询。接口存在不代表各能力均由默认backend保证，源码注释里的CRIU/durable规划不等于已有可用实现。

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

## Token 预算、抢占与异步在途

V1 scheduler按token预算、request状态与KV可用blocks推进。`max_num_batched_tokens`、`max_num_seqs`、model长度与chunked prefill改变每步输入，需同时看prefill/decode、队列和内存；microbenchmark不能代表RL真实长度分布。

KV不足时preemption/recompute会增加工作。异步调度包含inflight/stale output与延后block-free，未完成GPU写入前复用block会污染新请求；不能通过去同步“优化等待”而破坏ownership。睡眠/权重更新须与pause完成和request处理对齐，HTTP已响应与所有设备工作结束分别核对。

吞吐曲线应包含最长response/slow replica、preempt次数、recomputed tokens、prefix hit、weight-sync等待、policy staleness与训练步时。训练更快但rollout重算/传权更慢可能没有端到端收益。

## 混合 KV 模型

full attention保存全历史；sliding-window仅需有效窗口，SSM/混合模型还含独立state。官方hybrid-KV设计文档明确它基于历史提交并可能变动，源码当前`KVCacheManager`/coordinator/spec为最终依据。

估算不能一律总层数×序列长度：需按真实KV group、head/dim/dtype、TP分片、window、state和padding/page开销分别算。不同attention类型组的页大小约束会引入padding；文档的group page size与单层`KVCacheSpec.page_size_bytes`不是一个数量。

prefix cache是有效模型版本下的已有计算，不等于任意weight update之后仍有效。refit/wake后清理旧KV及相关connector状态，remote-KV异步失败/转移仍需协调。缓存命中和warmup与冷启动分开测。

## 数值、诊断与回退

固定token输入对比sleep前后、分tag恢复后及两轮weight更新后的logits/logprob；覆盖量化scale、buffers、frozen weights、draft/target和所有replica。生成token随机不同不必然错误，rank间参数/scale不同、旧KV和错误mask必须定位。

OOM看device实际占用、allocator allocated/reserved、host backup、KV预算、图池和receiver/gather临时峰值；卡住看pause/inflight→每worker状态→communicator与collective→allocator恢复→首次推理。单个`is_sleeping`值不证明全部resource恢复就绪。

worker sleep-backend与tensor-ownership测试是状态/接口回归，真实模型、多rank、HCUallocator/通信需现场验证。失败回退到已验证backend、禁用实验comm/graph offload或训推分离，恢复可信policy与KV后再开放生成；不要只重启进程并沿用不一致的样本版本。

## 固定证据与验证范围

- [docs/features/sleep_mode.md](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/docs/features/sleep_mode.md)
- [docs/design/hybrid_kv_cache_manager.md](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/docs/design/hybrid_kv_cache_manager.md)
- [vllm/device_allocator/sleep_mode_backend.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/vllm/device_allocator/sleep_mode_backend.py)
- [vllm/v1/worker/gpu_worker.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/vllm/v1/worker/gpu_worker.py)
- [vllm/v1/core/kv_cache_manager.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/vllm/v1/core/kv_cache_manager.py)
- [vllm/v1/core/sched/scheduler.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/vllm/v1/core/sched/scheduler.py)
- [vllm/config/scheduler.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/vllm/config/scheduler.py)
- [tests/v1/worker/test_sleep_mode_backend.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/tests/v1/worker/test_sleep_mode_backend.py)
- [tests/model_executor/test_sleep_mode_tensor_ownership.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/tests/model_executor/test_sleep_mode_tensor_ownership.py)
- [examples/rl/rlhf_async_new_apis.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/examples/rl/rlhf_async_new_apis.py)

本页在 2026-10-12 阅读上述固定源码和教程；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。
