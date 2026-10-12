---
id: doc-yuguo-jack-hyperloom-abfd3fa9a7cf9ecb66b9
title: yuguo-Jack/Hyperloom / docs/kernelforge/how-to/extending.md
engine: hyperloom
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: yuguo-Jack/Hyperloom
commit: 0425bde3f6e76e1588400c37d056dfd3bb75ac11
path: docs/kernelforge/how-to/extending.md
raw_sha256: 2b72594de15db211580237bd19bed54c2b85a228ae161f19a7d61c50415e17ac
sources: []
generated_body_sha256: baf24eb24444f30c4790968a3a70b30fc7e0b7b8e799742ef3a151ce7cd30f85
source_state: current-scan
---

# yuguo-Jack/Hyperloom / docs/kernelforge/how-to/extending.md

[Original at fixed commit](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/kernelforge/how-to/extending.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
myst:
  html_meta:
    "description": "How to extend KernelForge: add a new kernel backend agent, a new MCP tool, or new knowledge-base entries."
    "keywords": "KernelForge, extending, add kernel backend, add MCP tool, knowledge base, kernel_backends/base.py, mcp_server"
---

# Add a kernel backend, tool, or knowledge

KernelForge is designed to be extended. The three most common extension points
are a new kernel backend, a new GPU tool, and new knowledge.

## Add a new kernel backend agent

1. Create `src/kernelforge/kernel_backends/mybackend/` with:
   - `__init__.py`
   - `prompts.py` (defining `build_system_prompt(gpu_target, knowledge_content)`)
2. Add backend knowledge under `local_knowledge/languages/mybackend/`.
3. Register the backend in
   `src/kernelforge/kernel_backends/constants.py:KERNEL_BACKEND_PROMPT_MODULES`.

`--kernel-backend mybackend` then selects it.

## Add a GPU toolchain helper

1. Create `src/kernelforge/mcp_server/tools/mytool.py`.
2. Call it from the loop stage that needs it — the tools are plain functions,
   invoked directly rather than through a protocol.

## Add knowledge

Drop a `.md` file into the shipped tree at
`src/kernelforge/data/local_knowledge/languages/<language>/`, following the
`INDEX.md` layout already there. It is automatically loaded and injected into
the relevant kernel backend's prompt. Keep each file under about 2K tokens so
prompts stay focused.

Lessons the loop distils for itself go somewhere else — the *writable*
`knowledge_base/<backend>/learned/` under `$KERNELFORGE_PROJECT_ROOT` (default
`~/.cache/hyperloom/kernelforge`). Nothing under the installed package is
written at runtime.
