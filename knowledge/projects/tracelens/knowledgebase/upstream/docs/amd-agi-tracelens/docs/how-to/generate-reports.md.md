---
id: doc-amd-agi-tracelens-b16d81ae9e73150c855d
title: AMD-AGI/TraceLens / docs/how-to/generate-reports.md
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
path: docs/how-to/generate-reports.md
raw_sha256: 09f7e79a9dd2e5ad66e6cec7910d334feb703826742be8a31af935f849b5e52e
sources: []
generated_body_sha256: 26de7b7331b22da3128a12944970e146b34a21ec36f287f88ef13a7a7f21b11b
source_state: current-scan
---

# AMD-AGI/TraceLens / docs/how-to/generate-reports.md

[Original at fixed commit](https://github.com/AMD-AGI/TraceLens/blob/c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3/docs/how-to/generate-reports.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--
Copyright (c) 2024 - 2026 Advanced Micro Devices, Inc. All rights reserved.

See LICENSE for license information.
-->


# Generate TraceLens reports
```{meta}
:description: Learn how to generate TraceLens performance reports from PyTorch, JAX, rocprofv3, and collective-communication traces.
:keywords: TraceLens, performance report, PyTorch profiler, JAX, rocprofv3, collective communication, ROCm, GPU trace analysis
```

TraceLens generates structured performance reports from GPU trace files produced by PyTorch, JAX, and the AMD ROCm profiler. Choose the topic for your trace format:

- [Generate a PyTorch performance report](./generate-perf-report-pytorch.md)
- [Generate a PyTorch inference performance report](./generate-perf-report-pytorch-inference.md)
- [Generate a JAX performance report](./generate-perf-report-jax.md)
- [Generate a rocprof performance report](./generate-perf-report-rocprof.md)
- [Generate a collective-communication report](./collective-report.md)

After you have CSV report directories, append them with
`TraceLens_trace_index append --trace-path … --report-dir …`.
See [Index a corpus of traces](./trace-index.md).

## Related topics

- [What is TraceLens?](../what-is-tracelens.md)
- [Installation instructions](../install/install.md)
- [API reference](../reference/api-reference.md)
