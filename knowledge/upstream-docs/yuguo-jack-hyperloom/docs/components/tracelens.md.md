---
id: doc-yuguo-jack-hyperloom-16232b51c6f31c0a9fbe
title: yuguo-Jack/Hyperloom / docs/components/tracelens.md
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
path: docs/components/tracelens.md
raw_sha256: 692ccf26f1cb47a16f0c2175ad1d902f6f0e6c6cc15ffe9da496b6f2f7a94662
sources: []
generated_body_sha256: 56bdc9aa1e93f8fd9249779d66c359ba5f0eafeb14568662fb81c7e9f784b83a
source_state: current-scan
---

# yuguo-Jack/Hyperloom / docs/components/tracelens.md

[Original at fixed commit](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/components/tracelens.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
myst:
    html_meta:
        "description": "Learn about TraceLens, Hyperloom's trace analysis library. Covers hierarchical GPU performance breakdowns, roofline modeling, multi-GPU analysis, and trace comparison."
        "keywords": "TraceLens, Hyperloom, GPU performance, trace analysis, roofline modeling, PyTorch profiler, JAX, rocprofv3, AMD GPU, ROCm, benchmarking, LLM inference, vLLM, SGLang"
---
# TraceLens

TraceLens is a Python library focused on automating analysis from trace
files. It turns raw PyTorch, JAX, or rocprofv3 traces into hierarchical
performance breakdowns, roofline metrics, and multi-GPU communication analysis.

Within Hyperloom, TraceLens is the profiling brain of the workload
understanding stage: it consumes traces collected by [Magpie](magpie.md),
captures bottlenecks, and derives the roofline targets that seed the
optimization search tree.

- **Source**: <https://github.com/AMD-AGI/TraceLens>
- **License**: MIT

## Role in Hyperloom

The orchestration runtime enters TraceLens through two paths:

- The kernel request path:
  `src/hyperloom/orchestrator/kernel/request_handlers.py` dispatches
  `trace_analyze` requests as subprocesses that run
  `src/hyperloom/agents/kernel/tools/tracelens_analysis.py`. That script itself
  imports and calls `run_tracelens_skill` (the skill runner) internally under
  the agent route — the runner is not a separate subprocess dispatched by the
  orchestrator.
- The composite roofline action: `RooflineExecutor`
  (`src/hyperloom/orchestrator/actions/executors/roofline.py`) is an atomic
  `profile` + `trace_analyze` pipeline that first profiles the workload with
  Magpie, then calls `trace_analyze_handler()` directly on the trace.

Before profiling, Hyperloom can patch the active vLLM/SGLang server tree with
TraceLens-specific runtime flags through
`src/hyperloom/orchestrator/actions/executors/_server_patcher.py` and the
workload environment helpers. The generated report feeds the roofline ceilings
and bottleneck list used to score candidate optimizations. See
[Hyperloom optimization loop](../conceptual/optimization-loop.md).

## TraceLens documentation

For detailed documentation on TraceLens, see [TraceLens on ROCm Docs](https://rocm.docs.amd.com/projects/tracelens/en/latest/).
