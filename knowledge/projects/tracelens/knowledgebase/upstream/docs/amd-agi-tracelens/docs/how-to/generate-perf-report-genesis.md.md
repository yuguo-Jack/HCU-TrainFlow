---
id: doc-amd-agi-tracelens-391481d2e128d23ad071
title: AMD-AGI/TraceLens / docs/how-to/generate-perf-report-genesis.md
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
path: docs/how-to/generate-perf-report-genesis.md
raw_sha256: f87152e7a3c42bd1ade4f536bc157a6c70e37eb73e8379cb1d9d8366875c420d
sources: []
generated_body_sha256: bf619ed666732c2b93fc26d0fdd937791256307c3f049ffcdc02ddfebaa6f8fc
source_state: current-scan
---

# AMD-AGI/TraceLens / docs/how-to/generate-perf-report-genesis.md

[Original at fixed commit](https://github.com/AMD-AGI/TraceLens/blob/c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3/docs/how-to/generate-perf-report-genesis.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--
Copyright (c) 2026 Advanced Micro Devices, Inc. All rights reserved.

See LICENSE for license information.
-->

# Generate a Genesis or Taichi physics simulation performance report
```{meta}
:description: Learn how to generate a TraceLens performance report for Genesis and Taichi physics-simulation workloads, including steady-state isolation, kernel categorization, and HIP activity analysis.
:keywords: TraceLens, Genesis, Taichi, physics simulation, rocprofv3, pftrace, steady-state, kernel categorization, ROCm, AMD Instinct
```

Generate a performance report for **Genesis and Taichi physics-simulation workloads**. The report combines rocprof kernel analysis with pftrace HIP activity and memory copy reports, adds physics kernel categorization, and isolates the steady-state simulation window (excluding JIT and build overhead).

---

## Generate the report

Run the following command, pointing at the capture directory written by `rocprofv3`:

```bash
TraceLens_generate_perf_report_genesis \
    --capture-dir profile_output/<timestamp> \
    --output-dir analysis_output/<timestamp>
```

---

## Capture traces

Capture traces with `rocprofv3` while running a Genesis benchmark:

```bash
rocprofv3 --hip-trace --kernel-trace --memory-copy-trace \
    --output-format pftrace -d profile_output/<timestamp>/kernel_trace \
    -- python3 your_genesis_benchmark.py
```

---

## Expected directory layout

The tool expects the following structure under `--capture-dir`:

```
profile_output/<timestamp>/
├── kernel_trace/
│   ├── kernel_kernel_trace.csv    # required — GPU kernel dispatches
│   ├── kernel_results.json        # native rocprof JSON (fallback)
│   ├── kernel_results.pftrace     # Perfetto trace for HIP/memory analysis
│   ├── kernel_agent_info.csv
│   └── ...
├── run.log                        # optional — auto-detects benchmark wall_time
└── combined_manifest.json         # optional — capture metadata (n_envs, steps, etc.)
```

---

## Output files

The tool writes the following output files to the directory specified by `--output-dir`.

- **`genesis_perf_report.xlsx`** — Excel workbook with:
  - GPU timeline (steady-state window only, excluding JIT and build)
  - Kernel summary by physics category (Rigid Body Solver, Collision, Time Integration, etc.)
  - HIP activity summary (from pftrace)
  - Memory copy summary (from pftrace)

- **`genesis_summary.md`** — Markdown overview with steady-state GPU utilization and top kernels

---

## Physics kernel categories

Kernels are automatically categorized into Genesis-specific physics roles:

| Category | Pattern Examples |
|----------|----------------|
| Rigid Body Solver | `_kernel_solve_body*`, `func_solve_init*`, `_kernel_linesearch*` |
| Broadphase Collision | `func_broad_phase*` |
| Narrowphase Collision | `_func_narrowphase*` |
| Contact Management | `func_sort_contacts*`, `func_update_contact*` |
| Time Integration | `kernel_step_1*`, `kernel_step_2*`, `func_update_qacc*` |
| Constraints | `add_equality_constraints*`, `add_inequality_constraints*` |
| Forward Kinematics | `kernel_forward_kinematics*`, `kernel_update_verts*` |
| Geometry / AABB | `kernel_update_geom*`, `kernel_bit_reduction*` |
| Memory Ops (ROCm) | `__amd_rocclr_copyBuffer`, `__amd_rocclr_fillBuffer*` |
| Runtime Init | `runtime_initialize*`, `fill_ndarray*`, `ext_arr_to_ndarray*` |
| PyTorch Runtime | `at::native::*`, `elementwise_kernel*` |

---

## Steady-state detection

Genesis workloads have a distinctive two-phase pattern:
1. **JIT / Build phase** — Taichi compiles kernels on first invocation (large inter-kernel gaps)
2. **Simulation phase** — Dense, repetitive kernel dispatches at steady state

TraceLens automatically detects the phase boundary by finding the largest inter-kernel gap exceeding `--steady-state-gap-ms` (default: 1000 ms). Only the simulation phase is included in the performance report, giving accurate metrics without JIT overhead.

If no large gap is found, the tool falls back to using the last N seconds of the trace (auto-detected from `run.log` or `--steady-state-fallback-s`).

---

## CLI options

The following table describes all available options.

| Option | Default | Description |
|--------|---------|-------------|
| `--capture-dir` | (required) | Path to `profile_output/<timestamp>/` directory |
| `--output-dir` | `analysis_output` | Where to write the report |
| `--steady-state-gap-ms` | 1000 | Min gap (ms) to split JIT and build from simulation burst |
| `--steady-state-fallback-s` | auto | Timed benchmark window (default: auto from `run.log`, else 5s) |
| `--include-api` | off | Include HIP/HSA API events in rocprof JSON |
| `--kernel-details` | off | Include per-dispatch kernel details sheet |
| `--no-short-kernel-study` | on | Disable short kernel analysis |
| `--traceconv` | auto | Path to Perfetto `traceconv` binary |
| `--keep-work` | off | Retain intermediate `.work/` directory for debugging |

---

## Python API usage

Import and call the generator directly to receive pandas DataFrames instead of writing files:

```python
from TraceLens.Reporting.generate_perf_report_genesis import generate_perf_report_genesis

reports = generate_perf_report_genesis(
    capture_dir="profile_output/20260529_181047",
    output_dir="analysis_output/20260529_181047",
    steady_state_gap_ms=1000.0,
)

# reports["rocprof"]["kernel_summary"]  — DataFrame of kernels with Category column
# reports["rocprof"]["gpu_timeline"]    — steady-state GPU utilization
```
