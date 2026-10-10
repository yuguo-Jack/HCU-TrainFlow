# 第三方依赖与安装

## 完整安装

系统 Python 3.10+、Git、Git LFS 和 HCU-Knowledge 读取权限是基础条件。`thirdparty/manifest.json` 锁定 TraceLens HCU fork、三个 Hygon 算子 Skill 的源仓以及必需的 HCU-Knowledge。第三方依赖本身只登记来源清单，不把完整 checkout 或 HCU-Knowledge 全量复制到本仓。本工程自带 Wiki 则提交实际站点知识、配方、测量及精选证据，见 [知识归属](knowledge-architecture.md)；凭据永不入仓。

在工程根目录执行（PowerShell）：

```powershell
git lfs install
python scripts/setup_trainflow.py --skills-dir "$HOME/.codex/skills"
```

完整安装依次检查/获取三个依赖，用当前系统 Python 安装 TrainFlow、TraceLens、HCU-Knowledge 包，获取受管知识 checkout 的 LFS 原件，知识库本机索引未就绪时调用其自身 bootstrap 恢复缓存/索引，doctor 验收后安装 **11 个 Skill**：六个 TrainFlow、三个 Hygon kernel、HCU knowledge search/update。安装脚本不安装 CUDA/DTK、训练 PyTorch、TE、cuDNN 或模型；这些由实际训练环境提供。

失败返回非零，`.work/setup/status.json` 记录已完成阶段与失败阶段；修复后重跑会复用依赖和当前索引。缺私有仓权限、原件、Python 依赖或可用索引时不能声称完整安装通过。仅有 checkout 不等于知识搜索就绪。Git 使用本人已保存凭据；权限需本人获得，安装器不复制其他人的账号或自动提交访问申请。

### 复用已有知识库

```powershell
python scripts/setup_trainflow.py --knowledge-root "D:/my-knowledge/HCU-Knowledge" --skills-dir "$HOME/.codex/skills" --replace
```

本机路径记录在忽略提交的 `thirdparty.local.json`。检查 Git 来源与工程入口，保留该独立知识库的当前提交、配置和内容；不 pull、不重置、不降级到 TrainFlow 清单版本、不复制原件。先由 doctor 检查可用性、index_current 与快照状态；当前外部索引就绪则直接复用，不重复 hash 全部历史原件。缺失、过期或处于 rollback 的索引才调用 bootstrap，后者仅恢复/校验当前 checkout 的本地证据与索引，不更新飞书、链接或源码知识。缺 LFS 原件时先在该知识库按其安装说明恢复，再重跑。

全新机器没有外部绑定时，知识 checkout 默认位于 `thirdparty/HCU-Knowledge`，使用清单中的固定提交。外部绑定的实际提交会出现在依赖状态与本机安装记录中，兼容性由实际 bootstrap/doctor/Skill 安装检查，不冒称与清单提交相同。搬家后重新指定真实路径。需要改回受管目录时，检查并删除自己的 `thirdparty.local.json` 绑定文件，再运行完整安装；不会替用户删除独立知识库。

HCU-Knowledge 贯穿环境适配、性能优化和扩 DP/容错，按问题查询；必需安装不意味着每一步都要重复搜索。安装两个知识库 Skill 不授予自动更新大知识库的权限，普通训练/检索/局部 Wiki 更新均不附带更新它。

### Skills、账号与升级

更新分为内容维护和本机同步，由更新 Skill 衔接完成：

1. **内容维护**：`$hcu-engine-wiki-skill-update` 检查官方/相关 HCU 工程变化，修订本仓 Wiki、受影响的 Skill、命令和解析器，完成对应复核与测试。
2. **本机同步**：仓库内容验证后，安装器将 Skill 及 references 复制到实际 Agent 的 Skills 目录，并写入目录绑定。`--replace` 允许替换已有的不同内容，本身不搜索上游、不修订知识，也不决定依赖升级。
3. **安装验收与清理**：替换期间暂存本次旧内容；全部目标的文件哈希和绑定匹配后，自动清理本次临时备份。复制或校验失败则保留备份和错误，修复后再同步。未确认状态的历史备份不由本次安装自动扫除。

完整安装已就绪、仅更新本仓六个 Skill 时，由 Agent 执行：

```powershell
python scripts/install_skills.py --target "$HOME/.codex/skills" --workflow-only --replace
```

首次安装用 setup_trainflow；手动拉取 TrainFlow 新版本后，重新运行 setup_trainflow 并加 `--replace`，以核对包、依赖和全部 11 个入口。算子或知识库 Skill 的源版本确有变化时按对应维护范围同步，不因本仓文档变化而升级其他项目。HCU-Knowledge 的内容更新仍需单独授权。

当前阶段入口是 `hcu-train-environment-check-and-adapt`、`hcu-train-optimize` 和 `hcu-train-scale-and-stability`。安装器只为较早安装保留过时目录的清理兼容，不安装旧名称或旧别名。两个 HCU 知识 Skill 的 `workspace.json` 绑定实际知识 checkout；完整复制其脚本和 references。完成后重新打开 Agent 会话。Linux 使用对应 Skills 路径。

六个 TrainFlow Skill 的安装目录各有 `workspace.json`，其中 `project_root` 指向本次安装使用的工程绝对路径；个人路径只写入安装目录，不写入仓库源文件。新会话从其他工作目录使用 Skill 时，先采用用户明确指定的项目或 `TRAINFLOW_PROJECT`，未指定时读取该绑定。绑定只用于定位项目，不设置或覆盖任务的 `TRAINFLOW_WORKSPACE`。工程搬家后从新位置运行安装器并加 `--replace`，校验新绑定成功后清理本次旧备份；两个 HCU 知识 Skill 的 `root` 继续独立指向知识 checkout。

飞书在线检索另外安装/配置 `lark-cli` 并用本人身份授权；浏览器辅助访问按需配置 `playwright-cli`。离线索引就绪不表示在线权限就绪，任务启动和使用在线来源时检查实际请求状态。Git、飞书和浏览器的身份分别管理。详细知识安装与权限规则见实际知识库的 `docs/installation.md`。

依赖目录有修改、来源不符或受管提交不符时，保留现场并报告，禁止 reset/clean。依赖升级须先评估、更新锁并回归；普通安装不会擅自追最新分支。外部知识库由其独立维护流程管理。

## 定向维护命令

```powershell
# 仅检查依赖 checkout 身份；不是完整安装验收
python scripts/bootstrap_thirdparty.py --status
# 只修复选定依赖
python scripts/bootstrap_thirdparty.py --only tracelens
# 完整环境已就绪后，更新 11 个 Skill
python scripts/install_skills.py --target "$HOME/.codex/skills" --replace
```

bootstrap 默认包含 HCU-Knowledge，但只负责 Git checkout；完整初始化用 setup_trainflow。维护者的 `install_skills.py --workflow-only` 仅刷新六个本仓 Skill，供隔离开发使用，不代表完整安装。旧 `--with-kernel-skills` 和 `--include-knowledge` 保留解析兼容，默认已经包含这些必需项。

完整 Skill 安装与 setup 复用外部索引使用相同验收：doctor 的 `local_ready`、`index_current` 均为 true，`snapshot_mode` 为 current。rollback 快照或不完整的 doctor 输出会阻止安装；先完成知识库自身的本机 bootstrap，再重试，不以可读旧索引冒称当前知识就绪。

TraceLens 默认稀疏检出完整运行代码、文档和根文件，减少示例 trace 下载；按需可扩展目录。旧 AMD 上游 checkout 迁移到 HCU fork 使用：

```bash
python scripts/bootstrap_thirdparty.py --only tracelens --migrate-origin
python -m pip install -e thirdparty/TraceLens
```

仅允许来源和基准提交均与清单匹配、工作树干净的迁移；保留 upstream remote。不同来源/提交或本地修改需先人工核对。TraceLens 可选 LLM/联网 extra 不会默认安装。

## TraceLens 的实际集成

```bash
hcu-trainflow --workspace .work/analysis tracelens-report examples/tracelens-trace.json --project . --rank 0
hcu-trainflow --workspace .work/analysis tracelens-collective '/private/traces/rank*.json' --project . --world-size 8
```

单 rank 支持 PyTorch JSON 与 `.json.gz`，保存 native CSV、stdout/stderr、请求参数及 `report.json`；报告记录输入哈希和锁定的 TraceLens 提交。输出总在 workspace 内的新目录，不覆盖旧结果。`generated` 只表示产生了非空报告，完整训练结论仍需稳态窗口、实际 process groups、shape 与上限模型。

集成采用固定 checkout 的上游 Python report API，在独立进程执行。HCU fork 已修复本机复现的 Windows CSV 字段上限导入问题，原生 CLI 也可使用；TrainFlow 继续复用报告 API，不做全局 monkey patch。缺依赖、运行失败、超时或空表均保留失败信息，不降级伪报成功。

未提供匹配的 `--gpu-arch-json` 时不选择内置 AMD/NV 架构峰值。JSON 格式参考锁定 TraceLens 的 PerfModel/arch 定义，参数必须来自实际 HCU 环境；TrainFlow 的非通信热点建模仍单独进行。多 rank 工具要求完整 `0..world_size-1` 文件；“每个并行域至少两个 rank”的采样契约不代表可以自动运行要求全 rank 的报告。

### 完整上游能力的入口

fork 保留原有模块、API 和全部 13 个 console 命令。TrainFlow 的两个快捷命令之外，还可直接使用原生工具：

| 需求 | 上游入口 |
| --- | --- |
| 优化前后报告对比 | `TraceLens_compare_perf_reports_pytorch` / `TraceDiff` |
| graph / 推理剖面 | `TraceLens_generate_perf_report_pytorch_inference` |
| trace 分段、报告索引 | `TraceLens_split_trace`、`TraceLens_trace_index` |
| kernel 源码定位 | `TraceLens_resolve_kernel_source` |
| roofline、算子模型与回放 | `PerfModel`、`EventReplay` Python API |
| JAX、rocprofv3、pftrace HIP/HSA、内存拷贝、Genesis | 对应原生 report 命令，参数和格式以该版本文档为准 |
| Agent 分析和扩展 | 上游 Agent 目录及 optional extras，按需要配置 |

它们不会被 TrainFlow 自动调用，也不自动继承任务权限/产物归档；执行时使用同一任务的私有输入输出目录并保存命令、源码版本与原始证据。全部 CLI 的 `--help` 已检查，但各功能的 HCU 数据识别、额外依赖与精度/模型仍需对应验证。rocprof/pftrace 解析能力不代表自动兼容 hipprof 或 XProf/XCompute。详见 fork 的 [能力与维护说明](https://github.com/yuguo-Jack/TraceLens/blob/hcu/docs/hcu-integration.md)。

## 更新与回退

1. TraceLens 同时查看 AMD 上游与 HCU fork 的差异、实际脚本/API；新版本可能修改报告字段、Skill 步骤和依赖。优先复用现有模块及扩展接口；需要核心修改时保留复现证据与回归。
2. 经复核修改 manifest 的固定 commit，然后只同步选定依赖；dirty checkout 会阻止覆盖。
3. TraceLens 重新安装同一 Python，跑合成报告及目标 trace；算子 Skill 重新校验，再显式安装替换。
4. 涉及 HCU-Knowledge 时按用户授权单独更新，使用它自己的安装/迁移/校验流程。
5. 提交清单、相关用法和验证记录；回退到旧清单后重新同步/安装。正在运行的训练任务继续保留原来的源码和环境快照。

网络不稳定可在诊断 Git 网络后重试，必要时使用 Git 的 HTTP/1.1 配置；不要为方便把第三方 checkout 改为不明来源或把认证写进 URL。

## 训练环境中的 HCU 库

TE、Flash-Train、HCU Primus Turbo、RCCL、rocSHMEM、DeepEP、UCCL、UltraEP、MoonEP等按实际模型和瓶颈选择；它们不是本地主控安装时统一替换的依赖。先查HCU大知识库，再核对活动分支与镜像ABI，必要时在任务隔离前缀/容器构建候选，保留旧制品。接口、验证与PR归属见[工程联动](../skills/hcu-train-optimize/references/hcu-library-integration.md)。
