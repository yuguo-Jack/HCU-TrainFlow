# HCU-TrainFlow 设计入口

设计已落实为可执行 v0.1.0。通用设计按主题维护，避免一份长文与实现脱节：

- [架构与边界](docs/architecture.md)
- [三个工作流](docs/workflows.md)
- [性能分析](docs/profiling.md)
- [远程执行](docs/remote-execution.md)
- [长训运行](docs/operations.md)
- [知识更新](docs/wiki.md)
- [能力范围与后续验收](docs/capabilities.md)

后续开发保持原需求的核心约束：本地主控、统一入口 + 三个阶段 Skill + 两个 Wiki Skill、优化不损害质量、阶段 loss、≥90% 端到端热点中的非通信建模、Flash-Train 优先复用、远端持续监测、单一容错负责人、公开数据隔离。具体环境验证按任务补齐，不用本地合成测试冒充真实训练。
