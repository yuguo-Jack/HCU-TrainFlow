# 私有训练经验 Wiki

官方 Wiki 解释通用实现；私有经验 Wiki 保存某个环境、模型、源码和数据条件下的实际结果。参考 Hyperloom 将策略、实现身份和测量证据分开的做法，TrainFlow 增加训练上下文、阶段 loss、失败候选和 Cookbook 交付关系。

## 保存位置

私有 `TRAINFLOW_WORKSPACE` 中：

```text
objects/<prefix>/<sha>     原始日志、trace、报告与不可变经验记录
experience/
  INDEX.md                按任务、模型、环境和结果浏览
  pages/<id>.md           可直接阅读的经验页
  records/<id>.json       持久记录，供重建检索表和页面
```

检索表和任务事件保存在 Store 的 SQLite 数据库。备份整个私有工作区；objects 和 records 是长期资产，不能当普通源码缓存删除。公共 Git 仓不包含这些现场数据。

每条记录绑定原始 context 指纹与 context_spec。任务上下文应包含环境/设备/gfx、DTK/PyTorch/runtime/库版本、源码 SHA/patch、模型结构/checkpoint、数据/分词/样本指纹、精度、并行拓扑及启动配方。缺失字段需要补证据，不能推测。跨环境可检索，复用前仍需验证。

## 自动记录与解释记录

- `report` 保存报告、`flow-advance` 通过阶段时，自动生成经验记录与页面，保留原 context 和报告。旧事件缺少 context 时明确跳过，不用当前环境补写历史。
- 自动记录保留报告原有数据，不猜测指标单位和统计口径。Agent 在基线、关键候选、阶段 loss、扩容、故障恢复、阶段结束和 Cookbook 交付时补充结构化解释。
- accepted/rejected/incomplete 都保留；失败经验包含原因、边界和回退，不当作推荐配置。
- 经验写入失败不撤销已保留的实验报告，返回 pending 和续接命令。事件重放及相同手工输入重试幂等。

```bash
hcu-trainflow experience-sync TASK
hcu-trainflow experience-search "overlap memory" --model MODEL --environment ENV
hcu-trainflow experience-read RECORD_ID
hcu-trainflow experience-compare BASELINE_ID CANDIDATE_ID
hcu-trainflow experience-index
```

model/environment 是 context 对应值的精确过滤；复杂对象按规范 JSON 保存，也可先用问题词检索，再用 `--context` 判断是否同上下文并读全文。索引可重建，原始记录和证据必须保留。

同一事件或同一手工输入的并发重试复用一条记录；SQLite 事务协调事件身份和导航发布，避免互相覆盖索引。新记录保留 source_event，experience-index 可恢复事件映射；重建先验证全部记录、上下文与证据，再替换索引。页面或导航写入中断时，原始记录仍保留，可用 experience-sync / experience-index 恢复。备份时仍须保留整个私有工作区的数据库、records 和 objects。

## 解释记录契约

`experience-record TASK file.json` 的最小字段模板如下。hash 和说明必须替换为真实任务证据，不是演示测量：

```json
{
  "context": "CURRENT_TASK_CONTEXT_HASH",
  "milestone": "tp-overlap-candidate",
  "kind": "optimization",
  "summary": "问题、实施范围和结论",
  "outcome": "observed",
  "interpretation": "瓶颈假设、改动理由、适用和失败条件、回退及待验证项",
  "evidence": ["RETAINED_ARTIFACT_HASH"],
  "metrics": [],
  "loss": {"status": "not-run"}
}
```

kind 支持 environment、baseline、performance、numerical、diagnosis、scale、optimization、cookbook、completion。metrics 每项必须有有限 value 及 name/unit/scope/aggregation/measurement_window/evidence，证据属于本条记录。典型值包括 step p50/p95、tokens/s、峰值 allocated/reserved、关键 kernel shape/效率、通信等待、恢复时间和 checkpoint 进度。

有 baseline 时链接既有经验 ID，填写 comparison 的 controlled_variables、changed_variables、limitations；跨 context 还需 context_difference。程序展示两侧指标和差异，不自动计算不同口径的 speedup。复用历史方案先核对版本、shape、并发和资源条件。

loss 独立于性能结论：not-run/pass/fail/incomplete。非 not-run 需要同 context 的保留报告及 operator/short-run/stage 范围；pass 需要实际执行、无失败和必需覆盖。局部正确性或性能不能冒充阶段 loss。仍按每轮局部验证、稳定阶段验 loss 的流程，对照初始数值基线。

## Cookbook 关联

由成果所属阶段 Skill 负责最佳实践。先保存 baseline、候选、验证和边界，再写 kind=cookbook 的记录；delivery 字段示例：

```json
{
  "status": "draft",
  "public": true,
  "experience_ids": ["BASELINE_OR_RESULT_RECORD_ID"],
  "redaction_review": "拟公开方法与示例已核对，不含现场数据"
}
```

完整记录仍需要 context、milestone、summary、outcome 和 evidence。提交后增加 submitted 记录及 PR URL；合入、拒绝、替代使用 merged/rejected/superseded，历史不覆盖。可从最佳实践追回具体任务、候选和验证，也能从实验找到交付情况。

记录命令不发送 PR、不上传数据。公共 Cookbook 只放可公开方法/代码和获准示例；原始模型、数据、日志、内部链接和整份经验页留在私有工作区。公共导出器拒绝直接复制 experience、objects 等目录；发布沿用会话和目标仓授权。

## 主控与阶段 Skill

任务开始或遇到问题时，先检索相同模型/环境/机制的历史经验，再查官方 Wiki、线上 PR、底层源码和必要的 HCU 大知识库。里程碑后确认自动记录成功，补充重要解释。长训按阶段保存统计、异常和恢复结果，无需把每行 log 做成知识页。

主控在线时自主维护局部记录和官方 Wiki，不要求每次另行指定。CLI 重放事件不等于模型分析；主控离线时既有监测/容错继续，恢复后补解释和行动。没有真实环境前不生成虚构性能或 loss 记录。
