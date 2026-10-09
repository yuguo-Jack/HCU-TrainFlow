# JSON 契约和判定边界

以下值是示意，不能当作 HCU 的标称性能或统一精度容差。路径、阈值和来源必须由具体任务填写。完整可运行构造见 `src/hcu_trainflow/demo.py`。

## TaskSpec

`schema_version: 1`；`task_id` 为稳定 ID；`mode` 取 environment/adapt/analyze/optimize/diagnose/operate/full；`objective` 为任务目标；非空 `context` 描述比较范围；`permissions` 缺省为空，可选 execute/sync/notify/agent-dispatch；`recovery_owner` 指既有容错工具；`budget` 支持 max_operations/max_seconds。

context 包含初始 baseline、环境、模型、数据与质量契约身份。baseline 和 candidate 的源码可以不同，但属于同一个已冻结比较上下文。挂接协作循环后，各轮 candidate.snapshot 单独锁具体实现、配置与产物，报告必须绑定对应 candidate_snapshot；不能将旧报告移用到新候选。环境、模型、数据、初始基线或验证契约变化时用 task-context 更新并重新验收。未挂接 flow 的旧式任务没有候选绑定，仍需将候选身份放在 context，改变候选后更新 context。

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

assignment-add 接收 id、owner、goal、scope、allowed_paths、acceptance、budget、context。assignment-return 引用已保留的报告对象；主控仍需验收。inbox 的 pending→claimed→completed 与工作结果验收分开。

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
