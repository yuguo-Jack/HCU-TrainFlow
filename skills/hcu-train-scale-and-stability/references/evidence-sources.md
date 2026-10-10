# 排障的知识检索与源码查证

诊断指南的参考复核日期：2026-10-10。以下 ID/路径属于独立的 **HCU-Knowledge**，不是本 Skill 安装目录；按 `$hcu-knowledge-search` 的 `workspace.json` 找实际 KB_ROOT。路径只是导航，最新索引与当前部署版本须另核对。不复制内部原始材料到公开 Skill，也不因查询触发全库更新。

## 按问题查证

1. 提取最小检索条件：现象/首个错误、库/符号、gfx/DTK、进程模型、phase、shape/dtype、最后正常版本。先查同环境已验证证据，避免重复搜索同一问题。
2. 用 `$hcu-knowledge-search` 查询 HCU 机制和案例，再读命中正文/原件及版本。复杂问题分为数据/框架、通信/runtime、设备/系统几个机制查询；不要只搜整段日志。
3. 无答案、相互矛盾或版本落后时，按知识搜索 Skill 的 `search-pr` → `read-pr` → `read-pr-code` 追已收录或尚未收录的 PR/MR。读描述、review、最终改动、测试和合入状态；本地无命中不表示上游没有修复。
4. 官方训练引擎问题可联用 `$hcu-engine-wiki-search`。仍不足时主动搜索匹配版本的官方文档、公开 issue/PR 和工程经验；外部经验用于生成可验证假设，结论回到 HCU 实际实现。公开查询只带通用错误/符号，私有源码、节点地址和任务数据不外传。
5. 追到**实际加载制品对应的源码**：应用调用者 → 参数/分派 → 库/runtime → 测试。记录仓/分支、完整 SHA、submodule/build、路径/符号和实际二进制身份；最新源码只作比较，不能冒充现场实现。参考缓存与修改/提 PR 的开发 checkout 分开。
6. 每条候选经验写适用条件、支持/反证、与现场差异及最小验证。权限/网络/缺符号时保留缺口并请求所需帮助，不能以未读到替代已排除。按预算做能区分假设的实验；基本尝试无新证据则升级，而非继续堆命令。

调用示例（参数以安装的搜索 Skill 和 CLI 帮助为准）：

```text
python -X utf8 <KB_ROOT>/kb.py --root <KB_ROOT> search "RCCL 卡死 collective 参数"
python -X utf8 <KB_ROOT>/kb.py --root <KB_ROOT> read runtime-failure-triage
python -X utf8 <KB_ROOT>/kb.py --root <KB_ROOT> search-pr "graph proxy hang" --project rccl
```

默认搜索按 KB 配置联查飞书；显式离线时用 `--mode local`。返回摘要不是正文证据；`pending`/partial 材料仍可查阅，但适用范围和图片未解读项保持未知。

## HCU 入口与值得警惕的差异

| 问题 | 可搜的页面/原件 ID | 用于什么判断 |
|---|---|---|
| hang / VMFault / runtime 日志 | `runtime-failure-triage`；原件 `a526650defbae2e2ebb7d723`、`5bf3fcb071189001775383fe` | 数据/collective 契约和首个失败 rank；栈、信号及设备错误的版本边界 |
| collective 少下发 | `19468d24f21d7c717710057b`《DCU卡死hang问题确认及分析指引》 | comm/rank/opCount 的日志定位；旧脚本需审查，不能把局部指针跨进程合并 |
| HCU RCCL 调度/proxy/SM Free | `rccl-engineering-handbook`、`rccl-sm-free-p2p`、`rccl-test-engineering-handbook` | 已加载的 HCU 实现、正确性/带宽口径、graph/callback/PXN 条件；默认开关不等于实际启用 |
| 调试与异构转储 | DTK 26.10 hipgdb `bb00bc7bb9d80da7cc80e8f5`；hipprof `b5019dc7bc37f3ca23f13f12`；旧转储示例 `49152d9ec8bc9495a62aa0ce` | 先查匹配手册和本机帮助；hipprof 的转储接口曾移除再恢复，旧路径变量有缺陷记录 |
| 泄漏与 allocator | `4a472816b1d9de7d731896a2`；`pytorch-memory-stream-graph-lifecycle` | DTK 内存趋势/泄漏工具；allocated/reserved、跨流事件和 graph 池的不同生命周期 |
| 数值偏差 | `dcu_probe-engineering-handbook`、`hcuprobe-hook-tensor-lifecycle`、`hcuprobe-cross-rank-first-diff` | 采集当时的 tensor、跨 rank 首次分歧、空匹配/缺 rank 的误判 |
| 容错和健康重入 | `cluster-manager-engineering-handbook`、`cluster-fault-taint-recovery`，以及 `knowledge/projects/primus-safe/` | 区分子工程/部署入口，检测、处置、重建和解除隔离的独立条件 |

例：本次 KB 中 RCCL 总览对应 `80b1215701a8cb657c9ec5f2aab37cd8a7086727`，Cluster Manager 主题对应 `026452b298814065b317273c28cc6d707567c20c`，hcuprobe 对应 `b8dddb57debbe31fb9a0ba46f7429de9c28014a5`。这些用于说明参考快照，**不是工作流依赖锁或推荐部署版本**；现场另行固定。大库已记录的未合入 PR 与已部署的自定义分支分别检查。

## 公开官方补充

- [PyTorch distributed 调试](https://docs.pytorch.org/docs/stable/distributed.html)：组/成员、调试日志和 Gloo `monitored_barrier`。先核对 HCU PyTorch 实际实现，不能直接把 stable 文档所有能力当成本机已有。
- [PyTorch memory snapshot](https://docs.pytorch.org/docs/stable/torch_cuda_memory.html)：追分配生命周期；它只能看到 allocator 管理的内存，库外直接分配需另查。HCU 构建能否使用相关 API/可视化由现场确认。
- [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)：主机/容器限额与 memory.events；读取实际进程所属层级和时间增量。v1 环境用对应内核文档，不照搬 v2 路径。
- [Cluster Manager 固定源码](https://github.com/HYGON-AI/cluster-manager-das/tree/026452b298814065b317273c28cc6d707567c20c)：按部署子工程追控制与恢复；用现场版本比较该参考快照。

## 如何维护这些方法

更新 Skill 同时检查：工具帮助/版本、信号和变量语义、日志字段、组与 rank 映射、源码路径、采集副作用、异常/空结果、恢复状态和验证边界。已登记上游用 `knowledge/maintenance.json` 联动；HCU 私有依赖未登记时从任务版本和大库入口主动补查。不要仅因为某个脚本仍 exit0 就保留旧解析结论。

将已核对来源、未能核对的现场接口及必要验证写入更新记录；有真实环境后补现场用例，不用离线指南替代实测。指南变更还应复核环境适配与性能 Skill 的异常路由、主控交接和本机 Skill 同步。
