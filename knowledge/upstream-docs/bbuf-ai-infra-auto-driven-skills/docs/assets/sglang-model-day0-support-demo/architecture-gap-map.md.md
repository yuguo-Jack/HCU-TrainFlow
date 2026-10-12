---
id: doc-bbuf-ai-infra-auto-driven-skills-a80dbbd117ad62fb6497
title: BBuf/AI-Infra-Auto-Driven-SKILLS / docs/assets/sglang-model-day0-support-demo/architecture-gap-map.md
engine: tooling
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: BBuf/AI-Infra-Auto-Driven-SKILLS
commit: 154cc565d0374746442bac17bd69368b888f4775
path: docs/assets/sglang-model-day0-support-demo/architecture-gap-map.md
raw_sha256: b13d7bb2860424a5199e854c7561345768fb649ebb1ecebdb17d6519331aff07
sources: []
generated_body_sha256: fa5a3c364588e9f74a053b9226b34d6b7ffdfd8c7718db374eca5f475e657212
source_state: current-scan
---

# BBuf/AI-Infra-Auto-Driven-SKILLS / docs/assets/sglang-model-day0-support-demo/architecture-gap-map.md

[Original at fixed commit](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/blob/154cc565d0374746442bac17bd69368b888f4775/docs/assets/sglang-model-day0-support-demo/architecture-gap-map.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Architecture Gap Map

## Capability Classification

| Capability | Audit finding | Class | Fallback |
| --- | --- | --- | --- |
| Protocol | streaming reasoning/tool marker fragmentation | `day0-required` | Hold incomplete markers until the next chunk or stream end |
| Draft loading | remote speculative draft loading | `day0-required` | Download both target and draft through the same public loader contract |
| PD state | recurrent-state transfer in PD | `day0-required` | Disable PD until logical state layout and ownership agree |
| Graphs | CUDA Graph padding sentinels | `day0-required` | Eager execution for padded or unsupported batches |
| VLM release | multimodal image packaging | `day0-required` | Public image must contain processor and vision dependencies |
| Operations | post-Day-0 ownership | `day0-required` | Named public ledger owner and gate-reopen rule |
| Fused recurrent kernel | Shape-specialized decode | `performance-only` | Reference recurrent implementation |

## Evidence

- Evidence: https://github.com/sgl-project/sglang/pull/32541 | state: open | head: f748ae35a26fbe1be98db09967ffb828658b821a | limitation: Kimi K3 is an open hybrid-model precedent and is not shipped evidence for Aurora
- Evidence: https://github.com/sgl-project/sglang/pull/23882 | state: merged | head: 7978aa75e2c16db50f249aa25b9c5678abf6c7d2 | limitation: DeepSeek V4 is a merged compressed-state precedent, not validation of Aurora
