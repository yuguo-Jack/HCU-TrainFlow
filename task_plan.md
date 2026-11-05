# 当前任务：lite 分支重构（2026-11-05）

这是重构，不进行全量资料更新。用户最新要求：普通 GitHub/GitLab PR 只需联搜找到入口，原页、代码及必要讨论按需读取；不建立全评论/review镜像，不逐仓全量总结或按数量填表。

阶段一已独立完成：HCU-Knowledge lite c59fba6f5f58109aef2b9e1ca060734cf11138d0 / 0.6.1，GitHub/GitLab refs一致，四项CI成功。此后大库只读，不修改源材料、索引、安装或远端。

本阶段起点：TrainFlow lite 0f2e883b101fc1cebf627d9203b03068827a6a5a / 0.7.4，初始干净。只推 origin lite，不修改 main/旧tag，不自动打新tag。授权写入本checkout、本轮 .work/lite-refactor-20261105、既有六项Skill及既有系统Python包元数据；不装新依赖、不操作训练/GPU，不触碰其他任务Store。

- T01–T03 complete：轻量来源/路由与发现优先；取消九维/案例配额和全讨论补采。固定来源/版本/父锁/实际消费者保留，无全量资料刷新。
- T04 complete：净退役54,666份当前普通PR副本、4,318,805,195字节；保留53组当前引用PR+原件。现知识约68MB/1458页；共享索引28.9MB，首次约3.69s，无变化约0.59s、零重新解析。旧Git/64位generation可读，旧任务Store不清理。
- T05 complete：六项Skill/既有包0.8.0已同步，实际只读核验11项必需Skill及全部受管依赖current/ready；KB保持只读且精确锁c59fba6。CI分类资料/软件，浅检出，scope使用blob:none避免下载旧大正文。19/17003历史边界未改称已验证。
- T06 in_progress：整体独审无阻断，当前/无历史冷副本各20题全部命中且同SHA正文读取；10个历史原件及旧正式generation读取通过。完整本地1389passed/4平台skip，最终索引相关31项通过，知识/组织/文档/阅读路线检查通过。准备独立提交并推origin lite，实际CI和refs以发布回执为准。

冷验证副本最初非Force清理已移除其中的知识复制，但隐藏.git与cold-store仍在；进一步清理被自动审批blocked by policy拒绝，保留且不改工具绕过。此前受拒绝的旧Skill/pytest备份及含链接测试临时目录均未再尝试清理。本轮没有新增依赖、训练/GPU或新硬件资格验证。

本仓AGENTS要求将有用独立工作划分scope。实际Agent与归属见 .work/lite-refactor-20261105/agent-scopes.json；主控负责索引/reader/数据迁移/版本与最终发布。基线见同目录baseline.json。旧全量维护计划仅保存在0f2e883提交，不作为本轮任务指令。
