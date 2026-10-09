# Torch 原生训练：分析与优化路线

适用于直接用 PyTorch 训练循环、DDP/FSDP 或轻量封装的模型，包括视频生成、VLA、世界模型；也可用于大型训练引擎中的局部模块。它是优化阶段的一条分析路线，不新增阶段或 Skill。模型参数少不代表激活小：长视频、高分辨率、多视角、长时间展开都可能先耗尽显存。

## 1. 入口与共同契约

沿用 adapt 的环境验收、HCU 配方、源码锁和初始数值基线；扩 DP、筛机、checkpoint 和故障接管仍交给 fault-tolerance。`analyze` 只分析，不启动编译或训练实验。大模型引擎路线和 Torch 路线可以同时存在，按实际调用边界选择，不按模型名字强制二选一。

记录真实入口：数据读取/解码/增强 → H2D → forward → loss → backward → 梯度累积/同步 → optimizer → EMA（如有）→ scheduler → 保存/评估。确定 train/eval、冻结模块、共享权重、AMP、loss scaler、随机源和自定义 autograd。视频/VLA/世界模型还要固定帧数、分辨率、视角、动作维度、时序展开、padding/mask 和采样分布；不得通过改变任务数据或损失定义制造加速。

先评估单卡/多卡、DDP/分片、微批/累积、重算和 offload 的显存预算。用最紧张 rank 的 allocated/reserved、激活、workspace、通信/graph buffer、optimizer/保存恢复峰值实测修正；不因模型较小而默认需要复杂 TP/PP。保持有效全局 batch、样本/有效 token 数及梯度归一语义可比。

## 2. 分离启动成本与稳态整步

- 单独记录导入、加载、首次编译/autotune、首次 graph capture 与重新编译。稳态窗口覆盖完整训练步及代表性 shape，不把首次慢步混入吞吐，也不把反复发生的编译排除成一次性成本。
- 端到端使用完整窗口墙钟与实际完成工作量，跨设备异步工作在窗口边界正确收敛；GPU event 只用于定义清楚的设备片段，不替代 CPU/数据/通信在内的整步时间。
- 给 step 延迟分布、有效 samples/tokens/frames 每秒、显存峰值及编译摊销成本。不同帧数/分辨率/样本组成不可直接比较。沿用 profiler-off 配对重复测量和波动说明。
- 先区分输入饥饿、host dispatch、隐式同步、编译/重编译、collective 等待、真正设备计算。不要一见 GPU 空泡就归因于 CPU 算力不足。

## 3. 按证据选择专项

| 观察 | 源码与实验方向 | 必须验证 |
| --- | --- | --- |
| 数据等候、视频解码或大量小 H2D | DataLoader、采样/解码/增强、worker/线程与预取、pin memory/异步传输、存储带宽；先量各段等待 | 数据顺序/随机性、worker 内存、host 峰值；异步接口存在不代表已重叠 |
| CPU launch/同步密集 | 查 `.item()`、`.cpu()`、日志/指标/回调及每步 barrier；合并必要统计、延后安全的取值 | 日志与异常仍可观测，跨 rank collective 顺序一致，不能删除必要同步 |
| eager 碎算子、重复 block | 先对稳定热点模块试 `torch.compile`，比较 eager / compiled 的前向和反向图及真实 dispatch | 编译时间、fallback、实际 HCU backend，完整训练步收益 |
| graph break / guard / recompiles | 当前版本日志定位到源码；区分不支持操作、Python 副作用、数据依赖控制流、shape/stride/标量值变化 | 代表性动态输入都覆盖，不能只为单个样本消除 graph break |
| 动态时空尺寸导致频繁编译 | 评估动态 shape、有限 bucket、编译边界；保存 shape 分布和各变体成本 | padding/mask/样本权重等价，缓存与显存受控；不偷偷缩短视频或序列 |
| 小 kernel 很多但图较稳定 | 评估 graph capture/replay 或减少 host 调度 | 目标 HCU/PyTorch 支持、地址与生命周期、随机数、动态控制流、图池占用、反向和 optimizer；不盲开 NV 开关 |
| layout 转换/拷贝密集 | 查 permute/contiguous、视图、卷积/attention/GEMM 输入输出；按子图评估 layout | fwd/bwd、alias/in-place 契约与全链路转换成本；不全局强制 channels-last |
| backward/optimizer/重算显著 | 查 saved tensors、checkpoint、RNG、副作用、融合/foreach optimizer 和 state/offload 路径 | 梯度、参数更新、optimizer state、EMA 和恢复一致性；重算并非无条件省内存且不损吞吐 |
| 编译后通信暴露变多 | 联合检查 DDP bucket/通信触发与编译图边界，FSDP gather/prefetch 的存活区间 | 按通信指引测整步；“更大完整图”不必然更快 |

### 编译问题的定位顺序

先从目标安装包/分支源码与 `--help` 确定接口，再读取匹配版本官方教程。可用当前版本支持的 `TORCH_LOGS` 类别收集 graph breaks/recompiles/guards；不能把某一 DTK/PyTorch 版本的私有开关固定为默认配置。若编译失败或结果不符，可在可复现脚本中逐层隔离 eager → Dynamo 捕获 → AOTAutograd 前后向 → Inductor/Triton，保留原输入、dtype、stride、随机种子和版本；这些诊断 backend 的可用名称由当前版本确认。

`fullgraph` 可用于暴露断图，但不规定全训练循环必须单图；DDP 的通信时机可能依赖图边界。不要默认 suppress errors 后声称编译生效。手改生成缓存只适合定位，正式方案回到模型、图变换、编译器或稳定自定义算子入口，验证清空缓存后的重建。

**AOTInductor/export 不作为默认训练加速方案。** 仅当项目确实使用导出路径，或冻结编码器/评估/rollout 等子模块有明确需求时评估；分别核查 autograd、参数更新与部署支持。AOTAutograd 的训练图处理不能和 AOTI 推理打包混为一谈。需要可训练自定义算子时补正确 backward，以及当前编译路径需要的注册/形状/别名描述，再交给已有 Hygon kernel Skill。

## 4. 收益排序与交付

候选表记录：源码位置、症状、关键路径证据、预计整步可省时间范围、置信度、编译/显存代价、数值风险、依赖、验证及回退。区间来自当前计时与可达参考；不能重复相加互相重叠的收益，不使用固定百分比强迫无限优化。沿用 TrainFlow 的任务拆分、迭代、独立复核、experience 和预算，不另建一套权威 ledger。

系统/编译问题与算子优化可按独立范围并行。累计 ≥90% 端到端热点集合中的非通信 op 仍须按真实 shape 建模；框架优化不能代替该评估。优先复用 HCU TE/Flash-Train 和当前库能力；需要实现再调用 HIP/Triton Skills。

每轮比较初始正确基线的输出、loss 分量、梯度和参数更新，覆盖多 shape/mask、train/eval、累积边界、随机操作和保存恢复。稳定候选再验阶段 loss；视频/动作等任务使用匹配目标的质量与验证集指标，不能只套语言模型 loss。保留最近已验收最佳候选，退化方案记录原因并回退；交付实际采用的代码/配置、编译策略、缓存重建、收益和限制。

## 5. 版本查证入口

- [PyTorch compile 教程](https://docs.pytorch.org/tutorials/intermediate/torch_compile_tutorial)：eager 与编译调用路线。
- [编译问题定位源码文档](https://github.com/pytorch/pytorch/blob/main/docs/source/user_guide/torch_compiler/torch.compiler_troubleshooting.md)：断图、重编译、定位方法。
- [compile profiler 指南](https://docs.pytorch.org/docs/main/user_guide/torch_compiler/torch.compiler_profiling_torch_compile.html)：编译区域和 timeline 证据。
- [DDP 文档](https://docs.pytorch.org/docs/stable/generated/torch.nn.parallel.DistributedDataParallel.html)、[编译与分布式 FAQ](https://docs.pytorch.org/docs/stable/user_guide/torch_compiler/torch.compiler_faq.html)：bucket、累积和图边界。

这些是滚动官方入口，不是 HCU 支持承诺。当前任务将实际读取版本/提交写入私有经验；升级时与 HCU-Knowledge 中的 PyTorch、编译器、runtime、库和教程交叉核对。
