---
id: ecosystem/cases/mindspeed-ep-constraints
title: 案例：MoE overlap 的参数约束就是正确性契约
engine: mindspeed
kind: authored
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected source, official documentation and related PR reading; no HCU runtime
  validation
sources:
- source: ascend-mindspeed
  path: mindspeed/features_manager/moe/moe_alltoall_overlap.py
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: 98f147c94abd5db221b522a34a396d8a046f571e0d2075d3f6eb574aa322f6ec
- source: ascend-mindspeed
  path: mindspeed/features_manager/moe/moe_zero_memory.py
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: ef0f3874ed9f81d07aa70d701f2b2a62e78bf8c913832c4ab078bda371658248
---

# 案例：MoE overlap 的参数约束就是正确性契约

## 问题与机制

当前固定Core仍在注册MoE overlap前校验dispatcher、EP/TP、grouped GEMM与异步排列通信；这些条件决定布局、调用链与梯度依赖，而非仅为CLI整洁。已有案例经新HEAD复核后仍成立。[机制专题](../topics/mindspeed-moe-overlap-memory.md)补充Zero Memory与共享专家的成本和限制。

## 实现位置与参数边界

`MoEAlltoAllOverLapFeature`只接受EP>1及alltoall/alltoall_seq，要求grouped GEMM并拒绝use_ascend_mc2组合。alltoall禁止moe_tp_extend_ep，有shared expert时会调整共享专家overlap；alltoall_seq要求permutation异步通信，TP>1另有扩展EP条件。feature不仅替换MoELayer，还参与MLP/TransformerLayerpatch，需保存校验后的最终值。

此行为不能套到官方Bridge，其EP与shared-expert overlap当前约束不同；也不能用独立CoreHEAD替代MindSpeed-LLM实际锁定底座。

## 验证与复用决定

覆盖EP=1拒绝、dispatcher两类、TP=1/多TP、共享专家有无、grouped GEMM支持/fallback、重算/Zero Memory组合。合法配置比较输出、dgrad/wgrad、重复microbatch、router/aux loss和阶段loss；非法组合早期拒绝。记录各rank token偏斜、collective序列、异步句柄和峰值显存，性能以端到端关键路径判断。

本次没有HCU实测；可复用的结论是“调度提案必须记录实际dispatcher、隐式参数、依赖/互斥与验证”，不是任意平台同名flag可直接启用。失败时恢复普通dispatcher与缓存/计算完整路径，复核[总览](../overview/engineering-guide.md)与LLM实际gitlink。

## 固定证据与复核范围

- [mindspeed/features_manager/moe/moe_alltoall_overlap.py](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/mindspeed/features_manager/moe/moe_alltoall_overlap.py)
- [mindspeed/features_manager/moe/moe_zero_memory.py](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/mindspeed/features_manager/moe/moe_zero_memory.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
