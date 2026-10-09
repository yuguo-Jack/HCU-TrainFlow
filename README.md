# HCU-TrainFlow

## 面向 HCU 的大模型训练适配、优化与运行工作流

HCU-TrainFlow 将本地主控 Agent、远程执行、可追溯证据和训练引擎官方 Wiki 连接起来，用于预训练、SFT 与 RL 后训练。支持只检查环境、只分析模型性能或只诊断故障。

**当前版本 v0.2.0。** 本地任务、分析、数值检查、事件重放及 Wiki 更新流程有自动化回归，TraceLens 报告已接入并用合成 trace 验证；远程 HCU 训练、站点容错、飞书送达和具体 Agent 运行时唤醒仍需在用户提供的环境中接入验证。详见 [能力范围](docs/capabilities.md)。

## 核心组成

- **三个训练 Skill**：环境与模型适配；性能分析、优化和验证；扩容、容错衔接和故障诊断。成果交付属于各自流程。
- **两个 Wiki Skill**：官方引擎检索；官方知识与相关工作流用法更新。
- **证据与执行工具**：任务上下文、内容哈希、资源租约、可重放事件、显式命令卡、不可变代码快照及传输校验。
- **分析与质量工具**：真实并行组采样、端到端墙钟覆盖、非通信热点上限建模、全设备验收、逐轮正确性与阶段 loss 检查。
- **持续监测**：远端独立 watcher、停滞/恢复超时检测、事件 inbox、曲线报告及部署时配置的 Agent bridge。
- **局部官方 Wiki**：Megatron-LM/Core、Bridge、Energon；独立的 Transformer Engine 和 cuDNN Frontend 源码与教程专题；Primus、MindSpeed、LoongForge 机制；其他常用 SFT/RL 引擎入口。
- **第三方集成**：TraceLens 报告；三个 Hygon 算子 Skill 的安装源；可选 HCU-Knowledge。使用统一目录和固定版本清单。

## 安装与首次运行

```bash
git clone https://github.com/yuguo-Jack/HCU-TrainFlow.git
cd HCU-TrainFlow
python -m pip install -e ".[test]"
python scripts/bootstrap_thirdparty.py
python -m pip install -e thirdparty/TraceLens
hcu-trainflow --help
hcu-trainflow demo .work/demo-first
hcu-trainflow wiki-index .
hcu-trainflow wiki-search "EP overlap 显存" --engine megatron
python -m pytest -q
```

Windows 和 Linux 均使用 Python 3.10+。demo 会运行一个 CPU 子进程，并使用合成训练数据演示分析、loss 检查、监测和断线重放；不需要 GPU，不是性能基准。重复演示请使用新的目录。

安装五个工作流 Skill 和三个 Hygon 算子 Skill，例如在 PowerShell 中：

```powershell
python scripts/install_skills.py --with-kernel-skills --target "$HOME/.codex/skills"
$env:TRAINFLOW_PROJECT = (Get-Location).Path
$env:TRAINFLOW_WORKSPACE = "D:/trainflow-work/my-task"
```

现有不同版本默认不覆盖；更新时显式 `--replace`，安装器会先备份。省略 `--with-kernel-skills` 可只安装五个工作流 Skill。HCU-Knowledge 当前需要仓库权限，按需单独启用或复用已有安装；默认 bootstrap 只获取两个公开依赖。详见 [第三方依赖与安装](docs/integrations.md)。

## 目录

```text
src/hcu_trainflow/      CLI、任务状态、证据、执行、分析、质量、监测、Wiki
skills/                五个可安装 Skill
knowledge/             公开官方 Wiki、固定源码锁及维护关联
docs/                  安装、契约、工作流、部署与维护说明
examples/              合成输入、命令卡和部署模板
scripts/               Skill 安装与知识完整性校验
thirdparty/            版本清单、安装说明及忽略提交的依赖 checkout
tests/                 本地回归
.work/                 默认私有状态与可重建索引（不提交）
```

所有任务现场、数据、原始日志、源码缓存、工作 checkout 与凭据放到独立私有工作区。代码仓只发布工具、公开知识和合成示例。

## 文档

- [快速开始与 CLI](docs/quickstart.md)
- [TraceLens、算子 Skill 与 HCU-Knowledge 接入](docs/integrations.md)
- [三个工作流](docs/workflows.md) / [架构](docs/architecture.md)
- [性能分析与热点建模](docs/profiling.md)
- [远程执行](docs/remote-execution.md) / [长训监测](docs/operations.md)
- [官方 Wiki 索引](knowledge/README.md) / [更新协议](docs/wiki.md)
- [版本范围与后续验证](docs/capabilities.md) / [贡献与公开边界](CONTRIBUTING.md)

本工程借鉴 Hyperloom 的证据与编排思想、BBuf 的分析/故障重现方法，并复用 TraceLens 接口。具体来源和许可边界见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
