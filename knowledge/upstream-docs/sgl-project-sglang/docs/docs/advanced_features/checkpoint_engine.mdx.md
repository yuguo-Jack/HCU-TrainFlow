---
id: doc-sgl-project-sglang-e9a88b310863abd65152
title: sgl-project/sglang / docs/docs/advanced_features/checkpoint_engine.mdx
engine: sglang
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: sgl-project/sglang
commit: bd2d73daa5afda6bcad8d479a834f2e70bbe9569
path: docs/docs/advanced_features/checkpoint_engine.mdx
raw_sha256: 4ed58f6f4fbeae97e2be0f8e4c2277379f67f1c22e428dcc78365ac09480a016
sources: []
generated_body_sha256: cfcfb5877d038014ab8d51ef7c81ed96e6e24bb863b413de9c1845e4dff64ee5
source_state: current-scan
---

# sgl-project/sglang / docs/docs/advanced_features/checkpoint_engine.mdx

[Original at fixed commit](https://github.com/sgl-project/sglang/blob/bd2d73daa5afda6bcad8d479a834f2e70bbe9569/docs/docs/advanced_features/checkpoint_engine.mdx)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
title: "Checkpoint Engine Integration"
metatags:
    description: "SGLang checkpoint engine: distributed model weight loading, parallel multi-node setup, broadcast and P2P modes. Reduces loading time for large models."
---
The SGLang checkpoint engine integration provides an efficient way to load model weights using a distributed checkpoint loading system. This feature significantly reduces model loading time, especially for large models and multi-node setups, by parallelizing the weight loading process across multiple processes and nodes.

## Overview

The checkpoint engine integration allows SGLang to:
- Load model weights in parallel using multiple processes
- Distribute weight loading across multiple nodes to increase effective disk bandwidth
- Overlap weight loading with other initialization tasks like CUDA graph capture
- Support both single-node and multi-node deployments

## Installation

First, install the checkpoint engine package:

```bash Command
pip install 'checkpoint-engine[p2p]'
```

## Architecture

The system consists of two main components:

1. **SGLang Server**: Runs with `--checkpoint-engine-wait-weights-before-ready` flag to wait for weights before becoming ready
2. **Checkpoint Engine Workers**: Separate processes (managed by torchrun) that load and distribute model weights

The checkpoint engine uses a parameter server architecture with support for:
- **Broadcast mode**: Weights are broadcast from loading processes to inference processes
- **P2P mode**: Direct peer-to-peer weight transfer between processes
- **All mode**: Combination of both broadcast and P2P methods

## Usage Examples

### Single Node Setup

**Terminal 1 - Launch SGLang Server:**
```bash Command
python -m sglang.launch_server \
    --model-path Qwen/Qwen3-8B \
    --tp 8 \
    --load-format dummy \
    --checkpoint-engine-wait-weights-before-ready
```

**Terminal 2 - Run Checkpoint Engine:**

Using sglang entrypoint:
```bash Command
python -m sglang.srt.checkpoint_engine.update \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 8
```

Using torchrun directly:
```bash Command
torchrun --nproc-per-node 8 \
    examples/checkpoint_engine/update.py \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 8
```

### Multi-Node Setup (2 Nodes)

**Node 0:**

Launch SGLang server:
```bash Command
python -m sglang.launch_server \
    --model-path Qwen/Qwen3-8B \
    --tp 8 \
    --load-format dummy \
    --checkpoint-engine-wait-weights-before-ready \
    --host [IP]
```

Run checkpoint engine:

Using sglang entrypoint (recommended):
```bash Command
python -m sglang.srt.checkpoint_engine.update \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 8
```

Using torchrun directly:
```bash Command
torchrun --nproc-per-node 8 \
    --nnodes 2 \
    --node-rank 0 \
    --master-addr [IP] \
    --master-port 29500 \
    examples/checkpoint_engine/update.py \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 8
```

**Node 1:**

Launch SGLang server:
```bash Command
python -m sglang.launch_server \
    --model-path Qwen/Qwen3-8B \
    --tp 8 \
    --load-format dummy \
    --checkpoint-engine-wait-weights-before-ready \
    --host [IP]
```

Run checkpoint engine:

Using sglang entrypoint (recommended):
```bash Command
python -m sglang.srt.checkpoint_engine.update \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 8
```

Using torchrun directly:
```bash Command
torchrun --nproc-per-node 8 \
    --nnodes 2 \
    --node-rank 1 \
    --master-addr [IP] \
    --master-port 29500 \
    examples/checkpoint_engine/update.py \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 8
```

### Multi-Node Setup with Tensor Parallelism (TP=16)

**Node 0:**

Launch SGLang server:
```bash Command
python -m sglang.launch_server \
    --model-path Qwen/Qwen3-8B \
    --tp 8 \
    --load-format dummy \
    --checkpoint-engine-wait-weights-before-ready \
    --host [IP] \
    --dist-init-addr [IP]:9120 \
    --nnodes 2 \
    --node-rank 0
```

Run checkpoint engine:

Using sglang entrypoint (recommended):
```bash Command
python -m sglang.srt.checkpoint_engine.update \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 16
```

Using torchrun directly:
```bash Command
torchrun --nproc-per-node 8 \
    --nnodes 2 \
    --node-rank 0 \
    --master-addr [IP] \
    --master-port 29500 \
    examples/checkpoint_engine/update.py \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 16
```

**Node 1:**

Launch SGLang server:
```bash Command
python -m sglang.launch_server \
    --model-path Qwen/Qwen3-8B \
    --tp 8 \
    --load-format dummy \
    --checkpoint-engine-wait-weights-before-ready \
    --host [IP] \
    --dist-init-addr [IP]:9120 \
    --nnodes 2 \
    --node-rank 1
```

Run checkpoint engine:

Using sglang entrypoint (recommended):
```bash Command
python -m sglang.srt.checkpoint_engine.update \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 16
```

Using torchrun directly:
```bash Command
torchrun --nproc-per-node 8 \
    --nnodes 2 \
    --node-rank 1 \
    --master-addr [IP] \
    --master-port 29500 \
    examples/checkpoint_engine/update.py \
    --update-method broadcast \
    --checkpoint-path /path/to/Qwen/Qwen3-8B/ \
    --inference-parallel-size 16
```

## Configuration Options

### SGLang Server Options

- `--load-format dummy`: Use dummy format for initial loading (allows overlapping with other tasks)
- `--checkpoint-engine-wait-weights-before-ready`: Wait for checkpoint engine to provide weights before becoming ready
- `--host`: Host address for multi-node setups
- `--dist-init-addr`: Distributed initialization address for tensor parallelism

### Checkpoint Engine Options

- `--update-method`: Weight update method (`broadcast`, `p2p`, or `all`)
- `--checkpoint-path`: Path to model checkpoint directory
- `--inference-parallel-size`: Number of inference parallel processes
- `--endpoint`: SGLang server endpoint (default: `http://localhost:19730`)
- `--checkpoint-name`: Name for the checkpoint (default: `my-checkpoint-iter-0`)
- `--save-metas-file`: File to save checkpoint metadata
- `--load-metas-file`: File to load checkpoint metadata from
- `--uds`: Unix domain socket path for communication
- `--weight-version`: Version identifier for weights

## Performance Benefits

The checkpoint engine provides significant time savings in two main aspects:

1. **Multi-node Loading**: Each node only loads a portion of weights from disk, effectively increasing disk bandwidth. More participating nodes provide greater acceleration. Preliminary tests show 20-second acceleration when loading DeepSeek-R1 on H20-3e with two nodes.

2. **Single Process Optimization**: Using dummy format allows overlapping disk-to-CPU transfer with CUDA graph capture and other initialization tasks, providing additional time savings.

## Troubleshooting

- Ensure checkpoint engine package is installed: `pip install 'checkpoint-engine[p2p]'`
- Verify network connectivity between nodes in multi-node setups
- Check that the checkpoint path contains valid model files
- Monitor logs for connection errors between SGLang server and checkpoint engine
- Use `--sleep-time` parameter to add delays if needed for debugging

## References

- [Checkpoint Engine Repository](https://github.com/MoonshotAI/checkpoint-engine)