---
id: doc-bbuf-ai-infra-auto-driven-skills-4ce13c2d3af6bf4a75d2
title: BBuf/AI-Infra-Auto-Driven-SKILLS / docs/assets/sglang-model-day0-support-demo/validation-matrix.md
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
path: docs/assets/sglang-model-day0-support-demo/validation-matrix.md
raw_sha256: 1b5078f87b68dba2c194022efc26cef8b6f233bce4d5117afeac08c17fcabc44
sources: []
generated_body_sha256: 99ca8e9a94c25efa1077c2e7470dd02293ab8467237e4cd6aa858472df9acf2b
source_state: current-scan
---

# BBuf/AI-Infra-Auto-Driven-SKILLS / docs/assets/sglang-model-day0-support-demo/validation-matrix.md

[Original at fixed commit](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/blob/154cc565d0374746442bac17bd69368b888f4775/docs/assets/sglang-model-day0-support-demo/validation-matrix.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Validation Matrix

## Risk Pairs

| Pair | Shared risk | Required check |
| --- | --- | --- |
| MTP + recurrent state | Accepted-token commit and rejected-token rollback | Accepted lengths zero, partial, and full versus target-only state |
| PD + recurrent state | Logical ownership and wire layout | Prefill export/decode import round trip across TP4 roles |
| CUDA Graph + padding | Sentinel slots and stale replay metadata | Mixed real/padded batch versus eager output and state |
| Streaming + tools | Marker fragmentation and end holdback | Split every marker at every byte boundary |
| VLM + packaging | Processor/runtime dependency skew | Cold-start image request in the release image |

## Required Lanes

| Gate | Lane | Procedure | Expected result |
| --- | --- | --- | --- |
| Source | Revision lock | Resolve every public revision to 40 hex characters | Exact match |
| Load | Eager BF16 | Load target and draft, audit keys, generate twice | No missing required keys; deterministic tokens |
| Protocol | Reasoning/tools | Stream all marker splits and compare non-streaming | Same public fields and tool arguments |
| State | MTP/PD/graph | Run the five risk-pair checks above | Reference-equivalent committed state |
| Topology | TP8 and TP4+TP4 PD | Include idle and uneven request batches | All ranks remain live and correct |
| Quality/performance | Fixed public corpus | Compare quality, memory, and eager latency | Quality in band and model fits |
| Release | Fresh image | Build, launch, run cookbook, scan bundle | Reproducible success |
