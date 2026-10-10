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
