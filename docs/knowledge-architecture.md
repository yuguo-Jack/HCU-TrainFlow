# TrainFlow 自带 Wiki 与任务档案

TrainFlow 的可复用知识保存在工程 `knowledge/`，随 Git 提交、克隆和更新。官方实现、通用实践、实际站点配置和测量共同服务三个阶段；下一个任务无需连接上一个任务的 workspace。任务 Store 保存完整实验过程，里程碑后由所属阶段把可复用结论和必要证据整理进工程 Wiki。

| 内容 | 位置 | 保存范围 |
| --- | --- | --- |
| 官方引擎与依赖 | `knowledge/official-*-wiki/` 等现有专题 | 固定源码、教程、PR/review、调用链、优化机制及限制 |
| 通用工程实践 | `knowledge/practices/` | 环境发现、配方核对、调参、数值、恢复的方法，关联真实案例 |
| 跨任务站点知识 | `knowledge/sites/<site-id>/` | 真实硬件/软件/拓扑、环境变量、启动配方、单测基准、异常和恢复经验及其适用条件 |
| 模型与训练经验 | `knowledge/experiments/<case-id>/` | 有复用价值的模型配置、参数对照、关键性能/显存/loss、失败候选、扩 DP 和恢复结果，关联所属站点与源码 |
| 当前任务档案 | `TRAINFLOW_WORKSPACE` | 完整日志、trace、checkpoint、数据、开发 checkout、控制状态、看板、事件和任务 experience/reference |

站点配置和实测数据可以进入本仓 Wiki；这是 TrainFlow 的知识归属规则。外部 Cookbook/目标项目 PR 的发布要求单独处理，不能用它来阻止本站点知识沉淀。凭据、私钥、访问 token 不属于知识内容，始终不入仓。完整海量数据/模型权重也无需复制进知识库。

## 目录和证据

```text
knowledge/
  practices/                 # 跨站点的方法与机制
  sites/
    <site-id>/
      README.md              # 身份、能力、局限、导航和复用入口
      environment.json       # 已观测的环境事实，带时间和来源
      communication.md       # 有效配方与实测解释，可继续增加专题
      evidence/<revision>/   # 本页声明的精选原件，不依赖旧 workspace
      manifest.json          # 入仓证据相对路径、字节数、SHA256、来源/处理方式
  experiments/<case-id>/     # 达到里程碑后整理，不为凑目录创建空案例
```

专题页必须有唯一 `id`、标题、阶段、知识类型、观测/复核日期与验证边界。原命令与最终执行命令、固定源码/镜像/库身份、关键参数、结果、正确性、因果边界、复用前检查和失效触发都应写清。标称值、历史值、本次实测分别表达；“脚本跑完”不能写成环境达标。某站点的 NIC/GID/TC/固定端口等不能成为所有 HCU 集群默认值。

正文使用仓内相对链接；复制所引用的关键原件或注明为选摘及完整来源哈希。完整归档仍可保留在任务 workspace，但仓内页不能只有 `objects/<hash>` 或任务绝对路径，导致另一个用户无法理解或核验主要结论。`manifest.json` 校验已经声明的证据，并不证明文字推理正确。两个实证目录在 `.gitattributes` 中关闭换行归一化，避免 Windows/Linux checkout 改变原件哈希；提交前也应检查 Git 索引中的字节与清单一致。

## 统一检索，直接复用现有 CLI

```bash
hcu-trainflow --workspace NEW_TASK wiki-search "RCCL RoCE alltoall" --project TRAINFLOW_PROJECT --online-pr off
hcu-trainflow --workspace NEW_TASK wiki-read sites/cfs-roce-bw1000/communication --project TRAINFLOW_PROJECT
```

`wiki-search` 索引整个 `knowledge/**/*.md`，因此官方页、实践、站点及模型案例都能被搜到。站点事实不一定属于某个引擎；先按问题跨引擎搜索，再定向过滤，避免 `--engine megatron` 把通信现场记录排除。JSON/日志/图像由命中文章链接打开，未把所有原件全文自动索引的内容冒充可搜。重点术语、别名、变量名和数值解释须出现在 Markdown。

任务内细节仍用 `experience-search`、`experience-read`、`reference-query`。它们搜索所选 Store，不自动搜索所有 workspace。普通检索不改上游、不重新测量、不执行配方；知识命中也不是健康/性能门槛通过。

## 里程碑更新协议

1. 保存完整任务证据和现有 experience/reference，准确记录真实观测时间与上下文。
2. 有效配方、重要优化、显存/loss、故障/恢复或 Cookbook 交付形成稳定结论时，所属阶段自主更新工程 Wiki；不能只更新任务看板。失败与限制同样保留。
3. 选择证据，复制到仓内并登记哈希；将原始文件与衍生摘要分开，摘要说明转换与完整原件哈希。新增测量保留旧版本，当前入口链接到最新适用记录。重新阅读不刷新测量日期。
4. 与同站点总览、专题、相关模型案例及 Skill 交叉复核。配置/驱动/镜像/库/网络策略改变时标记受影响结论待复核，不能仅刷新数字或目录日期。
5. `python scripts/validate_knowledge.py` 核对页 ID 和证据。用另一个全新 Store 搜索、打开正文与关键证据；确认不依赖原任务目录，再按当前授权提交工程。

官方上游变化继续使用现有 Wiki update 协议；站点记录根据新观测/里程碑维护，不虚构远程自动采集。工作流可自主维护这些局部知识；普通任务不更新 HCU 大领域知识库，也不自动替换活动训练依赖。
