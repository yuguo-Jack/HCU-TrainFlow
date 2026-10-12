---
id: pr-hygon-ai--cluster-manager-das-3
title: 'feat(cluster-manager): add Docker launch and node recovery support'
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
pr_number: 3
updated_at: '2026-10-10T07:08:44Z'
artifact_sha256: dea1db40627a505aa6e7e26bbba6087406dc8bc85e92fc1344669250ecf820a5
artifact_path: knowledge/evidence/prs/HYGON-AI--cluster-manager-das/3-dea1db40627a505aa6e7e26bbba6087406dc8bc85e92fc1344669250ecf820a5.json
sources: []
generated_body_sha256: 819954d7b3c6a70aec383707e91ef85f72b297f0b02c26b0b9ce8c88b98ef4bc
---

# feat(cluster-manager): add Docker launch and node recovery support

[Upstream PR](https://github.com/HYGON-AI/cluster-manager-das/pull/3) · state: closed · merged: True

## Original PR description

No upstream description; do not infer motivation from title.

## Review and discussion

### reviews

- zhaoyu111111 · DISMISSED · 2026-09-24T10:03:44Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#pullrequestreview-5302877640)

(No body; status only.)

- hygon-ai-reviewer[bot] · COMMENTED · 2026-09-30T09:31:23Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#pullrequestreview-5364329541)

<!-- github-ai-review:v1:3:d2d0c683096f9beeee517cda3db009a89ba74f4d:33c0ccf2363188add504c7fe -->
## AI Review

### 🔴 需要修改

代码审查与 CI 失败证据综合后，存在需要处理的问题。

已确认 2 个问题，其中 1 个已添加到对应代码行。

<details>
<summary>变更概览</summary>

本次变更主要包含：

- 控制器启动流程与训练循环新增 Docker 容器准备调用：launcher 提供 prepare\_containers 时先在整个 hostfile 上预准备容器（失败抛错终止），节点替换后通过 prepare\_new\_containers 准备，失败时释放运行节点并等待一个监控周期后重试。
- README 新增 Docker 启动模式（预创建容器 + docker exec）的配置项与使用说明。
- 新增 DockerLauncher：先通过 clush 在各主机并行准备/复用训练容器，再构造 mpirun 命令按每主机一个进程启动训练脚本，并支持通过环境变量固定 OMPI/PRTE 的 TCP 网卡选择以及向所有 rank 注入 MPI\_RANK\_ENV/MPI\_FORWARD\_ENV 指定的变量。
- 新增 docker\_launcher，实现通过 SSH 连接首个训练主机并在其容器内以 docker exec 启动训练脚本，同时构造 shell 片段将 rank\_env 与 forward\_env 转发为 OMPI/PRTE 的 mca\_base\_env\_list 环境变量。

</details>

<details>
<summary>文件审查摘要</summary>

| 文件 | 变更 | 审查结果 |
| --- | --- | --- |
| <code>cluster_manager/cluster_manager/launcher/docker_launcher.py</code> | 新增 · +311/-0 | P2 × 1 |
| <code>cluster_manager/examples/start_docker.sh</code> | 新增 · +52/-0 | P3 × 1 |
| <code>cluster_manager/test/unit/test_docker_launcher.py</code> | 新增 · +396/-0 | — |
| <code>cluster_manager/cluster_manager/launcher/mpirun_launcher.py</code> | 修改 · +242/-5 | — |
| <code>cluster_manager/test/unit/test_job_lifecycle.py</code> | 修改 · +78/-0 | — |
| <code>cluster_manager/test/unit/test_launcher_monitor_resilience.py</code> | 修改 · +56/-3 | — |
| <code>cluster_manager/docs/config_guide.md</code> | 修改 · +51/-1 | — |
| <code>cluster_manager/cluster_manager/controller/distributed_job_manager.py</code> | 修改 · +35/-0 | — |
| <code>cluster_manager/README.md</code> | 修改 · +26/-3 | — |
| <code>cluster_manager/test/unit/test_runtime_context_faults.py</code> | 修改 · +25/-2 | — |
| <code>cluster_manager/test/unit/test_distributed_job_manager.py</code> | 修改 · +24/-1 | — |
| <code>cluster_manager/cluster_manager/node_management/node_pool.py</code> | 修改 · +3/-21 | — |
| <code>cluster_manager/cluster_manager/main.py</code> | 修改 · +16/-1 | — |
| <code>cluster_manager/cluster_manager/runtime/job_state_machine.py</code> | 修改 · +16/-0 | — |
| <code>cluster_manager/cluster_manager/launcher/launcher_factory.py</code> | 修改 · +9/-3 | — |
| <code>cluster_manager/cluster_manager/runtime/runtime_context.py</code> | 修改 · +11/-0 | — |

</details>

<details>
<summary>无法定位到 diff 行的问题（1）</summary>

#### P2 · 容器删除命令在容器内执行，remove\_container\_on\_stop likely静默失效

- 文件：<code>cluster_manager/cluster_manager/launcher/docker_launcher.py</code>（无法安全定位到当前 diff 行）
- 触发条件：remove\_container\_on\_stop=True且reuse\_container=False时调用stop\(\)。
- 证据与影响：docker rm -f被追加到inner末尾，而inner整体经remote\_cmd='docker exec -u root &lt;容器&gt; bash -lc &lt;inner&gt;'在容器内部执行；容器内通常没有docker客户端或daemon套接字。且命令被'&gt;/dev/null 2&gt;&amp;1 \|\| true'静默吞错，stop\(\)仍返回成功码。 容器实际不会被删除而调用方误以为清理成功，遗留容器占用资源，可能阻塞下次启动，违背该选项的目的。
- 修改建议：把docker rm -f从inner移出，放到宿主机层：在clush命令中随remote\_cmd并列\(如remote\_cmd+'; docker rm -f ...'\)，或执行后检查删除结果再记录/返回状态。

</details>

<details>
<summary>审查信息</summary>

- 变更统计：16 个文件，+1351/-40。
- 覆盖情况：共 16 个文件，已完整审查 16 个。
- 候选问题：4 项；证据复核过滤：2 项；发布前敏感信息保护：0 项。
- 本服务以 GitHub 提供的 PR diff 为审查主体，PR 描述与按相关性选取的仓库片段仅用于核验；未执行代码或重跑测试，结论仍需维护者核验。

</details>
提交修复并推送新 commit 后，将自动审查 PR 的最新版本。

<!-- github-ai-ci-backfeed:36693636557:1:start -->
<details>
<summary>CI 失败证据：PR Test \(cluster\_manager\)</summary>

- **unit / cluster\_manager unit tests**：直接证据：单测 test\_none\_run\_skips\_slurm\_job\_ensure 在 distributed\_job\_manager.py:65 抛出 AttributeError: 'DistributedJobManager' object has no attribute 'launcher'。该行是本次 diff 新增的 getattr\(self.launcher, "prepare\_containers", None\)，run\(\) 在 \_init\_components 之前访问 launcher，而该测试将 \_init\_components mock 掉导致属性不存在。
  - 与本次改动的关系：相关；报错位置 distributed\_job\_manager.py:65 与 diff 中新增的 prepare\_containers = getattr\(self.launcher, ...\) 一致，位于 \_ensure\_slurm\_job 之后、\_init\_components 之前；报错文件即被修改文件，触发路径可逐行核对，判定与本次改动相关。
  - 建议：在访问 self.launcher 前确保其已初始化（如在 \_\_init\_\_ 创建），或先 getattr\(self, "launcher", None\) 再取 prepare\_containers，或将该准备逻辑后移到 \_init\_components 之后。具体选择取决于 launcher 的预期生命周期，需作者结合完整类定义核验。

</details>
<!-- github-ai-ci-backfeed:36693636557:1:end -->

- hygon-ai-reviewer[bot] · COMMENTED · 2026-10-08T10:13:15Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#pullrequestreview-5455027088)

<!-- github-ai-review:v1:3:a356027eb009318cff2d89215a3d5db319c4b4b7:39ea1a971319a8235561823d -->
## AI Review

### 🔴 需要修改

代码审查与 CI 失败证据综合后，存在需要处理的问题。

已确认 1 个问题，其中 0 个已添加到对应代码行。

<details>
<summary>变更概览</summary>

本次变更主要包含：

- 在分布式任务控制器中新增 Docker 模式容器准备流程：启动前对全部训练节点调用 prepare\_containers，失败即抛异常终止；重启训练前对不在原分配内的新节点调用 prepare\_new\_containers，失败则释放运行节点并延时重试。
- 新增 DockerLauncher：通过 clush 在各节点批量准备训练容器，再经 mpirun 扇出启动训练，并把 MPI\_RANK\_ENV/MPI\_FORWARD\_ENV 及网络接口配置注入各 rank 环境。
- 新增 docker\_launcher.py：生成 shell 片段，在容器内导出 rank\_env 变量并经 OMPI/PRTE 的 mca\_base\_env\_list 转发 forward\_env；start\(\) 在首个分配主机的容器内执行训练脚本目录并通过内部 mpirun 经 sshd 扩散到其他节点。
- 新增 Docker 启动器：管理侧经 SSH 连接首个训练主机，通过 docker exec -d 在容器内 bash 中执行带网络与 rank 环境导出、工作目录切换的启动脚本，各参数均做 shell 转义；并新增基于 pgrep 的 TERM-then-KILL 自排除停止脚本构建逻辑。

</details>

<details>
<summary>文件审查摘要</summary>

| 文件 | 变更 | 审查结果 |
| --- | --- | --- |
| <code>cluster_manager/cluster_manager/launcher/mpirun_launcher.py</code> | 修改 · +242/-5 | P1 × 1 |
| <code>cluster_manager/test/unit/test_docker_launcher.py</code> | 新增 · +403/-0 | — |
| <code>cluster_manager/cluster_manager/launcher/docker_launcher.py</code> | 新增 · +316/-0 | — |
| <code>cluster_manager/test/unit/test_job_lifecycle.py</code> | 修改 · +78/-0 | — |
| <code>cluster_manager/test/unit/test_launcher_monitor_resilience.py</code> | 修改 · +56/-3 | — |
| <code>cluster_manager/docs/config_guide.md</code> | 修改 · +51/-1 | — |
| <code>cluster_manager/examples/start_docker.sh</code> | 新增 · +52/-0 | — |
| <code>cluster_manager/cluster_manager/controller/distributed_job_manager.py</code> | 修改 · +35/-0 | — |
| <code>cluster_manager/README.md</code> | 修改 · +26/-3 | — |
| <code>cluster_manager/test/unit/test_runtime_context_faults.py</code> | 修改 · +25/-2 | — |
| <code>cluster_manager/test/unit/test_distributed_job_manager.py</code> | 修改 · +24/-1 | — |
| <code>cluster_manager/cluster_manager/node_management/node_pool.py</code> | 修改 · +3/-21 | — |
| <code>cluster_manager/cluster_manager/main.py</code> | 修改 · +16/-1 | — |
| <code>cluster_manager/cluster_manager/runtime/job_state_machine.py</code> | 修改 · +16/-0 | — |
| <code>cluster_manager/cluster_manager/launcher/launcher_factory.py</code> | 修改 · +9/-3 | — |
| <code>cluster_manager/cluster_manager/runtime/runtime_context.py</code> | 修改 · +11/-0 | — |
| <code>cluster_manager/test/unit/test_cluster_schedule.py</code> | 修改 · +4/-0 | — |

</details>

<details>
<summary>无法定位到 diff 行的问题（1）</summary>

#### P1 · 非复用路径引用未定义变量，构建命令时抛 NameError

- 文件：<code>cluster_manager/cluster_manager/launcher/mpirun_launcher.py</code>（无法安全定位到当前 diff 行）
- 触发条件：以 reuse\_existing=False 走 else 分支构建 Docker 启动命令时。
- 证据与影响：可见代码中 reuse\_check、reuse\_end、remove\_command 仅在 if reuse\_existing 分支赋值，else 分支只对新 new\_container\_init 赋值；而 return 的 f-string 无条件插值 \{reuse\_check\}、\{remove\_command\}、\{reuse\_end\}。 非复用模式在 Python 层直接抛 NameError，Docker 启动命令无法生成，该模式完全不可用。
- 修改建议：在 else 分支补齐默认赋值：reuse\_check=""、reuse\_end=""，remove\_command 按设计保留清理命令或置空字符串。

</details>

<details>
<summary>审查信息</summary>

- 变更统计：17 个文件，+1367/-40。
- 覆盖情况：共 17 个文件，已完整审查 17 个。
- 候选问题：2 项；证据复核过滤：1 项；发布前敏感信息保护：0 项。
- 本服务以 GitHub 提供的 PR diff 为审查主体，PR 描述与按相关性选取的仓库片段仅用于核验；未执行代码或重跑测试，结论仍需维护者核验。

</details>
提交修复并推送新 commit 后，将自动审查 PR 的最新版本。

<!-- github-ai-ci-backfeed:37759176414:1:start -->
<details>
<summary>CI 失败证据：PR Test \(cluster\_manager\)</summary>

- **unit / cluster\_manager unit tests**：直接失败是 runner 环境预检：日志显示 hygon/ft-controller:latest 未加载到该 runner（L144-L145），预检脚本按既定分支 exit 1（L126-L130、L146），job 标记 failure，单元测试尚未开始执行，未见测试用例本身失败。
  - 与本次改动的关系：无法确定；失败点为固定守护检查：docker image inspect 未找到 CLUSTER\_MANAGER\_CI\_IMAGE 指向的镜像（L126-L130 对应报错 L144-L146），属 runner 侧镜像就绪问题；但本批无 PR 补丁（0/17 可引用），不排除该 PR 修改了调用方工作流的期望镜像名/ID 触发同一检查。
  - 建议：处理方向：在共享 runner ci-nmz2 上确认被评审镜像 tar 的加载状态；若预期镜像已更新，先加载对应的已评审 hygon-ft-controller-latest.tar 再重跑。同时核对 PR 是否改动了期望镜像配置。以上均未执行，仅为方向。

</details>
<!-- github-ai-ci-backfeed:37759176414:1:end -->

<!-- github-ai-ci-backfeed:37759176414:2:start -->
<details>
<summary>CI 失败证据：PR Test \(cluster\_manager\)</summary>

- **unit / cluster\_manager unit tests**：直接异常：L246 E NameError: name 'shlex' is not defined，位置 cluster\_manager/test/unit/test\_docker\_launcher.py:273（L248），该行执行 remote\_command = shlex.split\(command\)\[-1\] 但 shlex 未定义。导致测试 test\_docker\_stop\_sweeps\_inside\_container\_as\_root 失败（L250），汇总 1 failed, 169 passed（L251），退出码1（L252）。
  - 与本次改动的关系：相关；失败测试直接断言本批新增 docker\_launcher.py 中的 \_STOP\_GUARD（日志L241），属于针对新增模块 DockerLauncher 的单元测试；NameError 发生在测试文件第273行自身使用 shlex.split 处。测试文件补丁未出现在本批 5/17 diff 片段中，无法直接核对该文件，但错误行为与新增模块测试的触发路径可核对。
  - 建议：在 cluster\_manager/test/unit/test\_docker\_launcher.py 中补充 import shlex：日志显示第273行使用 shlex.split 而运行时未定义，而被测源码 docker\_launcher.py 的补丁已含 import shlex，问题应在测试文件的导入。建议先人工核对该文件当前导入列表。
- **unit / cluster\_manager unit tests**：直接证据：cluster\_manager/test/unit/test\_docker\_launcher.py:273 抛出 NameError: name 'shlex' is not defined，用例 test\_docker\_stop\_sweeps\_inside\_container\_as\_root 失败；汇总为 1 failed, 169 passed，随后任务进程 exit code 1。错误点在测试文件自身作用域，引用了 shlex 但缺少导入
  - 与本次改动的关系：相关；Run SHA 与 PR SHA 一致；NameError 是测试文件自身作用域的确定性错误，引用 shlex 未导入必然失败；测试针对 docker stop 容器内清扫功能，与本批次 diff 中launcher/docker化改造主题一致。本片段仅见 mpirun\_launcher.py 补丁，测试文件归属为基于日志上下文的推断
  - 建议：建议在 cluster\_manager/test/unit/test\_docker\_launcher.py 顶部补充 import shlex。本片段 diff 未展示该测试文件内容，实际导入情况需以仓库文件为准；此修改仅为方向性建议，需人工核验后确认
- **unit / cluster\_manager unit tests**：日志直接显示 NameError: name 'shlex' is not defined，位置为 cluster\_manager/test/unit/test\_docker\_launcher.py:273，该测试使用 shlex.split 但模块未导入 shlex；结果 1 failed, 169 passed，进程以退出码 1 结束，属代码缺陷而非依赖或环境问题。
  - 与本次改动的关系：相关；失败用例 test\_docker\_stop\_sweeps\_inside\_container\_as\_root 断言 docker exec -u root、\_STOP\_GUARD 等，与本 diff 中新增的 docker stop 逻辑（大量使用 shlex.quote）对应；但测试文件 patch 未包含在本批 5/17 片段中，缺失导入是否由本 PR 引入未能逐字核对。
  - 建议：在 cluster\_manager/test/unit/test\_docker\_launcher.py 顶部补充 import shlex（与文件现有导入方式保持一致）；属最小改动，需人工核验后提交。

</details>
<!-- github-ai-ci-backfeed:37759176414:2:end -->

<!-- github-ai-ci-backfeed:37759176414:3:start -->
<details>
<summary>CI 失败证据：PR Test \(cluster\_manager\)</summary>

- **unit / cluster\_manager unit tests**：单测 test\_docker\_stop\_sweeps\_inside\_container\_as\_root 在测试自身第273行执行 shlex.split\(command\) 时抛出 NameError: name 'shlex' is not defined，导致 1 failed（169 passed），进程以退出码1结束。报错位置为测试文件 cluster\_manager/test/unit/test\_docker\_launcher.py:273，而非被测模块内部。
  - 与本次改动的关系：相关；失败发生在针对本 PR 新增 DockerLauncher 的单测中；该测试断言 DockerLauncher.\_STOP\_GUARD，而该属性仅出现在本批 diff 新增的 docker\_launcher.py 中，可判断该测试属于本次改动；报错行位于测试文件自身，方向为其缺少 import shlex。
  - 建议：在 cluster\_manager/test/unit/test/…/test\_docker\_launcher.py 顶部补充 import shlex（第273行调用位于测试自身；源码 docker\_launcher.py 在本批 diff 中已正确 import shlex）。修改前需人工核对该测试文件的导入区再调整。
- **unit / cluster\_manager unit tests**：直接报错：cluster\_manager/test/unit/test\_docker\_launcher.py:273 执行 shlex.split\(command\)\[-1\] 时抛出 NameError: name 'shlex' is not defined，测试 test\_docker\_stop\_sweeps\_inside\_container\_as\_root 失败；结果 1 failed, 169 passed，导致 job 退出码 1。name 未定义通常为该测试模块缺少 import shlex，需查看测试文件确认。
  - 与本次改动的关系：相关；失败测试针对本 PR 新增的 DockerLauncher.stop 路径，其断言的 clush、docker exec -u root、prted、\_STOP\_GUARD 与 diff 中新增代码一一对应；Run SHA 与 PR SHA 一致，报错点位于测试文件自身第 273 行使用 shlex，属本次改动引入的测试代码问题。
  - 建议：核验 test\_docker\_launcher.py 的导入区，补充缺失的 shlex 导入（若第 273 行确为测试自身代码）；这是最小处理方向，实际修改前需人工确认测试文件完整内容。
- **unit / cluster\_manager unit tests**：直接异常为 NameError: name 'shlex' is not defined，发生于 cluster\_manager/test/unit/test\_docker\_launcher.py:273（remote\_command = shlex.split\(command\)\[-1\]），表明该测试模块缺少 import shlex；test\_docker\_stop\_sweeps\_inside\_container\_as\_root 失败，1 failed, 169 passed，随后进程以退出码 1 结束。
  - 与本次改动的关系：相关；异常发生在测试代码自身，NameError 直接表明测试文件未导入 shlex；该用例断言 DockerLauncher.\_STOP\_GUARD 与 docker exec -u root 的 stop 语义，与本 PR 为 launcher 增加 Docker 能力的主题一致，且 Run SHA 与 PR SHA 相同。本批 diff 未含该测试文件 patch，归属判断含推断成分。
  - 建议：最小方向：在 test\_docker\_launcher.py 顶部补充 import shlex，并自查该文件新增引用是否均有对应导入。此为待执行的修复建议，未实际执行，需维护者核验。
- **unit / cluster\_manager unit tests**：单测 test\_docker\_stop\_sweeps\_inside\_container\_as\_root 失败：在 cluster\_manager/test/unit/test\_docker\_launcher.py:273 执行 shlex.split 时抛出 NameError: name 'shlex' is not defined，汇总为 1 failed, 169 passed in 3.28s，随后任务以 exit code 1 结束。NameError 指向该名称在测试文件作用域未定义，最可能是缺失导入，需以文件内容核验。
  - 与本次改动的关系：相关；Run SHA 与 PR SHA 一致。失败用例针对 DockerLauncher 的容器内停止清理并断言 \_STOP\_GUARD，与 diff 中 mpirun\_launcher.py 新增的 docker stop 命令构造路径对应；NameError 发生在该测试自身代码行。本批 diff 为 5/17 片段，未包含该测试文件的 patch。
  - 建议：基于报错的最小方向：在 test\_docker\_launcher.py 顶部补充 shlex 导入（如 import shlex）。需人工核验该文件现有 import 列表后修改，不作为已确认结论。
- **unit / cluster\_manager unit tests**：直接异常为 NameError: name 'shlex' is not defined，失败点 cluster\_manager/test/unit/test\_docker\_launcher.py:273（用例 test\_docker\_stop\_sweeps\_inside\_container\_as\_root 中 shlex.split 调用处），汇总 1 failed, 169 passed，之后步骤以退出码 1 结束。
  - 与本次改动的关系：相关；失败用例位于本 PR 新增（STATUS: added）的 test\_docker\_launcher.py 内；diff 可见的文件头部导入块为 patch/os/pathlib/shutil/subprocess/time/pytest，不含 import shlex，与 NameError 报错可直接对应。
  - 建议：最小方向：在该测试文件导入区补充 import shlex。基于日志与片段推测的缺失导入，需先人工核对文件实际内容再修改。

</details>
<!-- github-ai-ci-backfeed:37759176414:3:end -->

- hygon-ai-reviewer[bot] · COMMENTED · 2026-10-10T04:27:45Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#pullrequestreview-5477564172)

<!-- github-ai-review:v1:3:9b249b2b17005d052f3dd00cf3138e8db8834f88:af89ec2e56b6d1023bdad8d0 -->
## AI Review

### 🔴 需要修改

发现有明确证据的高优先级问题。

已确认 2 个问题，其中 1 个已添加到对应代码行。

<details>
<summary>变更概览</summary>

本次变更主要包含：

- README 文档新增 Docker 启动模式说明：补充 CLUSTER\_LAUNCH\_MODE=docker 相关配置项（CONTAINER\_NAME、容器内路径、容器 SSH 端口等）、容器准备流程及停止训练时的容器处理策略。
- run\(\) 启动阶段新增 Docker 容器准备步骤：launcher 支持 prepare\_containers 时按 hostfile 初始化容器，返回非零则抛 RuntimeError 中止启动。
- \_start\_training 新增对 NodePool 替换节点的容器准备：launcher 支持 prepare\_new\_containers 时对新节点执行准备，失败则释放节点并等待后重试。
- 新增 DockerLauncher 启动器：通过 clush 在各主机并发准备训练容器，并用外层 mpirun 将训练命令分发到各节点，支持指定网络接口及向各 rank 转发配置/环境变量。

</details>

<details>
<summary>文件审查摘要</summary>

| 文件 | 变更 | 审查结果 |
| --- | --- | --- |
| <code>cluster_manager/cluster_manager/launcher/mpirun_launcher.py</code> | 修改 · +242/-5 | P1 × 1 · P2 × 1 |
| <code>cluster_manager/test/unit/test_docker_launcher.py</code> | 新增 · +404/-0 | — |
| <code>cluster_manager/cluster_manager/launcher/docker_launcher.py</code> | 新增 · +316/-0 | — |
| <code>cluster_manager/test/unit/test_job_lifecycle.py</code> | 修改 · +78/-0 | — |
| <code>cluster_manager/test/unit/test_launcher_monitor_resilience.py</code> | 修改 · +56/-3 | — |
| <code>cluster_manager/examples/start_docker.sh</code> | 新增 · +56/-0 | — |
| <code>cluster_manager/docs/config_guide.md</code> | 修改 · +51/-1 | — |
| <code>cluster_manager/cluster_manager/controller/distributed_job_manager.py</code> | 修改 · +35/-0 | — |
| <code>cluster_manager/README.md</code> | 修改 · +26/-3 | — |
| <code>cluster_manager/test/unit/test_runtime_context_faults.py</code> | 修改 · +25/-2 | — |
| <code>cluster_manager/test/unit/test_distributed_job_manager.py</code> | 修改 · +24/-1 | — |
| <code>cluster_manager/cluster_manager/node_management/node_pool.py</code> | 修改 · +3/-21 | — |
| <code>cluster_manager/cluster_manager/main.py</code> | 修改 · +16/-1 | — |
| <code>cluster_manager/cluster_manager/runtime/job_state_machine.py</code> | 修改 · +16/-0 | — |
| <code>cluster_manager/cluster_manager/launcher/launcher_factory.py</code> | 修改 · +9/-3 | — |
| <code>cluster_manager/cluster_manager/runtime/runtime_context.py</code> | 修改 · +11/-0 | — |
| <code>cluster_manager/test/unit/test_cluster_schedule.py</code> | 修改 · +4/-0 | — |

</details>

<details>
<summary>无法定位到 diff 行的问题（1）</summary>

#### P1 · 将宿主机 root 的 SSH 目录整体只读挂载进容器，造成凭据暴露面

- 文件：<code>cluster_manager/cluster_manager/launcher/mpirun_launcher.py</code>（无法安全定位到当前 diff 行）
- 触发条件：MPI-Docker 模式下任意 docker run 准备/启动容器后，容器内（通常以 root 运行）的用户代码或依赖包读取挂载目录。
- 证据与影响：本次改动新增 mounts += " -v /opt/hyhal:/opt/hyhal:ro -v /root/.ssh:/root/.ssh:ro"，把宿主机 root 的整个 .ssh 目录挂入容器。注释只说明了防止容器回写，并未限制读取，授权公钥校验不需要暴露目录内全部文件。 容器内工作负载可读取宿主机 root 的 SSH 凭据文件（如私钥）等敏感内容，在多租户训练集群中可能导致凭据外泄与跨节点横向移动。
- 修改建议：最小修复：改为按需挂载单个文件（如 authorized\_keys 和 sshd 所需主机密钥），或通过构建期注入/临时密钥方式提供，同时避免整个 .ssh 目录挂载；修复后需人工核验容器内启动流程仍可用。

</details>

<details>
<summary>审查信息</summary>

- 变更统计：17 个文件，+1372/-40。
- 覆盖情况：共 17 个文件，已完整审查 17 个。
- 候选问题：3 项；证据复核过滤：1 项；发布前敏感信息保护：0 项。
- 本服务以 GitHub 提供的 PR diff 为审查主体，PR 描述与按相关性选取的仓库片段仅用于核验；未执行代码或重跑测试，结论仍需维护者核验。

</details>
提交修复并推送新 commit 后，将自动审查 PR 的最新版本。

- hygon-ai-reviewer[bot] · COMMENTED · 2026-10-10T05:04:45Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#pullrequestreview-5477700284)

<!-- github-ai-review:v1:3:a815ffa428fb308dd9e562858893a810e9d77fbf:29621864b070b84888cc8d54 -->
## AI Review

### 🟡 建议修改

发现有明确证据的问题，建议核对并处理。

已确认 1 个问题，其中 1 个已添加到对应代码行。

<details>
<summary>变更概览</summary>

本次变更主要包含：

- 在分布式任务管理器生命周期中接入 Docker 容器准备逻辑：run\(\) 在初始化前通过 duck-typing 调用 prepare\_containers 为全部训练节点批量准备容器，失败则抛异常终止；\_start\_training\(\) 重启训练前对替换进来的节点调用 prepare\_new\_containers，准备失败时释放节点并等待后重试主循环。
- 新增 DockerLauncher 类（继承 MPIRunLauncher），用于 mpirun + docker 启动模式；构造时解析 MPI\_TCP\_IF\_INCLUDE、MPI\_RANK\_ENV、MPI\_FORWARD\_ENV、DOCKER\_STOP\_PATTERN 等环境变量，配置 TCP 网卡过滤、各 rank 一致的环境变量组合、需向容器内转发环境变量及停止进程匹配模式。
- 新增 Docker 启动器的容器准备与 mpirun 命令构建逻辑：通过 clush 在各主机并发创建或复用训练容器，并用 mca\_base\_env\_list 及 OMPI/PRTE 环境变量导出配置 rank 环境与网络接口。
- 新增 docker\_launcher 的环境变量处理逻辑：构建 shell 导出片段，将 rank\_env 变量导出并通过 OMPI/PRTE 的 mca\_base\_env\_list 把 forward\_env 指定的变量转发给容器内 mpirun 子进程；同时新增 start 方法，在 manager 启动时 prepared 的首台主机容器内启动训练脚本。

</details>

<details>
<summary>文件审查摘要</summary>

| 文件 | 变更 | 审查结果 |
| --- | --- | --- |
| <code>cluster_manager/examples/start_docker.sh</code> | 新增 · +56/-0 | P3 × 1 |
| <code>cluster_manager/test/unit/test_docker_launcher.py</code> | 新增 · +404/-0 | — |
| <code>cluster_manager/cluster_manager/launcher/docker_launcher.py</code> | 新增 · +316/-0 | — |
| <code>cluster_manager/cluster_manager/launcher/mpirun_launcher.py</code> | 修改 · +242/-5 | — |
| <code>cluster_manager/test/unit/test_job_lifecycle.py</code> | 修改 · +78/-0 | — |
| <code>cluster_manager/test/unit/test_launcher_monitor_resilience.py</code> | 修改 · +56/-3 | — |
| <code>cluster_manager/docs/config_guide.md</code> | 修改 · +51/-1 | — |
| <code>cluster_manager/cluster_manager/controller/distributed_job_manager.py</code> | 修改 · +35/-0 | — |
| <code>cluster_manager/README.md</code> | 修改 · +26/-3 | — |
| <code>cluster_manager/test/unit/test_runtime_context_faults.py</code> | 修改 · +25/-2 | — |
| <code>cluster_manager/test/unit/test_distributed_job_manager.py</code> | 修改 · +24/-1 | — |
| <code>cluster_manager/cluster_manager/node_management/node_pool.py</code> | 修改 · +3/-21 | — |
| <code>cluster_manager/cluster_manager/main.py</code> | 修改 · +16/-1 | — |
| <code>cluster_manager/cluster_manager/runtime/job_state_machine.py</code> | 修改 · +16/-0 | — |
| <code>cluster_manager/cluster_manager/launcher/launcher_factory.py</code> | 修改 · +9/-3 | — |
| <code>cluster_manager/cluster_manager/runtime/runtime_context.py</code> | 修改 · +11/-0 | — |
| <code>cluster_manager/test/unit/test_cluster_schedule.py</code> | 修改 · +4/-0 | — |

</details>

<details>
<summary>审查信息</summary>

- 变更统计：17 个文件，+1372/-40。
- 覆盖情况：共 17 个文件，已完整审查 17 个。
- 候选问题：1 项；证据复核过滤：0 项；发布前敏感信息保护：0 项。
- 本服务以 GitHub 提供的 PR diff 为审查主体，PR 描述与按相关性选取的仓库片段仅用于核验；未执行代码或重跑测试，结论仍需维护者核验。

</details>
提交修复并推送新 commit 后，将自动审查 PR 的最新版本。

- zhougf-zhiAn · APPROVED · 2026-10-10T07:07:21Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#pullrequestreview-5478074063)

(No body; status only.)

- hygon-ai-reviewer[bot] · COMMENTED · 2026-10-10T07:08:19Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#pullrequestreview-5478077038)

<!-- github-ai-review:v1:3:d75a6bcb16696905d7a5a91eb29ca6140778e8ea:c327c7324c54da67fe69b45d -->
## AI Review

### 🟡 建议修改

发现有明确证据的问题，建议核对并处理。

已确认 2 个问题，其中 0 个已添加到对应代码行。

<details>
<summary>变更概览</summary>

本次变更主要包含：

- README 新增 Docker 训练路径说明：引入预创建容器 + hostfile/Docker exec 生产路径，补充以 CLUSTER\_LAUNCH\_MODE=docker 为核心的容器名、容器内路径、容器 SSH 端口等配置项及停止/挂载行为约定。
- 为 Docker 启动模式新增容器准备逻辑：作业入口 run\(\) 在组件初始化前通过 launcher 的 prepare\_containers 预建容器，失败即抛错终止；\_start\_training 中检测 NodePool 替换出的新节点并调用 prepare\_new\_containers 补建容器，失败时释放节点并休眠后重试。
- 新增 DockerLauncher 启动器，用于 mpirun+docker 模式：按节点准备容器后在容器内运行训练脚本，初始化时从环境变量读取 TCP 网卡过滤、各 rank 需一致的环境变量键值对、需向对端转发的环境变量名及停止脚本的进程匹配模式，并定义停止脚本的自身保护标记。
- 新增 Docker 启动器逻辑：通过 clush 在每台主机上并行执行容器准备命令，确保每台主机有一个就绪的训练容器，支持仅补建缺失容器的节点恢复路径，并构建 mpirun 分发命令及跨 rank 环境变量导出片段。

</details>

<details>
<summary>文件审查摘要</summary>

| 文件 | 变更 | 审查结果 |
| --- | --- | --- |
| <code>cluster_manager/cluster_manager/launcher/docker_launcher.py</code> | 新增 · +316/-0 | P2 × 2 |
| <code>cluster_manager/test/unit/test_docker_launcher.py</code> | 新增 · +404/-0 | — |
| <code>cluster_manager/cluster_manager/launcher/mpirun_launcher.py</code> | 修改 · +251/-5 | — |
| <code>cluster_manager/test/unit/test_job_lifecycle.py</code> | 修改 · +78/-0 | — |
| <code>cluster_manager/test/unit/test_launcher_monitor_resilience.py</code> | 修改 · +61/-3 | — |
| <code>cluster_manager/examples/start_docker.sh</code> | 新增 · +61/-0 | — |
| <code>cluster_manager/docs/config_guide.md</code> | 修改 · +51/-1 | — |
| <code>cluster_manager/cluster_manager/controller/distributed_job_manager.py</code> | 修改 · +35/-0 | — |
| <code>cluster_manager/README.md</code> | 修改 · +26/-3 | — |
| <code>cluster_manager/test/unit/test_runtime_context_faults.py</code> | 修改 · +25/-2 | — |
| <code>cluster_manager/test/unit/test_distributed_job_manager.py</code> | 修改 · +24/-1 | — |
| <code>cluster_manager/cluster_manager/node_management/node_pool.py</code> | 修改 · +3/-21 | — |
| <code>cluster_manager/cluster_manager/main.py</code> | 修改 · +16/-1 | — |
| <code>cluster_manager/cluster_manager/runtime/job_state_machine.py</code> | 修改 · +16/-0 | — |
| <code>cluster_manager/cluster_manager/launcher/launcher_factory.py</code> | 修改 · +9/-3 | — |
| <code>cluster_manager/cluster_manager/runtime/runtime_context.py</code> | 修改 · +11/-0 | — |
| <code>cluster_manager/test/unit/test_cluster_schedule.py</code> | 修改 · +4/-0 | — |

</details>

<details>
<summary>无法定位到 diff 行的问题（2）</summary>

#### P2 · docker exec -d 分离启动使训练启动失败不可见

- 文件：<code>cluster_manager/cluster_manager/launcher/docker_launcher.py</code>（无法安全定位到当前 diff 行）
- 触发条件：容器内 exec\_path 不存在、work\_dir 目录缺失或训练脚本启动即报错（inner 含 set -eu 会立即退出）
- 证据与影响：remote\_cmd 使用 docker exec -d 分离执行 inner；-d 模式下 docker exec 创建 exec 后立即返回，不等待也不透传 inner 的退出码，而函数直接以该 ssh/docker 命令的执行结果作为返回值 启动握手命令几乎总是返回成功，训练命令实际启动失败会被当作启动成功上抛，调用方无法据此感知异常，问题需进入容器或查容器日志才能发现
- 修改建议：在同一条远程命令内先校验 exec\_path 与 work\_dir 存在，将训练输出重定向到容器内日志文件，或在返回前轮询 pgrep 确认进程存活，从而让失败可通过返回结果暴露

#### P2 · 追加 docker rm 使容器内停止脚本的失败退出码被掩盖

- 文件：<code>cluster_manager/cluster_manager/launcher/docker_launcher.py</code>（无法安全定位到当前 diff 行）
- 触发条件：remove\_container\_on\_stop=True 且不启用 reuse\_container 时，容器内停止 sweep 失败（例如容器已退出导致 docker exec 报错，或容器内进程清理失败）。
- 证据与影响：remote\_cmd 拼接为 "docker exec ... bash -lc &lt;sweep&gt;; docker rm -f ... &gt;/dev/null 2&gt;&amp;1 \|\| true"，末尾命令恒成功，远端 shell 退出码必为 0，clush 返回的 code 无法反映 sweep 的真实结果。不追加删除时则 eden 正常透传退出码，行为不一致。 code==0 使后面的失败日志永不触发，调用方判定停止成功；sweep 失败被静默吞掉，可能残留训练进程，恰是该模块注释所欲避免的阻塞下次启动的场景。
- 修改建议：先保存 sweep 退出码，清理后显式返回，例如在 remote\_cmd 中追加 "; rc=$?; docker rm -f ... &gt;/dev/null 2&gt;&amp;1 \|\| true; exit $rc"，使失败仍可通过 code 上报并记录日志。

</details>

<details>
<summary>审查信息</summary>

- 变更统计：17 个文件，+1391/-40。
- 覆盖情况：共 17 个文件，已完整审查 17 个。
- 候选问题：2 项；证据复核过滤：0 项；发布前敏感信息保护：0 项。
- 本服务以 GitHub 提供的 PR diff 为审查主体，PR 描述与按相关性选取的仓库片段仅用于核验；未执行代码或重跑测试，结论仍需维护者核验。

</details>
提交修复并推送新 commit 后，将自动审查 PR 的最新版本。

### issue_comments

- hygon-ai-reviewer[bot] · comment · 2026-09-24T09:56:56Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5811930298)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

审查尚未完整完成，无法给出整体结论；当前没有可发布的已确认问题，不代表代码没有问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 0 个，待审查 16 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T09:58:22Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5811952119)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

审查尚未完整完成，无法给出整体结论；当前没有可发布的已确认问题，不代表代码没有问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 2 个，部分审查 1 个，待审查 13 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:00:27Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5811985484)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

审查尚未完整完成，无法给出整体结论；当前没有可发布的已确认问题，不代表代码没有问题。

> 部分结果不可用：1/10 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 2 个，部分审查 2 个，待审查 12 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:00:30Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5811986328)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

审查尚未完整完成，无法给出整体结论；当前没有可发布的已确认问题，不代表代码没有问题。

> 部分结果不可用：2/10 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 2 个，部分审查 3 个，待审查 11 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:01:51Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5812005798)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

审查尚未完整完成，无法给出整体结论；当前没有可发布的已确认问题，不代表代码没有问题。

> 部分结果不可用：2/10 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 2 个，部分审查 3 个，待审查 11 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:03:55Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5812033166)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

审查尚未完整完成，无法给出整体结论；当前没有可发布的已确认问题，不代表代码没有问题。

> 部分结果不可用：2/10 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 2 个，部分审查 3 个，待审查 11 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:05:53Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5812060766)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

审查尚未完整完成，无法给出整体结论；当前没有可发布的已确认问题，不代表代码没有问题。

> 部分结果不可用：2/10 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 2 个，部分审查 3 个，待审查 11 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:07:07Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5812079902)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

审查尚未完整完成，无法给出整体结论；当前没有可发布的已确认问题，不代表代码没有问题。

> 部分结果不可用：1/10 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 4 个，部分审查 1 个，待审查 11 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:14:14Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5812187299)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

发现 1 个问题。

### [P1] reuse\_existing=False 时引用未赋值变量导致启动失败

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py（行号未确定）
- 触发条件：以 reuse\_existing=False（不复用已有容器）路径调用该命令构建方法时。
- 证据与影响：return 的 f-string 无条件内插 \{reuse\_check\} 与 \{reuse\_end\}，但两者仅在 if reuse\_existing: 分支内赋值；else 分支只赋值 new\_container\_init，提供的片段中未见其他默认赋值。按 Python 局部变量规则，该路径在构造命令字符串时会抛 UnboundLocalError。 不复用容器的常规新建启动在命令生成阶段即抛异常，Docker 启动功能不可用。
- 修改建议：在进入 if 前为 reuse\_check、reuse\_end 提供空字符串默认值，或仅按 reuse\_existing 条件拼接这两段；建议结合完整函数核验是否已有前置赋值。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 4 个，部分审查 1 个，待审查 11 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:16:04Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5812211236)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

发现 1 个问题。

### [P1] reuse\_existing=False 时引用未赋值变量导致启动失败

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py（行号未确定）
- 触发条件：以 reuse\_existing=False（不复用已有容器）路径调用该命令构建方法时。
- 证据与影响：return 的 f-string 无条件内插 \{reuse\_check\} 与 \{reuse\_end\}，但两者仅在 if reuse\_existing: 分支内赋值；else 分支只赋值 new\_container\_init，提供的片段中未见其他默认赋值。按 Python 局部变量规则，该路径在构造命令字符串时会抛 UnboundLocalError。 不复用容器的常规新建启动在命令生成阶段即抛异常，Docker 启动功能不可用。
- 修改建议：在进入 if 前为 reuse\_check、reuse\_end 提供空字符串默认值，或仅按 reuse\_existing 条件拼接这两段；建议结合完整函数核验是否已有前置赋值。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 8 个，部分审查 1 个，待审查 7 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:18:21Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5812240807)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

发现 1 个问题。

### [P1] reuse\_existing=False 时引用未赋值变量导致启动失败

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py（行号未确定）
- 触发条件：以 reuse\_existing=False（不复用已有容器）路径调用该命令构建方法时。
- 证据与影响：return 的 f-string 无条件内插 \{reuse\_check\} 与 \{reuse\_end\}，但两者仅在 if reuse\_existing: 分支内赋值；else 分支只赋值 new\_container\_init，提供的片段中未见其他默认赋值。按 Python 局部变量规则，该路径在构造命令字符串时会抛 UnboundLocalError。 不复用容器的常规新建启动在命令生成阶段即抛异常，Docker 启动功能不可用。
- 修改建议：在进入 if 前为 reuse\_check、reuse\_end 提供空字符串默认值，或仅按 reuse\_existing 条件拼接这两段；建议结合完整函数核验是否已有前置赋值。

> 部分结果不可用：1/10 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 8 个，部分审查 2 个，待审查 6 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:19:46Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5812259911)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

发现 1 个问题。

### [P1] reuse\_existing=False 时引用未赋值变量导致启动失败

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py（行号未确定）
- 触发条件：以 reuse\_existing=False（不复用已有容器）路径调用该命令构建方法时。
- 证据与影响：return 的 f-string 无条件内插 \{reuse\_check\} 与 \{reuse\_end\}，但两者仅在 if reuse\_existing: 分支内赋值；else 分支只赋值 new\_container\_init，提供的片段中未见其他默认赋值。按 Python 局部变量规则，该路径在构造命令字符串时会抛 UnboundLocalError。 不复用容器的常规新建启动在命令生成阶段即抛异常，Docker 启动功能不可用。
- 修改建议：在进入 if 前为 reuse\_check、reuse\_end 提供空字符串默认值，或仅按 reuse\_existing 条件拼接这两段；建议结合完整函数核验是否已有前置赋值。

> 部分结果不可用：1/10 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 8 个，部分审查 2 个，待审查 6 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:26:52Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5812356770)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

发现 2 个问题。

### [P1] reuse\_existing=False 时引用未赋值变量导致启动失败

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py（行号未确定）
- 触发条件：以 reuse\_existing=False（不复用已有容器）路径调用该命令构建方法时。
- 证据与影响：return 的 f-string 无条件内插 \{reuse\_check\} 与 \{reuse\_end\}，但两者仅在 if reuse\_existing: 分支内赋值；else 分支只赋值 new\_container\_init，提供的片段中未见其他默认赋值。按 Python 局部变量规则，该路径在构造命令字符串时会抛 UnboundLocalError。 不复用容器的常规新建启动在命令生成阶段即抛异常，Docker 启动功能不可用。
- 修改建议：在进入 if 前为 reuse\_check、reuse\_end 提供空字符串默认值，或仅按 reuse\_existing 条件拼接这两段；建议结合完整函数核验是否已有前置赋值。

### [P2] docker 模式 stop 命令引号在本地 shell 与 clush 参数拼接层丢失，容器内终止/清理逻辑与意图不符

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py:249
- 触发条件：docker\_enabled 为真且调用 stop\(\)（hostfile 非空）时，构造的 clush 命令交给本地 shell 执行。
- 证据与影响：cmd 形如 clush --hostfile 'hf' -b docker exec '名' bash -lc 'inner'；本地 shell 会剥掉 shlex.quote 产生的引号，clush 将剩余参数按空格拼接为远端命令且不重新加引号，于是 inner 中的 ';' 由宿主机远端 shell 解释：bash -lc 实际只接到 pkill，后续 pkill -KILL、docker rm 变为逐条在宿主机执行。 容器内进程不会被优雅 TERM 停止（bash -c 'pkill' 缺少参数报错被 \|\| true 掩盖）；docker rm -f 等靠分隔符错误落在宿主机 shell 才碰巧生效，remove\_container\_on\_stop 的行为依赖该巧合且部分子命令被丢弃。
- 修改建议：对 inner 做两层引号转义（如 inner 外再 shlex.quote 一次）以保证作为单一参数到达容器内 bash，或改为按条直接通过 clush 执行对应 docker 命令，并人工验证远端实际收到的命令串。

> 部分结果不可用：1/10 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 8 个，部分审查 2 个，待审查 6 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:29:14Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5812386440)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

发现 2 个问题。

### [P1] reuse\_existing=False 时引用未赋值变量导致启动失败

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py（行号未确定）
- 触发条件：以 reuse\_existing=False（不复用已有容器）路径调用该命令构建方法时。
- 证据与影响：return 的 f-string 无条件内插 \{reuse\_check\} 与 \{reuse\_end\}，但两者仅在 if reuse\_existing: 分支内赋值；else 分支只赋值 new\_container\_init，提供的片段中未见其他默认赋值。按 Python 局部变量规则，该路径在构造命令字符串时会抛 UnboundLocalError。 不复用容器的常规新建启动在命令生成阶段即抛异常，Docker 启动功能不可用。
- 修改建议：在进入 if 前为 reuse\_check、reuse\_end 提供空字符串默认值，或仅按 reuse\_existing 条件拼接这两段；建议结合完整函数核验是否已有前置赋值。

### [P2] docker 模式 stop 命令引号在本地 shell 与 clush 参数拼接层丢失，容器内终止/清理逻辑与意图不符

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py:249
- 触发条件：docker\_enabled 为真且调用 stop\(\)（hostfile 非空）时，构造的 clush 命令交给本地 shell 执行。
- 证据与影响：cmd 形如 clush --hostfile 'hf' -b docker exec '名' bash -lc 'inner'；本地 shell 会剥掉 shlex.quote 产生的引号，clush 将剩余参数按空格拼接为远端命令且不重新加引号，于是 inner 中的 ';' 由宿主机远端 shell 解释：bash -lc 实际只接到 pkill，后续 pkill -KILL、docker rm 变为逐条在宿主机执行。 容器内进程不会被优雅 TERM 停止（bash -c 'pkill' 缺少参数报错被 \|\| true 掩盖）；docker rm -f 等靠分隔符错误落在宿主机 shell 才碰巧生效，remove\_container\_on\_stop 的行为依赖该巧合且部分子命令被丢弃。
- 修改建议：对 inner 做两层引号转义（如 inner 外再 shlex.quote 一次）以保证作为单一参数到达容器内 bash，或改为按条直接通过 clush 执行对应 docker 命令，并人工验证远端实际收到的命令串。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 10 个，部分审查 1 个，待审查 5 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:32:22Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5812427917)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

发现 3 个问题。

### [P1] reuse\_existing=False 时引用未赋值变量导致启动失败

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py（行号未确定）
- 触发条件：以 reuse\_existing=False（不复用已有容器）路径调用该命令构建方法时。
- 证据与影响：return 的 f-string 无条件内插 \{reuse\_check\} 与 \{reuse\_end\}，但两者仅在 if reuse\_existing: 分支内赋值；else 分支只赋值 new\_container\_init，提供的片段中未见其他默认赋值。按 Python 局部变量规则，该路径在构造命令字符串时会抛 UnboundLocalError。 不复用容器的常规新建启动在命令生成阶段即抛异常，Docker 启动功能不可用。
- 修改建议：在进入 if 前为 reuse\_check、reuse\_end 提供空字符串默认值，或仅按 reuse\_existing 条件拼接这两段；建议结合完整函数核验是否已有前置赋值。

### [P2] docker 模式 stop 命令引号在本地 shell 与 clush 参数拼接层丢失，容器内终止/清理逻辑与意图不符

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py:249
- 触发条件：docker\_enabled 为真且调用 stop\(\)（hostfile 非空）时，构造的 clush 命令交给本地 shell 执行。
- 证据与影响：cmd 形如 clush --hostfile 'hf' -b docker exec '名' bash -lc 'inner'；本地 shell 会剥掉 shlex.quote 产生的引号，clush 将剩余参数按空格拼接为远端命令且不重新加引号，于是 inner 中的 ';' 由宿主机远端 shell 解释：bash -lc 实际只接到 pkill，后续 pkill -KILL、docker rm 变为逐条在宿主机执行。 容器内进程不会被优雅 TERM 停止（bash -c 'pkill' 缺少参数报错被 \|\| true 掩盖）；docker rm -f 等靠分隔符错误落在宿主机 shell 才碰巧生效，remove\_container\_on\_stop 的行为依赖该巧合且部分子命令被丢弃。
- 修改建议：对 inner 做两层引号转义（如 inner 外再 shlex.quote 一次）以保证作为单一参数到达容器内 bash，或改为按条直接通过 clush 执行对应 docker 命令，并人工验证远端实际收到的命令串。

### [P2] DOCKER\_CONTAINER\_SSH\_PORT 误用 MPIRUN\_PLM\_RSH\_ARGS 作为默认值

- 位置：cluster\_manager/examples/start\_docker.sh:18
- 触发条件：环境中已设置 MPIRUN\_PLM\_RSH\_ARGS（通常承载 mpirun rsh 参数而非端口号）时执行本脚本。
- 证据与影响：export DOCKER\_CONTAINER\_SSH\_PORT="$\{MPIRUN\_PLM\_RSH\_ARGS:-36000\}" 是脚本中唯一赋值变量与默认值来源变量不一致的行，其余均为 $\{同名校验默认\} 模式，疑似复制粘贴错误。 非数值的 rsh 参数字符串会作为容器 SSH 端口使用，导致 Docker 模式下 ssh 连接容器失败，训练启动流程中断。
- 修改建议：改为 export DOCKER\_CONTAINER\_SSH\_PORT="$\{DOCKER\_CONTAINER\_SSH\_PORT:-36000\}"，如需兼容旧变量另行显式转换并校验为数字。

> 部分结果不可用：1/10 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 10 个，部分审查 3 个，待审查 3 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-09-24T10:34:54Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-5812461744)

<!-- github-ai-reviewer-progress:3:bde222b17614e7c8c82c7d722bb4041516386798 -->
## AI Review

发现 4 个问题。

### [P1] reuse\_existing=False 时引用未赋值变量导致启动失败

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py（行号未确定）
- 触发条件：以 reuse\_existing=False（不复用已有容器）路径调用该命令构建方法时。
- 证据与影响：return 的 f-string 无条件内插 \{reuse\_check\} 与 \{reuse\_end\}，但两者仅在 if reuse\_existing: 分支内赋值；else 分支只赋值 new\_container\_init，提供的片段中未见其他默认赋值。按 Python 局部变量规则，该路径在构造命令字符串时会抛 UnboundLocalError。 不复用容器的常规新建启动在命令生成阶段即抛异常，Docker 启动功能不可用。
- 修改建议：在进入 if 前为 reuse\_check、reuse\_end 提供空字符串默认值，或仅按 reuse\_existing 条件拼接这两段；建议结合完整函数核验是否已有前置赋值。

### [P2] docker 模式 stop 命令引号在本地 shell 与 clush 参数拼接层丢失，容器内终止/清理逻辑与意图不符

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py:249
- 触发条件：docker\_enabled 为真且调用 stop\(\)（hostfile 非空）时，构造的 clush 命令交给本地 shell 执行。
- 证据与影响：cmd 形如 clush --hostfile 'hf' -b docker exec '名' bash -lc 'inner'；本地 shell 会剥掉 shlex.quote 产生的引号，clush 将剩余参数按空格拼接为远端命令且不重新加引号，于是 inner 中的 ';' 由宿主机远端 shell 解释：bash -lc 实际只接到 pkill，后续 pkill -KILL、docker rm 变为逐条在宿主机执行。 容器内进程不会被优雅 TERM 停止（bash -c 'pkill' 缺少参数报错被 \|\| true 掩盖）；docker rm -f 等靠分隔符错误落在宿主机 shell 才碰巧生效，remove\_container\_on\_stop 的行为依赖该巧合且部分子命令被丢弃。
- 修改建议：对 inner 做两层引号转义（如 inner 外再 shlex.quote 一次）以保证作为单一参数到达容器内 bash，或改为按条直接通过 clush 执行对应 docker 命令，并人工验证远端实际收到的命令串。

### [P2] DOCKER\_CONTAINER\_SSH\_PORT 误用 MPIRUN\_PLM\_RSH\_ARGS 作为默认值

- 位置：cluster\_manager/examples/start\_docker.sh:18
- 触发条件：环境中已设置 MPIRUN\_PLM\_RSH\_ARGS（通常承载 mpirun rsh 参数而非端口号）时执行本脚本。
- 证据与影响：export DOCKER\_CONTAINER\_SSH\_PORT="$\{MPIRUN\_PLM\_RSH\_ARGS:-36000\}" 是脚本中唯一赋值变量与默认值来源变量不一致的行，其余均为 $\{同名校验默认\} 模式，疑似复制粘贴错误。 非数值的 rsh 参数字符串会作为容器 SSH 端口使用，导致 Docker 模式下 ssh 连接容器失败，训练启动流程中断。
- 修改建议：改为 export DOCKER\_CONTAINER\_SSH\_PORT="$\{DOCKER\_CONTAINER\_SSH\_PORT:-36000\}"，如需兼容旧变量另行显式转换并校验为数字。

### [P3] 测试名声称验证调用顺序但断言未检查顺序

- 位置：cluster\_manager/test/unit/test\_distributed\_job\_manager.py:146
- 触发条件：若实现将 launcher.start 提前到 prepare\_new\_containers 之前调用（顺序回归），或在调用二者之间插入了缺失 prepare 的错误路径
- 证据与影响：prepare\_new\_containers 与 start 是两个独立的 MagicMock，assert\_called\_once\_with 只校验各自被调用一次及参数，不校验相互顺序；即使 start 先于 prepare 被调用，两条断言仍全部通过 测试无法覆盖其名称中 before launch 所声称的行为，调用顺序回归时仍通过，可能掩盖先启动后准备、容器未就绪即启动训练的缺陷
- 修改建议：通过 attach\_mock 将两个方法挂到统一父 Mock 或用 side\_effect 记录调用序列，再断言 prepare\_new\_containers 的调用记录先于 launcher.start

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 16 个文件，已审查 12 个，部分审查 1 个，待审查 3 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-10-10T03:14:54Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-6093201103)

<!-- github-ai-reviewer-progress:3:d1a29535b6a9fe19397c179c95f5202ad15462b4 -->
## AI Review

审查尚未完整完成，无法给出整体结论；当前没有可发布的已确认问题，不代表代码没有问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 17 个文件，已审查 0 个，部分审查 1 个，待审查 16 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-10-10T03:17:19Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-6093220299)

<!-- github-ai-reviewer-progress:3:b6e7559b4337f9377cd3d2e55e0acb331211584b -->
## AI Review

发现 1 个问题。

### [P2] 容器只读挂载宿主机整个 /root/.ssh，向容器内暴露 root SSH 凭据

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py:38
- 触发条件：宿主机 /root/.ssh 中存在 root 的 SSH 私钥等文件（集群免密登录场景普遍存在），且用户作业在容器内执行时。
- 证据与影响：mounts += " -v /opt/hyhal:/opt/hyhal:ro -v /root/.ssh:/root/.ssh:ro" 把宿主机整个 /root/.ssh 挂入容器；只读仅防止容器写入，并不限制读取目录内其他文件（如私钥）。 容器内运行的作业进程或被攻破的容器可读取宿主机 root 的 SSH 私钥并外带，进而在集群节点间横向越权，超出验证 authorized\_keys 的所需最小权限。
- 修改建议：仅挂载容器启动 sshd 所需的 authorized\_keys 文件到容器内专用路径，或为容器单独分发密钥，避免整目录暴露宿主机凭据。

> 部分结果不可用：1/10 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 17 个文件，已审查 8 个，部分审查 2 个，待审查 7 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-10-10T05:45:34Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-6094332315)

<!-- github-ai-reviewer-progress:3:629618d5b2c41bbd4ae169041f5794304f5388a6 -->
## AI Review

发现 2 个问题。

### [P1] 整目录只读挂载宿主机 root 的 .ssh 目录，私钥暴露给容器

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py（行号未确定）
- 触发条件：Docker MPI 启动路径每次准备容器时都无条件应用该挂载；容器内运行用户作业代码即可读取其内容。
- 证据与影响：\_docker\_prepare\_command 中新增 mounts += " -v /opt/hyhal:/opt/hyhal:ro -v /root/.ssh:/root/.ssh:ro"，将宿主机 root 的整个 .ssh 目录挂入容器；注释仅说明防止容器向该目录写入（copy keys into it），并未限制容器读取目录内容。 容器内以作业身份运行的进程可读取宿主机 root 的 SSH 私钥等文件，在多用户集群中可导致密钥泄露并横向接管宿主机或其他节点。
- 修改建议：仅将容器 SSH 登录所需的 authorized\_keys 单文件注入或挂载进容器，避免整目录挂载 host 的 .ssh；如保持现状需人工评估宿主机私钥暴露风险并做测试。

### [P2] 容器内 pkill -f 会匹配到包装 shell 自身，KILL 兜底阶段无法执行

- 位置：cluster\_manager/cluster\_manager/launcher/mpirun\_launcher.py（行号未确定）
- 触发条件：docker\_enabled 为真且调用 stop 停止容器内训练进程的正常流程。
- 证据与影响：inner 命令为 bash -lc 'pkill -TERM -f &lt;pattern&gt; \|\| true; sleep 2; pkill -KILL -f &lt;pattern&gt; \|\| true'，该 bash 进程的完整命令行本身包含 pattern（默认 python）；pkill -f 按整条命令行匹配且只排除自身、不排除父进程，bash 会收到 TERM。 父 bash 收到 TERM 后随之终止，脚本在第一个 pkill 后中断，sleep 2 与 pkill -KILL 兜底不再执行；仅 SIGTERM 存活的残留训练进程不会被强杀，停止不彻底。
- 修改建议：避免模式自匹配：如将以 pgrep -f 列出 PID 并排除包装 shell 自身/父进程后逐个 kill，或将 pkill 逻辑放入容器内脚本执行，使包装 shell 的命令行不含目标 pattern。

> 部分结果不可用：1/10 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 17 个文件，已审查 8 个，部分审查 2 个，待审查 7 个。

> 进度已保存。正在继续处理。

- hygon-ai-reviewer[bot] · comment · 2026-10-10T06:19:46Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#issuecomment-6094590556)

<!-- github-ai-reviewer-progress:3:03b73473ce3d81af77d2e3dd2c1294d07d5c0590 -->
## AI Review

审查尚未完整完成，无法给出整体结论；当前没有可发布的已确认问题，不代表代码没有问题。

> 部分结果不可用：1/10 批未完整完成，已保留可用问题。

> 审查未完整完成：以 GitHub 返回的 PR diff 为主体，关联上下文仅用于核验，未运行代码。

> 覆盖情况：共 17 个文件，已审查 2 个，部分审查 3 个，待审查 12 个。

> 进度已保存。正在继续处理。

### inline_comments

- hygon-ai-reviewer[bot] · comment · 2026-09-30T09:31:24Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#discussion_r4143072870)

File: `cluster_manager/examples/start_docker.sh` · line 51

**P3 · HOSTFILE 相对路径校验与实际执行目录不一致**

**触发条件：** 用户以相对路径传入 HOSTFILE（如 ./hosts）且相对路径仅相对脚本启动时的目录可读。

**证据与影响：** 第34行在当前目录用 \[\[ -r $\{HOSTFILE\} \]\] 校验通过后，第42行执行 cd "$\{SCRIPT\_DIR\}/.." 切换工作目录，再以同一相对路径 --hostfile "$\{HOSTFILE\}" 启动子进程，校验目录与消费目录不同。 校验在原目录通过，但子进程在新工作目录下打开相对路径失败，主程序启动即报 hostfile 不存在，脚本的可读性检查形同虚设。

**修改建议：** 在校验前将 HOSTFILE 解析为绝对路径（如 readlink -f 或 dirname/basename + pwd 拼接）再校验并传给子进程。

- hygon-ai-reviewer[bot] · comment · 2026-10-10T04:27:45Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#discussion_r4236379375)

File: `cluster_manager/cluster_manager/launcher/mpirun_launcher.py` · line None

**P2 · Docker 停止命令会误杀自身 shell，硬杀兜底不可达**

**触发条件：** docker\_enabled 下调用 stop，且容器内存在不响应 SIGTERM、需要强制终止的匹配进程

**证据与影响：** inner 经 bash -lc 执行，其字符串本身包含模式文本（默认 python），运行 pkill 的 bash 进程命令行同样包含该文本，会被 pkill -f 匹配；第一次 pkill -TERM 会向该 bash 发送 TERM，bash 退出后 sleep 2 与 pkill -KILL 均不会执行 TERM 无效时 KILL 兜底永不触发，进程无法被强制结束；当 remove\_container\_on\_stop 关闭时残留进程持续占用资源，停止失败

**修改建议：** 使运行 shell 的命令行不包含字面模式，例如通过环境变量传递模式（docker exec -e PATTERN=... bash -lc 'pkill -f "$PATTERN" ...'）或等效方式，保证 TERM/KILL 两段均可执行

- hygon-ai-reviewer[bot] · comment · 2026-10-10T05:04:45Z · [source](https://github.com/HYGON-AI/cluster-manager-das/pull/3#discussion_r4236491289)

File: `cluster_manager/examples/start_docker.sh` · line 45

**P3 · 相对路径 LOG\_DIR 在 cd 前后解析不一致，可能导致管理进程未启动且脚本退出码为 0**

**触发条件：** 调用方以相对路径设置 LOG\_DIR（如 LOG\_DIR=logs ./start\_docker.sh）运行脚本。

**证据与影响：** 第 45 行 mkdir -p "$\{LOG\_DIR\}" 在第 46 行 cd "$\{SCRIPT\_DIR\}/.." 之前执行，目录创建在调用方工作目录；而第 56 行重定向 &gt;&gt; "$\{LOG\_DIR\}/cluster\_manager.log" 在 cd 之后解析，指向项目目录下不存在的路径。同文件的 HOSTFILE 已做绝对路径归一，LOG\_DIR 未处理。 nohup 命令因重定向目录不存在而失败，main.py 不会运行；异步列表使脚本仍以 0 退出，部署方误以为启动成功且日志目录为空。

**修改建议：** 在 cd 之前将 LOG\_DIR 转为绝对路径（参照 HOSTFILE 的处理：先 mkdir 再用 cd/pwd 归一），或在重定向前确保目标目录存在并校验退出状态。

## Changed files and fixed code

- `cluster_manager/README.md` · modified · additions 26 / deletions 3
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/README.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/README.md)
- `cluster_manager/cluster_manager/controller/distributed_job_manager.py` · modified · additions 35 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/cluster_manager/controller/distributed_job_manager.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/cluster_manager/controller/distributed_job_manager.py)
- `cluster_manager/cluster_manager/launcher/docker_launcher.py` · added · additions 316 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/cluster_manager/launcher/docker_launcher.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/cluster_manager/launcher/docker_launcher.py)
- `cluster_manager/cluster_manager/launcher/launcher_factory.py` · modified · additions 9 / deletions 3
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/cluster_manager/launcher/launcher_factory.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/cluster_manager/launcher/launcher_factory.py)
- `cluster_manager/cluster_manager/launcher/mpirun_launcher.py` · modified · additions 251 / deletions 5
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/cluster_manager/launcher/mpirun_launcher.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/cluster_manager/launcher/mpirun_launcher.py)
- `cluster_manager/cluster_manager/main.py` · modified · additions 16 / deletions 1
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/cluster_manager/main.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/cluster_manager/main.py)
- `cluster_manager/cluster_manager/node_management/node_pool.py` · modified · additions 3 / deletions 21
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/cluster_manager/node_management/node_pool.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/cluster_manager/node_management/node_pool.py)
- `cluster_manager/cluster_manager/runtime/job_state_machine.py` · modified · additions 16 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/cluster_manager/runtime/job_state_machine.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/cluster_manager/runtime/job_state_machine.py)
- `cluster_manager/cluster_manager/runtime/runtime_context.py` · modified · additions 11 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/cluster_manager/runtime/runtime_context.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/cluster_manager/runtime/runtime_context.py)
- `cluster_manager/docs/config_guide.md` · modified · additions 51 / deletions 1
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/docs/config_guide.md)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/docs/config_guide.md)
- `cluster_manager/examples/start_docker.sh` · added · additions 61 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/examples/start_docker.sh)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/examples/start_docker.sh)
- `cluster_manager/test/unit/test_cluster_schedule.py` · modified · additions 4 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/test/unit/test_cluster_schedule.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/test/unit/test_cluster_schedule.py)
- `cluster_manager/test/unit/test_distributed_job_manager.py` · modified · additions 24 / deletions 1
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/test/unit/test_distributed_job_manager.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/test/unit/test_distributed_job_manager.py)
- `cluster_manager/test/unit/test_docker_launcher.py` · added · additions 404 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/test/unit/test_docker_launcher.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/test/unit/test_docker_launcher.py)
- `cluster_manager/test/unit/test_job_lifecycle.py` · modified · additions 78 / deletions 0
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/test/unit/test_job_lifecycle.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/test/unit/test_job_lifecycle.py)
- `cluster_manager/test/unit/test_launcher_monitor_resilience.py` · modified · additions 61 / deletions 3
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/test/unit/test_launcher_monitor_resilience.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/test/unit/test_launcher_monitor_resilience.py)
- `cluster_manager/test/unit/test_runtime_context_faults.py` · modified · additions 25 / deletions 2
  - [head](https://github.com/HYGON-AI/cluster-manager-das/blob/d75a6bcb16696905d7a5a91eb29ca6140778e8ea/cluster_manager/test/unit/test_runtime_context_faults.py)
  - [base](https://github.com/HYGON-AI/cluster-manager-das/blob/755688d2e5d2ee1ada179687c58843f9ef754ae6/cluster_manager/test/unit/test_runtime_context_faults.py)

## Evidence and interpretation boundary

[Original JSON, discussions and patches](../../evidence/prs/HYGON-AI--cluster-manager-das/3-dea1db40627a505aa6e7e26bbba6087406dc8bc85e92fc1344669250ecf820a5.json) · SHA-256 `dea1db40627a505aa6e7e26bbba6087406dc8bc85e92fc1344669250ecf820a5`.

Diff complete: True. Missing/binary/truncated patches require pinned source inspection. This is a source page, not an independently verified optimization case. Open, merged and released are different states; recheck the deployed dependency.
