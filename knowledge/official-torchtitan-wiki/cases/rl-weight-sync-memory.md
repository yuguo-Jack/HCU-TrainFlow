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
reviewed_on: '2026-10-12'
coverage: Curated source chains and official evidence at a fixed main commit; not
  all models, backends or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/rl/trainer.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 77eea0ae2d0db6b99c65a68db1db7b1844e38be0367d421f776eba2da92f82de
- source: pytorch-torchtitan
  path: torchtitan/rl/generator.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 109291afc2d11a6a0ccc39cd93374c32b9809ba003c82eb9966b9633eb415569
- source: pytorch-torchtitan
  path: torchtitan/rl/model/vllm_wrapper.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: c65f7744b246873aa71b0161dbb471108abc77646118a9c70f6c483539c304da
- source: pytorch-torchtitan
  path: torchtitan/rl/distributed/WEIGHT_SYNC.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: f04cf9beb18c900eab1c2aff5d079e1fe4fa4db03fda74286cf72ebd6ff3e669
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_vllm_wrapper.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: a188cead28dac31cf45fb49019a1a01e83333931dd6093c9691e46d2a4e0bc5b
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_weight_sync.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 0f180806965df19bfec4c7a323123ce676eb83c59c9acb611e54b6665c7c3d24
pr_sources:
- pr-pytorch--torchtitan-5107
- pr-pytorch--torchtitan-5268
---

# 案例：TitanRL 权重同步的训练侧暂存与生成侧峰值

## 两个不同的瓶颈

RL 权重同步可能同时在 trainer 和 generator 产生大块临时存储。PR #5107 处理 trainer 的 GPU cast/snapshot；PR #5268 处理 generator 加载时的全模型双份驻留。它们不是同一个开关，也不能只测一边的峰值。

## 训练侧：稳定 CPU mirror 与同步所有权

旧路径若在 GPU 把完整模型转换为生成 dtype，会产生接近模型大小的临时副本。改动将持久 CPU mirror 放在匹配 GPU NUMA 的 pinned memory，用它完成发布前的稳定快照，再进入 TorchStore。

追踪 `Trainer._setup_staging_model_state_dict`、`_stage_model_state_dict`、`_wait_for_staging_and_put_model_state_dict` 及异步 push/pull。下一轮 forward/backward 可以在不修改相应权重时 overlap，但 optimizer 修改原权重前必须等待必要 staging 完成；CPU buffer/key 在 pull 未完成前不可覆盖。否则发布的 tensor 可能混合两个 optimizer step。

把 GPU 等待和阻塞发布安排在线程中维持事件循环响应，不代表数据已经复制完成。代价包括主机 pinned memory、CPU/NUMA 带宽与 TorchStore 的复制；要同时测 Host 峰值和同步暴露时长。#5107 的说明不是一组通用的端到端提速百分比。

## 生成侧：按 FSDP group 加载

生成侧平时保留 unsharded 权重。若加载前给所有 FSDP group 一次性重建 sharded buffer，瞬时驻留接近两份模型；vLLM 已用大部分余量分配 KV cache 时，首次 sync 就可能 OOM。

#5268 在 `VLLMModelWrapper.load_state_dict` 的一次完整加载内，利用 pre/post hook 按共享 FSDP state 的 **group** 分配、复制、unshard、释放；不能简单按每个子 module 调一次 load。`fully_shard([norm,lm_head])` 的成员共享状态，tied embeddings 的跨模块 group 生命周期更长，必须一起处理。

不应为了通过加载就设 `strict=False`：缺失参数可能留下未初始化 buffer。失败条件还包括重复同步后 pointer/state 不一致、graph 引用旧存储、group 提前 unshard 读未加载参数、权重版本未完成就开始 rollout。

## 上游证据

#5268 作者报告 H100 95 GiB、BF16、vLLM memory limit 0.9：Qwen3.5-35B-A3B TP1 的额外同步显存约从 64.6 GiB 降到 1.6 GiB，同步约 1.3 s；Qwen3.5-9B TP1 约 16.7→1.9 GiB。它保留了原本 KV cache 容量，而非单纯降低 memory limit。

PR 包含 CPU FSDP group 生命周期回归、两卡 parity、相同/扰动/恢复权重的 greedy decode，以及较长 RL 运行记录；其中一个运行以 Host OOM 停止。必须保留这些适用边界，不能摘要成“内存和长稳全部通过”。本轮未复测这些结果。

## 可复用验证与回退

分别量 trainer GPU/Host、generator GPU/Host、KV cache、stage/push/pull/wait 和端到端有效 rollout/训练时间；覆盖 tied weights、TP/FSDP、连续多次同步、graph、异步队列、失败重试。每次生成明确记录 policy version，比较更新前后输出和 logprob，确认新权重真的生效。

HCU 接入先查已有 RL/推理工程的同步实现与底层通信库，不机械照搬 CUDA/TorchStore 的硬件假设。无法保证异步 buffer 生命周期时先回到明确同步的可靠基线，再逐项引入 overlap；完整恢复和训练质量优先于隐藏一次等待。

可定位到 CPU `test_vllm_wrapper.py::test_load_state_dict_allocates_one_fsdp_group_at_a_time`：构造 tied embedding group 与三个 block，检查复制前已分配、峰值至多两个 group、结束后释放且全部参数更新。`test_weight_sync.py` 检查 push→pull→release、版本传递、异步启动与异常传播；这些控制逻辑检查仍不能替代真实 RDMA/设备/多次训练更新的验证。

## 固定证据与使用边界

本页以官方主线 `65aaaa960698ab5d6e98c874177b41b9c30e9c58` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/rl/trainer.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/rl/trainer.py)
- [torchtitan/rl/generator.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/rl/generator.py)
- [torchtitan/rl/model/vllm_wrapper.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/rl/model/vllm_wrapper.py)
- [torchtitan/rl/distributed/WEIGHT_SYNC.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/rl/distributed/WEIGHT_SYNC.md)
- [tests/rl/unit_tests/cpu/test_vllm_wrapper.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/tests/rl/unit_tests/cpu/test_vllm_wrapper.py)
- [tests/rl/unit_tests/cpu/test_weight_sync.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/tests/rl/unit_tests/cpu/test_weight_sync.py)

- [PR #5107：描述、review、评论及 diff](../../prs/pytorch--torchtitan/PR-5107.md)
- [PR #5268：描述、review、评论及 diff](../../prs/pytorch--torchtitan/PR-5268.md)
