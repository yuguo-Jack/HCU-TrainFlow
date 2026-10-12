---
id: ecosystem/primus
title: AMD Primus：配置、后端补丁、并行与恢复
engine: primus
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected source, official documentation and related PR reading; no HCU runtime
  validation
sources:
- source: amd-agi-primus
  path: README.md
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: da7a135294ce239c33abefaeddf09aa2efc066cee6a8c887f66de5fbe0528e2d
- source: amd-agi-primus
  path: .gitmodules
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 3a6fe9a0aabd4d2d6d3b323171eec4c451c21001395a98d3b725279b91a61fc5
- source: amd-agi-primus
  path: pyproject.toml
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 9210165bd9a0b88af34750e9e9e79a51b79f5857bb49cd169587749fe8b866ea
- source: amd-agi-primus
  path: docs/01-getting-started/release-notes.md
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 8b2104077479072816058568dffd575a4c5f39a475cb717b41690704d5945143
- source: amd-agi-primus
  path: docs/02-user-guide/configuration-system.md
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 75400ddb115e87b357745d06f73a4e086e6f750dc3db352e5205444fafdc89a9
- source: amd-agi-primus
  path: docs/02-user-guide/megatron-lm-training.md
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: e1c828a5bb9b42ad164a0962034704d60d59ed878a80866a3f7ae284f207bb22
- source: amd-agi-primus
  path: primus/core/runtime/train_runtime.py
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 63c969944700b1d63d2393a9e96cb79ff373f25541f6f1e1fef060bdeb57de1c
- source: amd-agi-primus
  path: primus/core/patches/patch_runner.py
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 330529f72986ec1d291222b0c3fbf556863ca03b7e72c986cba1f2ac081a645e
- source: amd-agi-primus
  path: docs/04-technical-guides/fault-tolerance-and-elastic-training.md
  commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
  sha256: 95a139372f53910555884c391081d1a6da9cae86901aadd20ca4ce32b174be00
---

# AMD Primus：配置、后端补丁、并行与恢复

## 1. 定位与 HCU 参考边界

Primus 为多个训练后端提供统一配置、启动、补丁、测试及性能/运维入口。Megatron-LM、Megatron Bridge、TorchTitan、MaxText 等是它调用的后端；Primus 本身不是这些训练循环的全部实现。适合借鉴的是 ROCm 场景的启动契约、后端参数传播、编译与通信调度、重算及优化库接入。

当前父仓 `.gitmodules` 的 Megatron 路径指向 **NVIDIA/Megatron-LM**，不存在一个名为 `Primus-LM` 的独立 gitlink。产品或包描述出现 Primus-LM，不能据此指定另一仓 HEAD 作为实际依赖。任务采用的 HCU Primus-LM patch、AMD Primus 父仓和它锁定的官方 Core 应分别记录；通过 HCU-Knowledge 找当前可读 HCU 仓与活跃分支，再对照本页机制。

## 2. 工程目录与问题入口

| 路径 | 职责与继续阅读位置 |
| --- | --- |
| `runner/primus-cli`、`runner/helpers/` | direct/container/Slurm 启动、变量透传、设备和网络选择；多机脚本失效先查这里 |
| `primus/core/launcher/` | Python train/benchmark/projection/preflight 参数及命令组装 |
| `primus/core/config/`、`primus/configs/` | YAML 继承、module/model/platform 配方；查最终值而非只查某个 YAML |
| `primus/core/runtime/train_runtime.py` | `PrimusRuntime` 统一配置、环境、adapter、trainer 生命周期 |
| `primus/core/patches/` | 补丁 registry、上下文、条件、优先级及异常策略 |
| `primus/backends/megatron/` | Megatron trainer、模型及按功能划分的 patches；继续到实际被替换 Core/TE 符号 |
| `primus/backends/transformer_engine/` | Primus 的 TE overlap 对应实现，不是任意 TE 包的通用别名 |
| `tests/unit_tests/`、`tests/runner/` | 配置、补丁、版本契约与 launcher 测试；分布式性能仍需真实设备 |
| `docs/01-getting-started` 至 `06-developer-guide` | 安装、发布、训练、并行、优化、checkpoint 与开发测试 |

## 3. 安装、子模块及版本

`pyproject.toml` 要求 Python >=3.10，提供两个入口：`primus-cli` 是统一 Bash runner，`primus` 是 Python 命令。先按官方 bare-metal 或容器安装指南确认实际 Torch/ROCm/TE/Primus-Turbo，再安装父仓与后端；仅装 Python 壳不能证明后端扩展可用。递归 clone 或 submodule update 应保留父提交及 gitlink，避免“父仓固定、子仓浮动”。

本页父仓 `ab8735564c4cc3bb7c0475146057eee8dae4c650` 锁定：

| gitlink | 实际固定提交 |
| --- | --- |
| `third_party/Megatron-LM` | `d3528a21301db2d12e92912b3ec025dc8a2ed4d6` |
| `third_party/Megatron-Bridge` | `9577b1280eaadd60b9d7b0ce6df09ac80e87e323` |
| `third_party/torchtitan` | `73a0e6979dd10b6b1904098eb3c8f62c18ab87ce` |
| `third_party/maxtext` | `07c240fa070b9ef288e40deb60289f8057c553b6`，URL 为 ROCm/maxtext |

官方使用指南推荐 `rocm/primus:v26.8` 配合 `release/v26.8`，这是发布配对；本页精读 main 与该发布分支不同。指南还说明容器实际使用挂载的 host checkout，不能把镜像内烘焙代码版本当成正在执行版本。HCU 用现场镜像/DTK 的配套工程，核对 `import` 路径、git revision、共享库和 backend 日志。

## 4. 配置、运行与测试

官方新的训练入口是 `./runner/primus-cli ... -- train pretrain --config ...`，已删除旧的 `examples/run_*` launcher。container、direct、Slurm srun 使用同一 YAML，但容器环境变量并非全部自动透传：例如官方指南明确 `PYTORCH_CUDA_ALLOC_CONF` 需要显式 `--env` 或 container 配置；host export 不能证明容器收到。先读目标提交 CLI help 和实际 HCU 启动方式，不照抄 MI 系列设备/NIC 默认。

`extends` 按相对路径递归合并，后列配置覆盖前列，再应用自身配置。module 与 model 配置有独立冲突检查，experiment overrides 及 CLI override 再形成最终值。`work_group/user_name/exp_name/workspace` 标识工作路径；platform 省略时的默认平台不代表 HCU。top-level `env:` 由 runtime 在 backend import 之前导出；嵌套 module 的同名字段不自动获得该语义。

测试按配置解析→patch 单测→选定后端短训练→多 rank 通信/恢复展开。日志要能证明配置、设备隔离、backend、补丁和实际算子分发；`--dry-run` 只显示启动计划，`--export_config` 的参数存在也不能替代当前 runtime 是否真正写出了文件的检查。成功标准是实际 step 推进、数值基线、预期同步和可恢复 checkpoint，不能以 runner 返回或 import 成功代替。

## 5. 模型、数据与状态契约

模型 YAML 决定结构、dtype、attention/MLP、并行和 optimizer。保留模型真实性：缩层只用于明确的容量目的，不把配方误写成新模型；数据集类型、tokenizer、sequence length、有效 token、GBS/MB/梯度累计、shuffle 与恢复位置随实验保存。distributed optimizer 与 FSDP2 的约束不同，官方 guide 指出 FSDP2 不能照用其 distributed optimizer / parameter gather overlap 组合。

参数 gather、grad reduce、重算、FP8/FP4、TE 缓存及 checkpoint 都影响状态生命周期。patch 被启用不意味着所有 dtype、MTP、VPP、共享参数、graph 和恢复组合都支持，必须按对应代码与单测矩阵选取。

## 6. 从配置到实际实现

`PrimusRuntime` 读取配置→导出 top-level env→初始化环境/分布式→选择 backend adapter→`prepare_backend` / `convert_config`→`build_args` 补丁→trainer 构造→`setup` 补丁与 setup→init→`before_train` 补丁→train→`after_train` 与 cleanup。补丁上下文携带 backend/version/model/module/runtime_state，registry 依条件和优先级选择；`PRIMUS_PATCHES=none` 可关闭，指定 ID 可限制范围。

一个容易忽略的行为：通用 `run_patches` 默认记录导入/执行异常，只有 `stop_on_error` 才传播；本轮 runtime `_run_phase_patches` 没有传这个选项。因此“某 patch 函数会 raise”不能证明整次训练会失败。采用性能特性时应检查成功日志、被替换函数与 trace；避免补丁失败后普通路径继续训练却被记作优化已生效。

## 7. 两类重点性能机制

- [编译与 DDP/TP overlap](topics/primus-compile-overlap.md)：为什么参数 gather hook 要避开编译区域，TE1/TE2 路径如何选择，如何验证同步仍正确；关联 [已有案例](cases/primus-compile-ddp.md)。
- [选择性重算与内存取舍](topics/primus-recompute-memory.md)：全局层 ID、decoder/MTP、低精度 checkpoint 的正确性边界；关联 [已有案例](cases/primus-layer-recompute.md)。

这些都应从实际瓶颈进入：减少 CPU graph break 或暴露通信、用少量重算换 HBM 容量，收益与额外 buffer、计算和调度成本一起测。另可追 Primus-Turbo、grouped GEMM、router backward，但不要因特性名称相同就认为 HCU 已支持。

## 8. 数值、诊断与恢复

compile 有效但步时不降时，查 graph breaks、hook 所属 bucket、通信是否已经隐藏；overlap 卡住时检查 rank group、collective 顺序、启停 hook 和共享参数；重算异常时检查全局层 offset、RNG、低精度 context 和 MTP。性能比较保持数据/GBS、热身和稳定窗口一致，阶段验证 loss 与梯度，不频繁以长训替代局部回归。

容错文档区分 scheduler + checkpoint 重新拉起、优雅退出、Megatron 进程内重启及 TorchTitan torchft 等；后者还有可选依赖，不是所有 backend 的共同能力。HCU 任务以既有 Cluster Manager 为主要恢复 owner，不能同时让 scheduler、engine 内部重启和 Agent 各自改机器池/重启。恢复验收必须核对模型、optimizer、scheduler、RNG、数据位置及恢复后的持续推进。

## 9. PR、发布与后续更新

官方发布说明、[Releases](https://github.com/AMD-AGI/Primus/releases)、[PR 列表](https://github.com/AMD-AGI/Primus/pulls) 是持续变化入口；不能把 main 某项实现直接列成 v26.8 已发布。当前值得联查的固定 PR：[#1237 保留 HIP_VISIBLE_DEVICES](../prs/AMD-AGI--Primus/PR-1237.md) 防止 runner 重置共享设备选择；[#1240 router backward BF16](../prs/AMD-AGI--Primus/PR-1240.md) 是默认关闭且保留精度 fallback 的局部机制，需读其 Core/TE 依赖和测试。

[全仓源码导航](../source-maps/amd-agi-primus.md)、[官方文档原文](../upstream-docs/amd-agi-primus/)用于继续深入。`wiki-search-pr "问题或符号" --engine primus` 可找未写案例的线上 PR，随后追固定代码。更新父仓时必须联查 gitlink、runner 环境契约、runtime/patch API、模型 YAML、两篇专题和案例，不能只刷新 README。

## 固定证据与复核范围

- [README.md](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/README.md)
- [.gitmodules](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/.gitmodules)
- [pyproject.toml](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/pyproject.toml)
- [docs/01-getting-started/release-notes.md](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/docs/01-getting-started/release-notes.md)
- [docs/02-user-guide/configuration-system.md](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/docs/02-user-guide/configuration-system.md)
- [docs/02-user-guide/megatron-lm-training.md](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/docs/02-user-guide/megatron-lm-training.md)
- [primus/core/runtime/train_runtime.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/primus/core/runtime/train_runtime.py)
- [primus/core/patches/patch_runner.py](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/primus/core/patches/patch_runner.py)
- [docs/04-technical-guides/fault-tolerance-and-elastic-training.md](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/docs/04-technical-guides/fault-tolerance-and-elastic-training.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
