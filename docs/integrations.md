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

TraceLens checkout 默认仅展开运行代码、how-to 和根目录文件，减少示例 trace 的下载；源码提交仍固定，需要时可扩展稀疏目录。核心包和局部 Wiki 可先独立使用，TraceLens 子命令需要完成上面的 bootstrap 与依赖安装。

## 三个算子 Skill

在 PowerShell 中一次安装五个 TrainFlow Skill 和三个 Hygon 算子 Skill：

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

集成采用固定 checkout 的官方 Python report API，在独立进程执行。这样也避开当前上游 CLI 在 Windows 导入辅助模块时的 `csv.field_size_limit(sys.maxsize)` 溢出；未修改其源码或全局 monkey patch。缺依赖、运行失败、超时或空表均保留失败信息，不降级伪报成功。

未提供匹配的 `--gpu-arch-json` 时不选择内置 AMD/NV 架构峰值。JSON 格式参考锁定 TraceLens 的 PerfModel/arch 定义，参数必须来自实际 HCU 环境；TrainFlow 的非通信热点建模仍单独进行。多 rank 工具要求完整 `0..world_size-1` 文件；“每个并行域至少两个 rank”的采样契约不代表可以自动运行要求全 rank 的报告。

## 更新与回退

1. 查看依赖上游差异与实际脚本/API；新版本可能修改报告字段、Skill 步骤和依赖。
2. 经复核修改 manifest 的固定 commit，然后只同步选定依赖；dirty checkout 会阻止覆盖。
3. TraceLens 重新安装同一 Python，跑合成报告及目标 trace；算子 Skill 重新校验，再显式安装替换。
4. 涉及 HCU-Knowledge 时按用户授权单独更新，使用它自己的安装/迁移/校验流程。
5. 提交清单、相关用法和验证记录；回退到旧清单后重新同步/安装。正在运行的训练任务继续保留原来的源码和环境快照。

网络不稳定可在诊断 Git 网络后重试，必要时使用 Git 的 HTTP/1.1 配置；不要为方便把第三方 checkout 改为不明来源或把认证写进 URL。
