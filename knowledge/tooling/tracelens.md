---
id: tooling/tracelens
title: TraceLens 复用接口与训练补充信息
engine: tooling
stages:
- optimize
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: amd-agi-tracelens
  path: setup.py
  commit: c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3
  sha256: 29d8f29499f4a8f4a5fc2c0aa6407d6f400a7c5bfdfb3ba2be274aff493fc253
- source: amd-agi-tracelens
  path: TraceLens/Reporting/generate_perf_report_pytorch.py
  commit: c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3
  sha256: 1027bf63be0cbd1dc053c905256639e5cc870a61b0278a0669aaf7ede414ead0
- source: amd-agi-tracelens
  path: docs/how-to/collective-report.md
  commit: c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3
  sha256: 5e593b974ec752c8b43b4f5babd2edc86e3eed19cefcbcb63b05ca55de0d36ce
- source: hcu-tracelens
  path: README.md
  commit: e4e891de60d3ac3cff3046a58e5852d0814b3dc6
  sha256: a6624439b1ab85f4e6cf216da384883e5b4e9c1a18f733362394d72bb750851e
- source: hcu-tracelens
  path: setup.py
  commit: e4e891de60d3ac3cff3046a58e5852d0814b3dc6
  sha256: 29d8f29499f4a8f4a5fc2c0aa6407d6f400a7c5bfdfb3ba2be274aff493fc253
- source: hcu-tracelens
  path: TraceLens/util.py
  commit: e4e891de60d3ac3cff3046a58e5852d0814b3dc6
  sha256: 211170f3d63aa825ff06b2acc952b94486227434862bdbf7ff76417a339f2d65
- source: hcu-tracelens
  path: TraceLens/Reporting/generate_perf_report_pytorch.py
  commit: e4e891de60d3ac3cff3046a58e5852d0814b3dc6
  sha256: 1027bf63be0cbd1dc053c905256639e5cc870a61b0278a0669aaf7ede414ead0
- source: hcu-tracelens
  path: TraceLens/Reporting/generate_multi_rank_collective_report_pytorch.py
  commit: e4e891de60d3ac3cff3046a58e5852d0814b3dc6
  sha256: 0566e1ecf0606f7f39e22e99d1c264ea104ebee65f8e574b48d98f178338adf3
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/utils/arch_utils.py
  commit: e4e891de60d3ac3cff3046a58e5852d0814b3dc6
  sha256: 56093b8897f526694153e0303a35562a29cc465e48872c8f131aa853d9e6fb2a
- source: hcu-tracelens
  path: TraceLens/Agent/Analysis/utils/deterministic_fallback.py
  commit: e4e891de60d3ac3cff3046a58e5852d0814b3dc6
  sha256: 8fa877065e24b81512ee67f8d57d5424a95ddcfc0851a501828713e44c536935
- source: hcu-tracelens
  path: docs/hcu-integration.md
  commit: e4e891de60d3ac3cff3046a58e5852d0814b3dc6
  sha256: c9ad787d82130aa710e1fd009bbae950739a087ceea796257abfdda4bc5a40a5
- source: hcu-tracelens
  path: tests/platform/test_portability.py
  commit: e4e891de60d3ac3cff3046a58e5852d0814b3dc6
  sha256: eb580b92dedaa3675a67db14538bad7e631dfa8652b24e55354d3709963d01ad
---

# TraceLens 复用接口与训练补充信息

## 可直接复用

TrainFlow 锁定 HCU fork 的提交，保留 AMD 上游接口与完整功能。当前入口 `TraceLens_generate_perf_report_pytorch` 接收 `--profile_json_path`，可输出 `--output_xlsx_path` 或 `--output_csvs_dir`。Python API 还有 overlap、kernel summary、recompute、call stack 等选项。按 [集成指南](../../docs/integrations.md) 安装到本地分析环境后先核对 `--help`，再建立 command card；JAX、回放和性能模拟等额外依赖按实际路径配置。

```text
TraceLens_generate_perf_report_pytorch --profile_json_path rank0.json --output_csvs_dir report-rank0
```

还有独立 multi-rank collective 报告入口。不能将单 rank 报告当成全域验证。工具 architecture/Origami 等预测需要匹配 HCU 设备能力，不能把 AMD/NVIDIA 内置参数直接视为 HCU 标称值。

## 原生能力与 HCU 扩展

两个 TrainFlow 报告子命令没有覆盖所有原生工具。性能对照优先用 TraceDiff，graph attribution 复用原生 inference 报告，trace 分段/索引及源码定位使用对应 CLI；EventReplay 在匹配的远端环境执行。rocprofv3、pftrace、JAX 等输入也保留上游入口，具体格式和依赖仍需验证。完整功能表见集成指南及 fork 的维护文档。

目前 fork 的功能代码差异只有 Windows CSV 字段上限的兼容修复，没有删除解析器或模型。所有 13 个原生入口通过了 help/import 检查；这不表示所有格式和预测已用真实 HCU 数据验证。新增 HCU 支持先使用架构 JSON、`TL_EXTENSION` 及现有 op/collective 扩展接口，核心更改需要可复现的实际缺口、源码依据与回归。

## TrainFlow 负责的补充

真实 process groups、训练 phase/step、当前快照、shape 来源、90% 端到端覆盖、未归因时间、精度状态、模型内/独立性能差和后续优化责任人。TraceLens 的原始报告保留为证据，TrainFlow 的轻量区间归因只补充边界检查，不替代它的细节分析。

## 升级检查

升级 TraceLens 时对 CLI/API signature、输出列、时间单位、kernel 分类和 collective 命名重跑固定 trace。若字段不支持必须报缺失；不能把解析为空当成没有瓶颈。

更新同时检查 `amd-agi-tracelens` 与 `hcu-tracelens`，区分上游 main、fork hcu 和任务锁定提交。fork 补丁在上游已有等价实现后，经回归再移除。工具 checkout 保持干净，开发修改使用独立工作目录；真实 trace、现场硬件参数和凭据不进入公开仓。

## 固定源码与更新范围

- [setup.py](https://github.com/AMD-AGI/TraceLens/blob/c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3/setup.py)
- [TraceLens/Reporting/generate_perf_report_pytorch.py](https://github.com/AMD-AGI/TraceLens/blob/c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3/TraceLens/Reporting/generate_perf_report_pytorch.py)
- [docs/how-to/collective-report.md](https://github.com/AMD-AGI/TraceLens/blob/c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3/docs/how-to/collective-report.md)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。

- [HCU fork 能力与维护](https://github.com/yuguo-Jack/TraceLens/blob/e4e891de60d3ac3cff3046a58e5852d0814b3dc6/docs/hcu-integration.md)
