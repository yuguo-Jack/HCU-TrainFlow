---
id: doc-amd-agi-primus-150aca51baee029384d7
title: AMD-AGI/Primus / docs/06-developer-guide/tooling.md
engine: primus
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: AMD-AGI/Primus
commit: ab8735564c4cc3bb7c0475146057eee8dae4c650
path: docs/06-developer-guide/tooling.md
raw_sha256: 3c6bd62cf83e7b229284588cb63f38bebdf032686acca8bc8f4a572789e5dac3
sources: []
generated_body_sha256: 135082b3c9835ee077f5a5a12c102b1261ff59c83a63debfe135fa0a641cbfb3
source_state: current-scan
---

# AMD-AGI/Primus / docs/06-developer-guide/tooling.md

[Original at fixed commit](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/docs/06-developer-guide/tooling.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Tooling

Primus ships a set of auxiliary tools for analysis, benchmarking, visualization, installation, and diagnostics. They live under [`tools/`](https://github.com/AMD-AGI/Primus/blob/main/tools/README.md) in the repository; each tool keeps its own README with detailed usage instructions. This page is a lightweight index so the tooling is discoverable from the documentation.

## Available tools

| Tool | Directory | What it does | Docs |
|------|-----------|--------------|------|
| **IRLens** | `tools/IRLens/` | Parses XLA HLO text dumps and prints an execution skeleton with control flow, separating communication vs compute ops. | [README](https://github.com/AMD-AGI/Primus/blob/main/tools/IRLens/README.md) |
| **model_stats** | `tools/model_stats/` | Generates charts from the model config registry under `primus/configs/models`. | [README](https://github.com/AMD-AGI/Primus/blob/main/tools/model_stats/README.md) |
| **Pipeline Visualization** | `tools/visualization/pp_vis/` | Visualizes pipeline-parallelism schedules from dumped data or PP-simulator JSON via a local web UI. | [README](https://github.com/AMD-AGI/Primus/blob/main/tools/visualization/pp_vis/README.md) |
| **Auto Benchmark** | `tools/auto_benchmark/` | Interactive benchmark menu for Megatron/TorchTitan on MI300X/MI355X with metrics collection. | [README](https://github.com/AMD-AGI/Primus/blob/main/tools/auto_benchmark/Primus_Auto_Benchmark_README.md) |
| **Backend Gap Report / Engineering Dashboard** | `tools/backend_gap_report/` | Generation and publishing toolchain for the shared Primus engineering dashboard and backend-gap reports. | [README](https://github.com/AMD-AGI/Primus/blob/main/tools/backend_gap_report/README.md) |
| **Installation (venv)** | `tools/installation/` | Reproduces the Primus training Docker environment in a Python virtual environment (no Docker, no sudo). | [README](https://github.com/AMD-AGI/Primus/blob/main/tools/installation/README.md) |
| **Daily Report** | `tools/daily/` | Benchmark summary CSV generation used by CI workflows. | — |
| **Docker Helpers** | `tools/docker/` | Container startup and proxy scripts. | — |
| **Profile Trace** | `tools/profile_trace/` | Trace-file merging utility. | — |

## Related documentation

- [Primus tools](../02-user-guide/primus-tools.md)—the full catalog of Primus tools (CLI, tuning agent, ecosystem) with how-to starting points.
- [Tools overview](https://github.com/AMD-AGI/Primus/blob/main/tools/README.md)—the top-level index maintained alongside the code.
- [Profiling and observability](../04-technical-guides/profiling-and-observability.md)—how these tools fit into performance analysis.
- [Micro-benchmarking](../02-user-guide/micro-benchmarking.md)—running the benchmark suites the tools summarize.
