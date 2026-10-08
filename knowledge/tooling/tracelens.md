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
---

# TraceLens 复用接口与训练补充信息

## 可直接复用

当前入口 `TraceLens_generate_perf_report_pytorch` 接收 `--profile_json_path`，可输出 `--output_xlsx_path` 或 `--output_csvs_dir`。Python API 还有 overlap、kernel summary、recompute、call stack 等选项。安装到分析环境后先核对 `--help`，再建立 command card；TrainFlow 不强制安装其重依赖。

```text
TraceLens_generate_perf_report_pytorch --profile_json_path rank0.json --output_csvs_dir report-rank0
```

还有独立 multi-rank collective 报告入口。不能将单 rank 报告当成全域验证。工具 architecture/Origami 等预测需要匹配 HCU 设备能力，不能把 AMD/NVIDIA 内置参数直接视为 HCU 标称值。

## TrainFlow 负责的补充

真实 process groups、训练 phase/step、当前快照、shape 来源、90% 端到端覆盖、未归因时间、精度状态、模型内/独立性能差和后续优化责任人。TraceLens 的原始报告保留为证据，TrainFlow 的轻量区间归因只补充边界检查，不替代它的细节分析。

## 升级检查

升级 TraceLens 时对 CLI/API signature、输出列、时间单位、kernel 分类和 collective 命名重跑固定 trace。若字段不支持必须报缺失；不能把解析为空当成没有瓶颈。

## 固定源码与更新范围

- [setup.py](https://github.com/AMD-AGI/TraceLens/blob/c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3/setup.py)
- [TraceLens/Reporting/generate_perf_report_pytorch.py](https://github.com/AMD-AGI/TraceLens/blob/c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3/TraceLens/Reporting/generate_perf_report_pytorch.py)
- [docs/how-to/collective-report.md](https://github.com/AMD-AGI/TraceLens/blob/c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3/docs/how-to/collective-report.md)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
