# Skill 与文档的阅读导航

## 内容放在哪里

| 层次 | 职责 | 使用方式 |
| --- | --- | --- |
| `skills/<name>/SKILL.md` | 入口、模式边界、主要顺序、判断和验收要求 | 调用时先读；关键约束不能只藏在参考文档里 |
| `skills/<name>/references/` | 该阶段的详细方法、操作契约、分支排查 | 按下面的模式和触发条件读取；安装时随对应 Skill 完整复制 |
| `docs/` | 跨阶段协议、工具契约、部署安装、整体流程与设计解释 | 从绑定的工程读取；多个阶段共享一份，不复制进每个 Skill |
| `knowledge/` | 官方资料、可复用环境经验、最终模型优化总结及证据 | 通过 Wiki 检索/读取，必要时追 PR 和源码；不能替代现场验证 |
| 任务 workspace | 当前配置、实验、原始日志/trace、看板与中间结论 | 接手和推进时读取；不自动升级成跨任务知识 |

`docs/practices/` 保存多个阶段共用的方法或来源说明。单阶段执行细节放对应 `references/`。一条规则只维护一处详细正文，其他地方链接它并说明何时读取。Skill、docs 是流程方法；Wiki 是被查询的知识和证据。

## 安装后如何定位和读取

六个已安装 Skill 的 `workspace.json.project_root` 指向工程 checkout。工程内 `docs/...`、`knowledge/...`、`skills/...` 均相对于该根目录；Skill 内的 `references/...` 相对于该 Skill 目录。跨 Skill 的阅读链接从工程副本解析，不能把 `../../docs` 当成系统 Skills 目录旁边的文件。

首次使用、换 Agent 或工程升级后，先核对绑定及当前模式，读取本页对应行。安装目录的 Skill/reference 与工程版本必须一致；可用 `python scripts/sync_local_install.py --target <实际Skills目录> --check` 检查。正常轮次沿用已读且未变的规则，只补当前分支，不每轮通读全部文档。绑定失效、文件缺失或本地 Skill 过期应先修复；普通训练任务不为修复安装擅自拉上游或更换远端依赖。

Markdown 链接不会自动将所有文档注入 Agent 上下文。主控在任务计划/看板中记下当前模式、适用指南及未完成证据；委派时交给成员相同入口和当前分支。验收必须核对实际原件和程序门槛，不能用“文档已读”代替完成工作。

## 按模式进入

以下是入口，不是要求一次加载表中所有内容。命中条件时，在作出相应判断或操作前读取详细规则。

| 模式 / 入口 | 开始时读 | 按条件补读 |
| --- | --- | --- |
| [统一主控](../skills/hcu-trainflow/SKILL.md) | [接手与交接](agent-playbook.md)，当前阶段 Skill；持久循环按 [协作契约](collaboration.md) | 需要并行任务时读 [多 Agent](multi-agent.md)；维护主控时读 [维护约定](../skills/hcu-trainflow/references/maintenance.md) |
| 仅接手已有修改并交付，仍用统一主控 | [改动审查与交付](change-delivery.md)，按改动归属选择相关阶段契约 | 不创建训练 TaskSpec/flow-start；用已有证据确定受影响验证，再整理 PR/CI；不将原训练任务的未完成目标关闭 |
| [环境检查与适配](../skills/hcu-train-environment-check-and-adapt/SKILL.md) | [阶段方法](../skills/hcu-train-environment-check-and-adapt/references/workflow.md) 中当前模式部分，[环境发现与验收](environment-discovery.md) | 执行远程任务前读 [远程执行](remote-execution.md)；开始适配读 [容量与并行实验](practices/capacity-and-parallel-experiments.md) 和 [状态验证](training-state-validation.md)；失败读 [适配排障](../skills/hcu-train-environment-check-and-adapt/references/troubleshooting.md)。仅环境检查不进入模型修改 |
| [性能分析与优化](../skills/hcu-train-analyze-and-optimize/SKILL.md) | [证据驱动闭环](../skills/hcu-train-analyze-and-optimize/references/evidence-driven-loop.md)、[性能采集与分析](profiling.md)、[阶段执行契约](../skills/hcu-train-analyze-and-optimize/references/workflow.md) | 通信、Torch 原生、算子建模/同形状对照、数学库 tune 和底层库联动，按 Skill 对应步骤读专项；进入实现验证读 [验证与异常诊断](../skills/hcu-train-analyze-and-optimize/references/validation-diagnostics.md) 和 [状态验证](training-state-validation.md)。仅分析同样要解释热点与上限/未知，但不擅自运行优化实验 |
| [规模扩展与长稳运行](../skills/hcu-train-scale-and-stability/SKILL.md) | 扩容/接管读 [阶段方法](../skills/hcu-train-scale-and-stability/references/workflow.md)、[训练观测](training-observation.md) 与 [状态验证](training-state-validation.md)；仅诊断先读 [故障诊断](../skills/hcu-train-scale-and-stability/references/diagnosis.md) | 按症状读诊断分支和 [知识与源码查证](../skills/hcu-train-scale-and-stability/references/evidence-sources.md)；部署守护再读对应部署契约；诊断不自动扩大为重启或故障注入 |
| [局部 Wiki 搜索](../skills/hcu-engine-wiki-search/SKILL.md) | [查询方法](../skills/hcu-engine-wiki-search/references/workflow.md) 与 [Wiki 命令](wiki.md) 对应部分 | 本地证据不足时在线查 PR，再追最终源码；涉及 HCU 的事实按需联查大知识库，不更新它 |
| [Wiki 与 Skill 更新](../skills/hcu-engine-wiki-skill-update/SKILL.md) | [更新方法](../skills/hcu-engine-wiki-skill-update/references/workflow.md)、[Wiki 更新契约](wiki.md)、[维护关联](../knowledge/maintenance.json) | 修订受影响的 overview/topic/case/Skill/解析器；收尾按 [本机同步](integrations.md#skills账号与升级)。依赖锁变化需另做对应依赖验证 |

每个阶段都有自身交付与复核责任；只有用户要求完整流程时才串起全部阶段。命令以当前 CLI 帮助、实际部署分支和授权为准。

## Hyperloom、GEAK、BBuf 的借鉴内容

- **采用依据与固定源码位置**：[性能方法来源](practices/performance-methods.md)。这是追溯和维护入口，执行时不要求全文阅读三个参考工程。
- **训练优化中的执行方法**：[证据闭环](../skills/hcu-train-analyze-and-optimize/references/evidence-driven-loop.md) 包括证据刷新、三张关联表、候选命中、收益验证与停滞处置；[算子上限迭代](../skills/hcu-train-analyze-and-optimize/references/operator-ceiling-iteration.md) 包括条件上限和实现优先级；[通信专项](../skills/hcu-train-analyze-and-optimize/references/communication-optimization.md) 保留重叠与同步的证据边界。
- **排障中的执行方法**：[故障诊断](../skills/hcu-train-scale-and-stability/references/diagnosis.md) 包括失败条件保留、假设排除、最小复现、有界二分与交叉筛查；适配和优化入口按症状复用。
- **程序落实**：[分析建模](../src/hcu_trainflow/analysis.py) 提供算力/带宽/延迟项与输入校验；其余方法由 Skill 引导执行并提交实际证据，不宣称所有文字方法都已变成自动判断程序。

更新这些内容时同步核对维护关联、入口路由与安装副本。安装校验能发现缺文件、断开的本地文档链接、没有阅读入口的 references 和版本不一致；不能自动证明模型已理解每一条方法或实验已通过。
