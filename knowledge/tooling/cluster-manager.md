---
id: tooling/cluster-manager
title: HCU Cluster Manager：环境检查、运行控制与恢复边界
engine: tooling
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-and-document-reading
runtime_validated: false
reviewed_on: '2026-10-12'
sources:
- source: hygon-ai-cluster-manager-das
  path: README.md
  commit: 438847c1877cdce17cb524cb8825d49bd6917d6a
  sha256: efe4694924f4b21630b6e54f2dc49769db3d7c7db89314cbc8f01ba221d2a22f
- source: hygon-ai-cluster-manager-das
  path: hcu-envcheck/README.md
  commit: 438847c1877cdce17cb524cb8825d49bd6917d6a
  sha256: 985dd1a0189aa586a58d86c3dfbd4003fde8a060bb52442e086bdfbf7bababd9
- source: hygon-ai-cluster-manager-das
  path: hcu-envcheck/cluster_run/README.md
  commit: 438847c1877cdce17cb524cb8825d49bd6917d6a
  sha256: 694d4bd55b4cb627837552ed66caa353c9376190a2e9078684c17b09a65e7b06
- source: hygon-ai-cluster-manager-das
  path: hcu-envcheck/cluster_run/cli.py
  commit: 438847c1877cdce17cb524cb8825d49bd6917d6a
  sha256: 6f1dc6ce9a7b96c88666f456e2b3a5f1cdcff4a958899ef626eea27268812195
- source: hygon-ai-cluster-manager-das
  path: hcu-envcheck/pyproject.toml
  commit: 438847c1877cdce17cb524cb8825d49bd6917d6a
  sha256: 24f7607b6ced335b1edf06ba72500c062be7362894915cfbef075485cb77d518
- source: hygon-ai-cluster-manager-das
  path: cluster_manager/README.md
  commit: 438847c1877cdce17cb524cb8825d49bd6917d6a
  sha256: 6a4fe3655e97c824f6e2e3e430298db94a0612e4f5b25daeceef173bbfd42d34
- source: hygon-ai-cluster-manager-das
  path: cluster_manager/docs/architecture.md
  commit: 438847c1877cdce17cb524cb8825d49bd6917d6a
  sha256: c6d87768a1155701bfe83c7cd57927a7c38fd72be0835e74ae79a31944245f5f
- source: hygon-ai-cluster-manager-das
  path: hygon-ft-k8s/README.md
  commit: 438847c1877cdce17cb524cb8825d49bd6917d6a
  sha256: 7074aef14a60204b178ce2053c27c80e08d756bef2bf365e59a7223c578f4d07
- source: hygon-ai-cluster-manager-das
  path: stack-analyzer/README.md
  commit: 438847c1877cdce17cb524cb8825d49bd6917d6a
  sha256: 0c345c72dd25e4a14deb5acc21e14cadab301d73baa1aaf2f1582e451d7c28a7
---

# HCU Cluster Manager：环境检查、运行控制与恢复边界

## 定位与工程目录

本仓是多个独立子工程的集合，不是一个包装所有操作的容错命令。先按部署方式选择子工程，再看对应安装和源码。

| 目录 | 职责与问题入口 |
| --- | --- |
| `hcu-envcheck/bin/hcu-cluster-run` | 当前环境检查统一 Bash 入口，选择控制端 Python |
| `hcu-envcheck/cluster_run/` | CLI、节点分组、launcher、主动 payload、汇总与结果目录 |
| `hcu-envcheck/hcu_envcheck/` | 节点硬件、驱动、软件、网络/RDMA与资源探针 |
| `cluster_manager/cluster_manager/` | 单训练作业控制面：controller/runtime、节点池、launcher、monitor、event |
| `hygon-ft-k8s/` | Kubernetes Operator/Webhook/NodeHealth/训练 launcher 适配 |
| `stack-analyzer/` | 栈采集/分析工具，诊断取证与恢复控制分开 |

## 环境检查的新入口与安装

当前公开 HEAD `438847c1877cdce17cb524cb8825d49bd6917d6a` 中，hcu-envcheck 子工程对外入口为 **hcu-cluster-run**；旧 `hcu_envcheck/cli.py` 及旧 baremetal/k8s 子命令不能继续作为最新版配方。控制端 Python ≥3.10；目标探针和测试的解释器另用 `--remote-python` / `--test-python` 确认。可从源码使用 `bin/hcu-cluster-run --help`，先读该提交的 README、pyproject 与 CLI，而不是先全局安装旧包。

检查器接收分配好的 hostfile；它不替用户申请或管理 Slurm allocation。三种执行场景为 `shared-conda`、`node-local-conda`、`per-node-container`，不是旧 K8s 检查命令的别名。K8s 容错仍走同级 `hygon-ft-k8s`，不要因为检查入口收敛就宣称 K8s 容错被删除。

```bash
# 在任务映射目录运行，路径均替换为该站点的已核实输入。
./bin/hcu-cluster-run shared-conda platform,resource \
  -f /task/hostfile --env-script /task/env.sh --expected-devices 8
./bin/hcu-cluster-run per-node-container container-status \
  -f /task/hostfile --container TRAIN_CONTAINER -i IMAGE
```

第一条执行真实远端探针，第二条只核验指定容器状态/镜像，不证明设备空闲。主动 `rccl`、`gemm`、`ib-write-bw`、`custom` 另行按资源准入执行；`--dry-run` 只看计划，不是环境验收。

## 主动测试的调用与数据契约

控制端解析场景/操作与 hostfile → 按节点数分组 → 检查目标容器、环境和空闲 → 在实际节点加载 `env.sh` → launcher 启动 payload → 解析各组结果与原始证据。控制端环境脚本与目标环境脚本是不同执行层，不能只在登录机 source DTK。

`--group-size` 是每组节点数，`--slots` 是并发测试组数，不是 MPI rank。RCCL 默认 `rccl-tests` profile 使用已有 `*_perf`，多节点由脚本 MPI 启动；显式 `--profile worker` 才是 Python smoke 路径。`--nproc-per-node` 在不同 profile 中含义/默认值不同，按 CLI 确认。`ssh-torchrun` 需要足够并发启动组内所有成员，不能排队启动导致 collective 等待。

基础结果使用 `cluster-result.json` schema 2.0，类别为 `node_status`、`hardware_devices`、`system`、`driver_dtk`、`software_components`、`network_rdma`、`resource_state`、`network_health`、`execution_evidence`；折叠同值的 `members` 仍需展开检查实际覆盖。platform/resource 及部分 active_execution 路径即使结果 BLOCKED/INCOMPLETE 也可退出 0，须读状态、findings 与缺项。主动预检失败可能根本不创建 active-result，因此“没发现错误结果文件”不能当通过。性能需要匹配消息量、dtype、拓扑和参考值；源码中默认阈值不自动成为任何站点标准。RCCL 汇总的 in-place/out-of-place algbw/busbw 各取自己的峰值，应回逐 size 原始表比较，不能当作同一消息量的四项结果。

## 训练控制与故障恢复调用链

`main.py` / start.sh → `DistributedJobManager` → NodePool/BlacklistManager、LogMonitor/NHC、`JobStateMachine` → MPI/Docker launcher。日志和 NHC 通过 EventBus 产生事件；状态机先处理事件，再决定 START/STOP/NONE。主要状态为 INIT→STARTING→PENDING→RUNNING，故障进入 RECOVERING；PENDING 等待有效训练日志，不等于训练健康。

节点池维持 running/backup/abnormal 不重叠。恢复包括停止旧作业、确认故障节点、从池中补足、重启并重新观察。控制器不保存模型 checkpoint；训练端必须提供可恢复的模型/优化器/RNG/数据状态。控制器状态、节点池、快照和黑名单是共同持久化边界，同一 WORK_DIR 只允许一个控制器。

## 安装、运行、测试与诊断路线

裸机/Slurm 读 `cluster_manager/README.md`、setup.py、start.sh 和 deployment/recovery 文档；已有 Docker 路径另核对镜像、容器、脚本与 launcher 行为。`base` 日志解析器面向 Megatron，`special` 是已适配其他格式，不证明所有 RL 角色日志已覆盖。先离线输入真实日志确认 step/异常事件，再进行有界恢复验收。

K8s add-on 依赖既有 Volcano/Training Operator/设备插件及相应 RBAC；其安装脚本不替代这些平台。NodeHealth 进入宿主执行 NHC，训练镜像有 Python 不代表节点有 `run_nhc`。训练日志路径、checkpoint 和 Pod 重建后挂载都要单独验证。

故障先分成入口/权限与依赖、探针无输出、active test 性能异常、训练日志不匹配、节点不足、重启后没有有效 step。按对应 execution evidence、组日志、状态机、node pool 和训练 checkpoint 查证，不把“控制器还活着”当恢复完成。

## 影响范围、精度和回退

当前裸机/Slurm README 明确警告停止路径可能广泛终止 Python 进程，要求独占节点；Docker 停止语义另查对应 launcher。部署前必须审查实际分支和停止命令范围，不能在共享节点照搬。Agent 不在本轮执行这些命令。

TrainFlow 复用其唯一恢复负责人，独立 watcher 检查停滞、恢复超时、吞吐/显存和 loss。恢复后同时验证 optimizer/data step 与数值连续性；多套控制器不得争抢重启。回退先停止本任务控制者并确认原进程终态，保留状态文件与证据，不清空共享节点。

## 来源、PR 与更新

- [README.md](https://github.com/HYGON-AI/cluster-manager-das/blob/438847c1877cdce17cb524cb8825d49bd6917d6a/README.md)
- [hcu-envcheck/README.md](https://github.com/HYGON-AI/cluster-manager-das/blob/438847c1877cdce17cb524cb8825d49bd6917d6a/hcu-envcheck/README.md)
- [hcu-envcheck/cluster_run/README.md](https://github.com/HYGON-AI/cluster-manager-das/blob/438847c1877cdce17cb524cb8825d49bd6917d6a/hcu-envcheck/cluster_run/README.md)
- [hcu-envcheck/cluster_run/cli.py](https://github.com/HYGON-AI/cluster-manager-das/blob/438847c1877cdce17cb524cb8825d49bd6917d6a/hcu-envcheck/cluster_run/cli.py)
- [hcu-envcheck/pyproject.toml](https://github.com/HYGON-AI/cluster-manager-das/blob/438847c1877cdce17cb524cb8825d49bd6917d6a/hcu-envcheck/pyproject.toml)
- [cluster_manager/README.md](https://github.com/HYGON-AI/cluster-manager-das/blob/438847c1877cdce17cb524cb8825d49bd6917d6a/cluster_manager/README.md)
- [cluster_manager/docs/architecture.md](https://github.com/HYGON-AI/cluster-manager-das/blob/438847c1877cdce17cb524cb8825d49bd6917d6a/cluster_manager/docs/architecture.md)
- [hygon-ft-k8s/README.md](https://github.com/HYGON-AI/cluster-manager-das/blob/438847c1877cdce17cb524cb8825d49bd6917d6a/hygon-ft-k8s/README.md)
- [stack-analyzer/README.md](https://github.com/HYGON-AI/cluster-manager-das/blob/438847c1877cdce17cb524cb8825d49bd6917d6a/stack-analyzer/README.md)

按该仓完整目录与文档增量检查新增入口；通过 `wiki-search-pr` 搜索改动原因，再追当前实现和测试。正文是选定源码/官方文档解读，未在新现场运行。新 commit、接口、返回 schema 或依赖变化时，同时复核本页和相关工作流。
