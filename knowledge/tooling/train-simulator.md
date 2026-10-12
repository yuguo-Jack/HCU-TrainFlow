---
id: tooling/train-simulator
title: HCU Train Simulator：容量、并行方案与实测校准
engine: tooling
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-document-reading
runtime_validated: false
reviewed_on: '2026-10-12'
sources:
- source: hygon-ai-train-simulator
  path: README.md
  commit: b7d8e6f3becebf5d09121bb1c582436a371c6710
  sha256: db02bd9c26493e9b303784ba411f1048a4860e77f4644d809846e1583c486f6b
- source: hygon-ai-train-simulator
  path: src/hcu_train_simulator/cli.py
  commit: b7d8e6f3becebf5d09121bb1c582436a371c6710
  sha256: 4a8e17695b06d2b798b897e10f64322cf425e2c5aeb5cf7ae9a23e32325f432f
- source: hygon-ai-train-simulator
  path: src/hcu_train_simulator/benchmarks/README.md
  commit: b7d8e6f3becebf5d09121bb1c582436a371c6710
  sha256: 3434c41ac185d987f17174d8c807c4b3d1ea21ee9f921e24d28b53503e039cb0
- source: hygon-ai-train-simulator
  path: src/hcu_train_simulator/communication/README.md
  commit: b7d8e6f3becebf5d09121bb1c582436a371c6710
  sha256: 3870277403b6df4664748ec9d12b3690c07e65e188833d181aca12170414e44a
- source: hygon-ai-train-simulator
  path: tests/README.md
  commit: b7d8e6f3becebf5d09121bb1c582436a371c6710
  sha256: e9179c181d11227cde571ddbda9ed103ea90312e34b80cacd0d2c9fc0b428e3f
- source: hygon-ai-train-simulator
  path: pyproject.toml
  commit: b7d8e6f3becebf5d09121bb1c582436a371c6710
  sha256: f6eb75f9456532e91ba132721e831de247767d281fe8d1afcea62e9a27376c8e
---

# HCU Train Simulator：容量、并行方案与实测校准

## 定位与边界

官方仓 [HYGON-AI/hcu-train-simulator](https://github.com/HYGON-AI/hcu-train-simulator) 提供模型训练的显存、计算、通信与配置搜索估算，服务于“能否放下全参、如何切分、值得试哪些配置”。它不是训练引擎，也不证明模型数值正确、某库可运行或某节点健康。

## 目录与调用链

`src/hcu_train_simulator/cli.py` 解析 init/run/analyze/search/solve → 读取配置与模型 adapter → 显存/计算/通信估算 → 组合系统时间或求解候选 → 终端及可选 HTML 报告。`benchmarks/` 提供效率校准入口，`communication/` 说明通信模型，`tests/` 包含 dense/MoE 系统测试，`examples/` 提供模型配置。定位一个异常估算时，要同时追模型转换、并行配置和各成本项，不能只改最终 TGS。

## 安装、运行与测试

先固定仓库提交，按 pyproject 构建 wheel 或项目支持的安装方法；旧 README 的个人 GitLab clone 示例不替代注册的官方源。工具运行时不必启动训练，但 benchmark 子功能可能访问 GPU，须分开资源准入。

```bash
hcu-train-sim init
hcu-train-sim analyze memory config.yaml
hcu-train-sim analyze comm config.yaml
hcu-train-sim analyze compute config.yaml
hcu-train-sim run config.yaml --no-report
hcu-train-sim search config.yaml
hcu-train-sim solve config.yaml
```

这些命令在任务目录执行；init 写配置，run 默认可生成 training_report，search 当前主要输出终端结果，不应到 HTML 寻找不存在的搜索结论。以 `tests/README.md` 的 dense/MoE ST 用例及实际测试目录检查公式变更；源码/测试阅读不等于本页运行验收。

## 模型、硬件和单位契约

保留模型实际 architecture、层数、hidden、head/KV、MoE/shared expert、视觉分支、优化器及精度。嵌套 HF text/vision config 需使用匹配 adapter；模型名字相同不代表估算覆盖全部层型。报告所需参数不足先补模型证据，不随意缩 dim 让结果好看。

硬件字段包括 dtype 峰值、HBM GiB、每节点卡数、机内/机间单卡单向聚合 GB/s、GEMM/向量/优化器效率。`use_bandwidth_table=true` 用内置有效带宽时，不再次乘峰值效率；false 才是峰值×对应效率。样例 64 GiB、480 TFLOPS 等不是所有 HCU 型号默认真值。现场使用实测/标称分别记来源和口径。

## 机制一：全参容量与最差 stage

检查静态参数/梯度/优化器、动态激活、通信 buffer、重算/流水保留和 checkpoint 峰值，按最大 PP stage/rank 而非平均显存判断。首尾不同层数、视觉模块、共享专家和 embedding 可造成不均。至少预留可解释余量，再用短跑校准；预测能放下不等于分配器碎片、临时 workspace 或恢复峰值都安全。

卡足够时优先全模型一个适用 DP 实例；不足才按用户边界缩 layer。完整配置适配优化后扩 DP，不必每次反复强调最小域。不得以较小代理模型的校准证明全参 memory/loss 已验收。

## 机制二：并行搜索与 overlap 假设

search 按合法 TP/CP/PP/EP/ETP、microbatch、VPP 候选估算，显存超过 HBM-margin 或切分不合法的方案淘汰，再按 TGS 排序。`num_layers_per_vp_stage` 非空可驱动 interleaved schedule/P2P overlap，MoE 候选还可能启用 EP overlap；这是模拟假设，不能视为引擎已经打开对应优化。

auto/manual/none overlap 模式影响暴露通信；manual 比例来自用户估计时须写明。DeepEP heuristic 和普通 all-to-all 不具有相同成本模型；实测 profile 若发现竞争或同步等待，校正效率/暴露开销后再搜索，而不是把任意通信都完全隐藏。

## 诊断、校准与更新

预测显存与实际不符：核对模型解析、dtype/optimizer、microbatch/GBS、重算、最差stage与临时分配；预测通信过低：核对拓扑、单位、消息量、表值/峰值是否重复打折以及 overlap 是否真实；预测计算过低：检查注意力/稀疏索引器、非 GEMM 和 CPU/输入时间是否建模。

保留预测配置、固定代码、实测日志与误差解释。只采用有证据支持的修正，不为拟合一个 step 修改全局硬件真值。任何版本新 adapter、公式或搜索策略变化，都复核 TrainFlow 容量与并行实验指南；现场仍需实际 profile、内存和阶段 loss。

## 来源、PR 与更新

- [README.md](https://github.com/HYGON-AI/hcu-train-simulator/blob/b7d8e6f3becebf5d09121bb1c582436a371c6710/README.md)
- [src/hcu_train_simulator/cli.py](https://github.com/HYGON-AI/hcu-train-simulator/blob/b7d8e6f3becebf5d09121bb1c582436a371c6710/src/hcu_train_simulator/cli.py)
- [src/hcu_train_simulator/benchmarks/README.md](https://github.com/HYGON-AI/hcu-train-simulator/blob/b7d8e6f3becebf5d09121bb1c582436a371c6710/src/hcu_train_simulator/benchmarks/README.md)
- [src/hcu_train_simulator/communication/README.md](https://github.com/HYGON-AI/hcu-train-simulator/blob/b7d8e6f3becebf5d09121bb1c582436a371c6710/src/hcu_train_simulator/communication/README.md)
- [tests/README.md](https://github.com/HYGON-AI/hcu-train-simulator/blob/b7d8e6f3becebf5d09121bb1c582436a371c6710/tests/README.md)
- [pyproject.toml](https://github.com/HYGON-AI/hcu-train-simulator/blob/b7d8e6f3becebf5d09121bb1c582436a371c6710/pyproject.toml)

按该仓完整目录与文档增量检查新增入口；通过 `wiki-search-pr` 搜索改动原因，再追当前实现和测试。正文是选定源码/官方文档解读，未在新现场运行。新 commit、接口、返回 schema 或依赖变化时，同时复核本页和相关工作流。
