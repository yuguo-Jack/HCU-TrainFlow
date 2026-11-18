# 排障的知识检索与源码查证

诊断指南的参考复核日期：2026-11-18（HCU-Knowledge `a3a5be59183d564e54897e8a653604be8c91d505` / `v0.6.3`）。以下 ID/路径属于独立的 **HCU-Knowledge**，不是本 Skill 安装目录；按 `$hcu-knowledge-search` 的 `workspace.json` 找实际 KB_ROOT。路径只是导航，当前部署版本须另核对。不复制内部原始材料到公开 Skill，也不因查询触发全库更新。未变的手册/固定测试继续复用，其原硬件验证日期不因本次阅读而刷新。

## 按问题查证

1. 提取最小检索条件：现象/首个错误、库/符号、gfx/DTK、进程模型、phase、shape/dtype、最后正常版本。先查同环境已验证证据，避免重复搜索同一问题。
2. 用 `$hcu-knowledge-search` 查询 HCU 机制和案例，再读命中正文/原件及版本。复杂问题分为数据/框架、通信/runtime、设备/系统几个机制查询；不要只搜整段日志。
3. 无答案、相互矛盾或版本落后时，按知识搜索 Skill 的 `search-pr` → `read-pr` → `read-pr-code` 追已收录或尚未收录的 PR/MR。读描述、review、最终改动、测试和合入状态；本地无命中不表示上游没有修复。
4. 官方训练引擎问题可联用 `$hcu-trainflow-wiki-search`。仍不足时主动搜索匹配版本的官方文档、公开 issue/PR 和工程经验；外部经验用于生成可验证假设，结论回到 HCU 实际实现。公开查询只带通用错误/符号，私有源码、节点地址和任务数据不外传。
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
| 调试与异构转储 | DTK 26.10 hipgdb `bb00bc7bb9d80da7cc80e8f5`；hipprof `b5019dc7bc37f3ca23f13f12`；runtime-doc `926ac2b821c8b752dcf173f5`、`3f71ac460de6dcc823871b08` | 先查匹配手册和本机帮助；hipgdb 手册明确不支持 coredump 调试，hipprof 的转储接口曾移除再恢复；旧泄漏检测、Graph trace 和退出导出各有版本限制 |
| 泄漏与 allocator | `4a472816b1d9de7d731896a2`；`pytorch-memory-stream-graph-lifecycle` | DTK 内存趋势/泄漏工具；allocated/reserved、跨流事件、Graph RNG 保留对象和图池的不同生命周期；普通 checkpoint、IPC 和固定 VA 恢复分别核对 |
| 数值偏差 | `dcu_probe-engineering-handbook`、`hcuprobe-hook-tensor-lifecycle`、`hcuprobe-cross-rank-first-diff` | 采集当时的 tensor、跨 rank 首次分歧、空匹配/缺 rank 的误判 |
| RL 阶段阻塞/同步/恢复 | `verl-ppo-grpo-worker-chain`、`verl-weight-sync-checkpoint-lifecycle` | 按实际 worker/可选角色、权重传输 backend、sleep/wake 内存和保存完成状态追因，不只看 step 标签 |
| 异步通信/graph 完成 | `torchcomms-async-functional-watchdog`、`pytorch-memory-stream-graph-lifecycle` | host 返回、设备完成、消费依赖和 watchdog 时间不同，按实际后端分支检查 |
| 低精度通信或 EP 生命周期 | `aiter-int8-fp8-collective-contract`、`rocshmem-hcu-engineering`、`moonep-g1-contributor-capacity`、`ultraep-replica-gradient-lifecycle` | 位复制/数值 SUM/量化分别判读；provider、父仓固定依赖、plan/generation、清零副作用和真实消费 join |
| 编译后同步、Graph 或版本回归 | `dcc-engineering-handbook`、`galaxy-engineering-handbook`、`triton-hcu-mls-pipeline-contract`、`tilelang-hcu-pass-ownership` | 编译器前端/所选后端/runtime/制品分开；memory scope 宏、同步 owner、event capture 限制及 launch ABI |
| 性能/驻留与采集副作用 | `xprof-xcompute-workflow`、`hipprof-2610-metrics`、`infra-resource-critical-path` | 资源/依赖、指标层级和 replay 扰动，防止把采集伪影当硬件瓶颈 |
| 容错和健康重入 | `cluster-manager-engineering-handbook`、`cluster-fault-taint-recovery`、`cluster-preflight-evidence-lifecycle`，以及 `knowledge/projects/primus-safe/` | 区分预检、训练恢复器和 K8s；MPI rank/GPU slots、停止失败、清理未确认和节点重入各自核销；SaFE 的任务、通知、RayJob 重试另验 |

当前来源的差异决定怎样查证，不能只按项目名取最新文件：

- **RCCL**：本次固定 DTK `develop@bafb6ac5f5f369afe5abf2d4e9b3ed8314044300`，HSW 跨 host P2P 已回到拓扑检查并尊重用户 level/disable 约束，P2P channel 上界与 crossNic 搜索也有变化；旧“HSW 总绕过检查”不能用于诊断。双连接预连接、融合拓扑、实际连接与 Graph 分支仍分别采证。此前 MR153 的 PCIe 清零候选不因这些拓扑改动而视为修复，采用前核对该 MR 的实际状态与固定树；不能用旧 811 表标签或独立峰值拼接本次实测。
- **Cluster Manager**：固定 `main@ea2a1d1e95f3c524bcf1fdf74d382ec351ea8e3b` 的训练恢复器仍位于 `hcu-training-reliability/`，import 为 `cluster_manager`，命令为 `hcu-cluster-inspect`；`launcher/container_ssh.py` 和 Docker/MPI launcher 已使用独立容器 Ed25519、受管授权块与 known_hosts，并传播 `clush -S` 失败。替补容器复用同一准备链，coordinator↔peer 探测不等于全连接训练验证。可选 NRE 工程根为 `nvidia_resiliency_ext/`，适配 import 仍为 `hcu_resiliency_ext`；父 gitlink `0f034639db696ecd4b43311c63f7a0e693aa4d75`、包装器 `hcu-resiliency-ext==0.1.0` 与 `nvidia-resiliency-ext>=0.7,<0.8` 声明、组合 wheel 实际版本各自核对。跳过 CUPTI 扩展不证明其余 CUDA 依赖均已禁用；telemetry 的显式开关优先级、依赖回退和真实接管另验。`controller/distributed_job_manager.py::_stop_training` 与此前保留原件字节一致，停止失败仍可能推进 STARTING，不能由 SSH 修订推断恢复已安全。详细入口为 `cluster-manager-engineering-handbook`、`cluster-stack-resiliency-analysis`；接入门槛见项目 `docs/operations.md`“衔接站点恢复器”。
- **Primus-SaFE**：固定内部主线 `57339bb48281e599e358fda4733bf209faa06994`，沿 `primus-ray-shared-retry-budget` 与 `SaFE/job-manager/pkg/syncer/ray_success_review.go` 检查成功复核：当前 UID/dispatch/最终 native attempt、Sealed Session、无 pendingTransaction、version=1、complete=true、submission/cluster/nativeRetries 一致及布尔 hasFault。CRD 不存在、Session 待排干和 API 错误不同；确认故障的 fallback 仍扣共享持久预算，不能额外获赠一轮。`docs/examples/{pytorchjob,rayjob}/` 的 `maxRetry:0`、空镜像归档目录的跳过语义与已有 release 升级分别核对，不能把示例或脚本运行成功当部署/恢复通过。
- **Probe**：当前公开主源是 `HYGON-AI/hcu_probe-das` 的 `26.2.0-dev@1cf9e49686a2d3f61aca42ef110fdd1ac9660ffa`；内部 `b8dddb57debbe31fb9a0ba46f7429de9c28014a5` 保留历史机制证据。distribution 为 `hcu-probe`，import/CLI 为 `hcuprobe`，入口为 `hcuprobe.cli:main`。公开 `tools/compare.py` 的旧 namespace 已修复，precheck extra 已登记实际依赖；不再沿用旧包装器失效或 extra 缺失结论。核心 hook/service/collector/compare 的对应固定文件未变，异步快照、flush、缺失实体张量和空匹配限制继续保留。入口修复不等于所有 backend 或现场采集通过。
- **PyTorch**：常用 2.13 维护线与 2.16 专项线分开。本次 2.13 masked-FA 固定证据为 `bd0bddedc542c4813382e94aef3744b6fc6a2476`，应读实际 attention 分派、SDP 条件与对应测试；版本登记或源码存在不代表所有 mask/精度/反向路径均已实测。既有 2.16 专项 `main@c55e238d4b1c03e04d2b37c4642ed10d0117b929` 的 Graph RNG、retained 对象与 allocator 恢复边界继续保留，不能套到 2.13 wheel。`USE_ROCM` 对指定原地址的 expandable segment 恢复明确拒绝；测试跳过不是 HCU 功能通过，按项目 `docs/training-state-validation.md` 补受影响验证。

上述提交**不是工作流依赖锁或推荐部署版本**；现场另行固定。大库已记录的未合入 PR、历史快照与已部署的自定义分支分别检查；本次只有文档/源码审阅，没有 HCU 调试、采集或恢复实测。

## 公开官方补充

- [PyTorch distributed 调试](https://docs.pytorch.org/docs/stable/distributed.html)：组/成员、调试日志和 Gloo `monitored_barrier`。先核对 HCU PyTorch 实际实现，不能直接把 stable 文档所有能力当成本机已有。
- [PyTorch memory snapshot](https://docs.pytorch.org/docs/stable/torch_cuda_memory.html)：追分配生命周期；它只能看到 allocator 管理的内存，库外直接分配需另查。HCU 构建能否使用相关 API/可视化由现场确认。
- [Linux cgroup v2](https://docs.kernel.org/admin-guide/cgroup-v2.html)：主机/容器限额与 memory.events；读取实际进程所属层级和时间增量。v1 环境用对应内核文档，不照搬 v2 路径。
- [Cluster Manager 固定源码](https://github.com/HYGON-AI/cluster-manager-das/tree/ea2a1d1e95f3c524bcf1fdf74d382ec351ea8e3b)：按部署子工程追控制与恢复；用现场版本比较该参考快照。
- [Probe 固定源码](https://github.com/HYGON-AI/hcu_probe-das/tree/1cf9e49686a2d3f61aca42ef110fdd1ac9660ffa)：核对实际 wheel、CLI 分派、配置与采集/比较消费者，旧命名文档不覆盖当前实现。

## 如何维护这些方法

更新 Skill 同时检查：工具帮助/版本、信号和变量语义、日志字段、组与 rank 映射、源码路径、采集副作用、异常/空结果、恢复状态和验证边界。已登记上游用 `knowledge/maintenance.json` 联动；HCU 私有依赖未登记时从任务版本和大库入口主动补查。不要仅因为某个脚本仍 exit0 就保留旧解析结论。

将已核对来源、未能核对的现场接口及必要验证写入更新记录；有真实环境后补现场用例，不用离线指南替代实测。指南变更还应复核环境适配与性能 Skill 的异常路由、主控交接和本机 Skill 同步。

性能、适配和故障方法的公开参考对照见项目 `docs/practices/performance-methods.md`；BBuf 的复现/二分思路按训练状态和 HCU 工具改写，不直接采用其推理 HTTP/CUDA 调试命令。
