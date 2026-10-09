# 本地编辑与远程执行

## 私有目录建议

```text
private-workspace/
  sites/                连接及命令卡，不存入 public Git
  development/          实际 fork/分支/worktree，保留用户 patch
  references/           官方和第三方只读源码
  tasks/<task>/         任务状态、objects、runs、events、watch
  transfer/             不可变代码 bundle
```

HCU-Knowledge 的缓存目录不用于开发或 PR。先 fetch 所选真实活跃分支，记录 `git status`、origin/upstream、SHA 与子模块，绝不为更新删除用户改动。

## 快照与同步

```bash
hcu-trainflow --workspace /private/controller source-snapshot /private/development/model train.py src
hcu-trainflow --workspace /private/controller source-bundle SNAPSHOT_SHA /private/transfer/code.zip
scp /private/transfer/code.zip site:/private/transfer/code.zip
```

远端安装本包轻量运行依赖后：

```bash
hcu-trainflow --workspace /private/remote source-receive /private/transfer/code.zip /private/runs/SNAPSHOT_SHA
```

receiver 验证 manifest、文件集、路径、大小和每个 SHA，再建立新目录；不覆盖运行中的目录。bundle 只选源码，模型/数据/凭据不要加入。git HEAD 不能代表有未提交改动的工作树，实际快照以选中文件字节为准。

## 命令卡

`command-plan` 仅生成计划；`command-run task operation card lease` 执行。backend 为 local、ssh、ssh-docker、ssh-slurm 或 k8s。Docker 使用已存在的容器；Slurm 使用现有 allocation；K8s 使用明确 namespace/pod/container。它们是通用传输适配，部署前仍需核对 job、Pod UID、容器镜像和设备绑定。

Conda/裸机可直接给绝对解释器；需要 activation 时仅用已核实的绝对 POSIX 脚本。远端命令在快照目录执行，日志保留私有证据。不要把本地路径当远端路径。

## 中断与重试

operation ID 不重复执行已完成请求。超时、SSH 断线或 started 状态残留需核对远端进程、job 和输出，上传证据后 `operation-reconcile`。不能只换一个 operation ID 就重发训练。Python fencing 防止本工作区的过期拥有者发新动作；跨机器的真实运行隔离还依赖站点调度器。

核销未知操作后仍保留其超时预算占用，记为 `budget_seconds`；不会因为缺少本地主控的耗时结果就按零计费。这是保守预算核算，不是伪造的远程实测耗时。任务总预算和 assignment 预算都遵循此规则。资源被领取中的 assignment 整体预约时，无 assignment 身份的主控命令也不能绕过预约。
