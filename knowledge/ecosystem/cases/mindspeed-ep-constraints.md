---
id: ecosystem/cases/mindspeed-ep-constraints
title: 案例：MoE overlap 的参数约束就是正确性契约
engine: mindspeed
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: ascend-mindspeed
  path: mindspeed/features_manager/moe/moe_alltoall_overlap.py
  commit: 485d1077017a39963de83944230cfab26a6ec467
  sha256: 98f147c94abd5db221b522a34a396d8a046f571e0d2075d3f6eb574aa322f6ec
---

# 案例：MoE overlap 的参数约束就是正确性契约

## 源码事实

`MoEAlltoAllOverLapFeature` 在注册补丁前校验 dispatcher 和 EP。该实现限定 alltoall/alltoall_seq 且 EP 大于 1；需要 grouped GEMM。alltoall_seq 路径还要求异步 permutation 通信，TP 大于 1 时存在额外配置条件。

它会替换 MoELayer/MLP 等接口；alltoall 配合 shared expert 时还可能自动开启 shared-expert overlap。这里的行为不能套用到官方 Bridge，因为后者对应组合可能要求互斥。

## 对 HCU 的启发

优化提案必须同时记录“实际调用哪个 dispatcher、会隐式改哪些参数、依赖什么并行布局”。调度改动只提高通信并发但没有维持梯度依赖，会造成难以在单算子测试中发现的错误。

## 验证计划

构造 EP=1 拒绝路径、两类 dispatcher、TP=1/多 TP、共享专家有/无、grouped GEMM fallback 等矩阵。对合法组合检查输出、dgrad/wgrad、重复迭代和阶段 loss；对非法组合应早期报错。收集所有参与 ranks 的 token 分布、collective 顺序和峰值显存。

## 固定源码与更新范围

- [mindspeed/features_manager/moe/moe_alltoall_overlap.py](https://github.com/Ascend/MindSpeed/blob/485d1077017a39963de83944230cfab26a6ec467/mindspeed/features_manager/moe/moe_alltoall_overlap.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
