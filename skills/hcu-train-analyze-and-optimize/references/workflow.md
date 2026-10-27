# 工作目录与阅读入口

安装本 Skill 会复制其 references，共享 docs/Wiki 从工程读取。按入口约定采用用户明确的工程路径、`TRAINFLOW_PROJECT` 或安装目录 `workspace.json.project_root`；按项目 `docs/skill-reading-map.md` 的当前模式进入。`TRAINFLOW_WORKSPACE` 另指向任务私有目录。

完整安装共 11 个 Skill，包含必需的 HCU-Knowledge 与其检索/更新 Skill。按需跨查平台机制、原文与案例；普通优化、查询和局部经验维护不隐式更新 HCU 大知识库。

按需阅读项目：

- `docs/collaboration.md`：统一入口、候选复核、人的文件指导与断点接续。
- `docs/quickstart.md`：安装、任务、证据及 CLI。
- `docs/workflows.md`：三个工作流与验证门槛。
- `docs/environment-discovery.md` 第 6 节：性能差距的原件查证、基本排查、授权内有界对照与复验/升级；单测或模型表现异常时读取。
- `docs/profiling.md`：时间分母、热点建模和 TraceLens。
- `docs/operations.md`：远程 watcher、事件重放与恢复边界。
- `docs/training-observation.md`：原始训练进展、逐 member 健康及观察器生命周期。
- `docs/workspace-maintenance.md`：登记缓存的保守维护、context/epoch Store 与事件 peer 交接。
- `docs/wiki.md`：固定来源、更新复核和工作流维护。
- `knowledge/README.md`：官方引擎与生态章节。

不要从安装目录的父级猜仓库位置；先核对上述工程绑定。执行前检查 `hcu-trainflow --help` 和相关子命令帮助，不猜不存在的 flag。

开始分析/优化时读取[原生能力调优与实现迭代](native-engine-tuning.md)：先核对训练/推理引擎已有优化项及实际配置，与并行/显存联合取舍。后续缺依赖则衔接实现，补齐后返回配置及组合验证；仅分析保留建议与缺口，不启动优化实验。

## 候选缓存与观察交接

候选源码传输包、编译缓存和可重复解析的中间物，可按部署 policy 登记在 `cache/recreatable/FAMILY/GENERATION`；先保留固定来源和重建方法，使用前 pin，候选的远端操作明确完成并核销后释放。原始 trace、profile 窗口/shape 证据、初始数值基线、最好候选、恢复点及报告留在正常证据体系，不能因“已生成图表”就删除原件。调试 dump、重复 profiler 中间物和临时保存点另在 scratch/disposable 下登记 owner/pin；一批实验结束后，确认无用且停止写入、保留必要证据，才显式 retire。旧临时目录不自动登记或清理。

清理由主控在实验批次结束、阶段交接时调用 `scripts/maintain_workspace.py ... tick --trigger experiment-batch`，同阶段长时间工作默认6小时间隔，不随五分钟交互扫描。大采集/回放前只查容量；默认 dry-run，已配置自动删除 policy 时使用 `--enable-delete`，无需每轮重复审批。活跃/unknown 作业、lease、pin 或源码引用继续阻止淘汰，已保护代次不做重复大文件哈希。此策略不自动重建被清理缓存，也不会从大知识库刷新源码。

真实 TaskSpec context 改变时，使用新 context+epoch 观察 Store；只换 parser state-dir 不能重置 monitor 的旧上下文。保留旧原始日志、退出/观察回执及事件后，按新 manifest once/start-ready 检查，重连独立 sentinel，以唯一新 peer 导入事件。普通同 context 重试改 attempt ID 即可。先由固定源码和真实日志确定 rank0、全局最后 rank 或专用 logger 中谁实际输出训练进展；多节点仍分别验证全部必需 member 的健康和失败日志；阶段完成同时检查全组真实终态。详细步骤和脚本以 `docs/workspace-maintenance.md` 为准。

## 复用私有参考基准

按 `docs/experience-knowledge.md` 使用 `reference-query` 复用固定来源的峰值、环境和单测参考；性能比较精确匹配 shape/dtype、软件、拓扑、单位、统计及方法版本，区分标称峰值和实测可达值。失配、过期或冲突时再核对当前来源/安排已授权实测；新的可复用结果用 `reference-record` 关联原始证据与经验 ID。历史参考不代替本轮 profiler-off 测量或阶段 loss，也不自动更新 HCU 大知识库。

若精确 reference 缺失或不适用，继续 `experience-search` 跨上下文查产品/架构、指标和测试类型，读导航记录及固定原文，再核对当前 HCU 知识库、官方文档或实现；不要把“没有合格 reference”理解为“没有可借鉴的原文”。导航的 summary/interpretation 要带来源关键词、版本、表格位置与缺失条件；只存 evidence 哈希不会使原文正文自动可搜。条件补齐后再 `reference-record`，原记录保持可追溯。

## 通信带宽预期与差距

先查相关模式的近期预期，再对照当前相同条件单测和模型内耗时。DeepEP 高吞吐关注 HT dispatch/combine 带宽，不以低延迟（LL）表或本次测量自身代替预期。记录后端、节点/rank、物理/逻辑网卡拓扑、shape/dtype、版本、XDP，以及字节/FLOPs、计时、同步和统计口径；API 延迟、kernel 延迟和 RDMA 带宽要分开。

若近期参考只有部分条件匹配，给出带明确差异和不确定性的工程比较，保留原文价值；只有单位和方法可比才计算绝对/相对差距，不虚构参数或设任意通过比例。随后针对可验证的原因安排有界实验，区分独立通信上限、模型内 contention、overlap 与通算融合收益；模型数据量必须追实际 dispatcher 输入，不能直接拿全模型 hidden size 代替。详细检索与记录方法见 `docs/experience-knowledge.md`。

## 优化与分路线交付的顺序

模型在现有用户 patch/donor/HCU 适配树跑通后，若主仓差异较大，仍在该树按原闭环完成 profile、原生调参、必要的系统/通信/算子优化和精度验证；快速线不会将这些环节降为可选。逐候选冻结来源、改动、测量与精度证据，保留初始基线，不因提前移植而打断关键实验。最终按项目[双线方法](../../../docs/practices/engine-delivery-tracks.md)交付：快速线整理固定 commit 的模型 example/patch 并验证重放，稳定线维护发布配方。只有约定了主仓整合时才移植与验证；该项延期则仍保留待办，不能把它强加给仅要求快速方案的任务，也不能以旧版本证据替代新整合验证。
