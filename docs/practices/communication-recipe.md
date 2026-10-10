# 通信配方是完整执行条件

容器里只加载 DTK，不一定得到站点实际用于训练的配置。环境脚本可能进一步选择 NIC/GID、QP、RoCE 端口、GDR、算法或拓扑文件；同一测试二进制也可能动态加载不同通信库。缺少其中一层，测到的低带宽不能直接解释成硬件上限或 RCCL 缺陷。

本页给出可复用的方法；实际站点地址、版本、变量值和测量曲线见同仓 [BW1000_H / DTK26.10 两节点案例](../../knowledge/sites/cfs-roce-bw1000/communication.md)。通用方法不代表所有环境已经验收；现场实测按站点记录限定范围。

## 1. 还原启动链

保存用户原命令与最终执行命令。依次核对 scheduler/allocation、SSH/容器、hostfile 与 rank 映射、MPI/Torch launcher、DTK 激活、站点脚本、模型/测试专属覆盖。每个 rank 都应执行适用激活，不能只在协调节点的 shell 中 source。

```bash
# 模板：替换为已审阅、版本固定的实际脚本；不要直接照抄占位路径。
bash -c 'source /path/to/toolkit-env.sh && source /path/to/site-env.sh && exec /path/to/alltoall_perf -b 1M -e 4G -f 2 -g 1'
```

阅读被 source 的脚本，注意位置参数可能触发安装/改系统源，条件分支可能因文件不存在而不生效。保留脚本哈希和加载顺序；需要复现而原目录不在容器内时，复制原字节到授权任务目录并核对差异。MPI 与 PRRTE 版本、SSH端口/host身份、CPU绑定和slot映射都需实测，不能机械照搬另一个容器的连接方式。

## 2. 哪些变量需要查，为什么

以下是核对清单，不是必须全部设置的默认配方。先读实际 HCU 分支/库日志，尤其不要把 NVIDIA/AMD 同名变量的某版语义直接套用。

| 方面 | 常见入口/变量 | 应核对的实际证据 |
| --- | --- | --- |
| 控制与数据网 | `NCCL_SOCKET_IFNAME`、`GLOO_SOCKET_IFNAME`、`NCCL_IB_HCA`、`NCCL_IB_GID_INDEX` | 管理网和RoCE区分；verbs设备枚举、GID/port、地址、rank到NIC映射 |
| RDMA/GDR | `NCCL_IB_DISABLE`、`NCCL_NET_GDR_LEVEL`、`HSA_FORCE_FINE_GRAIN_PCIE` | 当前库识别的值、实际NET与GDR路径；数值等级可能有版本含义 |
| 多QP与网络分流 | `NCCL_IB_QPS_PER_CONNECTION`、HCU扩展 `NCCL_ROCE_SRC_PORT_LIST` | QP创建和端口修改成功日志、bond物理口计数；变量存在不代表底层调用成功 |
| QoS与重试 | `NCCL_IB_TC`、`NCCL_IB_TIMEOUT` | 当前网络策略是否适用；流量类别本身不能证明交换机QoS/PFC配置正确 |
| 算法与拓扑 | `NCCL_ALGO`、`NCCL_PXN_DISABLE`、`RCCL_MODEL_MATCHING_DISABLE`、`NCCL_TOPO_FILE`、`NCCL_GRAPH_FILE` | 实际加载文件及哈希、路径选择、是否被后续脚本覆盖；强制算法未必对所有消息量有益 |
| 驱动能力 | XDP及实际HCU驱动模块 | 版本匹配的只读查询、通信路径和库支持；未设置env不等于该能力关闭 |

`NCCL_ROCE_SRC_PORT_LIST`、`RCCL_MODEL_MATCHING_DISABLE` 等扩展必须先确认目标构建支持。排查固定源端口时检查函数调用方是否传播错误；若错误返回被忽略，必须进一步核对成功日志/实际流量。聚合口带宽异常需要检查每个物理从口；总bond统计看起来正常也可能掩盖分流不均。

## 3. 实际库和硬件身份

固定镜像 digest、DTK/runtime、通信库和测试二进制哈希、源码提交/补丁。`ldd`/RUNPATH用于预测；真实进程的动态库映射用于确认，二者可能不同。记录PCIe/NIC/NUMA、每卡显存、网口速度、bond模式/hash策略、MTU、链路状态和XDP等前后观测。不要通过容器DTK版本推定宿主驱动，也不要把PCIe速率当成RoCE线速。

GPU空闲要结合新鲜PID/设备FD、利用率、显存和调度预约。共享交换网络无法独占时记录这个限制；不要把别人的低利用率任务判为空闲，也不修改他人的网络、容器或进程。

## 4. 比较完整配方，再拆因果

用户给出有效配方时先忠实复现，明确不可避免的节点/SSH/launcher差异。保留启动、逐rank退出、正确性、日志和作用路径；不直接开展无界参数网格搜索。

| 实验层级 | 能支持的结论 | 不能支持的结论 |
| --- | --- | --- |
| 完整配方与旧方案 | 同测试口径下的组合差异 | 某一个开关贡献了全部收益 |
| 有界单变量 A/B/A | 匹配版本、资源、重复条件下的候选影响 | 对其他NIC/模型/消息量都有效 |
| 单通信与训练内对比 | 同shape/消息在并发压力下的变化 | collective驻留全部是线速传输，或overlap一定有效 |

最终测量区分预热、内部迭代平均、独立启动重复和分位数；INFO/profiler本身有成本。`algbw`、`busbw`、网口Gb/s、有效payload和双向汇总分别定义。消息量扫描的全表平均不等于平台最大带宽；没有实现错误校验的in-place列不能当正确性已过。不能以当前偏低结果替换历史合理预期。

## 5. 形成可跨任务使用的知识

将机制、排查方法和模板整理到本页/同目录；筛选**可跨项目复用的环境配方、已验证条件、关键结果及失效/回退边界**进入 `knowledge/sites/<site-id>/`，仅复制支撑结论的必要原件并登记哈希。一次性节点状态、试错流水和未定方案不入库。完整实验仍在任务档案，跨任务知识不能依赖旧 workspace 在线。

新任务先 `wiki-search "RCCL RoCE alltoall" --project TRAINFLOW_PROJECT --online-pr off`，读匹配站点记录，核对硬件/软件/拓扑/shape/dtype及方法。任务内结构化测量可另用 `reference-query`；该命令不会自动导入仓内站点 JSON。配置改变或过期时补查/测量，不重做已经满足相同条件的所有来源搜索。有效现场配方还应回填训练启动配方；通信单测通过不自动代表模型端到端收益或 loss 通过。
