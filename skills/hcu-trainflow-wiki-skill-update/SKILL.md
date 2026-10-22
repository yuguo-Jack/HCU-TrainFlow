---
name: hcu-trainflow-wiki-skill-update
description: 维护 HCU-TrainFlow-Wiki 的官方资料、通用环境经验与最终模型总结，并更新受影响的工作流 Skill、命令和解析器，验证后同步本机安装。
---

# hcu-trainflow-wiki-skill-update

## 开始前定位与阅读

先定位 HCU-TrainFlow checkout：用户明确指定的路径优先，其次 `TRAINFLOW_PROJECT`，再读本 Skill 安装目录的 `workspace.json` 中 `project_root`；验证该目录的项目标识、docs/skills 与版本，失效时重新安装绑定，不猜路径。私有 `TRAINFLOW_WORKSPACE` 由当前任务另行确定，不从项目绑定推断。先读项目 `docs/skill-reading-map.md` 的当前模式行，再按其中的开始/条件入口读正文。首次使用或工程升级后核对安装副本；文件缺失或绑定过期先修复，不能直接跳过指南。

默认只在当前任务工作空间及已核实的远端/容器映射目录内创建、修改、移动或删除；外部资料可按需读取。首次写入、映射变化或涉及外部路径时先读项目 `docs/workspace-boundaries.md`，复用已记录范围与授权；必要例外写清路径和影响，未获授权再询问，不逐条命令重复确认。 已授权的 Wiki/Skill 维护可写所绑定 TrainFlow 工程和选定安装位置；这是明确的维护范围，不扩展到 HCU 大知识库或上游环境。

维护 HCU-TrainFlow-Wiki 的官方资料、可复用环境经验、模型最终优化总结，以及随源变化的工作流用法。它可以由训练任务按需主动调用；不替代或触发 HCU 大知识库 update。

**知识归属先于采集。** 官方项目统一在 `knowledge/projects/<project>/knowledgebase/`：`upstream` 放原文、PR 和源码地图，`local` 放整理后的总览/指南/专题/案例/版本解释。`sources.json.knowledge_project` 决定生成位置，新增资料不要重建旧的分散目录。HCU 仓库知识通过 `$hcu-knowledge-search` 查询，不在本仓再收 HCU 源码文档、PR 或整套项目 Wiki；有明确的大库修订请求才另用其 update Skill。普通 HCU 源码查证保留任务缓存。

## 调用时机与更新范围

先读 `docs/knowledge-architecture.md` 的“任务中的维护时机”。任务初期在确认模型、环境和执行分支后检查相关官方资料的新鲜度，有影响的缺口在依赖该事实前定向更新；环境验收和优化阶段收尾分别筛选通用站点经验与已验收的模型最终总结，任务最终完成前再汇总一次。恢复任务先读已有处理记录，不能每次轮询重复刷新。

先判断本次属于官方来源、经验总结、工作流用法维护中的哪些范围：官方来源按下述更新协议；只提炼经验时按“站点、模型经验与任务档案的维护”处理，不附带全量采集 PR。两者都执行相关性、证据、索引/检索和安装收尾检查。直接修改本仓流程/Skill 后同样同步安装。CLI 的 knowledge_followup 只是给 Agent 的非阻塞提醒，不是自动执行服务；把实际处理结果写入原任务计划/看板。未形成可复用知识就记录原因，不凑页面。

训练中按相关来源和变化范围维护：只有影响当前命令、接口或结论的漂移才立即处理；无关上游新特性、全库补采和共享总结排到合适里程碑，不作为开始实验的前置工作。用户明确要求全量更新时仍覆盖全部登记来源。复核按影响选代码/检索/安装测试，纯文字改动不触发整套 GPU 实验；采集成功且未变内容不反复重读，关联判断和当前内容哈希仍须一致。

## 更新协议

HCU 大知识库已更新或用户要求对齐时，先只读核对其当前提交与变更影响：覆盖三个阶段引用的工程、工具/命令、依赖与能力边界，再检查 TrainFlow 锁和本机已安装 Skill。确有过时用法才修订对应指南、适配器和测试；无变化的有效证据继续复用。将检查范围、结论与未验证项写入现有维护记录，随后推进局部 Wiki 深化，不以只更新官方 Wiki 代替此项。不得附带更新 HCU 大库或自动改变正在训练的依赖。

1. 检查公共 GitHub/文档权限、限流与实际访问，不把 404 当成已删除。读取 knowledge/sources.json 与已有 observed/reviewed 游标。
2. 先读项目 `docs/wiki.md` 与 `docs/knowledge-architecture.md` 的“自动更新时的内容筛选”。按问题复核收录范围；已确定低相关资料在 sources.json 的 document_exclusions 登记路径模式和理由，不能只删页面让下次同步重建，也不能因目录通配符匹配就全收。`wiki-update PROJECT SOURCE` 依次检查完整树、document_globs 新文档（排除上述规则）、PR/讨论与登记源码；也可单独使用 wiki-inventory / wiki-sync-docs / wiki-sync-prs / wiki-refresh。重复运行续完 pending，检查所有阶段错误及 excluded_paths。未监测的新文件从完整树发现，按最新 commit 用 wiki-triage 记录 knowledge-added/not-relevant/deferred，不能只抓 README 宣称全仓无变化。web 来源生成内容指纹，不能当 Git SHA；TE/cuDNN 同时检查代码与官方教程。官网迁站按 `docs/wiki.md` 的 canonical 查证流程同步登记、声明与受影响链接，再重采正文，不放宽抓取保护。
3. PR 来源页保存描述、普通评论、行内评论、独立 review 顶层状态/正文、文件列表及原始 JSON。首次增量发现默认最近 30 天，已保留历史 PR 每七天重新查讨论；需要扩大范围用 --since，不能称已覆盖全部历史。发现分页未结束时按 discovery_pending/next_page 续扫原窗口，不能只看 pending=0 或为绕过上限缩窄时间范围。主动按问题 wiki-search-pr 补重要未收录 PR，再 wiki-pr 和 wiki-code 追最终代码；可显式 --retain-project 纳入公共来源页。缺 patch/分页/权限时保留失败并补证据，不将标题或初始描述直接编成案例。
4. 比较实际 active ref 与已锁版本，处理 submodule gitlink，不用子仓 HEAD 偷换。发布计划、open PR、merged main、released 和运行可用分开。
   官方发布与 roadmap 的查证入口见 `docs/wiki.md`“未收录的官方内容按需查证”；它们可能位于 Releases、官网、Issue/Discussion/Project，不能以 PR 采集代替。影响当前任务时按需阅读并追实现；持续策展按维护范围登记来源与覆盖缺口，未被现有采集器覆盖的页面不能宣称已自动全量同步。SFT/RL 模型专题可后续深化，当前问题仍须追官方模型配置、recipe 和 backend 源码。
5. 对每个 affected overview/topic/case 深读新实现、改原因、触发条件、测试、限制和回退，同仓交叉结论一起修正。必要时扩充关联的第三方优化采用/退役记录。
   PR 描述、review 或 diff 更新即使没有主干源码变化，也检查 wiki/pr-review 待办；对关联页复核后 wiki-review-pr 留下对应原始 artifact 与页面哈希的回执。
6. 按 knowledge/maintenance.json 检查官方变化影响；另读 knowledge/catalog/external-knowledge.json（或 `wiki-routes PROJECT`）核对 HCU 工具的维护关联。依托大库与实际部署/最新源码检查 Skill、环境命令、TraceLens 接口、日志字段、profile 参数和容错步骤；只修订本仓使用契约，不复制 HCU 仓库知识。任务所用 HCU 模型脚本、环境配置、launcher 或依赖变化时，复核适配/分析优化用法和配方。可复用站点经验按规范放 `knowledge/sites/`，临时排查留任务档案；检查依据、版本及未验证项记入本轮维护记录。
   新增或升级 HCU Primus Turbo、UCCL、UltraEP、MoonEP 等库时，复核 optimize 的 `references/hcu-library-integration.md`、通信专项及 adapt/规模长稳 Skill 调用；分别核对 HCU 主线/专项线、ABI/编译器、provider、同步/异步/精度边界与消费者。知识检索不足时读实际源码，不自动刷新大知识库。
   HCU Train Simulator 或训练引擎的模型 adapter、显存/求解公式、Profile、并行约束变化时，复核 `docs/practices/capacity-and-parallel-experiments.md` 和 adapt/optimize/coordinator；检查全参判断、余量与多实例资源隔离，保留旧预测/实测版本，不自动切换活动训练依赖。
   PyTorch/编译器/DDP/FSDP 或通信库版本变化时，同步复核 optimize 的 `references/torch-native-training.md` 和 `references/communication-optimization.md`；核实日志接口、编译/通信触发、同步与 buffer 生命周期。未登记的依赖变化也要按任务版本主动查源码，不能因为不在维护清单就跳过。
   性能方法同步查项目 `docs/practices/performance-methods.md` 的固定来源与路径（Hyperloom/GEAK/BBuf）：核对新版本的证据刷新、dispatch/oracle、重叠归因、测量与停止规则，并复核 optimize 的 `references/evidence-driven-loop.md`、`references/operator-ceiling-iteration.md` 及实际分析/质量评估代码。参考仓不是必装运行时，不能把其推理门槛或 AMD/NV 工具默认搬到 HCU 训练；方法源暂未注册的按该页有界查证并记录，不能伪称 Wiki 已全量更新。

   故障诊断与适配/优化异常指南也属于维护目标：同时复核规模长稳 Skill 的 `references/diagnosis.md`、`references/evidence-sources.md`、环境检查与模型适配的 `references/troubleshooting.md` 和 optimize 的 `references/validation-diagnostics.md`。检查 DTK hipgdb/hipprof 接口、runtime 信号/转储、RCCL/PyTorch 日志及内存 API、hcuprobe 与 Cluster Manager 的部署分支/恢复语义；按当前大库或源码查证，缺现场测试明确保留待验证，不能只换工具名字或年份。
7. 修改后逐页/逐工作流写 decisions：decision、note、当前 page_sha256、新 source_commit。`wiki-review` 验证回执后，`wiki-apply` 再检查并写公共锁/基线，然后 wiki-index。确实依赖现场的 Skill/命令验证可 --defer-workflows 说明具体缺口，程序保留待办并在下次继续显示；Wiki 内容可先完成，不能把延后项标通过。采集、内容复核、软件发布与硬件实测分别记录。
   复核后又改正文/工作流或新增同来源专题时，重新检查并留下新回执；即使上游没有新变化也不能沿用过期复核。PR 重采后同样处理由作者页变动引起的待办。
8. wiki-catalog 刷新来源/文档/PR 导航（wiki-update 已在收尾调用），wiki-index 更新搜索。运行本工程测试和真实问题检索，保存本次缺口及下次入口。Wiki 提交与 push 沿用任务授权；站点知识按本仓归属规则提交，凭据不入仓。原始缓存可重建，但源码版本锁、作者结论和公开证据链接必须保留。
9. **维护收尾包含本机同步。** 本仓 Wiki/docs、Skill/reference、脚本、CLI 或包配置有改动，复核和测试通过后，定位当前 Skill 安装所在的实际 Skills 目录，运行 `python scripts/sync_local_install.py --target <实际Skills目录>`，再以 `--check` 只读复核。它刷新本仓 editable Python 包和六个 Skill，检查内容哈希、绑定与阅读资源，成功后清理本次旧备份；失败不能报更新全部完成，按 `.work/setup/local-sync.json` 修复后重跑。源依赖约束、构建依赖或 thirdparty 锁有变化时先按 `docs/integrations.md` 完成对应安装/验证，局部同步不能代替依赖升级验收。仅文档/Wiki 内容通过 checkout 直接读取，但仍检查整个安装状态；同步完成后提醒新会话载入。其他安装目录只在明确选定时同步，不扫描所有 Agent；不自动更新 HCU-Knowledge。

实际依赖升级需另外复核 thirdparty/manifest.json：锁定提交、bootstrap 指定工具、重装对应 Python 依赖/Skill，再检查接口和报告。脏 checkout 不覆盖。更新局部 Wiki 不触发 HCU-Knowledge 拉取或更新，其私有权限缺口单独报告。参见项目 docs/integrations.md。

TraceLens 的官方来源为 `amd-agi-tracelens`；HCU fork 通过外部维护关联、thirdparty 锁和 docs 的集成契约核对，不能再作为局部 Wiki 来源采集。检查其上游基准、接口、补丁与 HCU 验证状态；上游有等价修复时经回归再退役本地补丁。锁变化时同步复核 manifest 的 integration_contracts，不能只改 Wiki 就自动推进训练依赖。

TraceLens 接口更新同时核对报告/collective、Graph、Roofline、Agent、hipprof/counters，以及 split/merge/compare 的请求、输入哈希和状态。源码定位、索引、EventReplay 保留原生使用路线；按受影响功能执行真实输入或合成回归，缺硬件时保留缺口。同步安装包与固定 checkout，避免本机仍导入临时开发副本。无需为一次文档改动重复采集全部硬件证据。

精度方法维护还需复核项目 `docs/practices/model-accuracy-diagnosis.md` 与三个阶段的入口。按 HCU-Knowledge 的 dcu_probe 项目或当前源码核对 hcu-probe/hcuprobe 包与 CLI、配置、hook/异步快照/flush、compare 映射和跨 rank 首差、训推接入；同时核对 PyTorch/TE 的精度与随机性接口。来源变更不代表所有后端已实测，保留登记/离线/现场的验证范围，不自动刷新 HCU 大库。

## 组织标准

来源新增、版本推进或收录范围改变时，按项目 `thirdparty/KNOWLEDGE-NOTICES.md` 的维护规则复核材料归属与许可；官网正文、仓库文档/PR、工具依赖和历史归属分别处理，保留固定原件与核对依据。只登记链接的 HCU 联动仓不重复采集其 Wiki 或整套许可。

流程文档同时遵守项目 `CONTRIBUTING.md` 的文档同步规则：对照当前代码和 CLI 核对根目录说明、docs、Skill/reference、Wiki 导航及图文入口；更新仍在使用的旧说明，清理前核查引用和维护关联。不要改写固定上游原文或删除兼容页面 ID 来消除旧字符串。收尾运行 `python scripts/check_documentation.py` 与原有知识/阅读路线检查；结构检查不能替代内容复核。

维护所有来源时先读项目 `docs/wiki-authoring-standard.md` 和 `knowledge/coverage.json`；按相同内容维度检查各工程，包括用于优化借鉴的 DeepSpeed、Primus、MindSpeed 系列和 LoongForge。新增来源补角色/入口/维度；补齐薄弱正文并关联实际源码，不用页数或原文采集量冒充深度。更新相关 README、参考选择表、HCU 库归属与受影响阶段，运行 `python scripts/check_wiki_coverage.py`；它只检查组织完整性，结论仍需源码复核。

流程与 Skill 只提炼跨模型、跨项目可迁移的方法。保留触发条件、输入契约、判断依据、验证和回退；命令用可发现的接口和参数化配置表示。单项目 shape/拓扑、地址、补丁、临时编译选项或实验顺序留在 workspace，不升级为通用默认或必做步骤。现有内容与新版本不同，先核对适用条件，不能把一次现场成功推广成所有环境适用。

按工程定位→目录→编译安装→运行/测试→调用链→优化机制→问题诊断→版本/依赖→证据组织。案例按问题/瓶颈→为什么改→实现符号→适用条件→正确性/性能证据→失败条件/回退。尚未逐模型覆盖的入口页保持 coverage 标记，不以页数代替深度。

全量、增量和任务中自主更新均按 `docs/wiki-authoring-standard.md` 筛选：发现重大或高价值优化项才需要整理详细案例，优先完善同机制已有案例。小修改按原规范更新相关章节、PR 摘要和证据，不为每个 PR 或每轮更新凑大案例；没有重大优化项可以不新增案例。按影响而非代码行数判断，重要精度/正确性/恢复变化仍须充分说明，受影响页面与 Skill 仍联动复核；缺证据记录待补入口，不虚构收益。统一内容粒度不要求案例数量相同。

## 站点、模型经验与任务档案的维护

整理已有页面也执行内容筛选：正文保留结论、适用条件、关键数据及最少充分证据；会话决策、待办、临时设施与逐次试验归任务档案。实际测量身份/版本/配方和可复用的具体 PR 问题仍需保留，不能为“通用”而删掉复现条件。引用与来源规则一并复核，排除既有文档需整理生成页及 ledger；不篡改原件、观测日期或未验证状态。完整规则只维护在 `docs/knowledge-architecture.md`。

参照 `docs/knowledge-architecture.md` 与 `docs/experience-knowledge.md`。共享 Wiki 只收录官方资料、跨项目可复用的通用环境经验，以及模型最终优化里程碑的总结和关键数据。筛选后分别进入 `knowledge/sites/` 或 `knowledge/experiments/`，复制必要原件并登记哈希；临时排查、逐次调参、算子中间报告、未验候选和 Cookbook 草稿只留任务 Store/看板。最终总结须交代数值验收与未达目标，不把局部通过改名成最终结果。跨任务搜索从工程 Wiki 进入。任务 report 和 flow-advance 只向私有任务 Store 自动沉淀原 context 与证据，不等于已更新共享 Wiki；里程碑后确认自动写入成功，必要时 experience-sync 续接。关键环境验收、基线、性能/显存优化、阶段 loss、扩容、故障及 Cookbook 交付由对应阶段补 experience-record 解释；失败尝试也保存。不能猜指标单位或补造 loss。Cookbook 记录关联原经验 ID、脱敏审核和 draft/submitted/merged 等状态及 PR 链接，外部 Cookbook 的数据发布要求单独遵守；本仓可保留符合收录条件的关键实测数据。局部经验和官方 Wiki 可自主按需更新，不调用 HCU 大知识库更新。

## 运行约定

仅跨项目可复用的通用环境经验和模型最终优化里程碑总结/关键数据按收录规则写入本仓 `knowledge/`；完整任务档案留 workspace，凭据/私钥/token 永不入仓。CLI 用 `hcu-trainflow --workspace <private-path>`；源码环境可用 `python -m hcu_trainflow`。先读项目 `docs/quickstart.md` 和当前任务上下文，再按需读相关章节。

主 Agent 在本地主控，专家分工记录 owner、scope、允许修改路径、预算与验收证据。运行代码使用独立开发 checkout 和不可变源快照；远端只执行明确命令/守护，不要求部署模型 Agent。TaskSpec 的 execute/sync/notify 权限是任务约定，不是 OS 安全沙箱。实际节点、容器、Pod UID、Slurm allocation 由部署任务确认。

HCU-Knowledge 随完整安装提供，贯穿环境适配、性能优化和扩 DP/容错；需要 HCU 事实、历史案例或底层实现时使用 `$hcu-knowledge-search`；也可以读当前对应分支源码和公开官方文档。知识检索不自动更新 HCU 大知识库。本工作流维护官方资料、可复用环境经验和模型最终优化总结，工作流方法在 docs/skills；具体依赖命令升级时同步复核 Skill/适配器，不能仅改 Wiki。

产物归属本 Skill：按目标仓规范准备集中、通用的改动、测试、PR 说明和回退方式。外部目标仓 PR/Cookbook 按目标发布要求处理；TrainFlow 自带 Wiki 按本仓知识归属规则保留通用环境经验、模型最终优化总结与必要证据，二者不要混同。遵循当前会话已给出的提交/发布授权。
