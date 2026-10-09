# 第三方工程与版本

`manifest.json` 登记必需依赖、固定提交及 checkout 位置；源码、材料和本机状态被主仓忽略，避免把私有资料提交到公共 TrainFlow。

| ID | 默认目录 | 用途 |
| --- | --- | --- |
| `tracelens` | `TraceLens/` | HCU fork，保留上游模块与原生 CLI，TrainFlow 复用报告 API |
| `cuda-optimized-skill` | `cuda-optimized-skill/` | 三个 Hygon HIP/Triton Skill、脚本和参考资料 |
| `hcu-knowledge` | `HCU-Knowledge/` | 必需 HCU 大领域知识库，贯穿三个阶段；当前需读取权限 |

从工程根执行 `python scripts/setup_trainflow.py --skills-dir <Agent技能目录>` 完成 Python 依赖、知识库 LFS/本机索引和 11 个 Skill 的安装。已有独立知识库可加 `--knowledge-root <实际目录>`，通过忽略提交的 `thirdparty.local.json` 复用，不重复复制、不拉取其新资料。

`bootstrap_thirdparty.py` 默认拉全部必需 checkout，`--only ID` 仅用于定向维护，`--status` 仅检查 Git 身份。Git 就绪不等于可查询；完整安装还需知识 bootstrap/doctor。没有权限或索引失败时报告未完成。任何依赖本地修改和来源差异都保留，不 reset/clean。

受管目录固定清单提交；独立知识库保留实际提交并做本机可用性验收。TraceLens 稀疏检出完整代码/文档，按需扩展；旧上游迁移到 fork、Skills 替换备份、飞书权限和升级步骤见 [安装指南](../docs/integrations.md)。训练引擎 fork/PR 开发继续使用任务独立 checkout，不能借用知识库源码缓存。
