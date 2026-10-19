---
id: doc-pytorch-torchtitan-d0d291f996686d7fce5b
title: pytorch/torchtitan / docs/evaluation.md
engine: torchtitan
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: pytorch/torchtitan
commit: a242475253433725f10f39c18f5ccbfdf188e097
path: docs/evaluation.md
raw_sha256: 01c96cc92985701cc7f3e64bdcff5180d454b5fb1c972d7e2684ae57017b4510
sources: []
generated_body_sha256: 6f325b86396a44cc527d9fd4ac9e24a897445a5f1d7848330ec6a57c25691e0d
source_state: current-scan
---

# pytorch/torchtitan / docs/evaluation.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/a242475253433725f10f39c18f5ccbfdf188e097/docs/evaluation.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Validation and Evaluation

`torchtitan` provides direct and indirect support for validation to support user's training goals. Direct support is provided by the `Validator` class which interacts directly with the training loop, and indirect support is provided through [HuggingFace checkpoint conversion](../torchtitan/components/checkpointer/README.md#huggingface) for users who want to do evaluation using external tools such as ELeutherAI's `lm_eval`.

## Validation
For users who want to perform validation directly during the training loop, we provide the `Validator` class which can be conveniently configured via `Validator.Config` in your recipe function. The validator class has access to and reuses many of the trainer's functions such as its parallelization, including pipelining.

Below is an example validation config:

```python
from torchtitan.components.data import (
    ConcatThenSplitPackingConfig,
    GrainDataLoader,
)
from torchtitan.components.validator import Validator
from torchtitan.components.data.text_datasets import DATASETS

validator=Validator.Config(
    freq=500,
    steps=-1,
    dataloader=GrainDataLoader.Config(
        dataset=ConcatThenSplitPackingConfig(
            dataset=DATASETS["c4_validation"],
        ),
        repeat=False,
    ),
),
```

Omitting `dataloader` uses this configuration by default.

Validation follows `training.disable_cuda_graphs` and shares the training graph pool.
See [CUDA graphs](../torchtitan/distributed/CUDA_GRAPH.md) for capture order and tensor lifetimes.

## Third-Party Evaluation
With `./scripts/checkpoint_conversion/convert_to_hf.py`, `torchtitan` offers support for converting checkpoints from DCP to safetensors format. Using this script, users can perform efficient evaluation separate from their training using external libraries that support HuggingFace e.g. `lm_eval` with `vllm` backend.

### Example usage of `lm_eval` with `vllm`:
To use this specific setup make sure to include a HuggingFace `config.json` file which is not provided by conversion script or `last_save_in_hf` option. The HF config file can be downloaded by running `python ./scripts/download_hf_assets.py --repo_id meta-llama/Llama-3.1-8B --assets config`.

Note that pip installing `lm-eval` may result in breaking `torchtitan` dev environment so we recommend creating a separate env.
```bash
pip install "lm-eval[vllm]"
lm_eval --model vllm \
    --model_args pretrained=./outputs/checkpoint/step-1000,tensor_parallel_size=8,dtype=auto,gpu_memory_utilization=0.8, \
    --tasks mmlu \
    --batch_size auto
```
|      Groups      |Version|Filter|n-shot|Metric|   |Value |   |Stderr|
|------------------|------:|------|------|------|---|-----:|---|-----:|
|mmlu              |      2|none  |      |acc   |↑  |0.6209|±  |0.0038|
| - humanities     |      2|none  |      |acc   |↑  |0.5481|±  |0.0066|
| - other          |      2|none  |      |acc   |↑  |0.7045|±  |0.0078|
| - social sciences|      2|none  |      |acc   |↑  |0.7351|±  |0.0078|
| - stem           |      2|none  |      |acc   |↑  |0.5357|±  |0.0085|
