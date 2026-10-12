---
id: doc-amd-agi-tracelens-cf5d48e53195c31a4942
title: AMD-AGI/TraceLens / docs/about/release-notes.md
engine: tooling
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: AMD-AGI/TraceLens
commit: c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3
path: docs/about/release-notes.md
raw_sha256: ffe7d5712a1be359dba675fed6ac0cdb21e6075dc469619ad99204f9b1e4d2a3
sources: []
generated_body_sha256: f54584cf53a032ee26122d082919a57a3e47159f0d2be4aed4b10638d5df29d1
source_state: current-scan
---

# AMD-AGI/TraceLens / docs/about/release-notes.md

[Original at fixed commit](https://github.com/AMD-AGI/TraceLens/blob/c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3/docs/about/release-notes.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--
Copyright (c) 2024 - 2026 Advanced Micro Devices, Inc. All rights reserved.

See LICENSE for license information.
-->


# TraceLens release notes
```{meta}
:description: Release notes for TraceLens. Learn what features and SDK modules are available in each version, and see links to the compatibility matrix.
:keywords: TraceLens, TraceLens 1.0.0, release notes, GPU trace analysis, performance models, TraceLens Agent, PyTorch, JAX, rocprofv3
```

This topic summarizes the features available in each TraceLens release. For the
hardware and software versions validated for a release, see the
[Compatibility matrix](../reference/compatibility.md).

## TraceLens 1.0.0

The release expands performance-model coverage; extends profiling support to
newer vLLM and SGLang versions along with xDiT diffusion and Genesis
physics-simulation workloads; strengthens the TraceLens Analysis Agent with a
portable skill layout and comparative graph-capture support; and overhauls
TraceDiff's name disambiguation. It also adds production-grade unit-test coverage.

### Performance models

This release adds the following performance models and classifications:

- **DeepSeek-V4 support:** Sparse paged-decode modes (sliding-window,
  compressed, and hybrid) and a sparse-prefill model, plus the
  manifold-constrained Hyper-Connection operator family.
- **Additional operators:** New models for nearest-neighbor upsampling (1D/2D/3D)
  and fused RMSNorm with quantization, efficient-attention classification, and an
  FP8 MoE precision fix for FP8/BF16 inputs.
- **Block-scaled GEMM detection:** Detection of block-scaled MXFP4/MXFP6 GEMM
  paths for roofline modeling.

### Frameworks and profiling

This release extends framework and profiling support:

- **vLLM and SGLang:** Profiling support through recent vLLM and SGLang releases,
  using stock upstream images where a patched image is no longer required.
- **xDiT diffusion:** Diffusion-model profiling using the same capture-merge
  infrastructure as vLLM and SGLang.
- **Genesis physics simulation:** A `TraceLens_generate_perf_report_genesis`
  report generator for Genesis/Taichi workloads that isolates the steady-state
  simulation window from JIT and build overhead.

### TraceLens Analysis Agent

This release includes the following agent improvements:

- **Portable skill layout:** Agent orchestrator, sub-agent, and template specs
  ship in a portable `skills/` layout discoverable by any agentic runner that
  supports skill-file discovery.
- **Comparative graph-capture analysis:** Comparative mode accepts a capture
  folder per trace, merging call-stack and shape information into both
  graph-replay trees before analysis.
- **Local evaluation:** Repeatability evals can run against a local serving
  backend for fully offline eval loops.

### TraceDiff

This release overhauls trace-tree matching:

- **Name disambiguation:** Same-named sibling nodes are matched by structure
  rather than position, with an additional aggressive matching pass for
  slightly-differing Python-function names.
- **Correctness fixes:** The same-name candidate-matching path is rewritten to
  fix several matching correctness issues.

### Test coverage

This release strengthens automated testing:

- **Unit coverage:** New unit-test suites span every SDK subpackage, including
  Trace2Tree, TreePerf, PerfModel, NcclAnalyser, TraceFusion, TraceDiff,
  EventReplay, Reporting, and the shared utilities.
- **Coverage reporting:** Coverage tracking and a coverage-regression gate run in
  continuous integration to guard against regressions.
