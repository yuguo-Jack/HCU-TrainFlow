---
id: doc-yuguo-jack-hyperloom-6745f0dfa2cc0dd84365
title: yuguo-Jack/Hyperloom / docs/components/agentkernelarena.md
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
path: docs/components/agentkernelarena.md
raw_sha256: e92bfb4dbfc96aa3531924903c580348f50c6b7738f705b8e38616ed5a6f0a0e
sources: []
generated_body_sha256: 02797eb2754c3e53453a50467772eea430fba7f3b71b836fe64ec980ef962639
source_state: current-scan
---

# yuguo-Jack/Hyperloom / docs/components/agentkernelarena.md

[Original at fixed commit](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/docs/components/agentkernelarena.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
myst:
    html_meta:
        "description": "Learn about AgentKernelArena, a standardized AMD evaluation arena for measuring AI coding agent performance on GPU kernel optimization tasks on ROCm."
        "keywords": "AgentKernelArena, GPU kernel, optimization, AI agents, ROCm, HIP, Triton, AMD GPU, evaluation, benchmark, leaderboard, Hyperloom"
---
# AgentKernelArena

AgentKernelArena is a standardized evaluation arena, built by AMD, that measures
how well AI coding agents perform on real GPU kernel optimization tasks. It runs
LLM-powered agents side-by-side on the same tasks in isolated workspaces and
scores them with objective, reproducible metrics for compilation, correctness,
and GPU performance.

- **Source**: <https://github.com/AMD-AGI/AgentKernelArena>
- **License**: MIT

## Role in Hyperloom

AgentKernelArena is not part of Hyperloom's default install or optimization
loop. It is a companion evaluation harness for comparing Hyperloom's
kernel-optimization agents against other AI coding agents on standardized GPU
kernel tasks. Its task categories (`hip2hip`, `triton2triton`, `flydsl2flydsl`,
and others) overlap with the kernel types that Hyperloom's kernel agent handles
through GEAK, but Hyperloom does not clone or invoke
AgentKernelArena in the normal runtime path.

## AgentKernelArena documentation

For detailed documentation on AgentKernelArena, see [AgentKernelArena on ROCm Docs](https://rocm.docs.amd.com/projects/agent-kernel-arena/en/latest/).
