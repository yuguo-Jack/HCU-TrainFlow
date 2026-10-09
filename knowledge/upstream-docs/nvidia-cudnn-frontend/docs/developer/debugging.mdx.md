---
id: doc-nvidia-cudnn-frontend-b53568675f2fedf79024
title: NVIDIA/cudnn-frontend / docs/developer/debugging.mdx
engine: cudnn-frontend
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: NVIDIA/cudnn-frontend
commit: 51a3de73e122aeedafe68070acf3b7ff3970534e
path: docs/developer/debugging.mdx
raw_sha256: b8788eb6cd49c1bc7625d9b8075086e193ab184b7e2a7b5b9378cb7fa504331d
sources: []
generated_body_sha256: 3f6917522afe13de2ef94ad06421fd46253e086eaf3be207e13647d44188d17a
source_state: current-scan
---

# NVIDIA/cudnn-frontend / docs/developer/debugging.mdx

[Original at fixed commit](https://github.com/NVIDIA/cudnn-frontend/blob/51a3de73e122aeedafe68070acf3b7ff3970534e/docs/developer/debugging.mdx)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
title: "Debugging"
---
For initial debugging, we recommend turning on the cuDNN frontend logging and checking for warnings and errors. The cuDNN frontend API logging records the execution flow through the cuDNN frontend API. This functionality is disabled by default, and can be enabled through methods described in this section.

## Debugging by Using Environment Variables

| Environment Variables | `CUDNN_FRONTEND_LOG_INFO=0` | `CUDNN_FRONTEND_LOG_INFO=1` |
| --- | --- | --- |
| `CUDNN_FRONTEND_LOG_FILE` not set | No Logging | No Logging |
| `CUDNN_FRONTEND_LOG_FILE` set to `stdout` or `stderr` | No Logging | Logging to `cout` or `cerr` |
| `CUDNN_FRONTEND_LOG_FILE` set to `filename.txt` | No Logging | Logging to the filename |

## Debugging by Using API Calls

Calling `cudnn_frontend::isLoggingEnabled() = true|false` has the same effect of setting the environment variable. Calling `cudnn_frontend::getStream() = stream_name` can be used to assign the output stream directly.

For further debugging, refer to the [Error Reporting and API Logging](https://docs.nvidia.com/deeplearning/cudnn/backend/latest/reference/troubleshooting.html#api-logging) to turn on the cuDNN backend logs.