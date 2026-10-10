# Findings

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
