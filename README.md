# HCU-TrainFlow

## 面向 HCU 大模型训练的全流程智能体协同工作流

An agentic workflow for end-to-end large-model training adaptation, optimization, and resilient scaling on HCU.

给出模型、环境和目标，由本地主控 Agent 协调适配、分析与优化、扩容验证及长训容错。每轮以实际证据推进，经过独立复核和修正；人在看板中补充意见，Agent 读取、回复并调整后续工作。适用于预训练、SFT、RL，以及 Torch 原生的视频生成、VLA、世界模型等训练，也支持只检查环境、只分析性能或只诊断故障。

**当前源码版本：`0.4.0.dev0`，开发中，尚未发布。** 协作循环、证据检查和文件交互已有本地自动化验证；正在结合真实 HCU 环境验证远程执行、模型适配、性能分析与训练观测。完整训练、Agent 运行时接续及站点容错仍需逐项验收。当前不能视为拿到任意集群就可无人值守运行的成品。见 [能力与验证边界](docs/capabilities.md)。

## 如何开始

安装后，在支持 Skill 的 Agent 中说：

> `$hcu-trainflow` 在我提供的环境中，对指定模型进行适配、性能优化和大规模验证。已有启动脚本、数据路径和资源范围如下……

主控会建立任务、确认缺失的关键条件，然后按阶段推进。已知环境和授权可以复用；正常步骤持续执行，遇到权限缺口、数值异常、收益平台期或需要专家判断时再提出具体问题。内部任务文件和命令由 Agent 管理。

## 工作流总览

[![HCU-TrainFlow 工作流总览：环境适配、性能优化与阶段验收、扩容长训；多 Agent、独立复核、远端执行和知识沉淀贯穿全程](docs/assets/workflow-overview.png)](docs/assets/workflow-overview.png)

[原尺寸图片](docs/assets/workflow-overview.png) · [可编辑流程图与验收规则](docs/workflow-map.md)

优化先权衡并行切分、显存峰值与余量、通信和实际吞吐，再用端到端 profile 推进系统调参与算子优化。保持初始数值基线；逐轮做局部正确性和性能回归，稳定阶段再验 loss。对累计 ≥90% 端到端热点中的非通信算子评估上限与效率。优先复用当前 HCU 工程配方和已有融合实现，按需使用三个 Hygon 算子 Skill。

同一优化阶段包含 [Torch 原生训练专项](skills/hcu-train-optimize/references/torch-native-training.md) 和 [通信优化专项](skills/hcu-train-optimize/references/communication-optimization.md)：覆盖数据与 host 开销、compile/断图/重编译、前后向、DDP/FSDP，以及通信暴露、overlap、通算融合和资源竞争。环境适配、扩 DP 与容错共用既有流程。资源不足时默认缩 layer 跑通或筛机；用户明确允许缩维时记录授权范围与模型差异。扩规模前先验收选定的完整配置，再逐级扩 DP 域并复核性能、显存和训练语义；缩维代理的结果不能声称为原完整模型验证。

完整阶段、优化回路、多 Agent、远端执行、长训守护和知识更新见 [工作流全景](docs/workflow-map.md)，其中列明阶段证据门槛及对应源码。

## 如何与 Agent 协作

每个任务在私有工作区生成：

```text
collaboration/<task>/BOARD.md       进度、待决问题、轮次复核和证据入口
collaboration/<task>/GUIDANCE.md    人的评论、回答和优先级调整
collaboration/<task>/QUESTIONS.md   问题、Agent 回答和追问
```

在 `GUIDANCE.md` 写意见，默认每 **5 分钟**采集一次；主控在后续实验与推进前检查已采集的指导并记录处理结果。需要立即生效时可让 Agent 刷新，或运行 `flow-board` / `flow-watch --once`。文件轮询本身不运行模型。会话关闭后的自动接续需要部署 Agent bridge；本机离线时远端守护和原有容错继续运行。详见 [协作循环与文件交互](docs/collaboration.md) 和 [长训守护](docs/operations.md)。

解释性问题可写入 `QUESTIONS.md`，主控按同一周期读取并在原问题下回答，保留问题与回答版本。问题不自动改变资源或重启授权；采集器不会代替离线的 Agent 生成答案。

主控在同一周期检查已登记的可重建缓存，默认只生成清理计划；明确启用的部署策略可自动保留最近3代并清理过期代次，活跃作业与证据继续保护，老目录不会自动删除。模型/实验 context 换代时使用独立观察 Store，重新核对全部成员监测及独立 sentinel。见 [工作区维护与观察交接](docs/workspace-maintenance.md)。

## 多 Agent 如何协同

主控根据模型与实测热点动态生成任务和 Agent 分工，不预设固定算子名单。环境与启动配方核对、系统分析，以及不同算子的详细分析和优化均可并行；某个算子具备实施条件后即可优化，无需等待其他算子的分析全部完成。相关 Agent 可提问、答复、共享发现和报告阻塞，消息与处理回执保存在同一任务中。

下游只消费已验收的结果；共享 GPU 的测量、耦合代码修改、集成和阶段 loss 验证由主控安排。任务领取、真实 Agent 会话、返回报告和验收分别记录，避免重复派发或把“已经返回”误当成“已经完成”。详见 [任务拆解与 Agent 协同](docs/multi-agent.md)。

## 知识如何参与工作流

**HCU-Knowledge 是完整安装的必需组成，贯穿三个阶段。** 按问题检索硬件、工具、HCU 工程、配方、优化与故障案例，并联查私有训练经验和官方引擎 Wiki；本地证据不足时继续在线搜索 PR、阅读讨论并追到对应版本的源码和底层依赖。必需安装不表示每个命令都强制查询。

局部官方 Wiki 可按问题和版本变化自主更新，并联动复核相关 Skill、命令与解析器用法；普通查询或训练任务不附带更新 HCU-Knowledge，也不会自动替换正在运行的训练依赖。可复用的站点配置、实测基准、性能/loss 和故障经验沉淀到本仓 `knowledge/sites/`、`knowledge/experiments/`，精选证据随仓提交，跨任务直接检索。完整任务档案留在 workspace；外部 Cookbook 的发布要求单独处理。参见 [知识归属与跨任务复用](docs/knowledge-architecture.md)。详见 [知识检索与维护](docs/wiki.md) 和 [训练经验记录](docs/experience-knowledge.md)。

## 安装

Python 3.10+、Git、Git LFS，以及 HCU-Knowledge 仓库读取权限。使用 SSH/Docker/Slurm/K8s 时需对应客户端与资源权限；HCU 训练软件由实际环境提供。

```bash
git clone https://github.com/yuguo-Jack/HCU-TrainFlow.git
cd HCU-TrainFlow
git lfs install
```

PowerShell 中完成依赖、知识库本机索引和 **11 个 Skill** 的安装（六个 TrainFlow、三个算子、两个 HCU 知识库）：

```powershell
python scripts/setup_trainflow.py --skills-dir "$HOME/.codex/skills"
$env:TRAINFLOW_PROJECT = (Get-Location).Path
$env:TRAINFLOW_WORKSPACE = "D:/trainflow-work/my-task"
```

已有独立知识库时加 `--knowledge-root /path/to/HCU-Knowledge`，复用原件、索引与配置，不重复克隆、不拉取其上游更新。升级 Skill 使用 `--replace`，旧版本先备份到扫描目录之外；旧 prepare/operate 名称自动迁移。缺少私有仓权限、LFS 原件或索引不可用时安装会报告未完成；不会静默跳过。飞书等在线能力另用本人账号授权。详见 [依赖与安装说明](docs/integrations.md)。

## 本地验证与阅读入口

```bash
hcu-trainflow --version
python -m pip install -e ".[test]"
hcu-trainflow collaboration-demo .work/collaboration-first
hcu-trainflow demo .work/analysis-first
python -m pytest -q
python scripts/validate_knowledge.py
```

两个 demo 使用合成输入，分别演示协作协议和训练分析/监测；不需要 GPU，不构成真实训练验证。每次演示使用新目录。

| 目录 | 内容 |
| --- | --- |
| `skills/` | 统一协作入口、阶段流程和 Wiki 检索/更新 |
| `src/hcu_trainflow/` | 持久任务、复核循环、执行与证据、分析和监测 |
| `knowledge/` | 官方训练引擎与生态 Wiki、固定来源、维护关联 |
| `docs/` | 协作约定、安装、契约、部署及验证说明 |
| `examples/`、`tests/` | 合成示例与本地回归 |
| `thirdparty/` | 依赖清单和忽略提交的工具 checkout |

任务源码、完整日志/trace/checkpoint、数据与看板保存在独立 workspace；默认 `.work/` 忽略提交。工程 Wiki 同时包含官方知识、通用实践、实际站点和模型案例及精选证据；凭据、私钥和 token 不入仓。

- [工作流全景](docs/workflow-map.md) / [协作循环](docs/collaboration.md) / [多 Agent 协同](docs/multi-agent.md) / [三个阶段工作流](docs/workflows.md)
- [快速开始与 CLI](docs/quickstart.md) / [架构](docs/architecture.md)
- [性能分析](docs/profiling.md) / [远程执行](docs/remote-execution.md)
- [真实训练观察](docs/training-observation.md) / [离线训练图表](docs/training-dashboard.md) / [缓存维护与观察换代](docs/workspace-maintenance.md)
- [官方 Wiki](knowledge/README.md) / [搜索与更新](docs/wiki.md) / [私有训练经验与 Cookbook 记录](docs/experience-knowledge.md)
- [贡献与公开边界](CONTRIBUTING.md) / [参考工程](THIRD_PARTY_NOTICES.md)
