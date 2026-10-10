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

1. [通信专题：原命令、环境变量、差距排查、三轮数据及原件](communication.md)。16 rank 的 1/2/4 GiB out-of-place busbw 中位41.68/42.57/42.06 GB/s；全部13点报告错误数0。in-place 校验未启用，不能算正确性通过。
2. `run_nhc` 在已检查宿主/镜像中未找到，用户允许暂时跳过；这是依赖缺口，不是环境通过项。后续真实容错需要单独补齐并验证。
3. 历史44.83 GB/s来自不同DTK/驱动及不完整条件，剩余差距保留。当前用户允许继续模型适配优化，不等于把这项比较变成达标。
4. 资源准入检查进程、设备FD、显存和利用率。即使0%利用率，仍可能有人保留显存；不能抢卡。外部网络和调度资源独占尚未证明。
5. 任务专属MPI临时SSH服务已回收；原始命令中的服务、端口和路径是历史证据。新任务使用自己的合法 launcher 与凭据，不依赖旧任务服务继续存在。

## 跨任务复用

先搜本页与通信专题，再读 [通用通信方法](../../../docs/practices/communication-recipe.md)。硬件/镜像/通信库/网卡策略/拓扑/规模/消息类型或脚本改变时重新判断适用性；不盲目套用结果阈值，不自动执行原件中的命令。

当前这套开发环境的测量参考安排在2026-10-17复核；此前发生配置变动应提前复核。以后新增模型调优、显存、loss和容错结论，关联到本页及 `knowledge/experiments/` 的对应案例，保留各自模型/版本边界。

[证据清单](manifest.json)保存仓内路径、SHA256、来源和处理方式。网络 JSON 是便于阅读的精简计数器，同目录 `.raw.json.gz` 保存逐字节完整原件；各轮 ZIP 保存全部16 rank 日志和回执，可独立核验。无需访问最初模型 workspace。
