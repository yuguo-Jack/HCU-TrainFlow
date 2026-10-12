---
id: ecosystem/topics/mindspeed-moe-overlap-memory
title: MindSpeed：MoE all-to-all 重叠、共享专家与 Zero Memory
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
- source: ascend-mindspeed
  path: mindspeed/core/transformer/moe/moe_feature/overlap/moe_layer_overlap_all2all.py
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: 5269dbf099be5a4cbfd4804511ca5108c1a23a8094b4696915f4330a94b9beb5
- source: ascend-mindspeed
  path: mindspeed/core/transformer/moe/moe_feature/overlap/grouped_mlp_with_comp_and_comm_overlap_all2all.py
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: a9b58be1b4c74c9c485fadb385ade818f23fbba464442f138bfb6d85a9dc4648
- source: ascend-mindspeed
  path: docs/en/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: 465129ba55e6466177a97aec18342cb47c0b90d4b9eefd9404b542419e7b64d4
- source: ascend-mindspeed
  path: docs/en/features/megatron_moe/megatron-moe-zero-memory.md
  commit: 241431d43e02a89556d2d2b3eacc7e24448adee5
  sha256: 1d4c360ee5c3a6df9dbf0ebff17eb2049a156f2b1faabc9a9958b7c2c84561b1
---

# MindSpeed：MoE all-to-all 重叠、共享专家与 Zero Memory

## 问题与收益来源

MoE dispatch/combine 在关键路径暴露等待，且专家 MLP 的激活占用限制 MB/并行切分时，通信重叠与 Zero Memory 是两个可联动的机制。前者重排异步通信与计算，后者用重算降低缓存激活；不能因都在 MoE 路径便算作同一个“无开销优化”。

## 参数验证就是接口契约

`MoEAlltoAllOverLapFeature` 的 `--moe-alltoall-overlap-comm` 要求 EP>1、dispatcher 为 alltoall/alltoall_seq 和 grouped GEMM，不能与 `use_ascend_mc2` 同开。alltoall 不接受 moe_tp_extend_ep；若有 shared expert 还可能自动开启共享专家 overlap。alltoall_seq 额外要求 permutation 异步通信，TP>1 要满足其扩展 EP 配置。各条件应按实际 feature 代码核查，而非只抄命令。

官方 Bridge 当前 EP overlap 的 shared-expert 约束不同，本底座的自动开启不能套到 Bridge。参数检查可能隐式改变共享专家字段，必须保存校验后的配置。

## 调用链与依赖

feature→MLP forward/init 和 TransformerLayer init 的 patch→MoELayer 替换为 AlltoAll/Seq adaptor→`moe_layer_overlap_all2all.py`→`grouped_mlp_with_comp_and_comm_overlap_all2all.py`。后者组织专家前反向、共享专家及通信依赖。继续追 dispatch counts、异步 collective 与 grouped GEMM，确认有效 token 和梯度都由同一布局解释。

Zero Memory 的 feature 另行校验 level0/level1、逐 PP rank 层数范围和是否启用 overlap/fb overlap；共享专家 forward 也有 patch。level 和 num_layers 组合不是任意可拼，fb overlap 的限制与普通 alltoall overlap不同。官方文档的内存百分比指可重算专家 MLP 中间状态范围，**不是整个训练峰值 HBM 的同等百分比**。

## 代价、数值与验收

减少暴露等待可能增加 buffer/活动微批，Zero Memory 又增加重复计算，两者需要联看 worst-rank HBM、dispatch/combine timeline、专家 token 偏斜与步时。记录 top-k、EP/TP、实际 dispatcher、shared expert、dtype 与输入规模，保持 effective batch 一致。

合法/非法配置分别测试；合法组合比输出、router/shared expert、dgrad/wgrad、重复 microbatch 与阶段 loss，非法组合应早期拒绝。通信按每个并行域代表 ranks 观测，单 rank 快不表示全局改善。源码可读不代表 NPU 实现已移到 HCU。

## 回退与持续复核

卡住先查是否某 rank 因参数/导入失败提前退出，再查 counts/句柄/collective 序列；内存升高区分通信 buffer 与激活。按完整机制恢复普通 dispatcher/缓存路径，保留基线。更新时联动[总览](../mindspeed.md)、[案例](../cases/mindspeed-ep-constraints.md)，以及实际 LLM 父仓锁定底座，不能只用独立 Core main 解释应用。

## 固定证据与复核范围

- [mindspeed/features_manager/moe/moe_alltoall_overlap.py](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/mindspeed/features_manager/moe/moe_alltoall_overlap.py)
- [mindspeed/features_manager/moe/moe_zero_memory.py](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/mindspeed/features_manager/moe/moe_zero_memory.py)
- [mindspeed/core/transformer/moe/moe_feature/overlap/moe_layer_overlap_all2all.py](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/mindspeed/core/transformer/moe/moe_feature/overlap/moe_layer_overlap_all2all.py)
- [mindspeed/core/transformer/moe/moe_feature/overlap/grouped_mlp_with_comp_and_comm_overlap_all2all.py](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/mindspeed/core/transformer/moe/moe_feature/overlap/grouped_mlp_with_comp_and_comm_overlap_all2all.py)
- [docs/en/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/megatron_moe/megatron-moe-alltoall-overlap-comm.md)
- [docs/en/features/megatron_moe/megatron-moe-zero-memory.md](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/en/features/megatron_moe/megatron-moe-zero-memory.md)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
