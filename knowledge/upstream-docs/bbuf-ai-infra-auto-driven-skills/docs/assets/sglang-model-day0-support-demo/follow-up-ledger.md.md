---
id: doc-bbuf-ai-infra-auto-driven-skills-28d67e361b0982f7c018
title: BBuf/AI-Infra-Auto-Driven-SKILLS / docs/assets/sglang-model-day0-support-demo/follow-up-ledger.md
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
path: docs/assets/sglang-model-day0-support-demo/follow-up-ledger.md
raw_sha256: 32ef7a60f7abbee45c5546c331375dbfa67135c67f924bb202953a1c2fbe98c9
sources: []
generated_body_sha256: ed02ea3f991e995b158dd1a7a7dccd7391a0750cc0570353fff0584ac71b056c
source_state: current-scan
---

# BBuf/AI-Infra-Auto-Driven-SKILLS / docs/assets/sglang-model-day0-support-demo/follow-up-ledger.md

[Original at fixed commit](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/blob/154cc565d0374746442bac17bd69368b888f4775/docs/assets/sglang-model-day0-support-demo/follow-up-ledger.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Post-Day-0 Follow-up Ledger

## Open Fixes

| Item | Affected claim | State | Owner | Exit criterion |
| --- | --- | --- | --- | --- |
| None at design freeze | None | clear | public model-support working group | Reopen a gate when a claimed lane regresses |

The public working group owns triage for fourteen days after release.

## Performance Work

| Item | Correct fallback | Scope | State |
| --- | --- | --- | --- |
| Fused recurrent decode | Eager recurrent path | B200, batch one decode | planned |
| Quantized MoE | BF16 experts | Not in Day-0 release cut | deferred |
| Vision CUDA Graphs | Eager vision encoder | Repeated exact image grid only | planned |

## Experiments and Reverts

| Item | Effective shipped state | Evidence | Revisit condition |
| --- | --- | --- | --- |
| Graph padding fast path | Disabled for padded batches | Eager parity lane | Sentinel proof and dispatcher tests pass |
| Multi-image requests | Unsupported | Fail-fast API test | Processor and scheduler contracts land |

Open, closed-unmerged, reverted, and default-disabled work never expands the
release claim.
