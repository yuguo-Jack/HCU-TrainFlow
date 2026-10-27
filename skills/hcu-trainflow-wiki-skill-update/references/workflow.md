# 工作目录与阅读入口

安装本 Skill 会复制其 references，共享 docs/Wiki 从工程读取。按入口约定采用用户明确的工程路径、`TRAINFLOW_PROJECT` 或安装目录 `workspace.json.project_root`；按项目 `docs/skill-reading-map.md` 的当前模式进入。`TRAINFLOW_WORKSPACE` 另指向任务私有目录。

按需阅读项目：

- `docs/quickstart.md`：安装、任务、证据及 CLI。
- `docs/workflows.md`：三个工作流与验证门槛。
- `docs/profiling.md`：时间分母、热点建模和 TraceLens。
- `docs/operations.md`：远程 watcher、事件重放与恢复边界。
- `docs/wiki.md`：固定来源、更新复核和工作流维护。
- `docs/knowledge-architecture.md` 的“任务中的维护时机”和“自动更新时的内容筛选”：入库价值、正文/过程归属、文档排除与旧页清理；新增和修订页面时必读。
- `knowledge/README.md`：HCU-TrainFlow-Wiki 总入口，含官方资料、通用环境经验和模型最终总结。
- `docs/wiki-authoring-standard.md` 与 `knowledge/COVERAGE.md`：全部来源共用的内容维度、专题和边界；新增或重构来源时同步 `coverage.json` 并运行 `scripts/check_wiki_coverage.py`。
- `docs/practices/engine-delivery-tracks.md`：稳定插件/快速适配路线、模型 example 与补丁重放、Cookbook 指路及稳定承接后的退役；相关版本更新时复核。
- `docs/optimization-reference-map.md`：跨引擎参考与 HCU 修改归属，发现调用/版本变化时一起复核。
- `knowledge/catalog/external-knowledge.json`：HCU 仓通过大库查证，TraceLens fork 通过实际依赖与集成契约查证；复核关联 targets，不另采集本地 HCU 项目 Wiki。官方来源由 sources.json 的 knowledge_project 归属统一项目目录；原始 JSON 证据保留固定哈希。

更新时先区分部署锁定版本、官方发布线与活跃开发线；默认分支不保证包含之前已引用的功能。分支切换或来源回退时检查提交关系、版本和关键文件差异，记录选线依据，不把已发布线的旧实现覆盖成“最新能力”。采集源码/原文与作者页内容复核分开，未精读 PR 可搜索但不能标成已形成可靠案例。

不要从安装目录的父级猜仓库位置；先核对上述工程绑定。执行前检查 `hcu-trainflow --help` 和相关子命令帮助，不猜不存在的 flag。
