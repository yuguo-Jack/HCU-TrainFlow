---
id: ecosystem/topics/loongforge-dp-balance
title: LoongForge：变长/视觉 DP 代价模型与跨 rank 样本均衡
engine: loongforge
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
- source: baidu-baige-loongforge
  path: docs/source/features/data_parallel_balancing.md
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: f58d64fbdfd9cb61d3bf2577d93928741be9f7f3532a36880bc89e525311b1d4
- source: baidu-baige-loongforge
  path: docs/source/features/vit_data_parallel_balancing.md
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: a7410b438bace81bba34381a2874cc19d8b091cfe9c36cb45e6bbad08f6d7532
- source: baidu-baige-loongforge
  path: loongforge/data/dp_balance/train_hooks.py
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: 98ae698ebf87dd8c3412983397b6a74ed9718c71eb038fed50f43c5dcab4ab75
- source: baidu-baige-loongforge
  path: loongforge/data/dp_balance/patches.py
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: 00cc59f327d372708595e7cfd11ef5137831ce1f88a53d4bb7f421d30216e1ec
- source: baidu-baige-loongforge
  path: loongforge/data/dp_balance/rerun_iterator.py
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: 59fff9f78b06df2dd88251e34012357b5a8c9dd035ddf8a15f30816439eb92f9
- source: baidu-baige-loongforge
  path: loongforge/data/dp_balance/rebalance/balance.py
  commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
  sha256: 84fcb5795b89a66e655b05c7728c106c864c2d0485599c5d95a29e75d20df24c
---

# LoongForge：变长/视觉 DP 代价模型与跨 rank 样本均衡

## 为什么等token数仍可能慢

packing后总token相同，若sequence分布不同，attention成本仍近似取决于各段长度平方和；视觉序列/帧数又增加差异。DP一步要等最慢rank。此机制面向真实样本不均，不应拿mock force-balanced的数据收益当真实训练吞吐。

## 配置和调用链

官方入口是`use-vlm-dp-balance`、`use-vit-dp-balance`等特性。`train_hooks.py`包装train_step，借`RerunDataIterator`安全预看microbatch，收集长度/样本统计并在warmup后拟合/广播代价；`patches.py`替换iterator和pin-memory排队/重排，`rebalance/balance.py`执行分配。代码使用实际DP的Gloo group，不将包含TP/CP的全world随意当DP组。

warmup计时避开首轮冷启动，模型为`a×sum(L_i²)+b×sum(L_i)+c×样本数`，是训练实测的负载拟合，**不是GPU roofline上限**。当前默认观测窗口等配置应按目标源码/CLI确认，输入或kernel/backend变化会让旧系数失效。

## 实际算法、状态与通信成本

算法depack样本，按估计cost排序分配，再move/swap修正；设置长度上限、停止容差，负载差异小或单个任务已经主导时跳过无意义重排。`MicroBatchLoadTracker`记录当前iteration累积cost，避免每个microbatch单独平衡却整步仍偏斜。

数据tensor仍通过`all_to_all_single`重分发，tokens/labels/visual/loss weights必须同步移动。“主要在CPU规划”不等于没有GPU通信或数据复制。DP小、计算短、网络慢时重排成本可能大于等待节省；CPU预取、host memory与采样开销同样需要观测。

## 数值、恢复和性能验收

比较每步样本ID多重集合、有效token、loss mask/权重、位置、多模态tensor对应与梯度；样本顺序变化可能改变随机augmentation和浮点归约，应检验阶段loss及保存恢复后的顺序/状态。分配容量和大样本不能静默丢弃。

性能记录各DP rank的预测/真实step、拟合误差、重排通信/CPU成本和worst-rank wall clock。先固定普通sampler基线，再选择DP不均明显的输入开启；不是默认所有模型打开。

## 排障、回退和更新

如果负载预测好但步时不降，查其他并行域瓶颈/网络/CPU与重排本身；loss偏差先核对样本/mask对应和分母。关闭均衡恢复普通sampler，保留一致的训练目标。更新hooks、queue、balance与模型/data consumer同时复核[总览](../loongforge.md)，不只调一个容差。

## 固定证据与复核范围

- [docs/source/features/data_parallel_balancing.md](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source/features/data_parallel_balancing.md)
- [docs/source/features/vit_data_parallel_balancing.md](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source/features/vit_data_parallel_balancing.md)
- [loongforge/data/dp_balance/train_hooks.py](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/loongforge/data/dp_balance/train_hooks.py)
- [loongforge/data/dp_balance/patches.py](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/loongforge/data/dp_balance/patches.py)
- [loongforge/data/dp_balance/rerun_iterator.py](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/loongforge/data/dp_balance/rerun_iterator.py)
- [loongforge/data/dp_balance/rebalance/balance.py](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/loongforge/data/dp_balance/rebalance/balance.py)

本页说明已阅读的官方源码、文档和机制。没有在 HCU 上执行这些上游测试；上游性能、发布状态与当前部署是否具备该能力应分别确认。更新时同时复核工程总览、相应专题、案例、调用方与依赖版本。
