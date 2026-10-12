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
commit: 2fed626696175480ae1ab3342a94017301a25209
path: docs/en/pytorch/features/mcore/checkpoint_resume.md
raw_sha256: 4144d12b5fe396934d65d05f46250e2622ff64b7d1ced2160b73d6c4d72394c0
sources: []
generated_body_sha256: 110355f0d82a8d01d542ae19aacb5df2ec071ca61a37e649440d8ab1159dc8a6
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/checkpoint_resume.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/features/mcore/checkpoint_resume.md)

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

> [!NOTE]
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
|-- latest_checkpointed_iteration.txt
|-- iter_0000001/
|   |-- mp_rank_00_000/
|   |   |-- distrib_optim.pt
|   |   |-- model_optim_rng.pt
|   |-- ...
|-- iter_0000500/
|   |-- mp_rank_00_000/
|   |   |-- distrib_optim.pt
|   |   |-- model_optim_rng.pt
|   |-- ...
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
