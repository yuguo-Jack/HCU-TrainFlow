# 配置模板与合成示例

本目录用于了解 TrainFlow 的输入格式、试跑分析接口和准备任务配置。这里的 trace、shape、算力和阈值均为演示输入；它们不代表某台 HCU 的实测性能、模型优化结果或已验收的生产配置。

## 文件分类

| 类别 | 文件 | 用途与使用前需要修改的内容 |
| --- | --- | --- |
| 任务模板 | [task.json](task.json) | 分析任务的目标、上下文、权限和预算；复制后填入真实任务身份与证据，权限按已授权范围设置 |
| 执行模板 | [ssh-docker-card.json](ssh-docker-card.json) | SSH + Docker 命令卡；替换站点别名、容器、工作目录和命令，并核对实际映射及 CLI |
| 监测模板 | [monitor-policy.json](monitor-policy.json)、[trainflow-watch.service](trainflow-watch.service) | 停滞、遥测、恢复与性能阈值，以及 systemd watcher 模板；按训练节奏和站点规则调整，替换服务里的占位符后再部署 |
| 更新复核模板 | [review-decisions.json](review-decisions.json) | Wiki 页面与工作流复核结论的空结构；填写真实复核结果，空对象不代表已完成复核 |
| 合成并行上下文 | [groups.json](groups.json)、[process-groups.json](process-groups.json) | 两个 rank 的 DP 示例；前者还含可用 rank，分别供采样计划与分析使用。真实任务需提供实际进程组 |
| 合成性能输入 | [trace.json](trace.json)、[window.json](window.json)、[models.json](models.json) | 简化 GEMM 时间线、分析窗口与性能上限模型；模型中的峰值明确为测试值，不能作为 HCU 硬件参数 |
| 合成 TraceLens 输入 | [tracelens-trace.json](tracelens-trace.json) | 演示 CPU op、HIP launch 与 GPU kernel 的关联字段；生成报告只说明接口能处理这份输入 |

## 怎么使用

- 配置模板先复制到当前任务的私有工作空间，再按真实环境填写；不要将实际节点、凭据、日志和结果回填进本目录。
- 合成输入可按[性能分析示例](../docs/profiling.md#输入契约)和[TraceLens 安装验证](../docs/integrations.md)试跑；输出写入任务目录，不能把演示报告当成真实优化证据。
- 真实采集需重新确认模型/软件身份、并行组、shape、计时窗口及硬件参数；模板阈值也需要现场校准。
- systemd 示例仅提供 watcher 进程托管形式，现场告警、恢复负责人和 Agent 唤醒需按[运行与守护](../docs/operations.md)单独接入验收。

## 真实操作记录放哪里

| 内容 | 位置 |
| --- | --- |
| 某次任务的启动配置、命令、完整日志、trace、实验候选及故障过程 | 该任务的私有工作空间、Store 和看板 |
| 跨任务可复用的环境经验及必要证据 | 筛选后进入 [knowledge/sites/](../knowledge/sites/) |
| 模型最终优化里程碑、精度与性能总结及关键数据 | 筛选后进入 [knowledge/experiments/](../knowledge/experiments/) |
| 可迁移的工作方法和决策步骤 | `docs/` 与对应 Skill 的参考文档 |

经验提炼遵守[知识收录规则](../docs/knowledge-architecture.md)和[训练经验记录](../docs/experience-knowledge.md)。实际任务记录与本目录的合成输入分别保留，不能用模板值填补缺失的实测数据。日常使用可直接从 `$hcu-trainflow` 入口描述任务，无需手工填写全部示例；CLI 接入见[快速开始](../docs/quickstart.md)。
