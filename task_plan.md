# 当前任务：lite 后续维护全面复核（2026-11-05）

用户要求重新全面 review，并确认后续按 lite 方式更新 lite、本地 checkout 也在 lite。此轮只修正重构与长期维护契约，不全量刷新资料、不变更训练环境。

- 阶段一 HCU-Knowledge 已独立完成：lite fb5d29e10b5a864d1349b10e472dab0fe5b16c31 / 0.6.2；GitHub/GitLab 两端一致，本地 321 项测试、四项远端 CI 通过。此后该仓、索引、安装和远端只读。
- 阶段二 TrainFlow 从干净 lite a41cc005080b0803e78b11c6acdc5a5349e9ad70 / 0.8.0 开始；既有重构已发布且七项 CI 通过。当前修正应用后无变化更新、删除路径证明、查询缓存、条件 catalog、弱命中联搜及目标分支 guard；保留原件、历史和检索入口。
- 长期规则：共享知识维护使用配置中的 lite，原始来源自己的 ref 独立选择；普通 PR 只发现 URL，正文、代码、必要讨论按需读取，不逐仓报告、不要求评论镜像。明确请求的后续更新应实际刷新选定来源，旧未刷新状态仅描述带日期的重构快照。
- 本地复核完成：Skill/docs 契约 78 项通过，完整软件测试 1427 passed / 4 平台条件 skipped，最后增量/原件/分支/联搜/登记漂移边界 151 项通过；1458 页、24 来源的知识组织、覆盖、文档、阅读资源检查通过。既有包 0.8.1、六项 Skill 已同步，全部 11 项必需 Skill 及三个受管依赖只读检查 current/ready。
- 发布验收规则：本轮单独提交 origin lite，核对实际 CI 和远端 refs；不动 main/旧标签，不自动打新 tag。提交 SHA、最终 CI 结果、清洁状态与两仓本地分支的权威回执记在 .work/lite-review-20261105/publication.json，不能用本计划代替实际发布证据。

写入范围：本 TrainFlow checkout 与本轮 .work/lite-review-20261105；按既有授权同步六项已安装 Skill 和系统 Python 已有包元数据。不装新依赖，不操作训练/GPU，不触碰其他任务 Store。已有原始重构验收和退役凭证在 .work/lite-refactor-20261105 保留。

本仓 AGENTS 要求有用独立工作划分 scope：lite_acquisition 负责来源增量运行时和隔离回归；lite_skills_install_ci 负责六项 Skill/docs/依赖锁；lite_coverage_docs 提供独立边界审查；主控负责检索联搜、CLI guard、验证器/CI、集成与发布。

此前旧备份、测试目录及冷验证副本残余清理被自动审批 blocked by policy 拒绝，保持原状，不重试或换工具绕过。本轮不进行清理。
