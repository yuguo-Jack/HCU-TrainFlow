# 2026-11-18 容错命令补充 review / 0.8.3

用户要求把 TrainFlow 容错命令纳入再次全面 review；沿用此前更新、同步、提交/push lite 和小标签授权。基点为已发布 eb86e0d / v0.8.2。第一阶段 HCU-Knowledge a3a5be5 / v0.6.3 保持只读，来源不重新刷新，现场作业和训练依赖不改动。

已完成：

1. 核对原生 CLI/parser、脚本/JSON、适配器与跨阶段恢复闭环；31次本地帮助成功，19条CLI及10条脚本示例参数核验，固定HCU入口与结果源码交叉核对。
2. 修复通用监测模板缺独立启动预算；旧context观察器可按原spec执行status/stop，CLI和API的start继续校验当前context。原record/config/process/argv/pidfd守卫保留，新回归不实际发信号。
3. 修正envcheck scenario/operation、分阶段结果与.state布局及最终退出解析；补真实console/launcher环境、NRE构建器和SaFE入口。退役3个已证明不存在的当前监控路径，保留历史原件。
4. 联动文档、Skill、阅读导航和真实消费者维护规则。独立代码/文档复核通过；完整软件测试1443 passed、4平台条件项skipped，知识/覆盖/文档/资源检查通过；本机六Skill与现有TrainFlow0.8.3元数据离线同步且--check通过。

正式收据：knowledge/catalog/fault-command-review-20261118.json。历史v0.8.2收据不改写；新收据绑定当前内容哈希与固定来源。

发布按origin/lite进行，核验实际提交CI后推送新的小标签v0.8.3；main及所有旧标签保持不动、不force，最终结果以Git引用和CI为准。未执行远程、GPU、故障注入或现场恢复演练。此前被策略拒绝的旧清理路径保留，不再重试。
