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
commit: bde4d001130e5112d984ba99f0546e22c09e1a89
path: docs/training/rlhf.md
raw_sha256: d5f1075d027de319baf6e7698cf21701d90a7026d3c1807b2439b38c6e2a4ec5
sources: []
generated_body_sha256: 5c4eeea2d644e0ea987a7ffb6014c4f0399cb689748740273e7899019d3ab847
source_state: current-scan
---

# vllm-project/vllm / docs/training/rlhf.md

[Original at fixed commit](https://github.com/vllm-project/vllm/blob/bde4d001130e5112d984ba99f0546e22c09e1a89/docs/training/rlhf.md)

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

For weight synchronization between training and inference, see the [Weight Transfer](weight_transfer/README.md) documentation, which covers the pluggable backend system with [NCCL](weight_transfer/nccl.md) (multi-GPU) and [IPC](weight_transfer/ipc.md) (same-GPU) engines. To verify that an update landed on every rank, see the [Weight Checker](weight_checker.md).

For MoE policies, see [Routed Experts Return](routed_experts.md) (`--enable-return-routed-experts`) to get the per-token expert routing of each rollout for routing replay (R3) in the trainer.

For pipelining generation and training to improve GPU utilization and throughput, see the [Async Reinforcement Learning](async_rl.md) guide, which covers the pause/resume API for safely updating weights mid-flight.

See the following notebooks showing how to use vLLM for GRPO:

- [Efficient Online Training with GRPO and vLLM in TRL](https://huggingface.co/learn/cookbook/grpo_vllm_online_training)
- [Qwen-3 4B GRPO using Unsloth + vLLM](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_(4B)-GRPO.ipynb)
