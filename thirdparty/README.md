# 第三方工程与版本

`manifest.json` 登记来源、固定提交和本地位置。bootstrap 在本目录建立独立 Git checkout；源码本身被主仓忽略，公共提交仅含清单和集成代码。这样不会把私有知识库内容发布到本仓，也不会重复维护第三方源码副本。

| ID | 目录 | 用途 |
| --- | --- | --- |
| `tracelens` | `TraceLens/` | 已接入 TrainFlow 的 PyTorch trace 与全 rank collective 报告。 |
| `cuda-optimized-skill` | `cuda-optimized-skill/` | 三个 Hygon HIP/Triton 算子 Skill 的完整源码、脚本与参考文件。 |
| `hcu-knowledge` | `HCU-Knowledge/` | 可选大领域知识库；当前需仓库读取权限。 |

从工程根执行：

```bash
python scripts/bootstrap_thirdparty.py
python -m pip install -e thirdparty/TraceLens
python scripts/bootstrap_thirdparty.py --status
```

默认只拉前两个公开工程，不自动执行其安装脚本或安装模型/训练环境。目录已有修改或来源不匹配时保留现场并报告，绝不 reset/clean。同步的是清单中的提交，不是每次擅自升级 HEAD。网络或权限失败返回非零；解决 Git 认证后可用 `--only ID` 重试。

TraceLens 默认稀疏检出运行代码、how-to 和仓库根文件，避免下载其大量示例 trace。需要阅读更多上游目录可在该 checkout 中 `git sparse-checkout add <目录>`；不会改变锁定提交。

HCU-Knowledge 明确启用：

```bash
python scripts/bootstrap_thirdparty.py --only hcu-knowledge
```

使用自己的 Git 凭据；无需在本仓保存 token。拉取时跳过 Git LFS 原件下载，正文、索引构建和原件恢复按其安装说明执行。已有独立 HCU-Knowledge 可以继续使用，无须额外复制。仓库以后公开只改变访问权限，不需更换目录或 URL。

Skill 安装、知识库绑定、升级与 TraceLens 验证见 [依赖集成指南](../docs/integrations.md)。这些 checkout 用于工具/知识依赖；训练引擎 fork、PR 开发与运行快照仍放任务私有工作区。
