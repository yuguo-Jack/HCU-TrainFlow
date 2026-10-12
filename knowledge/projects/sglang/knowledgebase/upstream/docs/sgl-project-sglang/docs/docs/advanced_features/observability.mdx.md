---
id: doc-sgl-project-sglang-d702610c9514c33ae9d3
title: sgl-project/sglang / docs/docs/advanced_features/observability.mdx
engine: sglang
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: sgl-project/sglang
commit: bd2d73daa5afda6bcad8d479a834f2e70bbe9569
path: docs/docs/advanced_features/observability.mdx
raw_sha256: f8eb0d926b3452809108aec3250da84361c85475d46354ab35bed5bbb9fa6b49
sources: []
generated_body_sha256: 924b30d5cd58fa2ff577546c8ac86dadcbf04d013dd7c8417e7fce5fe3b2578a
source_state: current-scan
---

# sgl-project/sglang / docs/docs/advanced_features/observability.mdx

[Original at fixed commit](https://github.com/sgl-project/sglang/blob/bd2d73daa5afda6bcad8d479a834f2e70bbe9569/docs/docs/advanced_features/observability.mdx)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
title: "Observability"
metatags:
    description: "SGLang observability: Prometheus metrics, request logging, request dump and replay, crash dump debugging."
---
## Production Metrics
SGLang exposes the following metrics via Prometheus. You can enable them by adding `--enable-metrics` when launching the server.
You can query them by:
```bash Command
curl http://localhost:30000/metrics
```

See [Production Metrics](../references/production_metrics) and [Production Request Tracing](../references/production_request_trace) for more details.

## Logging

By default, SGLang does not log any request contents. You can log them by using `--log-requests`.
You can control the verbosity by using `--log-request-level`.
See [Logging](./server_arguments#logging) for more details.

You can change verbosity at runtime:

```bash Command
python3 -m sglang.srt.managers.configure_logging --url http://localhost:30000 --log-level=debug
```

## Request Dump and Replay

You can dump all requests and replay them later for benchmarking or other purposes.

To start dumping, use the following command to send a request to a server:
```bash Command
python3 -m sglang.srt.managers.configure_logging --url http://localhost:30000 --dump-requests-folder /tmp/sglang_request_dump --dump-requests-threshold 100
```
The server will dump the requests into a pickle file for every 100 requests.

To replay the request dump, use `scripts/playground/replay_request_dump.py`.

## Crash Dump and Replay
Sometimes the server might crash, and you may want to debug the cause of the crash.
SGLang can preserve recent request data for replay and collect CUDA device coredumps for low-level debugging.

Set the crash diagnostics folder with `--crash-dump-folder /tmp/crash_dump`.

When SGLang handles a crash, it writes completed requests retained by the crash-dump buffer plus in-flight requests to `/tmp/crash_dump/<hostname>/crash_dump_<timestamp>.pkl`. The file also contains the server arguments and launch command. Replay it with `scripts/playground/replay_request_dump.py`.

On NVIDIA CUDA, the option also sets default environment variables before CUDA initializes. These defaults enable device coredumps on CUDA exceptions and allow SGLang to trigger device coredumps for live scheduler processes when it handles a crash. CUDA device coredumps are written to `/tmp/crash_dump/<hostname>/core.cuda.<timestamp>.<pid>`. Explicitly configured CUDA coredump environment variables take precedence, including a custom `CUDA_COREDUMP_FILE` path. This option does not configure OS process core dumps.