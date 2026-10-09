---
id: official-megatron-wiki/profiling
title: 训练 profiler 采样与 TraceLens 联动
engine: megatron
stages:
- prepare
- optimize
- operate
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: nvidia-megatron-lm
  path: megatron/training/training.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: 9df18e0c6002c0ee7c2f595d32e0bcb04dd4363e35fc0c9b8da206e8a2c1dfe8
- source: nvidia-megatron-lm
  path: megatron/training/arguments.py
  commit: a07014bbd47988608a05df23639c03441570e37b
  sha256: a6a17536d6cd4c66f956651b519d5e96b84c088133543f99ae90798a49b8899f
- source: hcu-tracelens
  path: setup.py
  commit: e4e891de60d3ac3cff3046a58e5852d0814b3dc6
  sha256: 29d8f29499f4a8f4a5fc2c0aa6407d6f400a7c5bfdfb3ba2be274aff493fc253
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/utils/deterministic_fallback.py
  commit: e4e891de60d3ac3cff3046a58e5852d0814b3dc6
  sha256: 8fa877065e24b81512ee67f8d57d5424a95ddcfc0851a501828713e44c536935
- source: hcu-tracelens
  path: docs/hcu-integration.md
  commit: e4e891de60d3ac3cff3046a58e5852d0814b3dc6
  sha256: c9ad787d82130aa710e1fd009bbae950739a087ceea796257abfdda4bc5a40a5
---

# 训练 profiler 采样与 TraceLens 联动

## 抓取窗口

在训练循环里核对本版本 `cfg.profiling`、`profile_step_start/end`、`profile_ranks`、PyTorch profiler 的启停。不要将历史版本启动 flag 直接套到新版配置。窗口选 warmup 后完整训练步，明确是否包含 optimizer、数据等待、checkpoint 或 evaluation。

保留每 rank 独立 trace 与 metadata：运行快照、step 区间、实际 groups、时钟域、shape/dtype/stride、phase 与 profiler 设置。shape/stack/memory 采集增加开销，只对所需窗口开启；吞吐比较另跑 profiler-off。

## 分析顺序

1. 空泡先分 CPU launch、数据读取、同步、PP 等待和内存分配；看到空白不能直接下 CPU 瓶颈结论。
2. 看同域 rank 的偏斜、collective 顺序、消息大小和等待。
3. 看融合粒度与 NV 参考真实调用链，再看 shape 对应 kernel。
4. 对累计覆盖端到端墙钟时间至少 90% 的热点集合逐个评估非通信计算项。

TrainFlow 的区间扫描将同 rank 重叠区间等份归因，作为可检查的排序代理；不是分布式关键路径证明。未归因/CPU/等待留在分母，覆盖不足显示 incomplete，不能偷偷换成 kernel 总时间。使用 TraceLens 的算子关联/collective/overlap 报告补足细节，跨 rank 对齐另保留校时依据。

## TraceLens HCU fork 与完整功能复用

TrainFlow 当前锁定 `yuguo-Jack/TraceLens` 的 `hcu` 分支提交，AMD 上游作为独立来源持续监测。fork 完整保留报告、通信分析、TraceDiff、PerfModel、EventReplay、trace 索引与 kernel 源码定位；当前最小补丁修复了 Windows CSV 字段上限导致的原生 CLI 导入失败。

训练分析优先使用已有模块：比较候选前后性能用 TraceDiff，graph attribution 用原生 graph 报告，跨任务查 shape/kernel 用 trace 索引，定位实现用源码解析器。同一任务原始 trace 与结果保存在私有 workspace。CLI 能启动不代表 HCU 事件已完整识别；回放、JAX/XPlane、Origami 模型等功能按对应依赖单独验证。

硬件峰值通过现有架构 JSON/扩展接口输入，算子规则沿已有映射和模型扩展；无法表达真实 HCU 格式时才修改核心解析，并提供最小复现与回归。不得为了让报告完成而套用其他硬件峰值、忽略未关联 kernel 或改变端到端分母。安装、迁移与功能入口见 [集成说明](../../docs/integrations.md)。

## 固定源码与更新范围

- [megatron/training/training.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/training/training.py)
- [megatron/training/arguments.py](https://github.com/NVIDIA/Megatron-LM/blob/a07014bbd47988608a05df23639c03441570e37b/megatron/training/arguments.py)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。

- [HCU TraceLens fork：能力、补丁与维护](https://github.com/yuguo-Jack/TraceLens/blob/e4e891de60d3ac3cff3046a58e5852d0814b3dc6/docs/hcu-integration.md)
