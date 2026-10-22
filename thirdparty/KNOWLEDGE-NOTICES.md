# 知识材料来源与许可声明

本页记录 TrainFlow 实际保留的第三方文档、PR 描述/讨论及相关声明的来源。材料仍归原作者或权利人所有，不随 TrainFlow 原创代码和说明改授 MIT；每篇页面保留原始 URL、提交或网页指纹。源码导航列出路径，不代表随仓复制了完整实现。

工程用途与联动范围见[第三方工程说明](../THIRD_PARTY_NOTICES.md)，依赖获取方式见[第三方安装说明](README.md)。只登记链接或调用外部工程，不因此重复收录其 Wiki 或复制整套许可证。

## 1. 来源快照与核对状态

**最近核对：2026-10-22。** 本次对照[本仓 `781f4370` 登记的来源](https://github.com/yuguo-Jack/HCU-TrainFlow/blob/781f4370ce2404286be17927ce827696a7ab2f6b/knowledge/sources.json)、源码树清单及依赖锁；这不是对所有上游最新 HEAD 的检查。

| 范围 | 核对结果与边界 |
| --- | --- |
| 21 个官方仓、27 份 LICENSE/NOTICE 副本 | 与上述登记快照的 Git blob 一致，比较时兼容 Windows 工作树换行；文件级、文档专用许可仍需按所用材料核对 |
| HCU TraceLens 的 LICENSE | 与依赖锁 `22786b16d429783927981bd592a47ad0f79db3ba` 中的 LICENSE 一致；它是工具依赖，不是第二套 HCU 项目 Wiki |
| Cluster Manager、Train Simulator 的 4 份声明 | 保留历史来源和集成归属；本次不宣称核对到这两个工程的最新版本 |
| 两项 NVIDIA 官网来源 | 已单列网页、声明入口和版本定位方式；不能用代码仓许可副本的一致性代替网页再分发范围的核对 |

下面的 **fixed original** 是许可副本的固定来源。许可内容未变时保留该链接，并单独更新核对记录；来源提交较早不等于副本内容已失效。当前来源登记见 [sources.json](../knowledge/sources.json)，树清单见 [catalog/repositories/](../knowledge/catalog/repositories/)，逐文件固定证据见 [source-lock.json](../knowledge/source-lock.json)。本表是有日期的核对结果，不自动随来源更新。

## 2. 官方仓材料的许可副本

文档目录、单个文件、代码片段或 PR 附件可能有各自的声明；下列根目录许可不覆盖一切材料。例如 Primus 的[文档许可页](https://github.com/AMD-AGI/Primus/blob/8e7a2406111e1c2c3d22112ddb3a1741c619b2ea/docs/license.md)、cuDNN Frontend 的 [LICENSING.md](https://github.com/NVIDIA/cudnn-frontend/blob/a7269d7607db343fb099dabf6d8fef47f4a2498c/LICENSING.md) 需要与实际使用内容一并阅读。

- [AMD-AGI/Primus / LICENSE](licenses/amd-agi-primus/LICENSE) · [fixed original](https://github.com/AMD-AGI/Primus/blob/ab8735564c4cc3bb7c0475146057eee8dae4c650/LICENSE)
- [AMD-AGI/TraceLens / LICENSE](licenses/amd-agi-tracelens/LICENSE) · [fixed original](https://github.com/AMD-AGI/TraceLens/blob/c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3/LICENSE)
- [Ascend/MindSpeed-LLM / LICENSE](licenses/ascend-mindspeed-llm/LICENSE) · [fixed original](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/LICENSE)
- [Ascend/MindSpeed-LLM / docs/LICENSE](licenses/ascend-mindspeed-llm/docs/LICENSE) · [fixed original](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/LICENSE)
- [Ascend/MindSpeed / LICENSE](licenses/ascend-mindspeed/LICENSE) · [fixed original](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/LICENSE)
- [Ascend/MindSpeed / docs/LICENSE](licenses/ascend-mindspeed/docs/LICENSE) · [fixed original](https://github.com/Ascend/MindSpeed/blob/241431d43e02a89556d2d2b3eacc7e24448adee5/docs/LICENSE)
- [baidu-baige/LoongForge / LICENSE](licenses/baidu-baige-loongforge/LICENSE) · [fixed original](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/LICENSE)
- [baidu-baige/Loong-Megatron / LICENSE](licenses/baidu-loong-megatron/LICENSE) · [fixed original](https://github.com/baidu-baige/Loong-Megatron/blob/64c279afb879229cff12fb293624e3691990403f/LICENSE)
- [deepspeedai/DeepSpeed / LICENSE](licenses/deepspeedai-deepspeed/LICENSE) · [fixed original](https://github.com/deepspeedai/DeepSpeed/blob/1c862f7df93f0345b977c67f5408d967b94bf4ae/LICENSE)
- [hiyouga/LlamaFactory / LICENSE](licenses/hiyouga-llama-factory/LICENSE) · [fixed original](https://github.com/hiyouga/LlamaFactory/blob/1fded918ac4723ac9966363f51ed4500866c5d1d/LICENSE)
- [areal-project/AReaL / LICENSE](licenses/inclusionai-areal/LICENSE) · [fixed original](https://github.com/areal-project/AReaL/blob/aedc21ec66ff03f329dcd4139945da8087e0d0e7/LICENSE)
- [modelscope/ms-swift / LICENSE](licenses/modelscope-ms-swift/LICENSE) · [fixed original](https://github.com/modelscope/ms-swift/blob/409170095f24b45b8945715341504d99b70a2bc0/LICENSE)
- [NVIDIA/cudnn-frontend / LICENSE-MIT.txt](licenses/nvidia-cudnn-frontend/LICENSE-MIT.txt) · [fixed original](https://github.com/NVIDIA/cudnn-frontend/blob/941078f2ce6aa0a45ac5813b81760a19c616732a/LICENSE-MIT.txt)
- [NVIDIA/cudnn-frontend / LICENSE.txt](licenses/nvidia-cudnn-frontend/LICENSE.txt) · [fixed original](https://github.com/NVIDIA/cudnn-frontend/blob/941078f2ce6aa0a45ac5813b81760a19c616732a/LICENSE.txt)
- [NVIDIA/cudnn-frontend / NOTICE](licenses/nvidia-cudnn-frontend/NOTICE) · [fixed original](https://github.com/NVIDIA/cudnn-frontend/blob/941078f2ce6aa0a45ac5813b81760a19c616732a/NOTICE)
- [NVIDIA/Megatron-Energon / LICENSE](licenses/nvidia-megatron-energon/LICENSE) · [fixed original](https://github.com/NVIDIA/Megatron-Energon/blob/accdabc3983843665a34cd1578c0e82d2403e3a9/LICENSE)
- [NVIDIA/Megatron-LM / LICENSE](licenses/nvidia-megatron-lm/LICENSE) · [fixed original](https://github.com/NVIDIA/Megatron-LM/blob/e30d863a6d82a3c45f2d71355dc73fbf5610967b/LICENSE)
- [NVIDIA-NeMo/Megatron-Bridge / LICENSE](licenses/nvidia-nemo-megatron-bridge/LICENSE) · [fixed original](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/53681c1aa264b54a1afa320830738382ee2a44f4/LICENSE)
- [NVIDIA/TransformerEngine / LICENSE](licenses/nvidia-transformerengine/LICENSE) · [fixed original](https://github.com/NVIDIA/TransformerEngine/blob/2e959f352c8e2d4b2709e6775867f2c7494656f3/LICENSE)
- [pytorch/torchtitan / LICENSE](licenses/pytorch-torchtitan/LICENSE) · [fixed original](https://github.com/pytorch/torchtitan/blob/b663c1673c00d97864bb32f18029ce5ec40442e2/LICENSE)
- [sgl-project/sglang / LICENSE](licenses/sgl-project-sglang/LICENSE) · [fixed original](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/LICENSE)
- [sgl-project/sglang / docs/LICENSE](licenses/sgl-project-sglang/docs/LICENSE) · [fixed original](https://github.com/sgl-project/sglang/blob/c6e822c29b9bb3d392e65a7bcb271a5d2d63613d/docs/LICENSE)
- [THUDM/slime / LICENSE](licenses/thudm-slime/LICENSE) · [fixed original](https://github.com/THUDM/slime/blob/05e3b017fed9e02de418c2fbac9d75602a534be5/LICENSE)
- [vllm-project/vllm / LICENSE](licenses/vllm-project-vllm/LICENSE) · [fixed original](https://github.com/vllm-project/vllm/blob/8d7b93fec2eb72ce01f2217472ac1f51b9bce600/LICENSE)
- [verl-project/verl / LICENSE](licenses/volcengine-verl/LICENSE) · [fixed original](https://github.com/verl-project/verl/blob/2035f58dcb06d8cad4caee107b30f4045d724367/LICENSE)
- [verl-project/verl / Notice.txt](licenses/volcengine-verl/Notice.txt) · [fixed original](https://github.com/verl-project/verl/blob/2035f58dcb06d8cad4caee107b30f4045d724367/Notice.txt)
- [yuguo-Jack/Hyperloom / LICENSE](licenses/yuguo-jack-hyperloom/LICENSE) · [fixed original](https://github.com/yuguo-Jack/Hyperloom/blob/0425bde3f6e76e1588400c37d056dfd3bb75ac11/LICENSE)

## 3. 官网教程与参考文档

官网资料按独立网页来源登记，保留具体 URL、观测信息及正文/原件指纹；网页的 `baseline_commit` 是内容指纹，不是代码仓 Git 提交。正文、示例代码和下载的软件按各自适用声明核对，不把产品代码的 Apache/MIT 许可直接套到整个网站。

| 登记来源 | 原始入口与声明 | 本仓阅读入口 |
| --- | --- | --- |
| `nvidia-transformerengine-docs` | [Transformer Engine 官网](https://docs.nvidia.com/deeplearning/transformer-engine/)；核对页面版权和其页脚链接的 [Terms of Service](https://www.nvidia.com/en-us/about-nvidia/terms-of-service/)，以及对应源码文档/示例的文件级许可 | [Transformer Engine Wiki](../knowledge/projects/transformer-engine/README.md) |
| `nvidia-cudnn-frontend-docs` | [cuDNN 官网](https://docs.nvidia.com/cudnn/)及 [Notices](https://docs.nvidia.com/cudnn/reference/notices/)；网页教程与 cudnn-frontend 仓库文件分别确认适用条件 | [cuDNN Frontend Wiki](../knowledge/projects/cudnn-frontend/README.md) |

当前已登记网页原文不等于已确认其全部再分发条件；本仓尚未登记逐页的授权适用核对结果。补充或更新官网原文前核对相应版本声明和允许保留的范围；无法确认时先保留链接与原创摘要，并明确待确认项。引用声明和保留来源本身不构成额外授权。

## 4. HCU 工具依赖与历史归属

HCU TraceLens 是当前集成依赖，其实际版本见 [manifest.json](manifest.json)。Cluster Manager、Train Simulator 的副本保留此前材料及仍在使用的集成说明的归属；HCU 仓库 Wiki 现由 HCU-Knowledge 维护，这些历史声明不表示 TrainFlow 继续采集它们的源码、文档或 PR。仅增加训练/推理/RL 仓库链接时更新[联动清单](../THIRD_PARTY_NOTICES.md#4-hcu-现场工具与工程联动)即可。

- [yuguo-Jack/TraceLens / LICENSE](licenses/hcu-tracelens/LICENSE) · [fixed original](https://github.com/yuguo-Jack/TraceLens/blob/30f5dcd539dd4e588678e34168c7fcf726dd987e/LICENSE)
- [HYGON-AI/cluster-manager-das / LICENSE](licenses/hygon-ai-cluster-manager-das/LICENSE) · [fixed original](https://github.com/HYGON-AI/cluster-manager-das/blob/438847c1877cdce17cb524cb8825d49bd6917d6a/LICENSE)
- [HYGON-AI/cluster-manager-das / NOTICE](licenses/hygon-ai-cluster-manager-das/NOTICE) · [fixed original](https://github.com/HYGON-AI/cluster-manager-das/blob/438847c1877cdce17cb524cb8825d49bd6917d6a/NOTICE)
- [HYGON-AI/hcu-train-simulator / LICENSE](licenses/hygon-ai-train-simulator/LICENSE) · [fixed original](https://github.com/HYGON-AI/hcu-train-simulator/blob/b7d8e6f3becebf5d09121bb1c582436a371c6710/LICENSE)
- [HYGON-AI/hcu-train-simulator / NOTICE](licenses/hygon-ai-train-simulator/NOTICE) · [fixed original](https://github.com/HYGON-AI/hcu-train-simulator/blob/b7d8e6f3becebf5d09121bb1c582436a371c6710/NOTICE)

## 5. 未观察到顶层许可的来源

[BBuf/AI-Infra-Auto-Driven-SKILLS](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/tree/e51089a7b5b25939d5ab6f2216df0ba07be30225) 在本次登记树中仍未发现顶层 LICENSE/NOTICE；[此前固定来源](https://github.com/BBuf/AI-Infra-Auto-Driven-SKILLS/tree/154cc565d0374746442bac17bd69368b888f4775) 同样如此。这是对具体清单的观察，不推断作者放弃权利或所有文件均无单独声明。保留归属不授予新的许可，扩大材料使用范围前须确认适用依据。

## 6. 后续维护规则

1. **核对实际来源与材料。** 新增来源、推进版本、改变保留范围或升级集成依赖时，检查 LICENSE、NOTICE、文档目录/文件专用声明，以及官网对应版本的声明。仅参考链接和保留原文分别处理。
2. **分开记录来源与复核。** 固定原件链接和副本来源保留；核对记录注明日期、对应源码/网页基线和结果。副本不变则记录比较依据，不能只改日期；声明变化时保留旧材料适用的原件，明确新材料的许可范围，不覆盖历史证据。
3. **明确未确认项。** 链接可访问、内容已抓取和允许再分发是不同状态。缺少适用依据时写清材料与缺口，新增内容先用链接和原创摘要，不把来源哈希校验通过记成授权核对通过。
4. **检查引用与发布。** 同步本页、第三方工程说明和受影响页面，保留署名及必要通知；检查本地链接、打包内容和来源证据。常规文档/知识校验不判断许可适用性。维护入口见 [Wiki 组织规范](../docs/wiki-authoring-standard.md)。
