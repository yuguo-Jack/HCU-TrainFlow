---
id: doc-sgl-project-sglang-83904cdffd7737b8f9b2
title: sgl-project/sglang / docs/docs/references/torch_compile_cache.mdx
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
path: docs/docs/references/torch_compile_cache.mdx
raw_sha256: 0ac66d959366823ded94fbc35fc9731b5d68e20a5855405ffead2a01627756e5
sources: []
generated_body_sha256: f53a93948dea8fe81cfa2d5786dab70fba2989fdded6347fcebc037e27958161
source_state: current-scan
---

# sgl-project/sglang / docs/docs/references/torch_compile_cache.mdx

[Original at fixed commit](https://github.com/sgl-project/sglang/blob/bd2d73daa5afda6bcad8d479a834f2e70bbe9569/docs/docs/references/torch_compile_cache.mdx)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
title: "Enabling cache for torch.compile"
metatags:
    description: "SGLang torch.compile cache: TORCHINDUCTOR_CACHE_DIR for faster deployment across multiple machines."
---
SGLang uses `max-autotune-no-cudagraphs` mode of torch.compile. The auto-tuning can be slow.
If you want to deploy a model on many different machines, you can ship the torch.compile cache to these machines and skip the compilation steps.

This is based on https://pytorch.org/tutorials/recipes/torch_compile_caching_tutorial.html


1. Generate the cache by setting TORCHINDUCTOR_CACHE_DIR and running the model once.
```text Output
TORCHINDUCTOR_CACHE_DIR=/root/inductor_root_cache python3 -m sglang.launch_server --model meta-llama/Llama-3.1-8B-Instruct --enable-torch-compile
```
2. Copy the cache folder to other machines and launch the server with `TORCHINDUCTOR_CACHE_DIR`.