---
id: doc-ascend-mindspeed-llm-0af12e52522a22b74d65
title: Ascend/MindSpeed-LLM / docs/zh/pytorch/features/mcore/kvallgather-context-parallel.md
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
path: docs/zh/pytorch/features/mcore/kvallgather-context-parallel.md
raw_sha256: 6c72c8a38794e3d08d10a563ec2277c2977229f1d1d243b3b5ea8508fc680706
sources: []
generated_body_sha256: 771f891a167b925030ecd18fa0a66a78860e9b4f203006daee62eff8d55dfe34
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/zh/pytorch/features/mcore/kvallgather-context-parallel.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/zh/pytorch/features/mcore/kvallgather-context-parallel.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# kvallgather 长序列并行

## 特性介绍

针对 sparse flash attention、lightning indexer、lightning indexer loss，在计算前对已切分的key和value执行allgather通信操作获得完整的key和value。

详细介绍请参考[**kvallgather_cp_algo**](https://gitcode.com/Ascend/MindSpeed/blob/master/docs/zh/features/kvallgather-context-parallel.md)。

## 使用方法

| 重要参数                                               | 参数说明                                                   |
|----------------------------------------------------|--------------------------------------------------------|
| --context-parallel-size [int]                      | 设置CP对应的数量，默认为1，根据用户需求配置。                               |
| --context-parallel-algo <b>kvallgather_cp_algo</b> | 长序列并行算法选项，设置为`kvallgather_cp_algo`，开启KVAllGather长序列并行。 |
| --seq-length [int]                                 | 输入序列的长度。                                               |

## 注意事项

1. 当前仅适配了sparse flash attention、lightning indexer融合算子、lightning indexer loss融合算子。
2. 当前仅支持`attention-mask-type`为`causal`。
3. 仅支持定长padding训练场景，采用负载均衡的序列切分方式，`--seq-length`要求能被 2 * context-parallel-size整除。
