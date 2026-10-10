---
id: sites/index
title: 跨任务站点环境、配方与实测知识
engine: cross-engine
kind: site-knowledge
stages: [adapt, optimize, fault-tolerance]
visibility: public
review_level: navigation
runtime_validated: false
---

# 站点知识

这些页面、配置和必要原件随 TrainFlow 提交，供不同模型任务复用；完整任务档案保留在各 workspace。检索命中表示有历史证据，仍须检查当前软硬件、配方和测量条件。

| 站点 | 已保留范围 | 尚未完成 |
| --- | --- | --- |
| [CFS / BW1000_H / gfx936 / RoCE](cfs-roce-bw1000/README.md) | SSH+Docker、DTK26.10、两节点16卡 RCCL all-to-all 配方与三轮实测，原始 rank/链路证据 | run_nhc 未安装；历史带宽比较仍有差异；完整训练/生产容错验证不能从这份通信测试推导 |

更新标准见 [知识架构](../../docs/knowledge-architecture.md)。失效记录仍可检索，新测量保留版本和差异，不将重新阅读时间当作测量时间。
