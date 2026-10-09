---
name: hcu-engine-wiki-search
description: 检索官方训练引擎与生态优化机制，核对固定提交、上下游依赖和原始源码；按需联查 HCU 领域知识库。
---

# 训练引擎官方 Wiki 检索

## 检索步骤

1. 确定引擎、训练类型、实际源码/依赖版本和阶段；未知先保留，不自动假定 main。
2. 初次 `wiki-index <project>`，随后 `wiki-search <query> --engine <engine> --stage <stage>`。优先精确符号、flag、文件、机制词，再扩展同义词。搜索没有索引可重建本地索引，不因此全量刷新上游。
3. 阅读命中页面全文及固定源码，核对 review_level、runtime_validated、局部页面是否已改变。结果相关不等于结论适用于当前分支。
4. 跨主题问题按依赖连接：并行 schedule→通信/TE→显存→数值→恢复，或 RL→rollout→weight sync→训练。需要时拉当前实际底层分支到独立参考/开发目录。
5. 官方 Wiki 不含 HCU 私有材料；必要时调用 HCU knowledge search 和在线飞书检索补上下文，权限不足及时反馈。不要因为查询顺手更新大知识库。

底层库可用 `--engine transformer-engine` 或 `--engine cudnn-frontend` 定向搜索。TE 独立 Wiki 覆盖精度/权重缓存、attention、overlap/显存、融合与教程；cuDNN Frontend 覆盖 graph/plan、SDPA、open kernels、host 缓存与教程。跨 TE→cuDNN→HCU TE/Flash-Train 的问题分别检索并核对调用条件，不能把官方 NV 示例命令直接当成 HCU 配方。

本机缺 HCU knowledge search 时按项目 docs/integrations.md 复用已有知识库或启用可选 thirdparty/HCU-Knowledge；需要仓库权限就提示用户。不可因未获权而把“未检索”写成“没有相关知识”。

## 回答要求

给结论、适用条件、固定来源、实现位置、反例/约束与待验证项。找不到源码或本页只是入口导航时明确说明。遇到版本漂移可建议/执行本项目官方 Wiki 更新（符合当前任务范围），运行中任务的源锁保持不变。

## 运行约定

先定位 HCU-TrainFlow checkout（用户给定路径或 `TRAINFLOW_PROJECT`）和私有 `TRAINFLOW_WORKSPACE`。不要把 site、数据、模型、日志或凭据写进公共仓。CLI 用 `hcu-trainflow --workspace <private-path>`；源码环境可用 `python -m hcu_trainflow`。先读项目 `docs/quickstart.md` 和当前任务上下文，再按需读相关章节。

主 Agent 在本地主控，专家分工记录 owner、scope、允许修改路径、预算与验收证据。运行代码使用独立开发 checkout 和不可变源快照；远端只执行明确命令/守护，不要求部署模型 Agent。TaskSpec 的 execute/sync/notify 权限是任务约定，不是 OS 安全沙箱。实际节点、容器、Pod UID、Slurm allocation 由部署任务确认。

需要 HCU 事实、历史案例或底层实现时使用可用的 `$hcu-knowledge-search`；也可以读当前对应分支源码和公开官方文档。知识检索不自动更新 HCU 大知识库。本工作流只维护自己的局部官方 Wiki；具体依赖命令升级时同步复核 Skill/适配器，不能仅改 Wiki。

产物归属本 Skill：按目标仓规范准备集中、通用的改动、测试、PR 说明和回退方式。公开 PR/Cookbook 只含脱敏的可公开方法与必要代码，不上传任务数据。遵循当前会话已给出的提交/发布授权。
