---
id: doc-hygon-ai-cluster-manager-das-d82ab49f91a6ba1662d9
title: HYGON-AI/cluster-manager-das / README.md
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
path: README.md
raw_sha256: efe4694924f4b21630b6e54f2dc49769db3d7c7db89314cbc8f01ba221d2a22f
sources: []
generated_body_sha256: 311dbc3b797be00ed65541204a556ad1165dadc76e2decba92f3215815b42308
source_state: current-scan
---

# HYGON-AI/cluster-manager-das / README.md

[Original at fixed commit](https://github.com/HYGON-AI/cluster-manager-das/blob/438847c1877cdce17cb524cb8825d49bd6917d6a/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

<!--
Copyright (c) 2026 Hygon Information Technology Co., Ltd.
SPDX-License-Identifier: Apache-2.0
-->

# cluster-manager-das：HCU 训练可靠性工具集

`cluster-manager-das` 面向大规模 HCU 分布式训练，覆盖训练前环境检查、Slurm/MPI 与 Kubernetes 运行期容错、训练 hang 诊断以及第三方容错库适配。

本仓库不是统一安装的单体软件。每个子项目都有独立的依赖、入口和部署方式；请先按场景选择子项目，再阅读对应 README 和 docs。

## 场景选择

| 目标 | 子项目 | 典型环境 | 主要影响 |
|---|---|---|---|
| 训练前检查 HCU、驱动、DTK、CPU、内存、NIC、RDMA、IB 和软件环境 | [`hcu-envcheck`](hcu-envcheck/README.md) | 裸金属、Slurm、Kubernetes | 普通检查以采集为主；主动模式会产生测试流量 |
| 监控训练，故障后隔离节点、选择备用节点并重启 | [`cluster_manager`](cluster_manager/README.md) | Slurm + MPI | 会停止并重新拉起训练进程 |
| 为 PyTorchJob 或 Volcano Job 增加运行期容错 | [`hygon-ft-k8s`](hygon-ft-k8s/README.md) | Kubernetes | 会创建集群资源，可能 taint 节点和删除 Pod |
| 训练 hang 后采集所有 rank 的 Python 堆栈并给出隔离建议 | [`stack-analyzer`](stack-analyzer/README.md) | Kubernetes、Docker、Ansible、单机 | 默认只采集和分析，不自动驱逐节点 |
| 将 `nvidia-resiliency-ext` profiling 模块重定向到 HCU 适配实现 | [`hcu_resiliency_ext`](hcu_resiliency_ext/Readme.md) | 第三方容错库适配 | 会修改 Python 模块导入行为 |

跨子项目的推荐执行顺序、场景衔接和恢复边界见：

- [端到端使用流程](docs/END_TO_END_WORKFLOW_CN.md)

## 子项目概览

### hcu-envcheck

训练启动前的一次性环境检查和主动通信验收工具。支持裸金属、Slurm、已有 Pod、临时探针 Pod、主动 RDMA/RCCL 和 IB Fabric 验收。

- [README](hcu-envcheck/README.md)
- [完整使用手册](hcu-envcheck/docs/USER_GUIDE.md)

### cluster_manager

Slurm/MPI 单任务控制面，负责节点池、日志/NHC/Slurm 监控、状态持久化以及故障后的停止、换节点和重启。

- [README](cluster_manager/README.md)
- [部署与启动](cluster_manager/docs/deployment_guide.md)
- [故障恢复与日常操作](cluster_manager/docs/recovery_workflow.md)
- [配置参考](cluster_manager/docs/config_guide.md)

### hygon-ft-k8s

通过 CRD、Webhook、Operator、DaemonSet 和 `ft-launcher` 增强 PyTorchJob 与 Volcano Job 的运行期容错。

- [README](hygon-ft-k8s/README.md)
- [安装指南](hygon-ft-k8s/docs/INSTALLATION_CN.md)
- [运行与恢复](hygon-ft-k8s/docs/OPERATIONS_AND_RECOVERY_CN.md)

### stack-analyzer

使用 `py-spy` 采集分布式训练堆栈，通过 Trie/signature 聚合和 PP/TP/DP 拓扑识别异常 rank 与建议隔离机器。

- [README](stack-analyzer/README.md)
- [采集与分析操作手册](stack-analyzer/docs/COLLECTION_AND_ANALYSIS_CN.md)
- [分析处理链路](stack-analyzer/docs/ANALYSIS_PIPELINE_CN.md)

### hcu_resiliency_ext

`nvidia-resiliency-ext` 的 HCU 兼容适配补丁。该目录不是独立控制器，需要在目标第三方源码版本中完成安装和兼容验证。

- [README](hcu_resiliency_ext/Readme.md)
- [安装说明](hcu_resiliency_ext/docs/INSTALLATION_CN.md)

## 目录结构

```text
hcu_cluster_manager/
├── docs/                       # 套件级流程
├── hcu-envcheck/               # 训练前环境检查
├── cluster_manager/            # Slurm/MPI 训练容错
├── hygon-ft-k8s/               # Kubernetes 训练容错
├── stack-analyzer/             # hang 堆栈诊断
└── hcu_resiliency_ext/         # 第三方容错库适配
```

## 根目录文件边界

`cluster_manager/start.sh` 是 Slurm/MPI 场景的环境模板，使用前必须按目标集群修改训练规模、Conda、共享路径和 Slurm 参数。Kubernetes 用户应进入 `hygon-ft-k8s`，使用该目录下的 `start.sh`。

`hygon-ft-k8s/docs/train_volcano.yaml` 是启用 `ft.hygon.io` 的 Volcano Job 示例，包含示例 Namespace、镜像、训练路径、数据路径、节点规模和存储挂载。复制到其他集群前必须逐项核对。

## 安全边界

- 主动带宽、RCCL、完整筛机、故障模拟和恢复测试只能在已确认空闲的节点上执行。
- `cluster_manager` 当前可能按 `python` 关键字终止目标节点进程，要求训练节点独占。
- `hygon-ft-k8s` 可能创建集群级资源、taint 节点、删除 Pod 并触发任务重建。
- `stack-analyzer` 需要 ptrace 权限；分析结果是诊断证据，不会自动执行驱逐。
- `hcu_resiliency_ext` 只能在已验证的第三方库版本上使用。

## 开发与测试

仓库提供统一的 Pytest 配置。在仓库根目录执行全部单元测试：

```bash
python -m pytest
```

也可以把 `pytest.ini` 中列出的子项目测试目录传给 Pytest，仅验证单个模块。

`cluster_manager` 的完整验证依赖 Slurm、MPI、HCU 和真实训练环境，不能把单元测试通过等同于生产链路验证。

README 只维护项目定位、能力、最短入口和文档导航；运行顺序、处理链路和恢复流程统一维护在对应 `docs/` 中。

## License

Copyright (c) 2026 Hygon Information Technology Co., Ltd.

This project is licensed under the Apache License, Version 2.0. See
[LICENSE](LICENSE) for the license terms. Third-party components and
attributions are documented in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
