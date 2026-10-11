---
id: doc-hcu-tracelens-e17c2f6a8be0fb0deff1
title: yuguo-Jack/TraceLens / docs/how-to/hcu-xprof-xcompute.md
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
path: docs/how-to/hcu-xprof-xcompute.md
raw_sha256: 4dec462f3efce61148f2283fca02ab924e6bcf30f4289867db46dd8cb1ec3dec
sources: []
generated_body_sha256: 5f1e998276dd4a5001d83c4351d2cdf0abe86b9fb560cfdaeed3cc6ffa062824
source_state: current-scan
---

# yuguo-Jack/TraceLens / docs/how-to/hcu-xprof-xcompute.md

[Original at fixed commit](https://github.com/yuguo-Jack/TraceLens/blob/30f5dcd539dd4e588678e34168c7fcf726dd987e/docs/how-to/hcu-xprof-xcompute.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--
Copyright (c) 2026 Advanced Micro Devices, Inc. All rights reserved.

See LICENSE for license information.
-->

# Read XProf / XComputeLight counter and SQTT output

`TraceLens.Reporting.xcompute` reads native XComputeLight CSV files. It does not
run a profiler, create a rocprofv3 trace, infer hardware peaks, or convert sampled
SQTT tables into a kernel bottleneck score.

The CSV dialect was observed with XProf 3.16.0, hsa-aqlprofile 3.6.2 and
XComputeLight 4.8.0 on gfx936, DTK 26.10, Torch 2.11 / HIP 7.2. The reader rejects
unrecognized headers instead of assuming another tool version has this format.
The local reader tests use authored fixtures; target collection and training
validation are separate evidence.

## Native formats and timing scope

| Output | Preserved representation |
|---|---|
| `<dispatch>_<kernel>.csv` counters | Ordered section/name/unit/value rows; literal `N/A` becomes JSON null, with the original value retained. Duplicate names in different sections remain separate. |
| `*_dispatch_results_summary_info.csv` | `Dispatch id,Kernel,XCD,Duration [ms]`; original cells plus exact dispatch identities and the explicitly labelled duration converted to ns. |
| `*_sqtt_dispatch_summary.csv` | Original columns, including XCD/SE/CU/wave counts and active-wave fields. |
| `*_sqtt_hot_inst.csv` | Original group/opcode/hits/latency columns. |
| `*_sqtt_bubble_summary.csv` | Original before/after/type/count/duration columns and example coordinates/source. |

SQTT `Duration`, `Latency`, `Max Duration` and `No-wave Idle` have no unit in these
CSV headers. Their units remain null; record the applicable tool documentation
or collection evidence in the manifest. Do not divide them by a dispatch runtime,
sum them as whole-device elapsed time, or treat an example CU as full-device
coverage. These tables describe sampled waves/instructions, with their own scope.

Counter replay can change caches and concurrency. The dispatch summary is
instrumented timing, not profiler-off operator latency or complete training-step
wall time. Report those measurements separately. A zero or unavailable metric
does not establish a physical bottleneck, and an instruction rate is not a
shape-specific Roofline efficiency without a matching workload and peak model.

## Capture manifest

Keep one capture entry for each original perf file and collection scope. Do not
join different perf files using identical dispatch numbers or kernel names.
Paths are relative to the manifest, or absolute. Record the exact collection and
conversion commands; the reader never executes them. Hash each input with
SHA256. A missing local perf can retain its original path and declared hash, but
its verification is `declared-only`.

```json
{
  "schema_version": 1,
  "captures": [{
    "id": "counter-pass",
    "tools": {"XProf": "3.16.0", "hsa-aqlprofile": "3.6.2", "XComputeLight": "4.8.0"},
    "gfx": "gfx936",
    "environment": {"DTK": "26.10", "torch": "2.11", "HIP": "7.2"},
    "source_perf": {"path": "probe.perf", "sha256": null},
    "commands": null,
    "counter_replay": true,
    "metric_basis": {"dispatch_duration": "native Duration [ms]", "counter_formula_source": null},
    "sampling": {"XCD": null, "SE": null, "CU": null},
    "workload": null,
    "csvs": [
      {"path": "probe_dispatch_results_summary_info.csv", "sha256": null},
      {"path": "3_vector_add.csv", "sha256": null, "xcd": 0, "workload": null}
    ]
  }]
}
```

Replace unknown values when evidence exists. Nulls are retained and reported as
provenance gaps; they are never filled with guessed units, tools or hardware
coverage. `commands` is a list of exact argument lists or command strings.
`metric_basis`, `sampling`, `environment` and `workload` are caller-supplied
objects. Keep the original manifest together with the perf and CSV files.

Counter CSVs bind only to a unique dispatch id + exact kernel + XCD within the
same capture's dispatch summary. The filename supplies the first two fields;
explicit `dispatch_id`/`kernel` fields support renamed files and must agree with
an original-format filename. Multiple XCD matches remain `unlinked` until the
CSV entry specifies the measured XCD. Absence of a summary also remains
`unlinked`. Binding checks capture membership as declared by the caller; it does
not establish an association with a PyTorch event or all calls of that kernel.

For training use, preserve per-call shape/dtype/stride, phase, rank, source trace
hash and event/operator identity in each CSV entry's `workload`. The entry is
retained as declared context, not inferred or broadcast to other dispatches.
Do not reuse counters from one specialization for all same-name kernels.

## API and offline CLI

```python
from TraceLens.Reporting.xcompute import parse_xcompute_csv, generate_perf_report_xcompute

native = parse_xcompute_csv("3_vector_add.csv")
report = generate_perf_report_xcompute("capture.json", "new-report-directory")
```

```bash
python -m TraceLens.Reporting.xcompute --manifest capture.json --output-dir new-report-directory
```

The API returns, and the CLI saves, `report.json` containing capture provenance,
input hashes, native tables, counter rows, exact dispatch bindings and gaps.
`parsed` means the declared provenance and binding checks passed; it is not
training correctness, verified bottleneck or optimization acceptance.
`incomplete` retains usable raw observations with explicit missing provenance or
ambiguous bindings. Invalid CSV, inconsistent hashes or contradictory identity
raise an error. Existing `report.json` is not overwritten.

## Collection permissions

An observed container initially failed with `Cannot open mem`; a temporary
diagnostic container succeeded after mapping `/dev/mem`, adding `SYS_RAWIO` and
mounting the applicable hyhal files read-only. This is a collection-environment
observation, not a default training-container configuration. Use the required
permissions only in the site-approved diagnostic scope after checking the tool
and driver requirements. The offline CSV reader requires none of these device
permissions.
