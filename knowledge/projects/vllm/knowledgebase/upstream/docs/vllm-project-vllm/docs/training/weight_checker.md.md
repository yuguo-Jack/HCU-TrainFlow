---
id: doc-vllm-project-vllm-e6a1bb2872c5ef5f034f
title: vllm-project/vllm / docs/training/weight_checker.md
engine: vllm
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: vllm-project/vllm
commit: f0a5f111f205b5c73bb34fbd41f8f0d9936b543f
path: docs/training/weight_checker.md
raw_sha256: a7ffac8123c9782e48d55cea5a3d34132701f3026e22653ed707dffd0e532ae0
sources: []
generated_body_sha256: e30df51167381c454ae8d3454afe239604982c947c24ded01d26a178e6d7bc9c
source_state: current-scan
---

# vllm-project/vllm / docs/training/weight_checker.md

[Original at fixed commit](https://github.com/vllm-project/vllm/blob/f0a5f111f205b5c73bb34fbd41f8f0d9936b543f/docs/training/weight_checker.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Weight Checker

The Weight Checker verifies that an RL weight update landed on every rank. It
hashes each model parameter with SHA-256, so a caller can save the original
digests, reset the weights, transfer them back, and confirm they match.

Enable it with `VLLM_SERVER_DEV_MODE=1`. All operations use
`POST /weight_checker`:

| Request | Response |
| --- | --- |
| `{"action": "checksum"}` | `{"checksums": {key: sha256_hex}}` |
| `{"action": "reset"}` | `{"status": "reset"}` |
| `{"action": "compare", "baseline": {key: sha256_hex}}` | `{"match": bool, "mismatches": [key]}` |

Keys have the form `dp{dp}:pp{pp}:pcp{pcp}:tp{tp}:{tensor_name}`, so each
shard is checked separately. All actions cover the target model's parameters,
which is what weight loading writes; `reset` zeroes them. The endpoint keeps no
state, so the caller holds the baseline. Invalid requests return HTTP 400.

## RL weight-update check

```bash
URL=http://localhost:8000

# 1. Stop serving, then save the original digests.
curl -X POST "$URL/pause?mode=abort"
curl -X POST $URL/weight_checker -H 'Content-Type: application/json' \
  -d '{"action":"checksum"}' > baseline.json

# 2. Zero the weights.
curl -X POST $URL/weight_checker -H 'Content-Type: application/json' \
  -d '{"action":"reset"}'

# 3. Transfer the original weights with start/update/finish_weight_update.

# 4. Compare against the baseline; expect {"match": true, "mismatches": []}.
curl -X POST $URL/weight_checker -H 'Content-Type: application/json' \
  -d "{\"action\":\"compare\",\"baseline\":$(jq .checksums baseline.json)}"

curl -X POST $URL/resume
```

## Limitations

- Stay paused from `checksum` to `compare`: the weights are invalid between
  `reset` and the transfer, and EPLB moves experts while serving.
- A request covers the engines managed by the API server it reaches. With
  several API servers (for example `--data-parallel-external-lb`), send it to
  each one.
- Buffers, draft models and LoRA adapters are not checked.
- CPU backends that repack linear weights hide them from the checker.
- compressed-tensors online transforms are not supported: their Hadamard
  weights are normalized once per storage, so restored copies differ.
- MoE weights padded beyond the checkpoint shape (DeepEP hidden size, MXFP4)
  keep uninitialized padding, so `compare` reports them as mismatches.
- The engine must be awake: sleep levels 1 and 2 release the weight memory.
- `--offload-backend prefetch` is not supported: parameters point at staging
  buffers, not the offloaded weights.
- Hashing copies every weight to CPU, so keep it off latency-sensitive paths.