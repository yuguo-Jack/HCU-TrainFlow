# 模型内外同条件对照

在端到端剖面出现热点或怀疑训练并发拖慢算子时使用。先取真实调用条件，再构造最小重放；类别由实际热点决定。这里只规范比较方法，具体后端函数、签名与可用测量工具从当前分支和镜像查证。

## 1. 保留可重放的调用条件

| 类型 | 必须核对的条件 |
| --- | --- |
| GEMM / grouped GEMM | 每个矩阵的 shape、stride、dtype、转置；fwd/dgrad/wgrad；输出及累积 dtype；alpha/beta、accumulate、bias/激活融合；group splits、空组和实际数学库/算法 |
| Attention / 递归注意力 | Q/K/V 或状态 shape、布局、head/group关系；mask/causal、序列长度及变长边界、scale、gate、归一化；前后向和保存/重算；实际 backend、数值路径及中间 kernel |
| 通信 | 实际 process group 有序 rank、物理拓扑、每 rank 输入/输出及每 peer split、dtype、in-place、async/wait、stream；dispatcher 通信前后布局；不能只根据 hidden size 推算消息量 |
| Copy / cast / contiguous | 源与目标设备、dtype、shape、stride、offset、字节量、pinned/pageable、non_blocking、alias；区分 D2D/H2D/D2H、类型转换、布局转换与无实际拷贝的 `to()` |
| 其他热点 | 真实算法、输入分布的影响、前后向、输出/临时状态及分发路径；不能借父 CPU op 的形状给所有子 kernel 套同一 FLOPs |

原始 trace 的 correlation、CPU 范围与调用侧元数据共同定位。元数据只读 shape/stride 等主机信息，避免为采集额外调用 GPU `.item()`、`.cpu()`、同步或打印张量。必要的内容采样单独做并注明扰动。Tensor 方法包装不能覆盖 C++ 内部所有 copy；TE 的 Python 包装也不能覆盖直接 C++ 调用，未捕获项继续列为缺口。

**调用身份优先于层号。** MoE 路由、动态序列和稀疏输入可能使两次运行同一层的真实 token/split 不同。把重放契约绑定到具体 run/rank/step/call，逐张量检查 shape/stride/dtype，再比较后端和 native kernel。不能将诊断 run 的分组 GEMM shape 套到干净 run 的同层 kernel；只有实际条件相同的调用才可跨 run 比较，其余分别报告。trace flow 重复或缺失时核对 runtime correlation 的唯一性，歧义记录为未匹配，不能按名称强行关联。

**提交边界可能延迟。** `_coalescing_manager` 等机制会先记录 collective，退出管理器时才通过 TensorList/coalesced API 提交。因此 Python 包装区间下没有 kernel，并不表示零通信。追踪实际提交、process group、等待和所有组成 tensor；独立单 API 重放只能证明同消息量路径，若没有复现合并提交，必须明确这一差别。包装参数 `async_op=False` 也不能证明管理器内部采用同步提交。

## 2. 三类测量分别保存

1. **干净端到端运行**：关 profiler 与侵入式采集，记录稳态 step/token、显存和当前初始基线。冷编译、启动、checkpoint、eval 分开列。
2. **模型内诊断运行**：稳态完整 step，多 rank，实际 kernel 区间和 CPU 提交/同步；元数据包装若改变提交节奏，单独标记，不当无扰动吞吐。记录每次调用分布，不只一个总均值。
3. **独立重放**：相同硬件、库、调用条件，先核对正确性与实际 kernel，再 warmup、多区块采样。分别报告设备服务时间与主机提交到完成时间；测量区间不含随机输入生成、编译或未计入模型的重置操作。输入数据影响路由/稀疏性时保留分布或选定样本，不能用等尺寸稠密随机张量替代算法。

独立通信所有参与 rank 同时重放实际 split 矩阵；检查发送/接收守恒、内容正确性和最慢 rank。分别给同步发起的基线与模型真实到达/等待，RCCL kernel 驻留时间可能包含等待其他 rank。小消息延迟不与大消息带宽直接比较。性能测量与其他作业的 GPU/NIC/CPU/存储竞争按准入规则隔离或明确记录。

重复小张量可能一直命中缓存；需要对照 HBM 上限时用匹配工作集或循环 buffer，保留热缓存/冷缓存条件。Copy 流量按读加写与单方向两种口径明确命名，不能把 memcpy API 时长、SDMA事件和转换 kernel 混为一个数字。

GPU 服务时间按完整调用的所有子事件计算，包含必要的 scratch memset、copy 与多个计算 kernel，双方使用相同类别和窗口。大 tensor 可能因索引范围被拆为多个 kernel：FLOPs/字节按实际处理区间累计，不能给每个子 kernel 重复记整张量工作量。服务时间求和与区间并集分别命名，有并发时不混用。独立测试的 profiler 单次样本也可能显著慢于 profiler-off 多区块；两者都保留并调查，不能拿某个较慢 profile 作分母宣布“模型没有拖慢”。

## 3. 判断与后续实验

- 给出模型/独立耗时比及采样波动；只有计时范围一致、差距超出实际噪声后才称显著拖慢。阈值随现场基线记录，不能事后选最好样本。
- 独立实现已经明显低于匹配可达参考：沿算子 Skill 查计数器、访存、调度/指令并优化实现。
- 独立正常而模型变慢：按证据对照通信 overlap、queue/stream、频率/功率、HBM竞争、缓存、CPU提交和rank到达；一次改变一个因素，复验端到端收益与正确性。不要直接把所有通信等待认作带宽不足。
- kernel 很快但主机提交到完成慢：追小op数量、同步和融合机会。融合需明确可合并边界、减少的读写/launch、保存状态与累加精度，先查现有 HCU TE/Flash-Train/Primus Turbo 能力。
- 上限表分别列理论下界、匹配独立可达参考、当前模型实测。`max(FLOPs/算力, bytes/带宽, 延迟下界)` 是假设模型；效率大于1需复核条件。小GEMM、归约、依赖链、混合通算不能机械套大方阵峰值。

同一个 op 的 fwd/bwd 或不同 shape 可能有不同结论。最终按不重复的端到端墙钟贡献排序；保存每个热点的实现位置、条件、独立实测、模型实测、上界、剩余空间与保留/优化/待证据决定。稳定候选按主 Skill 做阶段 loss，不因一次 kernel 正确便宣称训练精度保持。

## 4. 融合实现和编译兼容的实验边界

优先资格验证已有后端，保留失败的编译日志、最小复现和当前编译器源码证据。改变编译选项修复一个融合算子时，先核对它是否是进程级开关：全局关闭某项优化可能同时改变模型中其他算子。采用可回退、显式启用且版本绑定的最小作用范围，并实测前向、autograd worker 上的反向、异常退出后的状态恢复；没有隔离的并发编译不能视作已验证。记录最终真实 dispatch，分别检查局部数值/梯度和模型收益，再在稳定阶段对初始数值基线验 loss。局部兼容实验不能自动成为所有环境的默认开关。
