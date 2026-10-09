# 训练工作流与验收

通过 `$hcu-trainflow` 统一启动；下列三个阶段保持独立入口和原有领域边界。完整任务采用 [实施、独立复核、修正的协作循环](collaboration.md)，阶段产物与候选快照绑定。只检查环境、只分析性能或只诊断故障仍可单独使用。

## 环境与模型适配

依次做权限/资源确认、工具发现、全节点设备验收、源仓/分支锁定、HCU 启动配方适配跑通和正确性基线。健康预期对应 shape/dtype/拓扑/软件版本及测量单位；未采集项目保留 incomplete。脚本随工程变化时先看最新命令/源码，再登记 CommandCard，不能靠历史用法猜测。

启动方案优先参考所选 HCU 工程适用分支已有的同模型脚本、环境变量和配置，并结合现场 Docker/Conda/Slurm/K8s 方式及用户 patch 调整。没有同模型脚本时参考同引擎相近模型的 HCU 配方；缺少适用配方时，才结合官方模型定义与当前 HCU 实现构建启动方案。NV 官方资料用于核对模型与训练语义，平台环境和启动命令须在实际 HCU 分支验证。沿包装脚本追踪最终入口及生效参数，保存脚本来源、版本、调整理由和与官方语义的差异；旧 HCU 脚本也需要兼容性检查。详见 [启动配方核对](../skills/hcu-train-adapt/references/workflow.md#启动配方选择与核对)。

预训练与 SFT 使用相同的基本环境/数值流程，但 SFT 必须额外确认模板、packing 和 loss mask。RL 另外建立 actor/critic/ref/reward/rollout/weight sync 的资源与版本图，保留样本 policy version 和异步语义。

## 性能优化

优化阶段按实际调用选择大型引擎或 [Torch 原生训练专项](../skills/hcu-train-optimize/references/torch-native-training.md)，可以混用，不新增阶段。视频生成/VLA/世界模型侧重输入与时空 shape、autograd、compile/断图/重编译、DDP/FSDP 及编译后的实际后端；共同保留初始数值基线、≥90% 非通信热点建模和阶段 loss。AOTI 不默认用于训练。

[通信优化专项](../skills/hcu-train-optimize/references/communication-optimization.md) 覆盖真实 process groups、消息与依赖、DP bucket/FSDP 预取、TP/EP/PP/CP 调度、chunk-ready、AG-GEMM/GEMM-RS 和设备侧通算融合。对照纯通信、纯计算、模型内并发与整步表现，量化暴露时间、计算退化和额外显存，不以时间线相交宣称加速。

先评估并行切分与显存预算，建立可行候选布局，再端到端采样并迭代系统调参/overlap/内存和融合粒度，然后形状级上限与实现优化。并行度、微批/梯度累积、重算与状态分片共同影响显存、通信、PP 空泡和算子 shape；按最吃紧 rank 的峰值及必要余量筛选，再用 profiler-off 吞吐实测选择，不能只追求“能装下”或“占满显存”。具体对照项和已有官方教程见 [并行切分与显存调参](../knowledge/official-megatron-wiki/parallelism.md#调参推理)。

不要要求先完成全部融合才能分析剩余热点。Flash-Train 先复用现有能力，算子实现交由已有 Hygon HIP/Triton 技能。子 Agent 可并行读取独立证据，但同资源实验串行，修改范围不重叠。

比较实验保存 warmup、profiler-off 重复次数、配对次序、设备状态及方差。每轮局部正确性与实际 candidate 分发必须通过；阶段候选冻结后验 loss。初始基线和回退方案保持不变，不能一路与上一次误差更大的候选比较。

## 扩容、容错和诊断

资源不足时可仅缩 layer 做适配或筛机；扩规模前恢复完整模型，在能够容纳它的模型并行布局上先跑通并复核，再逐级扩 DP 域并接入单一恢复负责人。每一级重新验收节点池、吞吐效率、通信、显存与保存恢复。扩 DP 时明确固定有效全局 batch 还是获准改变训练配方，并据此调整累积/学习率等，不能把弱扩展与强扩展结果混比。节点池随故障和重新验收变化。监测 loss、吞吐、显存、checkpoint、step/token 进展及恢复超时；独立监测 watcher 的心跳。容错动作权限在部署具体任务时确定。

故障按第一异常分层：环境/网络、调度/进程组、数据、Python/C++、设备 kernel、保存恢复。先采现场再重现和选择工具，错误或性能停滞时适时给人类专家最小证据包。

## 交付

改动归属训练引擎、TE、Flash-Train、编译/运行时或容错工程相应责任边界。PR 描述问题与最终行为、适用条件、验证和回退，遵循该仓规范。Cookbook 输出可公开的最佳实践；现场数据、内部链接和性能敏感资料不进入本 public 仓。
