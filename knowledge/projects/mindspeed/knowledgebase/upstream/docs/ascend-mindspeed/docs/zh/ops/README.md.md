---
id: doc-ascend-mindspeed-a3247f6a123cc2bb64d8
title: Ascend/MindSpeed / docs/zh/ops/README.md
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
path: docs/zh/ops/README.md
raw_sha256: 81840792cad9114d1fe2d5080597daedebfb8a3a87bbb4b6a94e28b5116c2b8a
sources: []
generated_body_sha256: dcffa09e8e73bd72f38f11e60b430f91dd07db3741e4c530fcbe0eb47600f720
source_state: current-scan
---

# Ascend/MindSpeed / docs/zh/ops/README.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/zh/ops/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# 如何运行算子

## 前置安装

+ CANN
+ CANN-NNAL(Ascend-Transformer-Boost)
+ TorchNPU

## 编译和安装

### 1. 设置环境变量

```shell
# 默认路径，请按需修改。
source /usr/local/Ascend/ascend-toolkit/set_env.sh
```

#### 如果使用 Ascend-Transformer-Boost

```shell
# 默认路径，请按需修改。
source /usr/local/Ascend/nnal/atb/set_env.sh
```

### 2. 包含头文件

+ 最新版本的 TorchNPU
+ 最新版本的 cann

### 3. 安装脚本

```shell
python3 setup.py build
python3 setup.py bdist_wheel
pip3 install dist/*.whl --force-reinstall
```
