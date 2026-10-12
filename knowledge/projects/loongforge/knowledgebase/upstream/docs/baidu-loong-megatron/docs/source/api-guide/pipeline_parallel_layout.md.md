---
id: doc-baidu-loong-megatron-f67745864330ad5172ee
title: baidu-baige/Loong-Megatron / docs/source/api-guide/pipeline_parallel_layout.md
engine: loongforge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: baidu-baige/Loong-Megatron
commit: 64c279afb879229cff12fb293624e3691990403f
path: docs/source/api-guide/pipeline_parallel_layout.md
raw_sha256: 47bdd29137dc8e48c7a67d6086af84ca3e3a66a38ce774f4429cd26b65b82ebf
sources: []
generated_body_sha256: 1222823043b3e614e2ade64a7fbb2bece39232d1654e433116dafaa722e8db42
source_state: current-scan
---

# baidu-baige/Loong-Megatron / docs/source/api-guide/pipeline_parallel_layout.md

[Original at fixed commit](https://github.com/baidu-baige/Loong-Megatron/blob/64c279afb879229cff12fb293624e3691990403f/docs/source/api-guide/pipeline_parallel_layout.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Custom Pipeline Model Parallel Layout

*This is an experimental feature and may be changed.*

`--pipeline-model-parallel-layout` is a flexible API for defining the pipeline parallel partitioning, which is essential for balanced partitioning for an imbalanced model. For example, to partition DeepSeek-V3 (61 decoder layers + 1 mtp layer) with PP16VPP2, we can include the arguments as follows:

```bash
--pipeline-model-parallel-size 16
--pipeline-model-parallel-layout "Et*3|(tt|)*29,m|L"
```

| PP \ VPP rank |            0            |       1       |
|---------------|-------------------------|---------------|
|       0       | embedding + 3 × decoder |  2 × decoder  |
|      1~13     |        2 × decoder      |  2 × decoder  |
|       14      |        2 × decoder      |      mtp      |
|       15      |        2 × decoder      |      loss     |

In the layout string, stages are split by '|'. Replicated stages or layers can be described with multiplication. Commas can be used cosmetically. Symbol choices:

* `E` = embedding layer
* `t` = transformer decoder layer
* `m` = MTP layer
* `L` = loss calculation layer

Note that it is legal to have empty stages, e.g., `E||t|L` (the second stage is empty).
