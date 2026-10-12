---
id: doc-pytorch-torchtitan-b6f132c9d383d44338b5
title: pytorch/torchtitan / torchtitan/experiments/transformers_modeling_backend/README.md
engine: torchtitan
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: pytorch/torchtitan
commit: 65aaaa960698ab5d6e98c874177b41b9c30e9c58
path: torchtitan/experiments/transformers_modeling_backend/README.md
raw_sha256: 813a6accc31021e494064e22df5c268ea5df9212e67445ae1304fd5cdc741854
sources: []
generated_body_sha256: 0301f8e73c81a5bdca65da56f3bd61e3389188ddde07b5385a80ee3669c18401
source_state: current-scan
---

# pytorch/torchtitan / torchtitan/experiments/transformers_modeling_backend/README.md

[Original at fixed commit](https://github.com/pytorch/torchtitan/blob/65aaaa960698ab5d6e98c874177b41b9c30e9c58/torchtitan/experiments/transformers_modeling_backend/README.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Huggingface Transformers Modeling backend

This enables HF transformers models to be trained with 4D parallelism.

This backend uses the TorchTitan SPMD type system.

## Quick start

- Requirements `transformers==5.9.0`

- Test recipes: `torchtitan_recipes/tests/transformers_modeling_backend.py`
```diff
...
- --module torchtitan_recipes.tests.models.llama3
+ --module torchtitan_recipes.tests.transformers_modeling_backend
 --config transformers_modeling_backend_debugmodel
...
```
- Train: `LOG_RANK=7 MODULE=torchtitan_recipes.tests.transformers_modeling_backend CONFIG=transformers_modeling_backend_debugmodel_compile ./run_train.sh`
    - Make sure you have created the tokenizers beforehand
<img width="1334" height="453" alt="image" src="https://github.com/user-attachments/assets/da459448-027b-4af9-8176-6a3e433a272c" />

## Supported Features

- The following models were tested. This is backend coverage, not a set of
  recommended production training recipes:
    - Dense (FSDP/CP/TP/PP/`torch.compile`)
        - `meta-llama/Llama-3.2-1B`
        - `microsoft/phi-2`
        - `Qwen/Qwen2.5-7B`
        - `mistralai/Mistral-7B-v0.1`
        - `ByteDance-Seed/Seed-Coder-8B-Instruct`
        - `Qwen/Qwen3-4B-Instruct-2507`
        - `arcee-ai/AFM-4.5B`
        - `ibm-granite/granite-3b-code-base-2k`
        - `baidu/ERNIE-4.5-0.3B-Base-PT`
        - `kyutai/helium-1-preview-2b`
        - `allenai/OLMo-7B-hf`
        - `mistralai/Ministral-8B-Instruct-2410`
    - MoE (see the table below for parallelism support)
        - `Qwen/Qwen3-30B-A3B` (qwen3_moe, GQA)
        - `mistralai/Mixtral-8x7B-Instruct-v0.1` (mixtral, GQA)
        - `allenai/OLMoE-1B-7B-0924` (olmoe, GQA)
        - `deepseek-ai/DeepSeek-V2-Lite` (deepseek_v2, MLA)
        - `deepseek-ai/DeepSeek-V3` (deepseek_v3, MLA)
        - `zai-org/GLM-4.7` (glm4_moe, MLA)
        - `zai-org/GLM-5` (glm_moe_dsa, MLA + DSA sparse attention)
        - `google/gemma-4-26B-A4B-it` (gemma4_text)

### Attention

Attention runs on **FlexInnerAttention**. `attn_mask_type` selects the flex mask:
`causal` (plain causal) or `block_causal` (causal + same-document, for packed /
SFT sequences).

### MoE

The MoE block is swapped to TorchTitan's grouped-experts MoE to enable expert
parallelism and the `grouped_mm` fast path.

Parallelism support, validated at debug scale (2-step loss decreasing) across the
combinations below. FSDP composes with every listed axis.

| Model(s) | attn | TP | EP | CP | notes |
|---|---|---|---|---|---|
| Qwen3-30B-A3B | GQA | yes | yes | yes | full matrix up to TP+EP+CP |
| Mixtral-8x7B, OLMoE-1B-7B | GQA | yes | yes | yes | TP+EP, EP+CP |
| DeepSeek-V2-Lite, V3, GLM-4.7 | MLA | yes | yes | yes* | TP+EP; *flex+CP verified on DeepSeek-V2-Lite (EP+CP) |
| GLM-5 | MLA + DSA | no | yes | no | DSA indexer fails loud under TP; CP not wired -- FSDP/EP only |
| Gemma-4-26B-A4B | GQA | no | yes | no | attention TP not viable (num_global_key_value_heads=2) -- FSDP/EP only |

PP is not yet wired for the MoE path (see Further work).

## Known issues to address later

- When using HF modeling, the test `FSDP=2 vs FSDP=2 + PP=2`, the `loss` and `grad_norm` not bitwise matching (but converging) while it is the case with Torchtitan modeling. This will be addressed in another PR but the culprit is probably `register_buffer` when loading `seed_checkpoint`
- the HF modeling has lower MFU than Torchtitan MFU

## Further work

- Missing PP support for MoE
- Load HF weights
- Add LORA support
- Support for Titan RL
