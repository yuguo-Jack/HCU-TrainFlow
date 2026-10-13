# HCU-TrainFlow 架构与设计导航

本页是设计文档的导航，不是工作流启动入口。安装和使用见 [README](README.md)，安装后通过 `$hcu-trainflow` 启动；首次了解工程可先读 [工程介绍](docs/project-overview.md)。当前版本以 README 和 [变更记录](CHANGELOG.md)为准。

架构、方法和执行规则按主题维护：

- [架构与边界](docs/architecture.md)
- [接手与阶段交接](docs/agent-playbook.md)
- [三个阶段工作流](docs/workflows.md)与[详细流程图](docs/workflow-map.md)
- [性能采集](docs/profiling.md)与 [TraceLens 分析](docs/tracelens-analysis.md)
- [模型精度诊断](docs/practices/model-accuracy-diagnosis.md)
- [远程执行](docs/remote-execution.md)
- [工作空间与写入边界](docs/workspace-boundaries.md)
- [规模扩展与长训运行](docs/operations.md)
- [Wiki 组织与更新](docs/wiki.md)
- [代码交付与 PR](docs/change-delivery.md)
- [能力范围与后续验收](docs/capabilities.md)

执行规则以对应 Skill 和上述专题文档为准。统一入口协调三个阶段 Skill 与两个 Wiki Skill，支持完整流程和独立阶段任务；按实际瓶颈推进，优先复用现有 HCU 算子库和通信库能力，通过局部回归、整步收益和阶段 loss 验证候选。已验证能力与待验证范围分别记录，不以本地测试代替真实训练验收。
