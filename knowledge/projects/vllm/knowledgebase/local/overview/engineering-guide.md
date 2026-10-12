---
id: engines/vllm
title: vLLM：RL 权重同步、生成与显存交接的工程地图
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
  path: README.md
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: 4dc7399323b9660117f8cc1226afb7a81cdbb912dbb4ae74b66d89052417d11c
- source: vllm-project-vllm
  path: pyproject.toml
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: eaa19cba70f13234be4acdc1eeb2126b937c6f0892fd1af29863db5a62bee95b
- source: vllm-project-vllm
  path: setup.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: b2ce0549ef12e33c1db846c417235f4e4d104673a09ba29333694f283440347c
- source: vllm-project-vllm
  path: docs/getting_started/installation/gpu.rocm.inc.md
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: 2df1b0495fd6b39d75451a29dd97f9c19d5926d74b41fbe129121e5a18b14b5a
- source: vllm-project-vllm
  path: docs/models/supported_models.md
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: bd5879be29836d74b2e974d107f1a9fe50706ba5f9a0d854edc497981d98fb94
- source: vllm-project-vllm
  path: docs/training/rlhf.md
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: b523c750e27aabd2c342609a6eb042a2d97a5d37aff6db56e48164d23442e290
- source: vllm-project-vllm
  path: docs/training/weight_transfer/README.md
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: 0667bf0764bba25629a931ad8c81801517cfc4a478d4b57286cdeb5591e40518
- source: vllm-project-vllm
  path: docs/features/sleep_mode.md
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: 85bd01f925e1ad92c80ac023214ec1a1dd7d431fc8ae03ba4ee214cfb8ab13de
- source: vllm-project-vllm
  path: vllm/v1/worker/gpu_worker.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: e970aa29a738aa15cd963d9f9202ca6d3d504e98fd344959fd998e940472a5a0
- source: vllm-project-vllm
  path: vllm/v1/core/sched/scheduler.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: d546a324891860fbaeb2d82a85b2a7970825972cac7c8f7327d84632fa53d04d
- source: vllm-project-vllm
  path: examples/rl/rlhf_async_new_apis.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: b422474b8ae8d7d6b5e7fb52fb5e7ba50bbd48c79be76f1b856502cfe0fe1fae
- source: vllm-project-vllm
  path: tests/v1/worker/test_gpu_worker_weight_transfer.py
  commit: 8d7b93fec2eb72ce01f2217472ac1f51b9bce600
  sha256: aa88face06df5f7e7313211e22845474670e1437218ec99165efce40b25a1a67
---

# vLLM：RL 权重同步、生成与显存交接的工程地图

## 训练职责和阅读路线

vLLM在RL中提供高吞吐rollout、eval及训练后的权重安装，负责推理调度/KV/模型执行；训练optimizer、优势估计、loss和checkpoint由consumer负责。每个问题同时查verl/AReaL等adapter与vLLM接口、训练端export和实际HCU fork。

[权重同步专题](../topics/weight-transfer.md)说明sender、gather和每轮start/update/finish；[显存与KV专题](../topics/memory-and-scheduling.md)说明sleep、分tag恢复、调度/混合KV及数值。不要把服务吞吐优化与RL策略更新正确性分开验收。

## 工程目录和调用链

| 目录/文件 | 职责 | 问题入口 |
| --- | --- | --- |
| `pyproject.toml`、`setup.py`、`docs/getting_started/installation/` | 构建、平台wheel/扩展和依赖 | Torch ABI、目标平台、包与源码身份 |
| `vllm/config/` | 模型、并行、scheduler、weight-transfer等配置 | 一个参数到底落在哪一层 |
| `vllm/entrypoints/` | Python/HTTP控制和请求入口 | 暂停、权重操作、状态报告 |
| `vllm/v1/core/sched/` | 请求状态与token/KV预算 | 等待、抢占、异步在途、吞吐尾延迟 |
| `vllm/v1/core/kv_cache_manager.py` | KV分配/命中/释放协调 | 长上下文、滑窗、prefix、混合模型 |
| `vllm/v1/worker/gpu_worker.py` | 设备初始化、模型运行、sleep/refit | 内存handoff、候选路径、底层执行 |
| `vllm/distributed/weight_transfer/` | source、client、factory、transport | 训练分片物化、跨副本更新、逐层buffer |
| `vllm/device_allocator/` | sleep backend/allocator | 物理内存恢复、graph/communicator状态 |
| `vllm/model_executor/`、`vllm/attention/`、`csrc/` | 模型、quantization、attention与扩展 | 参数名/分片、kernel分发和算子性能 |
| `examples/rl/`、`tests/distributed/`、`tests/v1/worker/` | RL例子、transport/worker回归 | 同步、IPC/训推分离、失败状态验证 |

一次rollout为consumer→generation入口→engine-core/scheduler→executor/worker/model-runner→模型kernel→outputs；一次policy同步另走training WeightSource→client/transport→worker→load/post-load→版本提交。两个链路在pause、KV和weight-version相交，不能只读其中一个。

## 安装与实际运行

当前固定pyproject声明Python ≥3.11且<3.15，build依赖指定Torch；源码setup依据目标平台构建扩展，ROCm官方指南与HCU镜像配方应分别阅读。遵循实际HCU fork支持的Torch/DTK/编译器/通信版本，记录wheel来源、source SHA、扩展路径和backend日志；`vllm.__version__`不是动态库加载证据。

从HCU消费者既有rollout脚本选择serve或嵌入式LLM/AsyncLLM；固定模型config/tokenizer、TP/PP/DP/EP、attention/quantization、max-model-len、scheduler预算和memory配置。训练main与推理main各自latest并不保证兼容，wire params、loader格式和控制端必须成组锁定。

## 模型、数据和运行验收

官方supported-models按实现/任务列入口；新HF架构名称、视觉/SSM/滑窗/MLA、MoE和draft支持需追对应model与平台backend。训练分片参数需转换为模型真正使用的名字、shape/layout、dtype/scales；MoE专家与tied weights特别核对。

验收顺序：导入与候选backend确认→固定tokenprompt生成→两次权重更新→每副本权重/版本与logits验证→pause/sleep/wake→请求恢复→消费者RL小跑。`tests/v1/worker/test_gpu_worker_weight_transfer.py`覆盖worker委派和非法状态，sleep-backend/tensor-ownership测试覆盖部分资源生命周期；有模型、transport、设备的集成测试才能证明真实通信，不能把mock测试覆盖当现场通过。

每批rollout记录policy version、输入token、sampling和stop/mask/logprob定义。推理logprob是否temperature调整或来自哪个distribution需与consumer训练定义对齐；允许随机生成差异，但量化、stale权重/KV和不一致rank不是采样噪声。

## 性能、故障与恢复

以RL迭代计时分账：training gather/export、weight transfer、postprocess、sleep/wake、重新prefill、生成/排队。优先看最慢replica/rank和真实token长度分布；对照独立同shapeattention/GEMM/通信与训练并发时的争用。机制与代价见两专题。

同步卡住先确认所有训练rank是否按metadata同序materialize、所有rolloutworker是否进入receive；OOM先看逐层group是否退化、weight/KV恢复是否同时峰值、host backup是否重叠。失败同步不消费新policy样本；明确可信版本、所有worker结果和更新状态后再恢复。服务重启不代替consumer checkpoint/RNG/样本游标恢复。

## Release、规划、PR 与维护

本页固定官方main `8d7b93fec2eb72ce01f2217472ac1f51b9bce600`；2026-10-12最近可见正式release为[v0.31.0](https://github.com/vllm-project/vllm/releases/tag/v0.31.0)。[Releases](https://github.com/vllm-project/vllm/releases)、[官方文档](https://docs.vllm.ai/)、[Issues/RFC](https://github.com/vllm-project/vllm/issues)、[PR](https://github.com/vllm-project/vllm/pulls)共同核对规划、合入和发布。sleep-backend源码引用RFC #34303是扩展动机，不证明所有durable/CRIU backend已实现。

保留[PR #59772](../../upstream/prs/vllm-project--vllm/PR-59772.md)作为可选ModelExpress依赖/CI测试约束的历史入口；它修测试发现与skip，不能称为训练传权性能提升。相关实现PR需按问题继续`wiki-search-pr "weight transfer layerwise" --engine vllm`，再追head/base和真实调用。

`wiki-update PROJECT vllm-project-vllm`同步[全仓目录](../../upstream/source-map/vllm-project-vllm.md)、[原文](../../upstream/docs/vllm-project-vllm)及讨论；source/factory/transport/worker、模型loader、tests和consumer的train-export必须交叉复核。原文同步完成不等于所有模型或HCU后端验证完成。

## HCU 使用前的独立核对

HCU 侧若通过 vLLM 插件接入，基础包、插件及算子扩展是不同版本；先确认实际 entry points、兼容性 gate、doctor/启动日志、worker 与 model-runner 加载链。稳定参考与活跃开发分支分别核对，不能把官方 main 的新 weight-transfer/sleep API 自动视为较早 HCU 包已支持。HCU-Knowledge 提供当前仓/分支、模型与优化案例；据其固定证据和现场基础包版本继续读实际源码，避免用旧整体 fork 的安装/patch 方式覆盖新插件。

## 固定证据与验证范围

- [README.md](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/README.md)
- [pyproject.toml](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/pyproject.toml)
- [setup.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/setup.py)
- [docs/getting_started/installation/gpu.rocm.inc.md](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/docs/getting_started/installation/gpu.rocm.inc.md)
- [docs/models/supported_models.md](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/docs/models/supported_models.md)
- [docs/training/rlhf.md](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/docs/training/rlhf.md)
- [docs/training/weight_transfer/README.md](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/docs/training/weight_transfer/README.md)
- [docs/features/sleep_mode.md](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/docs/features/sleep_mode.md)
- [vllm/v1/worker/gpu_worker.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/vllm/v1/worker/gpu_worker.py)
- [vllm/v1/core/sched/scheduler.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/vllm/v1/core/sched/scheduler.py)
- [examples/rl/rlhf_async_new_apis.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/examples/rl/rlhf_async_new_apis.py)
- [tests/v1/worker/test_gpu_worker_weight_transfer.py](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/tests/v1/worker/test_gpu_worker_weight_transfer.py)

本页在 2026-10-12 阅读上述固定源码和教程；官方接口、上游测试内容、HCU 分支支持及现场实测分别判断。本轮没有执行 GPU 测试，也不宣称覆盖全部模型或 transport。更新时复核总览、两个机制专题、训练框架适配器、调用方测试与 Skill；普通查询可继续追在线 PR 和固定源码，不能将查询缓存自动升级为共享结论。
