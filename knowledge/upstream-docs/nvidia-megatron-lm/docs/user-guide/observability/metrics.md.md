---
id: doc-nvidia-megatron-lm-2b1aa72652bf1f30a61f
title: NVIDIA/Megatron-LM / docs/user-guide/observability/metrics.md
engine: megatron
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: NVIDIA/Megatron-LM
commit: ab1a28486b92adb3702f1289ff3a332cdb74294f
path: docs/user-guide/observability/metrics.md
raw_sha256: 4e8142f7a32bcb1db82ab835651bda295d89691537e2b977569418950e9a7899
sources: []
generated_body_sha256: fa66ab49e3aadcd5e4ac16e37cf1badc570fadf9a8e35e771707626edb78b9b1
source_state: current-scan
---

# NVIDIA/Megatron-LM / docs/user-guide/observability/metrics.md

[Original at fixed commit](https://github.com/NVIDIA/Megatron-LM/blob/ab1a28486b92adb3702f1289ff3a332cdb74294f/docs/user-guide/observability/metrics.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!---
   Copyright (c) 2026, NVIDIA CORPORATION. All rights reserved.
   NVIDIA CORPORATION and its licensors retain all intellectual property
   and proprietary rights in and to this software, related documentation
   and any modifications thereto. Any use, reproduction, disclosure or
   distribution of this software and related documentation without an express
   license agreement from NVIDIA CORPORATION is strictly prohibited.
-->

# Metrics

Megatron emits training metrics under the `megatron.training.*` namespace.

All metrics are emitted **only on the export rank** (`is_exporting = True`). Non-exporting ranks don't create metric instruments.

For the general instrument pattern (weak-reference caching, None-skipping), see
[lens: metrics](https://github.com/NVIDIA-NeMo/Lens/blob/main/docs/user-guide/metrics.md).

## Training metrics (`megatron.training.*`)

Training has no OTel standard, so Megatron uses a project-specific namespace. Emission is tied to `--log-interval` (same cadence as TensorBoard and W&B loggers).

| Metric | Type | Unit | Description |
|---|---|---|---|
| `megatron.training.step_duration_ms` | Histogram | ms | Duration of one training step in milliseconds |
| `megatron.training.loss` | Gauge | — | Training loss (last value per log interval) |
| `megatron.training.throughput_tflops` | Gauge | TFLOP/s | Training throughput in TFLOP/s/GPU |
| `megatron.training.tokens_per_sec` | Gauge | tokens/s | Training throughput in tokens per second |
| `megatron.training.grad_norm` | Gauge | — | Global gradient norm |
| `megatron.training.skipped_iters` | Counter | — | Optimizer steps skipped (NaN/inf loss) |
| `megatron.training.learning_rate` | Gauge | — | Current learning rate |
| `megatron.training.memory_allocated_gb` | Gauge | GB | Peak GPU memory allocated |

Loss, throughput, grad norm, and learning rate are **Gauges** (point-in-time value), not Histograms — this produces a Prometheus `gauge` which is semantically correct for a value that changes every log interval.

### Emission site

`megatron/training/training.py` calls `record_training_metrics()` from `megatron.core.telemetry.training_metrics` every `--log-interval` iterations. The instrument module caches per-Meter instruments using `WeakKeyDictionary` to avoid leaking on re-init.

## Prometheus metric names

The OTel SDK may append a unit suffix when exporting to Prometheus.

| OTel instrument name | Prometheus metric (example) |
|---|---|
| `megatron.training.loss` | `megatron_training_loss` (Gauge) |
| `megatron.training.step_duration_ms` | `megatron_training_step_duration_ms_milliseconds` |
| `megatron.training.throughput_tflops` | `megatron_training_throughput_tflops` (Gauge) |
| `megatron.training.tokens_per_sec` | `megatron_training_tokens_per_sec` (Gauge) |
| `megatron.training.skipped_iters` | `megatron_training_skipped_iters_total` |

Dashboards use regex patterns (e.g. `{__name__=~"megatron_training_loss.*"}`) to match regardless of suffix. If a panel shows "No data", use **Explore → Prometheus → Metrics browser** to discover exact names on your SDK version.

## Filtering across runs

Metrics carry the `nemo.run.id` resource attribute on every data point. Use it to filter in Grafana:

```
{nemo_run_id="<id>", __name__=~"megatron_training_.*"}
```

Or to compare two runs:

```
{nemo_run_id=~"run-a|run-b", __name__="megatron_training_loss"}
```

## Metric vs span attribute

A recurring pitfall: putting training loss on a span attribute instead of a metric.

- **Loss** changes every iteration. Put it on `megatron.training.loss` metric. Prometheus stores each value; Grafana plots the series.
- **Iteration number** is categorical context for a specific span. Put it on `megatron.iteration` span attribute. Jaeger uses it for filtering.

Don't do it the other way. Loss on a span attribute produces no useful time series in Jaeger; it's wasted data. Iteration on a metric label produces one metric series per iteration — unbounded cardinality explosion.

See [lens: metrics — Metric vs span attribute vs resource attribute](https://github.com/NVIDIA-NeMo/Lens/blob/main/docs/user-guide/metrics.md#metrics-vs-span-attributes-vs-resource-attributes).

## Adding custom metrics

To add Megatron-specific metrics, add a new file under `megatron/core/telemetry/` following the pattern in `megatron/core/telemetry/training_metrics.py`:

1. Declare a `WeakKeyDictionary` for per-Meter instrument caching.
2. Implement `_get_<domain>_instruments(meter)` that creates and caches instruments.
3. Implement `record_<domain>_metrics(meter, **kwargs)` that records only non-`None` values.

Use `megatron.<subsystem>.<metric>` naming for application-specific metrics, reserving the shared `dl.*` and `gen_ai.*` namespaces for cross-consumer or standard metrics.

See the existing `nemo.lens.instruments.inference` as a template.