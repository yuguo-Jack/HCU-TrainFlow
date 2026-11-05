---
id: doc-baidu-baige-loongforge-b9e8df93f25f6f7fbf13
title: baidu-baige/LoongForge / docs/source/embodied_tutorial/quick_start_index.md
engine: loongforge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: baidu-baige/LoongForge
commit: 042a68102395b9f4024d1a61084592c4c618371a
path: docs/source/embodied_tutorial/quick_start_index.md
raw_sha256: 726904ce0c37b7ee500e28d5cb188b16307e37c59b5562d45f5855e2f6faa4c5
sources: []
generated_body_sha256: 402d1cc9753b00119b5df0f47ccb1cf0ffe3358267c1155fc86f675da078a94e
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source/embodied_tutorial/quick_start_index.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/docs/source/embodied_tutorial/quick_start_index.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Quick Start

Ready-to-run launch scripts for each supported embodied model live under [`examples/embodied/`](https://github.com/baidu-baige/LoongForge/tree/master/examples/embodied). Pick the guide for your model below. For framework-wide conventions (directory layout, launch scripts, configuration layering), see the [Overview](overview.md).

## VLA Models

Vision-Language-Action models that map camera observations and language instructions to robot actions.

```{toctree}
:maxdepth: 1

quick_start_pi05
quick_start_gr00t_n1_6
quick_start_gr00t_n1_7
quick_start_xvla
```

## WAM Models

World-Action Models (WAM) that learn world dynamics and generate actions for embodied control.

```{toctree}
:maxdepth: 1

quick_start_lingbot_va
quick_start_cosmos3
quick_start_fastwam
quick_start_dreamzero
```
