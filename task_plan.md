# HCU-TrainFlow v0.1.0 implementation plan

## Scope
Implement the first usable local-centred workflow release. Preserve the 36 requirements and staged roadmap from the approved design. Five Skills: prepare, optimize, operate, wiki search, wiki update. Real HCU/site validation remains explicit and separate from local fixture tests.

## Phases
1. Source/interface research, public boundary and release contracts — complete
2. Task/evidence/leases, source snapshots and execution adapters — complete
3. Environment/quality gates, profile analysis, experiments and monitoring — complete
4. Public upstream Wiki, refresh/impact/search and workflow maintenance — complete
5. Five Skills, installation, reproducible demo and tests — complete
6. Integrated review, clean installation, public export, GitHub release — complete

## Delivery rules
- Keep working copies, credentials, site data and original private planning outside the published file set.
- Prefer measured evidence; all-skip, empty trace and mismatched snapshots cannot pass.
- Analysis-only, environment-only and diagnose-only are independent modes.
- Per-iteration correctness and stage-level loss validation are distinct.
- Remote watcher persists when the controller is offline; existing recovery remains single-owner.
- HCU-Knowledge is an optional read-only reference during this development.

## Errors and decisions
- Original planning documents are preserved under ignored .private/planning-original; public documentation will be curated separately.

## Follow-up: HCU launch recipe priority

- Complete: corrected preparation guidance to reuse applicable HCU scripts and the user's deployment, with official model/training semantics as the reference.
- Complete: reviewed related workflow, Megatron topics, profiling and maintenance guidance together; Wiki integrity and all three changed Skills validate successfully.

## Active follow-up: training libraries and bundled integrations

1. Inspect current TE, cuDNN Frontend and TraceLens sources/tutorials and dependency repository layout — complete.
2. Add detailed official library Wiki topics, monitored source/tutorial paths, source locks and workflow impact rules — complete.
3. Integrate TraceLens execution and reproducible thirdparty acquisition, including optional private HCU-Knowledge and the three Hygon kernel Skills — complete.
4. Update installation/workflow guidance, validate fresh-environment behavior and real TraceLens fixture execution, review — complete. Publication is recorded in Git history.

Public repository stores reusable integration and public authored knowledge. HCU-Knowledge contents remain in an ignored checkout and access failure cannot block the public workflow installation.

### Follow-up acquisition issues

- cuDNN Frontend shallow clone hit an HTTP/2 early EOF; TraceLens pack transfer stalled. Retry with HTTP/1.1 and sparse acquisition to avoid large non-code payloads.
- TE's historical user-guide URL returns 404; use the current canonical documentation root and pinned in-repository tutorial sources.
- The pinned TraceLens CLI imports an unrelated helper that sets csv.field_size_limit(sys.maxsize), overflowing Windows C long. The integration uses its supported report API in an isolated worker, retaining the upstream checkout unmodified.

## Active follow-up: reusable HCU TraceLens fork

1. Verify account and create/reuse the public yuguo-Jack fork with upstream history — complete.
2. Preserve upstream modules and commands; document HCU extension/validation boundaries, and repair only locally reproduced compatibility defects — complete.
3. Point TrainFlow to the reviewed fork commit; provide explicit safe migration from the upstream checkout and retain the upstream knowledge source — complete.
4. Validate native command entrypoints, report regressions, dependency migration and repository integrity — complete. Publication is recorded in both Git repositories.

## 2026-10-09: collaborative workflow and review loop (active)

User requests a unified autonomous entry Skill, persistent implement/review/correct cycles, file-based human guidance and progress, renaming prepare to adapt and operate to fault-tolerance, accurate development version/README, and no release. Existing three stage workflows plus two Wiki Skills remain callable; one coordinator entry is now explicitly requested. Real HCU validation is deferred until a site is supplied.

1. Inspect TrainFlow and pinned Humanize/BBuf/Hyperloom reference implementations — complete.
2. Design and implement evidence-bound iteration/review and human board contracts integrated with existing task/execution/monitor state — complete.
3. Add unified Skill, rename stage Skills with safe installation migration, and rewrite workflow-first docs — complete.
4. Exercise interruption/resume, stale reviews, human guidance and numerical/scale gates; review and validate; no release or new tag — complete.


## Agent coordination follow-up

1. Inspect existing assignment, review and execution contracts; identify safe parallel stages — complete.
2. Implement dependency-aware assignment lifecycle, bounded dispatch selection and related-agent message receipts; preserve execution uncertainty and quality gates — complete.
3. Use the agreed agentic project description, five-minute guidance collection, stage/coordinator Skills and concrete parallelization guidance — complete.
4. Test dependency/race/stale-result/message/resource cases, review and install Skills, push development changes without release/tag — complete locally; publication is recorded in Git history and CI.

- Dynamic operator decomposition clarification: use real model/profile operator identity and implementation scope; independent analysis and optimization proceed concurrently without an all-operator analysis barrier — complete.

## 2026-10-09: official and task knowledge completion

1. Complete HCU-Knowledge online PR/MR fallback and pinned source reading, test/review and publish v0.5.3 first — complete, pushed and tagged.
2. Implement official Wiki PR discovery/read/source tracing, persistent public PR pages, full source-tree navigation and resumable source/PR update coverage — complete.
3. Expand official engine documentation and source navigation with versioned evidence, deepen Megatron ecosystem; distinguish automatic source maps from authored analysis — complete.
4. Add private task experience knowledge: environment/model/version identity, performance/loss evidence, successful and failed optimization milestones, retrieval and cookbook delivery provenance; integrate flow milestones — complete.
5. Test offline and real public retrieval; review privacy, pagination, stale evidence and restart behavior; install Skills — complete. Development changes committed; push verification is recorded in Git remote state. No TrainFlow release/tag.

Real training and site-dependent command validation remain pending until hardware is supplied. This does not defer source-based Wiki work. HCU-Knowledge is not updated as a side effect of TrainFlow operation.

## 2026-10-09: overall pre-environment review

1. Review execution/monitoring, flow/team state, numerical/performance gates, Wiki and experience persistence against actual source and regression tests — complete.
2. Reproduce and repair concrete defects, preserving public/private boundaries and existing workflow scope — complete; independent reproduction and cross-review included.
3. Run complete local tests, knowledge validation and relevant CLI/demo smoke checks; synchronize changed Skills if needed — complete: 206 tests, 485 pages/24 sources, all six installed Skills matched.
4. Commit and push reviewed development changes; report readiness and site-dependent validation limits. No tag/release — validated for publication; final publication is recorded in Git remote state and CI.

## 2026-10-09: detailed workflow diagrams

1. Map current stages, code gates, optimization loops, Agent coordination, remote execution, monitoring and knowledge lifecycle — complete.
2. Add editable diagrams with source links and explicit implementation/site-validation boundaries; connect existing reading entries — complete.
3. Render and inspect diagrams, verify links and gate mapping, publish documentation without release/tag — locally validated; publication recorded in Git history and remote state.

## 2026-10-09: Torch training and required knowledge integration

1. Read the supplied reference implementation and current HCU knowledge — complete.
2. Integrate conditional Torch-native and communication guidance into the existing optimization Skill; clarify restoration and DP scale-out — complete.
3. Require HCU-Knowledge in full setup, including index and bound Skills; support reuse and explicit permission failures — complete.
4. Refresh diagrams, review/test setup and Skills, synchronize local installation, commit/push without release — complete locally; publication recorded in Git history.

## Real-environment qualification (active)

1. Discover and qualify authorized transport, container, occupancy, tool provenance and computation/communication capabilities.
2. Adapt a fixed official model proxy on current HCU software; establish component numerics, real-data baseline and checkpoint restoration.
3. Exercise measured training traces, dynamic optimization tasks, private experience, independent review, monitoring and scale-out.
4. Generalize and test each reproduced workflow/TraceLens defect, synchronize Skills and review public-safe changes; no release.

Site inventory, model/data definitions, raw measurements and user guidance are retained only in the external private task workspace. Environment and model gates remain incomplete until their actual coverage passes.

### Qualification checkpoint

- Transport, immutable snapshots, bounded resource admission, training observation, multi-member health, private references and offline plots have reusable implementations and CPU regressions.
- Actual component numerics, bounded training, multiple-rank profiling, an optimization comparison, stage loss observations and collector failure/recovery have been exercised. These are separate evidence cohorts, not a blanket production pass.
- Main HCU delivery integration was qualified separately: the mixed-precision checkpoint path was repaired, and bounded save/load/continued-step checks ran. Distributed and full numerical qualification remain separate; no donor performance result is relabelled as main-branch acceptance.
- Initial public review, Skill synchronization and development commits are complete; actual clean-CI failures were repaired and the four-job follow-up matrix passed. No tag/release; unsupported automatic recovery/notification and full-size model claims stay open.

## Performance discrepancy follow-up

1. Require reference/method/configuration/path checks, HCU knowledge and fixed-source investigation, and authorized bounded trials before accepting a discrepancy investigation as complete — implemented.
2. Preserve unresolved evidence-backed gaps through environment-check even when execution succeeds or an older floor is reached; distinguish failure from missing comparison evidence — implemented with regressions.
3. Exercise the sequence on a private collective diagnosis and retain per-rank configuration, correctness, physical-port counters and rollback evidence — initial A/B/A executed with per-rank numerical/exit checks; counter/source review and any additional candidate stay in private evidence.
4. Review, run the complete test suite and knowledge validator, synchronize managed Skills and publish development changes without release/tag — local review, complete regression and managed Skill synchronization passed; publication is recorded in Git history and remote CI.

## 2026-10-10: substantive workflow qualification and technical board

User requires engineering detail and real scientific optimization, not ceremony. Prioritize a single coordinator; delegate only an independent substantial task with clear expected benefit or one necessary review.

1. Audit actual environment, model/parallelism/profile/operator, recovery/monitor and RLCR evidence; publish a complete private capability/validation matrix with commands, dependencies and gaps. In progress.
2. Extend the generated board with evidence-backed technical sections and update rules: environment/results vs expected, model/memory/parallelism, bottleneck conclusions, per-op bounds/headroom, experiments and decisions, scale/recovery/training health, RLCR findings. Pending.
3. Execute focused real-model profiling/shape-bound analysis, justified parameter and operator optimization trials on fresh idle resources; quantify numerical/performance outcomes and limitations. Pending.
4. Establish actual fault-tool command/dependency ownership; exercise task-local controlled failure, diagnosis, screening where supported, checkpoint relaunch and observation; clearly separate full site capabilities from partial tests. Pending.
5. Validate RLCR revise→repair→independent-review on a meaningful candidate, integrate lessons into the existing six Skills, regression/review/sync and push public-safe changes. Pending.

No automatic big knowledge-base update. No new public release. No artificial Agent roster or per-command review. Site traffic/host modification and destructive fault injection remain outside scope; controlled failure of our own test process only. User latest request authorizes onward model/workflow qualification; historical partial communication reference remains an explicit limitation, not a reason to silently stall all independent work.


### 当前持续推进（2026-10-10）

- [x] 跨任务站点知识与必要原件进入本仓 Wiki；检索、哈希、相对链接、Skill 规则及独立 review。
- [ ] donor 原执行分支完成微批 ABBA、系统/算子优化与阶段 loss，维持主仓交付延后。
- [ ] Cluster Manager 实际故障触发、任务身份停止、checkpoint 自动恢复和持续监测；CPU控制协议验证不代替此项。
- [ ] 将后续可复用调参、loss、故障结果继续沉淀到同仓站点/模型案例。


## 2026-10-10：全参容量预估与多实例优化

用户补充：先用 HCU Train Sim 等判断完整模型可行性，卡足优先全参，卡不足才缩 layer；资源富余时独立完整模型实例并行优化，明确分工和及时交流。已核对公开模拟器 b7d8e6f3（CLI/adapter/模板），并修正 proxy/adapt 的旧“优先缩层”措辞；协同协议沿用现有 team/lease/inbox，新增实践、更新阶段 Skill 和可编辑流程图。预测不作为硬件或全模型验证，当前 Kimi K3 模拟覆盖仍需核实，实际实验继续。


## 2026-10-10：HCU底层工程联动

按用户要求将HCU Primus Turbo、UCCL、UltraEP、MoonEP纳入按瓶颈选择/复用/修改重编/分层验证/目标PR的链路。已检索HCU-Knowledge保留报告，明确通用与专项分支和接口边界；HCU问题先查询大知识库，同问题已取回证据可复用，不触发大库更新。训练引擎与容错项目不扩名单。


## 当前收尾：共享知识筛选与通用工作流（2026-10-10）

- [x] 共享 Wiki 收紧为官方资料、可跨项目复用环境经验、模型最终优化里程碑；中间候选完整归回任务档案。
- [x] 工作流方法迁入 docs/practices，统一所有引用、维护目标及 Skill 的收录/搜索边界。
- [x] 更新 Skill 更名 hcu-engine-wiki-skill-update；保留旧安装的可恢复迁移，本机六个入口同步。
- [x] 方法只保留通用触发/输入/判断/验证/回退；项目参数与临时绕过留 workspace。
- [ ] 完成独立复核修正和提交推送。真实算子及训练质量验证在任务工作区继续；不发布 release。


## 2026-10-10 硬件建模交接与算子阶段复核

- 两节点16卡只读属性与管理工具复核，统一硬件基线；产品标签冲突、旧测量执行映射缺口明确保留。
- 非Adam高贡献模型8项CPU检查通过，主控接受分析阶段；每项工作量、条件效率、余量与下一动作已更新看板。完整优化没有据此关闭。
- baseline初版→HIP优化、现有Triton→Triton优化的交接与负责人验收已写通用Skill；本机三项变更Skill已同步。
- 真实CM恢复密封日志经现有解析/绘图得到3张图、9步记录，历史离线视图不进入实时监控。
- 站点硬件知识及精选6原件随公共工程；全新Store可搜读；独立review唯一来源过度断言已修正。72项相关测试和490页/25来源校验通过，无release。
