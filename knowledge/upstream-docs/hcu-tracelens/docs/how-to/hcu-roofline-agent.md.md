---
id: doc-hcu-tracelens-6902d096cb8729463df3
title: yuguo-Jack/TraceLens / docs/how-to/hcu-roofline-agent.md
engine: tooling
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: yuguo-Jack/TraceLens
commit: 30f5dcd539dd4e588678e34168c7fcf726dd987e
path: docs/how-to/hcu-roofline-agent.md
raw_sha256: 6bd1d5d18d84512755a2aa192bf02df13d1d96b49442ec1f16e31eae77489928
sources: []
generated_body_sha256: 3b3df69967b20f140a0ea86b43936923870f241b4ee8febd37c3f8d5d457c500
source_state: current-scan
---

# yuguo-Jack/TraceLens / docs/how-to/hcu-roofline-agent.md

[Original at fixed commit](https://github.com/yuguo-Jack/TraceLens/blob/30f5dcd539dd4e588678e34168c7fcf726dd987e/docs/how-to/hcu-roofline-agent.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--
Copyright (c) 2026 Advanced Micro Devices, Inc. All rights reserved.

See LICENSE for license information.
-->

# HCU roofline diagnostics and native Agent analysis

HCU analysis uses an explicit site architecture file. It does not substitute an
AMD device's bandwidth or TFLOPS. Existing AMD architecture files and APIs retain
their behavior.

## Architecture and workload qualification

An identity-only architecture is valid input and produces unknown headroom:

```json
{
  "name": "HCU_DEVICE",
  "manufacturer": "Hygon",
  "mem_bw_gbps": null,
  "max_achievable_tflops": {},
  "hcu_roofline": {
    "schema_version": 1,
    "device_arch": null,
    "provenance": null,
    "workload_mappings": []
  }
}
```

Use the device name and ISA observed at the site. Populate the native
`mem_bw_gbps` and `max_achievable_tflops` fields from retained calibration
evidence. The `hcu_roofline.provenance` object requires:

| Field | Contract |
|---|---|
| `kind` | `measured` or `calibrated` |
| `source` | Path or URI of retained calibration evidence |
| `device_name`, `device_arch` | Match architecture identity; ISA feature suffixes are allowed |
| `timestamp` | Calibration time |
| `stack` | Actual software versions, for example Torch and HIP/DTK |
| `conditions` | Calibration workloads, sizes, timing method and limitations |

Optionally record `conditions.compute.<compute_spec>.shape = [M, N, K]` to
expose whether a GEMM matches the calibration shape. A different shape remains
a conditional diagnostic. An arbitrary GEMM microbenchmark is not a hardware
peak or proof that smaller GEMMs can reach its throughput.

Every workload needs a reviewed mapping. For a dense 2D GEMM:

```json
{
  "name": "aten::mm",
  "compute_spec": "matrix_fp32",
  "model": "TraceLens.PerfModel.perf_model.aten_mm",
  "status": "qualified",
  "evidence": "retained-workload-contract-review.json"
}
```

Add `input_dims` and/or `input_type` exact selectors when qualification is
limited to particular inputs. A mapping must match one registered model and
compute specification unambiguously. The exporter reconstructs that model
from recorded shapes and dtypes, then verifies FLOPs and compulsory bytes
against the CSV. Missing work, incompatible models or missing precision-specific
references stay unknown. There is no BF16 fallback for unknown HCU work.

Published hardware ceilings belong in the separate optional
`hcu_roofline.theoretical` object, with its own `mem_bw_gbps`,
`max_achievable_tflops`, and `provenance`. That provenance uses `kind: "vendor"`,
an authoritative source and the observed device identity. It produces a separate
ideal modeled lower bound and never overwrites the measured envelope. Omit it
when no accepted vendor specification exists.

## Native commands

Generate an ordinary eager report, then prepare with the same site file:

```bash
python -m TraceLens.Reporting.generate_perf_report_pytorch \
  --profile_json_path trace.json \
  --output_csvs_dir analysis_output/perf_report_csvs \
  --gpu_arch_json_path site_arch.json

python -m TraceLens.Agent.Analysis.utils.orchestrator_prepare \
  --trace-path trace.json --platform HCU_DEVICE \
  --gpu-arch-json site_arch.json --output-dir analysis_output

python -m TraceLens.Agent.Analysis.utils.hcu_analysis run \
  --output-dir analysis_output --category-timeout-s 60
```

Preparation exports the actual category manifest and
`category_data/hcu_roofline.json`. HIP runtime and driver wrappers are excluded
from fusion containers. The `run` command executes native scripts selected
from that manifest, records commands/logs, aggregates priorities, and validates
outputs. It does not invoke an LLM or write Agent findings. `metrics_complete`,
missing findings, and a validated Agent report are separate states in
`hcu_native_analysis.json`.

Each CPU category command has a configurable timeout of 60 seconds by default
and at most 300 seconds. The total execution budget defaults to 240 seconds,
configured by `--analysis-timeout-s` (at most 300). Each child receives the
smaller of its category timeout and the remaining total budget. Timed-out
Python processes are killed and waited for;
partial metrics are removed, and a timeout receipt remains in
`native_category_logs/<category>.execution.json`.

Independent workers can analyze only observed categories, then aggregate:

```bash
python -m TraceLens.Agent.Analysis.utils.hcu_analysis analyze \
  --output-dir analysis_output --category gemm
python -m TraceLens.Agent.Analysis.utils.hcu_analysis aggregate \
  --output-dir analysis_output
```

The aggregate stage checks every observed category. Failed runs, missing outputs
and stale outputs cannot become successful empty results. Categories select
native functions; they do not require a fixed roster of Agent sessions.

An Agent completes analysis by reading the native category instructions, metrics
and retained source evidence, writing findings and `analysis.md`, explicitly
accepting that reasoning for the current inputs, then running:

```bash
python -m TraceLens.Agent.Analysis.utils.hcu_analysis review \
  --output-dir analysis_output --include-report
python -m TraceLens.Agent.Analysis.utils.hcu_analysis aggregate \
  --output-dir analysis_output
```

`review` records the invoking Agent's acceptance; it does not invoke an Agent.
An independent category worker can use `review --category <observed-category>`
without `--include-report`. The final report review requires all categories.
The deterministic `run` command never binds existing reasoning automatically.

Preparation fingerprints the trace contents and explicit site file. Native
execution receipts bind the manifest, category CSV/metadata/data, native input
CSVs, Roofline audit, relevant analysis code and exact metrics output. Comparative
analysis binds both trace CSV directories and the comparison utilization metadata.
Aggregate
requires current successful receipts. Missing receipts, same-path trace/site
overwrites, changed inputs or changed metrics produce failure. Reprepare and
reanalyze after source changes. Findings/report also require current review
bindings. Identical inputs and identical rerun metrics may reuse the accepted
reasoning. Changed sources or prose require an explicit Agent review.

HCU compute findings keep useful conditional observations
before the required empty `Recommendations`/`Detailed Analysis` sections when
no impact is qualified. System findings may state non-quantifiable hypotheses.
Reviewed negative native results can use empty sections without invented
recommendations. The final report still needs normal native validation.

## Per-operation export and interpretation

```bash
python -m TraceLens.PerfModel.hcu_roofline \
  --perf-csv analysis_output/perf_report_csvs/unified_perf_summary.csv \
  --arch-json site_arch.json --output headroom.json
```

Python APIs: `qualify_hcu_arch`, `evaluate_hcu_roofline_row`, and
`export_hcu_roofline` in `TraceLens.PerfModel.hcu_roofline`.

| Output | Meaning |
|---|---|
| `status`, `missing_fields` | Supported diagnostic or explicit missing qualification/work/reference |
| `measured_reference_time_us` | `max(FLOPs/reference TFLOPS, bytes/reference bandwidth)` per invocation |
| `efficiency_vs_measured_pct` | Reference time divided by observed `kernel_time_sum / count` |
| `conditional_headroom_ratio` | Observed mean time divided by measured reference time |
| `conditional_kernel_time_headroom_us` | Conditional gap across invocations; no E2E interpretation |
| `conditional_screening_score` | Conditional gap divided by summed operator kernel time, for screening |
| `theoretical_lower_bound_us` | Separate ideal bound, only with a qualified supplied vendor ceiling |
| `architecture_provenance`, `calibration_scope`, `calibration_shape_match` | Identity, stack, source and workload scope |
| `achievable_kernel_speedup`, `achievable_e2e_savings_pct` | Unknown until separately validated intervention evidence exists |

Native CSV `GFLOPS` and binary `Data Moved (MB)` describe one invocation; count
multiplies work. Efficiency uses summed duration divided by count, not an
unweighted mean of percentages. Compulsory bytes are modeled traffic, not HBM
counters. `priority_data.json.hcu_headroom` ranks conditional diagnostics;
measured-envelope ratios and unknown work never enter quantified or heuristic
E2E savings. Fusion retains launch counts and modeled input/output traffic, with
dependencies and fused-workload evidence required before quantifying savings.

The GPU timeline window, summed kernel durations and end-to-end training time
are distinct. Overlap can make sums exceed the window. Preparation records the
native timeline span separately; direct export accepts
`--wallclock-time-us` and never invents it from kernel sums. An ideal per-op
bound does not establish removable critical-path time or achievable model
speedup. Validate those with a paired intervention, consistent window boundaries,
overlap accounting and the actual workload.
