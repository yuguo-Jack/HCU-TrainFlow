# 官方 Wiki 的检索、更新和关联

## 持久内容与缓存

knowledge 中 Markdown 是作者结论，sources.json 是所监测路径和 ref，source-lock.json 是固定来源清单，maintenance.json 将源码变更连接到 Skill/命令/解析器。索引、抓取原文、staging、review receipt 在私有工作区。重要更新后把公共来源锁和作者页一起提交，缓存不进入 Git。

SQLite FTS5 使用英文符号分词、中文 bigram 和 BM25 标题加权；不下载 embedding 模型。它支持 engine/stage 过滤，检索不访问远端。当前轻量检索应通过真实问题持续评估，必要时再加重排；无需先引入大模型索引。

## 更新闭环

1. `wiki-refresh PROJECT SOURCE_ID` 解析 ref 到 SHA 并拉注册文件，不随意扫描用户私有目录。新增主题先注册需要的源码/测试/配置路径。
2. 比较最近已复核内容，列所有受影响总览、专题、案例与 workflow。重复采集无新变更不会抹掉此前待复核。
3. Wiki Skill 阅读 diff 和完整函数、必要时 PR、release、roadmap 和实际 dependency gitlink。`wiki-pr owner/repo N` 完整分页采集 issue comments、inline comments、顶层 review 和文件列表；缺 diff 标明 partial 并补源码。
4. 逐页修正结论及新引用；为 page/workflow 填 decision、note、page_sha256、source_commit，再 `wiki-review PROJECT STAGE decisions.json`。新 commit 尚有失败路径不得通过。
5. 作者把公开来源锁/正文更新后重新 index、检查源码链接与真实问题检索。运行中任务不自动升级依赖；需要新 context 和相应验证。

抓取 ref 变化但监测路径未变，只说明这些路径未变；不是全仓无功能变化。源码引用路径仍存在也不能证明正文解释正确。Agent 必须查看关联总览、专题和案例的语义一致性。

## 阅读深度

Megatron 生态为首版重点。其他引擎有入口导航及任务检查契约，但不宣称逐模型完全覆盖。扩展页按定位/目录/安装/运行/测试/调用链/优化/诊断/更新组织；案例要有瓶颈、改动理由、实现位置、适用条件、验证及回退。

## 与 HCU 大知识库

按需检索 HCU 知识库、在线飞书或当前底层源码；大知识库不作为启动硬依赖。此项目局部 Wiki 更新不会调用 HCU 大知识库更新技能。权限与 HCU 命令发生变化时，独立记录现场缺口并请求用户协助。
