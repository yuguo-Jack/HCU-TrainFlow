# JSON 契约和判定边界

以下值是示意，不能当作 HCU 的标称性能或统一精度容差。路径、阈值和来源必须由具体任务填写。完整可运行构造见 `src/hcu_trainflow/demo.py`。

## TaskSpec

`schema_version: 1`；`task_id` 为稳定 ID；`mode` 取 environment/adapt/analyze/optimize/diagnose/operate/full；`objective` 为任务目标；非空 `context` 描述比较范围；`permissions` 缺省为空，可选 execute/sync/notify/agent-dispatch；`recovery_owner` 指既有容错工具；`budget` 支持 max_operations/max_seconds。

context 包含初始 baseline、环境、模型、数据与质量契约身份。baseline 和 candidate 的源码可以不同，但属于同一个已冻结比较上下文。挂接协作循环后，各轮 candidate.snapshot 单独锁具体实现、配置与产物，报告必须绑定对应 candidate_snapshot；不能将旧报告移用到新候选。环境、模型、数据、初始基线或验证契约变化时用 task-context 更新并重新验收。未挂接 flow 的旧式任务没有候选绑定，仍需将候选身份放在 context，改变候选后更新 context。

task-context 的每次实际重置还记录 context_epoch。切换 A→B→A 不会重新启用 A 的旧验收、旧 assignment 或旧 flow；历史证据保留用于查阅，重新规划并登记新验收后才可推进。普通阶段转换不会重置已验证的上下文。

## 环境验收

```json
{
  "context": "TASK_CONTEXT_HASH",
  "required": [
    {"node": "allocated-node", "device": "0", "check": "gemm",
     "kind": "performance", "conditions": {"dtype": "bf16", "m": 4096, "unit": "TFLOP/s"},
     "minimum": 100, "basis": "REPLACE_WITH_MATCHED_EXPECTATION"}
  ]
}
```

观测是数组，每项重复 node/device/check/conditions/context，另含 status、executed、evidence 和 value。三元组不可重复，每个 required 项必须有匹配观测；匹配只覆盖契约声明的条件，Agent 必须把关键条件写全。

性能检查低于可比且有依据的 `minimum` 时为 `fail`；条件或证据不足为 `incomplete`，不能凭统一百分比生成阈值。任何未通过的 performance 项均附 `follow_up`，报告的 `follow_up_required=true` 提醒当前 Agent 执行[差距排查闭环](environment-discovery.md#6-性能不及预期时的排查顺序)。`classification` 区分 `matched-performance-failure`、`provisional-performance-discrepancy`、`check-failure` 和 `evidence-gap`；这不是自动执行或根因判定。

若测试退出正常或达到旧最低线，但原件支持仍有未处理的可信性能差距，负责 Agent **必须**在对应的 performance 观测中保留：

```json
{
  "performance_discrepancy": {
    "summary": "原表与当前数据存在待解释差距；列明可比部分及限制",
    "evidence": ["REGISTERED_REFERENCE_SHA256", "REGISTERED_RAW_TEST_SHA256"],
    "missing_conditions": ["原表的软件构建身份尚待核对"]
  }
}
```

以上片段合入原观测；示意 ID 必须替换为 `artifact-add` 返回的 64 位小写 SHA256，并同时放在观测自身的 `evidence` 数组。summary 与 evidence 非空，missing_conditions 可省略或为字符串数组；未知字段、伪类型和缺关联证据会报错。该记录表示**尚未关闭**的差距，不接受 `resolved=true` 等直接放行字段；即使 status=pass 也转为 incomplete，进入 `required_missing`，已确定的 fail 则保持 fail。程序不自动推断“明显”或猜缺失条件，Agent 不能用不填记录的方式忽略已发现的问题。

纯函数/`environment-check` 验证字段及证据关联，不读取 artifact 内容来证明比较成立；报告登记 `report-add` 时按既有 Store 规则验证证据已注册且完整。原失败及处理经过在 flow/experience 中保留，读原件、做授权内有界尝试和回归后，才用新的观测重新判定；移除字段本身不构成关闭问题的证据。

## QualityContract 与记录

```json
{
  "context": "TASK_CONTEXT_HASH",
  "sample_fingerprint": "FROZEN_SAMPLE_AND_MASK_HASH",
  "aggregation": "global-valid-token-mean",
  "min_steps": 100,
  "atol": 0.001,
  "rtol": 0.001,
  "tolerance_basis": "REPLACE_WITH_NUMERICAL_JUSTIFICATION"
}
```

baseline/candidate 各含 context、sample_fingerprint、aggregation、executed、evidence、steps 数组、loss 数组。candidate 还必须 `candidate_path_exercised: true`。`skipped_required`、`failures` 或失败 status 阻止通过。steps 必须严格递增且完全对齐，loss 必须有限。程序比较固定窗口，不自动证明数据指纹的真实性或长期收敛。

`iteration-check` 输入 correctness、baseline_times、candidate_times、context、可选 max_regression。correctness 另要求 profiler_off=true 和 measurement_protocol。至少三次匹配性能重复，输出 iteration-kept 仍是 pending-stage-validation，不是生产默认。

## OperatorModel

models JSON 按分析输出中的 op key（优先）或 kernel name 映射。GEMM 提供 kind=gemm、m/n/k/batch；其他算子提供 flops/bytes/latency_floor_us。与之匹配的 peak_flops_s、bandwidth_bytes_s、basis 为依据，可追加 isolated_us、reference_us、efficiency_target 和 workload_evidence。

峰值单位是 FLOP/s 和 byte/s，时间单位是微秒。输入缺 shape/dtype 时必须补 workload_evidence；通信项有实际计算时标 mixed_compute。没有证据的模型不因给了数字就变成有效硬件结论。

## ReportEnvelope

`report-add` 所读 JSON 含 context、status、evidence。pass 要求 executed>0、无 failures/required_missing。evidence 先通过 artifact-add 保留为 SHA256 对象。报告必须由负责的 Agent/人阅读原始证据后形成；存储完整性和声明字段不能防止作者写错结论。

协作循环还要求 candidate_snapshot 与候选清单 artifact 相同。候选、独立 review、目标与人的回复契约见 [协作循环](collaboration.md)；不要只调用 task-transition 跳过已登记的 review。

## Assignment 与接手

`team-plan TASK FILE` 记录 rationale、max_parallel 和 assignments。每项有 id、owner、goal、scope、allowed_paths、acceptance、budget、context，并可声明 depends_on、peers、mode、checkout、resources、resource_scope、required。resource_scope 默认 assignment（整项预约），operation 用于不同算子并行开发、仅在实际测试时按资源租约互斥。`assignment-add` 保留为单项追加入口。

`assignment-claim` 返回 token 和已验收依赖报告的 inputs 哈希；`assignment-bind` 绑定真实运行时 session。`assignment-return ... --token N` 引用 JSON 报告（context、精确 inputs、summary、evidence）；`assignment-review` 的 accept 才解锁下游。`assignment-yield` 要求证实工作已静止，恢复必须重新领取；cancel 不等于完成。旧的未领取 assignment 不能直接 return。

`agent-send` 保存有方向的 question/answer/finding/blocker/handoff；`agent-ack` 区分 seen 与 handled，回答由提问方确认。消息不自动启动模型。事件 inbox 的投递状态与消息处理、工作验收是三套不同状态。字段示例、并行条件和过期处理见 [多 Agent 契约](multi-agent.md)。

## WikiReview

```json
{
  "pages": {
    "knowledge/PAGE.md": {
      "decision": "still-applicable",
      "note": "说明新旧源码差异以及为什么正文仍成立",
      "page_sha256": "CURRENT_AUTHORED_PAGE_HASH",
      "source_commit": "OBSERVED_SOURCE_COMMIT"
    }
  },
  "workflows": {}
}
```

decision 可为 updated/still-applicable/historical。所有 affected pages 与 workflows 必须分别给出结论；不能漏掉总览只更新案例。review receipt 表示内容复核记录，硬件验证仍单独登记。
