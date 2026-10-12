---
id: doc-yuguo-jack-hyperloom-8a8e63da5f46b8ec23da
title: yuguo-Jack/Hyperloom / docs/components/index.md
engine: hyperloom
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: yuguo-Jack/Hyperloom
commit: 0425bde3f6e76e1588400c37d056dfd3bb75ac11
path: docs/components/index.md
raw_sha256: b09b9f503e24391f95f28e1d7cbb076fa8b5b296d461d337bfb4b87cf99c1a47
sources: []
generated_body_sha256: 8f55c1ee740fc0bc5547428881d8f84061fe859f32da25f5c0ed291432a931b1
source_state: current-scan
---

# yuguo-Jack/Hyperloom / docs/components/index.md

[Original at fixed commit](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/components/index.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
myst:
    html_meta:
        "description": "Explore Hyperloom's specialized components: IntelliKit for GPU profiling, Magpie for benchmarking, TraceLens for trace analysis, GEAK for kernel optimization, and AgentKernelArena for agent evaluation."
        "keywords": "Hyperloom, components, IntelliKit, Magpie, TraceLens, GEAK, AgentKernelArena, GPU profiling, benchmarking, kernel optimization, AMD GPU, ROCm, evaluation"
---
# Hyperloom components

Hyperloom orchestrates several specialized tools. Each has its own
documentation page; the overarching optimization flow that ties them together
is described in [Hyperloom optimization loop](../conceptual/optimization-loop.md).

The following table lists each component with its role, source repository, and documentation link.

| Component | Role | Source | Documentation|
|-----------|------|--------|--------------|
| [IntelliKit](intellikit.md) | Low-level GPU profiling primitives | [AMDResearch/intellikit](https://github.com/AMDResearch/intellikit) | [IntelliKit Docs](https://rocm.docs.amd.com/projects/intellikit/en/latest/) |
| [Magpie](magpie.md) | Benchmark engine with trace-collection support | [AMD-AGI/Magpie](https://github.com/AMD-AGI/Magpie) | [Magpie Docs](https://rocm.docs.amd.com/projects/magpie/en/latest/) |
| [TraceLens](tracelens.md) | Agentic trace analysis and roofline targets | [AMD-AGI/TraceLens](https://github.com/AMD-AGI/TraceLens) | [TraceLens Docs](https://rocm.docs.amd.com/projects/tracelens/en/latest/) |
| [GEAK](geak.md) | GPU kernel generation and optimization (Triton, HIP, or FlyDSL) | [AMD-AGI/GEAK](https://github.com/AMD-AGI/GEAK) | [GEAK Docs](https://rocm.docs.amd.com/projects/geak/en/latest/) |
| [AgentKernelArena](agentkernelarena.md) | Optional standardized evaluation arena for agent benchmarking | [AMD-AGI/AgentKernelArena](https://github.com/AMD-AGI/AgentKernelArena) | [AgentKernelArena Docs](https://rocm.docs.amd.com/projects/agent-kernel-arena/en/latest/) |
