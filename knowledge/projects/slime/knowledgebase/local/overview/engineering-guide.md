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
reviewed_on: '2026-10-20'
coverage: selected mechanisms, recipes and tests at pinned official source; not every model/backend and no HCU runtime execution
sources:
- source: thudm-slime
  path: README.md
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: a564ad953d0961bd3d2f1343c74825dd900b2c1bf4a2b5471b9b7badc5d7b4d3
- source: thudm-slime
  path: setup.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 3d6f0f81b68f4357388f499bf6b5d0e526d2892744e15ebced15a07400b501c2
- source: thudm-slime
  path: requirements.txt
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 44209321a1ff53467a850f6318626c925d7b5677fcba2a6338d8bfba85c342fa
- source: thudm-slime
  path: train.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 9ab1d9a987182dc5ae57d19ca82a3807fd18adee8cecf0afe118cadbd8939939
- source: thudm-slime
  path: slime/ray/rollout.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 4b2cc58e04e583d5fd3d34d3a6f2ffbed79f37e52fefceaef95e63b8aa666304
- source: thudm-slime
  path: slime/ray/actor_group.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: ded0c12645992c7ab5c7034a91b418f195a6109dda02c3af0d0548804f39340c
- source: thudm-slime
  path: slime/backends/megatron_utils/actor.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 9f0e0cd3119c8354cd76c1972c908143b7f933b2653a1f53a2a898b1f8b13739
- source: thudm-slime
  path: slime/backends/megatron_utils/arguments.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 20bc1b4278c0eaa051a877a8e5482f9671490d417c37a6b22375c5bbfef82dee
- source: thudm-slime
  path: slime/backends/megatron_utils/data.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: b01a78b17b7d9ed93666982af378b6d2d74951473cad85f432e44d4cb8f926c8
- source: thudm-slime
  path: slime/backends/megatron_utils/loss.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 92ca932bd18019d5899272da1ae65da4a9f8172c4dbdeecbf6897b1f62d7e754
- source: thudm-slime
  path: slime/data/checkpoint.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 98e0b5724e59ee2e6f9df3459f4d598cc987a2e060f2de372abe15d92166adb7
- source: thudm-slime
  path: slime/backends/megatron_utils/update_weight/update_weight_from_disk_delta.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: ac78a67f02d146331f377c9246b60109d039101b99b5d4058ad6932981411293
- source: thudm-slime
  path: docs/en/get_started/quick_start.md
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 63be929c874a50862172c7fe923d122b4211a8d73592ad25ca1fb47ddb0e8b69
- source: thudm-slime
  path: docs/en/get_started/usage.md
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 47a3a0cc04d9e575a9379024e75e9d75e5a0c69eb19e134a59d98e7c4ca76d86
- source: thudm-slime
  path: docs/en/advanced/parallelism-memory.md
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 3f797e9973ec95f8a8f9a119eeb0b14aff6eff32129988bc950493efe49f8bed
- source: thudm-slime
  path: docs/en/advanced/policy-mismatch.md
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 5cee4b66dc494b1146a0bbc7b549e50037602972ef39b74feb40a97f05501f74
- source: thudm-slime
  path: docs/en/advanced/delta-weight-sync.md
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 2c0f424890480c6d8465e3f0455542c2adc8495de0d7bad311149b0b342c9966
- source: thudm-slime
  path: docs/en/advanced/fault-tolerance.md
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 1f120c4b4cd11d830dff3b0d4e50d676a293821a00f0370868a5cdedbc2e72ae
- source: thudm-slime
  path: docs/en/advanced/observability.md
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 32da138c5ee1e9ef3ef642465a23896d349c885b5bb7cf0bacee8ee12a982f8b
- source: thudm-slime
  path: tests/test_policy_loss.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 120c60a9e284b691dab54be58027eb67ae534d1e39cf416f4a2555a14834c589
- source: thudm-slime
  path: tests/test_disk_delta_recovery.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 0d0753a32ba90f91dc51871f7c62ca474f99ad1a13385dcf94ac8f0e4c56c125
- source: thudm-slime
  path: tests/test_training_recovery.py
  commit: a4202e0595467d9374d9a68d45a34f45c3f8d230
  sha256: 84797613939502cca123d0903761f8e3ae19f350ae1aaf5f18bddaaeefc8c7b9
---

# Slime：Megatron–SGLang 闭环、数据并行与恢复工程指南

## 1. 定位和上游/HCU边界

Slime 连接 Megatron 训练、SGLang 生成、reward/data 插件和 Ray 资源调度，支持同步、异步数据生产以及训练/推理分离。其 RL 迭代由策略训练、权重发布、服务和数据进度共同决定；这些不是独立包导入即可完成的功能。

本页精读官方 main 固定提交，`setup.py` 版本为0.4.0。HCU公开/内部维护线可能采用不同 Megatron/SGLang patch 与模型插件，包版本也可能落后于分支名。先用 HCU-Knowledge 选活跃 HCU 维护线并锁 SHA；官方 main 的新恢复/权重能力不能直接当成该线已支持。

## 2. 工程组织与源码入口

| 位置 | 职责、下一层 |
| --- | --- |
| [`train.py`](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/train.py) | 本次训练attempt生命周期、rollout/训练、save、权重更新与eval |
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

[Quick Start](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/get_started/quick_start.md)提供已匹配Megatron/SGLang/TE的NVIDIA镜像和源码pin路线，AMD另有平台指南；不能直接把 `--gpus all`、CUDA镜像或 `/root`构建脚本用于HCU。使用HCU已匹配镜像及仓内HCU入口，写入/安装保持任务映射目录边界。

在已有兼容软件栈中，官方使用 `python -m pip install -e . --no-deps` 保留镜像依赖；先检查 `import slime, sglang, megatron.core` 的实际路径及设备。`requirements.txt`含直接依赖、straw queue、checksum/compression等，但不独立构建全部GPU栈。记录Megatron/Bridge、SGLang及patch、Torch/DTK、TE/attention/MoE库完整版本；同样的Slime pip版本不能证明它们相同。

`setup.py`将wheel标为当前CPythonABI及Linux平台，不能视为任意Python平台通用纯Python包。多机Ray的worker也需要同样依赖、共享路径及环境，不以driver可导入作为成功判据。

当前 SGLang adapter 同时识别旧 `ServerArgs` dataclass 与新 msgspec Struct，并按真实字段映射部分 graph/DSA 配置名；旧参数别名兼容不是所有 SGLang 版本可混装的证明。独立 `sglang_python_executable` 路径还要求服务子进程与父进程分别核对版本、环境和健康状态。新的运行环境准备保留 host allocation 等有效设置，不能照旧把整个 allocator 配置无差别删掉。

本轮模型配方已扩大长响应预算并新增 GLM5-next 的 allgather-CP 白名单；它们仍是官方配置起点，不是 HCU 容量或精度实测。按实际 response+prompt 总长度核对 KV、CP、activation 和 logprob workspace，不把文档示例卡数或默认128K当任务必需值。

## 4. 配方、启动与验证

从 `scripts/run-<model>.sh` 或官方交互lab生成的 `experiment.sh` 读参数，然后进入 `train.py`。Megatron模型配置、HF checkpoint转换、rollout后端的model/采样/并行、reward与数据字段必须成套核对。先评估完整模型容量、健康设备与最坏 rank 余量，完整配置可行就保留；确需缩 layer 定位时保留其余结构参数与 optimizer，并标明裁剪功能验证不等于完整模型性能结果。

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

[并行/显存教程](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/parallelism-memory.md)解释TP/PP/CP/EP和distributedoptimizer/offload/recompute。MoE容量用总参数，不能用active参数算权重存储；EP不是在dense TP×PP×CP×DP身份外再乘一遍。Adam示例18byte/parameter只是特定精度的状态账本，activation、通信buffer、refcopy、KV和转换峰值另算。

profile分别看训练forward/backward、rolloutprefill/decode、reward、同步、hostcompression/copy、保存/队列等待。[观测文档](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/observability.md)给出metrics/trace入口，指标不能代替kernel上限或数值证据。模型recipe的卡数/并行只是起点，不是实测最低显存或HCU最优组合。

本轮恢复采用原 save 目录内的 rewind/session 协议；旧 branches/current 指针说明不再代表当前写入路径。缺少可用 rollout 快照时可能以 empty queue 恢复模型，并告警数据重放边界，见[联合恢复专题](../topics/delta-publication-and-recovery.md)。日志中“加载成功”必须分别解释模型状态、样本流和 retained serving。

Logprob/entropy chunking 当前通过单一 autograd 节点在 backward 重算，减少保留 full-vocabulary softmax 和重复 full-logits 梯度分配；CPU offsets、合并 response gather 和留在设备端的日志标量也减少同步，详见[CP/loss 专题](../topics/packed-cp-and-policy-loss.md)。这些机制保留完整 logits/梯度与通信成本，不能只按 chunk 大小估计整步峰值。

## 8. 故障、精度和续训

| 现象 | 优先证据 |
| --- | --- |
| loss随CP/microbatch变 | packed位置/response mask、实际step sample/token分母、MCore归约缩放 |
| rollout和actor概率差 | 相同参数版本、tokenizer、temperature、attention、量化与policy-mismatch配置 |
| delta后输出异常 | sender snapshot、base/targetversion、全hostchecksum、GPUreload和cache状态 |
| GPU空闲却无batch | admission/backpressure、有效样本接受、reward异常、队列及训练消费 |
| 模型保存后仍重复训练 | jointcommit、model/optimizer/RNG、数据receipts/进度；完成一次train并不持久化 |
| 重启找不到serving | Ray仍存活、sessionidentity、namedactor与原配置兼容性 |

[当前官方容错](https://github.com/THUDM/slime/blob/a4202e0595467d9374d9a68d45a34f45c3f8d230/docs/en/advanced/fault-tolerance.md)保留serving/rollout数据以便**重新提交**训练，并在下次权重更新前处理failedengines；不自动重试训练job，也不接管scheduler/node故障。Ray或ServingCluster丢失要重建服务并从checkpoint恢复，不能承诺所有在途token逐位续接。

## 9. 文档、PR和持续维护

[官方文档](https://thudm.github.io/slime/) · [Releases](https://github.com/THUDM/slime/releases) · [PR](https://github.com/THUDM/slime/pulls) · [fixed source map](../../upstream/source-map/thudm-slime.md) · [已保留原文](../../upstream/docs/thudm-slime)。版本发布、main新能力、HCU适配和任务实测分开；README/PR中的计划不是已实现能力。

相关已收录 PR：[disk delta shard index #2442](../../upstream/prs/THUDM--slime/PR-2442.md)、[保留 serving 的 Megatron 重启 #2444](../../upstream/prs/THUDM--slime/PR-2444.md)。配合版本发布/恢复专题阅读最终实现，并回到 PR 来源查看描述与 review；保留服务不能代替自动故障接管。

在线检索如 `wiki-search-pr "delta restart baseline" --engine slime`，取正文/review/最终代码/测试。更新loss、packing/CP、train loop、data commit或weightsync后同时修订本页、两专题、案例和消费者。当前未全面精读每个模型插件、全部reward/异步组合和所有SGLang接收端实现，也未在HCU训练或故障注入。
