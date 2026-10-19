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
reviewed_on: '2026-10-20'
coverage: Curated source chains and official evidence at a fixed main commit; not all models, backends
  or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: torchtitan/rl/trainer/trainer.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 35f0171826f745ea5c82458b176831e2e5ced1969ac352d5f60092fc4ad0b65c
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/generator.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: aecf95576c0710a68846850e63703b928fa41f5e426232a36069a0b3b424175e
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/vllm/model_wrapper.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: fafc5445e083d8a5eaecfbee41c16c2e1c7ea43790296217bcd7827b0841a974
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 5f4cdb46330683cb8bd2a65d764662712972fb8989afe35a9b9dfbe5e3270209
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_vllm_wrapper.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 0fb187c2c30227b547566cd0b2195426be17d095234dcafdb8059d0df70d7797
- source: pytorch-torchtitan
  path: tests/rl/unit_tests/cpu/test_trainer_loop.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 56708d030bafecf2b37c81362f9ae50a6744db9d94e41522b6af62ba5d6a92f3
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/system.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 99f940aa2efdf924cf99838de83266d752fe2f9a3e39a75b34dac5e3e06c0345
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/engine_loop.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 9c4679f1923f8d2f0a946b8576bccec5a810bf54e3996cc5c0af385341222a15
pr_sources:
- pr-pytorch--torchtitan-5107
- pr-pytorch--torchtitan-5268
---
# 案例：TitanRL 权重同步的训练侧暂存与生成侧峰值

## 两个不同的瓶颈

RL 权重同步可能同时在 trainer 和 generator 产生大块临时存储。PR #5107 处理 trainer 的 GPU cast/snapshot；PR #5268 处理 generator 加载时的全模型双份驻留。它们不是同一个开关，也不能只测一边的峰值。

## 训练侧：稳定 CPU mirror 与同步所有权

旧路径若在 GPU 把完整模型转换为生成 dtype，会产生接近模型大小的临时副本。改动将持久 CPU mirror 放在匹配 GPU NUMA 的 pinned memory，用它完成发布前的稳定快照，再进入 TorchStore。

当前入口在 `rl/trainer/trainer.py`：追踪 `Trainer._setup_staging_model_state_dict`、`_stage_model_state_dict`、`_wait_for_staging_and_put_model_state_dict` 及 `push_model_state_dict`；Controller/router负责相应pull，旧weight-sync端点名与目录已迁移。下一轮 forward/backward 可以在不修改相应权重时 overlap，但 optimizer 修改原权重前必须等待必要 staging 完成；CPU buffer/key 在 pull 未完成前不可覆盖。否则发布的 tensor 可能混合两个 optimizer step。

把 GPU 等待和阻塞发布安排在线程中维持事件循环响应，不代表数据已经复制完成。代价包括主机 pinned memory、CPU/NUMA 带宽与 TorchStore 的复制；要同时测 Host 峰值和同步暴露时长。#5107 的说明不是一组通用的端到端提速百分比。

## 生成侧：按 FSDP group 加载

生成侧平时保留 unsharded 权重。若加载前给所有 FSDP group 一次性重建 sharded buffer，瞬时驻留接近两份模型；vLLM 已用大部分余量分配 KV cache 时，首次 sync 就可能 OOM。

#5268 在当前 `rl/generator/vllm/model_wrapper.py::VLLMModelWrapper.load_state_dict` 的一次完整加载内，利用 pre/post hook 按共享 FSDP state 的 **group** 分配、复制、unshard、释放；不能简单按每个子 module 调一次 load。`fully_shard([norm,lm_head])` 的成员共享状态，tied embeddings 的跨模块 group 生命周期更长，必须一起处理。

不应为了通过加载就设 `strict=False`：缺失参数可能留下未初始化 buffer。失败条件还包括重复同步后 pointer/state 不一致、graph 引用旧存储、group 提前 unshard 读未加载参数、权重版本未完成就开始 rollout。

## 上游证据

#5268 作者报告 H100 95 GiB、BF16、vLLM memory limit 0.9：Qwen3.5-35B-A3B TP1 的额外同步显存约从 64.6 GiB 降到 1.6 GiB，同步约 1.3 s；Qwen3.5-9B TP1 约 16.7→1.9 GiB。它保留了原本 KV cache 容量，而非单纯降低 memory limit。

PR 包含 CPU FSDP group 生命周期回归、两卡 parity、相同/扰动/恢复权重的 greedy decode，以及较长 RL 运行记录；其中一个运行以 Host OOM 停止。必须保留这些适用边界，不能摘要成“内存和长稳全部通过”。本轮未复测这些结果。

## 可复用验证与回退

分别量 trainer GPU/Host、generator GPU/Host、KV cache、stage/push/pull/wait 和端到端有效 rollout/训练时间；覆盖 tied weights、TP/FSDP、连续多次同步、graph、异步队列、失败重试。每次生成明确记录 policy version，比较更新前后输出和 logprob，确认新权重真的生效。

HCU 接入先查已有 RL/推理工程的同步实现与底层通信库，不机械照搬 CUDA/TorchStore 的硬件假设。无法保证异步 buffer 生命周期时先回到明确同步的可靠基线，再逐项引入 overlap；完整恢复和训练质量优先于隐藏一次等待。

可定位到 CPU `test_vllm_wrapper.py::test_load_state_dict_allocates_one_fsdp_group_at_a_time`：构造 tied embedding group 与三个 block，检查复制前已分配、峰值至多两个 group、结束后释放且全部参数更新。当前 `test_trainer_loop.py` 检查push→pull→release、optimizer前等待上次push、下次push前等待上次pull、最后一次transfer收尾和异常传播；这些控制逻辑检查仍不能替代真实 RDMA/设备/多次训练更新的验证。

## 当前传输 API 与统计范围

主干将这条链明确称为model state dict transfer。MonarchActorSystem先在trainer mesh建立TorchStore storage并初始化全部角色client；trainer复用pinned CPU mirror，当前put显式 `direct_rdma=False`。不能因TorchStore一般支持RDMA就把本发布步骤记成GPU-to-GPU零拷贝，也不能把RDMA microbatch数据传输混入权重同步收益。

Generator在engine loop的step边界加载，排队load可合并到最高版本；Controller等待所有generator完成pull才释放新的rollout groups。这既影响策略freshness，也让早完成的generator可能等慢者。指标名和trace入口已采用 `trainer_push_model_state_dict` / `generator_pull_model_state_dict`，比较旧报告时按相同stage边界映射。当前group加载机制及strict=True仍保留，但历史H100数字不是重构后的新基准。

## 固定证据与使用边界

本页以官方主线 `a242475253433725f10f39c18f5ccbfdf188e097` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/rl/trainer/trainer.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/trainer/trainer.py)
- [torchtitan/rl/generator/generator.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/generator/generator.py)
- [torchtitan/rl/generator/vllm/model_wrapper.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/generator/vllm/model_wrapper.py)
- [torchtitan/rl/actors/monarch/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/actors/monarch/README.md)
- [tests/rl/unit_tests/cpu/test_vllm_wrapper.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/rl/unit_tests/cpu/test_vllm_wrapper.py)
- [tests/rl/unit_tests/cpu/test_trainer_loop.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/rl/unit_tests/cpu/test_trainer_loop.py)

- [PR #5107：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5107.md)
- [PR #5268：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5268.md)

## 权重同步之外的生成故障

当前生成器区分单请求 admission/generation 异常与 engine loop 故障，失败返回和 request 清理不能替代权重更新资格。同步测量期间若出现请求失败，记录成功率与失败分布，避免以完成请求减少造成的显存/耗时下降冒充优化。当前请求故障/路由释放细节见 [TitanRL](../topics/titanrl.md)。

## 本次补充的实现与测试依据

- [torchtitan/rl/actors/monarch/system.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/actors/monarch/system.py)
- [torchtitan/rl/generator/engine_loop.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/generator/engine_loop.py)
