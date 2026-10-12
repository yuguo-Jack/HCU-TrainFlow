---
id: doc-bbuf-ai-infra-auto-driven-skills-b4478bd4516862afd1d3
title: BBuf/AI-Infra-Auto-Driven-SKILLS / docs/assets/sglang-model-day0-support-demo/release-lock.md
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
path: docs/assets/sglang-model-day0-support-demo/release-lock.md
raw_sha256: 927e653cbc2dc553aa91676669397b8019a3a92a0a0d3674a88b9d6a4b64b7ab
sources: []
generated_body_sha256: 9639997bc20d02e7346da4631221cd47333cafd72d8198ed07fd9dc5084a6966
source_state: current-scan
---

# BBuf/AI-Infra-Auto-Driven-SKILLS / docs/assets/sglang-model-day0-support-demo/release-lock.md

[Original at fixed commit](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/blob/154cc565d0374746442bac17bd69368b888f4775/docs/assets/sglang-model-day0-support-demo/release-lock.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Release Lock

## Source Revisions

| Component | Public source | Immutable revision |
| --- | --- | --- |
| Fictional model | `https://huggingface.co/example/Aurora-Hybrid-70B-VL` | `1111111111111111111111111111111111111111` |
| Fictional processor | `https://huggingface.co/example/Aurora-Hybrid-70B-VL` | `1111111111111111111111111111111111111111` |
| SGLang | `https://github.com/sgl-project/sglang` | `2222222222222222222222222222222222222222` |
| Transformers | `https://github.com/huggingface/transformers` | `3333333333333333333333333333333333333333` |

## Artifacts

| Artifact | Public identifier | Verified relation |
| --- | --- | --- |
| Image | `ghcr.io/example/aurora-day0:2026-08-15` | Build labels record the pinned SGLang revision |
| Weights | `example/Aurora-Hybrid-70B-VL` | Revision is pinned above |
| Cookbook | `docs/models/aurora-hybrid-70b-vl.md` | Commands use the same image and revisions |

## Limitations

- Only NVIDIA B200 TP8 unified and TP4+TP4 PD are claimed.
- Only BF16, one RGB image, and MTP draft lengths up to four are claimed.
- Optimized recurrent and MoE kernels remain optional.
- Any revision change reopens source, load, quality, and release gates.
