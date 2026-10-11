# 工作目录与阅读入口

安装本 Skill 会复制其 references，共享 docs/Wiki 从工程读取。按入口约定采用用户明确的工程路径、`TRAINFLOW_PROJECT` 或安装目录 `workspace.json.project_root`；按项目 `docs/skill-reading-map.md` 的当前模式进入。`TRAINFLOW_WORKSPACE` 另指向任务私有目录。

按需阅读项目：

- `docs/quickstart.md`：安装、任务、证据及 CLI。
- `docs/workflows.md`：三个工作流与验证门槛。
- `docs/profiling.md`：时间分母、热点建模和 TraceLens。
- `docs/operations.md`：远程 watcher、事件重放与恢复边界。
- `docs/wiki.md`：固定来源、更新复核和工作流维护。
- `knowledge/README.md`：HCU-TrainFlow-Wiki 总入口，含官方资料、通用环境经验和模型最终总结。

不要从安装目录的父级猜仓库位置；先核对上述工程绑定。执行前检查 `hcu-trainflow --help` 和相关子命令帮助，不猜不存在的 flag。
