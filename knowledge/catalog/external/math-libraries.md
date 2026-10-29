---
id: tooling/hcu-math-library-tuning
title: HCU 数学库日志与调优入口
kind: external-reference
engine: tooling
stages:
- optimize
owner: external
search_skill: hcu-knowledge-search
runtime_validated: false
sources: []
---

# HCU 数学库日志与调优入口

HCU rocBLAS、hipBLASLt、MIOpen 的工程、教程、PR/MR 和版本能力由 **HCU-Knowledge** 维护，不在 TrainFlow 重建仓库 Wiki。用 `$hcu-knowledge-search` 按实际库、gfx、DTK、调用路径查询；必要时追到已加载版本的源码。

- rocBLAS：先读[持续更新的自动选优说明](https://kcnm6g5dkw5p.feishu.cn/docx/L6Z3dA3osolfS4xv63jc5qsqnhf)及其当前推荐工具，再查询 `auto_select_tools Auto_tuning.py tuning_args`、真实 bench、配置加载与目标 CU；核对工具当前副作用和候选覆盖。
- MIOpen：查询 `MIOpenDriver NHWC FIND_MODE FIND_ENFORCE`，分清实际消费者、用户选优记录与编译缓存；不套用 AMD 的模式编号或默认值。
- hipBLASLt：查询真实 bench/grouped 参数与版本支持；当前工作流只整理优化需求，不默认采用尚未验证可用的自行调优工具。

工作流方法集中在[数学库日志与调优交接](../../../skills/hcu-train-analyze-and-optimize/references/math-library-tuning.md)：触发条件、复现、rocBLAS 自行选优、MIOpen 布局/缓存实验、数值与整步验证。具体仓库归属见[底层联动](../../../skills/hcu-train-analyze-and-optimize/references/hcu-library-integration.md)。

维护时读取[外部用法关联](../external-knowledge.json)，复核受影响的 Skill、调优指南和调用契约。普通检索只留任务缓存，不自动更新 HCU 大库；本文是导航与维护入口，不表示所有工具已在当前硬件验证。
