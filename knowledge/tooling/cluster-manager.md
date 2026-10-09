---
id: tooling/cluster-manager
title: HCU Cluster Manager：环境检查与单一恢复负责人
engine: tooling
stages:
- adapt
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-09'
sources:
- source: hygon-ai-cluster-manager-das
  path: README.md
  commit: 026452b298814065b317273c28cc6d707567c20c
  sha256: efe4694924f4b21630b6e54f2dc49769db3d7c7db89314cbc8f01ba221d2a22f
- source: hygon-ai-cluster-manager-das
  path: hcu-envcheck/hcu_envcheck/cli.py
  commit: 026452b298814065b317273c28cc6d707567c20c
  sha256: f5a7ae99bffa88c4aa14691438ecf38ad97e1d6fddce4d86da5cc4564aaa9560
- source: hygon-ai-cluster-manager-das
  path: cluster_manager/docs/architecture.md
  commit: 026452b298814065b317273c28cc6d707567c20c
  sha256: c6d87768a1155701bfe83c7cd57927a7c38fd72be0835e74ae79a31944245f5f
---

# HCU Cluster Manager：环境检查与单一恢复负责人

## 按子工程选择

本提交公开仓由 hcu-envcheck、Slurm/MPI cluster_manager、hygon-ft-k8s、stack-analyzer 及第三方容错适配组成。它们不是一个统一安装的命令。环境检查、节点替换/重启、K8s operator 和堆栈采集应按部署类型分别阅读。

## 已核对的入口

hcu-envcheck 的 CLI 有 baremetal-cluster、k8s-pod、k8s-cluster、active-rdma-slurm、ib-fabric-slurm 等子命令。NHC 开关及 command/config/selected/removed 有独立参数，源码默认 NHC executable 名称为 `run_nhc`。这说明 workflow 应发现当前工具版本再生成命令，不能永久写死某份 check 脚本。

## 环境验收

被动采集与主动带宽/通信压测分开。主动测试在分配给该任务的可用节点上运行，明确设备覆盖、消息大小、dtype、拓扑和预期来源。公开 README 说明部分恢复路径对节点进程和集群资源有较大影响，因此部署时必须设置资源归属与恢复负责人。

## TrainFlow 的位置

外部工具继续负责隔离、选节点与重启，TrainFlow watcher 负责独立观测进展、发现未恢复和将证据递交本地 Agent。本机离线时 remote watcher 仍运行；告警渠道及 Agent launcher 由部署任务配置。没有部署验证前不宣称已经实现飞书送达或 Codex 唤醒。

## 固定源码与更新范围

- [README.md](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/README.md)
- [hcu-envcheck/hcu_envcheck/cli.py](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/hcu-envcheck/hcu_envcheck/cli.py)
- [cluster_manager/docs/architecture.md](https://github.com/HYGON-AI/cluster-manager-das/blob/026452b298814065b317273c28cc6d707567c20c/cluster_manager/docs/architecture.md)

上述链接固定到本轮阅读的提交。上游变化时，需要同时检查总览、调用链、专题、案例和相关 Skill。本文区分源码行为与迁移建议；没有声称在 HCU 上完成性能或精度验证。
