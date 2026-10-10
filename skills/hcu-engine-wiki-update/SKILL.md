---
name: hcu-engine-wiki-update
description: 更新局部官方训练 Wiki、PR review 与依赖锁，并复核受影响的 Skill、命令和解析器，保持可追溯知识与用法。
---

# 训练引擎 Wiki 与工作流维护

维护本工程官方 Wiki 和随源变化的工作流用法。它可以由训练任务按需主动调用；不替代或触发 HCU 大知识库 update。

## 更新协议

1. 检查公共 GitHub/文档权限、限流与实际访问，不把 404 当成已删除。读取 knowledge/sources.json 与已有 observed/reviewed 游标。
2. 先读项目 `docs/wiki.md`。`wiki-update PROJECT SOURCE` 依次检查完整树、document_globs 新文档、PR/讨论与登记源码；也可单独使用 wiki-inventory / wiki-sync-docs / wiki-sync-prs / wiki-refresh。重复运行续完 pending，检查所有阶段错误。未监测的新文件从完整树发现，按最新 commit 用 wiki-triage 记录 knowledge-added/not-relevant/deferred，不能只抓 README 宣称全仓无变化。web 来源生成内容指纹，不能当 Git SHA；TE/cuDNN 同时检查代码与官方教程。
3. PR 来源页保存描述、普通评论、行内评论、独立 review 顶层状态/正文、文件列表及原始 JSON。首次增量发现默认最近 30 天，已保留历史 PR 每七天重新查讨论；需要扩大范围用 --since，不能称已覆盖全部历史。主动按问题 wiki-search-pr 补重要未收录 PR，再 wiki-pr 和 wiki-code 追最终代码；可显式 --retain-project 纳入公共来源页。缺 patch/分页/权限时保留失败并补证据，不将标题或初始描述直接编成案例。
4. 比较实际 active ref 与已锁版本，处理 submodule gitlink，不用子仓 HEAD 偷换。发布计划、open PR、merged main、released 和运行可用分开。
5. 对每个 affected overview/topic/case 深读新实现、改原因、触发条件、测试、限制和回退，同仓交叉结论一起修正。必要时扩充关联的第三方优化采用/退役记录。
   PR 描述、review 或 diff 更新即使没有主干源码变化，也检查 wiki/pr-review 待办；对关联页复核后 wiki-review-pr 留下对应原始 artifact 与页面哈希的回执。
6. 按 knowledge/maintenance.json 同时检查 Skill、环境命令、TraceLens 接口、日志字段、profile 参数和容错步骤。HCU 命令可以依托大知识库当前内容或自主看最新工程源码；任务所用 HCU 模型脚本、其引入的环境配置、launcher 或依赖变化时，一并复核 adapt/optimize 的用法和任务配方。本仓 `knowledge/sites/` 同步维护实际站点配置与配方及关键证据；不能只更新官方 Wiki 文本。
   新增或升级 HCU Primus Turbo、UCCL、UltraEP、MoonEP 等库时，复核 optimize 的 `references/hcu-library-integration.md`、通信专项及 adapt/fault-tolerance 调用；分别核对 HCU 主线/专项线、ABI/编译器、provider、同步/异步/精度边界与消费者。知识检索不足时读实际源码，不自动刷新大知识库。
   HCU Train Simulator 或训练引擎的模型 adapter、显存/求解公式、Profile、并行约束变化时，复核 `knowledge/practices/capacity-and-parallel-experiments.md` 和 adapt/optimize/coordinator；检查全参判断、余量与多实例资源隔离，保留旧预测/实测版本，不自动切换活动训练依赖。
   PyTorch/编译器/DDP/FSDP 或通信库版本变化时，同步复核 optimize 的 `references/torch-native-training.md` 和 `references/communication-optimization.md`；核实日志接口、编译/通信触发、同步与 buffer 生命周期。未登记的依赖变化也要按任务版本主动查源码，不能因为不在维护清单就跳过。
7. 修改后逐页/逐工作流写 decisions：decision、note、当前 page_sha256、新 source_commit。`wiki-review` 验证回执后，`wiki-apply` 再检查并写公共锁/基线，然后 wiki-index。确实依赖现场的 Skill/命令验证可 --defer-workflows 说明具体缺口，程序保留待办并在下次继续显示；Wiki 内容可先完成，不能把延后项标通过。采集、内容复核、软件发布与硬件实测分别记录。
   复核后又改正文/工作流或新增同来源专题时，重新检查并留下新回执；即使上游没有新变化也不能沿用过期复核。PR 重采后同样处理由作者页变动引起的待办。
8. wiki-catalog 刷新来源/文档/PR 导航（wiki-update 已在收尾调用），wiki-index 更新搜索。运行本工程测试和真实问题检索，保存本次缺口及下次入口。Wiki 提交与 push 沿用任务授权；站点知识按本仓归属规则提交，凭据不入仓。原始缓存可重建，但源码版本锁、作者结论和公开证据链接必须保留。

实际依赖升级需另外复核 thirdparty/manifest.json：锁定提交、bootstrap 指定工具、重装对应 Python 依赖/Skill，再检查接口和报告。脏 checkout 不覆盖。更新局部 Wiki 不触发 HCU-Knowledge 拉取或更新，其私有权限缺口单独报告。参见项目 docs/integrations.md。

TraceLens 同时监测 `amd-agi-tracelens` 上游与 `hcu-tracelens` fork。查看 fork 的上游基准、补丁记录及 HCU 验证状态；保留可复用模块和全部原生能力，优先扩展现有解析/模型。上游已有等价修复时经回归后退役本地补丁，不能只改 Wiki 就自动推进训练依赖。

## 组织标准

按工程定位→目录→编译安装→运行/测试→调用链→优化机制→问题诊断→版本/依赖→证据组织。案例按问题/瓶颈→为什么改→实现符号→适用条件→正确性/性能证据→失败条件/回退。尚未逐模型覆盖的入口页保持 coverage 标记，不以页数代替深度。

## 站点、模型经验与任务档案的维护

参照 `docs/knowledge-architecture.md` 与 `docs/experience-knowledge.md`。里程碑后将有复用价值的真实配置/变量、性能/显存/loss、故障和恢复结论整理进 `knowledge/sites/` 或 `knowledge/experiments/`，复制关键原件并登记哈希；不要只留任务 Store 或引用其 objects 路径。跨任务搜索从工程 Wiki 进入。任务 report 和 flow-advance 自动沉淀原 context 与证据；里程碑后确认自动写入成功，必要时 experience-sync 续接。关键环境验收、基线、性能/显存优化、阶段 loss、扩容、故障及 Cookbook 交付由对应阶段补 experience-record 解释；失败尝试也保存。不能猜指标单位或补造 loss。Cookbook 记录关联原经验 ID、脱敏审核和 draft/submitted/merged 等状态及 PR 链接，原数据不进入 public。局部经验和官方 Wiki 可自主按需更新，不调用 HCU 大知识库更新。

## 运行约定

先定位 HCU-TrainFlow checkout（用户给定路径或 `TRAINFLOW_PROJECT`）和私有 `TRAINFLOW_WORKSPACE`。跨任务站点配置、有效配方、关键性能/loss和精选证据写入本仓 `knowledge/`；完整任务档案留 workspace，凭据/私钥/token 永不入仓。CLI 用 `hcu-trainflow --workspace <private-path>`；源码环境可用 `python -m hcu_trainflow`。先读项目 `docs/quickstart.md` 和当前任务上下文，再按需读相关章节。

主 Agent 在本地主控，专家分工记录 owner、scope、允许修改路径、预算与验收证据。运行代码使用独立开发 checkout 和不可变源快照；远端只执行明确命令/守护，不要求部署模型 Agent。TaskSpec 的 execute/sync/notify 权限是任务约定，不是 OS 安全沙箱。实际节点、容器、Pod UID、Slurm allocation 由部署任务确认。

HCU-Knowledge 随完整安装提供，贯穿环境适配、性能优化和扩 DP/容错；需要 HCU 事实、历史案例或底层实现时使用 `$hcu-knowledge-search`；也可以读当前对应分支源码和公开官方文档。知识检索不自动更新 HCU 大知识库。本工作流维护自己的官方 Wiki、实践及站点/模型经验；具体依赖命令升级时同步复核 Skill/适配器，不能仅改 Wiki。

产物归属本 Skill：按目标仓规范准备集中、通用的改动、测试、PR 说明和回退方式。外部目标仓 PR/Cookbook 按目标发布要求处理；TrainFlow 自带 Wiki 按本仓知识归属规则保留实际站点/模型经验与精选证据，二者不要混同。遵循当前会话已给出的提交/发布授权。
