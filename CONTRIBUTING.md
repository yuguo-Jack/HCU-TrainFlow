# 贡献与公开发布

问题或 PR 请描述实际版本、最小复现、预期/实际行为及验证。本工程 Wiki 保存真实站点配置、配方和关键实测及精选原件，按 `docs/knowledge-architecture.md` 组织并随仓提交。完整任务日志、数据集与模型权重留在 workspace；凭据、私钥和 token 永不入仓。外部 Cookbook/其他目标仓 PR 按其发布要求处理，不套用到本站点知识。通用协议测试使用合成数据并标注范围。

代码检查：`python -m pytest -q`、`python scripts/validate_knowledge.py`。变更涉及跨进程/时间/版本时测试失败、中断和重放路径，不只测 happy path。

知识更新修改同仓所有受影响结论，保留固定来源/适用范围，原文抓取和作者推理分开。第三方代码依其许可证使用；本仓不因为链接某项目就获得其代码再许可权。

项目过程记录在 task_plan.md、findings.md、progress.md；docs 只放通用架构和使用说明。
