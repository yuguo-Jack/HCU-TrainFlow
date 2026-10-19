---
id: official-torchtitan-wiki/releases-prs-and-update
title: TorchTitan 官方教程、Release、特性 PR 与持续更新
engine: torchtitan
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-tutorial-reading
runtime_validated: false
reviewed_on: '2026-10-20'
coverage: Curated source chains and official evidence at a fixed main commit; not all models, backends
  or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 3634007b5cca45b6e3ce61742e818c4c7fdb9c5147092cc4872e0752c00f7b75
- source: pytorch-torchtitan
  path: RELEASE.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 25602fde9bc0d1742bea6e1072b69db8565f4c37168b49b4a65b017f2d6b657b
- source: pytorch-torchtitan
  path: assets/version.txt
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 998f6b887ed7a6ef44e84210d0237b715bed42ea7254f48dc418afec0a484103
- source: pytorch-torchtitan
  path: pyproject.toml
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 0341afacb518276f192c2c8a836c32426e80856bf8c5f0ff194c3028c221520d
- source: pytorch-torchtitan
  path: torchtitan_recipes/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: a72fb9eab9eb7f376a50622327954f614694ed6aea5bb782aae51035e9c9157a
- source: pytorch-torchtitan
  path: torchtitan/config/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: e62e3776a4dd1c2179b3643d9e611f5a6f53fc972ac16de4588ee96a99a06b9b
- source: pytorch-torchtitan
  path: tests/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 0872f733f18e85e085802fff3813cd1ee359ec1cc10b8d5929642e62d4c4e712
- source: pytorch-torchtitan
  path: torchtitan/distributed/activation_remat.py
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 4e935605e29f904ad5c5bef1036e265021f42c334a7a17c6d01083040dffc5a7
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/README.md
  commit: a242475253433725f10f39c18f5ccbfdf188e097
  sha256: 5f4cdb46330683cb8bd2a65d764662712972fb8989afe35a9b9dfbe5e3270209
pr_sources:
- pr-pytorch--torchtitan-4760
- pr-pytorch--torchtitan-5033
- pr-pytorch--torchtitan-5101
- pr-pytorch--torchtitan-5107
- pr-pytorch--torchtitan-5137
- pr-pytorch--torchtitan-5250
- pr-pytorch--torchtitan-5263
- pr-pytorch--torchtitan-5268
- pr-pytorch--torchtitan-5277
- pr-pytorch--torchtitan-5280
- pr-pytorch--torchtitan-5288
---
# TorchTitan 官方教程、Release、特性 PR 与持续更新

## 本轮固定范围

| 内容 | 已收录范围 | 不能由此推断 |
| --- | --- | --- |
| 源码 | main 的固定提交 `a242475253433725f10f39c18f5ccbfdf188e097`；全仓路径/对象清单 | 全部文件已逐行精读或硬件验证 |
| 作者专题 | 15 页总览、目录、安装运行测试、训练/数值、并行/显存、编译通信、MoE/量化、profile、恢复、RL 与 3 个案例 | 每个模型/后端均已形成完整专题 |
| 官方原文 | 当前来源锁、文档 ledger 与全仓路径清单中的训练教程/README | 图表、外链或依赖工程已全部离线复制 |
| PR | 已保留的重要历史 PR 与本次增量窗口；完成范围以独立 PR ledger 为准 | 历史 PR 全量采集或全部案例精读 |
| PR 证据 | body、普通/行内评论、顶层 review 状态与正文、文件/patch、固定 base/head | 已 merged 等于已 release；作者实验等于本任务实测 |
| 运行 | 本轮做知识/搜索/更新与项目离线检查 | TorchTitan 已在 HCU 跑通 |

目录和 PR 分页已经完成的范围，由各自 ledger 表达；源码路径尚未精读、PR 尚未形成解释，不通过伪造复核回执改成已验证。本页统计是这次补充时的快照，后续更新以来源清单为准。

## Release 不等于 main 的版本文件

2026-10-20 复核官方 Releases，最新非预发布仍为 [v0.3.0](https://github.com/pytorch/torchtitan/releases/tag/v0.3.0)，发布于 2026-09-03。本次固定 main 的 `assets/version.txt` 仍为 `0.2.2`；应分别保存 tag、commit、包版本和依赖，不能根据一个字符串断言主线退回旧功能。

发布信息按[官方 Releases](https://github.com/pytorch/torchtitan/releases)查证；本库不单独批量归档发布页 JSON。v0.3.0 的兼容表、旧目录和参数是那次发布的条件，不自动适用于当前 main；例如主线之后重组 recipe、移除旧 CLI，用 release 教程运行 main 需要逐项核对。

查看新动态时同时检查 [Releases](https://github.com/pytorch/torchtitan/releases)、[官方 PR](https://github.com/pytorch/torchtitan/pulls)、[Issues](https://github.com/pytorch/torchtitan/issues) 与当前 README 的计划/讨论入口。没有某个 `roadmap` 标签的查询结果，不代表没有路线图。计划、draft/open PR、merged commit、release 和 HCU 分支分别标记。

## 官方教程导航

| 主题 | 本地整理入口 | 官方原始路径 |
| --- | --- | --- |
| Config / recipe / override | [安装运行](../guides/build-run-test.md) | `config/README.md`、`config/OVERRIDE.md`、`torchtitan_recipes/README.md` |
| 目录、模型和数据 | [源码地图](../overview/source-map.md)、[模型与数据](../topics/models-and-data.md) | `models/*/README.md`、`components/data/README.md` |
| 并行、PP、FSDP、重算 | [并行与显存](../topics/parallelism-and-memory.md) | `distributed/PARALLELISM_CONTEXT.md`、`PIPELINE_PARALLEL.md`、`FSDP.md`、`REMAT.md` |
| Compile / Graph / MoE | [编译通信](../topics/compile-fusion-and-communication.md) | `experiments/graph_trainer/README.md`、`models/common/dist_moe/README.md` |
| MXFP8 / NVFP4 / optimizer state | [低精度](../topics/moe-and-low-precision.md)、[数值](../topics/training-and-numerics.md) | `quantization/*/README.md`、`components/optim/BF16_OPTIMIZER_STATES.md` |
| Profiler / debug / benchmarks | [性能诊断](../topics/profiling-and-diagnosis.md) | `observability/`、`docs/debugging.md`、`docs/benchmarks/` |
| 保存恢复与容错 | [恢复](../topics/checkpoint-and-stability.md) | `components/checkpointer/README.md`、`experiments/torchft/README.md` |
| RL 与版本同步 | [TitanRL](../topics/titanrl.md) | `rl/README.md`、`rl/BITWISE_PARITY.md`、`rl/actors/monarch/README.md` 及当前服务实现 |
| CPU/GPU/集成回归 | [测试路线](../guides/build-run-test.md) | `tests/README.md` |

`torchtitan/...` 前缀可在 [全文件导航](../../upstream/source-map/pytorch-torchtitan.md) 中检索；[原文与章节列表](../../../../../catalog/README.md)和[文档 ledger](../../../../../catalog/document-ledgers/pytorch-torchtitan.json)给出实际保留页。上游 agent prompts、自动实验日记与零散研究日志按 source exclusions 排除，不注入共享知识或当作维护指令。

## 关键 PR 的阅读层次

| PR | 本次观察状态 | 去哪里看 | 主要边界 |
| --- | --- | --- | --- |
| #5277、#5280 | merged | 目录/配置专题 | 路径与构建次序改变，需复核启动和模型布局 |
| #5101 | merged | 重算专题 | FullAC 迁到 torch_remat，旧开关不照搬 |
| #5137、#5250 | merged | WGRAD 案例 | 梯度所有权、舍入、PP/graph 禁用条件 |
| #5033 | merged | Attention Residual 案例 | kernel 吞吐与模型吞吐不等价 |
| #5107、#5268 | merged | RL 权重同步案例 | trainer CPU 暂存与 generator FSDP group 峰值分别测量 |
| #4760 | 2026-10-20 API复核仍open；既有review包含请求修改 | PR 原文和 CP/MLA 候选 | 通信压缩/打包仍在评审，既有review报告过训练数值漂移；不能当现成等价优化 |
| #5263 | 2026-10-20 API复核仍open、未merge | 编译通信专题及 PR 原文 | DeepEP 新 API 与模型限制，deferred counts 不代表消除 CPU 等待 |

上表状态是采集时观察，不是永久结论。PR review 的修改意见、讨论中的失败与当前 patch 都保留；不要只读标题或作者最初的收益描述。

本次 [#4760 候选](../../upstream/prs/pytorch--torchtitan/PR-4760.md) 的 K/V all-gather 路线已改为先传归一化后的压缩 KV latent 与 headless key，再在本地执行 `wkv_b` 展开。Ulysses 路线先投影，再合并 Q 与 packed KV 传输，输入通信仍有一次 all-to-all 和一次 all-gather，输出 head→token 还需 all-to-all。该候选 head 还拒绝 fused MLA 与 CP 的组合、拒绝 TorchTitan vLLM MLA 路线，并禁用相应 Kimi parity/RL 测试；这些限制属于尚未合入的 PR，不直接归给本页固定 main。禁用测试和旧实验数据都不构成本次等价性或 HCU 验收。

## 搜索、追代码与更新

```bash
# 从项目目录执行；先跨知识库搜，再按明确引擎范围缩小。
hcu-trainflow wiki-search "TorchTitan 梯度累积" --project .
hcu-trainflow wiki-search "weight sync" --engine torchtitan --project .
hcu-trainflow wiki-search-pr "attention residual" --engine torchtitan
hcu-trainflow wiki-pr pytorch/torchtitan 5033
hcu-trainflow wiki-code pytorch/torchtitan a242475253433725f10f39c18f5ccbfdf188e097 torchtitan/models/common/linear/linear.py

# 定向更新；max 只是单批上限，存在 pending 时继续相应阶段。
hcu-trainflow wiki-update . pytorch-torchtitan --max-documents 100 --max-prs 50
```

普通检索只写私有缓存。Wiki update Skill 先看权限/新鲜度和完整文件树，再处理文档新增/变更、PR 讨论与源码差异；按问题可补任意历史或尚未收录的 PR。新增模型文件即使不匹配当前 document globs 也能通过全树发现，随后决定是否扩大收录范围。

主线/PR 变化后同时复核同仓总览、专题、案例，以及 `maintenance.json` 关联的 Torch 原生训练指引、profiling 和精度方法。复核当前正文 hash 后写来源锁，更新 catalog 和索引，再验证本机安装。已在运行的任务保留自己的固定版本，不因 Wiki 更新自动替换依赖。

Release/roadmap 非 PR 内容由维护 Agent 沿官方入口核查并更新版本解释和链接，不宣称 CLI 已对所有发布页和 discussion 做后台自动全量爬取。保留原文中的 benchmark 条件和硬件仍需按问题阅读，不能把历史性能数字当现场预期。

## 本轮实际迁移与未决边界

配置从 activation checkpoint policy 构建器转为 `activation_remat` dataclass；Linear/MoE 包、统一 attention/feed_forward 字段、RL service/ActorSystem 目录同时迁移。Graph/validation 共用 pool、逐组 replay、惰性预处理、PP loss kwargs 和首个 WGRAD 输出 dtype 都影响调用者与数值；不能仅替换来源 SHA。

当前主干已有 DeepEP v2 ElasticBuffer，不等于具体 deferred-epilogue PR #5263 已合入。此次 API核对的 #5263 head为 `d5e59c25e0900889fe19c2c3c7120273719c4373`，#4760 head为 `6ec06994290d0ceed8797638890cd9d21b965e9f`，两者均未merge；PR完整讨论与变动覆盖仍由各自采集记录表达。PP capture 的3项/4项输入结构不一致见[编译专题](../topics/compile-fusion-and-communication.md)，在解决与验证前不将新增 Graph 测试当作该引擎组合验收。

## 固定证据与使用边界

本页以官方主线 `a242475253433725f10f39c18f5ccbfdf188e097` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/README.md)
- [RELEASE.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/RELEASE.md)
- [assets/version.txt](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/assets/version.txt)
- [pyproject.toml](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/pyproject.toml)
- [torchtitan_recipes/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan_recipes/README.md)
- [torchtitan/config/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/config/README.md)
- [tests/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/tests/README.md)

- [PR #4760：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-4760.md)
- [PR #5033：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5033.md)
- [PR #5101：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5101.md)
- [PR #5107：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5107.md)
- [PR #5137：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5137.md)
- [PR #5250：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5250.md)
- [PR #5263：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5263.md)
- [PR #5268：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5268.md)
- [PR #5277：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5277.md)
- [PR #5280：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5280.md)
- [PR #5288：描述、review、评论及 diff](../../upstream/prs/pytorch--torchtitan/PR-5288.md)

## 本次补充的实现与测试依据

- [torchtitan/distributed/activation_remat.py](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/distributed/activation_remat.py)
- [torchtitan/rl/actors/monarch/README.md](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/torchtitan/rl/actors/monarch/README.md)
