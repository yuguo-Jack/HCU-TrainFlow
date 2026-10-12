---
id: doc-ascend-mindspeed-llm-6a7812e410e4cddb88e8
title: Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/variable_length_flash_attention.md
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
path: docs/en/pytorch/features/mcore/variable_length_flash_attention.md
raw_sha256: a316a8fd224556a43fb9a5bf0ac2cf8c41d29734dc06098fc4dbf0efabeaf462
sources: []
generated_body_sha256: 2d1db5e1880c9de33fa74be86ff902e33fa7a838308e3997c50b3f5fcb345205
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/features/mcore/variable_length_flash_attention.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/features/mcore/variable_length_flash_attention.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Variable-Length FlashAttention Training Scenarios

## Training Scenarios

Within a batch, the input text sequence usually comes from concatenating multiple documents (docs). By default, the system treats multiple documents as a single sequence, and it does not mask self-attention between them. In some cases, the documents must remain independent, and self-attention must not cross document boundaries. In this case, the attention mask and position IDs must be reset at each end-of-document (EOD) position.

## Solution

The variable-length mode of the underlying FlashAttention operator supports this training scenario.

## Usage

### 1. Data Preparation

First, ensure that you add an EOD token to the end of each document.

```shell
# To enable TND, you must add EOD: --append-eod
python ./preprocess_data.py \
   --input ./dataset/train-00000-of-00001-a09b74b3ef9c3b56.parquet \
   --tokenizer-name-or-path ./model_from_hf/Llama3-hf/ \
   --output-prefix ./dataset/enwiki \
   --workers 4 \
   --log-interval 1000  \
   --append-eod \
   --tokenizer-type PretrainedFromHF
```

### 2. Training Parameter Settings

Add the `--reset-attention-mask` parameter to the model training script.

After you enable it, the system generates the `actual_seq_len` variable based on the EOD positions to indicate the actual length of the concatenated documents.

## How It Works

### 1. Before Enablement

Initialize `attn_mask` as a compressed lower-triangular matrix (2048*2048).

<img alt="Triangular causal attention mask before enablement" src="../../figures/variable_length_flash_attention/causal_mask.png" width="261"/>

Multiple documents are treated as a single sequence, self-attention between them is not masked, and all tokens participate in the computation.

### 2. After Enablement

Do not initialize a mask. Instead, generate `actual_seq_len` based on the EOD positions. Suppose the true text lengths in one sequence are [2, 2, 0, 2, 2]. Then `actual_seq_len` is [2, 4, 4, 6, 8].
The actual compute cost depends on `actual_seq_len`.

`attn_mask` can be represented as follows, although the system does not generate it during actual computation:

<img alt="Variable-length attention mask after enablement" src="../../figures/variable_length_flash_attention/varlen_mask.png" width="414"/>

The blank area in the lower left does not participate in the computation.
