---
id: pr-hygon-ai--cluster-manager-das-4
title: 'feat(envcheck): unified cluster runner, site config, and rccl multi-node fixes'
engine: tooling
stages:
- adapt
- optimize
- fault-tolerance
kind: source-pr
coverage: upstream-body-and-discussions
review_level: source-reported
runtime_validated: false
repository: HYGON-AI/cluster-manager-das
pr_number: 4
updated_at: '2026-10-10T02:08:40Z'
artifact_sha256: d6a4d7e06042677be039b326aa45937b3f2853787f9366d7aacff00c9419b2e8
artifact_path: knowledge/evidence/prs/HYGON-AI--cluster-manager-das/4-d6a4d7e06042677be039b326aa45937b3f2853787f9366d7aacff00c9419b2e8.json
sources: []
generated_body_sha256: af06b0cdb3796bf4186556208f4ac79a68b23ab3dd3dd866c7c4bb9f163ba510
---

# feat(envcheck): unified cluster runner, site config, and rccl multi-node fixes

[Upstream PR](https://github.com/HYGON-AI/cluster-manager-das/pull/4) · state: closed · merged: False

## Original PR description

Sync from fork zhaoyu111111/cluster-manager-das.

- unified bin/hcu-cluster-run entry (scenario x operation), group hostfiles, container lifecycle with managed peer SSH, token-guard cleanup
- site cluster_env.conf layer for rccl communication defaults; RCCL_EXTRA_LD_PATH for the shca plugin
- fix multi-node rccl: rank/guard scripts materialized to shared log dir (mpirun argv re-splitting broke inline bodies)
- container checks/tests require -i/--image
- run directories: <scenario>_<operation>_<timestamp>
- thousand-node log folding via --log-detail milestone|every|quiet
- dead-code removal (legacy cluster_group_run.sh, old CLI), MANIFEST.release fix
- 489 unit tests green (Windows + Linux nodes)

## Review and discussion

### reviews

- hygon-ai-reviewer[bot] · COMMENTED · 2026-10-09T15:32:23Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/4#pullrequestreview-5472134575)

<!-- github-ai-review:v1:4:9ef5761f8fc971f08de9c9ae457232ec604dc3de:bd37b201939013a6b7ae6b50 -->
## AI Review

### ⚪ 审查未完成

部分内容未完成审查，当前结论不代表全部改动。

已确认 8 个问题，其中 3 个已添加到对应代码行。

<details>
<summary>变更概览</summary>

本次变更主要包含：

- 统一入口更名为 bin/hcu-cluster-run 后，本批同步更新 .gitattributes/.gitignore（忽略回传的运行报告及站点本地 cluster\_env.conf 与基准配置），新增 AGENTS.md 工程约定文档，并调整 MANIFEST.release 必需文件列表（移除旧入口脚本与 USER\_GUIDE.md，加入 scripts/test.sh、tests、pyproject.toml、docs、cluster\_run）。
- 将 hcu-envcheck 的 README 重写为统一入口 hcu-cluster-run 的使用说明，覆盖三种环境场景、基础检测与主动测试操作、容器检查及日志/输出目录约定。
- README.md 重写为统一入口 hcu-cluster-run 的场景化使用说明，涵盖容器维护、RCCL/IB 检测参数与 scripts/test.sh 测试入口；同时删除指向 docs/USER\_GUIDE.md 的旧迁移跳转文件 hcu-envcheck/USER\_GUIDE.md。
- 新增 bin/hcu-cluster-run 控制端 bash 引导脚本：解析符号链接定位安装根目录并处理失效工作目录，分离消费控制器选项（--controller-env-script/--controller-python）并保留其余参数原文转发，提供场景化用法帮助。

</details>

<details>
<summary>文件审查摘要</summary>

| 文件 | 变更 | 审查结果 |
| --- | --- | --- |
| <code>hcu-envcheck/cluster_run/payloads/_torch_common.py</code> | 新增 · +72/-0 | P2 × 1 |
| <code>hcu-envcheck/cluster_run/preflight.py</code> | 新增 · +436/-0 | P2 × 1 |
| <code>hcu-envcheck/install.sh</code> | 修改 · +22/-15 | P2 × 1 |
| <code>hcu-envcheck/README.md</code> | 修改 · +172/-81 | P3 × 2 |
| <code>hcu-envcheck/cluster_run/payloads/dcu_idle_check.sh</code> | 新增 · +94/-0 | P3 × 1 |
| <code>hcu-envcheck/docs/USER_GUIDE.md</code> | 修改 · +202/-1217 | P3 × 1 |
| <code>hcu-envcheck/hcu_envcheck/baremetal_cluster.py</code> | 重命名 · +628/-461 | P3 × 1 |
| <code>hcu-envcheck/hcu_envcheck/active_rdma.py</code> | 删除 · +0/-2634 | — |
| <code>hcu-envcheck/hcu_envcheck/ib_fabric.py</code> | 删除 · +0/-2377 | — |
| <code>hcu-envcheck/hcu_envcheck/k8s_cluster.py</code> | 删除 · +0/-1912 | — |
| <code>hcu-envcheck/scripts/test.sh</code> | 新增 · +1257/-0 | — |
| <code>hcu-envcheck/hcu_envcheck/cli.py</code> | 删除 · +0/-979 | — |
| <code>hcu-envcheck/cluster_run/cli.py</code> | 新增 · +943/-0 | — |
| <code>hcu-envcheck/cluster_run/payloads/rccl_perf_test.sh</code> | 新增 · +590/-0 | — |
| <code>hcu-envcheck/tests/test_acceptance_contract.py</code> | 新增 · +576/-0 | — |
| <code>hcu-envcheck/hcu_envcheck/k8s.py</code> | 删除 · +0/-475 | — |
| <code>hcu-envcheck/hcu_envcheck/preflight.py</code> | 修改 · +2/-440 | — |
| <code>hcu-envcheck/cluster_run/payloads/check_deepep_env.sh</code> | 新增 · +366/-0 | — |
| <code>hcu-envcheck/cluster_run/payloads/task_guard.sh</code> | 新增 · +323/-0 | — |
| <code>hcu-envcheck/cluster_run/active.py</code> | 新增 · +322/-0 | — |

> 其余 80 个文件未逐项展开。

</details>

<details>
<summary>无法定位到 diff 行的问题（5）</summary>

#### P2 · env\_script 为 None 时 stderr 标记匹配会抛 TypeError

- 文件：<code>hcu-envcheck/cluster_run/preflight.py</code>（无法安全定位到当前 diff 行）
- 触发条件：以签名允许的 env\_script=None 调用 run\_container\_preflight 且 check\_idle=True，资源探测返回任意不匹配固定标记（cp/conda/module）的 stderr 行
- 证据与影响：remote\_stderr 非空时执行 any\(env\_script in line and "No such file or directory" in line ...\)；env\_script 为 None 时 \`None in line\` 直接抛出 TypeError，分支未做空值判断，而参数类型声明为 str \| None 预检流程整体异常中断，无法生成节点级结果，已完成的容器状态与资源探测证据丢失，一次瞬态远程 stderr 即可触发
- 修改建议：在标记条件中增加非空判断，如 env\_script is not None and env\_script in line ...，或在 env\_script 为 None 时跳过该匹配

#### P3 · 容器场景示例缺少文档中声明必填的 -i/--image 参数

- 文件：<code>hcu-envcheck/README.md</code>（无法安全定位到当前 diff 行）
- 触发条件：用户按文档「容器场景」示例原样运行 per-node-container platform,resource 命令。
- 证据与影响：第 75-77 行示例仅有 -f、--env-script、--container，未含 -i/--image；而同文档第 4 节明确写「容器场景的基础/主动检测与 script 均必填 -i/--image」，PR 描述也声明 container checks/tests require -i/--image，示例与强制要求自相矛盾。 按示例执行的命令会因缺少必填参数被预检拒绝（参数错误），或导致文档与实际必填约束之一错误，造成明确使用困扰。
- 修改建议：在容器场景示例命令中补上 -i &lt;镜像&gt; 参数，与「容器场景必填 -i/--image」的说明保持一致。

#### P3 · 文档示例硬编码开发者个人本地路径

- 文件：<code>hcu-envcheck/README.md</code>（无法安全定位到当前 diff 行）
- 触发条件：其他用户按 README 的 Windows 测试说明或 script 示例原样复制命令执行时。
- 证据与影响：新增内容中的 PowerShell 用例将解释器路径设为某开发者的个人用户目录绝对路径（检测到个人信息，原值不展示），另一 script 示例的绝对路径中也含真实用户名目录；文档示例与通用环境矛盾。 示例命令在其他机器上无法直接执行；个人用户目录与真实用户名被发布到公开文档，存在个人信息暴露。
- 修改建议：将示例中的个人绝对路径替换为通用的 python/python3 或占位符（如 &lt;python&gt;、&lt;prefix&gt;/env/env.sh），不包含真实用户目录和用户名。

#### P3 · 容器场景 platform/resource 示例缺少必填的 -i/--image

- 文件：<code>hcu-envcheck/docs/USER_GUIDE.md</code>（无法安全定位到当前 diff 行）
- 触发条件：读者按 3.1 节复制执行 per-node-container platform、resource 或 platform,resource 示例命令。
- 证据与影响：同节说明文字明确 platform/resource 执行前会“按必填的 -i/--image 核验容器实际镜像与指定一致”，container-status 示例也带有 -i "$IMAGE"，但三个容器内检测示例命令均未提供 -i/--image。 照抄示例会因缺少必填参数被命令行拒绝，与文档自身声明矛盾，造成明确的使用错误。
- 修改建议：为三个示例补充 -i "$IMAGE"，或在示例处说明容器场景该参数同样必填。

#### P3 · 开启 resource 类别时指标解析失败 findings 重复输出

- 文件：<code>hcu-envcheck/hcu_envcheck/baremetal_cluster.py</code>（无法安全定位到当前 diff 行）
- 触发条件：HCU 指标解析抛出异常，且 policy.check\_categories 包含 "resource"。
- 证据与影响：同一异常处理分支中既有原有的 findings.append\(Finding\("UNKNOWN", "HCU\_METRIC\_PARSE\_FAILED", ...\)\)，本次又新增了对 resource\_findings 追加相同 Finding；随后新增的 if "resource" in policy.check\_categories: findings.extend\(resource\_findings\) 把该 Finding 再次并入 findings。 节点结果 findings 数组中出现两条完全相同的 HCU\_METRIC\_PARSE\_FAILED 记录，报告重复列举、统计口径翻倍。
- 修改建议：保留两者其一：删除 except 中对 findings 的直接 append，仅写入 resource\_findings；或在 extend 前按 code 去重。

</details>

<details>
<summary>审查信息</summary>

- 变更统计：100 个文件，+9553/-11406。
- 覆盖情况：共 100 个文件，已完整审查 73 个。
- 候选问题：10 项；证据复核过滤：2 项；发布前敏感信息保护：0 项。
- 本服务以 GitHub 提供的 PR diff 为审查主体，PR 描述与按相关性选取的仓库片段仅用于核验；未执行代码或重跑测试，结论仍需维护者核验。

</details>
提交修复并推送新 commit 后，将自动审查 PR 的最新版本。

<!-- github-ai-ci-backfeed:37932756503:1:start -->
<details>
<summary>CI 结果：质量门禁未通过</summary>

质量门禁检测到需处理的问题；敏感命中原文、字段值、路径和日志引用不在评论中展示，请由有权限的维护者查看原始报告并处理。

</details>
<!-- github-ai-ci-backfeed:37932756503:1:end -->

<!-- github-ai-ci-backfeed:37932756224:1:start -->
<details>
<summary>CI 失败证据：PR Test \(hcu-envcheck\)</summary>

- **unit / hcu-envcheck unit tests**：工作流首个步骤的 fork PR 防护检查按设计触发：L34/L35 显示 BASE\_REPOSITORY 与 HEAD\_REPOSITORY 不同（PR 来自 fork 仓库），脚本进入 exit 1 分支，输出 "ERROR: fork pull requests cannot execute code on the shared CI runner."（L37），随后进程以 exit code 1 结束（L38）。失败发生在单元测试执行之前，测试本身未运行。
  - 与本次改动的关系：无关；该检查仅比较环境变量 HEAD\_REPOSITORY 与 BASE\_REPOSITORY，是仓库来源策略门禁；失败先于任何测试或构建步骤，未触及 diff 中被移除的 hcu-envcheck/bin/hcu-envcheck 与 hcu-envcheck/hcu-envcheck.sh。触发条件是 PR 来自 fork，与改动文件内容无关。
  - 建议：代码无需修改。由维护者按仓库流程处理 fork CI 限制：例如将分支同步到上游仓库重新发起 PR，或经授权流程以受控方式允许该 fork PR 运行 CI。以上为方向性建议，未经执行验证。
- **unit / hcu-envcheck unit tests**：任务在 fork 守卫步骤即失败：HEAD\_REPOSITORY 与 BASE\_REPOSITORY 不一致（PR 来自 fork 仓库），步骤打印 ERROR: fork pull requests cannot execute code on the shared CI runner. 并以 exit 1 结束（L37、L38），单元测试未开始执行。
  - 与本次改动的关系：无关；失败步骤是固定守卫：仅比较 HEAD\_REPOSITORY 与 BASE\_REPOSITORY（L25-L28），不涉及 diff 改动内容；被复用工作流来自基础仓库 refs/heads/main（L15），本次改动不影响该判断，且失败发生在任何测试代码运行之前。
  - 建议：该失败源于共享 CI 运行器对 fork PR 的执行策略，非代码缺陷；最小方向是按仓库既有流程由维护者在基础仓库侧触发或批准运行，或在允许执行 fork 代码的运行器环境执行测试，无需修改业务代码。

</details>
<!-- github-ai-ci-backfeed:37932756224:1:end -->

### issue_comments

- hygon-ai-reviewer[bot] · comment · 2026-10-10T01:52:46Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/4#issuecomment-6092393145)

<!-- github-ai-reviewer-progress:4:a1e688a538a2dc3e746873bbf56a0fd72e53f23e -->
## AI Review

发现 1 个问题。

### [P3] 错误退出信息按 stdout 判定着色但写入 stderr，重定向日志会混入 ANSI 转义码

- 位置：hcu-envcheck/cluster\_run/common.sh:46
- 触发条件：脚本在终端中运行且 stdout 仍为 TTY、将 stderr 重定向到文件或管道时，执行到 ce\_die。
- 证据与影响：第41行以 ce\_color\_init 1（检测 fd 1）设置颜色变量，第46行 ce\_die 却把带色文本输出到 &gt;&amp;2，与本文件“对应流是终端才带色，进文件/管道自动关”的声明不一致。 错误信息中的 ANSI 转义序列会随 stderr 写入日志文件或管道，影响后续检索与解析；反之 stderr 为终端而 stdout 被管道时错误信息反而无色。仅影响显示，不影响退出语义。
- 修改建议：按实际输出流初始化颜色（对 fd 2 再调用一次 ce\_color\_init 2，ce\_die 使用 stderr 侧变量），或让 ce\_die 直接不使用颜色。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 99 个文件，已审查 22 个，待审查 50 个，跳过 27 个。

> 跳过原因：无 patch 27 个；文件类型过滤 0 个。

> 进度已保存。正在继续处理。

### inline_comments

- hygon-ai-reviewer[bot] · comment · 2026-10-09T15:32:23Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/4#discussion_r4231803865)

File: `hcu-envcheck/cluster_run/payloads/_torch_common.py` · line None

**P2 · OMPI 世界大小变量名拼接错误，多进程直接 mpirun 启动时 world\_size 恒为 1**

**触发条件：** 通过 mpirun 直接启动且环境中只有 OpenMPI 变量（无 RANK/WORLD\_SIZE/HCU\_WORLD\_SIZE）时，configure\_direct\_mpi\_environment 内调用 rank\_value\("WORLD\_SIZE", 1\)。

**证据与影响：** rank\_value 将 OpenMPI 前缀按 "OMPI\_COMM\_WORLD\_" + name 拼接，对 WORLD\_SIZE 得到 OMPI\_COMM\_WORLD\_WORLD\_SIZE；OpenMPI 实际变量是 OMPI\_COMM\_WORLD\_SIZE（RANK/LOCAL\_RANK 对应拼接恰好正确，仅此键错误）。 world\_size 回落为 1，init\_process\_group 因 &lt;=1 直接返回 False，多节点/多进程检查静默跳过分布式初始化，检查结果不反映真实通信行为。

**修改建议：** 对 WORLD\_SIZE 使用显式映射（OMPI\_COMM\_WORLD\_SIZE），如维护 name→OMPI 后缀映射表或在 rank\_value 中特判 SIZE。

- hygon-ai-reviewer[bot] · comment · 2026-10-09T15:32:23Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/4#discussion_r4231803878)

File: `hcu-envcheck/install.sh` · line 185

**P2 · 替换安装后旧命令符号链接悬空，调用直接失败**

**触发条件：** bin\_dir 中已存在旧版本创建的 hcu-envcheck、hcu-envcheck-doctor、hcu-envcheck-verify 链接，且本次安装的 target 已存在时使用 --force 替换安装。

**证据与影响：** 各命令循环从三个命令改为仅 hcu-cluster-run，旧命令名不再出现在任何校验、建链或替换循环中；替换循环仅对已存在的 hcu-cluster-run 链接执行 mv，对旧命令链接没有清理或迁移逻辑，而旧 target 目录被移入 transaction 后其指向路径失效。 旧链接残留于 PATH 并变为悬空符号链接，用户或既有脚本调用 hcu-envcheck 等旧命令时报错中断，属于本次命令收敛引入的升级回归。

**修改建议：** 在替换/激活阶段检测旧三个命令链接：确认其指向本包旧安装后一并移入 transaction 或删除，并在安装完成输出中说明旧命令已下线。

- hygon-ai-reviewer[bot] · comment · 2026-10-09T15:32:23Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/4#discussion_r4231803884)

File: `hcu-envcheck/cluster_run/payloads/dcu_idle_check.sh` · line None

**P3 · --cards 缺少参数值时静默回退为检查全部卡**

**触发条件：** 脚本以 --cards 作为最后一个参数运行，或调用方传入空变量（如 --cards "$CARDS" 且 CARDS 为空）

**证据与影响：** case 分支中 --cards 取 CARDS\_CSV="$\{2:-\}" 且无任何校验，空串与未设置时的默认值（文档注明默认全部）不可区分；而同段中 --vram-max/--util-max 空值时会被正则校验拒绝并 die，处理不一致 漏传卡号时不报错而是检查全部卡，若本机其他卡繁忙会在预检阶段误判 BUSY，阻塞后续测试流程且无明确错误提示，增加排障成本

**修改建议：** 对 --cards 与其他取值选项一致处理：值为空时 die 提示缺少参数值，并可增加格式校验（如仅允许数字与逗号）

## Changed files and fixed code

- `.gitignore` · modified · additions 4 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/.gitignore)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/.gitignore)
- `hcu-envcheck/.gitattributes` · modified · additions 1 / deletions 1
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/.gitattributes)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/.gitattributes)
- `hcu-envcheck/.gitignore` · modified · additions 5 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/.gitignore)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/.gitignore)
- `hcu-envcheck/AGENTS.md` · added · additions 52 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/AGENTS.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/AGENTS.md)
- `hcu-envcheck/MANIFEST.release` · modified · additions 6 / deletions 2
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/MANIFEST.release)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/MANIFEST.release)
- `hcu-envcheck/README.md` · modified · additions 171 / deletions 81
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/README.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/README.md)
- `hcu-envcheck/USER_GUIDE.md` · removed · additions 0 / deletions 12
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/USER_GUIDE.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/USER_GUIDE.md)
- `hcu-envcheck/bin/hcu-cluster-run` · added · additions 140 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/bin/hcu-cluster-run)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/bin/hcu-cluster-run)
- `hcu-envcheck/bin/hcu-envcheck` · removed · additions 0 / deletions 104
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/bin/hcu-envcheck)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/bin/hcu-envcheck)
- `hcu-envcheck/bin/hcu-envcheck-doctor` · removed · additions 0 / deletions 71
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/bin/hcu-envcheck-doctor)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/bin/hcu-envcheck-doctor)
- `hcu-envcheck/bin/hcu-envcheck-verify` · removed · additions 0 / deletions 44
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/bin/hcu-envcheck-verify)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/bin/hcu-envcheck-verify)
- `hcu-envcheck/cluster_run/GUIDE.md` · added · additions 53 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/GUIDE.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/GUIDE.md)
- `hcu-envcheck/cluster_run/README.md` · added · additions 24 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/README.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/README.md)
- `hcu-envcheck/cluster_run/__init__.py` · added · additions 9 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/__init__.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/__init__.py)
- `hcu-envcheck/cluster_run/__main__.py` · renamed · additions 9 / deletions 5
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/__main__.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/__main__.py)
- `hcu-envcheck/cluster_run/active.py` · added · additions 324 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/active.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/active.py)
- `hcu-envcheck/cluster_run/baselines/gemm_baseline.conf.example` · added · additions 15 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/baselines/gemm_baseline.conf.example)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/baselines/gemm_baseline.conf.example)
- `hcu-envcheck/cluster_run/baselines/rccl_baseline.conf.example` · added · additions 28 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/baselines/rccl_baseline.conf.example)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/baselines/rccl_baseline.conf.example)
- `hcu-envcheck/cluster_run/cli.py` · added · additions 945 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/cli.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/cli.py)
- `hcu-envcheck/cluster_run/cluster_env.conf.example` · added · additions 108 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/cluster_env.conf.example)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/cluster_env.conf.example)
- `hcu-envcheck/cluster_run/common.sh` · added · additions 49 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/common.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/common.sh)
- `hcu-envcheck/cluster_run/consistency.py` · added · additions 191 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/consistency.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/consistency.py)
- `hcu-envcheck/cluster_run/container_ssh.py` · added · additions 250 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/container_ssh.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/container_ssh.py)
- `hcu-envcheck/cluster_run/env.py` · added · additions 90 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/env.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/env.py)
- `hcu-envcheck/cluster_run/examples/nodes.txt.example` · added · additions 5 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/examples/nodes.txt.example)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/examples/nodes.txt.example)
- `hcu-envcheck/cluster_run/extra_checks.py` · added · additions 203 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/extra_checks.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/extra_checks.py)
- `hcu-envcheck/cluster_run/hostfile.py` · added · additions 99 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/hostfile.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/hostfile.py)
- `hcu-envcheck/cluster_run/launchers.py` · added · additions 146 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/launchers.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/launchers.py)
- `hcu-envcheck/cluster_run/lifecycle.py` · added · additions 291 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/lifecycle.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/lifecycle.py)
- `hcu-envcheck/cluster_run/node_script.py` · added · additions 136 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/node_script.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/node_script.py)
- `hcu-envcheck/cluster_run/payloads/__init__.py` · added · additions 8 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/payloads/__init__.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/payloads/__init__.py)
- `hcu-envcheck/cluster_run/payloads/_torch_common.py` · added · additions 83 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/payloads/_torch_common.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/payloads/_torch_common.py)
- `hcu-envcheck/cluster_run/payloads/check_deepep_env.sh` · added · additions 366 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/payloads/check_deepep_env.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/payloads/check_deepep_env.sh)
- `hcu-envcheck/cluster_run/payloads/dcu_idle_check.sh` · added · additions 97 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/payloads/dcu_idle_check.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/payloads/dcu_idle_check.sh)
- `hcu-envcheck/cluster_run/payloads/gemm_perf_test.sh` · added · additions 298 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/payloads/gemm_perf_test.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/payloads/gemm_perf_test.sh)
- `hcu-envcheck/cluster_run/payloads/gemm_worker.py` · added · additions 56 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/payloads/gemm_worker.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/payloads/gemm_worker.py)
- `hcu-envcheck/cluster_run/payloads/ib_write_bw_worker.py` · added · additions 50 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/payloads/ib_write_bw_worker.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/payloads/ib_write_bw_worker.py)
- `hcu-envcheck/cluster_run/payloads/rccl_perf_test.sh` · added · additions 590 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/payloads/rccl_perf_test.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/payloads/rccl_perf_test.sh)
- `hcu-envcheck/cluster_run/payloads/rccl_worker.py` · added · additions 77 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/payloads/rccl_worker.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/payloads/rccl_worker.py)
- `hcu-envcheck/cluster_run/payloads/task_guard.sh` · added · additions 323 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/payloads/task_guard.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/payloads/task_guard.sh)
- `hcu-envcheck/cluster_run/preflight.py` · added · additions 440 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/preflight.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/preflight.py)
- `hcu-envcheck/cluster_run/task_control.py` · added · additions 310 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/task_control.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/task_control.py)
- `hcu-envcheck/cluster_run/tests/help_smoke_check.sh` · added · additions 17 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/tests/help_smoke_check.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/tests/help_smoke_check.sh)
- `hcu-envcheck/cluster_run/testsuites.py` · added · additions 110 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/cluster_run/testsuites.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/cluster_run/testsuites.py)
- `hcu-envcheck/docs/INDEX.md` · added · additions 7 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/docs/INDEX.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/docs/INDEX.md)
- `hcu-envcheck/docs/USER_GUIDE.md` · modified · additions 202 / deletions 1217
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/docs/USER_GUIDE.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/docs/USER_GUIDE.md)
- `hcu-envcheck/examples/check-nodes.sh` · removed · additions 0 / deletions 203
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/examples/check-nodes.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/examples/check-nodes.sh)
- `hcu-envcheck/examples/k8s-nodes.txt` · removed · additions 0 / deletions 7
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/examples/k8s-nodes.txt)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/examples/k8s-nodes.txt)
- `hcu-envcheck/examples/slurm-nodelist.sh` · removed · additions 0 / deletions 38
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/examples/slurm-nodelist.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/examples/slurm-nodelist.sh)
- `hcu-envcheck/examples/ssh-nodes-file.sh` · removed · additions 0 / deletions 39
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/examples/ssh-nodes-file.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/examples/ssh-nodes-file.sh)
- `hcu-envcheck/hcu-envcheck.sh` · removed · additions 0 / deletions 21
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu-envcheck.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu-envcheck.sh)
- `hcu-envcheck/hcu_envcheck/active_rdma.py` · removed · additions 0 / deletions 2634
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/active_rdma.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/active_rdma.py)
- `hcu-envcheck/hcu_envcheck/baremetal.py` · modified · additions 208 / deletions 41
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/baremetal.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/baremetal.py)
- `hcu-envcheck/hcu_envcheck/baremetal_cluster.py` · renamed · additions 628 / deletions 461
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/baremetal_cluster.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/slurm_cluster.py)
- `hcu-envcheck/hcu_envcheck/cli.py` · removed · additions 0 / deletions 979
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/cli.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/cli.py)
- `hcu-envcheck/hcu_envcheck/cluster_checks.py` · modified · additions 120 / deletions 42
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/cluster_checks.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/cluster_checks.py)
- `hcu-envcheck/hcu_envcheck/environment.py` · modified · additions 102 / deletions 84
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/environment.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/environment.py)
- `hcu-envcheck/hcu_envcheck/ib_fabric.py` · removed · additions 0 / deletions 2377
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/ib_fabric.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/ib_fabric.py)
- `hcu-envcheck/hcu_envcheck/k8s.py` · removed · additions 0 / deletions 475
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/k8s.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/k8s.py)
- `hcu-envcheck/hcu_envcheck/k8s_cluster.py` · removed · additions 0 / deletions 1912
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/k8s_cluster.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/k8s_cluster.py)
- `hcu-envcheck/hcu_envcheck/output.py` · modified · additions 33 / deletions 4
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/output.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/output.py)
- `hcu-envcheck/hcu_envcheck/pod_probe.py` · modified · additions 170 / deletions 66
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/pod_probe.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/pod_probe.py)
- `hcu-envcheck/hcu_envcheck/preflight.py` · modified · additions 2 / deletions 440
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/preflight.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/preflight.py)
- `hcu-envcheck/hcu_envcheck/rccl_output.py` · modified · additions 1 / deletions 1
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/rccl_output.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/rccl_output.py)
- `hcu-envcheck/hcu_envcheck/rdma_policy.py` · modified · additions 1 / deletions 1
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/rdma_policy.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/rdma_policy.py)
- `hcu-envcheck/hcu_envcheck/roce_health.py` · modified · additions 1 / deletions 1
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/roce_health.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/roce_health.py)
- `hcu-envcheck/hcu_envcheck/verbs.py` · added · additions 45 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/hcu_envcheck/verbs.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/verbs.py)
- `hcu-envcheck/install.sh` · modified · additions 22 / deletions 15
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/install.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/install.sh)
- `hcu-envcheck/pyproject.toml` · modified · additions 5 / deletions 2
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/pyproject.toml)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/pyproject.toml)
- `hcu-envcheck/scripts/build_release.ps1` · modified · additions 14 / deletions 2
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/scripts/build_release.ps1)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/scripts/build_release.ps1)
- `hcu-envcheck/scripts/build_release.sh` · modified · additions 11 / deletions 2
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/scripts/build_release.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/scripts/build_release.sh)
- `hcu-envcheck/scripts/test.sh` · added · additions 1257 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/scripts/test.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/scripts/test.sh)
- `hcu-envcheck/tests/test_acceptance_contract.py` · added · additions 578 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_acceptance_contract.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_acceptance_contract.py)
- `hcu-envcheck/tests/test_active_rdma.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_active_rdma.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_active_rdma.py)
- `hcu-envcheck/tests/test_baremetal.py` · modified · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_baremetal.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_baremetal.py)
- `hcu-envcheck/tests/test_baremetal_cluster.py` · renamed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_baremetal_cluster.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_slurm_cluster.py)
- `hcu-envcheck/tests/test_base_execution_exit.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_base_execution_exit.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_base_execution_exit.py)
- `hcu-envcheck/tests/test_benchmark_profiles.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_benchmark_profiles.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_benchmark_profiles.py)
- `hcu-envcheck/tests/test_cli_output.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_cli_output.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_cli_output.py)
- `hcu-envcheck/tests/test_cluster_report.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_cluster_report.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_cluster_report.py)
- `hcu-envcheck/tests/test_cluster_run.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_cluster_run.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_cluster_run.py)
- `hcu-envcheck/tests/test_consistency_contract.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_consistency_contract.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_consistency_contract.py)
- `hcu-envcheck/tests/test_container_preflight.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_container_preflight.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_container_preflight.py)
- `hcu-envcheck/tests/test_container_ssh.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_container_ssh.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_container_ssh.py)
- `hcu-envcheck/tests/test_container_status.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_container_status.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_container_status.py)
- `hcu-envcheck/tests/test_entrypoint.py` · modified · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_entrypoint.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_entrypoint.py)
- `hcu-envcheck/tests/test_environment_contract.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_environment_contract.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_environment_contract.py)
- `hcu-envcheck/tests/test_extra_interfaces.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_extra_interfaces.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_extra_interfaces.py)
- `hcu-envcheck/tests/test_ib_fabric.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_ib_fabric.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_ib_fabric.py)
- `hcu-envcheck/tests/test_k8s_cluster_scale.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_k8s_cluster_scale.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_k8s_cluster_scale.py)
- `hcu-envcheck/tests/test_k8s_nodes_file.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_k8s_nodes_file.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_k8s_nodes_file.py)
- `hcu-envcheck/tests/test_k8s_output_capture.py` · removed · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_k8s_output_capture.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_k8s_output_capture.py)
- `hcu-envcheck/tests/test_launch_contract.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_launch_contract.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_launch_contract.py)
- `hcu-envcheck/tests/test_new_interface.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_new_interface.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_new_interface.py)
- `hcu-envcheck/tests/test_node_script_control.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_node_script_control.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_node_script_control.py)
- `hcu-envcheck/tests/test_output.py` · modified · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_output.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_output.py)
- `hcu-envcheck/tests/test_parsers.py` · modified · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_parsers.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_parsers.py)
- `hcu-envcheck/tests/test_rdma_protocol.py` · modified · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_rdma_protocol.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_rdma_protocol.py)
- `hcu-envcheck/tests/test_task_control.py` · added · additions 0 / deletions 0
  - [head](https://github.com/zhaoyu111111/cluster-manager-das/blob/a1e688a538a2dc3e746873bbf56a0fd72e53f23e/hcu-envcheck/tests/test_task_control.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/tests/test_task_control.py)

## Evidence and interpretation boundary

[Original JSON, discussions and patches](../../evidence/prs/HYGON-AI--cluster-manager-das/4-d6a4d7e06042677be039b326aa45937b3f2853787f9366d7aacff00c9419b2e8.json) · SHA-256 `d6a4d7e06042677be039b326aa45937b3f2853787f9366d7aacff00c9419b2e8`.

Diff complete: False. Missing/binary/truncated patches require pinned source inspection. This is a source page, not an independently verified optimization case. Open, merged and released are different states; recheck the deployed dependency.
