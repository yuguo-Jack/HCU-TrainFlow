---
id: doc-yuguo-jack-hyperloom-e08cdcf64f54583119fa
title: yuguo-Jack/Hyperloom / docs/components/intellikit.md
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
path: docs/components/intellikit.md
raw_sha256: 0b4538de1ae221bcafd78fbf8de9f1e39a1203db260e5f050c40fbcee724115a
sources: []
generated_body_sha256: 42bf2a3ea024e93bc779ff017ea039f7c1db5145361de255cb0efd5387dd3cd6
source_state: current-scan
---

# yuguo-Jack/Hyperloom / docs/components/intellikit.md

[Original at fixed commit](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/components/intellikit.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
myst:
    html_meta:
        "description": "Learn about IntelliKit, Hyperloom's GPU profiling and validation toolkit. Covers Kerncap, Metrix, Linex, Nexus, Accordo, and MCP server packages for AMD GPU workloads."
        "keywords": "IntelliKit, Hyperloom, GPU profiling, AMD GPU, ROCm, Kerncap, Metrix, Linex, Nexus, Accordo, MCP, kernel optimization, HIP, hardware counters, benchmarking"
---
# IntelliKit

IntelliKit is a set of agent-first Python tools for AMD-focused performance
and validation. Most of the stack targets GPUs through ROCm, turning hardware
counters, traces, dispatch data, and Heterogeneous System Architecture (HSA) packets into clear Python APIs and
Model Context Protocol (MCP) servers. It's structured as a monorepo of
independently installable packages (Kerncap, Metrix, Linex, Nexus, Accordo, plus
the `rocm_mcp` and `uprof_mcp` server bundles).

Within Hyperloom, IntelliKit is not called directly. It sits underneath
[Magpie](magpie.md), which relies on IntelliKit for some of its low-level GPU
profiling primitives. Hyperloom therefore depends on IntelliKit transitively,
through Magpie.

- **Source**: <https://github.com/AMDResearch/intellikit>
- **License**: MIT

## Role in Hyperloom

Hyperloom doesn't reference IntelliKit directly. Kernel profiling and
validation in Hyperloom is powered by [Magpie](magpie.md), which in turn relies
on IntelliKit for some of its low-level GPU profiling primitives. IntelliKit is
an indirect, transitive dependency reached through Magpie.

## IntelliKit documentation

For detailed documentation on IntelliKit, see [IntelliKit on ROCm Docs](https://rocm.docs.amd.com/projects/intellikit/en/latest/).
