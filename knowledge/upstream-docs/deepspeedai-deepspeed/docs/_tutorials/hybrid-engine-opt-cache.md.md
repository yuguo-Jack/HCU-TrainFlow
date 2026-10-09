---
id: doc-deepspeedai-deepspeed-c8cf1ff5557c3459fdd4
title: deepspeedai/DeepSpeed / docs/_tutorials/hybrid-engine-opt-cache.md
engine: deepspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: deepspeedai/DeepSpeed
commit: bc1ad320a9afb516797577924a9983c6d7cd6793
path: docs/_tutorials/hybrid-engine-opt-cache.md
raw_sha256: 7bc72e9abe9835a9e87f5321a4717f7cd3acd4552f4f86b6e42c33b45198a628
sources: []
generated_body_sha256: 61a3e63d7a6d9433280f7c4c35b51c2ce95dd397fa7595764e050c32d4b98c6a
source_state: current-scan
---

# deepspeedai/DeepSpeed / docs/_tutorials/hybrid-engine-opt-cache.md

[Original at fixed commit](https://github.com/deepspeedai/DeepSpeed/blob/bc1ad320a9afb516797577924a9983c6d7cd6793/docs/_tutorials/hybrid-engine-opt-cache.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
title: "Hybrid Engine OPT cache compatibility"
---

Hybrid Engine's injected OPT layers implement the legacy tuple-cache interface.
OPT decoder layers exposing `cache_position` or `past_key_values` use a newer
cache contract. Those models now retain native Hugging Face generation, with
an explicit warning that inference acceleration is unavailable. Training and
`engine.module.generate()` remain available; this does not add native-kernel
support for the newer Cache interface.

The legacy OPT injection path is unchanged. The fallback does not provide
inference tensor parallelism, continuous-batching native-cache operations, or
CUDA Graph acceleration. Use the supported legacy path when those features
are required.

The offline regression in
`tests/unit/hybrid_engine/test_he_opt_cache.py` uses two data-parallel ranks,
a tiny randomly initialized OPT, and repeated training/generation transitions.
Each rank compares greedy output tokens with an independent Hugging Face model
loaded from the updated weights. No model download is required.