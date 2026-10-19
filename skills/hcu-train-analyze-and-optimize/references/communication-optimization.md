# 训练通信：暴露时间、overlap 与通算融合

本指引属于现有 optimize 阶段，适用于训练引擎及 Torch DDP/FSDP。先保证通信正确性与环境带宽验收；按问题检索 HCU-Knowledge 的 RCCL、Galaxy、rocSHMEM、DeepEP、UCCL、UltraEP、MoonEP、MORI、Flux 和引擎案例，再看当前部署分支源码。名称相同不代表接口、异步语义或架构支持相同。

候选后端的作用、HCU 分支与可修改/重编的验证顺序见[工程联动](hcu-library-integration.md)。UCCL 的collective/P2P/EP、UltraEP的副本/梯度生命周期、MoonEP的节点内事务接口分别评估，不能当作同一层可互换的开关。

## 1. 建立边界和基线

先核对消费者锁定的通信依赖和实际 backend/topology。节点内 IPC、特殊互联、普通 RDMA 的能力标志和测试配方不可互换；不能仅凭 `internode` 字段判断物理节点范围，也不把某专项关闭网络的配方用于常规跨机。provider 的编译期 ABI、GPU/HCA 映射和注册内存所属 PD/QP 要与加载制品一致，环境变量不能修复 ABI 不匹配。更换 EP 后端另验同步/异步、Graph、多次并发调用及梯度归并；存在 dispatch/combine API 不等于这些能力均已实现。

按实际 process group 记录 rank→设备/节点/NIC、TP/PP/DP/CP/EP（含组合组）、消息字节、dtype、collective/P2P、调用序列、stream/event、producer→consumer 和 buffer 生命周期。每个非单例组至少两个代表 rank；定位最慢 rank、全组一致性或运行 TraceLens collective 报告时补全所需 ranks。校时后再比较跨 rank 先后。

对相同消息量、成员、dtype、拓扑分别测：纯通信、对应 GEMM/attention 等纯计算、当前训练并发窗口。记录启动/排队、真正传输、等待、整步尾部暴露时间及 overlap 时计算退化。RCCL kernel 持续时间可能含等待/协议轮询，不能全算成链路传输；时间线相交也不能证明通信被有效隐藏。

无依赖且资源独立的理想 overlap 窗口下界可参考 `max(Tcompute, Tcomm)`，真实数据依赖、启动和资源竞争会抬高下界。此式只用于边界清楚的窗口，不作为整个训练步的理论上限。报告整步时间/吞吐、暴露通信、纯计算与并发计算差异、显存峰值和尾延迟；不要把多个 stream 的时间求和当作端到端时间。

### 1.1 数值协议与后端策略必须一起核对

低精度载荷不能只按 dtype 名和通信字节验收。先确定数据含义、参与 rank 的 scale、求和顺序与最终舍入，再选 oracle 和回退；普通 CAR、通信量化 QR、EP dispatch/combine 分别保留契约。

| 接入点 | 需要查证和验证的差异 |
| --- | --- |
| AITER INT8/FP8 AG 与 RS | 当前 AG 保留原始位，RS 则进行数值 SUM：INT8 为 INT32 累加后保留低 8 位；E4M3FN/E5M2 为按源 rank 顺序 FP32 累加后一次非饱和 RNE 转回，不隐含外部 scale。FNUZ 与不满足 custom 准入的 FP8 RS 明确拒绝，原生 RCCL FP8 SUM 不能作为等价兜底。用匹配合同的独立 oracle 覆盖特殊值、溢出、dim、对齐、变化输入及真实 rank 组。 |
| 原地输出与回退 | 先看准入和真实输出所有权。当前 AITER 的低层 RS 成功写 out 仍返回 None，不支持时也可能返回 None；不能按返回值再调用一次 collective。框架封装返回新 tensor 与底层原地接口分别检查，失败须在修改数据前安全回退或明确报错。 |
| rocSHMEM 的 host collective 路由 | 按当前消费者固定版本检查策略。新 develop 分节点内/间和 collective 读取 `ROCSHMEM_RCCL_MIN_SIZE_INTRA` / `_INTER`，旧单一变量不再读取，等于阈值也可进入 RCCL；alltoallv 的 device counts 使 size 阈值不适用。team capability、symbol 和组内配置一致性仍有门禁；不要把一套默认阈值固化到所有拓扑或旧消费者。 |
| EP async、plan 与工作区视图 | 返回 event 不自动取消 host planning、跨 rank 校验或单 in-flight 限制。MoonEP 当前 async 返回完成 event，消费 stream 需要 join；zero-copy 视图仍受 generation/工作区寿命约束。UltraEP 专家副本梯度归并会消费并清零源缓冲，异常后直接重跑并非幂等；优化器前的 grad join、新权重消费前的 weight join 及迭代 flush 分别验收。 |

能力依据从大库 `aiter-int8-fp8-collective-contract`、`rocshmem-hcu-engineering`、`moonep-g1-contributor-capacity` 和 `ultraep-replica-gradient-lifecycle` 进入。以上说明对应版本的检查点，不能当成任意已安装库都支持的能力表。微基准含 copy-in、host 直接绑定或 Graph event 的口径须明确；某 dtype/拓扑的局部收益不推导成模型整步收益。

## 2. 先调调度与粒度，再判断融合

| 层面 | 重点实验 | 约束 |
| --- | --- | --- |
| DP / DDP | 梯度 ready 顺序、bucket 大小/数量、归约触发、梯度累积与最终同步 | 小 bucket 启动多，大 bucket 易形成尾部；累积期间的 `no_sync` 范围和 loss/梯度归一按当前实现确认，最后一次必须正确同步 |
| FSDP / 状态分片 | 参数 all-gather、梯度 reduce-scatter、prefetch、reshard、重算配合 | 预取可缩等待但延长全参存活，提高显存峰值；所有 rank 参数版本与 optimizer state 一致 |
| TP / SP | AG→GEMM、GEMM→RS、反向对偶路径、现有 Flux/TE buffer 调度 | 先复用 HCU 已支持实现；切片依赖、layout、余数、对齐和反向语义共同验证 |
| PP / CP | microbatch 调度、P2P、序列切片交换、早发晚等、慢 stage | 保持模型/有效 batch/梯度累积语义；缓冲与调度改变要重新测空泡和峰值 |
| EP / MoE | dispatch→expert→combine，跨 microbatch overlap、负载与 token 分布 | 空 expert、极不均负载、变 token 数、恢复和 buffer 复用；降低字节量若涉及量化需另验数值 |
| Torch 编译边界 | 编译图与 bucket/prefetch 触发时机 | 图融合可能延后 collective；joint profile，不只看 kernel 数下降 |
| Runtime / 拓扑 | stream/event、队列映射、NIC 绑定和并发资源 | `GPU_MAX_HW_QUEUES` 核对 HCU runtime 实现后做单变量对照；不套 `CUDA_DEVICE_MAX_CONNECTIONS`，也不假定队列越多越好 |

每次分清无 overlap、启动太晚、过早 wait、粒度过粗、尾部不均，还是 SM/HBM/互联/队列竞争。先调整已有正确路径的调度和 chunk/bucket，再决定是否需新 kernel。记录 chunk 大小、启动数、buffer 峰值和最差 rank；只优化平均 rank 可能使训练更慢。

## 3. 通算融合与设备侧通信

只有证据表明计算与通信边界是主要可改善项时，再考虑分块 AG-GEMM、GEMM-RS、dispatch/compute/combine 等融合。先读当前 HCU Flux、MORI、rocSHMEM、TE 或引擎已有实现和测试；区别跨 kernel 的 overlap、批量 collective、真正的通算融合，不能用“合并 launch”代替正确的依赖协议。

设计中明确：生产者何时完成 chunk、谁发布信号、可见性/fence/等待范围、消费者何时读取、谁回收或重用 buffer、跨步/跨 rank sequence/epoch 如何区分、尾块如何处理。若采用设备侧通信，还须证明实际目标支持的 progress 机制与资源预留，避免所有计算资源占满而通信无法前进。精确协议依据库和硬件文档，不从 NV 或 AMD 的同名原语推导 HCU 等价。

按 fwd/bwd/dgrad/wgrad 区分路径，验证累加精度、归约顺序、缩放/量化、layout、alias、in-place、padding、空块及非整除 shape；异步 handle 返回不等于设备数据可用。梯度归约必须在 optimizer 使用前完成，参数同步必须在下一次消费前完成，checkpoint 不得保存仍在异步修改的状态。

先最小单元/多 rank 正确性，再并发压力、多步累积、不同消息/拓扑和保存恢复；超时与故障注入只在部署约定已授权的隔离测试中有界执行。慢 rank、少量 token、空 expert 等测试缺失不能宣称通用。阶段稳定后再验 loss，不能用局部误差容差替代长窗口训练验收。

## 4. 与 Agent 和训练闭环联动

通信分析和各计算算子的实现可并行，但共同 owner 管理相交的接口、buffer 生命周期和同步协议；改变协议前给消费者发消息，集成前核对版本。共享 GPU/网络的性能实验串行或确保真实隔离。融合后的 kernel 必须重新建计算/流量模型，并计入非通信热点覆盖，不能整个划到“通信”而跳过 ≥90% 集合的效率评估。

每个候选保存：旧/新依赖图、process groups、消息/shape、单测与整步对照、计算退化、额外显存、数值结果、支持范围、回退、目标源码提交。预期收益排序以可减少的关键路径为依据；若 overlap 图更满但整步更慢，回退或重调。引擎调度改动交引擎，库机制交其 HCU 主仓；底层实现沿用已有 HIP/Triton Skills，外部目标PR按其发布规范；本仓Wiki保留可复用站点配置、关键实测与证据，完整档案留workspace。
