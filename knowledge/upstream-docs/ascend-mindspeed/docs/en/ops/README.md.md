---
id: doc-ascend-mindspeed-a78d1eb159a8f519b0c7
title: Ascend/MindSpeed / docs/en/ops/README.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed
commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
path: docs/en/ops/README.md
raw_sha256: 5c0409c9e8d44a90fa064e3e7b361cb2cd644ac8ed4215502473f443217a5a33
sources: []
generated_body_sha256: 5786559cbd9403383b65ac604e0540be878fcb55d3f4e0870e8f61653acb6eaf
source_state: current-scan
---

# Ascend/MindSpeed / docs/en/ops/README.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/ops/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# How to Run an Operator

## Prerequisites

+ CANN
+ CANN-NNAL (Ascend-Transformer-Boost)
+ TorchNPU

## Compilation and Installation

### 1. Environment Variable Settings

```shell
# The default path is used. Change it if necessary.
source /usr/local/Ascend/ascend-toolkit/set_env.sh
```

#### If the Ascend Transformer Boost is used

```shell
# The default path is used. Change it if necessary.
source /usr/local/Ascend/nnal/atb/set_env.sh
```

### 2. Included Header Files

+ Latest TorchNPU version
+ Latest CANN version

### 3. Installation Scripts

```shell
python3 setup.py build
python3 setup.py bdist_wheel
pip3 install dist/*.whl --force-reinstall
```
