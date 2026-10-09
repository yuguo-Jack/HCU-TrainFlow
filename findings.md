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
