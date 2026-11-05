---
id: doc-ascend-mindspeed-llm-283eac0f917cf08f3031
title: Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/checkpoint_resume.md
engine: mindspeed
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: Ascend/MindSpeed-LLM
commit: f5f84bbbac05be79f883b30629d7f637e6f4649e
path: docs/en/pytorch/features/mcore/checkpoint_resume.md
raw_sha256: 235bd94e2190aaf7616b59fe9e5afada11262ef4c0714ec30616f8092c0baa81
sources: []
generated_body_sha256: 134f7c65d1836e6ab806d9f7ac23efd39c6540c40b3fb665b0074fbc7d5a5b15
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/checkpoint_resume.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/f5f84bbbac05be79f883b30629d7f637e6f4649e/docs/en/pytorch/features/mcore/checkpoint_resume.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Checkpoint-based Resumable Training

## Use Case

During large-scale model pretraining, training may stop because of hardware failures, resource scheduling, or similar issues. To support resuming training after an interruption, the system provides the **checkpoint-based resumable training** feature. This document briefly explains how to configure and use this feature.

---

## How to Use

### 1. Prerequisites for Checkpoint-based Resumable Training

To use checkpoint-based resumable training, set the related parameters correctly when you launch the pretraining script. This ensures that the optimizer state, model parameters, and training progress are all saved completely.

Key parameters

| Parameter                     | Description |
|------------------------------|--------------------------------|
| `--use-distributed-optimizer` | This Parameter must be enabled. This saves the optimizer state across data parallel ranks in a distributed manner, which makes later restoration easier. |
| `--finetune` | ❌ Do not set this option. Otherwise, the system skips loading the optimizer state. |
| `--no-load-optim` | ❌ Do not set this option. Otherwise, the system does not restore the optimizer state, such as the learning rate and momentum. |
| `--no-load-rng` | ❌ Do not set this option. Otherwise, the system does not restore the random state. |

> [!NOTE] Note
> If you set `--finetune`, `--no-load-optim`, or `--no-load-rng`, the system does not restore the optimizer state or the random state. Therefore, it cannot truly resume training.

---

### 2. Saving Training Checkpoints

During training, if you configure `--save $SAVE_PATH` and a save interval such as `--save-interval`, the system automatically saves full checkpoints at regular intervals. These checkpoints include:

- Model weights
- Optimizer states
- Training iterations
- Random states

Example

```bash
--save /your/checkpoint/path \
--save-interval 500   # Save every 500 steps
```

Each save produces the following structure:

```shell
/your/checkpoint/path/
├── latest_checkpointed_iteration.txt
├── iter_0000001/
│   ├── mp_rank_00_000/
│   │   ├── distrib_optim.pt
│   │   └── model_optim_rng.pt
│   └── ...
└── iter_0000500/
    ├── mp_rank_00_000/
    │   ├── distrib_optim.pt
    │   └── model_optim_rng.pt
    └── ...
```

Key parameters:

| Parameter                     | Description |
|------------------------------|--------------------------------|
| `--use-distributed-optimizer` | This parameter must be enabled. This saves the optimizer state across data parallel ranks in a distributed manner, which makes later restoration easier. |
| `--no-save-optim` | ❌ Do not set this option. Otherwise, the system does not save the optimizer state, such as the learning rate and momentum. |
| `--no-save-rng` | ❌ Do not set this option. Otherwise, the system does not save the random state. |

---

### 3. Loading Weights to Resume Training

To resume training after an interruption, specify `--load` in the pretraining script launch command and point it to the previous save path. The following shows a parameter snippet. Incorporate it into the complete pretraining command:

```text
CHECKPOINT_PATH=/your/checkpoint/path

--use-distributed-optimizer  # Use the distributed optimizer. Required
--load ${CHECKPOINT_PATH}
```

> The system automatically reads `latest_checkpointed_iteration.txt`, finds the latest iteration, and restores the model and optimizer states.

### 4. Verifying the Resuming Result

The system restores the following content automatically:

- Model parameters
- Optimizer states, including Adam momentum and variance
- Learning rate scheduler state
- Completed training iterations, which prevents repeated training

After restoration, training continues from the checkpoint and prints the following log output:

```shell
successfully loaded checkpoint from xx at iteration x
(min, max) time across ranks:
load-checkpoint ....................:(9289.88, 9288.22)
```

---

## Usage Constraints

1. **File integrity**: Ensure that the checkpoint files under `$CHECKPOINT_PATH` are complete and intact.
2. **Training configuration consistency**: When you resume training, the batch size, model structure, number of training iterations, optimizer type, and similar settings should match the saved run.
3. **Distributed environment match**: Keep the number of NPUs and the parallel strategy, such as TP/DP, unchanged. Otherwise, loading fails.
