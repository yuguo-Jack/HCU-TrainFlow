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
commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
path: docs/source_zh/embodied_tutorial/quick_start_index.md
raw_sha256: c1e5db6f2fca31d0024f7be374a541946454a2a6d9be614437b0387414177710
sources: []
generated_body_sha256: 15d27f42a151c2ac5ab8b13bcb23d3767f84db9a8b13a96dc0e1d586e78ca879
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source_zh/embodied_tutorial/quick_start_index.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source_zh/embodied_tutorial/quick_start_index.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# 快速入门

每个支持的具身模型均在 [`examples/embodied/`](https://github.com/baidu-baige/LoongForge/tree/master/examples/embodied) 下提供了开箱即用的启动脚本。请在下方选择对应模型的指南；框架整体约定（目录结构、启动脚本、配置分层）请参阅[概述](overview.md)。

## VLA 模型

视觉-语言-动作（VLA）模型，将相机观测与语言指令映射为机器人动作。

```{toctree}
:maxdepth: 1

quick_start_pi05
quick_start_groot_n1_6
quick_start_groot_n1_7
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
