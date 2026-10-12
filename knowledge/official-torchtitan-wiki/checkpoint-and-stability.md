---
id: official-torchtitan-wiki/checkpoint-and-stability
title: TorchTitan Checkpoint、恢复语义与长稳训练
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
  path: torchtitan/components/checkpointer/README.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: a385b4f49f7e170b6f4cbd5acf888aaad140bc5cc6b720789c5252def5c3a856
- source: pytorch-torchtitan
  path: torchtitan/components/checkpointer/base.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: b5c261173bffe3a60a01fe708dd4cc77526b1ad80ede8fd882dd27abe960a3a7
- source: pytorch-torchtitan
  path: torchtitan/components/checkpointer/dcp.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 04e293b4fe60ef655b13989198f48c2fabb480a8741704cf7de2cc718225be30
- source: pytorch-torchtitan
  path: torchtitan/components/checkpointer/torch_checkpointing.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 6e26f9773054379b2f63f29347ac764734e9e3bd0b435e4dd7a74b15ddcf9e6d
- source: pytorch-torchtitan
  path: torchtitan/components/optim/ema.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: 25adab00ead2846704bbf6bf1b2fd9560d6e80008bc2048c2fad10a6116be4f8
- source: pytorch-torchtitan
  path: torchtitan/experiments/torchft/README.md
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: d46632a55b147e5085c3ff1e0e05fb00a6ceb2be6001dabf102759fb63a87572
- source: pytorch-torchtitan
  path: torchtitan/trainer.py
  commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
  sha256: e7a7162304a1741cfa86ef7969d7619f985f2263f9aace617bdc6955185c41f4
---

# TorchTitan Checkpoint、恢复语义与长稳训练

## 恢复与导出必须区分

TorchTitan 有 DCP 和其他 Checkpointer 实现；统一接口不意味着异步和存储行为完全一致。恢复应包含模型、optimizer、scheduler、trainer step、数据游标及适用的 RNG/EMA 状态。只导出模型给推理或 HF 转换，不能证明训练可无损续跑。

`last_save_model_only` 当前默认 True，最后一份导出可能不具备完整恢复状态。`export_dtype` 影响模型导出，不等价于训练内部 dtype。接管长训前明确哪一份是完整恢复点，不能根据目录时间最新就自动选择 model-only 文件。

## 加载优先级与兼容

存在有效训练 checkpoint 时，续训路径优先于 HF 初始权重；`initial_load_path`、`initial_load_in_hf` 与 `hf_assets_path` 的作用不同。HF 模型转换需要与实际模型 flavor、参数 FQN、切分和 dtype 对齐。`exclude_from_loading` 用于明确的 warm start，不适合作为故障恢复中悄悄忽略状态的办法。

新增 EMA 时可能需要首次冷启动其状态；后续完整恢复必须恢复 EMA，不能永久排除。改变 PP/TP/FSDP 布局应验证 checkpoint reshard 与参数名称，而不仅验证 load 没报错。

## 异步保存也有状态所有权

CPU staging 完成和持久化完成是不同事件。`maybe_wait_for_staging` 防止原始状态修改早于快照完成，`maybe_wait_for_saving` 等待后端保存结果。进程退出、下一次覆盖或清理目录之前必须知道哪个 future 已完成；看到输出目录不代表可恢复。

同时记录保存吞吐、CPU pinned memory、共享文件系统延迟和训练 step 抖动。增加异步 overlap 可能提高 Host 内存峰值，也可能让多个保存排队；应以完整恢复测试和任务墙钟决定设置。

## 恢复验证流程

1. 保留固定源码、依赖、有效配置和一个完整 checkpoint；短跑到确定 step，记录下一批数据标识、LR/optimizer step 和质量指标。
2. 正常停止并恢复，对比参数、optimizer/scheduler、样本游标与后续数值；避免把正常首次初始化与恢复初始化混合。
3. 在隔离资源上再验证进程失败、节点退出或存储异常时，既有容错的检测、隔离、恢复选择与重新拉起。
4. 恢复后检查有效训练进度、吞吐/显存、loss、非有限值和重复/跳过数据；任务“有进程”不是恢复成功。
5. 清理只在阶段/容量节点进行，保留最后可靠完整恢复点和验收证据，不删除 in-flight staging/save 使用的路径。

## TorchFT 的适用范围

官方 TorchFT 集成是持续演进的实验路径，通过 replica groups、Lighthouse/quorum 和状态传递支持部分失败后的继续运行，主要面向复制权重的 DDP/HSDP 语义。它与启动一个普通 HSDP job 的 topology 和故障语义不同；DiLoCo 等模式还改变同步/优化过程，需单独验证训练质量。

HCU 任务仍以已经部署的 Cluster Manager/容错系统为恢复控制方。若引入 TorchFT，先确定故障边界和唯一重启/恢复所有者，避免外层重复杀进程或两个系统同时加载/重启。官方命令中的设备变量、lighthouse 默认、配方字段和通信后端需按现场确认；某些 README 可能保留旧 CLI，源码解析器优先。

长期监控同时覆盖心跳、step/token 进度、loss/grad norm、吞吐与内存趋势、恢复尝试和 checkpoint 新鲜度。本机离线时远端既有监控和容错继续工作，恢复后主控核对原操作状态再接续，见 [运行与容错](../../docs/operations.md)。

## 固定证据与使用边界

本页以官方主线 `65aaaa960698ab5d6e98c874177b41b9c30e9c58` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [torchtitan/components/checkpointer/README.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/components/checkpointer/README.md)
- [torchtitan/components/checkpointer/base.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/components/checkpointer/base.py)
- [torchtitan/components/checkpointer/dcp.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/components/checkpointer/dcp.py)
- [torchtitan/components/checkpointer/torch_checkpointing.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/components/checkpointer/torch_checkpointing.py)
- [torchtitan/components/optim/ema.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/components/optim/ema.py)
- [torchtitan/experiments/torchft/README.md](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/experiments/torchft/README.md)
- [torchtitan/trainer.py](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/trainer.py)
