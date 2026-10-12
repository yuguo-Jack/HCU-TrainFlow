---
id: engines/sglang
title: SGLang：RL 生成依赖的工程、运行与维护地图
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
  path: README.md
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 7c99b50fa5ef9f4a666a2f73860f746d3fc259e7e7912d4bff88dffdc1dc4c5e
- source: sgl-project-sglang
  path: python/pyproject.toml
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 298881e298c02e98ac4290e4a650d743ea07ed1f3d5077057a4b3254af407757
- source: sgl-project-sglang
  path: docs/docs/get-started/install.mdx
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: ac8f441fbcec836843e04f76e5581780c3e1ff12f4835c5fd0701b7af7d17b29
- source: sgl-project-sglang
  path: docs/docs/advanced_features/sglang_for_rl.mdx
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 751d2c54c7cc87780a7e9005a76930f73a562c6cf4d9db1574bef4eafaeecd76
- source: sgl-project-sglang
  path: python/sglang/srt/entrypoints/engine.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 5925c9a39703856a88a5b4f0e6e486a1ed3969d3786c48fea8ebdeffd990f99d
- source: sgl-project-sglang
  path: python/sglang/srt/managers/tokenizer_manager.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 3ff205aa036a3355ce93c420346dd00ef0bf4ba3013769cd8bcfa4f5ba59753f
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 8ebda29ff526cf61826ff8b2a6c907ad4d9cce3d580401a300b00308bbeedc67
- source: sgl-project-sglang
  path: python/sglang/srt/server_args.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 53285a7c988a59c99ab7954c9ca28a2de9b1c68a3065e988379a1d64df79d8e2
- source: sgl-project-sglang
  path: test/registered/rl/test_update_weights_from_distributed.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 0c06da440fd0de2b7250cd17ff6f47506eb22e4341d651fb8d49fdd9d1a2643e
- source: sgl-project-sglang
  path: test/registered/rl/test_multi_instance_release_memory_occupation.py
  commit: c6e822c29b9bb3d392e65a7bcb271a5d2d63613d
  sha256: 3f746be087e1ee08cdb7287ed12cb3e3016dec9551f321c382bc2a4de4aabbc8
pr_sources:
- pr-sgl-project--sglang-42561
- pr-sgl-project--sglang-43758
---

# SGLang：RL 生成依赖的工程、运行与维护地图

## 在训练链路中的职责

SGLang 为 RL 提供 rollout、evaluation 和训练后权重 refit，并管理生成期间的 KV、调度与显存。策略 loss、优势估计、optimizer 和训练 checkpoint 仍由 verl、slime、AReaL 等消费者拥有。需要同时锁定消费者适配器与 SGLang 的实际 HCU 分支，不能仅按“使用 SGLang”推定所有权重协议兼容。

本页是完整阅读入口；[权重更新与 policy 版本](sglang/weight-update.md)解释参数同步和缓存一致性，[显存、KV 与 rollout 调度](sglang/memory-and-scheduling.md)解释训练/生成切换。RL 的端到端效率要合并训练、传权、恢复、生成与排队窗口分析。

## 工程目录与源码入口

| 目录/文件 | 职责 | 从什么问题进入 |
| --- | --- | --- |
| `python/pyproject.toml`、`docs/docs/get-started/install.mdx` | Python 包、构建依赖、平台安装 | wheel 与源码不一致、后端导入/ABI 问题 |
| `python/sglang/srt/entrypoints/engine.py` | Python `Engine` 控制入口 | 嵌入式 RL 对接、API 生命周期 |
| `srt/managers/tokenizer_manager.py` | 请求预处理、tokenization、异步控制请求 | 请求已到服务但未进入设备调度 |
| `srt/managers/scheduler.py` | 请求 dispatch、batch 组装、生成推进、pause/continue | 排队、CPU 空泡、partial rollout、并发状态 |
| `srt/managers/scheduler_components/weight_updater.py` | 权重会话、版本、flush、显存 release/resume | 更新后 stale KV、部分失败、训练/rollout handoff |
| `srt/weight_sync/tensor_bucket.py` | 混合 dtype 权重的 flat buffer 与元数据 | packing 开销、byte offset、生命周期 |
| `srt/mem_cache/`、`srt/model_executor/` | KV/prefix、模型和后端执行 | 长 prompt 内存、attention/quantization 实际分发 |
| `python/sglang/kernels/` | 当前树的 AOT/JIT/设备 kernel | 框架显示已融合但后端回退、kernel 效率 |
| `test/registered/rl/` | 权重同步、多实例内存等回归 | 定义训练集成成功判据 |
| `docs/docs/advanced_features/sglang_for_rl.mdx` | 官方 RL API 教程 | 接口语义、启动选项与 refit 方式 |

当前官方文档主要为 `docs/docs/**/*.mdx`；目录更新需扫描当前树，不能沿旧 `.rst` 模式宣称教程无变化。大仓还含 diffusion、前端语言等，当前训练用途的主路线是语言模型 SRT 与消费者的 rollout adapter。

## 安装、依赖与真实加载

当前固定 `python/pyproject.toml` 声明 Python ≥3.10，main 的构建/运行依赖包含指定 Torch、FlashInfer 和 `torch_memory_saver`。这是此提交的依赖事实；release wheel、NVIDIA 主干、AMD 平台与 HCU patch 可能不同。HCU 安装先读现用 fork 和镜像配方，核对 DTK/PyTorch、attention/MoE backend、通信实现、编译扩展，以及每个进程实际加载的包/动态库路径。

官方教程提供 pip/wheel、源码和容器路线；源码包入口位于 `python/`。只查 `sglang.__version__` 不能证明实际 kernel 与 fork 对应，需保存源码 SHA、wheel 标识和候选 backend 选择日志。内存 saver 启用后还需确认其实际 adapter，而不是只检查 flag 出现在 argv。安装不是本次 Wiki 阅读的前置要求。

## 运行与分层验收

1. 按 HCU 工程已有同模型脚本启动 Python Engine 或服务入口，核对模型 config/tokenizer、TP/DP/EP、context、dtype、quantization、网络与设备；官方 recipe 用于确认语义。
2. 固定 tokenized prompt 做首轮生成，保存输出 token、logprob、实际 backend 和峰值。只有 `/health` 成功不足以证明模型可用。
3. 在训练 adapter 的同一协议下执行至少两轮 refit；各 rollout replica/rank 的版本与必要参数校验均完成后再消费样本。
4. 覆盖 pause/retract、在途请求、KV 清理、release/resume 与再次生成。服务进程存活、显存释放和恢复后的数值正确是不同判据。
5. 使用 `test_update_weights_from_distributed.py` 检查更新和 tied weight，使用多实例 release-memory 测试检查共享设备。测试需要的模型、TP、transport 与设备不齐时明示 skip。

修改某后端还要读 `test/registered` 对应 kernel/model 测试，不以 RL smoke 代替反向、量化或全部模型验证；SGLang 本身不负责训练 backward。

## 模型、数据和数值契约

从消费者的模型 export/转换代码追到 SGLang model loader：名字、分片、tied embedding、量化权重与 scale 都要一致。HF config 支持并不等于任意 HCU 后端支持；MoE、MLA、混合 attention、MTP/draft 的真实路径分别核对。

RL 样本关联 prompt/tokenizer、生成参数、stop/truncation、response mask、policy/weight version 与 logprob 的计算定义。采样可导致合法的 token 差异；优先固定输入对照 logits/teacher-forcing logprob，然后再比较随机 rollout 分布。不能把 speculative draft、旧 KV 或过期权重产生的概率直接用于当前策略 loss。

## 性能机制和诊断入口

权重 bucket 合并减少消息和调用次数，但增加临时 flat buffer；缓存前缀减少重复 prefill，但依赖相同模型版本和正确生命周期。睡眠释放物理显存可提高共卡利用率，但会引入主存/PCIe恢复和重新生成 KV 的成本。具体契约见两个专题。

profile 分开排队、tokenization/CPU 调度、prefill、decode、传权和 sleep/resume；用同模型、长度分布、并行配置对比单独 rollout 与训练争用后的性能。慢 rank/慢 replica、权重更新尾延迟和 policy staleness 都可能限制 RL 吞吐。GPU timeline 空白不能直接认定 engine kernel 慢。

卡住先看 tokenizer→scheduler→worker 哪一段不再推进，再核对所有 TP/更新组 rank 的会话和 collective。OOM 分别检查权重接收 buffer、KV、图池和驻留状态；loss/logprob 异常检查版本与 cached state。失败后优先停止消费不一致样本，以可信 checkpoint/version 恢复生成，随后按消费者的恢复权处理训练，不自动重放一次可能已改写权重的 RPC。

## 发布、PR 与更新路线

2026-10-12 观测的官方主干为 `c6e822c29b9bb3d392e65a7bcb271a5d2d63613d`，最近可见正式 release 为 [v0.5.21](https://github.com/sgl-project/sglang/releases/tag/v0.5.21)；主干新接口不自动等于该 release 或 HCU 分支包含。

[发布流程](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/docs/docs/developer_guide/release_process.mdx)、[Releases](https://github.com/sgl-project/sglang/releases)、[官方 Issues](https://github.com/sgl-project/sglang/issues)和 [PR](https://github.com/sgl-project/sglang/pulls)共同查证。路线规划无统一自动全量抓取承诺，按实际问题查讨论、目标分支与最终代码。

[PR #43758](https://github.com/sgl-project/sglang/pull/43758) 已合入本页固定 main，说明 flush 失败与已加载权重不是原子回滚；[PR #42561](https://github.com/sgl-project/sglang/pull/42561)截至本轮仍 open，讨论 per-runner 部分更新，不能当已修复能力。原有 [#39265](../prs/sgl-project--sglang/PR-39265.md)保留历史 packed-buffer 讨论入口。

更新使用 `wiki-update PROJECT sgl-project-sglang`；[全仓目录](../source-maps/sgl-project-sglang.md)、[原文](../upstream-docs/sgl-project-sglang/)和 `wiki-search-pr "weight update cache" --engine sglang`用于继续追查。同步阅读 release 与当前代码，联动 RL 消费者的调用协议；不能因仓库升级只修本页标题而保留旧专题。

## HCU 使用前的独立核对

本页介绍官方固定实现。HCU 模型专项线可能新增或撤回 DeepEP/量化/Graph/KV 保护与快路，不能从旧 HCU 案例推定当前支持，也不能从 guard 删除推定约束消失。安装时对照所选 HCU 源码的实际 AOT/HIP setup、依赖和扩展签名；README 或旧 `sgl-kernel` 路径与源码不一致时，先建立可验证的同一版本配方。权重更新会话、pause/retract/flush 和 torch-memory-saver 路径需在消费者与 HCU 分支一起复核。相关 HCU 仓与案例按需查询 HCU-Knowledge。

## 固定证据与验证范围

- [README.md](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/README.md)
- [python/pyproject.toml](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/pyproject.toml)
- [docs/docs/get-started/install.mdx](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/docs/docs/get-started/install.mdx)
- [docs/docs/advanced_features/sglang_for_rl.mdx](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/docs/docs/advanced_features/sglang_for_rl.mdx)
- [python/sglang/srt/entrypoints/engine.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/sglang/srt/entrypoints/engine.py)
- [python/sglang/srt/managers/tokenizer_manager.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/sglang/srt/managers/tokenizer_manager.py)
- [python/sglang/srt/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/sglang/srt/managers/scheduler.py)
- [python/sglang/srt/server_args.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/python/sglang/srt/server_args.py)
- [test/registered/rl/test_update_weights_from_distributed.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/test/registered/rl/test_update_weights_from_distributed.py)
- [test/registered/rl/test_multi_instance_release_memory_occupation.py](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/test/registered/rl/test_multi_instance_release_memory_occupation.py)

本页在 2026-10-12 阅读上述固定源码和教程；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。
