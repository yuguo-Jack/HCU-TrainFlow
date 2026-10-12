---
id: engines/slime
title: Slime：Megatron–SGLang 闭环、数据并行与恢复工程指南
engine: slime
kind: authored
stages:
- adapt
- optimize
- fault-tolerance
visibility: public
review_level: selected-source-reading
runtime_validated: false
reviewed_on: '2026-10-12'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime
  execution
sources:
- source: thudm-slime
  path: README.md
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: f26cc2aec04657f27d2560bf576f357262f138f763561a911f818474ce11dd1f
- source: thudm-slime
  path: setup.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 3d6f0f81b68f4357388f499bf6b5d0e526d2892744e15ebced15a07400b501c2
- source: thudm-slime
  path: requirements.txt
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 01c4ef7d63459573a68fedc50a18a2d4a40618a5435a73638543ac7ec0b03eb3
- source: thudm-slime
  path: train.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 5dfcec6737e53d613e5db94fc20459dd6d58282d17f01bab410868251522fc9d
- source: thudm-slime
  path: slime/ray/rollout.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 70587fb942d26784290ef949b30045a7c292c53123307c96d80925901b5282c3
- source: thudm-slime
  path: slime/ray/actor_group.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: ded0c12645992c7ab5c7034a91b418f195a6109dda02c3af0d0548804f39340c
- source: thudm-slime
  path: slime/backends/megatron_utils/actor.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 66a159753c6c3e1c8509b781f301551caf0a27e2dfe5c810dea8003b75b3710d
- source: thudm-slime
  path: slime/backends/megatron_utils/arguments.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: aa9f5b7341d4d9f5554e7d376a6d916999e469bca7a7699f0d465e6290a2e2e9
- source: thudm-slime
  path: slime/backends/megatron_utils/data.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 581ed42c5bd2dcfe0af5b262cce8d5fee1719bf30da4ca3ec9bb1de73806abef
- source: thudm-slime
  path: slime/backends/megatron_utils/loss.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 65c68c20b2a967e4331ce918cb72910657e6caf977638f3afbc6791d2f06ae15
- source: thudm-slime
  path: slime/data/checkpoint.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 8511194a0f1b27705084a14974c5805e830ba2850900ef38ee02bcfd72082443
- source: thudm-slime
  path: slime/backends/megatron_utils/update_weight/update_weight_from_disk_delta.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: ac78a67f02d146331f377c9246b60109d039101b99b5d4058ad6932981411293
- source: thudm-slime
  path: docs/en/get_started/quick_start.md
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: ef7d054608be36ced9033189a1d9dc90cfa50475ef40b2599d07135157468497
- source: thudm-slime
  path: docs/en/get_started/usage.md
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 1305d31cb0489966b3f793630b7cbae72b50353ecede6c3a4100f211d186f044
- source: thudm-slime
  path: docs/en/advanced/parallelism-memory.md
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 6071c1eadf948dc39300e51300dd9dcae05830d58df3e2f44db5e60081893f82
- source: thudm-slime
  path: docs/en/advanced/policy-mismatch.md
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 5cee4b66dc494b1146a0bbc7b549e50037602972ef39b74feb40a97f05501f74
- source: thudm-slime
  path: docs/en/advanced/delta-weight-sync.md
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 2c0f424890480c6d8465e3f0455542c2adc8495de0d7bad311149b0b342c9966
- source: thudm-slime
  path: docs/en/advanced/fault-tolerance.md
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 1f120c4b4cd11d830dff3b0d4e50d676a293821a00f0370868a5cdedbc2e72ae
- source: thudm-slime
  path: docs/en/advanced/observability.md
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 32da138c5ee1e9ef3ef642465a23896d349c885b5bb7cf0bacee8ee12a982f8b
- source: thudm-slime
  path: tests/test_policy_loss.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 328ad469218438ebc83785eafc78708b958a7658d4fbaa2655f59934bade1481
- source: thudm-slime
  path: tests/test_disk_delta_recovery.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: 0d0753a32ba90f91dc51871f7c62ca474f99ad1a13385dcf94ac8f0e4c56c125
- source: thudm-slime
  path: tests/test_training_recovery.py
  commit: 05e3b017fed9e02de418c2fbac9d75602a534be5
  sha256: dd7782502cb1f27adedc2f2b287a7fe70fff2035d4c3a08b85244bd3372fc770
---

# Slime：Megatron–SGLang 闭环、数据并行与恢复工程指南

## 1. 定位和上游/HCU边界

Slime 连接 Megatron 训练、SGLang 生成、reward/data 插件和 Ray 资源调度，支持同步、异步数据生产以及训练/推理分离。其 RL 迭代由策略训练、权重发布、服务和数据进度共同决定；这些不是独立包导入即可完成的功能。

本页精读官方 main 固定提交，`setup.py` 版本为0.4.0。HCU公开/内部维护线可能采用不同 Megatron/SGLang patch 与模型插件，包版本也可能落后于分支名。先用 HCU-Knowledge 选活跃 HCU 维护线并锁 SHA；官方 main 的新恢复/权重能力不能直接当成该线已支持。

## 2. 工程组织与源码入口

| 位置 | 职责、下一层 |
| --- | --- |
| [`train.py`](https://github.com/THUDM/slime/blob/05e3b017fed9e02de418c2fbac9d75602a534be5/train.py) | 本次训练attempt生命周期、rollout/训练、save、权重更新与eval |
| `slime/ray/placement_group.py`、`actor_group.py` | Ray资源、训练actor创建、RPC分发与等待 |
| `slime/ray/rollout.py` | RolloutManager；生成/数据转换/训练分片、健康及恢复衔接 |
| `slime/backends/megatron_utils/actor.py` | MegatronTrainRayActor、model/ref/critic、训练与状态装卸 |
| `megatron_utils/data.py`、`cp_utils.py`、`loss.py` | packed token/CP切分、logprob/advantage/PPO/SFT loss |
| `megatron_utils/update_weight/` | tensor/distributed/disk/delta等发布协议与版本 |
| `slime/backends/sglang_utils/` | engine/group、服务调用、暂停与缓存、权重接收 |
| `slime/data/checkpoint.py`、`slime/data/` | 联合model/data checkpoint与可恢复进度，不只一份权重文件 |
| `slime/rollout/`、`slime_plugins/` | 生成策略、fully-async、reward/模型/任务插件 |
| `scripts/`、`docker/`、`patch/` | 模型配方、匹配镜像/源码pin、底层patch |
| `tests/`、`docs/en/advanced/` | CPU/设备/恢复测试和并行、调度、观测教程 |

## 3. 安装与依赖栈

[Quick Start](https://github.com/THUDM/slime/blob/05e3b017fed9e02de418c2fbac9d75602a534be5/docs/en/get_started/quick_start.md)提供已匹配Megatron/SGLang/TE的NVIDIA镜像和源码pin路线，AMD另有平台指南；不能直接把 `--gpus all`、CUDA镜像或 `/root`构建脚本用于HCU。使用HCU已匹配镜像及仓内HCU入口，写入/安装保持任务映射目录边界。

在已有兼容软件栈中，官方使用 `python -m pip install -e . --no-deps` 保留镜像依赖；先检查 `import slime, sglang, megatron.core` 的实际路径及设备。`requirements.txt`含直接依赖、straw queue、checksum/compression等，但不独立构建全部GPU栈。记录Megatron/Bridge、SGLang及patch、Torch/DTK、TE/attention/MoE库完整版本；同样的Slime pip版本不能证明它们相同。

`setup.py`将wheel标为当前CPythonABI及Linux平台，不能视为任意Python平台通用纯Python包。多机Ray的worker也需要同样依赖、共享路径及环境，不以driver可导入作为成功判据。

## 4. 配方、启动与验证

从 `scripts/run-<model>.sh` 或官方交互lab生成的 `experiment.sh` 读参数，然后进入 `train.py`。Megatron模型配置、HF checkpoint转换、rollout后端的model/采样/并行、reward与数据字段必须成套核对。超大模型仅缩layer时保留结构参数与optimizer；裁剪功能验证不等于完整模型性能结果。

先验证模型转换/单次logprob/forward-backward，再验证生成→reward→train→update_weights闭环和checkpoint恢复。调试支持debug-rollout-only/debug-train-only，以及固定rollout dump用于隔离训练问题；不要默认清掉保留Ray/SGLang资源再启动恢复任务。

上游 `tests/test_policy_loss.py` 是CPU clipping及调用参数检查；CP/恢复测试有不同fixture/资源。真正训练须验证角色资源、多个microbatch、梯度和阶段reward/loss，保存运行日志及真实Python退出码。本轮只有源码和测试内容阅读。

## 5. 数据和数值契约

rollout不只是一条字符串：tokens、response/total lengths、loss masks、行为logprob、reward、group和版本是训练接口。Megatron HF转换后的命名/vocab padding、MoE expert布局与SGLang参数也要匹配。

`loss_type`选择policy/value/SFT/custom路径，优势估计、KL、entropy、importance sampling和sample/token平均属于算法语义。减少old logprob前向、换采样temperature、过滤response或改mask都需要数值验证，不归类为无风险系统调参。CP packed token的切分必须与后端attention一致；同名CP开关不是同一种layout。

## 6. 当前训练控制链

`create_rollout_manager`确定资源/恢复计划 → `create_training_models`加载状态 → 初次推权重 → `training_ready`才恢复生产 → `generate` → 可选rollout offload → actor/critic train → `training_completed`释放队列容量 → 必要时联合save → training状态清理 → 暂停新rollout admission → update_weights → 后续恢复admission/KV → eval。

actor是否在critic-onlywarmup中更新、训练offload/release、eval与save间隔分别判断。**training_completed不是持久化提交**，只有jointcheckpoint成功才允许推进可恢复边界。最后一步不再启动无消费者的新生成。

## 7. 性能与显存两个专题

- [packed/CP、PPO loss与有效分母](../topics/packed-cp-and-policy-loss.md)：token切分、无lossrank的autograd路径、sample/token目标及局部回归。
- [disk delta发布与训练恢复边界](../topics/delta-publication-and-recovery.md)：新fullbaseline、版本/checksum、服务保留、jointcheckpoint与调度器职责。

[并行/显存教程](https://github.com/THUDM/slime/blob/05e3b017fed9e02de418c2fbac9d75602a534be5/docs/en/advanced/parallelism-memory.md)解释TP/PP/CP/EP和distributedoptimizer/offload/recompute。MoE容量用总参数，不能用active参数算权重存储；EP不是在dense TP×PP×CP×DP身份外再乘一遍。Adam示例18byte/parameter只是特定精度的状态账本，activation、通信buffer、refcopy、KV和转换峰值另算。

profile分别看训练forward/backward、rolloutprefill/decode、reward、同步、hostcompression/copy、保存/队列等待。[观测文档](https://github.com/THUDM/slime/blob/05e3b017fed9e02de418c2fbac9d75602a534be5/docs/en/advanced/observability.md)给出metrics/trace入口，指标不能代替kernel上限或数值证据。模型recipe的卡数/并行只是起点，不是实测最低显存或HCU最优组合。

## 8. 故障、精度和续训

| 现象 | 优先证据 |
| --- | --- |
| loss随CP/microbatch变 | packed位置/response mask、实际step sample/token分母、MCore归约缩放 |
| rollout和actor概率差 | 相同参数版本、tokenizer、temperature、attention、量化与policy-mismatch配置 |
| delta后输出异常 | sender snapshot、base/targetversion、全hostchecksum、GPUreload和cache状态 |
| GPU空闲却无batch | admission/backpressure、有效样本接受、reward异常、队列及训练消费 |
| 模型保存后仍重复训练 | jointcommit、model/optimizer/RNG、数据receipts/进度；完成一次train并不持久化 |
| 重启找不到serving | Ray仍存活、sessionidentity、namedactor与原配置兼容性 |

[当前官方容错](https://github.com/THUDM/slime/blob/05e3b017fed9e02de418c2fbac9d75602a534be5/docs/en/advanced/fault-tolerance.md)保留serving/rollout数据以便**重新提交**训练，并在下次权重更新前处理failedengines；不自动重试训练job，也不接管scheduler/node故障。Ray或ServingCluster丢失要重建服务并从checkpoint恢复，不能承诺所有在途token逐位续接。

## 9. 文档、PR和持续维护

[官方文档](https://thudm.github.io/slime/) · [Releases](https://github.com/THUDM/slime/releases) · [PR](https://github.com/THUDM/slime/pulls) · [fixed source map](../../upstream/source-map/thudm-slime.md) · [已保留原文](../../upstream/docs/thudm-slime)。版本发布、main新能力、HCU适配和任务实测分开；README/PR中的计划不是已实现能力。

相关已收录 PR：[disk delta shard index #2442](../../upstream/prs/THUDM--slime/PR-2442.md)、[保留 serving 的 Megatron 重启 #2444](../../upstream/prs/THUDM--slime/PR-2444.md)。配合版本发布/恢复专题阅读最终实现，并回到 PR 来源查看描述与 review；保留服务不能代替自动故障接管。

在线检索如 `wiki-search-pr "delta restart baseline" --engine slime`，取正文/review/最终代码/测试。更新loss、packing/CP、train loop、data commit或weightsync后同时修订本页、两专题、案例和消费者。当前未全面精读每个模型插件、全部reward/异步组合和所有SGLang接收端实现，也未在HCU训练或故障注入。
