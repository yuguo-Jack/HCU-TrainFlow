---
id: doc-ascend-mindspeed-llm-c5c4f7d5a7268410a7b6
title: Ascend/MindSpeed-LLM / docs/en/pytorch/tools/deterministic_computation.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: 2fed626696175480ae1ab3342a94017301a25209
path: docs/en/pytorch/tools/deterministic_computation.md
raw_sha256: 52c23e2fb4281bb06486974dfe7396faad0384286d7ca84da700c438eb45c389
sources: []
generated_body_sha256: 85d7dba1cf3a397af0b713526ef36bd93b8ffb8ba60e3a7323e8a62d21a78d2f
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/tools/deterministic_computation.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/tools/deterministic_computation.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Ascend Deterministic Computation

## Use Cases

During training, random factors can make each run differ slightly, which prevents the loss curve, performance curve, and other results from matching exactly.
However, repeated runs and comparison experiments sometimes require deterministic results to ensure reproducibility.
To meet this need, this feature introduces deterministic computation, which lets users ensure consistent results across multiple training runs on Ascend chips and helps with performance tuning, comparison experiments, and other tasks.

## How to Use

To enable this feature, add `--npu-deterministic` to the script and set the environment variable `export HCCL_DETERMINISTIC=true`. The default seed is 1234, and you can also set a custom value.

## Effects

With deterministic computation enabled, multiple experiments with the same parameters produce the same results.

> If you configure `HCCL_LOGIC_SUPERPOD_ID`, changes in the cluster topology during RoCE communication can lead to different collective communication behavior. The communication algorithms then follow different logic, and the two deterministic schemes are not aligned.
