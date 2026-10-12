---
id: official-source-catalog
title: 官方源码 文档 PR 覆盖与更新索引
kind: source-map
engine: cross-engine
review_level: inventory-only
runtime_validated: false
sources: []
generated_body_sha256: 78c5da53c648b06196efa374e37f9b31d3ce2feebadd5b76409d38125383408c
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

文档收录范围：训练引擎、并行与ZeRO、offload、数值、性能、显存、恢复及相关运行接口；通用机制和必要示例保留，基础应用/云平台入门按问题另查。

- [源码目录](../source-maps/deepspeedai-deepspeed.md)：2422 路径，固定 `bc1ad320a9afb516797577924a9983c6d7cd6793`，目录覆盖。
- [文档目录](../upstream-docs/deepspeedai-deepspeed/)：扫描发现 59 份；保留 59 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- 按已复核范围排除 3 份文档；规则与理由见 sources.json 的 document_exclusions。排除不代表上游删除，仍可按固定源码路径查阅。
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

文档收录范围：RL rollout配套推理、权重同步、显存生命周期、并行/通信、Graph与编译、性能诊断和部署；前端语言入门不默认收录。

- [源码目录](../source-maps/sgl-project-sglang.md)：11888 路径，固定 `bd2d73daa5afda6bcad8d479a834f2e70bbe9569`，目录覆盖。
- [文档目录](../upstream-docs/sgl-project-sglang/)：扫描发现 59 份；保留 59 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- 按已复核范围排除 3 份文档；规则与理由见 sources.json 的 document_exclusions。排除不代表上游删除，仍可按固定源码路径查阅。
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

- [源码目录](../source-maps/hcu-tracelens.md)：1376 路径，固定 `30f5dcd539dd4e588678e34168c7fcf726dd987e`，目录覆盖。
- [文档目录](../upstream-docs/hcu-tracelens/)：扫描发现 5 份；保留 5 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。

## hygon-ai-train-simulator

来源：HYGON-AI/hcu-train-simulator


## pytorch-torchtitan

来源：pytorch/torchtitan

文档收录范围：Official pretraining/SFT/RL recipes, architecture, N-D sharding, performance, precision, data/checkpoint and debugging. Experimental modules remain explicitly experimental; upstream benchmark data are not HCU results.

- [源码目录](../source-maps/pytorch-torchtitan.md)：1187 路径，固定 `65aaaa960698ab5d6e98c874177b41b9c30e9c58`，目录覆盖。
- [文档目录](../upstream-docs/pytorch-torchtitan/)：扫描发现 64 份；保留 64 份（包含历史）；历史范围 0 份。扫描模式见 sources.json，pending 由更新运行报告给出。
- 按已复核范围排除 12 份文档；规则与理由见 sources.json 的 document_exclusions。排除不代表上游删除，仍可按固定源码路径查阅。
- [PR #4651：Fix EP shape live-outs by keeping same-root AllToAll dim-0 queries chunk-local](../prs/pytorch--torchtitan/PR-4651.md)
- [PR #4760：[CP] Optimize Kimi K3 MLA all-gather and Ulysses communication](../prs/pytorch--torchtitan/PR-4760.md)
- [PR #4772：Add global batch-wise MoE auxiliary loss](../prs/pytorch--torchtitan/PR-4772.md)
- [PR #4835：[Deepseek V4] Dsv4 sparse indexer loss](../prs/pytorch--torchtitan/PR-4835.md)
- [PR #5033：[KimiK3 Perf] Add local compilation and overrides fla kernel for Kimi attention residual](../prs/pytorch--torchtitan/PR-5033.md)
- [PR #5101：Move FullAC to torch_remat](../prs/pytorch--torchtitan/PR-5101.md)
- [PR #5107：[rl] Stage trainer weight casts in pinned CPU memory](../prs/pytorch--torchtitan/PR-5107.md)
- [PR #5137：[HiMidLoLinear] Accumulate LM-head WGRAD into the running fp32 grad in place](../prs/pytorch--torchtitan/PR-5137.md)
- [PR #5153：[module] Keep Module buffers in their dtype across module casts](../prs/pytorch--torchtitan/PR-5153.md)
- [PR #5182：[rl] Fail an invalid generation request without crashing the generator](../prs/pytorch--torchtitan/PR-5182.md)
- [PR #5186：[rl] DAPO-Math: score Math-Verify in worker processes with a hard timeout](../prs/pytorch--torchtitan/PR-5186.md)
- [PR #5188：[rl] DAPO-Math grader: box the gold answer before parsing](../prs/pytorch--torchtitan/PR-5188.md)
- [PR #5190：[rl] Extract the generator's engine loop into VLLMEngineLoop](../prs/pytorch--torchtitan/PR-5190.md)
- [PR #5217：[rl] release a routing session when its rollout ends (2/5)](../prs/pytorch--torchtitan/PR-5217.md)
- [PR #5218：[rl] drain mode: wait for the pinned generator instead of re-pinning (3/5)](../prs/pytorch--torchtitan/PR-5218.md)
- [PR #5219：[rl] opt-in repin_load_ratio for sticky routing (4/5)](../prs/pytorch--torchtitan/PR-5219.md)
- [PR #5220：[rl] hold each multi-turn session's KV between its turns (5/5)](../prs/pytorch--torchtitan/PR-5220.md)
- [PR #5227：[fix] wandb: stop dropping validation metrics logged at a training step (1/2)](../prs/pytorch--torchtitan/PR-5227.md)
- [PR #5228：[rl] Periodic validation, optionally overlapped with training (2/2)](../prs/pytorch--torchtitan/PR-5228.md)
- [PR #5233：[WIP] [rl] Bump StickySessionRoutingStrategy max_sessions default to 262144](../prs/pytorch--torchtitan/PR-5233.md)
- [PR #5234：[rl] Name training-loop timings by what they measure (1/2)](../prs/pytorch--torchtitan/PR-5234.md)
- [PR #5235：[rl] Reply to the weight push from its worker thread, so the pull overlaps forward/backward (2/2)](../prs/pytorch--torchtitan/PR-5235.md)
- [PR #5250：[Linear] In-place WGRAD accumulation for the bf16 Linear](../prs/pytorch--torchtitan/PR-5250.md)
- [PR #5251：[rl] Fix generator OOM from weight sync spike](../prs/pytorch--torchtitan/PR-5251.md)
- [PR #5254：[rl] Count every token in perf/trainer throughput; log controller GC time](../prs/pytorch--torchtitan/PR-5254.md)
- [PR #5255：[rl] MoE router replay: train on the experts the generator chose](../prs/pytorch--torchtitan/PR-5255.md)
- [PR #5256：[rl] keep session KV in an evict-last free-queue tier instead of pinning it (on #5220)](../prs/pytorch--torchtitan/PR-5256.md)
- [PR #5257：[rl] vLLM priority scheduling: serve rollout groups in the order they started](../prs/pytorch--torchtitan/PR-5257.md)
- [PR #5259：Fuse DSv3 sequence-wise loss forward/backward](../prs/pytorch--torchtitan/PR-5259.md)
- [PR #5263：[MoE] Opt-in shared-expert overlap with deferred DeepEP dispatch](../prs/pytorch--torchtitan/PR-5263.md)
- [PR #5266：Make the vision encoder CP-invariant, only dp_shard](../prs/pytorch--torchtitan/PR-5266.md)
- [PR #5267：[qwen3.5] Raise offset_rmsnorm's recompile limit to 16](../prs/pytorch--torchtitan/PR-5267.md)
- [PR #5268：[rl] FSDP generator: sync weights one FSDP module at a time](../prs/pytorch--torchtitan/PR-5268.md)
- [PR #5269：[rl] spawn_proc_mesh: roles that share a host mesh get disjoint GPUs](../prs/pytorch--torchtitan/PR-5269.md)
- [PR #5270：[rl] Verifiers generation server: reject prompts that leave no room for an output token](../prs/pytorch--torchtitan/PR-5270.md)
- [PR #5271：[rl] RL model defaults in every run: fp32 lm_head, frozen MoE expert bias and router gate](../prs/pytorch--torchtitan/PR-5271.md)
- [PR #5272：[rl] trainer ranks pull their own microbatches by RDMA ref](../prs/pytorch--torchtitan/PR-5272.md)
- [PR #5273：[rl] Store each turn's prompt as a delta on the previous turn (linear-size multi-turn rollouts) (1/2)](../prs/pytorch--torchtitan/PR-5273.md)
- [PR #5274：[rl] RolloutTurn and TrainingSample per-token fields as numpy arrays (2/2)](../prs/pytorch--torchtitan/PR-5274.md)
- [PR #5276：[Kimi K3] Make the vision encoder CP-invariant](../prs/pytorch--torchtitan/PR-5276.md)
- [PR #5277：Reorganize repo structure, dependencies, docs, and tests](../prs/pytorch--torchtitan/PR-5277.md)
- [PR #5279：[DistMuon] Send redistributed inputs and directions in BF16](../prs/pytorch--torchtitan/PR-5279.md)
- [PR #5280：Build sharded model configs; separate RL trainer and generator models](../prs/pytorch--torchtitan/PR-5280.md)
- [PR #5282：Initialize CPU-offloaded EMA directly in pinned host storage](../prs/pytorch--torchtitan/PR-5282.md)
- [PR #5283：Fix tuple assignment in spmd_types.py](../prs/pytorch--torchtitan/PR-5283.md)
- [PR #5284：[rl] Build and pack training batches in their own process](../prs/pytorch--torchtitan/PR-5284.md)
- [PR #5285：[rl] Add an opt-in RDMA fast path for trainer microbatches](../prs/pytorch--torchtitan/PR-5285.md)
- [PR #5286：[rl] read each trainer rank's microbatches two ahead of training](../prs/pytorch--torchtitan/PR-5286.md)
- [PR #5288：Resolve commits before checkout in loss_compare and checkpoint_compat_test](../prs/pytorch--torchtitan/PR-5288.md)
- [PR #5289：[data] Give each DatasetConcatConfig child its own seed](../prs/pytorch--torchtitan/PR-5289.md)
- [PR #5290：[rl] Controller GC: freeze the setup heap, fold generator metrics per rollout and group](../prs/pytorch--torchtitan/PR-5290.md)
- [PR #5291：[rl] Build and pack training batches in their own process](../prs/pytorch--torchtitan/PR-5291.md)
- [PR #5292：[rl] Drain in-flight rollouts during shutdown](../prs/pytorch--torchtitan/PR-5292.md)
- [PR #5294：[rl] Keep Verifiers env-server workers off the trainer imports](../prs/pytorch--torchtitan/PR-5294.md)
- [PR #5295：Remove shared SDPA and use Varlen attention in Flux](../prs/pytorch--torchtitan/PR-5295.md)
- [PR #5296：[Attn] Remove SDPA and use Varlen attention in Flux](../prs/pytorch--torchtitan/PR-5296.md)
- [PR #5298：[rl][easy] Require torchmonarch>=0.7.0](../prs/pytorch--torchtitan/PR-5298.md)
- [PR #5299：[rl] offload idle session KV to CPU (6/6)](../prs/pytorch--torchtitan/PR-5299.md)
- [PR #5300：[rl] Send each trainer DP replica only its column of the grid](../prs/pytorch--torchtitan/PR-5300.md)
