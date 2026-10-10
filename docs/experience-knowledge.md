# 任务经验档案与工程 Wiki

官方 Wiki 解释通用实现；任务经验保存某个环境、模型、源码和数据条件下的完整实际结果。跨任务共享的站点、配方和模型经验整理到随工程提交的 `knowledge/`，见 [知识归属](knowledge-architecture.md)。本页 CLI 针对所选任务 Store，不代替工程 Wiki。参考 Hyperloom 将策略、实现身份和测量证据分开的做法，TrainFlow 增加训练上下文、阶段 loss、失败候选和 Cookbook 交付关系。

## 保存位置

私有 `TRAINFLOW_WORKSPACE` 中：

```text
objects/<prefix>/<sha>     原始日志、trace、报告与不可变经验记录
experience/
  INDEX.md                按任务、模型、环境和结果浏览
  pages/<id>.md           可直接阅读的经验页
  records/<id>.json       持久记录，供重建检索表和页面
  references/
    README.md, INDEX.md   私有硬件、环境与性能参考入口
    records/<id>.json     固定来源与适用条件的参考记录
    pages/<id>.md         可重建的可读参考页
```

检索表和任务事件保存在 Store 的 SQLite 数据库。备份整个私有工作区；objects 和 records 是长期资产，不能当普通源码缓存删除。完整 Store 不复制进 Git；有复用价值的现场配置、关键数值和精选证据按知识架构整理入仓。

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

### 有效现场配方必须形成可检索经验

环境检查、通信排障或调参得到有复用价值的结果后，由所属阶段主动整理；不等用户再次提醒，不只在临时 research 报告里保存。仍使用现有 `experience-record` 和有精确适用条件的 `reference-record`，不新增平行知识库。

- **身份与拓扑：** 站点/节点和设备、产品/gfx、实际镜像 digest、驱动/runtime/通信库构建与哈希、网卡/链路/NUMA、容器和调度方式。未知项明确保留；镜像标签不能代替构建身份。
- **可复现配方：** 原命令、实际执行命令及差异、环境脚本的加载顺序与固定原件；显式列出有用的非敏感环境变量、默认或未设置值、每个 rank 的实际生效验证和动态库路径。凭据与完整未经筛选的环境转储不入页。
- **效果与因果边界：** 测试 shape/dtype、消息量、rank/节点、计时与字节定义、预热/重复层级、各轮结果/正确性，与预期及原配方比较。多变量配方收益不能归给单个开关；带宽、延迟和不同统计列分别保留。
- **复用与回退：** 适用/不适用条件、复用前检查、过期触发、实际故障与回退。参考成功不代表新任务自动健康通过；更换硬件、镜像、库、网络策略、节点规模或脚本需重新判断适用范围。
- **入库验收：** 经验正文写入实际检索词/别名与命令变量名，链接固定原件、实验和参考记录；用新任务可能提出的问题做 `experience-search`，并对可量化参考做一次同条件 `reference-query`，确认能查到正文和原始证据。任务记录之后，将可复用站点/模型知识和必要原件整理进工程 Wiki，再从新 Store 验证 wiki-search 与相对链接。

任务开始或遇到问题时，先检索相同模型/环境/机制的历史经验，再查官方 Wiki、线上 PR、底层源码和必要的 HCU 大知识库。里程碑后确认自动记录成功，补充重要解释。长训按阶段保存统计、异常和恢复结果，无需把每行 log 做成知识页。

HCU-Knowledge 与两项知识库 Skill 属于完整安装的必需依赖，贯穿适配、优化和容错。按问题查阅不等于每一步强制查询；本项目的搜索、局部记录和官方 Wiki 维护也不会顺便更新 HCU 大知识库。

主控在线时自主维护局部记录和官方 Wiki，不要求每次另行指定。CLI 重放事件不等于模型分析；主控离线时既有监测/容错继续，恢复后补解释和行动。没有真实环境前不生成虚构性能或 loss 记录。

## 可复用的硬件、环境和单测参考

查到并核对过的硬件能力、标称关键指标、环境身份和近期单测数据，可以保存在 `experience/references/`。它们可在后续模型任务中复用，避免反复查询同一份资料。该目录使用原有 Store 的不可变 objects、事务和私有文件结构，不部署额外数据库或向量模型；与经验记录通过可选 `experience_ids` 关联。复制整个私有 workspace 后仍可读取原件并重建页面。

Agent 维护这些记录，用户无需手工生成结构化数据。只有三个命令：

```bash
hcu-trainflow --workspace PRIVATE reference-record reference.json
hcu-trainflow --workspace PRIVATE reference-query target.json
hcu-trainflow --workspace PRIVATE reference-index
```

`reference-query` 直接返回完整记录、来源、原始证据 ID 和私有页面。它只读本地资料，不联网、不重新运行单测，也不更新 HCU-Knowledge；需要刷新时由当前 Agent 在已授权范围内查证或安排实测。跨任务共享采用本仓 `knowledge/sites/` 或 `knowledge/experiments/`；此查询不会自动导入仓内 JSON。用 `--workspace` 明确选择任务 Store，不能把切换/复制旧任务目录作为工程知识的唯一复用方式。

### 记录的含义

| 字段 | 契约 |
| --- | --- |
| `schema_version` / `key` / `title` | 版本 1；稳定的指标/事实键；可读标题 |
| `category` | `hardware`、`environment` 或 `performance` |
| `basis` | `documented` 文档事实；`nominal` 产品标称；`historical-measurement` 历史实测；`site-measurement` 当前现场实测。分别保存，不能互换含义 |
| `scope` | 按 hardware/software/topology/workload/environment 写明确约束，不使用 unknown、any、通配符；无关维度可省略，但省略须有依据 |
| `value` / `unit` / `statistic` | 原始单位和值，不自动换算。性能/标称值必须是有限非负数；事实可为文字或布尔值。statistic 明确 nominal/documented/median/p95 等口径 |
| `method` | 固定的 `id`、`revision`、方法 `description`；不能仅写 main/latest |
| `observed_at` | 实际测量或现场观测时间；不能写“这次重新看报告”的时间 |
| `reviewed_at` / `reviewer` | 本次内容核对的时间与负责人；不伪称独立硬件验收 |
| `sources` | 每项含 `id`、原始 `uri`、固定 `revision`、`retrieved_at` 和本记录中的 `evidence` 列表；latest URL 也须保存正文哈希/版本 |
| `evidence` | 已进入当前 Store 的原始报告、文档、日志或库存证据 artifact ID；只有链接而没有正文证据不能登记为可复用基准 |
| `freshness` | 明确按固定来源版本，或按实际观测年龄与到期时间复核 |
| `limitations` | 适用和失败条件、信息缺口、额外验证要求；不能留空 |
| `supersedes` / `experience_ids` | 可选：替代的固定参考 ID / 关联的实验经验 ID，旧记录不删除 |

硬件记录至少有 `scope.hardware.architecture`；标称峰值还必须有具体 `product`，避免同架构不同产品混用。算力峰值应把精度、dense/sparse、频率等影响上限的条件写进 scope；不能把某产品的宣传峰值直接用作另一配置的实测上限。

性能记录必须有 software、topology、workload，其中 workload 明确 shape 和 dtype；method 记录测试脚本/命令版本、预热、重复、计时、同步、聚合及字节/FLOPs 定义。通信记录要覆盖节点/设备数、网卡与互联、collective、消息量等实际影响比较的条件。现场实测与环境记录还必须绑定 environment 与 software 身份；仅用可能漂移的镜像 tag 不足以证明相同构建，应保存 digest/源码/动态库等适用身份。与正确性结果和真实原始单测报告一同阅读，不把保留参考值当成通过检查。

同名指标的三种数值分别写不同 basis。例如标称 HBM 带宽、历史 copy 单测和当前节点 copy 单测仍是三份记录，不能合并成一个“标准性能”。需要将某站点测量提炼为跨站参考时，另建经过复核的 historical-measurement 记录，解释去掉哪些环境约束及依据，不能直接放宽旧记录。

### 时效和精确匹配

稳定硬件事实可用 `freshness: {"mode": "source-revision"}`，没有人为设定的强制有效期。若查到来源新版本，在查询的 `source_revisions` 中提供对应 source ID/版本；不同版本返回 stale，触发内容核对。未提供当前版本时，结果明确只依据固定来源，不声称刚刚核对了线上最新文档。

环境与测量使用 `freshness: {"mode": "age", "max_age_seconds": ... , "update_due": "带时区的 ISO 时间"}`。实际到期取 `observed_at + max_age_seconds` 与 `update_due` 中较早者；有效期依指标、站点变更频率和任务要求设定，没有全工程统一的默认天数。重新读取或重建索引不会重置时效。所有时间必须带时区，测量不晚于 review，review 不能在未来。

目标查询必须有精确 `key` 和 `scope`。按记录中每个约束匹配目标，缺少字段返回 missing；不同架构、软件、shape、dtype、拓扑等返回 mismatched。性能比较还需目标提供相同 unit、statistic 及 method 的 id/revision；不会自动把 GB/s 换成 GiB/s，或把 p95 当中位数。目标可以带额外条件，但记录没有约束的字段不等于已在所有取值上验证过，必须结合 limitations 判断其是否确实独立。

| 查询结果 | 下一步 |
| --- | --- |
| `compatible` 且 `reusable_ids` 非空 | 作为本次分析的有条件参考，保留来源；不必重新检索同一资料 |
| `stale` | 按来源版本/测量有效期复核，并联查经验导航中的新材料；必要时补新记录 |
| `mismatched` | 跨上下文搜索原文及历史条件，为目标另找参考；保留旧范围记录 |
| `missing` | 先补齐查询条件并搜索经验原文导航，再查 HCU 知识库/当前来源或安排已授权实测；不猜数值 |
| `selection_status=conflict` | 同一精确契约有不同有效数值，暂不自动选择，核对证据后明确替代 |

`compatible` 表示参考条件匹配，`environment_pass` 始终为 false；健康、正确性、性能与阶段 loss 门槛仍需当前任务的实际证据。同契约矛盾值保留并显示 conflicts；复核后用 `supersedes` 替代。跨架构、basis、单位或方法的记录不能互相替代。已有合适的新记录时，旧的过期/被替代记录不会迫使每次查询都重新采集。

### 未确认资料仍可搜，查到后追溯原文

严格 reference 缺少所需条件，不代表知识库没有相关材料。产品标称、历史表格、飞书或仓库说明尚不能满足 scope 时，先用 `experience-record` 登记 `kind=environment` 或 `diagnosis`、`outcome=observed` 的导航记录，保留原文 artifact、来源/版本/表格位置、已知条件和缺项；它不声明现场通过，也不把未知适用条件填成猜测值。

经验检索索引记录本身的文字，**不会递归索引 evidence artifact 的正文**。summary/interpretation 应写入原文支持的产品名、架构名、指标及常用别名、测试类型、版本、shape/dtype、定位和限制。未确认的产品到 gfx 对应关系要明确标注，不将相似名称当作同一硬件。

```bash
# 缺少精确 reference 时，先用主题/指标跨任务检索，避免过早使用精确环境过滤。
hcu-trainflow --workspace PRIVATE experience-search "DeepEP high throughput bandwidth"
hcu-trainflow --workspace PRIVATE experience-read RECORD_ID
hcu-trainflow --workspace PRIVATE artifact-read SOURCE_ARTIFACT PRIVATE_SOURCE_FILE
```

从导航读固定原文，必要时核对当前官方/飞书/代码来源。补齐适用范围、方法和时效后，才用 `reference-record` 登记可复用数值。条件尚不完整时，可以在经验记录中提供有明确差异说明的工程比较：逐项列出已知/未知条件、原始值及单位、可支持的结论与后续验证。不能把它包装成精确兼容、自动通过标准，或为凑齐 schema 编造缺失字段。

### 最新带宽预期与当前实测

环境验收和通信优化既要有本次实测，也要主动寻找**当前相关测试类型**的文档标称或近期历史预期，注明源版本及查阅时间。当前单测只能建立现场基线，不能独自证明达到应有水平。

对 DeepEP 等多模式库，分别记录高吞吐（HT）dispatch/combine 的带宽和低延迟（LL）的延迟/带宽；**LL 表不能替代 HT 带宽预期**。比较前核对后端、硬件/网卡与连接数、节点/rank、消息量/shape、dtype、软件与 XDP 等实际影响因素，以及字节定义、计时区间、同步和统计方法。API 总延迟、单 kernel 延迟、RDMA 带宽和双向汇总带宽也不能互换。

找到相近但不完全同条件的近期数据时，保留原文并给出有条件的差距分析，不因条件不齐就丢弃参考价值；也不自定一个百分比宣告通过。只有单位与方法确实可比时计算绝对/相对差距，再用当前条件的实测或明确的验收要求解决剩余不确定性。

可信差距还要按[环境性能排查闭环](environment-discovery.md#6-性能不及预期时的排查顺序)继续查配置/链路/库实现及尝试可逆对照。参考查询的 compatible 不是当前性能通过，mismatched/missing 也不是停止排查的理由。沿用 diagnosis 经验记录保留原件、假设、尝试、正确性/作用证据、保留或回退及未解项；未解决的环境观测附 `performance_discrepancy`，不只更新参考页面就宣告处理完成。

`reference-index` 先校验所有固定记录和 evidence，再重建 Markdown，不覆盖原件；页面生成失败可重试。记录原件被改写或证据丢失会报错，不能以重新建索引洗掉问题。完整 references 属于任务档案；精选测量、适用条件和必要原件按知识架构整理到本仓 Wiki。外部 Cookbook 导出边界单独遵守。
