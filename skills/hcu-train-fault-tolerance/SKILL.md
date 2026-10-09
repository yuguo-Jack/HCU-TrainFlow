---
name: hcu-train-fault-tolerance
description: 扩容 HCU 训练并衔接现有容错，持续观测进展、诊断卡住或崩溃及内存问题；支持仅故障诊断。
---

# HCU 训练扩容与故障诊断

支持 `diagnose` 只做诊断或 `operate/full` 扩容与长训。故障处置权限、通知渠道、资源范围在部署具体任务时确定。

## 扩容和接管

1. 完整模型最小 DP 域验证、阶段质量及显存余量就绪后，按实际启动方式用 Cluster Manager 为主、适用时 Primus 相关工具补充筛机。维护健康节点池与更新时间，坏节点修复需重新验收。
2. 记录唯一恢复负责人、job/attempt、节点/设备映射、源快照、checkpoint 和数据游标。容错工具负责既有隔离/重启；Agent 收集证据、定位、准备修复，新增代码/参数的上线按本任务授权。
3. 远端独立运行 watcher/日志归一化器。监测 step/token 进展、loss/grad、吞吐、显存、checkpoint、进程和恢复阶段；进程活着不等于训练正常，重新启动不等于恢复成功。
4. 将事件写入持久化 outbox。飞书通知可复用现有容错渠道；Agent 唤醒使用部署时明确配置的运行时桥接，不能把 webhook 送达或 inbox 文件出现叫作 Agent 已接手。领取、处理和完成分别回执。
5. 本机休眠不停止远端监测和既有容错。恢复后按 sequence 重放并去重，先核对当前 attempt/checkpoint/控制权，再采取动作。另部署独立 heartbeat observer，防止 watcher 自己挂掉无人发现。

## 故障诊断步骤

- **进程卡住：** 保存全 rank 日志/时间、Python/native stack、调度及 collective 序列；识别最先偏离者、缺席 rank、数据/保存等待。先收现场，再最小重现。不要看到大家都在通信就断定通信库 bug。
- **core dump/设备错误：** 保存运行二进制和源码/build ID、core、第一错误、输入 shape、精度、异步边界。使用匹配调试器/符号，隔离最小触发；同步调试改变性能，不用其时间做优化结论。
- **内存/显存增长：** 分 allocated/reserved、主存/pinned、KV/激活/优化器/通信/图池，观察跨 step 斜率及引用生命周期；区分缓存稳定平台与持续泄漏。检查 checkpoint、offload、异步队列和异常路径清理。
- **性能持续下降：** 比较时钟/温度/健康、相同 shape 孤立测试、数据、通信和新版本；`GPU_MAX_HW_QUEUES` 与 overlap 只在受控实验中调整。
- **恢复反复失败：** 校验 checkpoint 完整性、数据游标、版本和恢复 deadline；重启后连续进展与数值才是恢复证据。不要同时启动第二个恢复控制器。

## 输出

诊断报告包含症状时间线、最强证据、已排除项、可复现步骤、下一验证和责任边界。长训报告附曲线、incident、恢复耗时和未解决告警。现场原始信息保存在私有工作区；修复按对应容错/训练仓标准提交，并记录可回退方案。

## 与统一主控衔接

由 `$hcu-trainflow` 调用时，沿用当前任务、目标和私有工作区；本阶段负责实际领域工作，主控负责 `flow-next`、独立复核和推进。交付候选源/配置清单、原始证据和绑定 candidate_snapshot 的报告；不要另起无关联任务，也不要绕开复核直接推进状态。出现新的指导先读取 GUIDANCE.md 并回应；明确记录收益、数值/显存代价、未完成项和需要专家判断的问题。完整契约见项目 `docs/collaboration.md`。本 Skill 仍可按用户指定独立使用，不强制开展全流程。

## 运行约定

先定位 HCU-TrainFlow checkout（用户给定路径或 `TRAINFLOW_PROJECT`）和私有 `TRAINFLOW_WORKSPACE`。不要把 site、数据、模型、日志或凭据写进公共仓。CLI 用 `hcu-trainflow --workspace <private-path>`；源码环境可用 `python -m hcu_trainflow`。先读项目 `docs/quickstart.md` 和当前任务上下文，再按需读相关章节。

主 Agent 在本地主控，专家分工记录 owner、scope、允许修改路径、预算与验收证据。运行代码使用独立开发 checkout 和不可变源快照；远端只执行明确命令/守护，不要求部署模型 Agent。TaskSpec 的 execute/sync/notify 权限是任务约定，不是 OS 安全沙箱。实际节点、容器、Pod UID、Slurm allocation 由部署任务确认。

需要 HCU 事实、历史案例或底层实现时使用可用的 `$hcu-knowledge-search`；也可以读当前对应分支源码和公开官方文档。知识检索不自动更新 HCU 大知识库。本工作流只维护自己的局部官方 Wiki；具体依赖命令升级时同步复核 Skill/适配器，不能仅改 Wiki。

产物归属本 Skill：按目标仓规范准备集中、通用的改动、测试、PR 说明和回退方式。公开 PR/Cookbook 只含脱敏的可公开方法与必要代码，不上传任务数据。遵循当前会话已给出的提交/发布授权。
