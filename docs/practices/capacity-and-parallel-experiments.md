# 全参数容量预估与多实例并行优化

先判断**完整模型能否在实际可用资源上训练**，再决定是否缩减。显存估算与短跑能容纳完整参数时，直接开展全参适配和优化；仅在资源不足时优先缩 layer，其他维度缩减仍遵循用户授权。这里的全参表示完整模型配置，不能把“所有代理参数都参与训练”称为原模型全参。

## 1. 容量预估进入适配起点

1. 固定官方模型配置、实际 HCU 执行分支、精度、优化器、序列长和数据/训练语义，核对层数、混合层型、专家总数、词表、视觉/MTP 等组成。MoE 容量按全部常驻专家参数计算，不能用每 token 激活参数数目替代。
2. 确认可使用的健康卡数、单卡显存、机内/机间拓扑及其他用户占用。集群总卡数不是当前可用卡数；所有模拟和后续测量注明这个时间点的资源条件。
3. 优先参考适用 HCU 配方和 HCU Train Simulator 的当前匹配分支，核对模型 adapter、估算公式、命令帮助和已校准 profile。工具不覆盖当前模型时，可以补显式参数/状态估算和短跑校准；**工具缺能力不等于硬件容量不足**。
4. 比较可实现的 TP/PP/CP/EP/ETP、状态分片、重算、微批/梯度累积；先看最吃紧 rank/stage 的峰值。计入参数、梯度、优化器/主权重、保留激活、临时/通信 buffer、allocator/图缓存、保存恢复峰值和必要余量。记录哪些部分尚未建模。
5. 输出候选布局及判断依据：模型结构覆盖、所需卡数、每 stage 估算和余量、实际可用卡数、推测瓶颈、短跑计划。模拟可行的完整配置先短跑校准；实测显存或实际分支不支持时修正布局/模型假设，然后才判断是否确需缩模。不为省事直接从缩层开始。
6. 留存全配置、模拟输入/输出与版本、采用/拒绝理由和短跑实测。看板 configuration 列出“全参 / 缩层 / 授权缩维”，区分 predicted 与 measured；中间输入、结果、误差和候选保存在任务档案；只有可跨项目复用的环境经验或最终模型优化总结按知识架构筛选入 Wiki。

不要求每个任务先运行一个完整网格搜索，也不把模拟器作为不可替代的硬依赖。已有同版本、同结构的可靠实测可复用，并复核本次差异。

优化器容量按实际参数组、精度和分片方式估算；矩阵算法可能需要完整矩阵聚合、正交化中间量和流水通信 buffer，不能套用另一优化器的每参数字节数或默认沿 DP 均分。先核对当前实现是否支持所选状态分片，再计入最重 rank 的峰值。算法/分组变化后的容量和短跑基线要求见[配方核对](../../skills/hcu-train-environment-check-and-adapt/references/workflow.md#优化器和参数分组属于模型训练配方)。

## 2. HCU Train Simulator 的实际入口与限制

已核对公开仓 [HYGON-AI/hcu-train-simulator](https://github.com/HYGON-AI/hcu-train-simulator)，固定提交 `b7d8e6f3becebf5d09121bb1c582436a371c6710`。以下是该提交的入口；以后依实际 checkout 的 `--help` 和源码核对，不保证未来命令不变。

```bash
# 在独立参考 checkout 安装，用任务自己的模拟目录保存输入/输出。
python -m pip install /path/to/hcu-train-simulator
hcu-train-sim --help
hcu-train-sim init
# 修改 config.yaml：完整 model_path、现场硬件和候选并行设置；
# 离线预估明确 profile_config.mode: theoretical，避免 auto 触发 GPU benchmark。
hcu-train-sim analyze memory config.yaml
hcu-train-sim search config.yaml
hcu-train-sim solve config.yaml --memory-margin-gib 5
hcu-train-sim run config.yaml --no-report
```

这些是按需选择的入口，不是每个模型必须全部执行的串行清单。`5 GiB` 是该版本求解示例/默认余量，不是所有环境的安全线；任务按未建模 buffer、动态 shape、恢复峰值和实测误差决定余量。

| 核对项 | 固定源码行为与工作流处理 |
| --- | --- |
| 模型覆盖 | `models/registry.py` 与具体 adapter、ModuleSpec 决定估算结构。当前模型缺少专用 adapter 时，逐项核对混合层型、递归/残差状态、辅助训练头和专家布局；generic 输出不能作为完整结构已覆盖的证明。 |
| 容量 | `estimators/memory.py` 按 PP/VP stage 估算；静态状态字节、激活 dtype、分片假设必须与实际优化器相符。总显存除参数数目不能代替峰值判断。 |
| 自动求解 | `commands/solve.py` 的 GBS 输入是偏好下限，可能为气泡限制增大 GBS；不能直接把输出作为保留原训练语义的配方。重新核对样本/token、累积和学习率契约。 |
| 搜索 | `commands/search.py` 可能随 VP 开启 overlap；逐项展开实际输出配置，不能把多个变量变化归因于单一切分。无结果先查非法候选/错误，不直接宣称全参不可能。 |
| Profile | 理论、已有校准数据和现场测量分别标记；当前内置 profile 不能替代 DTK 26.10/Torch 2.11 的现场数据。`auto` 可能运行 GPU 算子，仍需资源准入。 |
| 精度与吞吐 | 预测不证明实际实现被调用、loss 等价、峰值安全或性能收益；最终依据目标镜像和源码短跑及正常阶段验证。 |

固定证据：[CLI](https://github.com/HYGON-AI/hcu-train-simulator/blob/b7d8e6f3becebf5d09121bb1c582436a371c6710/src/hcu_train_simulator/cli.py)、[模型注册](https://github.com/HYGON-AI/hcu-train-simulator/blob/b7d8e6f3becebf5d09121bb1c582436a371c6710/src/hcu_train_simulator/models/registry.py)、[显存估算](https://github.com/HYGON-AI/hcu-train-simulator/blob/b7d8e6f3becebf5d09121bb1c582436a371c6710/src/hcu_train_simulator/estimators/memory.py)、[搜索](https://github.com/HYGON-AI/hcu-train-simulator/blob/b7d8e6f3becebf5d09121bb1c582436a371c6710/src/hcu_train_simulator/commands/search.py)、[求解](https://github.com/HYGON-AI/hcu-train-simulator/blob/b7d8e6f3becebf5d09121bb1c582436a371c6710/src/hcu_train_simulator/commands/solve.py)。普通任务读取这些证据不触发 HCU-Knowledge 更新。

## 3. 完整模型的最小可行训练实例

“最小 DP 实例”在这里指**足以运行完整模型、满足引擎与并行约束的一套独立训练作业**，并非所有情况下强制 `DP=1`。MoE 的 EP、expert-DP、dense-DP，状态分片及 TP/ETP/CP/PP 的关系由所选引擎实现决定；不能机械把所有并行度相乘计算卡数。

先选可运行且有显存余量的布局，完成真实前后向/优化器和短跑校准，再优化这个实例。阶段稳定后逐级扩 DP 检查吞吐、通信、质量和容错。若本轮确需缩模，保留代理范围；资源增加后重新评估全参，不把旧的缩模决定永久沿用。

## 4. 资源富余时并行优化多个实例

有更多已准入资源且存在独立、有价值的优化方向时，主控可分配多个完整模型实例。它们是**彼此独立的候选实验**，不是一个训练作业新增的 DP rank；不能共享可写 checkpoint、rendezvous、运行目录或混合梯度。

- **分工前冻结公共基线。** 相同模型、数据/样本规则、初始 checkpoint/RNG、precision、优化器、有效 GBS/token 与质量契约；每个实例用真实独立 checkout、候选快照、节点/GPU 列表、端口、输出目录、监测身份与资源租约。改变布局时仍明确可比/不可比项目。
- **按假设拆分。** 例如两个互不耦合的系统/算子方向；先写每个 owner 的问题、改动范围、受影响机制、预算、期望证据与 peers。主控分析任务收益和资源成本，不按闲卡数量凑 Agent，不启动重复搜索。
- **共享进展与依赖。** 每个有效发现、失败边界、接口变化或新瓶颈，通过既有 `agent-send` 和宿主投递及时告知 peers/主控。成员在新实验和提交前读 inbox，保留引用的源/证据哈希；不等人的五分钟看板周期才交换信息。固定候选跑到一半不偷偷引入别人新代码，采用后生成新候选并明确差异回归。
- **隔离真实测量域。** 不同 GPU 仍可能争用 CPU、NIC、交换机链路、功率和共享 CFS。把共同资源登记为相同 resource；无法证明隔离时性能测量串行，源码分析和准备可以并行。记录并发负载；跨节点候选先各自测基线，不能把两台机器差异算作优化收益。
- **统一复验与集成。** 汇总兼容改动与冲突，主控在共同参考实例上配对复验后组合，核对真实性能、显存、dispatch 与局部正确性。稳定候选才做阶段 loss，不让每个 Agent 频繁长时验 loss。多项收益不能简单相加。
- **筛选最终总结。** 公共基线、实例/资源与变量、成对结果、失败条件、组合复验和阶段 loss 先记录在任务档案；当前优化阶段结束后，仅将最终总结与关键数据按知识架构筛选进入 `knowledge/experiments/`。中间候选与完整 trace 不进入共享 Wiki。

协议复用 [多 Agent 协同](../multi-agent.md)、[代理范围](../proxy-contract.md) 和 [优化 Skill](../../skills/hcu-train-optimize/SKILL.md)，不另建调度系统。

## 5. 持续维护

模型 adapter、显存公式、Profile 环境、求解器默认值、引擎并行约束或现场拓扑变化时，联动复核本页与 adapt/optimize/coordinator 的用法。自动更新知识不自动切换活动训练依赖。先核对实际源码和命令，再重新估算受影响布局并补短跑校准；旧预测和实测保留各自版本及误差，不能覆盖成“当前已验证”。
