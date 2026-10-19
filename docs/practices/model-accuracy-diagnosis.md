# 模型精度诊断：跨平台对照与 HCU 自查

本页供适配、优化和长稳阶段共用。首次建立数值基线、融合/编译/低精度改动后出现偏差，以及训练中出现 NaN/Inf、loss 异常、梯度异常或恢复后偏离时，按症状进入。仅环境检查无需跑模型精度实验；仅分析或诊断按授权交付定位证据，不自行重启训练或修改候选。

**目标是定位第一处有意义的分歧，并验证修复。** 不要求每个新任务先全量 dump，也不把反复长训当排查方法。正常优化做受影响的局部正确性回归；较长 loss 对照放在稳定里程碑，沿用[训练状态验证](../training-state-validation.md)与[质量契约](../contracts.md#qualitycontract-与记录)。工具未部署、无法重放或无独立参考时保留缺口，不能把空报告写成通过。

## 1. 先确认比较对象

权重转换 roundtrip 只验证其实际覆盖的 dtype、张量和转换方向，不替代前后向、优化器更新或阶段 loss。部分低精度路径可能被测试明确跳过；也要区分模块输出 dtype 与矩阵指令的内部累加/截断类型。模型脚本覆盖配置后保存最终 resolved 配方，不能只比较输入配置文件。

同名模型、相同 seed、相似 loss 曲线都不足以证明条件相同。建立两组对照前，保留以下最少充分清单；原件和实际路径放任务 workspace：

| 对齐对象 | 必须核对的事实 |
| --- | --- |
| 模型与初态 | 模型定义/配置、权重与 buffer、实际加载 key、权重转换规则；优化器参数组/master/moment、scheduler、EMA 及低精度状态。初始化时比较实际张量，不能只比 seed |
| 输入与目标 | 固定 batch 的原始/预处理内容指纹、token ID、labels 的位移、position、mask、packing、padding、有效 token 分母。视频/VLA 等另固定图像/帧/动作归一化、增强、噪声和 timestep |
| 执行语义 | train/eval、dropout/RNG 流、梯度累积次数、有效全局 batch、loss sum/mean 与辅助项、clip/unscale、跳步、学习率及总调度长度 |
| 并行身份 | DP/TP/PP/CP/EP 组与切片、实际 rank 到逻辑层/样本的映射、microbatch 与累积边界；PP 重算要区分原 forward 和 recompute |
| 数值路径 | 存储/计算/累加 dtype、autocast、矩阵乘精度、量化 scale/amax 历史、规约精度、attention backend、compile/graph、融合与实际 dispatch |
| 软件与采集 | 源码/submodule/制品版本、HCU/DTK 或 NV/CUDA 环境、Probe 版本、过滤条件、采集开销、缺失项和基线自身重复误差 |

任务先前采用缩层代理时，对照双方必须是同一代理；不能拿全模型和缩层 loss 相比。保留完整目标的未覆盖范围，不为精度排查擅自改 hidden dim、优化器或训练目标。数据敏感时在授权环境内对比，外发问题包使用经核对的脱敏复现，不上传真实样本/权重。

### 低精度状态与 checkpoint 版本

权重 dtype 相同不代表训练状态相同。分别核对 recipe、量化 scale/amax 历史、权重缓存与 optimizer master/state 的所有者和保存范围；恢复后执行相同输入的下一步，比较实际状态更新与输出/梯度。无状态 recipe 的空附加状态可能符合格式，带历史的 recipe 则不能靠丢弃该状态绕过加载错误；状态是否必需须由实际版本的序列化与加载代码判定。

HCU-Knowledge 的 `te-fp8-state-and-recompute` 保留了这种版本差异：TE `main@73dbcf534252`（2.18 开发线）对已识别的 stateless recipe 不再保存/反序列化 pickle 附加状态；DelayedScaling 历史、旧格式或未知 payload 默认可能被拒绝。`NVTE_ALLOW_UNSAFE_PICKLE_EXTRA_STATE=1` 是可信旧 checkpoint 的显式兼容选择，不是通用训练默认，更不能代替 scale/history 恢复后的数值验收。`release_v2.16` 和现场制品需分别查实现，不能由 main 新策略推定其行为。普通模型权重转换往返、完整训练状态恢复和异步写入完成仍是不同检查。

## 2. 有 NVIDIA 环境：分层建立跨平台对照

1. **确定可比实现。** 以支持该模型的官方训练配方/实现为语义依据，HCU 端使用适用的 HCU 启动方式。记录官方与 HCU 补丁差异；NV 运行也需通过自身基本正确性检查，不能把某张卡的输出自动当作数学真值。
2. **导出共同初态与固定 batch。** 优先从同一权重和训练状态加载；转换 QKV 排布、转置、expert 顺序、分片或绑定权重时，校验转换后实际逻辑张量。硬件数量不一致时先比较可对应的局部模块，或按逻辑切片重建比较；不直接配对不同意义的 rank0。
3. **先固定一个短窗口。** 对照输入 → block 边界 → logits/各 loss 项 → 输入和参数梯度 → unscale/clip/规约 → 参数更新与状态。梯度相同但更新不同，优先查 optimizer/master/state；前向接近但 backward 不同，查保存量、重算、梯度缩放与分布式归约。
4. **区分算法差异与实现错误。** 核对两端矩阵乘和 attention 精度、融合边界、累加/舍入点、低精度状态；TF32、flush-to-zero 等设置分别沿各自 Torch/编译器/库版本的真实消费者确认，不能假设 HCU/NV 同名选项等价。改变计算精度或 subnormal 处理后检查生成代码/实际 dispatch 与对应边界输入，不能只比较全局配置或复用另一精度条件的调优结论。先以两端各自重复运行估计波动；跨平台不默认要求逐位一致。控制 dropout 时需对齐实际随机输入/掩码；临时关闭只能定位，修复后回到原训练语义验证。
5. **对可疑模块交叉验证。** 相同捕获输入分别跑 HCU 候选、NV 路径，以及可获得的独立/更高精度参考。判断差异从哪里产生，而不是只看谁更接近谁。NV 卡放不下全模型时可只承担局部参考，不能把它写成全模型 NV 对照通过。
6. **修复后恢复真实配置。** 局部输出、梯度与更新通过，再在稳定阶段从相同初态验证实际配方的 loss。两端不同并行规约次序时记录可比层级；无法做逐 step 等价，另设计有依据的统计评估，不能把不匹配数据送入 `quality-check` 凑通过。

## 3. 没有 NVIDIA 环境：逐层自查与独立参考

按当前证据选择最有区分力的一步，不机械做完所有组合：

| 方法 | 能回答什么 | 必须保留的限制 |
| --- | --- | --- |
| 同 HCU 基线重复运行 | 本机随机性、非确定性、间歇并发差异多大 | 重复一致不能排除共同错误，loss 下降也不能证明实现正确 |
| HCU 最后可信版本对候选 | 改动引入了什么回归 | 可信版本也可能继承旧 bug；核对当时输入/状态/验收，不只看旧 pass |
| 原生/eager/未融合实现对候选 | compile、融合、低精度或特定 backend 是否引入偏差 | 两条路径可能调用同一底层库；确认独立性，逐项改变，重新核对 dispatch |
| 小规模 CPU FP64/FP32 或独立公式 | 可疑数学运算、梯度及累加是否符合定义 | 更高精度参考须真正采用相应计算且算法适用；不能证明 HCU 全模型、通信或低精度状态正确 |
| 小规模梯度数值检查 | 自定义 backward/JVP/VJP 是否符合前向 | 只用于支持的可微、足够精度且确定的局部输入；routing、离散 top-k、不可微点、随机过程、重叠内存要专门处理 |
| 有数学依据的不变量与边界样本 | mask、归一化、置换、分片重组、空 expert、边界长度的契约 | 只检查模型确实满足的性质；不能默认所有 masked 张量应有限或所有归一化值都非负 |
| 同初态单机/多机、连续/恢复对照 | 归约、数据分片、状态恢复是否引入差异 | 保持有效 batch/归一化和逻辑数据相同；多机专属竞态可能不在单机复现 |

保守路径可在单个可疑模块使用 FP32 或关闭某个融合以缩小范围。每次记录变量、预期判别和结果；排查用配置不直接成为最终修复，更不能为通过比较暗改精度/优化器/目标。必要时调用现有 baseline/HIP/Triton Skill，建立独立契约和局部参考后优化。

参考仍不充分时，结论写成“已排除哪些原因、当前覆盖哪些局部契约、尚缺什么对照”，交用户/模型或库专家；没有 NV 不阻止合理自查，也不能宣称已验证 HCU/NV 等价。

## 4. HCU Probe 的接入与证据检查

### 先发现当前工具

用 `$hcu-knowledge-search` 查询项目 `dcu_probe` 的工程报告、`hcuprobe-hook-tensor-lifecycle` 和 `hcuprobe-cross-rank-first-diff`，再核对目标环境当前源码与入口。已核对的固定版本为 `26.2.0-dev@b8dddb57`：distribution 是 `hcu-probe`，import/CLI 为 `hcuprobe`，实现位于 `python/hcuprobe/`。这是查证起点，不是固定要求所有环境安装此版本；历史 `dcu_probe`/`msprobe` 命名、配置和目录不能混用。

公开参考 [HYGON-AI/hcu_probe-das@de68655e](https://github.com/HYGON-AI/hcu_probe-das/tree/de68655e9bd3a3678fd29889982135c473d25f94) 已可读取，但不能据仓名推导 import 命名空间。其 pyproject 仍打包 `python/hcuprobe` 并提供 `hcuprobe` CLI，新增 `python/hcuprobe/tools/compare.py` 却残留 `hcu_probe.core...` 导入；该包装器及仓内框架接入示例尚不能视为已验证安装入口。先用当前制品的正式 CLI/API 核验，不自动安装仓内附带的其他 Agent Skill，也不因新增框架文档就认定训练、推理及所有后端均已通过。

在实际采集环境确认包来源、Torch/HCU 兼容性以及：

```bash
hcuprobe --help
hcuprobe compare --help
```

构造器、配置 schema、compare 参数、支持的后端和安装 extra 以该版本为准。仓库包含上游其他后端不等于 HCU 可用；NV 侧也需检查兼容性。安装/导入失败先按知识库和源码解决当前依赖，不能为调试盲目替换训练 Torch/DTK。若该框架路径不支持 Probe，使用已核对的引擎 dump 或有界自定义 hook 采等价证据，标明缺口。

### 采集生命周期

下面只示意已核对版本的生命周期，配置文件及训练函数由任务按现场准备，不是通用可直接运行的模型脚本：

```python
from hcuprobe.pytorch import PrecisionDebugger

debugger = PrecisionDebugger(config_path=probe_config_path)
# 在实际分布式初始化、设备/rank 选择完成后进入需要采集的范围。
debugger.start(model=model)
try:
    run_selected_training_step()  # 需采 backward 时，本范围必须覆盖真实反向。
finally:
    debugger.stop()
debugger.step()  # 仅正常完成后推进；映射到真实 iteration/microbatch。
```

多 microbatch、1F1B、重算、共享模块及多个模型实例需按实际调用序列接入，不能机械在每次 forward 后 `step()`。默认 hook 不保证自动捕获 optimizer 的全部 master/state；需要更新证据时显式保存更新前后状态，核对与参数 ID/分组对应。诊断 NaN 时可按当前 PyTorch 使用 `detect_anomaly` 覆盖前向及反向取栈，但它不保证捕获所有前向 Inf、通信错误和自定义实现；辅以明确边界的 finite/状态检查，不常驻性能运行。

### 先小范围统计，再采实体张量

1. 选相同少量 step、相关 rank 与层，先确认 hook 真正命中。保存 rank/组、microbatch、phase、调用序号和 module/API 到语义边界的映射。forward 重算不能和原 forward 混配；不要只按文件排序或同名层配对。
2. 用统计或摘要缩小范围，再对候选层及其输入/输出/梯度补实体 tensor 与栈。统计不能还原逐元素误差；摘要只用于快速筛查，不能当容差或密码学证明。该固定版本部分名为 MD5 的字段实际是 CRC32，使用时检查当前实现。
3. 核对 start/stop/step、flush、JSON 索引与实际文件。空匹配、未匹配调用、缺 rank、缺 backward、meta/fake 只有元数据、异步写入未完成都记录为不充分。退出码 0 或报告存在不代表数值通过。
4. 异步采集可能 clone 张量并延长显存占用，保存线程也会引入同步/I/O。必须确认快照在后续原地修改前固定、跨流生产者完成、异常退出是否 flush；不能把引用到后续被改写的张量当当时输入。
5. 编译/Graph 模式可能绕过 hook，Probe 也可能引入 graph break 或改变调度。诊断用 eager 能缩小问题，但最终应在原 compiled/graph 路径用其真实输入和边界证据复验；采集后消失的故障保留竞态候选，不能直接关闭。
6. 采集前估计字节量、额外显存和磁盘余量，按定位逐步扩范围；缺少通信因果信息时再补相关完整进程组。完成诊断后关闭采集，独立测性能。废弃 dump 按[工作区维护](../workspace-maintenance.md)在阶段收尾/低频节点退役，失败唯一原件、基线和修复证据保持保护。

## 5. 如何判读误差与定位首差

先验证 shape、dtype、layout、有效区间和语义映射，再看数值。对正常有限张量，按预先声明的 `abs(candidate-reference) <= atol + rtol * abs(reference)` 等契约报告超限比例、最大/均方误差、误差分布及异常坐标；可辅以相对 L2、余弦和幅值分布。接近零的参考值需注明相对误差分母处理，不能只看余弦一个数，也不能忽略少量高幅值异常。

NaN/Inf 单列计数、位置和最早来源。attention mask 等语义允许的 `-inf` 只在已声明边界按模式检查；loss、梯度或更新中的非有限值不可通过 `equal_nan`、删异常样本、夹值或抬高容差掩盖。双零/单零向量和空张量按明确契约处理。阈值来自任务精度要求、参考算法、dtype/累加误差和基线自身重复差异，不照抄工具默认“达标分数”，不得看见候选误差后放宽。

混合精度的溢出另核对实际 loss scale、`found_inf`、是否跳过参数更新、scheduler 推进及后续有限值。受控缩放/跳步与坏梯度写入参数不是同一现象；连续溢出、无有效更新或与基线行为不符必须排查。保留原始异常，不把跳步样本改写成正常更新；当前监控的非有限告警仍需解释和处置，不能仅凭“用了动态缩放”消警或放行质量门槛。

逐步缩小：**异常时间/step → 逻辑 block → API/融合边界 → 首差的输入与输出 → 固定调用方和底层库源码 → 独立复现**。单轮先验证最能区分假设的一项；有单调且可复现的范围才二分，误差会衰减或非确定性时不能假定“越后误差越大”。

| 首差位置或症状 | 下一步优先检查 |
| --- | --- |
| 模型入口已经不同 | 数据游标、tokenizer/增强、mask/labels、初态或转换；不先调 kernel |
| 输入相同、前向首次偏离 | 边界/mask、cast/累加、低精度 scale、实际 backend、未初始化/越界或跨流读写；归属 TE/Flash-Train/Primus Turbo/数学库等实际实现 |
| 前向通过、反向首次偏离 | 保存/重算的中间量、detach/in-place、dropout mask、loss scaling、累积/清零和自定义 backward |
| 归约前后才出现偏差 | process group、数据分片、sum/mean、分母、规约 dtype/顺序、异步完成与 buffer 生命周期 |
| 梯度通过、参数更新偏离 | 参数 ID/组、master/moment/step、unscale/clip 顺序、跳步、weight decay、部分更新后错误重试 |
| 恢复后或若干步才偏离 | scheduler/RNG/数据位置、量化状态/EMA、异步 checkpoint 完成、数值累计；从最后可信保存点重放同样数据 |

Probe 自动首差分析是候选定位，不能代替因果确认。多 rank 必须核对通信组、P2P peer 和调用顺序，沿错误接收张量回溯发送者；不把 CSV 第一行或最先打印异常的 rank 当根因。交叉更换节点/库只能在资源授权内进行，并固定其他变量，用来区分软件与硬件/链路问题。

初始基线或常规回归若在充分覆盖下满足声明契约，记录覆盖范围后直接回所属阶段，无需强找一个根因。原异常未复现却仍无法解释时，仅能报告“该窗口未复现”，继续保留原问题和证据；一次对照通过不能关闭间歇故障。

## 6. SFT、RL 与扩规模的补充

- **SFT**：分别检查模板、assistant-only loss mask、packing 边界、label shift、padding/截断、LoRA base/adapter 与可训练参数范围。平均 loss 接近也可能隐藏监督 token 不同，先比实际参与 loss 的 token 集。
- **RL**：先固定同一批 rollout 样本、policy/权重版本、温度/采样与生成 mask、位置、logprob 算法，比较训练侧与 rollout 侧对相同 token 的 teacher-forced logprob。reward/advantage/KL/clip 与可选 critic 分开查；检查旧/新 policy、异步数据年龄、截断/终止和权重同步完成。不同随机生成文本的 reward 曲线不能直接当精度对照；恢复后首批 rollout 和更新另验，不扩大为完整 RL 收敛证明。
- **视频、VLA、世界模型**：固定预处理/增强、噪声、timestep、条件输入、loss 权重/规约及 EMA；按实际时空和动作布局匹配，避免把文本模型的 token loss 口径套用到所有目标。
- **扩 DP/切并行**：先定义强/弱扩展、有效 batch 与学习率策略，验证按有效 token/样本加权的归约。若 batch 或训练语义已变，单独建立新上下文，旧曲线只能参考，不能强行逐 step 对齐。分片重组后才比较逻辑参数/梯度。
- **长训异常**：保留异常前最近有效 checkpoint、数据/RNG 和首错窗口。由既定恢复负责人按任务策略处理重启；数值异常不应默认无限从同一问题状态重启。Agent 的取证、修复与重新验收沿原控制权边界进行。

## 7. 修复验收、交接与结论范围

先做能复现原问题的局部修复回归（输出、输入/参数梯度及受影响更新/状态），再回到原融合、compile、精度、并行/恢复配方验证真实 dispatch。有效修复进入同一候选快照，稳定阶段做同初态 loss 对照；性能在关闭重型采集后单独测。基线、当前最佳和候选分别保留，组合优化不能只与上一轮候选比较。

沿用现有问题 ID、context/attempt、report 和 BOARD，不新增一套审批流程。简明诊断记录至少包含：

- 症状/触发条件、初态与样本/配方指纹、基线与候选制品身份。
- 有 NV/无 NV 的参考路径及其独立性，采集覆盖/未匹配项/额外开销。
- 首个可信分歧、原始张量/栈/源码位置、误差分布与阈值依据。
- 已排除项、根因置信度、修复或临时缓解、局部/集成/阶段验证和回退。
- 未验证范围与下一步；受影响候选未通过不得晋级，其他独立调查可继续。

`quality-check` / `stage-quality` 重算已保留的阶段 loss 与身份条件，不会运行 Probe、自动验证 tensor mapping 或证明模型正确。Probe CSV/图片附为原始证据，不能伪造为通过的 QualityContract。局部正确、同平台回归、跨平台可比、阶段质量和长期收敛分别表述。只有跨项目可复用的方法进入本指南；一次排查与中间 dump 留任务档案，合格最终总结按 Wiki 规则筛选。

## 8. 查证与后续维护

本方法依据 HCU-Knowledge 已保留的 `dcu_probe` 工程报告及两个专题，并核对 `b8dddb57debbe31fb9a0ba46f7429de9c28014a5` 的 PyTorch debugger 生命周期。该来源为内部工程，通过已绑定 HCU 知识库查询；不把其私有源码复制进公共 TrainFlow。

2026-10-20 增量复核还使用公开 Probe `de68655e9bd3a3678fd29889982135c473d25f94` 的包元数据和包装器、HCU TE `main@73dbcf534252d13f463d63c439cf7c41bb05150e` 的 `_extra_state.py`/`module/base.py`，以及 HCU PyTorch 公开 `2.12.0-dev@acf085724329a8c07556709324cb757ce7046fbd` 的精度消费者与数值修正。它们补充本页的版本/状态核验方法；没有安装 Probe、重放 checkpoint 或进行 HCU/NV 精度实测。具体来源与未覆盖项继续从大库工程指南查询，不把开发线文档、UT 记录或同号 wheel 当作现场兼容证明。

通用边界参考 [PyTorch 数值精度](https://docs.pytorch.org/docs/2.11/notes/numerical_accuracy.html)、[可复现性](https://docs.pytorch.org/docs/2.11/notes/randomness.html)、[autograd 调试](https://docs.pytorch.org/docs/2.11/autograd.html#debugging-and-anomaly-detection)。这里核对的是 2.11 文档，实际命令/配置仍须匹配部署版本；CPU/NV/其他平台的文档不证明 HCU 分支已实现同样能力。

更新 Skill 维护本页时，同时检查 Probe 的包/入口、config schema、hook 与异步落盘、compare/mapping/首差、训练和推理框架接入，以及三个阶段的阅读路径。必要时查最新源码/PR，普通查询不更新 HCU 大知识库。不要求预先验证所有模型/后端；当前登记的方法、离线回归和现场实测分别记录。
