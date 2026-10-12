# 第三方工程与版本

`manifest.json` 登记必需与可选依赖、固定提交及 checkout 位置；源码、材料和本机状态被主仓忽略，避免把私有资料提交到公共 TrainFlow。

| ID | 默认目录 | 用途 |
| --- | --- | --- |
| `tracelens` | `TraceLens/` | HCU fork，保留上游模块与 CLI；接入报告、Graph、Roofline/效率、原生 Agent、HCU profiler，并按需在远端执行 EventReplay |
| `cuda-optimized-skill` | `cuda-optimized-skill/` | 三个 Hygon HIP/Triton Skill、脚本和参考资料 |
| `hcu-knowledge` | `HCU-Knowledge/` | 必需 HCU 大领域知识库，贯穿三个阶段；[GitHub 主仓](https://github.com/yuguo-Jack/HCU-Knowledge) / [内部 GitLab 镜像](http://42.228.13.241:10068/dcutoolkit/deeplearing/hcu-knowledge) |
| `kernelwiki` | `KernelWiki/` | 可选 NVIDIA 算子知识、PR 与源码参考，供算子 Skill 寻找优化思路 |

从工程根执行 `python scripts/setup_trainflow.py --skills-dir <Agent技能目录>` 完成 Python 依赖、知识库 LFS/本机索引和 11 个 Skill 的安装。已有独立知识库可加 `--knowledge-root <实际目录>`，通过忽略提交的 `thirdparty.local.json` 复用，不重复复制、不拉取其新资料。

`bootstrap_thirdparty.py` 默认拉全部必需 checkout，`--only ID` 仅用于定向维护，`--status` 仅检查 Git 身份。Git 就绪不等于可查询；完整安装还需知识 bootstrap/doctor。没有权限或索引失败时报告未完成。任何依赖本地修改和来源差异都保留，不 reset/clean。

受管目录固定清单提交；独立知识库保留实际提交并做本机可用性验收。TraceLens 稀疏检出完整代码/文档，按需扩展；旧上游迁移到 fork、Skills 替换备份、飞书权限和升级步骤见 [安装指南](../docs/integrations.md)。训练引擎 fork/PR 开发继续使用任务独立 checkout，不能借用知识库源码缓存。

## HCU-Knowledge 来源选择

GitHub 为主仓，内部 GitLab 保存同步副本；可访问 GitLab 项目的内部人员无需 GitHub 私有仓权限。首次安装选择内部来源：

```powershell
python scripts/setup_trainflow.py --skills-dir "$HOME/.codex/skills" --knowledge-source gitlab
```

仅获取该依赖可用 `python scripts/bootstrap_thirdparty.py --only hcu-knowledge --knowledge-source gitlab`，随后运行完整安装。两处来源共用清单固定提交，默认仍从 GitHub 获取；选项只决定新 checkout 的来源，已有 checkout 保留其 origin，后续 LFS 从该 origin 获取。GitLab 仍需网络可达及本人项目读取权限。

独立从任一来源克隆的知识库都可通过 `--knowledge-root` 绑定。若清单提交或 LFS 对象尚未同步，安装会报告未完成，不改用其他提交。已有 GitHub checkout 需要切换来源时，先核对本地状态，再显式修改它的 origin；安装器不会自动切换或覆盖。

TraceLens 的离线入口、原生 Agent 推理交接、远端回放及真实 HCU 验证边界见[分析指南](../docs/tracelens-analysis.md)。依赖安装成功和报告生成不表示所有硬件、模型或训练路径已经验证。

## 可选 KernelWiki

完整安装时加 `--with-kernelwiki`，共安装 12 个 Skill。已有 TrainFlow 可单独补装：

```powershell
python scripts/bootstrap_thirdparty.py --only kernelwiki
python scripts/install_skills.py --kernelwiki-only --target "$HOME/.codex/skills"
python scripts/install_skills.py --kernelwiki-only --target "$HOME/.codex/skills" --check
```

上游根目录就是 `KernelWiki` Skill；安装时保留其查询脚本、Wiki、PR 资料、源码摘录和 LICENSE，排除 `.git` 与运行缓存。默认流程不获取、不安装、不更新或删除这个可选入口。已有不同内容先比较，明确替换非 Git 安装可加 `--replace`；独立 Git checkout 由其自己的 Git 流程维护，安装器不替换其历史。版本升级先复核并更新清单固定提交，再显式补装。

它补充 NVIDIA 优化机制参考，不替代 HCU-Knowledge；HCU 的指令、参数、数值契约和收益仍按当前硬件、实现与实测核验。完整安装及检查见[安装指南](../docs/integrations.md#可选-kernelwiki)。
