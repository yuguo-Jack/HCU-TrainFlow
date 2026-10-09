# 第三方依赖与安装

## 统一目录与可复现版本

`thirdparty/manifest.json` 是本版本测试的依赖清单。执行 bootstrap 后建立 TraceLens、cuda-optimized-skill 的 Git checkout，HCU-Knowledge 可单独启用。主仓不会递归提交其源码、数据、凭据或运行缓存；Git clone 本仓后还需执行下面的安装步骤。

```bash
python -m pip install -e ".[test]"
python scripts/bootstrap_thirdparty.py
python -m pip install -e thirdparty/TraceLens
python scripts/bootstrap_thirdparty.py --status
```

使用当前系统 Python。TraceLens 的分析依赖（pandas、openpyxl 等）由其包声明安装；不需要在本地主控安装 CUDA、DTK、PyTorch 训练环境、TE 或 cuDNN。其可选 LLM/联网分析 extra 未启用，集成只调用本地报告 API。

TraceLens checkout 默认展开完整运行代码、文档和根目录文件，减少示例 trace 的下载；源码提交仍固定，需要时可扩展稀疏目录。核心包和局部 Wiki 可先独立使用，TraceLens 子命令需要完成上面的 bootstrap 与依赖安装。

### 从原上游 checkout 迁到 HCU fork

现在锁定 [yuguo-Jack/TraceLens](https://github.com/yuguo-Jack/TraceLens) 的 `hcu` 分支提交，并记录 AMD 上游基准。已经用 v0.2.0 拉过依赖的用户执行：

```bash
python scripts/bootstrap_thirdparty.py --only tracelens --migrate-origin
python -m pip install -e thirdparty/TraceLens
```

迁移仅接受清单中登记的原上游 URL 与基准提交，且工作树必须干净；保留 `upstream` remote 后将 `origin` 改为 fork，再检出锁定提交。来源、HEAD、已有 upstream 不匹配或存在修改时会停止该依赖的迁移，保留现场。`--status` 始终只读；默认 bootstrap 不擅自修改 origin。新安装直接拉 fork，无需迁移参数。

## 三个算子 Skill

在 PowerShell 中一次安装六个 TrainFlow Skill（一个统一入口、三个阶段和两个 Wiki） 和三个 Hygon 算子 Skill：

```powershell
python scripts/install_skills.py --with-kernel-skills --target "$HOME/.codex/skills"
$env:TRAINFLOW_PROJECT = (Get-Location).Path
$env:TRAINFLOW_WORKSPACE = "D:/trainflow-work/my-task"
```

Linux 可将目标改为 `~/.codex/skills`。安装器检查完整源目录，连同脚本、指令资料和 references 一起复制，仅选择 Hygon 的三个 Skill，不安装 CUDA 优化 Skill。已有不同版本默认报错；确认替换时加 `--replace`，原目录备份在 Skill 扫描目录之外。

未安装到 Agent 系统目录时，也可按明确路径读取 `thirdparty/cuda-optimized-skill/skills/<name>/SKILL.md`，但自动发现通常需要安装。优化 Skill 会先检查安装状态，缺失时给出本指南入口，不假定别人机器上已有这些能力。

## 可选 HCU-Knowledge

仓库当前需要读取权限。公共工作流和局部官方 Wiki 可独立运行；认证缺口不伪装成“知识库为空”。启用时：

```bash
python scripts/bootstrap_thirdparty.py --only hcu-knowledge
```

随后阅读 `thirdparty/HCU-Knowledge/INSTALL.md` 与 `docs/installation.md`，按该版本要求配置本机依赖、Git LFS 原件、workspace 和 bootstrap。知识库自身安装命令会生成机器绑定文件；不要用普通目录复制取代它。例如已完成知识库配置后：

```powershell
python -X utf8 thirdparty/HCU-Knowledge/tools/setup_workspace.py install-skills --skills-dir "$HOME/.codex/skills"
```

已有可用 HCU-Knowledge 时保留其绑定即可，不执行上面的替换安装。知识库本地索引重建只处理当前 checkout，不表示已更新飞书、原始链接和上游仓库。训练查询不触发大知识库更新，也不会因本工程刷新官方 Wiki 而自动更新大知识库。

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
