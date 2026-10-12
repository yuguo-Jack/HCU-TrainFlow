---
id: doc-sgl-project-sglang-0aec51501da00dbb2675
title: sgl-project/sglang / docs/docs/advanced_features/session_radix_cache.mdx
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
path: docs/docs/advanced_features/session_radix_cache.mdx
raw_sha256: 0b50a3e5b8b5e97d3ce035801d18183ce1fa06dba9f6644f9c0f75bc0bf748cd
sources: []
generated_body_sha256: f0fca9983911bc2bf8c79d17a27c44957e0dd02abd908ebfa4408eb090c55d69
source_state: current-scan
---

# sgl-project/sglang / docs/docs/advanced_features/session_radix_cache.mdx

[Original at fixed commit](https://github.com/sgl-project/sglang/blob/bd2d73daa5afda6bcad8d479a834f2e70bbe9569/docs/docs/advanced_features/session_radix_cache.mdx)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
title: "Session-Aware Radix Cache"
metatags:
    description: "Keep active sessions ahead of unrelated KV in UnifiedRadixCache eviction order."
---

Session-aware radix caching improves cache hits for long-lived, multi-turn workloads under memory pressure. It registers reusable KV to a session and evicts unreferenced KV before KV still referenced by an active session.

Session references are soft protection, not memory pins. Referenced KV can still be evicted when reclaiming unreferenced KV is insufficient.

## Enable the cache

This feature is implemented only by `UnifiedRadixCache`.

```bash Command
python3 -m sglang.launch_server \
  --model-path MODEL_PATH \
  --enable-session-radix-cache
```

## Pass and close the session

Your application must pass the same top-level `session_id` on every request in a session. The ID labels cache references only; it does not append or reconstruct conversation context, so each request must still contain the intended prompt.

```bash Command
curl http://localhost:30000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "FULL_PROMPT_FOR_THIS_TURN",
    "sampling_params": {"max_new_tokens": 128},
    "session_id": "agent-42"
  }'
```

When a request finishes, SGLang automatically registers its reusable cache leaves under the `session_id`. This reference-only workflow does not require an `/open_session` call.

Call `/close_session` when the application session ends, including error and cancellation paths:

```bash Command
curl -X POST http://localhost:30000/close_session \
  -H "Content-Type: application/json" \
  -d '{"session_id": "agent-42"}'
```

Closing removes the session's references but does not immediately free its KV. The KV remains reusable and returns to the normal eviction order.

## Eviction behavior

The cache tracks references independently for each UnifiedRadixCache component. Device and host eviction use the same session preference.

| Component | Referenced data | Eviction order |
| --- | --- | --- |
| Full attention | The reusable prefix path from the registered leaf to the root | Unreferenced nodes first, then referenced nodes with fewer session references, then the configured policy such as LRU |
| Sliding-window attention (SWA) | The reusable tail covering the sliding window plus page-alignment allowance | Two LRU passes: unreferenced nodes first, then referenced nodes if more space is required |
| Mamba | The reusable state on the registered leaf | Two LRU passes: unreferenced nodes first, then referenced nodes if more space is required |

UnifiedRadixCache still applies component cascade rules. Evicting an internal Full node also evicts its SWA and Mamba data; evicting SWA also evicts Mamba data; evicting Mamba affects only Mamba. Evicting a leaf removes all component data on that leaf.