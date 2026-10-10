---
id: practices/index
title: TrainFlow 可复用工程实践
engine: cross-engine
stages: [adapt, optimize, fault-tolerance]
visibility: public
review_level: engineering-methodology
runtime_validated: false
---

# 可复用工程实践

这里保存从适配、优化和运行过程中提炼的通用方法，随 TrainFlow 工程提交。方法是否适用由当前源码和现场条件决定；实际站点配置与测量在同仓 `sites/` 保存，完整任务档案留在 workspace。

- [通信现场配方、RoCE 与 RCCL 差距排查](communication-recipe.md)：发现完整启动链、核对变量/库与实际路径、复现实测、区分多变量收益与单变量因果。
- [执行基线、候选验证与主仓交付顺序](execution-baseline.md)：保持实验连续性、复用已有资格、差异回归。

实际站点入口见 [站点知识](../sites/README.md)，归属与维护规则见 [知识架构](../../docs/knowledge-architecture.md)。现有 `wiki-search` 搜索整个工程 Wiki；本任务原始经验另用 `experience-search`。没有现场记录时保持缺口，不从模板捏造配置或数值。
