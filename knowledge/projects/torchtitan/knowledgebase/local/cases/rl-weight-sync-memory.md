---
id: official-torchtitan-wiki/cases/rl-weight-sync-memory
title: 案例：TitanRL 权重同步的训练侧暂存与生成侧峰值
engine: torchtitan
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-11-04'
retrieved_on: '2026-11-04'
coverage: Curated source chains and official evidence at a fixed main commit; not all models, backends
  or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/rl/trainer/trainer.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: f52d1d78a769b06bc511dc638486626592d0f0bdbd249d14a2f8df4107d0c3b3
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/generator.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: fe3ccd0288aa613d11234607fa24e91e98953015dd75a49657da0b4c7dd56b01
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/vllm/model_wrapper.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: dfd3054a05f24eefa3e7bfaa5ffc24433700ede8579e53d8371277ae9a0f56e8
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 3b46f79840dec9f3efd25319247fe259c0009daeec74bf381d06c483ddea8b09
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_vllm_wrapper.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 56b1b2822e75fd8eb63441a8937e758ca31e9aefa0bf0a6df8f8288915efa705
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_trainer_loop.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 6787b02e01bfb80565c070eea69f6fbf63494a4dce00cbe4c55ea9e456163a3f
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/system.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: fe63bfd041a5f03d4f8afc4f80b77f1085c7c808ae2b4a2d3cf4786b938c1bb9
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/engine_loop.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 08690a20311acba28c61b8ca65a2062da4bbfd0ee2cb2168b50543887dd401b0
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_engine_loop.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: b9a5defb95961aad5fab4f6cf65705e2e118f74d5292f1b89e3e785b7cc85c0f

pr_sources:
- pr-pytorch--torchtitan-5107
- pr-pytorch--torchtitan-5268
---
# 案例：TitanRL 权重同步的训练侧暂存与生成侧峰值

## 两个不同的瓶颈

RL 权重同步可能同时在 trainer 和 generator 产生大块临时存储。PR #5107 处理 trainer 的 GPU cast/snapshot；PR #5268 处理 generator 加载时的全模型双份驻留。它们不是同一个开关，也不能只测一边的峰值。

## 训练侧：Store 快照与同步所有权

PR #5107 的 pinned CPU mirror 是历史阶段。当前 `Trainer.push_model_state_dict` → `_put_model_state_dict` 直接发布 live 模型 tensor，移除了 `_setup_staging_model_state_dict` / `_stage_model_state_dict`。SharedMemory transport 可直接把 tensor 复制/转换到 StorageVolume；其他 transport 可能按批临时 GPU cast。容量预算应按实际 transport 测 GPU/Host 和 Store，不能继续固定计入 trainer 自有整模型镜像，也不能据此说没有任何暂存。

独立 push stream 在 optimizer 更新最终完成时捕获依赖；worker 将该 stream 设为 current 并同步，因为 RDMA 读可能在 stream 顺序之外。Controller 在下次 optimizer 修改权重前等待 push，在下次 push 覆盖 Store key 前等待所有 generator pull。forward/backward overlap 依赖其不修改 persistent model state；违反该条件会混合两步权重。

transfer dtype 从根 `precision.param_dtype` 与基础 `precision.dtype` 决定，buffers 与 `preserve_dtype_params` 以自身 dtype 发送。节省一份 Host 镜像也可能把转换或等待移到另一端，按真实有效 rollout/训练时间评价。

## 生成侧：按 FSDP group 加载

生成侧平时保留 unsharded 权重，逐组加载仍控制 sharded 临时峰值。当前入口为 `VLLMModelWrapper.load_model_state_dict(fetch)`，取代旧的一次 `load_state_dict` pre/post hooks：按共享 FSDP state 分组，显式 reshard → 分配 sharded storage → fetch 全部该组参数 → unshard → 释放，再处理 buffers。tied embedding/norm/LM-head 同组，不能按单个 module 提前 all-gather；`_reshard` 还处理 FORWARD 状态下 public reshard 会 no-op 的情形，并保持 Graph 使用的 unsharded storage。

默认 `cpu_prefetch` 在生成期间读完整 pinned CPU 副本，load 再复制；`gpu_fetch` 不建这份副本，暂停 engine 后逐组直接读取 Store，拒绝量化参数，增加同步暴露时间。fetch 在 stream 顺序外写入时，必须先等旧工作及新分配完成，返回前写入完成。

每个参数 key 都要填充，缺失报错；gpu_fetch 的 `strict=False` 只允许未发布 buffers 保持原值。某 rank fetch 失败后仍完成剩余组 collective，随后传播错误并让所有 generator ranks 停止 loop，避免其他 rank 卡住或继续使用部分新权重。失败后不能直接重用已污染模型继续 rollout。

## 上游证据

#5268 作者报告 H100 95 GiB、BF16、vLLM memory limit 0.9：Qwen3.5-35B-A3B TP1 的额外同步显存约从 64.6 GiB 降到 1.6 GiB，同步约 1.3 s；Qwen3.5-9B TP1 约 16.7→1.9 GiB。它保留了原本 KV cache 容量，而非单纯降低 memory limit。

PR 包含 CPU FSDP group 生命周期回归、两卡 parity、相同/扰动/恢复权重的 greedy decode，以及较长 RL 运行记录；其中一个运行以 Host OOM 停止。必须保留这些适用边界，不能摘要成“内存和长稳全部通过”。本轮未复测这些结果。

## 可复用验证与回退

分别量 trainer GPU/Host、generator GPU/Host、KV cache、stage/push/pull/wait 和端到端有效 rollout/训练时间；覆盖 tied weights、TP/FSDP、连续多次同步、graph、异步队列、失败重试。每次生成明确记录 policy version，比较更新前后输出和 logprob，确认新权重真的生效。

HCU 接入先查已有 RL/推理工程的同步实现与底层通信库，不机械照搬 CUDA/TorchStore 的硬件假设。无法保证异步 buffer 生命周期时先回到明确同步的可靠基线，再逐项引入 overlap；完整恢复和训练质量优先于隐藏一次等待。

可定位到 CPU `test_vllm_wrapper.py` 的逐 FSDP group 加载、fetch 失败与缺失参数回归：构造 tied embedding group 与三个 block，检查复制前已分配、峰值至多两个 group、结束后释放且全部参数更新。当前 `test_trainer_loop.py` 检查push→pull→release、optimizer前等待上次push、下次push前等待上次pull、最后一次transfer收尾和异常传播；这些控制逻辑检查仍不能替代真实 RDMA/设备/多次训练更新的验证。

## 当前传输 API 与统计范围

MonarchActorSystem 在 trainer mesh 建立 StorageVolume 并初始化所有角色 client；权重 PUT 仍显式 `direct_rdma=False`。Store 快照、generator 可选 pinned CPU prefetch、逐组 GPU 临时 storage 和 KV cache 是不同容量项；RDMA microbatch 数据不混入权重同步收益。

排队 load 可合并到最高版本；gpu_fetch load 只有全部 ranks 读完才完成。Controller 继续等待所有 generator pull 才释放下一批 rollout groups，早完成者可能等最慢者。指标仍为 `trainer_push_model_state_dict` / `generator_pull_model_state_dict`。历史 #5268 的 H100 数字只证明当时 group-loading 改动，不是当前 transport/load-mode 重构后的基准。

## 固定证据与使用边界

本页以官方主线 `485c065cb248863bf2e2c65588becd6d7a8bcf83` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/rl/trainer/trainer.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/trainer/trainer.py)
- [torchtitan/rl/generator/generator.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/generator/generator.py)
- [torchtitan/rl/generator/vllm/model_wrapper.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/generator/vllm/model_wrapper.py)
- [torchtitan/rl/actors/monarch/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/actors/monarch/README.md)
- [tests/rl/unit_tests/cpu/test_vllm_wrapper.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/rl/unit_tests/cpu/test_vllm_wrapper.py)
- [tests/rl/unit_tests/cpu/test_trainer_loop.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/rl/unit_tests/cpu/test_trainer_loop.py)

- [PR #5107：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5107.md)
- [PR #5268：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5268.md)

## 权重同步之外的生成故障

当前生成器区分单请求 admission/generation 异常与 engine loop 故障，失败返回和 request 清理不能替代权重更新资格。同步测量期间若出现请求失败，记录成功率与失败分布，避免以完成请求减少造成的显存/耗时下降冒充优化。当前请求故障/路由释放细节见 [TitanRL](../topics/titanrl.md)。

## 本次补充的实现与测试依据

- [torchtitan/rl/actors/monarch/system.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/actors/monarch/system.py)
- [torchtitan/rl/generator/engine_loop.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/generator/engine_loop.py)

- [tests/rl/unit_tests/cpu/test_engine_loop.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/rl/unit_tests/cpu/test_engine_loop.py)
