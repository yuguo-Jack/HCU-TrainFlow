---
id: doc-yuguo-jack-hyperloom-00e893cb7ccb93fce70e
title: yuguo-Jack/Hyperloom / docs/components/magpie.md
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
path: docs/components/magpie.md
raw_sha256: 81bc5700746328dac61afe4b680f538bdcb0b96bcb3561b067e21fb0f1926217
sources: []
generated_body_sha256: eeb1c6f2de99bb4e998bc4f9c03b4f761633665aead7c7ba9c88777f2b45cba4
source_state: current-scan
---

# yuguo-Jack/Hyperloom / docs/components/magpie.md

[Original at fixed commit](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/components/magpie.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
myst:
    html_meta:
        "description": "Learn about Magpie, Hyperloom's benchmark engine for GPU kernel correctness and performance evaluation. Covers Analyze, Compare, and Benchmark modes for AMD and NVIDIA GPUs."
        "keywords": "Magpie, Hyperloom, GPU benchmarking, kernel evaluation, AMD GPU, ROCm, HIP, CUDA, vLLM, SGLang, TraceLens, MCP, benchmark engine, throughput, LLM inference"
---
# Magpie

Magpie is a lightweight, general-purpose framework for evaluating GPU kernel
correctness and performance on AMD (HIP) GPUs. It exposes
three evaluation modes — Analyze, Compare, and Benchmark — plus framework-level
(vLLM or SGLang) benchmarking with built-in TraceLens trace analysis.

Within Hyperloom, Magpie is the benchmark engine. The kernel agent and the
optimization loop drive Magpie to spin up a serving framework, run the workload,
collect traces, and emit a structured `benchmark_report.json` file; those traces are
the input that [TraceLens](tracelens.md) then analyzes. Magpie relies on
[IntelliKit](intellikit.md) for some low-level GPU profiling tools.

- **Source**: <https://github.com/AMD-AGI/Magpie>
- **License**: MIT

## Role in Hyperloom

The optimization loop drives Magpie's benchmark mode as a subprocess. The
command line is built by `build_benchmark_command()` /
`MagpieBackend.build_command()` in
`src/hyperloom/orchestrator/actions/executors/benchmark_backend.py`; callers
such as `_grid_runner.py` and `baseline.py` invoke it to launch one run per
variant:

```python
cmd = [
    magpie_python, "-m", "Magpie", "-v", "benchmark",
    "--benchmark-config", str(config_path),
    "--output-dir", str(output_dir),
    "--run-mode", "local",
]
```

Each run produces a `benchmark_report.json` that Hyperloom parses to extract
throughput/measurements and pick winners. To make concurrent benchmark runs
robust, `src/hyperloom/orchestrator/actions/executors/_magpie_patcher.py`
applies an idempotent, atomic-write patch to Magpie's installed `benchmarker.py`
(`_prepare_benchmark_scripts`) so a concurrent reader never sees a half-copied
script. See [Hyperloom optimization loop](../conceptual/optimization-loop.md) for more information.

## Magpie documentation

For detailed documentation on Magpie, see [Magpie on ROCm Docs](https://rocm.docs.amd.com/projects/magpie/en/latest/).
