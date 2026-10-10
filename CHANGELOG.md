# Changelog

## Unreleased

- Expand the README overview into environment/model adaptation, performance and quality iteration, and DP scaling with sustained recovery/observation. Explain content maintenance through the Wiki/Skill update entry and installation synchronization separately.
- Verify all installed Skill files and directory bindings before cleaning backups created by a successful replacement. Preserve originals on failure and leave historical backups untouched; obsolete entry names remain cleanup compatibility only. The Wiki/Skill update workflow now explicitly synchronizes changed local workflow Skills after validation.

## 0.5.0 — 2026-10-10

- Add a complete project introduction covering task takeover, environment acceptance, faithful model adaptation, capacity planning, bottleneck-driven optimization, numerical validation, DP scaling and sustained recovery/observation.
- Refresh the README overview and detailed workflow diagrams, including parallel same-shape replay and operator-ceiling work, baseline/HIP/Triton handoffs, native math-library benchmark reproduction, retained-input stage-quality checks and deployment-specific monitoring boundaries.
- Connect the introduction, editable diagrams and existing implementation guides from the homepage. Align source, package metadata and current documentation on version 0.5.0 without a development suffix.
- Carry forward the reviewed workflow and evidence contracts from 0.4.0.dev1. This documentation/version update does not add new hardware qualification; full-model convergence, new sites and production notification/Agent wake-up still require their own acceptance evidence.

## 0.4.0.dev1 — 2026-10-10 development milestone

- Consolidate entry, stage handoffs, bounded diagnostics, evidence reuse and stopping decisions in the agent playbook. Keep environment-only, analysis-only, standalone optimization and diagnosis within the requested scope; preserve the full-task integration order.
- Bind installed TrainFlow Skills to their project checkout without binding another task's private workspace. Complete installation still includes HCU-Knowledge and the three Hygon operator Skills; querying or maintaining TrainFlow does not refresh the large knowledge base.
- Harden numerical acceptance against non-pass outcomes, malformed evidence and invalid candidate steps. Require retained comparison inputs, frozen initial-state/recipe identities and candidate binding for stage-quality advancement; preserve legacy window comparisons as explicitly ineligible for a new stage. Add a predeclared timing-dispersion gate; keep local correctness, stage loss and long-run convergence distinct.
- Preserve unresolved execution during cancellation and handoff, validate lease lifetimes, and harden execution/Agent event delivery failure paths with CPU regressions.
- Recompute PR review impact when authored pages or source associations change. Include curated raw evidence and overview assets in source distributions, and verify knowledge readiness before complete Skill installation.
- Document the qualified SSH + Docker scope: multi-rank profiling, representative operator validation/modeling, proxy training and a bounded cross-node checkpoint recovery with the launching SSH session disconnected. This does not qualify arbitrary sites, full-model convergence, physical controller shutdown, production notifications or autonomous Agent wake-up.

This tag records a reviewed development checkpoint. It is not a production release or a claim that all planned site integrations have been exercised.

## 0.3.0.dev0 — Unreleased

- Add dependency-aware parallel assignments, atomic scope/resource reservations, native session bindings, accepted-result handoffs and durable peer questions/answers/blockers. Known independent executions can coexist; uncertain remote outcomes still require reconciliation.
- Collect guidance every five minutes by default, with explicit immediate refresh; expose team progress and message receipts on the task board. Reference Multica routing/receipts and Hyperloom implementation ownership without adding their runtimes.
- Add the unified collaborative workflow Skill, with persistent implementation/review/correction rounds, evidence-bound stage advancement, full-goal checks and bounded review failures.
- Add private Markdown boards, preserved human guidance, explicit responses/questions and durable wake-up events; an actual Agent runtime/bridge is still required.
- Rename preparation to `hcu-train-adapt` and operations to `hcu-train-fault-tolerance`, with backed-up installation migration and unchanged independent task modes.
- Reframe documentation around collaboration; add a clearly synthetic, resumable protocol demonstration. Real HCU and multi-Agent deployment validation remains pending; no release or tag for this development version.

## 0.2.1 — 2026-10-09

- Pin the public HCU TraceLens fork while preserving upstream APIs and all native command entrypoints; document capability requirements and HCU validation boundaries.
- Add explicit, guarded upstream-to-fork origin migration and retain upstream provenance in report receipts.
- Monitor both TraceLens upstream and the HCU fork in Wiki/workflow maintenance. Verified the fork's Windows portability fix, native command help and local report paths.

## 0.2.0 — 2026-10-09

- Add independent Transformer Engine and cuDNN Frontend Wikis: source maps, build/test guidance, training call chains, precision/cache, attention, fusion and official tutorials.
- Register official website documents alongside pinned repository sources, with content fingerprints, raw evidence, failure reporting and page/workflow review requirements.
- Integrate pinned TraceLens PyTorch and complete-rank collective report APIs; retain native tables, provenance and logs in private workspaces.
- Add selective thirdparty bootstrap and installation of the three Hygon kernel Skills; HCU-Knowledge remains an optional, separately authorized checkout.
- Validate public dependency acquisition, eight-Skill installation and synthetic trace reporting locally; real HCU profiling remains deployment validation work.

## 0.1.0 — 2026-10-09

- First executable release: five Skills, evidence/task state, explicit execution cards, source snapshots and verified bundles.
- Training-window coverage and operator bounds, complete health coverage, iteration and stage-quality checks.
- Durable normalized-log monitoring, incidents, replay, inbox and operator-configured agent bridge.
- Public official-engine Wiki, ecosystem mechanism cases, SQLite search, staged refresh and top-level PR review capture.
- CPU-only end-to-end demonstration and automated failure/recovery tests. Real HCU/site integrations explicitly remain deployment validation work.
