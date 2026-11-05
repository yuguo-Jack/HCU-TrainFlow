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
reviewed_on: '2026-11-04'
coverage: reviewed implementation chains and official guides; not all models, backends or HCU runtime qualification
sources:
- source: sgl-project-sglang
  path: README.md
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: a7654a48a8cd08c824e4445cb906405704148a3c55fb84362c7071d27397303c
- source: sgl-project-sglang
  path: python/pyproject.toml
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 53aa6decc9cdb9e86240b9747810e153f5cdfc477dcd1be37de97fabe14d18ef
- source: sgl-project-sglang
  path: docs/docs/get-started/install.mdx
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: bac06371373c1ab6d53d7075a4cfd894ca93a26d2ed220defb22e58065aa1cf4
- source: sgl-project-sglang
  path: docs/docs/advanced_features/sglang_for_rl.mdx
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 68ed10e2b44ce57413380df288feb3dc0b1f8a6b650589cf6ba97a340566b20f
- source: sgl-project-sglang
  path: python/sglang/srt/entrypoints/engine.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: cc13ef61843629907135f3258ac3efceca1da95e1e959cba77c72e1e0b405033
- source: sgl-project-sglang
  path: python/sglang/srt/managers/tokenizer_manager.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 5a34747dfc5592c45b4e8a82c1ad767e4e57cade786eedc9ddf94bd37926ef30
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: d6158d7d4271ef93991e69965f101a183b63f33baa041468cf83355a24d474f0
- source: sgl-project-sglang
  path: python/sglang/srt/server_args.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: b4c2b1799eb900a1576c6a5b561aa5684927752c53bd251d2d0a78e1448e7a81
- source: sgl-project-sglang
  path: test/registered/rl/test_update_weights_from_distributed.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: a76b527b0aeb9397288bcb7f1d653934d248e077031ba03c636cd0e792ce1e1e
- source: sgl-project-sglang
  path: test/registered/rl/test_multi_instance_release_memory_occupation.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: af97eca5bb9d28fc5cbe5312054c6f6f90fd3928317e8c06b3bb594849cb4a9d
- source: sgl-project-sglang
  path: python/sglang/srt/model_executor/model_runner_components/weight_updater.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: ff30b299cc3672fff0970fee1afd9fb85c31db3fb990d9132f7f7a8e7d4f5c00
- source: sgl-project-sglang
  path: python/sglang/srt/model_executor/model_runner_components/weight_exporter.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 36ded4febd1682e387f537103ec8c099efd9a2df6c464c61b4226295ac88bf2a
- source: sgl-project-sglang
  path: docs/docs/developer_guide/release_process.mdx
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 3777014aaba84367903f92c52f7898a34185fab20ee3ff9069ae8a6521f3c1cb
- source: sgl-project-sglang
  path: python/sglang/srt/managers/scheduler_components/weight_updater.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 2e65bb16c08c45f126666e2109d8fdf3139e37fccc9b889a6e4f4692bd8b1032
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/kv/router.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 4ae69633da6f617a676c0d25c53a3d7ead01d77cf697e40ee4379f377ca883b5
- source: sgl-project-sglang
  path: python/sglang/srt/mem_cache/kv_weight_version_tracker.py
  commit: fd19cfb660f42bd3ceb6df7598bd343572e30d2c
  sha256: 43688f519119233fe8c3f56d4ff658a70340fb3145a45e4b8f73c109791add05
pr_sources:
- pr-sgl-project--sglang-42561
- pr-sgl-project--sglang-43758
---

# SGLang：RL 生成依赖的工程、运行与维护地图

## 在训练链路中的职责

SGLang 为 RL 提供 rollout、evaluation 和训练后权重 refit，并管理生成期间的 KV、调度与显存。策略 loss、优势估计、optimizer 和训练 checkpoint 仍由 verl、slime、AReaL 等消费者拥有。需要同时锁定消费者适配器与 SGLang 的实际 HCU 分支，不能仅按“使用 SGLang”推定所有权重协议兼容。

本页是完整阅读入口；[权重更新与 policy 版本](../topics/weight-update.md)解释参数同步和缓存一致性，[显存、KV 与 rollout 调度](../topics/memory-and-scheduling.md)解释训练/生成切换。RL 的端到端效率要合并训练、传权、恢复、生成与排队窗口分析。

## 工程目录与源码入口

| 目录/文件 | 职责 | 从什么问题进入 |
| --- | --- | --- |
| `python/pyproject.toml`、`docs/docs/get-started/install.mdx` | Python 包、构建依赖、平台安装 | wheel 与源码不一致、后端导入/ABI 问题 |
| `python/sglang/srt/entrypoints/engine.py` | Python `Engine` 控制入口 | 嵌入式 RL 对接、API 生命周期 |
| `srt/managers/tokenizer_manager.py` | 请求预处理、tokenization、异步控制请求 | 请求已到服务但未进入设备调度 |
| `srt/managers/scheduler.py` | 请求 dispatch、batch 组装、生成推进、pause/continue | 排队、CPU 空泡、partial rollout、并发状态 |
| `srt/managers/scheduler_components/weight_updater.py` | 权重会话、版本、flush、显存 release/resume | 更新后 stale KV、部分失败、训练/rollout handoff |
| `srt/model_executor/model_runner_components/weight_updater.py`、`weight_exporter.py` | 实际参数加载、派生缓存门禁和导出限制 | RPC 到达但更新被拒、日志 rollback 与真实版本不符 |
| `srt/model_loader/`、`srt/weight_cache/` | loader 选择、量化收尾、daemon 共享权重 | 冷加载可用但 refit 不支持、共享 storage 与 sleep 不兼容 |
| `srt/weight_sync/tensor_bucket.py` | 混合 dtype 权重的 flat buffer 与元数据 | packing 开销、byte offset、生命周期 |
| `srt/mem_cache/`、`srt/model_executor/` | KV/prefix、模型和后端执行 | 长 prompt 内存、attention/quantization 实际分发 |
| `python/sglang/kernels/` | 当前树的 AOT/JIT/设备 kernel | 框架显示已融合但后端回退、kernel 效率 |
| `test/registered/rl/` | 权重同步、多实例内存等回归 | 定义训练集成成功判据 |
| `docs/docs/advanced_features/sglang_for_rl.mdx` | 官方 RL API 教程 | 接口语义、启动选项与 refit 方式 |

当前官方文档主要为 `docs/docs/**/*.mdx`；目录更新需扫描当前树，不能沿旧 `.rst` 模式宣称教程无变化。大仓还含 diffusion、前端语言等，当前训练用途的主路线是语言模型 SRT 与消费者的 rollout adapter。

## 安装、依赖与真实加载

当前固定 `python/pyproject.toml` 声明 Python ≥3.11，main 的构建/运行依赖包含指定 Torch、FlashInfer 和 `torch_memory_saver`。这是此提交的依赖事实；release wheel、NVIDIA 主干、AMD 平台与 HCU patch 可能不同。HCU 安装先读现用 fork 和镜像配方，核对 DTK/PyTorch、attention/MoE backend、通信实现、编译扩展，以及每个进程实际加载的包/动态库路径。

官方教程提供 pip/wheel、源码和容器路线；源码包入口位于 `python/`。只查 `sglang.__version__` 不能证明实际 kernel 与 fork 对应，需保存源码 SHA、wheel 标识和候选 backend 选择日志。内存 saver 启用后还需确认其实际 adapter，而不是只检查 flag 出现在 argv。安装不是本次 Wiki 阅读的前置要求。

当前包声明 Python ≥3.11、Torch 2.14.1、Transformers 5.19.0、FlashInfer 0.7.2 和 sglang-kernel 0.4.10；本轮改动还涉及 humming-kernels 0.1.18、sgl-deep-gemm 0.2.5.post3 等依赖。它们描述官方固定树，不是 HCU 安装配方；不能只更新 Python 包而复用不匹配的扩展。`ServerArgs` 的 launch command、repr 与对外配置输出对 watermark secrets 做脱敏，保存 effective config 时区分可复现的非敏感字段与需按部署管理的密钥，不能把日志打印完整参数当成验证要求。

`ServerArgs` 不再重导出 `Arg/NS/A`、`LoRARef`、`CudaGraphConfig` 等内部配置类型；外部 adapter 应从实际定义模块导入，不能依赖旧的偶然 re-export。旧 `--monokernel-backend amd|msa` 已弃用并映射到专用 AMD/NVIDIA 开关；kernel plugin 的实际设备路径仍需核对，不能将其名称直接改成 HCU 通用参数。

## 运行与分层验收

1. 按 HCU 工程已有同模型脚本启动 Python Engine 或服务入口，核对模型 config/tokenizer、TP/DP/EP、context、dtype、quantization、网络与设备；官方 recipe 用于确认语义。
2. 固定 tokenized prompt 做首轮生成，保存输出 token、logprob、实际 backend 和峰值。只有 `/health` 成功不足以证明模型可用。
3. 先核在线更新对派生权重缓存、量化/loader 和共享 weight-cache 的门禁，再在训练 adapter 的同一协议下执行至少两轮 refit；各 rollout replica/rank 的版本与必要参数校验均完成后再消费样本。
4. 覆盖 pause/retract、在途请求、KV 清理、release/resume 与再次生成。服务进程存活、显存释放和恢复后的数值正确是不同判据。
5. 使用 `test_update_weights_from_distributed.py` 检查更新和 tied weight，使用多实例 release-memory 测试检查共享设备。测试需要的模型、TP、transport 与设备不齐时明示 skip。

修改某后端还要读 `test/registered` 对应 kernel/model 测试，不以 RL smoke 代替反向、量化或全部模型验证；SGLang 本身不负责训练 backward。

## 模型、数据和数值契约

从消费者的模型 export/转换代码追到 SGLang model loader：名字、分片、tied embedding、量化权重与 scale 都要一致。HF config 支持并不等于任意 HCU 后端支持；MoE、MLA、混合 attention、MTP/draft 的真实路径分别核对。

当前 Scheduler 在 begin 前先检查所选全部 runner 的派生缓存，具体 runner 加载入口也会拒绝无法随在线参数写入刷新的派生缓存，包括补偿 mHC splits、HPC-Ops bf16xfp32 GEMM 缓存和模块自行声明的限制；共享 daemon 权重也有独立的修改/sleep 门禁。能正常生成、能导出或能冷加载，并不自动证明可用于反复 refit 的 RL。两篇专题给出实际 guard、收尾和失败边界，不把关闭某优化的上游提示变成 HCU 通用默认。

RL 样本关联 prompt/tokenizer、生成参数、stop/truncation、response mask、policy/weight version 与 logprob 的计算定义。采样可导致合法的 token 差异；优先固定输入对照 logits/teacher-forcing logprob，然后再比较随机 rollout 分布。不能把 speculative draft、旧 KV 或过期权重产生的概率直接用于当前策略 loss。

当前 KV 路线把请求 state storage、模型层到子池的 router 和虚拟到物理 slot 的 `IdSpace` 分开。自定义 attention、host-cache 或 PD adapter 要沿新的 typed view/route 读取，不能按旧 pool 类型或 `layer_id` 偶然相等推断布局。暂停后能否 refit/sleep 还取决于 overlap、PD、HiCache 和 offload 是否真正排空，见显存专题。

`--enable-prefill-weight-versions` 为目标模型的 prompt KV 提供权重版本区间，便于发现跨版本 prefix；它不清理旧 KV、不隔离请求，也不替代训练端的采样/权重版本合同。当前实现只支持 generation、非 encoder-decoder 且 PP=1。

## 性能机制和诊断入口

权重 bucket 合并减少消息和调用次数，但增加临时 flat buffer；缓存前缀减少重复 prefill，但依赖相同模型版本和正确生命周期。睡眠释放物理显存可提高共卡利用率，但会引入主存/PCIe恢复和重新生成 KV 的成本。具体契约见两个专题。

profile 分开排队、tokenization/CPU 调度、prefill、decode、传权和 sleep/resume；用同模型、长度分布、并行配置对比单独 rollout 与训练争用后的性能。慢 rank/慢 replica、权重更新尾延迟和 policy staleness 都可能限制 RL 吞吐。GPU timeline 空白不能直接认定 engine kernel 慢。

卡住先看 tokenizer→scheduler→worker 哪一段不再推进，再核对所有 TP/更新组 rank 的会话和 collective。OOM 分别检查权重接收 buffer、KV、图池和驻留状态；loss/logprob 异常检查版本与 cached state。失败后优先停止消费不一致样本，以可信 checkpoint/version 恢复生成，随后按消费者的恢复权处理训练，不自动重放一次可能已改写权重的 RPC。

## 发布、PR 与更新路线

2026-11-04 阅读的官方主干固定为 `fd19cfb660f42bd3ceb6df7598bd343572e30d2c`。本轮最近 10 条 release 元数据快照中，最新可见正式版为 [v0.5.23](https://github.com/sgl-project/sglang/releases/tag/v0.5.23)（2026-11-02 发布）；该快照不是全历史扫描，主干接口也不自动等于 release wheel 或 HCU 分支的能力。

[发布流程](https://github.com/sgl-project/sglang/blob/8e7601ae4a48c1127afd1bcdccf0a0ad61dbf043/docs/docs/developer_guide/release_process.mdx)、[Releases](https://github.com/sgl-project/sglang/releases)、[官方 Issues](https://github.com/sgl-project/sglang/issues)和 [PR](https://github.com/sgl-project/sglang/pulls)共同查证。路线规划无统一自动全量抓取承诺，按实际问题查讨论、目标分支与最终代码。

[PR #43758](https://github.com/sgl-project/sglang/pull/43758) 已合入本页固定 main，说明 flush 失败与已加载权重不是原子回滚；[PR #42561](https://github.com/sgl-project/sglang/pull/42561) 在 2026-11-01 关闭且未合入；关闭说明是作者闲置 PR 数量超过软上限，并非部分更新问题已修复。本页固定实现仍使用会话级 `loaded_weights`，应继续核对 per-runner 结果。原有 [#39265](../../upstream/prs/sgl-project--sglang/PR-39265.md)保留历史 packed-buffer 讨论入口。

更新使用 `wiki-update PROJECT sgl-project-sglang`；[全仓目录](../../upstream/source-map/sgl-project-sglang.md)、[原文](../../upstream/docs/sgl-project-sglang)和 `wiki-search-pr "weight update cache" --engine sglang`用于继续追查。同步阅读 release 与当前代码，联动 RL 消费者的调用协议；不能因仓库升级只修本页标题而保留旧专题。

## HCU 使用前的独立核对

本页介绍官方固定实现。HCU 模型专项线可能新增或撤回 DeepEP/量化/Graph/KV 保护与快路，不能从旧 HCU 案例推定当前支持，也不能从 guard 删除推定约束消失。安装时对照所选 HCU 源码的实际 AOT/HIP setup、依赖和扩展签名；README 或旧 `sgl-kernel` 路径与源码不一致时，先建立可验证的同一版本配方。权重更新会话、pause/retract/flush 和 torch-memory-saver 路径需在消费者与 HCU 分支一起复核。相关 HCU 仓与案例按需查询 HCU-Knowledge。

## 固定证据与验证范围

- [README.md](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/README.md)
- [python/pyproject.toml](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/pyproject.toml)
- [docs/docs/get-started/install.mdx](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/docs/docs/get-started/install.mdx)
- [docs/docs/advanced_features/sglang_for_rl.mdx](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/docs/docs/advanced_features/sglang_for_rl.mdx)
- [python/sglang/srt/entrypoints/engine.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/entrypoints/engine.py)
- [python/sglang/srt/managers/tokenizer_manager.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/managers/tokenizer_manager.py)
- [python/sglang/srt/managers/scheduler.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/managers/scheduler.py)
- [python/sglang/srt/server_args.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/server_args.py)
- [test/registered/rl/test_update_weights_from_distributed.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/test/registered/rl/test_update_weights_from_distributed.py)
- [test/registered/rl/test_multi_instance_release_memory_occupation.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/test/registered/rl/test_multi_instance_release_memory_occupation.py)

- [python/sglang/srt/model_executor/model_runner_components/weight_updater.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/model_executor/model_runner_components/weight_updater.py)
- [python/sglang/srt/model_executor/model_runner_components/weight_exporter.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/model_executor/model_runner_components/weight_exporter.py)

- [docs/docs/developer_guide/release_process.mdx](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/docs/docs/developer_guide/release_process.mdx)
- [python/sglang/srt/mem_cache/kv/router.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/mem_cache/kv/router.py)
- [python/sglang/srt/mem_cache/kv_weight_version_tracker.py](https://github.com/sgl-project/sglang/blob/fd19cfb660f42bd3ceb6df7598bd343572e30d2c/python/sglang/srt/mem_cache/kv_weight_version_tracker.py)


本页在 2026-11-04 复核上述固定源码、教程及最近 10 条 release 元数据；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。
