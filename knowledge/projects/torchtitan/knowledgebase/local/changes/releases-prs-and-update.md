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
reviewed_on: '2026-11-04'
retrieved_on: '2026-11-04'
coverage: Curated source chains and official evidence at a fixed main commit; not all models, backends
  or HCU runtime validated.
sources:
- source: pytorch-torchtitan
  path: README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 85a02ce07f786fac33c3d2cda4e9b4fa460b0b68e8308ddfda5ddd2c0f9fdf13
- source: pytorch-torchtitan
  path: RELEASE.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 25602fde9bc0d1742bea6e1072b69db8565f4c37168b49b4a65b017f2d6b657b
- source: pytorch-torchtitan
  path: assets/version.txt
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 998f6b887ed7a6ef44e84210d0237b715bed42ea7254f48dc418afec0a484103
- source: pytorch-torchtitan
  path: pyproject.toml
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 4c8bd1c4a4c82eaea345ccb97abf671a1e59faf92df2d9fa147ce21c5e7fe780
- source: pytorch-torchtitan
  path: torchtitan_recipes/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 80bf0cdce6473544775bf13189368107b72642a97efb075a9486e77a21ecbe1c
- source: pytorch-torchtitan
  path: torchtitan/config/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: e62e3776a4dd1c2179b3643d9e611f5a6f53fc972ac16de4588ee96a99a06b9b
- source: pytorch-torchtitan
  path: tests/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 73f9a9597a0aaeef657c103ec1cc544375c0e9229f49a9a50abcd8d3a02af248
- source: pytorch-torchtitan
  path: torchtitan/distributed/activation_remat.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 4e935605e29f904ad5c5bef1036e265021f42c334a7a17c6d01083040dffc5a7
- source: pytorch-torchtitan
  path: torchtitan/rl/actors/monarch/README.md
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 3b46f79840dec9f3efd25319247fe259c0009daeec74bf381d06c483ddea8b09
- source: pytorch-torchtitan
  path: torchtitan/config/configs.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 3465866709813651cc91114c4a006a5cc3c05d6069e9f04200e68d10c91c3659
- source: pytorch-torchtitan
  path: torchtitan/training_engine.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: 2ffe06874d3a03ccc91d407f1bc91d5f2beaa9c746738dd3a3646f1c800a798f
- source: pytorch-torchtitan
  path: torchtitan/distributed/accelerator_graph.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: dec500ca70df82c8c8388b41e49970cd9dbbdd2a1c287217c4783827b576e9d5
- source: pytorch-torchtitan
  path: torchtitan/rl/trainer/trainer.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: f52d1d78a769b06bc511dc638486626592d0f0bdbd249d14a2f8df4107d0c3b3
- source: pytorch-torchtitan
  path: torchtitan/rl/generator/generator.py
  commit: 485c065cb248863bf2e2c65588becd6d7a8bcf83
  sha256: fe3ccd0288aa613d11234607fa24e91e98953015dd75a49657da0b4c7dd56b01

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
| 源码 | main 的固定提交 `485c065cb248863bf2e2c65588becd6d7a8bcf83`；全仓路径/对象清单 | 全部文件已逐行精读或硬件验证 |
| 作者专题 | 15 页总览、目录、安装运行测试、训练/数值、并行/显存、编译通信、MoE/量化、profile、恢复、RL 与 3 个案例 | 每个模型/后端均已形成完整专题 |
| 官方原文 | 当前来源锁、文档 ledger 与全仓路径清单中的训练教程/README | 图表、外链或依赖工程已全部离线复制 |
| PR | 已保留的重要历史 PR 与本次增量窗口；完成范围以独立 PR ledger 为准 | 历史 PR 全量采集或全部案例精读 |
| PR 证据 | body、普通/行内评论、顶层 review 状态与正文、文件/patch、固定 base/head | 已 merged 等于已 release；作者实验等于本任务实测 |
| 运行 | 本轮做知识/搜索/更新与项目离线检查 | TorchTitan 已在 HCU 跑通 |

目录和 PR 分页已经完成的范围，由各自 ledger 表达；源码路径尚未精读、PR 尚未形成解释，不通过伪造复核回执改成已验证。本页统计是这次补充时的快照，后续更新以来源清单为准。

## Release 不等于 main 的版本文件

2026-11-04 官方 Releases API 快照列出最新非预发布 [v0.4.0](https://github.com/pytorch/torchtitan/releases/tag/v0.4.0)，发布于 2026-10-28，target 为 `release/0.4`；v0.3.0（2026-09-03）属于此前发布。本次固定 main 的 `assets/version.txt` 仍为 `0.2.2`；应分别保存 tag、commit、包版本和依赖，不能根据一个字符串断言主线退回旧功能，也不把 main 所有改动自动归给 v0.4.0。

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
| #5107、#5268 | 历史采集为 merged | RL 权重同步案例 | 原 CPU mirror 已被新主线移除；历史 H100 数字不覆盖当前 transport/load mode |
| #4760 | 2026-11-04 API 核对 closed、merged；2026-10-19 合入 | PR 原文和当前 CP/MLA 消费者 | 通信压缩/打包已进入主线；BF16 梯度累积顺序与 native checkpoint key 变化仍须验证 |
| #5263 | 2026-11-04 API 核对仍 open、未 merge | 编译通信专题及 PR 原文 | DeepEP 新 API 与模型限制，deferred counts 不代表消除 CPU 等待 |

上表状态是采集时观察，不是永久结论。PR review 的修改意见、讨论中的失败与当前 patch 都保留；不要只读标题或作者最初的收益描述。

[#4760](../../upstream/prs/pytorch--torchtitan/PR-4760.md) 当前固定 head 为 `5018b40a5547d51193e157ff3d61cad3cb20c22e`、base 为 `2fa29617b8b17cb80b5b1b7a4c4cfaa5077b1cb8`，已合入。K/V all-gather 路线先传归一化压缩 KV latent 与 headless key，再本地 `wkv_b` 展开；Ulysses 输入合并 Q 与 packed KV，仍有一次 all-to-all 和一次 all-gather，输出 head→token 还需 all-to-all。它降低通信量，也改变投影/归约位置；作者固定 BF16 比较首步 logits/loss 相同但梯度不同，后续更新与 loss 并非 bitwise 等价，未证明真实数据收敛。

PR head 的 fused-MLA+CP 拒绝及当时 vLLM MLA/测试禁用是该版本边界；当前 main 已有独立 compressed-cache 消费者，不能用旧 PR 限制覆盖新实现。native checkpoint 的 `wkv_b` 移入 `attention.inner_attention`，旧 native key 不再自动重映射；HF adapter 兼容与旧 native 恢复是两件事。历史 H100 吞吐与禁用测试都不构成本次 HCU 验收。

## 搜索、追代码与更新

```bash
# 从项目目录执行；先跨知识库搜，再按明确引擎范围缩小。
hcu-trainflow wiki-search "TorchTitan 梯度累积" --project .
hcu-trainflow wiki-search "weight sync" --engine torchtitan --project .
hcu-trainflow wiki-search-pr "attention residual" --engine torchtitan
hcu-trainflow wiki-pr pytorch/torchtitan 5033
hcu-trainflow wiki-code pytorch/torchtitan 485c065cb248863bf2e2c65588becd6d7a8bcf83 torchtitan/models/common/linear/linear.py

# 定向更新；max 只是单批上限，存在 pending 时继续相应阶段。
hcu-trainflow wiki-update . pytorch-torchtitan --max-documents 100 --max-prs 50
```

普通检索只写私有缓存。Wiki update Skill 先看权限/新鲜度和完整文件树，再处理文档新增/变更、PR 讨论与源码差异；按问题可补任意历史或尚未收录的 PR。新增模型文件即使不匹配当前 document globs 也能通过全树发现，随后决定是否扩大收录范围。

主线/PR 变化后同时复核同仓总览、专题、案例，以及 `maintenance.json` 关联的 Torch 原生训练指引、profiling 和精度方法。复核当前正文 hash 后写来源锁，更新 catalog 和索引，再验证本机安装。已在运行的任务保留自己的固定版本，不因 Wiki 更新自动替换依赖。

Release/roadmap 非 PR 内容由维护 Agent 沿官方入口核查并更新版本解释和链接，不宣称 CLI 已对所有发布页和 discussion 做后台自动全量爬取。保留原文中的 benchmark 条件和硬件仍需按问题阅读，不能把历史性能数字当现场预期。

## 本轮实际迁移与未决边界

本轮对固定主线逐页沿消费者核对：根 PrecisionConfig 与 preserve-dtype 参数贯穿 FSDP/export/RL transfer；LocalCompileConfig 取代列表；accelerator-graph 重命名保持 HIP 拒绝；PP prepare 的四项输入与 loss kwargs 缺口已在实现和 CPU 测试修复。FSDP partial backward/group cleanup、DistMuon child communicator、模型级 loss kwargs/CP、checkpoint exports/完成标记和 Cuspy 输出格式均有实际变化。

RL trainer 移除自有 CPU mirror，generator 增加 cpu_prefetch/gpu_fetch 并改为显式逐组 fetch、严格参数覆盖及失败全 rank 停机。旧 #5107/#5268 说明只作为机制历史与特定实验，当前接口详见专题和案例。WGRAD 核心/直接回归、Attention Residual override 未变，已在相应案例记录具体保留依据。

本轮 API/原件核对更正了旧 #4760 open 结论，当前为 merged；#5263 保持 open，head `d5e59c25e0900889fe19c2c3c7120273719c4373`、base `448b9c8be41abc7fcbd5ccc768242b8865d4347b`。后者仅为 opt-in shared-expert scheduling，默认关闭、仍等待 CPU counts，不支持由此宣称 compact training Graph 可用；作者验证为特定 H200 单机 BF16 EP8/TP/AC 矩阵，非 FP8/Dist-MoE/PP/CP/多机或收敛证明。上游 CI action_required 不等于通过。

本页读了这两项的当前状态/说明及固定 main 消费者，全部 PR 评论、review 和文件覆盖由主控独立 PR ledger 表达，不冒称已完成全窗口语义审阅。没有安装、构建或执行上游训练/设备测试。

## 固定证据与使用边界

本页以官方主线 `485c065cb248863bf2e2c65588becd6d7a8bcf83` 为源码基准。完成选定调用链与教程阅读；本轮没有安装或运行 TorchTitan，未在 HCU 验证。上游报告的测试与性能不等于本工程实测。

- [README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/README.md)
- [RELEASE.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/RELEASE.md)
- [assets/version.txt](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/assets/version.txt)
- [pyproject.toml](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/pyproject.toml)
- [torchtitan_recipes/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan_recipes/README.md)
- [torchtitan/config/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/README.md)
- [tests/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/tests/README.md)

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

- [torchtitan/distributed/activation_remat.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/activation_remat.py)
- [torchtitan/rl/actors/monarch/README.md](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/actors/monarch/README.md)

- [torchtitan/config/configs.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/config/configs.py)

- [torchtitan/training_engine.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/training_engine.py)

- [torchtitan/distributed/accelerator_graph.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/distributed/accelerator_graph.py)

- [torchtitan/rl/trainer/trainer.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/trainer/trainer.py)

- [torchtitan/rl/generator/generator.py](https://github.com/pytorch/torchtitan/blob/485c065cb248863bf2e2c65588becd6d7a8bcf83/torchtitan/rl/generator/generator.py)
