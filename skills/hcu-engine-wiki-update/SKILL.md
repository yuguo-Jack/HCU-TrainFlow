---
name: hcu-engine-wiki-update
description: 更新局部官方训练 Wiki、PR review 与依赖锁，并复核受影响的 Skill、命令和解析器，保持可追溯知识与用法。
---

# 训练引擎 Wiki 与工作流维护

维护本工程官方 Wiki 和随源变化的工作流用法。它可以由训练任务按需主动调用；不替代或触发 HCU 大知识库 update。

## 更新协议

1. 检查公共 GitHub/文档权限、限流与实际访问，不把 404 当成已删除。读取 knowledge/sources.json 与已有 observed/reviewed 游标。
2. `wiki-refresh <project> <source-id>` 收集注册路径的最新内容和固定提交。新增主题需把关键源码/测试/配置路径登记进去；不能只抓 README 宣称全仓无变化。检查树/分支和相关 release/roadmap/PR。
3. 需要 PR 依据时 `wiki-pr owner/repo number`，采集正文、普通评论、行内评论、独立 review 顶层正文及文件分页。API diff 缺失或超限时补 base/head 源码。记录未完成分页/权限缺口，不能继续标记全部完成。
4. 比较实际 active ref 与已锁版本，处理 submodule gitlink，不用子仓 HEAD 偷换。发布计划、open PR、merged main、released 和运行可用分开。
5. 对每个 affected overview/topic/case 深读新实现、改原因、触发条件、测试、限制和回退，同仓交叉结论一起修正。必要时扩充关联的第三方优化采用/退役记录。
6. 按 knowledge/maintenance.json 同时检查 Skill、环境命令、TraceLens 接口、日志字段、profile 参数和容错步骤。HCU 命令可以依托大知识库当前内容或自主看最新工程源码；不能只更新官方 Wiki 文本。
7. 修改后逐页/逐工作流写 decisions：decision、note、当前 page_sha256、新 source_commit。`wiki-review` 全部通过后记录 receipt，再 `wiki-index`。采集完成不是内容复核完成，更不是硬件实测通过。
8. 运行本工程测试和真实问题检索，保存本次缺口及下次入口。公共材料提交与 push 沿用任务授权，私有数据禁止进入公共仓。原始缓存可重建，但源码版本锁、作者结论和公开证据链接必须保留。

## 组织标准

按工程定位→目录→编译安装→运行/测试→调用链→优化机制→问题诊断→版本/依赖→证据组织。案例按问题/瓶颈→为什么改→实现符号→适用条件→正确性/性能证据→失败条件/回退。尚未逐模型覆盖的入口页保持 coverage 标记，不以页数代替深度。

## 运行约定

先定位 HCU-TrainFlow checkout（用户给定路径或 `TRAINFLOW_PROJECT`）和私有 `TRAINFLOW_WORKSPACE`。不要把 site、数据、模型、日志或凭据写进公共仓。CLI 用 `hcu-trainflow --workspace <private-path>`；源码环境可用 `python -m hcu_trainflow`。先读项目 `docs/quickstart.md` 和当前任务上下文，再按需读相关章节。

主 Agent 在本地主控，专家分工记录 owner、scope、允许修改路径、预算与验收证据。运行代码使用独立开发 checkout 和不可变源快照；远端只执行明确命令/守护，不要求部署模型 Agent。TaskSpec 的 execute/sync/notify 权限是任务约定，不是 OS 安全沙箱。实际节点、容器、Pod UID、Slurm allocation 由部署任务确认。

需要 HCU 事实、历史案例或底层实现时使用可用的 `$hcu-knowledge-search`；也可以读当前对应分支源码和公开官方文档。知识检索不自动更新 HCU 大知识库。本工作流只维护自己的局部官方 Wiki；具体依赖命令升级时同步复核 Skill/适配器，不能仅改 Wiki。

产物归属本 Skill：按目标仓规范准备集中、通用的改动、测试、PR 说明和回退方式。公开 PR/Cookbook 只含脱敏的可公开方法与必要代码，不上传任务数据。遵循当前会话已给出的提交/发布授权。
