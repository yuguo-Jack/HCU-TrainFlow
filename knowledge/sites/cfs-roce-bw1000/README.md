---
id: sites/cfs-roce-bw1000/index
title: CFS BW1000_H gfx936 SSH Docker RoCE 站点总览
engine: cross-engine
kind: site-knowledge
stages: [adapt, optimize, fault-tolerance]
visibility: public
review_level: source-and-measurement-review
runtime_validated: false
observed_at: '2026-10-10T01:22:41.549842+00:00'
---

# CFS / BW1000_H / RoCE 站点

本页把任务中的站点发现变成随工程共享的知识。`runtime_validated: false` 表示整站/生产训练尚未验收；下方通信专题有明确限定的实际执行证据。

## 环境与使用入口

- 计算节点本次使用 `10.32.4.110`、`10.32.4.76`，每节点8张 BW1000_H，gfx936、80 CU、每卡可见65520 MiB。SSH+Docker，容器 host 网络，`/cfs` 为共享存储；任务写入 `/cfs/yuguo/<任务名>`。
- 测试镜像 `10.16.1.152:5000/jenkins/model_test_env/megatron:0.19.2-ubuntu22.04-dtk2610-py3.12-1009`；实际不可变 ID、DTK26.10、HIP7.2.26365、Torch版本和动态库见 [环境摘要](environment.json)。镜像 tag 可能被更新，复用前核对 ID。
- 每节点4组 RoCE bond，每组两条200 Gbit/s物理链路，MTU9100；管理网 `eth0`，GID3。固定端口、TC160和QP4是本站点实测配方的组成，不是通用推荐值。
- 加载顺序为 DTK 激活，再站点环境脚本。必须核对各 rank 实际环境与加载库；镜像有库不等于训练进程在用它。

## 配方、基准与已知缺口

1. [硬件参数与 Roofline 参考](hardware-baseline.md)：有效CU、wave、LDS、显存、频率/功耗与既有GEMM/copy实测。新增64/76观测中管理工具报BW3000，与旧runtime的BW1000_H标签不同；精确SKU映射尚未确认，不能据旧标签直接选外部标称峰值。[通信专题：原命令、环境变量、差距排查、三轮数据及原件](communication.md)：16 rank 的 1/2/4 GiB out-of-place busbw 中位41.68/42.57/42.06 GB/s；全部13点报告错误数0。in-place 校验未启用，不能算正确性通过。
2. `run_nhc` 在已检查宿主/镜像中未找到；这是依赖缺口，不是环境通过项。需要 NHC 的环境验收或容错部署应先补齐并验证。
3. 历史44.83 GB/s来自不同DTK/驱动及不完整条件，不能作为严格同条件达标依据。
4. 资源准入检查进程、设备FD、显存和利用率。即使0%利用率，仍可能有人保留显存；不能抢卡。外部网络和调度资源独占尚未证明。
5. 原始执行记录中的任务服务、端口和路径不属于站点固定入口。新任务需确认自己的 launcher、hostfile 与连接条件。

## 跨任务复用

先搜本页与通信专题，再读 [通用通信方法](../../../docs/practices/communication-recipe.md)。硬件/镜像/通信库/网卡策略/拓扑/规模/消息类型或脚本改变时重新判断适用性；不盲目套用结果阈值，不自动执行原件中的命令。

测量日期保留在各专题；复用前核对环境是否变化，涉及当前性能验收时重新测量。符合收录标准的模型最终优化总结关联到 `knowledge/experiments/`，中间调参与诊断过程保存在任务档案。

[证据清单](manifest.json)保存仓内路径、SHA256、来源和处理方式。网络 JSON 是便于阅读的精简计数器，同目录 `.raw.json.gz` 保存逐字节完整原件；各轮 ZIP 保存全部16 rank 日志和回执，可独立核验。无需访问最初模型 workspace。
