---
id: doc-bbuf-ai-infra-auto-driven-skills-67179dde383b135d4eff
title: BBuf/AI-Infra-Auto-Driven-SKILLS / docs/assets/sglang-model-day0-support-demo/pr-dag.md
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
path: docs/assets/sglang-model-day0-support-demo/pr-dag.md
raw_sha256: 1484ad5776703d6289765be06b2eec175a20dc1e09693faa756d4828557e5951
sources: []
generated_body_sha256: b515059fa5a760d0ebb56d6fd7a894f0dfcf9e1fe6ffa98939a392a27eea6fb4
source_state: current-scan
---

# BBuf/AI-Infra-Auto-Driven-SKILLS / docs/assets/sglang-model-day0-support-demo/pr-dag.md

[Original at fixed commit](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/blob/154cc565d0374746442bac17bd69368b888f4775/docs/assets/sglang-model-day0-support-demo/pr-dag.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Pull Request DAG

## Dependencies

| Node | Scope | Depends on | Merge state |
| --- | --- | --- | --- |
| P0 | Public infrastructure: remote target/draft loader and recurrent-state transport contract | none | planned |
| P1 | Model spine: config, weights, hybrid attention, MoE, state, eager fallback | P0 | planned |
| P2 | Protocol/VLM: streaming parser, image processor, vision encoder/projector | P1 | planned |
| P3 | Platform/packaging: B200 dispatch and public image dependencies | P1 | planned |
| P4 | Validation/docs: risk-pair CI, cookbook, release lock, follow-up ownership | P1, P2, P3 | planned |

The integration PR visualizes the five nodes and cannot merge before P0
through P4 close their gates.

## Merge Gates

| Node | Gate to merge |
| --- | --- |
| P0 | Target and draft remote-load parity; PD recurrent-state round trip |
| P1 | Complete weight audit; eager/reference parity; TP8 liveness |
| P2 | Fragmented-marker streaming tests; image preprocessing parity |
| P3 | Reproducible image build; eager fallback and dispatcher tests |
| P4 | All seven gates, public recipes, sanitizer, and named follow-up owner |
