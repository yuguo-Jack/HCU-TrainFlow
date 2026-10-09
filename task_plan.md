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
