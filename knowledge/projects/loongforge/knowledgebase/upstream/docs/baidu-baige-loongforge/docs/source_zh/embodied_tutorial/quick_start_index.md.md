---
id: doc-baidu-baige-loongforge-7b6cef79ca28702aa17d
title: baidu-baige/LoongForge / docs/source_zh/embodied_tutorial/quick_start_index.md
engine: loongforge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: baidu-baige/LoongForge
commit: 042a68102395b9f4024d1a61084592c4c618371a
path: docs/source_zh/embodied_tutorial/quick_start_index.md
raw_sha256: dcbff205d456c4e44a68635b517ac9d267ee4b4c6e265aca847390b31c99cc33
sources: []
generated_body_sha256: 60260e62d9b0991c92ea7cc77d41d0bbc8fd34cb55548f472bf466b5214649fa
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source_zh/embodied_tutorial/quick_start_index.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/042a68102395b9f4024d1a61084592c4c618371a/docs/source_zh/embodied_tutorial/quick_start_index.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# 快速入门

每个支持的具身模型均在 [`examples/embodied/`](https://github.com/baidu-baige/LoongForge/tree/master/examples/embodied) 下提供了开箱即用的启动脚本。请在下方选择对应模型的指南；框架整体约定（目录结构、启动脚本、配置分层）请参阅[概述](overview.md)。

## VLA 模型

视觉-语言-动作（VLA）模型，将相机观测与语言指令映射为机器人动作。

```{toctree}
:maxdepth: 1

quick_start_pi05
quick_start_gr00t_n1_6
quick_start_gr00t_n1_7
quick_start_xvla
```

## WAM 模型

世界-动作（WAM）模型，学习世界动态并为具身控制生成动作。

```{toctree}
:maxdepth: 1

quick_start_lingbot_va
quick_start_cosmos3
quick_start_fastwam
quick_start_dreamzero
```
