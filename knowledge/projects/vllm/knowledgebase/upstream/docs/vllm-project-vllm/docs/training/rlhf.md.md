---
id: doc-vllm-project-vllm-b2a7d42b3ecd0a62f85a
title: vllm-project/vllm / docs/training/rlhf.md
engine: vllm
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: vllm-project/vllm
commit: 25e7c5728d834335288d080e1c36810fa111d4da
path: docs/training/rlhf.md
raw_sha256: 56d2f446eb98232949176564869840ad8bcc9d182b8ce40959bd4f28f5d22bf8
sources: []
generated_body_sha256: 63f51011be96cb2c63e7c2991d9b121752374083eb50d138d39d37bfefd680b6
source_state: current-scan
---

# vllm-project/vllm / docs/training/rlhf.md

[Original at fixed commit](https://github.com/vllm-project/vllm/blob/25e7c5728d834335288d080e1c36810fa111d4da/docs/training/rlhf.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Reinforcement Learning from Human Feedback

Reinforcement Learning from Human Feedback (RLHF) is a technique that fine-tunes language models using human-generated preference data to align model outputs with desired behaviors. vLLM can be used to generate the completions for RLHF.

The following open-source RL libraries use vLLM for fast rollouts (sorted alphabetically and non-exhaustive):

- [Cosmos-RL](https://github.com/nvidia-cosmos/cosmos-rl)
- [ms-swift](https://github.com/modelscope/ms-swift/tree/main)
- [NeMo-RL](https://github.com/NVIDIA-NeMo/RL)
- [Open Instruct](https://github.com/allenai/open-instruct)
- [OpenRLHF](https://github.com/OpenRLHF/OpenRLHF)
- [PipelineRL](https://github.com/ServiceNow/PipelineRL)
- [Prime-RL](https://github.com/PrimeIntellect-ai/prime-rl)
- [SkyRL](https://github.com/NovaSky-AI/SkyRL)
- [TRL](https://github.com/huggingface/trl)
- [Unsloth](https://github.com/unslothai/unsloth)
- [verl](https://github.com/volcengine/verl)

For weight synchronization between training and inference, see the [Weight Transfer](weight_transfer/README.md) documentation, which covers the pluggable backend system with [NCCL](weight_transfer/nccl.md) (multi-GPU) and [IPC](weight_transfer/ipc.md) (same-GPU) engines. To verify that an update landed on every rank, see the [Weight Checker](weight_checker.md). To check updates for a new model without a trainer, see [Verifying a New Model Without a Trainer](weight_transfer/README.md#verifying-a-new-model-without-a-trainer).

For MoE policies, see [Routed Experts Return](routed_experts.md) (`--enable-return-routed-experts`) to get the per-token expert routing of each rollout for routing replay (R3) in the trainer.

For pipelining generation and training to improve GPU utilization and throughput, see the [Async Reinforcement Learning](async_rl.md) guide, which covers the pause/resume API for safely updating weights mid-flight.

See the following notebooks showing how to use vLLM for GRPO:

- [Efficient Online Training with GRPO and vLLM in TRL](https://huggingface.co/learn/cookbook/grpo_vllm_online_training)
- [Qwen-3 4B GRPO using Unsloth + vLLM](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_(4B)-GRPO.ipynb)
