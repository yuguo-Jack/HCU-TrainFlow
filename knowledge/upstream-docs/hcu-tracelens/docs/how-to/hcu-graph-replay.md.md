---
id: doc-hcu-tracelens-a9b2eb6068779723e425
title: yuguo-Jack/TraceLens / docs/how-to/hcu-graph-replay.md
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
path: docs/how-to/hcu-graph-replay.md
raw_sha256: 26e52400eb7aeb07902d9b05a862ad20f1170b1c340e2b4d59da924a5489b1c1
sources: []
generated_body_sha256: 24ea89b4278165c2a34c15aad986add9ad3d764d1e1027c5fffcbad9c4dc2ca7
source_state: current-scan
---

# yuguo-Jack/TraceLens / docs/how-to/hcu-graph-replay.md

[Original at fixed commit](https://github.com/yuguo-Jack/TraceLens/blob/30f5dcd539dd4e588678e34168c7fcf726dd987e/docs/how-to/hcu-graph-replay.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--
Copyright (c) 2026 Advanced Micro Devices, Inc. All rights reserved.

See LICENSE for license information.
-->

# HCU training graphs and isolated event replay

Training graph attribution combines **captured host/operator structure** with
**measured replay GPU events**. It preserves shapes, dtypes and strides recorded
by the capture profiler. It does not infer missing shapes, restore training
state, or establish loss/gradient equivalence. Validate the training workload's
loss, gradients and state separately on the actual HCU runtime.

HIP PyTorch uses `torch.cuda` APIs. Record shape metadata and CPU/GPU activities
in both capture and replay traces. Annotate each graph segment explicitly:

```python
from torch.profiler import record_function

with record_function("tracelens.train_graph.capture:training:step"):
    with torch.cuda.graph(graph):
        training_body()

with record_function("tracelens.train_graph.replay:training:step"):
    graph.replay()
```

Each capture annotation must contain exactly one matching
`hipStreamBeginCapture`/`hipStreamEndCapture` (or CUDA-named equivalents) pair.
Each host replay annotation must contain exactly one graph launch on its own
process/thread. Repeat a replay annotation for repeated executions. Use distinct
segment IDs for independently captured forward/backward segments. IDs may use
letters, digits, `_`, and `-`. GPU copies of the annotation are ignored.

## Strict graph sidecar

The bundle contains capture/replay traces plus a JSON sidecar. Hashes bind exact
trace bytes; signatures must come from actual tensors at capture and replay.
Filenames are relative to the capture folder and cannot escape it.

```json
{
  "schema": "tracelens.training_graph.v1",
  "mapping_contract": "serialized_single_stream",
  "replay_file": "replay.json",
  "replay_sha256": "<64 lowercase SHA256 hex characters>",
  "provenance": {
    "torch_version": "<actual Torch version>",
    "hip_version": "<actual HIP version>",
    "device_type": "hcu",
    "signature_source": "runtime_tensor_metadata"
  },
  "captures": [{
    "capture_id": "training",
    "segment_id": "step",
    "phase": "train_step",
    "file": "capture.json",
    "sha256": "<64 lowercase SHA256 hex characters>",
    "input_signature": [
      {"name": "x", "shape": [2, 3], "dtype": "torch.float32", "stride": [3, 1]}
    ],
    "replay_input_signature": [
      {"name": "x", "shape": [2, 3], "dtype": "torch.float32", "stride": [3, 1]}
    ]
  }]
}
```

`phase` is `forward`, `backward`, or `train_step`. The two signatures must agree
exactly. The serialized single-stream contract is a declaration by the capture
producer; TraceLens additionally checks nonoverlapping dispatches, one explicit
GPU stream, identical counts and ordered compute-kernel identities. Every
compute dispatch must record `args.kernel`. Memcpy and memset match their event
classes at the same position. No batch-size rounding, event skipping, grouping
by approximate names, or ambiguous multistream mapping is accepted.

The capture API window includes all host threads in its process, including
autograd workers. Capture CPU timestamps/durations remain in `capture_origin`.
Augmented CPU events have zero duration and `timing_origin=capture_structure_only`;
only original replay GPU events contribute measured GPU time. A failure rejects
the whole mapping and produces no partly augmented result.

```python
from TraceLens.Trace2Tree.training_graph import (
    generate_training_graph_report, merge_training_capture_trace, sha256_file,
)

tree = merge_training_capture_trace("bundle", "bundle/contract.json")
tables = generate_training_graph_report(
    "bundle", "bundle/contract.json",
    output_csvs_dir="results/graph",
    collective_analysis=False,
    gpu_arch_json_path="actual-hcu-ceilings.json",
)
```

The report uses native `TreePerfAnalyzer` and PerfModel tables, including each
captured forward/backward operation's metadata. Hardware ceilings come from the
supplied architecture options. `graph_attribution` gives raw replay event index,
raw capture dispatch/operator indexes, source hashes, owner, shape/dtype/stride
and measured GPU duration. `graph_contract` records replay instances;
`graph_sanity` records GPU time/count checks. A training report fails if kernel
accounting or per-kernel attribution checks fail.

```shell
python -m TraceLens.Trace2Tree.training_graph \
  --capture-folder bundle --manifest bundle/contract.json \
  --replay bundle/replay.json --report results/graph-contract.json \
  --csvs-dir results/graph --gpu-arch-json actual-hcu-ceilings.json
```

The CLI writes `status=complete` or `status=rejected` with a reason and returns
a nonzero exit status on rejection. The existing merge API recognizes a training
sidecar object; upstream inference metadata lists retain their original behavior.

## Same-shape operator replay

`EventReplayer.replay()` returns the actual operator output. It resolves one
exact installed schema overload and permits a bounded set of functional ATen
operators, including GEMM, elementwise/reduction operations and supported
activation/softmax/layer-normalization backward operations. Mutating/out,
collective, custom, RNG and stateful operations have no supported replay
contract. Tensor lists and incomplete or ambiguous schemas are rejected.

The default `input_semantics="synthetic"` creates fresh values with the recorded
dtype and strides. It benchmarks an isolated same-shape operator; it is not a
captured-value reproduction. Expanded/zero-stride layouts are preserved.
Metadata must explicitly include `Input type`, `Input Dims`, `Input Strides` and
`Concrete Inputs`. Missing strides are never replaced with contiguous strides.
Storage allocation is bounded (16,777,216 elements by default).

Captured-value replay requires exactly the named tensor arguments and preserves
their logical values/dtype/strides across CPU/HIP transfer. Shared input storage
is rejected because this contract does not model aliasing. Replay detaches
inputs and uses `no_grad`; it does not accumulate parameter gradients.

```python
from TraceLens import EventReplayer

replayer = EventReplayer(
    recorded_mm_event, device="cuda",
    input_semantics="captured",
    input_values={"self": captured_x, "mat2": captured_w},
)
output = replayer.verify(captured_output, rtol=1e-5, atol=1e-6)
```

`verify()` checks output structure, shape, dtype, finite values and numerical
agreement. It raises on failure and requires captured inputs. Multi-output
backward operators can be checked against a tuple reference. Capture values and
reference from the **same invocation**; matching shapes cannot prove their
provenance. Keep this operator check separate from training loss/state checks.

Export a replay bundle next to its source trace (or in a parent directory):

```python
from TraceLens.EventReplay.hcu_replay import write_replay_bundle

write_replay_bundle(
    "bundle/eager.json", raw_event_index, "bundle/mm-replay.json",
    provenance={
        "torch_version": actual_torch_version,
        "hip_version": actual_hip_version,
        "device_type": "hcu",
        "signature_source": "runtime_tensor_metadata",
        "values_source": "captured_runtime",
    },
    input_values={"self": captured_x, "mat2": captured_w},
    expected_output=captured_output,
)
```

This writes JSON metadata and a tensor-only `.pt` file, binds their hashes and
the raw source event index, and stores the exact operator schema. Omitting
`input_values` deliberately creates a synthetic bundle with no captured-output
verification. The runner loads tensors with `weights_only=True`.

```shell
python -m TraceLens.EventReplay.hcu_replay \
  --bundle bundle/mm-replay.json --device hcu \
  --warmup 3 --steps 10 --max-seconds 30 \
  --report results/mm-replay.json
```

`hcu` requires a HIP PyTorch build; the report includes actual device name and
architecture. Explicit `cpu` or `cuda:<index>` are supported; unavailable devices
never fall back silently. Timing uses synchronized device events on HIP/CUDA
and wall clock on CPU, with prepared inputs. Warmup, sample counts and wall time
between completed calls are bounded. Python cannot preempt a running kernel or
device synchronization, so use an external process deadline for runtime failure
qualification. The report records input semantics, source hashes, tolerances,
numerical status, actual runtime and individual timing samples. Numerical or
provenance failures return nonzero; missing verification is `not_requested`.
