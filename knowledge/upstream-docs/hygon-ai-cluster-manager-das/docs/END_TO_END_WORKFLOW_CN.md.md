---
id: doc-hygon-ai-cluster-manager-das-f498a46e0cdf6f10c6d2
title: HYGON-AI/cluster-manager-das / docs/END_TO_END_WORKFLOW_CN.md
engine: tooling
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: HYGON-AI/cluster-manager-das
commit: 438847c1877cdce17cb524cb8825d49bd6917d6a
path: docs/END_TO_END_WORKFLOW_CN.md
raw_sha256: babb3b49f70520374867561c3502eee77ce9dcbccdbbb05163c6c093f173ba32
sources: []
generated_body_sha256: 9b27536fa25858490ada314ce99933451fec1d3a506260bc8408d5ee6b1332d5
source_state: current-scan
---

# HYGON-AI/cluster-manager-das / docs/END_TO_END_WORKFLOW_CN.md

[Original at fixed commit](https://github.com/HYGON-AI/cluster-manager-das/blob/438847c1877cdce17cb524cb8825d49bd6917d6a/docs/END_TO_END_WORKFLOW_CN.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--
Copyright (c) 2026 Hygon Information Technology Co., Ltd.
SPDX-License-Identifier: Apache-2.0
-->

# HCU 训练可靠性工具集端到端使用流程

本文保存仓库级的执行顺序和场景衔接。具体命令、恢复边界和故障排查以各子项目 docs 为准。

## 推荐使用流程

```text
训练前环境验收
    hcu-envcheck
         ↓
选择训练平台
    ├── Slurm/MPI：cluster_manager
    └── Kubernetes：hygon-ft-k8s
         ↓
训练 hang 时采集和分析堆栈
    stack-analyzer
```

`hcu_resiliency_ext` 是第三方容错库适配层，不是上述主流程的必选组件。

### 第一步：执行训练前检查

裸金属或 Slurm 节点推荐使用项目提供的示例脚本：

```bash
cd hcu-envcheck

./bin/hcu-envcheck-doctor
vi examples/baremetal-nodes.txt
./examples/check-nodes.sh
```

结果默认保存在独立运行目录：

```text
hcu-envcheck/out/nodes_check_YYYYMMDD_HHMMSS_ffffff/
```

`hcu-envcheck` 支持五类入口：

- `baremetal-cluster`：裸金属或 Slurm 多节点检查。
- `k8s-pod`：检查一个已经运行的 Pod。
- `k8s-cluster`：使用指定训练镜像检查一批 Kubernetes 节点。
- `active-rdma-slurm`：执行主动 RDMA/RCCL 验收。
- `ib-fabric-slurm`：检查 Native IB 一跳链路和交换机端口计数器。

日常启动前检查优先使用前三类。主动 RDMA、RCCL 和 IB Fabric 验收只能在已经确认空闲并满足独占条件的 Slurm allocation 中执行。

完整说明：

- [快速使用说明](../hcu-envcheck/README.md)
- [完整使用手册](../hcu-envcheck/docs/USER_GUIDE.md)

### 第二步：选择运行期容错方案

#### Slurm/MPI

```bash
cd cluster_manager
python -m pip install -e .
hcu-cluster-inspect --help
```

`cluster_manager` 在登录节点或控制节点运行，主要负责：

- 校验已有 Slurm 作业和训练规模。
- 从 hostfile 初始化运行、备用、正常和异常节点池。
- 监控训练日志、NHC 和 Slurm 状态。
- 发现故障后停止当前训练、隔离异常节点、选择备用节点并重新启动。
- 持久化节点池、运行状态、迭代信息和故障快照。

正式启动需要准备已有 Slurm Job ID、hostfile、sbatch 脚本、训练启动脚本和训练参数文件。不要直接把仓库根目录的 `start.sh` 当作通用启动器，具体限制见 [cluster_manager README](../cluster_manager/README.md)。

#### Kubernetes

```bash
cd hygon-ft-k8s

bash start.sh install
bash start.sh status
```

`hygon-ft-k8s` 通过以下组件增强 PyTorchJob 和 Volcano Job：

- Admission Webhook 注入 `ft-launcher` 和容错环境。
- Operator 消费 `FaultEvent`，执行故障聚合、节点 taint、Pod 删除和状态回写。
- `nodehealth-agent` DaemonSet 周期执行节点健康检查。
- `ft-launcher` 包装训练命令、运行日志监控并上报故障。

恢复工具拥有的 unhealthy taint：

```bash
cd hygon-ft-k8s
bash start.sh recover node95 node39,node97
```

恢复会执行多轮 IB 状态、IB 带宽、NHC 和检查 Pod 验证。目标节点和参考节点必须空闲；默认只删除 `ft.hygon.io/node-unhealthy:NoSchedule`，不会删除其他 taint。

详细部署、权限、标签、镜像和 Volcano 配置见 [hygon-ft-k8s README](../hygon-ft-k8s/README.md)。

### 第三步：训练 hang 后执行堆栈诊断

安装：

```bash
cd stack-analyzer
python -m pip install .
```

不连接真实集群即可先运行内置演示：

```bash
stack-analyzer demo --scenario pp --method trie
stack-analyzer demo --scenario eval --method auto
```

真实诊断分为两步：

1. 通过 Kubernetes、Docker SSH、Ansible 或本地采集方式执行 `py-spy dump`，生成 `stacks.json`。
2. 使用 hostfile 和 PP/TP/DP 拓扑分析异常 rank，输出 `outlier_ranks` 和 `machines_to_evict`。

`machines_to_evict` 是结合并行拓扑给出的隔离建议，不代表其中每台机器都是根因，也不会自动执行驱逐。具体采集权限、拓扑参数和结果解释见 [stack-analyzer README](../stack-analyzer/README.md)。
