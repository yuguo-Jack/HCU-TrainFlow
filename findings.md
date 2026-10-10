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
