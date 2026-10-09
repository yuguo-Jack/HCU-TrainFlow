---
id: official-source-catalog
title: 官方源码 文档 PR 覆盖与更新索引
kind: source-map
engine: cross-engine
review_level: inventory-only
runtime_validated: false
sources: []
generated_body_sha256: 9d660deb0a33c9e43dcb96748094078ddbdbd8582f088f9e2b4913bcd3a59b98
---

# 官方来源覆盖目录

此页由来源目录和已保留页面重建。完整路径、文档采集和内容精读是不同覆盖层；没有逐模型或硬件验证的隐含承诺。

## amd-agi-primus

来源：AMD-AGI/Primus

- [源码目录](../source-maps/amd-agi-primus.md)：3033 路径，固定 `9b0ce906466cdf4d795597317a79cb368725ff1c`，目录覆盖。

## amd-agi-tracelens

来源：AMD-AGI/TraceLens

- [源码目录](../source-maps/amd-agi-tracelens.md)：1350 路径，固定 `c5da90ee7d59e49bf75e8602f0211da1f6dcd8b3`，目录覆盖。

## ascend-mindspeed

来源：Ascend/MindSpeed

- [源码目录](../source-maps/ascend-mindspeed.md)：1979 路径，固定 `485d1077017a39963de83944230cfab26a6ec467`，目录覆盖。

## ascend-mindspeed-llm

来源：Ascend/MindSpeed-LLM

- [源码目录](../source-maps/ascend-mindspeed-llm.md)：2310 路径，固定 `bc4e91cc6d344937df4d2f36f6ac26828051482c`，目录覆盖。

## bbuf-ai-infra-auto-driven-skills

来源：BBuf/AI-Infra-Auto-Driven-SKILLS

- [源码目录](../source-maps/bbuf-ai-infra-auto-driven-skills.md)：627 路径，固定 `6dc9c66a008daded66f214022919ff88b2186252`，目录覆盖。

## hygon-ai-cluster-manager-das

来源：HYGON-AI/cluster-manager-das

- [源码目录](../source-maps/hygon-ai-cluster-manager-das.md)：375 路径，固定 `026452b298814065b317273c28cc6d707567c20c`，目录覆盖。

## nvidia-megatron-energon

来源：NVIDIA/Megatron-Energon

- [源码目录](../source-maps/nvidia-megatron-energon.md)：274 路径，固定 `d8dba7f399dcf4dcf4e42b7f8412a9ad9abe463b`，目录覆盖。
- [文档目录](../upstream-docs/nvidia-megatron-energon/)：扫描发现 32 份；保留 32 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- [PR #301：Keep datasets usable after closing a loader](../prs/NVIDIA--Megatron-Energon/PR-301.md)

## nvidia-megatron-lm

来源：NVIDIA/Megatron-LM

- [源码目录](../source-maps/nvidia-megatron-lm.md)：4156 路径，固定 `ab1a28486b92adb3702f1289ff3a332cdb74294f`，目录覆盖。
- [文档目录](../upstream-docs/nvidia-megatron-lm/)：扫描发现 43 份；保留 43 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- [PR #6878：Mxfp8 refit bounded memory](../prs/NVIDIA--Megatron-LM/PR-6878.md)
- [PR #7534：[dev] docs: add combined 1F1B MoE A2A overlap guide](../prs/NVIDIA--Megatron-LM/PR-7534.md)
- [PR #7897：Widen paged-stash copy/pop kernel launches](../prs/NVIDIA--Megatron-LM/PR-7897.md)
- [PR #7942：Declare the residual on the pre-MLP norm of the fused MLA spec](../prs/NVIDIA--Megatron-LM/PR-7942.md)

## nvidia-transformerengine

来源：NVIDIA/TransformerEngine

- [源码目录](../source-maps/nvidia-transformerengine.md)：1332 路径，固定 `39c30c577f5dd4f9fba921ee011b5cd797ae667e`，目录覆盖。
- [文档目录](../upstream-docs/nvidia-transformerengine/)：扫描发现 15 份；保留 15 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- [PR #3517：[PyTorch] Support distributed weights in GroupedLinear's grouped-tensor path](../prs/NVIDIA--TransformerEngine/PR-3517.md)
- [PR #3546：[PyTorch] Enable LayerNormLinear UB AG overlap under no_grad](../prs/NVIDIA--TransformerEngine/PR-3546.md)

## nvidia-nemo-megatron-bridge

来源：NVIDIA-NeMo/Megatron-Bridge

- [源码目录](../source-maps/nvidia-nemo-megatron-bridge.md)：3703 路径，固定 `34ddd53b0e023d93f107f29b7dc61f9c5dd76a57`，目录覆盖。
- [文档目录](../upstream-docs/nvidia-nemo-megatron-bridge/)：扫描发现 36 份；保留 36 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- [PR #6140：Fix(qwen3vl): finalize TE precision after decoder replacement](../prs/NVIDIA-NeMo--Megatron-Bridge/PR-6140.md)
- [PR #6343：fix(ckpt): preserve NemotronH checkpoint embedding keys](../prs/NVIDIA-NeMo--Megatron-Bridge/PR-6343.md)

## thudm-slime

来源：THUDM/slime

- [源码目录](../source-maps/thudm-slime.md)：775 路径，固定 `0b0c277d5b4cc66efc3b6db269e2e5184e8f3b1e`，目录覆盖。
- [文档目录](../upstream-docs/thudm-slime/)：扫描发现 22 份；保留 22 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- [PR #2442：fix(weight-sync): honor checkpoint shard indexes in disk delta sync](../prs/THUDM--slime/PR-2442.md)
- [PR #2444：Support manual Megatron restarts with retained serving](../prs/THUDM--slime/PR-2444.md)

## baidu-baige-loongforge

来源：baidu-baige/LoongForge

- [源码目录](../source-maps/baidu-baige-loongforge.md)：2666 路径，固定 `f65a7caf88fca602a46c0e48b1f56dbcb295bc3f`，目录覆盖。

## deepspeedai-deepspeed

来源：deepspeedai/DeepSpeed

- [源码目录](../source-maps/deepspeedai-deepspeed.md)：2422 路径，固定 `bc1ad320a9afb516797577924a9983c6d7cd6793`，目录覆盖。
- [文档目录](../upstream-docs/deepspeedai-deepspeed/)：扫描发现 62 份；保留 62 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- [PR #8534：Deprecate loco zero++](../prs/deepspeedai--DeepSpeed/PR-8534.md)
- [PR #8632：Harden ZeRO-1/2 offload gradient storage lifetime and stream ordering](../prs/deepspeedai--DeepSpeed/PR-8632.md)

## hiyouga-llama-factory

来源：hiyouga/LlamaFactory

- [源码目录](../source-maps/hiyouga-llama-factory.md)：776 路径，固定 `ce9dc9e072f80fa3abe0989d4ab90da25f083438`，目录覆盖。
- [文档目录](../upstream-docs/hiyouga-llama-factory/)：扫描发现 3 份；保留 3 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- [PR #10762：[v1] Support multimodal Ulysses CP and memory-efficient chunk loss for SFT](../prs/hiyouga--LlamaFactory/PR-10762.md)

## inclusionai-areal

来源：areal-project/AReaL

- [源码目录](../source-maps/inclusionai-areal.md)：1689 路径，固定 `01de0a83e17cb12c918fc791466138ddbd4168c9`，目录覆盖。
- [文档目录](../upstream-docs/inclusionai-areal/)：扫描发现 29 份；保留 29 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- [PR #1679：fix(dataset): align VLM SFT loss masks with responses](../prs/areal-project--AReaL/PR-1679.md)
- [PR #1697：perf: reduce VLM CPU broadcast and microbatch memory overhead](../prs/areal-project--AReaL/PR-1697.md)

## modelscope-ms-swift

来源：modelscope/ms-swift

- [源码目录](../source-maps/modelscope-ms-swift.md)：1850 路径，固定 `22249748429ce7e8516640e35cbe997e572a233a`，目录覆盖。
- [文档目录](../upstream-docs/modelscope-ms-swift/)：扫描发现 14 份；保留 14 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- [PR #10188：docs: clarify configuration for fractional loss weights](../prs/modelscope--ms-swift/PR-10188.md)
- [PR #10242：[bugfix] drop dp_cp_group from content_metadata when saving mcore checkpoint](../prs/modelscope--ms-swift/PR-10242.md)

## sgl-project-sglang

来源：sgl-project/sglang

- [源码目录](../source-maps/sgl-project-sglang.md)：11888 路径，固定 `bd2d73daa5afda6bcad8d479a834f2e70bbe9569`，目录覆盖。
- [文档目录](../upstream-docs/sgl-project-sglang/)：扫描发现 62 份；保留 62 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- [PR #39265：[sglang-miles] Allocate packed weight receive buffers directly from metadata](../prs/sgl-project--sglang/PR-39265.md)

## vllm-project-vllm

来源：vllm-project/vllm

- [源码目录](../source-maps/vllm-project-vllm.md)：8654 路径，固定 `f0a5f111f205b5c73bb34fbd41f8f0d9936b543f`，目录覆盖。
- [文档目录](../upstream-docs/vllm-project-vllm/)：扫描发现 16 份；保留 16 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- [PR #59772：[CI] Fix ModelExpress handling in weight transfer tests](../prs/vllm-project--vllm/PR-59772.md)

## volcengine-verl

来源：verl-project/verl

- [源码目录](../source-maps/volcengine-verl.md)：1496 路径，固定 `5ab22f8a4989c438c1a0dbeca87ce1a00ef5436d`，目录覆盖。
- [文档目录](../upstream-docs/volcengine-verl/)：扫描发现 38 份；保留 38 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- [PR #7926：[trainer, rollout] fix: honor V1 standalone rollout memory budget](../prs/verl-project--verl/PR-7926.md)
- [PR #8064：[rollout, vllm] fix: drop tied-embedding alias in fp8 weight sync](../prs/verl-project--verl/PR-8064.md)

## yuguo-jack-hyperloom

来源：yuguo-Jack/Hyperloom

- [源码目录](../source-maps/yuguo-jack-hyperloom.md)：2399 路径，固定 `0425bde3f6e76e1588400c37d056dfd3bb75ac11`，目录覆盖。

## nvidia-cudnn-frontend

来源：NVIDIA/cudnn-frontend

- [源码目录](../source-maps/nvidia-cudnn-frontend.md)：2928 路径，固定 `51a3de73e122aeedafe68070acf3b7ff3970534e`，目录覆盖。
- [文档目录](../upstream-docs/nvidia-cudnn-frontend/)：扫描发现 16 份；保留 16 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- [PR #1373：Bind SM90 dense and packed half attention natively](../prs/NVIDIA--cudnn-frontend/PR-1373.md)
- [PR #1456：frost(compiled_cache): an in-process memo in front of the compiled-plan cache](../prs/NVIDIA--cudnn-frontend/PR-1456.md)

## nvidia-transformerengine-docs

来源：https://docs.nvidia.com/deeplearning/transformer-engine/


## nvidia-cudnn-frontend-docs

来源：https://docs.nvidia.com/deeplearning/cudnn/latest/


## hcu-tracelens

来源：yuguo-Jack/TraceLens

- [源码目录](../source-maps/hcu-tracelens.md)：1354 路径，固定 `e4e891de60d3ac3cff3046a58e5852d0814b3dc6`，目录覆盖。
