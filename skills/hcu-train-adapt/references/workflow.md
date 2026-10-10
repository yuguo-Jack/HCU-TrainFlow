# 工作目录与阅读入口

环境检查需同时按 `docs/cluster-health-and-screening.md` 核对现场 `run_nhc`、ClusterShell `clush`、当前 ClusterManager 检查脚本；先单节点确认命令、范围与输出，再有限并发扩展。命令缺失或未返回结果记为未知，不能当节点健康。

安装本 Skill 不会复制整个 Wiki。设置 `TRAINFLOW_PROJECT` 指向已 clone 的 HCU-TrainFlow；`TRAINFLOW_WORKSPACE` 指向任务私有目录。

完整安装包含 11 个 Skill，HCU-Knowledge 及其检索/更新 Skill 是必需依赖；先核对目录绑定和本地可用性。资料权限不足时反馈具体来源，不能将缺少知识库的安装称为完整就绪。普通适配与查询不隐式更新 HCU-Knowledge。

按需阅读项目：

- `docs/collaboration.md`：统一入口、候选复核、人的文件指导与断点接续。
- `docs/quickstart.md`：安装、任务、证据及 CLI。
- `docs/workflows.md`：三个工作流与验证门槛。
- `docs/environment-discovery.md`：发现镜像/宿主工具、复用容错检查、区分工具误判与硬件问题、建立可比性能预期；第 6 节要求对可信差距继续基本排查和有界尝试。
- `docs/source-transfer.md`：Windows/Linux 源码、执行位与仓内链接的固定内容传输。
- `docs/workspace-maintenance.md`：可重建缓存登记、使用 pin、五分钟维护和 context 独立观察 Store。
- `docs/training-observation.md`：真实训练日志、进程身份和退出回执；启动阶段与真实进展分开。
- `docs/training-state-validation.md`：tokenizer 一致性、优化器状态、checkpoint 资源错误和短窗口续训等价验证。
- `docs/profiling.md`：时间分母、热点建模和 TraceLens。
- `docs/operations.md`：远程 watcher、事件重放与恢复边界。
- `docs/wiki.md`：固定来源、更新复核和工作流维护。
- `knowledge/README.md`：官方引擎与生态章节。

不要读取安装目录相对路径猜测仓库位置；先使用明确项目路径。执行前检查 `hcu-trainflow --help` 和相关子命令帮助，不猜不存在的 flag。

## 启动配方选择与核对

先确认现场的镜像/Conda、调度资源、启动入口和用户 patch，再从选定的活跃 HCU 仓分支寻找可复用脚本。这套规则适用于预训练、SFT 和 RL；RL 还要分别核对训练、rollout 推理及权重同步的启动链。

| 可用资料 | 使用方式 |
| --- | --- |
| HCU 工程已有同模型脚本 | 优先采用其环境、依赖和启动约定，验证与当前硬件、软件及现场部署兼容。 |
| 只有同引擎相近模型的 HCU 脚本 | 复用已确认的平台设置；依据目标模型官方配方核对结构、精度、数据和训练参数，列出差异。 |
| 没有适用的 HCU 脚本 | 结合官方模型语义、HCU 当前实现和实际环境形成新配方，明确尚未验证的部分。 |
| 用户已有脚本或 patch | 保存原始基线与现场约束，在其基础上合并必要修改；与仓内示例冲突时核查实现及实际配置，不覆盖用户改动。 |

运行前按以下顺序核对，并在任务私有目录保留结果：

1. **追踪实际启动链。** 阅读顶层脚本、`source` 引入的配置、包装脚本和最终训练入口；确认变量覆盖顺序与最终 argv。DTK 激活与现场环境脚本分别核对，保留原配方加载顺序及内容哈希；现场脚本可能设置通信 TC、端口/GID、QP 或库路径，不把仅加载 DTK 的命令视为等价。该要求同样适用于环境单测。核对 Docker 环境传递、Conda 解释器、Slurm allocation 或 K8s Pod 的实际约束，以及每个 rank 必要非敏感参数实际生效，不把控制端的环境当作所有远端已继承。用户给出已知可工作的配方时，先在当前授权和资源准入内复现，再进行有依据的单变量调优；连接/资源调整与原命令的差异明确保留。
2. **匹配软件与设备。** 核对 DTK、PyTorch、编译器、通信库、TE/Flash-Train、动态库与设备可见性；环境变量以当前 HCU 实现支持和实际生效为准。NV 的变量名、数值和优化开关不能机械替换；例如 `GPU_MAX_HW_QUEUES` 的取值须有目标 runtime 及实测依据。
3. **核对分布式启动。** 检查节点/进程数、rank、设备映射、网卡及 rendezvous 配置；平台启动设置可以不同，目标模型语义仍需与参考一致。
4. **核对训练语义。** 对照官方模型结构、tokenizer、数据处理、mask、精度、优化器及 batch/并行配置；HCU 脚本可能包含演示规模或性能试验参数，不能无条件沿用。缩层代理单独记录。
5. **验证临时进程通信。** checkpoint 使用 Python 多进程时，在实际容器/解释器中按 `docs/training-state-validation.md` 运行 `scripts/probe_training_tempdir.py`；选择任务目录内已有的短 `TMPDIR`，核对真实 AF_UNIX 与 spawn Manager 往返。编译缓存可另放目录，不把长 attempt 名直接拼进 socket 路径。路径或共享盘变化后重测；后续 EOFError 要回查最早的子进程异常。
6. **保存可复现证据。** 记录脚本与依赖提交、原配方到任务配方的修改及原因、实际入口/工作目录、必要且非敏感的生效参数与环境。避免全量导出环境中的令牌或凭据。随后进行局部正确性和基线验证。

脚本、依赖或部署方式变化后重新核对以上项目；必要时检索 HCU-Knowledge 并回到当前分支源码确认，不把历史成功记录当作当前兼容性证明。

## 新模型和构建入口的适配验收

当模型仅在官方开发分支支持时，固定官方模型定义、训练功能分支、HCU 主仓和镜像中底层库的版本；分别记录功能来源与最终交付仓。先确认推理实现是否包含可用的反向与训练语义，不能用一个能够 forward 的推理示例替代训练基线。

1. 沿真实 launcher 追到模型 builder/config container。新增入口可能绕过旧 `model_provider` 或 `get_model`；审计钩子必须实际命中，未生成结构/梯度记录不能算验收完成。
2. 记录初始化、参数迁移、精度包装、DDP/FSDP 和优化器构建的顺序。CPU 初始化不等于允许把普通 GPU 优化器的参数永久留在 CPU；但 CPU offload、FSDP/meta 等专用路径有不同契约，不应一律强制 `.cuda()`。修复要覆盖相邻配置分支并在真实设备重验。
3. 确认实际层类型/数目、路由、激活、归一化、位置编码和参数形状。缩层时保留关键结构及跨层边界；用户允许缩维时记录授权和差异，避免只留下某一种层而误称模型适配完成。
4. 缺失底层融合实现时，用语义明确、独立验证的保守实现建立基线。随后按实际调用粒度和数值契约推进融合；不能为跑通静默换激活、routing、归一化或 mask。
5. 对 HCU 特有后端开关同时检查当前库源码、已有训练脚本、支持条件和真实 dispatch。分组 GEMM 至少覆盖前向、输入梯度、权重梯度、空 expert、梯度累积；独立子进程在 import 前固定开关，避免库缓存使对照失真。固定输入和容差，不以设置成功替代调用/正确性/性能证据。
6. 先做有界组件与完整链路检查，再使用固定 tokenizer、独立训练/验证 split 建立真实文本基线。随机 token 测试只能证明链路可运行；保存并实际恢复 checkpoint，核对模型、优化器、RNG、数据位置和总目标 step 的语义。

初始审计可能逐参数同步并严重影响性能。资格检查记录全部必要证据后，性能测量应关闭这类审计、排除编译/数据初始化窗口，重新运行 profiler-off 基准。缺少首次真实 iteration 时仍处于 startup，不能用观察器心跳宣布训练健康或已收敛。

## 缓存与观察部署

建立部署时记录私有缓存 policy，默认每五分钟由主控做一次有界 dry-run；已经明确开启自动清理的部署按同一 policy 调用 `scripts/maintain_workspace.py ... tick --enable-delete`。只由一个调用者维护，不让每个阶段或 Agent 重复扫描。当前没有登记缓存则跳过；不会自动整理旧目录。

新生成的源码传输 archive、可重建编译中间物可从一开始放在 `cache/recreatable/FAMILY/GENERATION`，通过 register 写明固定重建来源，使用前 pin、接收哈希核对和实际操作核销后释放。开发 checkout、Store objects/snapshots、原始材料、训练日志与 checkpoint 不放入该清理根。跨节点消费者也须遵守 pin，不能凭本机 lease 过期推断远端不再使用。

首次训练部署参考 `docs/training-observation.md`；已有观察任务改变真实 context 时按 `docs/workspace-maintenance.md` 准备新 context+epoch Store，保留旧 parser/monitor 数据。核对同版本 wheel/模块和显式同步的 observer 脚本；本机安装 Skill 不会更新远端。先 once，再 start 并验证 ready/心跳；每个必需 member 的进程与观察器都要检查，从固定源码与真实日志确认实际进度来源；其首次 iteration 不能覆盖其余节点。独立 sentinel 与事件 peer 随新 Store/launch 更新。

## 复用私有参考基准

按 `docs/experience-knowledge.md` 的 `reference-query` 先查当前架构/产品、软件身份、拓扑及单测条件的私有参考；compatible 且无冲突时可直接引用原证据，不反复联网查同一信息。缺项、范围变化或过期才按现有环境检查流程补查/实测，并用 `reference-record` 保留来源和有效期。标称、历史实测、当前现场实测分开；基准记录不能替代实际健康/正确性验收，也不触发 HCU-Knowledge 更新。

`reference-query` missing/stale/mismatched 时，先用 `experience-search` 按产品/架构、指标、测试类型跨上下文查待确认原文导航，暂不加精确 model/environment 过滤；随后 `experience-read` 并读取其 evidence 原件。索引不会自动扫描 artifact 正文，保存导航时须在 summary/interpretation 写明关键词、版本、表格位置和缺项。必要时联查 HCU-Knowledge 与当前来源，核对后再登记严格 reference；未知条件不补成猜测值。

性能预期应包含相关模式的近期历史/文档依据，不只比较本次测量自身。DeepEP 高吞吐应核对 HT dispatch/combine 带宽，不能用 LL 延迟表代替；检查网卡拓扑、dtype/shape、版本、XDP 和计时/字节定义。条件略有差异时仍可给出有明确限制的工程比较，保留未知项，不自定通过比例。详细记录方式见 `docs/experience-knowledge.md`。

## 适配工作树与最终交付

适配已跑通、但与 HCU 最新活跃主仓差异较大时，可以沿当前用户 patch、donor 或 HCU 适配工作树继续性能分析、侵入式优化和后续验证，不必为提前移植主仓中断关键实验。固定各来源提交、补丁和每个候选的源码/配置/数值证据，保持独立开发 checkout。将主仓整合作为明确未完成交付项；最终集中、模块化接入 HCU 当前活跃出口，再对整合后的代码重跑相应回归，不能把旧工作树的通过结论直接移贴过去。
