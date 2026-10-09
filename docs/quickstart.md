# 安装与使用

## 依赖

Python 3.10+、SQLite FTS5、PyYAML（安装本包时拉取）。开发测试需 pytest。Git 用于源码与版本管理，SSH/scp、Docker、kubectl、Slurm 客户端只在使用相应执行方式时需要。TraceLens 通过固定 checkout 和本机 Python 的报告 API 集成，安装三个算子 Skill 及可选 HCU-Knowledge 的步骤见 [第三方集成](integrations.md)。HCU 训练依赖由目标环境提供，本包不下载 PyTorch/DTK/模型。

```bash
python -m pip install -e ".[test]"
python scripts/validate_knowledge.py
python -m pytest -q
hcu-trainflow --workspace .work/local init
hcu-trainflow demo .work/demo-001
```

查看 demo 返回的 HTML 报告：含 step、loss、梯度与显存合成曲线，以及监测故障记录。合成证据只验证程序逻辑。

## 创建任务

从 `examples/task.json` 复制到私有目录并修改。先明确只分析、只诊断还是完整推进。

```bash
hcu-trainflow --workspace /private/task-a task-create /private/task-a/task.json
hcu-trainflow --workspace /private/task-a task-show example-analysis
```

CLI 所有输出默认 JSON。0 表示命令正常完成；2 表示 fail/incomplete/partial/attention 等需要处理的结果；1 为输入/运行错误；130 为中断。source collected、bridge returned、脚本 exit0 不表示模型质量通过，必须看具体状态字段。

报告 envelope 必须包含当前 task-show 返回的 context 哈希、status、evidence 数组；pass 还要求 executed>0、没有 failures/required_missing。evidence 是 `artifact-add` 返回的对象 ID。报告由负责 Agent/人根据原始证据撰写；程序验证完整性，不声称能证明任意手填结论真实。

## 常用命令组

| 目的 | 命令 |
|---|---|
| 任务与证据 | task-create/show/context/transition、artifact-add/read、report-add |
| 资源与执行 | lease-acquire/renew/release、command-plan/run、operation-reconcile |
| 源码传输 | source-snapshot/materialize/bundle/receive |
| 多 Agent | assignment-add/return、inbox、inbox-dispatch |
| 验收 | environment-check、proxy-check、iteration-check、quality-check |
| 分析 | profile-plan、profile-analyze、tracelens-report、tracelens-collective |
| 长训 | watch、heartbeat-check、events-export/import、monitor-report |
| Wiki | wiki-index/search/refresh/pr/review |
| 公开交付 | public-export |

参数以子命令 `--help` 为准。JSON 文件用 UTF-8；PowerShell 重定向可能带 BOM，读取器已兼容。远端命令避免把凭据放 argv/env 明文卡中，使用站点管理的认证设施。

## Skill 使用例

- `$hcu-train-prepare`：只检查分配的环境，按实际节点和设备生成缺项表。
- `$hcu-train-optimize`：只分析这些 ranks 的 trace，给热点、效率和下一步实验。
- `$hcu-train-operate`：诊断卡住，先保存全 rank 现场，不触发重启。
- `$hcu-engine-wiki-search`：查 EP overlap 与重算的版本限制。
- `$hcu-engine-wiki-update`：复核最新官方/生态源码，并同步受影响的用法。

第三方使用者自行配置私有工作区和资源；不要拷贝另一位用户的凭据或现场目录。

各输入字段和判定边界见 [JSON 契约](contracts.md)。
