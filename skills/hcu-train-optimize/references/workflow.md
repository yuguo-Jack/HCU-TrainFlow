# 工作目录与阅读入口

安装本 Skill 不会复制整个 Wiki。设置 `TRAINFLOW_PROJECT` 指向已 clone 的 HCU-TrainFlow；`TRAINFLOW_WORKSPACE` 指向任务私有目录。

按需阅读项目：

- `docs/collaboration.md`：统一入口、候选复核、人的文件指导与断点接续。
- `docs/quickstart.md`：安装、任务、证据及 CLI。
- `docs/workflows.md`：三个工作流与验证门槛。
- `docs/profiling.md`：时间分母、热点建模和 TraceLens。
- `docs/operations.md`：远程 watcher、事件重放与恢复边界。
- `docs/wiki.md`：固定来源、更新复核和工作流维护。
- `knowledge/README.md`：官方引擎与生态章节。

不要读取安装目录相对路径猜测仓库位置；先使用明确项目路径。执行前检查 `hcu-trainflow --help` 和相关子命令帮助，不猜不存在的 flag。
