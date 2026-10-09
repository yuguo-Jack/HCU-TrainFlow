---
id: doc-nvidia-transformerengine-223007e59795eebd96aa
title: NVIDIA/TransformerEngine / examples/pytorch/comm_gemm_overlap/README.md
engine: transformer-engine
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: NVIDIA/TransformerEngine
commit: 39c30c577f5dd4f9fba921ee011b5cd797ae667e
path: examples/pytorch/comm_gemm_overlap/README.md
raw_sha256: 16d677ac34c025955d7afc08b89aa1d4ca620a888fbb351543fd6b45269dd936
sources: []
generated_body_sha256: 8af8a017f174899ae7f097961192236f771c171188e8fea10da8d589c2cfcc1d
source_state: current-scan
---

# NVIDIA/TransformerEngine / examples/pytorch/comm_gemm_overlap/README.md

[Original at fixed commit](https://github.com/NVIDIA/TransformerEngine/blob/39c30c577f5dd4f9fba921ee011b5cd797ae667e/examples/pytorch/comm_gemm_overlap/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Overlapping Communication with GEMM in TransformerEngine Modules

## Requirements

- Tensor-parallel GPUs must be on a single node, and connected over NVLink/NVSwitch.
- `CUDA_DEVICE_MAX_CONNECTIONS=1` must be enabled in the environment.
- For best performance, point-to-point communication via _CUDA Multicast_ needs CUDA Toolkit 12.0+
  and CUDA driver 535+ on devices with compute capability 9.0 or newer.
- Devices older than compute capability 9.0 require `UB_SKIPMC=1` in the environment in order to fall
  back on a less performant implementation based on CUDA Inter-Process Communication (IPC) handles.

## Examples

### Single node, tensor-parallel LayerNormMLP:

Forward and backward passes with layer weights distributed over all GPUs in a single node.

```bash
$ torchrun --nnodes=1 --nproc-per-node=$(nvidia-smi -L | wc -l) te_layer_with_overlap.py

# Sample output on 8x H100s:
#   [rank0:node0] |-- Created tensor-parallel group: [0, 1, 2, 3, 4, 5, 6, 7]
#   !!! [UB] Create UbufP2PCommOverlap Communicator
#   UB_TIMEOUT is set to 110 sec, 217800000000 cycles, freq: 1980000khz
#   MC initialized successfully, window size = 549755813888
#   !!! [UBP2P] Register UBuf 1
#   !!! [UBP2P] Register UBuf 2
#   !!! [UBP2P] Register UBuf 3
#   !!! [UBP2P] Register UBuf 4
#   !!! [UB] Register UBuf 5
#   !!! [UBP2P] Register UBuf 6
#   !!! [UB] Register UBuf 7
#   !!! [UB] Register UBuf 8
#   !!! [UBP2P] Register UBuf 9
#   !!! [UB] Register UBuf 10
#   [rank0:node0] Iter 1
#   [rank0:node0] |-- Generate random input batch
#   [rank0:node0] |-- Forward pass
#   [rank0:node0] |-- Compute loss
#   [rank0:node0] |-- Backward pass
#   [rank0:node0] |-- Optimizer step
#   [rank0:node0] Iter 2
#   [rank0:node0] |-- Generate random input batch
#   [rank0:node0] |-- Forward pass
#   [rank0:node0] |-- Compute loss
#   [rank0:node0] |-- Backward pass
#   [rank0:node0] |-- Optimizer step
#   [rank0:node0] Iter 3
#   [rank0:node0] |-- Generate random input batch
#   [rank0:node0] |-- Forward pass
#   [rank0:node0] |-- Compute loss
#   [rank0:node0] |-- Backward pass
#   [rank0:node0] |-- Optimizer step
#   [rank0:node0] Iter 4
#   [rank0:node0] |-- Generate random input batch
#   [rank0:node0] |-- Forward pass
#   [rank0:node0] |-- Compute loss
#   [rank0:node0] |-- Backward pass
#   [rank0:node0] |-- Optimizer step
#   [rank0:node0] Iter 5
#   [rank0:node0] |-- Generate random input batch
#   [rank0:node0] |-- Forward pass
#   [rank0:node0] |-- Compute loss
#   [rank0:node0] |-- Backward pass
#   [rank0:node0] |-- Optimizer step
```
### Single node, mixed data- and tensor-parallel LayerNormMLP:

Uses `torch.nn.parallel.DistributedDataParallel` for replicating the model across 2 tensor-parallel
groups in a single node.

```bash
$ torchrun --nnodes=1 --nproc-per-node=$(nvidia-smi -L | wc -l) te_layer_with_overlap.py --num-replicas 2

# Sample output on 8x H100s:
#   [rank0:node0] |-- Created tensor-parallel group: [0, 1, 2, 3]
#   [rank4:node1] |-- Created tensor-parallel group: [4, 5, 6, 7]
#   [rank0:node0] |-- Created data-parallel group: [0, 4]
#   [rank3:node1] |-- Created data-parallel group: [3, 7]
#   [rank1:node1] |-- Created data-parallel group: [1, 5]
#   [rank2:node0] |-- Created data-parallel group: [2, 6]
#   !!! [UB] Create UbufP2PCommOverlap Communicator
#   UB_TIMEOUT is set to 110 sec, 217800000000 cycles, freq: 1980000khz
#   MC initialized successfully, window size = 549755813888
#   !!! [UBP2P] Register UBuf 1
#   !!! [UBP2P] Register UBuf 2
#   !!! [UBP2P] Register UBuf 3
#   !!! [UBP2P] Register UBuf 4
#   !!! [UB] Register UBuf 5
#   !!! [UBP2P] Register UBuf 6
#   !!! [UB] Register UBuf 7
#   !!! [UB] Register UBuf 8
#   !!! [UBP2P] Register UBuf 9
#   !!! [UB] Register UBuf 10
#   [rank4:node1] Iter 1
#   [rank0:node0] Iter 1
#   [rank0:node0] |-- Generate random input batch
#   [rank4:node1] |-- Generate random input batch
#   [rank0:node0] |-- Forward pass
#   [rank4:node1] |-- Forward pass
#   [rank4:node1] |-- Compute loss
#   [rank0:node0] |-- Compute loss
#   [rank0:node0] |-- Backward pass
#   [rank4:node1] |-- Backward pass
#   [rank4:node1] |-- Optimizer step
#   [rank0:node0] |-- Optimizer step
#   [rank4:node1] Iter 2
#   [rank0:node0] Iter 2
#   [rank0:node0] |-- Generate random input batch
#   [rank4:node1] |-- Generate random input batch
#   [rank4:node1] |-- Forward pass
#   [rank0:node0] |-- Forward pass
#   [rank4:node1] |-- Compute loss
#   [rank0:node0] |-- Compute loss
#   [rank4:node1] |-- Backward pass
#   [rank0:node0] |-- Backward pass
#   [rank4:node1] |-- Optimizer step
#   [rank0:node0] |-- Optimizer step
#   [rank4:node1] Iter 3
#   [rank0:node0] Iter 3
#   [rank0:node0] |-- Generate random input batch
#   [rank4:node1] |-- Generate random input batch
#   [rank0:node0] |-- Forward pass
#   [rank4:node1] |-- Forward pass
#   [rank4:node1] |-- Compute loss
#   [rank0:node0] |-- Compute loss
#   [rank4:node1] |-- Backward pass
#   [rank0:node0] |-- Backward pass
#   [rank0:node0] |-- Optimizer step
#   [rank4:node1] |-- Optimizer step
#   [rank0:node0] Iter 4
#   [rank4:node1] Iter 4
#   [rank0:node0] |-- Generate random input batch
#   [rank4:node1] |-- Generate random input batch
#   [rank0:node0] |-- Forward pass
#   [rank4:node1] |-- Forward pass
#   [rank0:node0] |-- Compute loss
#   [rank4:node1] |-- Compute loss
#   [rank4:node1] |-- Backward pass
#   [rank0:node0] |-- Backward pass
#   [rank4:node1] |-- Optimizer step
#   [rank0:node0] |-- Optimizer step
#   [rank4:node1] Iter 5
#   [rank0:node0] Iter 5
#   [rank0:node0] |-- Generate random input batch
#   [rank4:node1] |-- Generate random input batch
#   [rank0:node0] |-- Forward pass
#   [rank4:node1] |-- Forward pass
#   [rank0:node0] |-- Compute loss
#   [rank4:node1] |-- Compute loss
#   [rank0:node0] |-- Backward pass
#   [rank4:node1] |-- Backward pass
#   [rank4:node1] |-- Optimizer step
#   [rank0:node0] |-- Optimizer step
```

**NOTE:** To run with Fp8 compute on supporting hardware, add the `--fp8` flag to the commands
shown above.