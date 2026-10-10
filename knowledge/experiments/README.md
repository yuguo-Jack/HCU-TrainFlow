---
id: experiments/index
title: TrainFlow 模型适配与性能实验记录
engine: cross-engine
stages: [adapt, optimize, fault-tolerance]
visibility: public
review_level: index
runtime_validated: false
---

# 模型实验与复用边界

本目录保存跨任务可检索的模型配置、优化依据、性能/显存/loss 观察、失败条件和精选原始证据。每项结论保留环境、源快照、比较方法与验证范围；完整 trace、数据集、checkpoint 和控制状态留在任务 workspace。

- [Kimi K3 / BW1000_H](kimi-k3-bw1000/README.md)：全参容量下界、缩减模型的微批 A/B/B/A 调参，以及 FP32→BF16 权重回拷的局部验证。阶段 loss、完整模型和自动容错未由该案例证明。

复用前联查 [站点配方](../sites/README.md) 和 [通用实践](../practices/README.md)，核对实际部署差异。`manifest.json` 中路径均相对案例目录，精选原件可直接从新 checkout 阅读，无需原任务缓存。
