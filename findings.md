# Findings

## 2026-10-12: Check/adapt naming and optional KernelWiki

- Runtime stage codes stay unchanged; Skill routing, display name, directory, reading links and Wiki maintenance targets use hcu-train-check-and-adapt. Previous names remain only in installer migration and migration tests.
- KernelWiki root is its Skill. Pin b6b4301, fetch to ignored thirdparty/KernelWiki, opt in via --with-kernelwiki or install only via --kernelwiki-only; keep all query/evidence/license resources but exclude Git metadata/caches and thirdparty checkout from sdist.
- Align cuda-optimized-skill to reviewed f39ba95 so new installs include the HCU cases/PR/KernelWiki reference guidance. No HCU-Knowledge source refresh.
- Existing system KernelWiki differs only in scripts/validate.py; preserve this independent local change. Verify new optional installation in an isolated .work directory instead. Default setup does not touch it.


## 2026-10-09 — implementation baseline
- Approved design has 36 requirements, 106 work packages, 12 modules and exactly five Skill entrypoints.
- First release follows the first vertical development batch; no training cluster was assigned.
- Existing directory contained five planning documents and no Git repository or implementation.
- Preserve original detailed planning privately; publish reusable implementation, public-source explanations and explicit capability status only.
- Core implementation uses system Python; no CUDA/DTK/training-engine dependency is required for control-plane installation.

## Implementation evidence
- TraceLens currently exposes TraceLens_generate_perf_report_pytorch with --profile_json_path and --output_xlsx_path / --output_csvs_dir. Keep it optional and verify installed --help.
- Primus has source-guarded per-layer recomputation and two-tier DDP hooks for compile/parameter-gather interactions; useful mechanisms require version-specific review before HCU adoption.
- LoongForge carries its Megatron implementation as a pinned gitlink: parent and child commits must both be recorded.
- Python sqlite3 context managers commit/rollback but do not close connections; explicit close is required before renaming index files on Windows.

- Initial Git whitespace review detected CRLF text as trailing whitespace under this host configuration. Added a repository LF policy and normalized only the intended tracked text files; cached source bytes remain unchanged.

## HCU model adaptation clarification

- The prepare Skill and several Megatron pages said to start from official recipes, which could mislead agents into copying NVIDIA platform setup and launch commands.
- Applicable HCU scripts, their sourced environment/configuration and the user's deployment form the launch reference. Official recipes remain the model/training semantic reference; both old HCU scripts and new task changes require compatibility and correctness checks.

## Training library / integration expansion

- TE currently has one short Megatron chapter and only four monitored files; cuDNN Frontend is absent. Both need their own detailed public-source sections and tutorial monitoring.
- TraceLens is currently mentioned as an external command only. Add an executable integration and pin its source alongside the kernel Skill repository.
- Use a tracked thirdparty manifest with ignored checkouts and selective bootstrap. This retains repository identity/version without publishing private HCU-Knowledge contents or making an authenticated clone mandatory for public users.
- Verified Git access to the optional private knowledge repository; it needs its own workspace-bound Skill installer and Git LFS setup, not an unbound copy of its Skills.
- TE now marks pytorch/fp8.py deprecated in favor of quantization.py. Attention selection distinguishes fused/flash/unfused backends; userbuffer overlap tutorial has NVIDIA-specific topology/connection constraints that cannot be copied as HCU defaults.
- cuDNN Frontend includes both backend graph APIs and open-source kernel families. Current source covers Python graph backends, plan/workspace reuse, MoE activation/quantization fusions and sparse attention; open-source frontends do not imply all cuDNN backend kernels are public.
- Official website latest/stable and main source are separate revisions. Track both; do not silently infer that newly added main APIs exist in the installed release.
- TraceLens report APIs work on Windows without the unrelated CLI helper that overflows C long via csv.field_size_limit(sys.maxsize). Keep upstream unmodified and invoke report APIs in an isolated process.
- Report generation is not training validation: preserve native statistical denominators, complete rank requirements and explicit HCU architecture input. Truncated tables must still produce a failed report receipt.
- Native report, gzip and complete two-rank synthetic collective paths are locally verified. Fresh bootstrap also verified the sparse clone path, avoiding unnecessary example trace downloads.

## HCU TraceLens fork

- Created the public yuguo-Jack/TraceLens fork; `hcu` is the default integration branch and `main` retains the initial AMD upstream baseline. Development uses a separate checkout from the installed thirdparty dependency.
- Preserved all 13 native command entrypoints and upstream modules/dependency declarations. Base installation supports CLI help without the optional JAX/Origami runtime; that does not validate those execution paths on HCU.
- A narrow CSV OverflowError fix restores native CLI imports on affected Windows Python builds. Existing graph-under-recording tests continue to pass; upstream private-repository notification is guarded to the upstream repository identity.
- Prefer existing hardware JSON, architecture extension and op-model/collective interfaces. Actual HCU trace formats and measurements are required before adding hardware predictions or new kernel-specific rules.

## Collaborative workflow inspection, 2026-10-09

Current checkout ebf419c declares 0.2.1; only existing Git tag is v0.1.0. It has five separate Skills and task/evidence/monitor/assignment primitives but no unified coordinator Skill or explicit persistent implementation/review loop. README emphasizes component inventory. Public Humanize references differ: PolyArch advertises a Claude implementation/Codex review RLCR loop with annotated plans; humanfia is a separate flow runtime (Python 3.12+, different license/runtime assumptions). Inspect source before deciding reuse. Existing docs correctly retain remote/site validation gaps.

Reference inspection: PolyArch Humanize 4eeb392cd2450c3df99cb898bd6b24839967bbc3 defines RLCR as Ralph-Loop with Codex Review. Its native stop-hook enforces round state, plan integrity, summaries, review success/nonempty output and issue handling; full-alignment review runs periodically. humanfia 60cab7e69fbff07dd2968088df6a64c6e23accd6 separates flow runtime from actor/reviewer RLAR and external humanize1-flow. TrainFlow should reuse these evidence/review/resume principles with its own training quality gates rather than install global hooks or bypass runtime approvals. No external reference instructions are being executed.

BBuf 6dc9c66a008daded66f214022919ff88b2186252 contains sglang-humanize-review grounded in PR review episodes, not the same runtime as Humanize RLCR. Preserve real candidate dispatch, historical-review freshness, replay-first incidents and profiler evidence. Hyperloom 0425bde3f6e76e1588400c37d056dfd3bb75ac11 has persistent loop state, plan critic, best lineage, stalled progress and measured round admission. Reuse mechanisms in a harness-neutral training loop; do not import inference-specific scores, timeout constants, global stop hooks, auto-push or permissive agent execution defaults.

Implementation decision: attach an optional durable collaborative session to existing TaskSpec/Store. A single entry Skill drives next-work/review/revise/advance decisions; independent reviews bind plan, task revision, candidate snapshot and reports. Existing machine gates remain mandatory. Iteration acceptance is distinct from stage-loss acceptance. Private BOARD.md is generated; human-owned GUIDANCE.md revisions are retained and acknowledged. Board polling emits existing agent inbox events; actual auto-wakeup still needs a configured local bridge. No background monitor or notifications are installed by this development task.


Implementation review: flow evidence now separates the frozen comparison context from each candidate manifest, so an optimization iteration does not reset every task stage. Current report IDs and candidate_snapshot must agree; legacy tasks without flow keep their existing context-based invalidation. Human guidance changes supersede pending/accepted reviews, are deduplicated against the last observed content (reverts remain new events), and queued guidance needs final disposition. An authorized local bridge may wake a reader despite pending guidance, while experiment execution remains gated. Bridge consumers must begin task commands after the short delivery operation returns; a synchronously nested whole-Agent run can otherwise block on its own started operation. Actual runtime/site acceptance remains pending.


The current assignment API only registers pending work and accepts an owner's return; it has no dependency graph, resource-aware claim, result acceptance or peer message protocol. Strengthening it requires separating planned/claimed/returned/accepted states, pinning dependency result hashes when claiming, and reserving shared write scopes/resources. Independent analysis can fan out; measurement on shared GPUs and integration remain controlled. The requested five-minute interval must throttle ordinary automatic guidance reads, not just change the watcher sleep; explicit board refresh may scan immediately.

## Parallel coordination reference and implementation review

- Multica c76a012dc70da037372159bbd19a4f69f0120783: read squads.mdx, handler/comment.go trigger routing and resolveCommentTriggerEnqueue, comment_steer_test.go, and worker-to-leader wake tests. Useful distinctions are leader-directed delegation, running-turn supplements, durable pending inputs, truthful queue/delivery outcomes and separate result acceptance. Its LICENSE contains additional conditions; no code/runtime is copied.
- Hyperloom 0425bde3f6e76e1588400c37d056dfd3bb75ac11 orchestration.py partitions implementation by independent files/functions/mechanisms, keeps coupled kernel/launch changes together and requires the synthesis owner to judge compatibility; specialists.py bounds concurrency and retains sibling failure outcomes. These guide TrainFlow decomposition and integration instead of a fixed Agent count.
- Team plans now declare dependency DAGs, peers, scopes, resources and finite budgets. Atomic claims bind exact accepted input reports and token; native runtime IDs are recorded separately from claims. Returned reports need controller/other-reviewer acceptance. Blocking findings supersede pending/accepted flow reviews.
- Peer messages have idempotent IDs, current context/goal, directed question/answer/finding/blocker/handoff semantics and seen/handled receipts. A question closes only when its author confirms the answer; evidence is required for resolving blockers. Yielding verified-quiescent work avoids slot starvation while waiting. Source/goal changes retain old evidence but prohibit stale results; old active claims stay reserved until verified stopped.
- Review found two concurrency hazards and corrected them: command idempotency must include assignment/token, and task execution budgets must reserve in-flight timeouts. A short authorized local delivery bridge can run while a worker is executing or its remote outcome is unknown; this only wakes a reader and never clears the incident.
- Five-minute collection is enforced on automatic guidance reads, not only watcher sleep. Explicit refresh remains immediate. Real Agent launch, runtime delivery, filesystem isolation and HCU training still need site-level validation; session/owner strings are attribution, not authentication.

- Operator parallelism clarification: independent attention/GEMM/MoE implementations can run complete local optimization loops concurrently. Added operation-scoped resource ownership so a long-lived operator Agent takes the shared GPU lease only during actual measurement; assignment-scoped exclusivity remains available for experiments requiring continuous ownership. Shared interface edits and integrated numerical/performance regression remain coordinated.

## Official and experience Wiki audit

HCU-Knowledge v0.5.3 published first (80da7cefc). Its online GitHub and internal GitLab chain verified. Hyperloom experience_sink/reader/integration separate implementation identity, measured correctness and warm-start revalidation; TrainFlow adopts evidence-bound environment/model contexts, durable milestones and negative results, without importing its kernel-specific runtime. New Wiki source inventories revealed upstream canonical repository migrations: hiyouga/LlamaFactory, areal-project/AReaL, verl-project/verl. Old source IDs and fixed evidence remain; canonical registry names updated.

- Megatron PR #7897 demonstrates description drift: initial description proposed config switches, final diff uses device-selected fixed launch settings. Authored case distinguishes source claims from final implementation and from HCU validation.
- Public Wiki and private experiment Wiki are separate durable assets. Report/flow milestone capture does not manufacture metric units or numerical validation; cookbook delivery records link back to immutable experiences and preserve publication status without exporting raw data.

## 2026-10-09: pre-environment correctness review

Confirmed and repaired boundary failures, with reproductions and regression coverage:
- Watcher stall/recovery clocks incorrectly moved with the last-1000 sample window; short-file rotation could go undetected. Preserve per-attempt progress and file identity/prefix state, migrate existing observations.
- Report/health/quality paths differed on positive integer execution and required coverage; legacy malformed PASS and context A→B→A could revive stale evidence. Apply consistent admission and reset-generation eligibility.
- Claimed checkout/resources were task-local; unassigned commands could bypass reservations. Coordinate explicit scopes across the workspace, and recheck late/transitive input blockers at acceptance/use.
- Reconciliation of an interrupted operation could drop its budget reservation. Retain labelled conservative budget accounting separately from measured duration.
- Unchanged Wiki refresh could clear review after local edits; search could use another checkout's/stale index. Bind page/workflow hashes, propagate edited/new topics, and select an immutable local generation per query.
- Concurrent experience retries could create duplicate records and overwrite navigation; interrupted publication/rebuild could lose event mappings. Serialize canonical identity/publication and recover from retained records.
- Online PR fallback did not propagate partial failure to CLI exit status; combined multi-repository display truncation could appear complete. Both are explicit now.

Readiness boundary: protocol/unit fixtures and public Wiki retrieval are locally testable. Site commands, HCU kernel traces and numerical convergence, native Agent wake-up, site recovery ownership and real multi-node fault injection remain environment integration work. No real training measurements were fabricated. No HCU-Knowledge update or TrainFlow release/tag.

## Detailed workflow mapping

Existing README/architecture/team diagrams were summaries. The new workflow map separates system tuning, shape-bound efficiency assessment and implementation validation; distinguishes local iteration from stage loss; and maps full-mode report gates directly to core.GATES. Agent scheduling, file guidance, remote execution uncertainty, site recovery ownership and knowledge updates have separate views so readers can trace dependencies without assuming a built-in model runtime or validated site deployment.

## User-supplied end-side workflow comparison

- Comparison scope is the supplied hygonpilot-skills illustration, not an audit of its repository or actual execution. Its visible strengths are explicit framework/communication/Triton/kernel routing by expected end-to-end benefit, startup-versus-steady-state benchmarking, rollback/best-known records and a dedicated regression-bisect entry.
- TrainFlow already has the environment/baseline/profile/optimize/regression cycle, system-first analysis, lower-level kernel Skills, profiler-off repetitions and retained candidates. Its additional explicit scope is training parallelism/memory, gradients/optimizer/stage loss, actual process groups, dynamic multi-Agent dependencies/reviews, remote execution uncertainty, scaling/long-run recovery and official/private knowledge lifecycle. Features absent from the supplied drawing cannot be assumed absent from that project.
- In TrainFlow, prioritization and best-candidate selection currently depend on the coordinator and evidence; there is no standalone expected-benefit ranking model or regression-bisect command. Graph-break/AOTI-specific triage and separate cold-start cost accounting could be made more explicit. These are potential follow-ups, not implemented features of this illustration change. Real HCU integration remains pending.

## Torch and communication reference review

Inspected the user-supplied hygonpilot-skills at 3b949665dbb74a2340f8a257345bb0672e37f08c, specifically the coordinator, framework, communication and Inductor guides. Useful mechanisms: execution-path classification, cold/steady separation, evidence-ranked routing, communication readiness/chunking and best-known rollback. Inference AOTI, request-serving benchmarks, fixed environment knobs and GPU-only timing are not general training defaults. Re-expressed guidance independently; private reference checkout remains ignored and its knowledge layout is not imported.

HCU-Knowledge current local search succeeds; Galaxy results reinforce version-specific queue/stream semantics and preservation of historical API boundaries. Existing full installation did not require the domain KB; this is a real installation gap, not only wording. Reuse the existing checkout without fetching upstream knowledge or duplicating originals.

Installation review also found unnecessary full historical validation on each external-KB reinstall. Setup now probes current index health and snapshot mode before restoring it; first-time, stale and rollback cases still bootstrap. The full local check passed, while future ready-index reuse avoids that repeated cost. HCU-Knowledge source/knowledge content is unchanged.

## Real environment: reusable findings

- Nested SSH execution and ProxyJump have different authentication locations; preserve strict host identity and existing credential boundaries.
- Runtime/library activation differs between host and container; import-only checks may still access GPU devices. RDMA sysfs naming alone does not determine IB versus RoCE.
- Source transport needs Windows Git executable and symlink semantics; content snapshots preserve internal-link provenance without assuming writable alias semantics.
- Modern model-builder paths can bypass legacy audit hooks; validate actual parameter placement through initialization, precision wrappers, DDP and optimizer construction.
- Real training observation must separate initialization from progress, source clocks from collection clocks, and verified child exit from process disappearance.
## Real-environment integration lessons

- A successful transfer hash is not enough when nested repositories contain Git symlink placeholders or executable files. Read the owning index, preserve link provenance and reject unavailable child metadata rather than accepting a parent repository fallback.
- Distributed training may print progress on the last global rank. Verify the engine logger and monitor every required member independently; progress from one rank cannot certify all workers.
- A paused collector can be detected and recovered without signalling training. This demonstrates collector-health handling only; training restart, notifications and Agent wake-up require their own deployment and evidence.
- The same source with different audit/profile settings is not one performance cohort. Keep initial state, input sequence, optimizer configuration, parallel layout and measurement mode explicit when comparing optimization and loss.
- Small native FP32 parameter groups can coexist with mixed-precision optimizer groups. Main-branch checkpoint qualification must preserve their actual optimizer ordering; forward/backward success alone does not demonstrate save or restart correctness.
- Offline plots must distinguish missing samples, copied heartbeat state and actual fresh metrics. Hashes bind the retained bytes; chart appearance does not establish quality or performance acceptance.

## Performance discrepancies require follow-through

A test can execute correctly and meet an old floor while a credible reference gap remains unexplained. Environment assessment now accepts a typed, evidence-linked unresolved discrepancy and preserves incomplete status; failed matched thresholds remain failures. The Agent must inspect original units/conditions, actual transport/library implementation and authorized bounded alternatives. Logical HCA/bond counts do not establish physical-port bandwidth; count actual active members and collect their traffic/error/congestion deltas. A/B/A is bounded diagnosis, not a replacement for repeated optimization comparisons, production network acceptance or model-level loss checks.

The validator checks declarations and retained evidence references, not the truth of engineering reasoning. Removing a discrepancy field cannot by itself close an investigation: original reports, trial evidence and independent review remain required through the existing flow and private experience mechanisms. No new workflow state machine or automatic site-setting mutation was introduced.


## 2026-10-10：全参容量预估与多实例优化

用户补充：先用 HCU Train Sim 等判断完整模型可行性，卡足优先全参，卡不足才缩 layer；资源富余时独立完整模型实例并行优化，明确分工和及时交流。已核对公开模拟器 b7d8e6f3（CLI/adapter/模板），并修正 proxy/adapt 的旧“优先缩层”措辞；协同协议沿用现有 team/lease/inbox，新增实践、更新阶段 Skill 和可编辑流程图。预测不作为硬件或全模型验证，当前 Kimi K3 模拟覆盖仍需核实，实际实验继续。


## 2026-10-10：HCU底层工程联动

按用户要求将HCU Primus Turbo、UCCL、UltraEP、MoonEP纳入按瓶颈选择/复用/修改重编/分层验证/目标PR的链路。已检索HCU-Knowledge保留报告，明确通用与专项分支和接口边界；HCU问题先查询大知识库，同问题已取回证据可复用，不触发大库更新。训练引擎与容错项目不扩名单。


## 共享检索与工作流泛化边界（2026-10-10）

wiki-search 实际只索引 knowledge/**/*.md。中间试验即便写了待验证仍会影响后续检索，应在入库前筛选。通用操作方法属于 docs/Skill，执行细节属于任务配置；共享模型页需最终优化结论与关键数据，不能把每个候选当里程碑。已有通信环境知识保留。旧 Skill 名通过安装器备份迁移，不保留重复发现入口；底层 CLI wiki-update 的采集语义没有改名。


## 2026-10-10 硬件建模交接与算子阶段复核

- 两节点16卡只读属性与管理工具复核，统一硬件基线；产品标签冲突、旧测量执行映射缺口明确保留。
- 非Adam高贡献模型8项CPU检查通过，主控接受分析阶段；每项工作量、条件效率、余量与下一动作已更新看板。完整优化没有据此关闭。
- baseline初版→HIP优化、现有Triton→Triton优化的交接与负责人验收已写通用Skill；本机三项变更Skill已同步。
- 真实CM恢复密封日志经现有解析/绘图得到3张图、9步记录，历史离线视图不进入实时监控。
- 站点硬件知识及精选6原件随公共工程；全新Store可搜读；独立review唯一来源过度断言已修正。72项相关测试和490页/25来源校验通过，无release。
# Integrated review, 2026-10-10

- Final independent review reproduced and closed two additional gate gaps: legacy loss comparisons could ignore explicitly contradictory initial/recipe identities and grant a new stage; dispatch could bind an old event to a newer context or revive local events after A→B→A. New stage-quality PASS requires retained comparison inputs and recomputation, context/candidate binding and registered raw evidence; legacy window results remain readable but ineligible. Local event sequence and expected execution context/epoch now protect dispatch; imported remote sequence still requires actual attempt/job reconciliation.
- Final source/install acceptance: six Skills retain portable project bindings; all 68 curated originals, images and attribution files survive an actual source distribution; PR review rescans authored pages and rejects superseded public evidence; complete installation uses one strict knowledge-readiness check. New takeover/quality documents participate in source-to-workflow maintenance mapping. HCU-Knowledge was not refreshed.

- Baseline full suite: 964 passed, 4 platform-dependent skips. Source/Skill audits found explicit-status numerical false acceptance; candidate step values could compare equal through Python bool/float coercion. Fixed with affirmative status validation, typed evidence/series/steps and regressions. Added optional predeclared MAD timing gate and explicit initial-state/recipe identities for new stage A/B contracts; historical contracts retain limited, stated scope.
- Handoff findings: installed workflow Skills lack checkout binding; standalone environment/optimization instructions leak full-task obligations; stage A/B needs a directly discoverable same-state procedure. Added a common agent playbook and mode-specific branches; installer binding is being implemented independently.
- Runtime reviewer reproduced unresolved work hidden by terminal flow state, operation path collision, invalid lease TTL, control-plane gate bypass and dispatch claim stranded by preflight failure. Installer reviewer reproduced missing retained evidence in sdist and newly associated pages omitted from PR review. Repairs are scoped to those paths with CPU regressions.
- Inspection errors were local only: PowerShell does not expand Bash-style brace paths; a guessed ci.yml name was absent (actual workflow discovered from .github/workflows); one patch hunk matched a partial line and was retried against its exact section. No remote operation or source content was affected.

- Starting tree is clean at 01f7bd2; project declares 0.4.0.dev0, only v0.1.0 is tagged. User now explicitly requests a tag after review, superseding the earlier no-tag instruction; no GitHub release is requested.
- Existing instructions cover many real-environment lessons, but accumulated guidance and persistent phase state must be checked together for a fresh Agent handoff. In particular, bounded diagnostics under an incomplete environment gate must not silently become a qualified full workflow.
- Preserve documented limits: the validated setup is SSH + Docker with a reduced model/workflow proxy; physical local shutdown, other execution adapters and full-model convergence remain distinct from CPU tests and bounded recovery drills.

## 2026-10-10：0.5.0 文档一致性复核

- 工程介绍按任务的输入、判断、证据和产出组织；正式流程与实际硬件验收范围分别陈述。
- 旧总览中无条件“恢复完整模型”和“本机离线后守护继续”容易产生误读：现在区分完整目标与获准代理，以及已部署验收的远端守护。
- 代表 rank 采样与 TraceLens 完整 collective 报告分开；后者需要全部 0..N-1 rank 文件及实际进程组上下文。
- 算子同形状独立实测与上限建模可并行，优化按实际占比和剩余空间推进；完整数学库 bench 命令、baseline/HIP/Triton 衔接及阶段质量重算进入详图。
- 主图由 built-in imagegen 更新并人工检查，复现提示保存于 docs/assets/workflow-overview.prompt.md；精确分支以可编辑 Mermaid 和文档契约为准。

## 2026-10-10：更新 Skill 与安装器分工

原 README 的总览主要展开优化，环境适配及扩容持续容错缺少同等清晰的入口，现已按三阶段重写。--replace 是将已核对的源 Skill 同步到安装目录，不承担上游查证或内容更新；更新 Skill 此前未明确同步本机收尾，现已补齐。旧 prepare/operate 入口已不存在，安装器仅保留识别历史目录的兼容。新替换先保留旧内容，全部哈希/绑定验收后清理本次备份；历史备份不自动扫除，避免删除之前失败安装的恢复材料。

## 2026-10-10：诊断方法与命名复核

- HCU-Knowledge 已查 runtime-failure-triage、RCCL/rccl-test、Cluster Manager 与 hcuprobe 总览/专题、PyTorch allocator 生命周期，以及 DTK26.10 hipprof 手册。collective 参数不一致、signal handler、VMFault/assert 和库外分配都有关键适用边界，不能照抄旧故障命令。
- DTK26.10 hipprof 文档保留历史 --input-core 移除/恢复及 --leak-check 修复记录，故工作流先检查实际版本/帮助，再选择采集方式；不混同 hipprof 和 XProf/XCompute。
- 官方交叉核对：PyTorch distributed（Gloo monitored_barrier）、memory snapshot（allocator 可见范围）、Linux cgroup v2（memory.events 层级/增量）。具体来源已写入 Skill references/evidence-sources.md。
- 本轮新指南属于文档/源码查证，不表示真实 hang/core/leak/数值/存储等故障已在当前集群复现。适配和优化增加异常分流，通用方法留 Skill，事件原件继续留 workspace。
- 批量编辑曾因主控 Skill 无“运行约定”标题中止；检查实际标题后继续，前面成功的改动未重复插入。


## 2026-10-10 — 0.5.1 全阶段方法与性能闭环复核

- 固定读取 AMD-AGI/Hyperloom@880c1672a84cb718e48f640def0bd79e24294d44、AMD-AGI/GEAK@ba509ef31d416350269266b626ec455e9d9475d1、BBuf/AI-Infra-Auto-Driven-SKILLS@6dc9c66a008daded66f214022919ff88b2186252；参考克隆只在忽略提交的 .work/references，未覆盖用户 Hyperloom fork。逐项采用矩阵与可追溯源码在 docs/practices/performance-methods.md。
- 采用：初始/最佳/候选分离，按源码/shape/执行结构刷新 profile，映射/正式/计数器/计时分离，热点源码/重叠/融合三表，dispatch 先验，完整 API 成本，条件性整步上限，组合验证和有界策略转向。已有动态并行、热点90%、三项算子 Skill、数学库 tune 和阶段 loss 沿用。
- 不照搬：TP=1 推理限定、固定0.5%/5%门槛、AMD峰值/计数器、推理移除autograd、每轮清缓存、把区间重叠等同因果隐藏、无差别重试/固定Agent人数。低GPU占比不自动定性CPU瓶颈。
- HCU大库只读核对：xprof-xcompute-workflow、hipprof-2610-metrics、infra-resource-critical-path、rocblas-kme-padding-contract、pytorch-memory-stream-graph-lifecycle、torchcomms-async-functional-watchdog、verl-ppo-grpo-worker-chain、verl-weight-sync-checkpoint-lifecycle，并沿用上一轮 runtime/RCCL/Cluster Manager/转储内存资料。
- 故障方法补充：假设及反证、可重放条件、采集缺失的降级、有界版本二分、节点/绑定交叉矩阵、四种异步完成、RL worker/同步/峰值/恢复边界。适配补能力分层修复、graph/backward初始化，性能异常与统一主控互通。
- 发现并修复 analysis.model_operator 中 slowdown_threshold 不做有限性校验、其他阈值在早分支下未验证的问题；增加可复算 bound_terms_us/limiting_terms/算术强度，允许copy的零FLOPs，拒绝派生溢出。标签保持条件模型而非物理瓶颈。
- 独立只读前向检验：graph/eager与过期shape、噪声小收益候选、OOM累计值/异步wait/混合attempt场景均正确保留证据缺口；20步合成trace计算并集74%、未解释26%、覆盖目标未达。未发现可行动的新问题。不是新HCU现场验收。


## 2026-10-11：Skill 阅读分层与安装一致性

- 已核实本机 Python editable 包绑定 D:/codex/projects/HCU-TrainFlow，六个系统 Skill 通过 workspace.json 绑定工程；docs/Wiki 不复制进系统 Skills，需保留 checkout。
- 方法来源页与执行 references 职责不同。补充 docs/skill-reading-map.md，前移工程定位，明确按模式和条件读正文；详细文档链接不会自动注入上下文。
- 独立阶段 references/workflow.md 的旧提示只提显式路径，现统一补充 workspace.json 绑定，避免与入口冲突。
- 更新 Skill 原收尾仅针对 Skill/reference。现所有本仓维护接入 sync_local_install.py，刷新 editable 包与六个入口；只读检查不安装，不更新第三方或大知识库。依赖清单变化仍走完整安装。
- 安装器迁移 hcu-train-optimize → hcu-train-analyze-and-optimize，无旧别名；缺资源、安装漂移、错误绑定有非零检查。完整安装和 CI 增加阅读资源检查。


## 2026-10-11：整体契约复核（进行中）

- 已确认 flow.next_step 用内部阶段代号拼接Skill名，产生已不安装的旧入口，说明只扫描完整名称不足。此次应以实际返回值和安装资源进行行为验收。
- 主控目前普遍要求TaskSpec/flow-start；仅交付用户patch应明确直接复用阶段交付规范，不伪造环境或stage-quality报告以绕过训练状态机。

### 已确认的边界与修复

- 运行时与安装器复用 `skill_registry.py`；真实 CLI + 临时安装目录的 8 项新场景原先全部失败，修复后通过，覆盖六种模式、完整七次转换和候选报告被替换后的 repair。完成/取消不会再误发适配入口。
- 独立审查复现现代观察缺省 `timestamp_basis` 被当作源时钟，缺原始字节范围/封存仍 `completion_verified=true`，也可产生伪 slowdown。仅现代明确 source-log-clock 才进入源时钟路径；未知时钟完成需原始范围+已核验封存，绘图一致。持久进度版本升至 4，从保留事件重算，回归覆盖旧版错误状态升级。
- 独立审查复现从工程外执行完整安装、使用相对 skills_dir，子进程实际位置与 ready 回执不同。入口统一归一化目标；新增真实安装器的 11 个合成 Skill 回归，外部包/Git/KB 操作模拟，未触碰外部仓。
- 交付-only 正向走读：主控→阅读导航/接手指南→change-delivery→所属阶段相关契约可闭合；无硬件时保留未验证项并按目标仓规范 draft/阻塞，不建无关训练状态机，不新增 Skill。
- 复核模块边界：执行权限/租约/未知结果核销、上下文/候选/独立审核门槛、数值输入和阶段 loss、团队依赖与资源范围、持久监控、局部 Wiki 更新哈希、本机安装绑定和文档读取路线。未给缺证据的猜测追加修改；合成/CPU 回归不等于新增 HCU 实测覆盖。


## 2026-10-11 TraceLens 真实资格与方法复核

- BW1000_H/gfx936、DTK26.10、Torch2.11.0/HIP7.2.26365 空闲设备完成 eager/fwd+bwd Graph、真实值 EventReplay、FP32/BF16/copy calibration；原件在任务私有 workspace。同期占用检查避开已被占用节点。
- hipprof 原始 JSON 与真实 binary pftrace 经官方 Perfetto 转换后六张表一致：92 kernel、18 copy、26 memset。发现 procId 可能为 autograd worker，关联须用 pid/index；整数纳秒不能被微秒显示舍入取代。
- XProf3.16.0/aqlprofile3.6.2 初始报 Cannot open mem；专用临时容器 /dev/mem+SYS_RAWIO 与 hyhal只读后 counter/SQTT实采成功。XComputeLight4.8.0读perf导出10CSV成功；N/A、无单位SQTT列与额外replay时间不可当零或无profile基线。未修改已有训练容器。
- 原生Agent分类成功但发现缺失列被当0、CPU时间回退为GPU时间、旧输出可能复用；这些影响解释的缺口分别修正。Qualification probe逐步同步，其88.69%idle不能当生产训练瓶颈。
- 实测4096GEMM envelope不能假定512×768×256调用可达，自动headroom仅条件筛查，3个mm支持/7项unknown不掩盖覆盖缺口。
- 同名kernel可跨shape/phase，TrainFlow模型新增精确key或applies_to契约。保留初始oracle、profiler-off配对、阶段loss、实际rank组、单一恢复owner等合理流程。
- 外部主源复核涵盖PyTorch FSDP/compile实战、FlashAttention IO、AMD FP8组合消融、MLPerf训练Graph；不复制推理窗口、固定阈值或NV/AMD峰值。详见docs/practices/performance-methods.md与私有method-review.md。
- Wiki旧e4基线与依赖f22存在漂移，增加明确dependency_sources关联校验；来源升级需要同步当前页面、inventory、文档证据和维护目标，历史固定证据可保留。
- 同仓联动复核发现 Megatron profiling 专题也保留旧的 Windows-only 补丁描述；已与工具总览共同更新并绑定当前依赖，不能只修其中一页。
- 独立审核补齐原生 Agent 的来源、CSV、架构、代码、metrics、findings 与报告内容绑定；comparative 模式绑定两侧 CSV 及比较利用率。`run` 不自动认可旧推理，需活跃 Agent 显式 review；输入变化后回执失效。
- 发布后的 TraceLens `30f5dcd539dd4e588678e34168c7fcf726dd987e` 已在空闲 gfx936 上重跑 captured-value mm 回放，数值通过，10 个同步 device-event 样本完整；结束后无 KFD 残留。此计时不是源 trace 单 kernel 的相同范围，不据此计算模型拖慢倍数。
- Linux CI揭示旧DeepSpeed PR链接大小写与Git目录不一致；Windows路径存在性不能单独证明可移植。链接已修复，知识校验器先保留书写大小写再核对每层目录，避免resolve规范化掩盖错误。


## 2026-10-11：Wiki 内容筛选复核

站点正文夹带用户继续执行的决策、临时容器/端口和排期；这些归过程档案，复现身份及证据仍保留。document_globs 的广匹配会恢复单独删掉的生成页，因此加入 document_exclusions（路径模式→复核理由），并阻止与既有 ledger 冲突的自动同步。仅排除 DeepSpeed 的 CIFAR/GAN/Azure 入门和 SGLang 前端语言三篇，共六份来源页；源码树、PR、性能/训练资料和原始站点证据均保留。内容价值由 Agent 判断，程序仅执行明确范围并校验一致性。

## 2026-10-11：介绍性文档一致性

- 工程介绍和细图仍标 0.5.0，未跟上当前主线的 Graph、Roofline、EventReplay、原生 Agent 和 HCU profiler 集成；首页过早引出工具，第三方 README 仍只写报告 API。
- 架构图将私有任务 experience 称作另一套 Wiki，遗漏共享知识提升条件；仅交付路径未画出，分析细图会让只分析请求先经过布局候选实验。
- 本次按已实现方法修订分流，增加 TraceLens 图 3.6，明确工具生成、Agent 推理/复核及实际训练验收分别判断；扩容、监控及资格范围保持既有证据边界。
- 收录范围/带理由排除、同仓关联复核、本机安装同步进入知识维护介绍；保留完整源码导航，未刷新 HCU-Knowledge 或外部来源。

## 2026-10-11：0.6.0 全工程审查

- 总览位图已无版本号，但 workflow-map.md 导语与生成提示词说明仍标工程版本；这些移除，图面不因发版反复变化。包、README 和 changelog 作为发布版本入口。
- 优化 Skill 仍有“两个报告入口”及按先融合后建模理解的编号顺序，须与新 TraceLens 条件入口和实际按瓶颈推进统一；先核对具体文档再修改。
- 查询不存在的 skill_ids.py 一次，实际共享入口在 skill_registry.py；已按文件清单定位，未影响工程。

- 确认并修复四项真实问题：截断 RCCL 热点先走通信豁免导致 complete；returned 成员收到晚到 blocker 后连 revise 都不能执行；flow 登记后初始化中断导致重试遗漏 draft→prepared；无 flow 或重规划前上下文 A→B→A 导致旧消息重新有效。
- 重入仅补初始化，不覆盖 GUIDANCE 或复活轮次；缺失已登记指导要求恢复。返工仅放行 revise，finish/accept/依赖 gate 不放宽。消息用原始事件顺序与 context epoch 校验，无数据库结构迁移。
- 统一仅分析、独立优化、全流程质量验收分支；修正 TraceLens 入口数量、同名模型的适用条件、现代日志源时钟与有界恢复资格说明。保留原有按瓶颈推进、并行隔离、未知执行核销和单恢复 owner 方法。
- 全量本地回归 1167 passed / 4 skipped；跳过项为 Windows 上不能执行的 Linux AF_UNIX/spawn 资格用例，交由 Linux CI 验证。独立成员针对修复复核及73项流程/团队、6项截断通信测试通过。
- 自有16张 Mermaid 解析/渲染全部成功，总览位图人工核对无版本；固定保存的上游知识图保持原件。63份介绍/指南/Skill Markdown 中390个本地链接和锚点通过；489页/25来源知识校验、59阅读页/78可达页通过。


## 2026-10-11：工作流效率复核

- 程序真实重复：完整流程基线通过后，进入 profiling 仍需为相同 baseline 再提交候选、再审核；现仅对紧邻且未变化的基线交接复用原 review，保留原状态、报告和原子审计事件。新报告、指导、分工、上下文或未核销执行均不能借此通过。
- 程序迟报：候选报告/快照/迭代不合约时，先发 review 请求，等 accept 才发现缺口。现提交及 flow-next 先预检，不完整候选直接 repair，不占 reviewer；审核后仍再次校验。
- 文字上的低效风险：将每次小实验读成独立候选、把完整热点表读成首项优化前置条件、每个重要实验重复查库、成员验收后整体重复全审、未来阶段 required 任务阻塞当前提交。统一候选粒度、按影响复验和滚动派发，不新增审核层或 Humanize 依赖。
- 环境按首批实际分配资源开始，复用匹配且有原件的既有验收，新增节点/变化项在接入前补验；实时占用/身份仍检查。扩容保留规模/状态/恢复验收依据，诊断按最能区分当前假设的步骤，既有容错不等文档写完。
- 初筛先低成本正确性/短测，正式保留再配对/集成，稳定阶段验 loss；TraceLens 按问题选工具，模型公式未变直接引用。≥90%热点处置、必要 profiler、初始oracle、权限/资源和唯一恢复owner等科学性约束不降低。只交付路径已有受影响验证规则，保留未加训练义务。

## 2026-10-11：临时大文件维护范围

现有 retention 只允许 cache/recreatable 四层路径，所有 checkpoint 扩展名均拒绝；单树全内容哈希并限制 10 GiB，不适合失效 checkpoint/core dump 的大体积回收。复用原登记、使用 pin、Store 操作核销、计划哈希、隔离和回执机制，增加专门临时产物目录与明确退役证明。临时大文件只做元数据身份检查，前提是写者停止、消费者释放 pin、关键原件/摘要留存；不把该检查当 checkpoint 完整性验收。运行/未知作业仍保守阻止删除，空间检查持续可做。

用户补充要求减少扫描：维护独立于300秒交互采集，采用实验批次/阶段/恢复收尾触发与默认6小时周期，持久冷却状态让重复 tick 不遍历文件树；阶段/空间触发也有1小时冷却。大写入前只查文件系统容量并另核查配额。正式保存点仍由引擎/站点策略管理；仅已明确废弃的临时产物退役，默认1小时宽限，任务最终收尾明确策略可设0而不绕过其他检查。处置记录限1 MiB，防止维护反复读大对象；重新退役保留旧依据并重置宽限。

## 2026-10-11：Wiki Skill 的名称与内容范围不一致

中文菜单来自 TrainFlow Skill 的 agents/openai.yaml display_name；HCU-Knowledge 两个 Skill 没有这个覆盖，name 已是英文 ID。两个现有 Wiki Skill 的正文和 wiki-search 已涵盖官方资料、通用站点经验和最终模型总结，但入口名称/简介、部分导航仍称官方训练引擎。共享入库主要由 Agent 筛选；report/flow-advance 的 experience 自动记录仅落任务 Store，不能冒充已入共享 Wiki。需要把任务初期与最终收尾的调用责任写清并提供不阻塞训练的程序提醒。

## 2026-10-12：官方页面回退

capabilities.md 此前最近修改于 v0.6.1，v0.6.2 未单独同步 Wiki 命名/维护时机。CLI 线上自动回退仅针对 PR；Releases、roadmap Issue/Discussion/Project 与未登记官网由宿主网页工具按需查证。已实查 NVIDIA/Megatron-LM releases、roadmap issue 5676 和 verl Megatron 模型扩展官网/仓内原文，入口可读；不据此宣称全部官方网页已自动索引。

## 2026-10-12：精度诊断缺口

现有方法分散在 training-state-validation、三个阶段 reference 和质量比较程序中，缺统一的有/无 NV 路线及 Probe 可用性/采集判读。HCU-Knowledge dcu_probe 固定 b8dddb57 当前包为 hcu-probe、import/CLI 为 hcuprobe，目录迁移至 python/hcuprobe；旧 dcu_probe 示例不可机械照搬。Probe 统计、摘要和实体数据能力不同，空匹配不通过，异步 clone/flush 会影响显存和同步，跨 rank 首差需通信组元数据。

保持六个 Skill 数量与 QualityContract 阶段门槛不变，新增跨阶段方法正文并接回阅读链；不把无 NV 的重复一致性写成正确性或跨平台等价。

### 精度方法最终复核

- 原有质量代码保留真实候选、同初态/配方、样本与原始对照重算；日志/长稳监控保留非有限历史，不因后续有限采样清除异常。本轮未发现需要修改这些门槛的缺陷，保持运行逻辑。
- 方法须区分初始基线通过、未复现旧异常与找到首差；流程图补直接返回阶段的正常分支，间歇问题仍保留。动态 loss scaling 的跳步需要核对状态与参数是否更新，不把所有溢出等同于不可恢复故障，也不消除原始告警。
- 共用指南放 docs/practices，由六个既有入口体系按需路由；不增加新 Skill，不把具体排查中间件放共享 Wiki。维护关联覆盖相关官方源码与三个阶段，HCU Probe 当前接口另按大库/现场源码查证。

## 2026-10-12：总览图的信息层级

总览无需枚举具体算子库/通信库；概括优先复用、能力或性能不足时基于对应库实现，并链接现有详细联动指南即可。扩规模与长稳部分需显式写精度/loss及恢复后的复核，交付需覆盖训练引擎及相关库/工具的责任归属、跨仓 PR 依赖和验证。保留原操作方法和运行边界，未增加阶段或修改执行逻辑。新版总览图采用更细边框/箭头和低饱和配色，深色文字维持可读性。

## 2026-10-12：TorchTitan 当前主线入口

官方 README 当前已采用 MODULE/CONFIG 选择 Python recipe，支持预训练/SFT 与 TitanRL，模型/并行/底层依赖必须以固定主线源码确认。历史 TOML/旧路径不可直接当作当前命令；官方 README 的支持或跑分不代表 HCU 已验证。将完整目录、正文精读与 PR 原文采集区分。

### TorchTitan 初步源码核对

- 固定主线 65aaaa960698ab5d6e98c874177b41b9c30e9c58。官方 Releases 最新非预发布 v0.3.0（2026-09-03），当前 main 的 assets/version.txt 仍是 0.2.2；版本文件不能替代发布查询或固定提交。
- 现行调用链为 ConfigLoader → Trainer → TrainingEngine；训练行为由 Python recipe 配置，通用 --section.option 已不支持。模型 config 在构造时按 parallelism 分片，改变 CP/EP 等必须重建配置。
- EP 从同一 dense world 切出 sparse mesh，不额外乘进 world_size；global token loss normalization、HSDP 梯度同步、torch_remat 区域与副作用要按现实现记录。
- Fake PG / real-PP-fake-SPMD 仅验证有限配置、形状/显存路径，不能提供真实通信、loss 或吞吐结论。官方文档和当前源码也有历史表述差异，作者页明确以符号实现校核。

### TorchTitan 优化与验证边界

- 官方当前 CUDA graph 检查明确排除 ROCm；Kimi K3 的 DistMuon recipe 对 TP>1 报错，不能通过换 AdamW 掩盖训练语义变更。
- #5033 的独立 Attention Residual Triton fwd+bwd 比 local compile 快，但指定端到端 debug 实验更慢；#5266 的视觉 CP 改造通信量减少，也没有直接带来 step 提速。把 kernel/collective 局部数据与模型结果分别保留。
- #5137/#5250 的 WGRAD 优化依赖 AccumulateGrad 的 buffer 重挂接；分离 backward、tracing 和数值舍入必须一起看。#5107/#5268 的 RL 内存优化分别改变 trainer CPU staging 与 generator FSDP group 加载，不是统一开关。
- 所有新来源通过既有动态 registry、全文索引、在线 PR 与固定代码链路工作，不需新增搜索后端或安装训练框架。Release/roadmap 由 Agent 定向核查，CLI 文档/PR 增量采集不等于自动理解所有新功能。


## 2026-10-12：工作空间写入边界复核

- 清理已经由 retention 的登记、pin、活动/未决作业、隔离和身份检查约束；缺口是其他阶段、成员和安装/Wiki 维护没有统一写入范围。采用一份共用指南和六入口短规则，不增加任务状态或逐命令审批。
- command-plan 的 cwd/argv quoting 只确定执行位置与参数，不是文件系统沙箱；不能自动阻止第三方工具向绝对路径写入。映射与隐式缓存须由配方/部署核实，必要时结合只读挂载和权限。
- `_new_transfer_destination` 原先先 resolve，能够把悬空目标/父目录链接解析到未预期位置。改为解析前检查各级 symlink/reparse point 与 ..；只修正意外重定向，不宣称抵御并发父目录替换。
- TraceLens 已有报告输出隔离，但 Python 临时文件和 Matplotlib 字体/XDG 缓存仍可能继承宿主默认路径。两个受管离线 worker 统一在当前报告目录定位这些输出及转换缓存，保留 HOME 和主进程环境。
- 复核源码快照/接收、命令组、任务与 Agent 范围、观察器、临时 IPC 探针、retention 和 Skill 安装备份：保留已有生命周期/归属检查；普通执行、正式 Wiki 维护、安装升级采用不同明确目标，不把所有写入强行锁在 SQLite Store 下。

## 2026-10-12 Wiki 均衡维护开始
当前 main=55fb210，版本0.6.5，工作树干净。已有 Megatron/TorchTitan/TE/cuDNN多专题，其他引擎多数单篇，需要按内容维度补齐而非凑相同页数；新增来源更新须走原有采集/复核协议。
# 2026-10-12 HCU-Knowledge 更新后的前置影响复核

- 只读基准为 HCU-Knowledge `4596fd4365805696b17ed312d34822e042f6e339`（0.5.4），覆盖本轮正文变更与三个阶段的现行依赖。未更新大库、未运行远端训练。
- 本机六个 TrainFlow Skill 与维护前 HEAD 一致，三算子 Skill 与 `cuda-optimized-skill@f39ba95` 一致，两个 HCU 知识 Skill 与当前大库一致；绑定均正确。系统 Python 的三个 editable 包来自预期 checkout。问题是 TrainFlow 的 HCU-Knowledge 安装锁仍指向旧提交，已调整；外部绑定继续复用现有知识库，不另建副本。
- Cluster Manager：更新入口已登记，但需要补足 schema 2.0 实际类别、BLOCKED/INCOMPLETE 可能 exit0、旧选节点/doctor 入口撤除、RCCL 独立峰值与真实 size、Docker 替补准备与旧进程退出的边界。已经联动环境页、工具 Wiki 与诊断指南。
- 训练/推理：Megatron、Bridge、DeepSpeed、verl、Slime、AReaL、SGLang、vLLM 的实际 HCU 分支、父仓 gitlink、插件与基础包须成组核对；近期存在模块迁移、旧开关删除和功能撤回。未发现 TrainFlow 强制安装这些旧版本的脚本；加强制品/配方与当前支持检查，不把私有源码复制进公开 Wiki。
- 库与编译：复核 TE、Primus Turbo、AITER、BoltOPs、CK、Hytlass、FlashAttention、Moe、Triton、TileLang、FlyDSL、XLA；补真实 grouped 参数、forward-only/反向、输出初始化、内部累加与包装布局、机器事务和资源口径。通信侧复核 RCCL、DeepEP、rocSHMEM、MoonEP、UltraEP、TorchComms 的依赖/后端/完成语义，不把拓扑专项泛化为全平台能力。
- 诊断与工具：Probe 现有 b8dddb57 入口及 XProf/XCompute 与 DTK26.10 hipprof 的区分仍适用；保留原现场验证范围。Primus Safe 工作负载创建与通知送达、UID 及镜像依赖分别验收；检查完成不等于本轮实测通过。
- 安装比对原始清单在忽略的 `.work/wiki-maintenance/install-preflight.json`。新正文及 Wiki 汇总完成后重新整体安装验收，而非提前同步半成品。

## Balanced Wiki: final content review findings (2026-10-12)

- All 27 sources have fixed acquisition/review baselines. The 22 reading groups share nine content dimensions; 99 authored pages and 27 workflow targets have current content hashes. Equal coverage dimensions do not claim every model, backend or upstream file has been deeply read.
- Fixed two demonstrated maintenance gaps: coordinated content acquisition now uses the inventoried commit; a first authored-page review is required even when upstream hashes are unchanged. Regression tests cover branch movement and missing first-review receipts.
- Review examples: Megatron Paged Stash documentation and configuration have different scopes; its historical launch PR description mentions configuration fields absent from the final implementation. SGLang cache-flush failure can leave new weights loaded; per-runner partial-update tracking remains an open proposal. TE RMSNorm/MXFP8 fusion has explicit layout/numerical constraints and review discussion questioning performance estimates. DeepSpeed offload safety remains tied to storage/stream ownership.
- HCU source/branch references are evidence-qualified, not deployment locks. RCCL points to the DTK repository, separate from rccl-test and ROCm references. The broader HCU-Knowledge update was consumed read-only; its private bodies and credentials were not copied into public Wiki.
- Retained PRs are searchable source evidence, not automatically authored cases. Twenty-one directly cited PRs were reviewed against current related pages, with 244 page bindings; other collected PRs retain source-reported status. Full repository path inventories remain available even where file-level curation is deferred.
- Local full suite: 1262 passed, 4 platform skips. Twenty-two representative engine/tool queries and cross-engine retrieval passed. Existing installation upgraded to 0.6.6; all 11 required Skills verified, six TrainFlow Skills synchronized. No new GPU qualification.
# Wiki layout and ownership audit (2026-10-12)

- Current layout splits authored knowledge between official-*-wiki, engines, ecosystem and tooling; generated PR/doc/source-map pages are elsewhere. Raw evidence and generated reading pages have distinct purposes, but project entry/ownership should be uniform.
- User requests project-first organization comparable to HCU-Knowledge, with all consumers/references migrated. HCU repository knowledge belongs in HCU-Knowledge; TrainFlow retains official upstream knowledge and qualified reusable operating/model experience.
- Initial worktree is clean at 4e62412; latest tag/version is v0.6.6. Current local install binds this checkout. Maintenance scope includes checkout and selected installed TrainFlow Skills; HCU-Knowledge remains read-only.
- Official material now belongs to 20 projects / 24 sources. Generated reading pages live beside project explanations; immutable PR JSON remains central. Preserved 5,163 existing page IDs, all 1,203 retained official document bytes and all 3,863 retained raw PR evidence bytes. Retired 31 redundant HCU/source-ledger/release-snapshot files; no source refresh or hardware validation implied.
- Cluster Manager and Train Simulator use explicit HCU-Knowledge project routes. Official AMD TraceLens remains an upstream Wiki; its HCU fork uses fixed dependency/integration contracts and workflow usage docs, without claiming the big knowledge base has a complete fork Wiki. External monitored interfaces and affected workflow targets remain inspectable through wiki-routes.
- Review found two compatibility edges: old workflow-pending paths also need migration, and external-reference must be an accepted CLI filter. Both repaired with regressions. Generated project/global navigation now also gets local-link validation. Old reviewed hashes are retained rather than silently reapproved after relinking.
- Running the real catalog CLI with project `.` exposed relative/absolute path mixing introduced by canonical layout paths. Collection/review/catalog boundaries now normalize the project root; the relative-project retain/catalog/search regression passes. Final full suite: 1,272 passed, 4 platform skips; current version/install 0.6.7.

## 2026-10-13: TraceLens parity baseline
TrainFlow main c504471 pins HCU TraceLens 30f5dcd (upstream c5da90e). Latest checked upstream 493f750 adds 5 commits: test selection, BFS deque, doc dependencies, splitter busy ratio, FP4/FP6 benchmark tile sweep. 13 upstream console entries preserved. Prior real gfx936 qualification covers bounded Graph, replay, Roofline, Agent and HCU profiler adapters, not every native command. Development checkout is older e4e891d and clean; refresh it before editing. Actual Git credential account verified yuguo-Jack; old TraceLens author yuguo, configure development checkout correctly.

TraceLens native gaps found: TraceDiff, TraceFusion and semantic Graph detection only recognized CUDA category names; benchmark idle checks lacked hy-smi and could classify unknown as idle; arch naming guessed AMD from memory size; source artifact discovery lacked DTK component layout. Remote experiments used a dedicated verified shared-task mapping and isolated containers. One node had a driver/runtime initialization failure after a site driver update; another authorized idle node completed qualification. The user-suggested device-number repair was tested only in the task container and restored after it failed; no host driver or other container was modified.

- Final native qualification: real eager/Graph/replay, measured-reference Roofline, six Agent metrics, two-rank RCCL, same-capture hipprof JSON/pftrace equivalence, fresh counter/SQTT, source/index/split/TraceDiff/self-comparison. The three new managed TrainFlow modes also ran against those real traces with the published dependency pin.
- Full Linux native regression initially passed 3,680 tests; reported failures were traced to missing optional parser/dependency/fixtures and two report helper defects, then corrected/retested. Follow-up suites passed 340 (with one newly exposed helper failure subsequently fixed) and 275/1 skip. Final local HCU suite passed 264/1 skip. These overlapping suites are not summed or presented as a wholly repeated full-suite pass. Remaining Windows-only upstream test assumptions are separate from native Linux/HCU qualification.
- TrainFlow review added incomplete states for truncated step ranges, timeline-only comparisons and missing rank activity. Optional OpenXLA xprof pins setuptools below 70; license-file metadata permits TrainFlow packaging with 69.5 without breaking the existing analysis installation.
