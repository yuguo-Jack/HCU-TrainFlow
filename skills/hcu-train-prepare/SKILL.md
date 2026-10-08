---
name: hcu-train-prepare
description: 检查 HCU 训练环境或将预训练、SFT、RL 模型适配跑通；支持仅环境检查，建立拓扑、源快照及正确性基线。
---

# HCU 训练环境与模型适配

支持 `environment` 单独验收或 `adapt/full` 推进模型。先确定模式，环境检查任务交付检查结果后即可结束，不强行开始训练。

## 工作步骤

1. **接受任务与权限。** 记录模型、训练类型、资源、运行方式、数据/权重位置、已有 patch、预算、预期和可执行范围；缺失关键项及时询问，其他阅读与命令发现可继续。
2. **发现真实环境。** 读取已有镜像/脚本、当前工具源码与 `--help`。优先 Cluster Manager 对应子工程、run_nhc/check 脚本和 DTK 工具；按裸机/Conda、SSH+Docker、Slurm、K8s 区分。工具不存在或权限不足登记缺口，不能假定通过。
3. **建立验收矩阵。** 覆盖全部分配节点/设备的健康、GEMM、HBM、机内互联，以及适用 NIC/拓扑的机间通信与 RCCL 正确性。预期必须有硬件/同环境测量/用户资料依据，dtype、shape、单位和消息量可比。被动检查和主动压测分开；主动操作只在任务授权资源内执行。
4. **选择源仓与分支。** 公开 HYGON 与内部仓等价时优先公开；公开明显落后则参考真实活跃内部实现。比较关键文件/功能与依赖，不仅看默认分支或最新提交时间。保留用户 patch；开发 checkout 不得借用 HCU-Knowledge 缓存。锁官方、HCU、底层库和 submodule 提交。
5. **按官方配方跑通。** Megatron 优先参见 official-megatron-wiki；SFT/RL 读对应引擎入口。大模型可仅缩 num_layers，其他模型语义保留。`proxy-check` 记录差异，完整模型仍需后续验收。
6. **建立基线。** 对齐 tokenizer/数据顺序/mask/精度/参数更新。存在 NV 环境则做匹配对照；没有也要保守参考与局部正确性，不阻塞所有后续探索。空跑、required skip、fallback 或候选未分发不能通过。

## 交付

输出环境覆盖表（pass/fail/incomplete）、差异与缺权限项、源/依赖锁、可重复启动和单测命令、基线快照、数值契约及已知风险。用 `environment-check` 评估契约；留存证据后 `report-add`。纯环境模式允许交付不通过的诊断结果，但必须明确其不允许训练放行。

详见 references/workflow.md；安装/命令变化时复核当前工程，禁止把示例节点或旧参数变成默认值。

## 运行约定

先定位 HCU-TrainFlow checkout（用户给定路径或 `TRAINFLOW_PROJECT`）和私有 `TRAINFLOW_WORKSPACE`。不要把 site、数据、模型、日志或凭据写进公共仓。CLI 用 `hcu-trainflow --workspace <private-path>`；源码环境可用 `python -m hcu_trainflow`。先读项目 `docs/quickstart.md` 和当前任务上下文，再按需读相关章节。

主 Agent 在本地主控，专家分工记录 owner、scope、允许修改路径、预算与验收证据。运行代码使用独立开发 checkout 和不可变源快照；远端只执行明确命令/守护，不要求部署模型 Agent。TaskSpec 的 execute/sync/notify 权限是任务约定，不是 OS 安全沙箱。实际节点、容器、Pod UID、Slurm allocation 由部署任务确认。

需要 HCU 事实、历史案例或底层实现时使用可用的 `$hcu-knowledge-search`；也可以读当前对应分支源码和公开官方文档。知识检索不自动更新 HCU 大知识库。本工作流只维护自己的局部官方 Wiki；具体依赖命令升级时同步复核 Skill/适配器，不能仅改 Wiki。

产物归属本 Skill：按目标仓规范准备集中、通用的改动、测试、PR 说明和回退方式。公开 PR/Cookbook 只含脱敏的可公开方法与必要代码，不上传任务数据。遵循当前会话已给出的提交/发布授权。
