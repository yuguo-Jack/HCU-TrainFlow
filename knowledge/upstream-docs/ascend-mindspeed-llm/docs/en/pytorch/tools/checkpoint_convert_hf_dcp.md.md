---
id: doc-ascend-mindspeed-llm-69f905f76801ea231906
title: Ascend/MindSpeed-LLM / docs/en/pytorch/tools/checkpoint_convert_hf_dcp.md
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
path: docs/en/pytorch/tools/checkpoint_convert_hf_dcp.md
raw_sha256: 6324a683f152a7f31a1844f7ba73b6fde55a3f0ec0bbbf4b2fd5cb0deab18457
sources: []
generated_body_sha256: fd87096931420b03a3ecbaed35ff136499f06aabd99c788f921b59d02e8e1c0f
source_state: current-scan
---

# Ascend/MindSpeed-LLM / docs/en/pytorch/tools/checkpoint_convert_hf_dcp.md

[Original at fixed commit](https://github.com/Ascend/MindSpeed-LLM/blob/2fed626696175480ae1ab3342a94017301a25209/docs/en/pytorch/tools/checkpoint_convert_hf_dcp.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# Guide to Using the MindSpeed LLM FSDP2 Backend DCP Weight Conversion Tool

## Use Cases

During LLM training and deployment, the DCP weight conversion tool is commonly used in the following scenarios:

- Train in the DCP format, then convert the resulting model weights to the Hugging Face standard format for inference or downstream tasks.
- Handle models with so many parameters that the full weights cannot be loaded into memory at once for format conversion.

The `merge_dcp_to_hf.py` script merges shards incrementally. This preserves correctness while minimizing memory usage. Therefore, it is suitable for LLM weight format conversion.

## Usage

### 1. CLI Parameters

| Parameter | Type | Default | Description |
|------|------|--------|------|
| --load-dir | str | None (required) | Directory that stores the DCP weights. It must contain valid PyTorch distributed checkpoint files. |
| --save-dir | str | `<load-dir>/hf_ckpt` | Output directory for Hugging Face-format weights. |
| --model-configs | str | None | Directory that contains model configuration files. The script copies it to the output directory. |
| --shard-size | int | `5000000000` (5 GB) | Maximum byte size of a single weight shard file. |

### 2. Basic Conversion

The simplest usage is as follows:

```bash
python mindspeed_llm/fsdp2/checkpoint/merge_dcp_to_hf.py \
        --load-dir <DCP_weight_path>
```

After the command runs, the Hugging Face-format weights are generated in the `<DCP_weight_path>/hf_ckpt` directory.

### 3. Specifying an Output Directory

If you need to save the converted model to a specific location, use the `--save-dir` parameter to specify the output directory:

```bash
python mindspeed_llm/fsdp2/checkpoint/merge_dcp_to_hf.py \
        --load-dir checkpoints/my_model/dcp_checkpoint \
        --save-dir hf_models/my_model
```

### 4. Copying Model Configuration Files at the Same Time

If you want the generated Hugging Face weights to load directly with `from_pretrained()`, provide the model configuration files, such as `config.json` and `tokenizer.json`:

```bash
python mindspeed_llm/fsdp2/checkpoint/merge_dcp_to_hf.py \
        --load-dir checkpoints/my_model/dcp_checkpoint \
        --save-dir hf_models/my_model \
        --model-configs pretrained_models/qwen3-8b
```

The script also copies the configuration files in that directory to the output directory.

### 5. Controlling the Weight Shard Size

For environments with limited memory resources, you can use `--shard-size` to control the maximum size of a single weight shard:

```bash
python mindspeed_llm/fsdp2/checkpoint/merge_dcp_to_hf.py \
        --load-dir checkpoints/my_model/dcp_checkpoint \
        --shard-size 2000000000
```

This example limits the size of each shard to 2 GB. Therefore, it helps reduce the memory peak during conversion.

## Outputs

1. When the total model size does not exceed `shard-size`, the output is a single file:

    ```text
    output_directory/
    ├── model.safetensors
    ├── config.json
    └── tokenizer.json
    ```

2. When the total model size exceeds `shard-size`, the output is split into shards:

    ```text
    output_directory/
    ├── model-00001-of-00005.safetensors
    ├── model-00002-of-00005.safetensors
    ├── model-00003-of-00005.safetensors
    ├── model-00004-of-00005.safetensors
    ├── model-00005-of-00005.safetensors
    ├── model.safetensors.index.json
    ├── config.json
    └── tokenizer.json
    ```

## Notes

- `--load-dir` must point to a complete and valid DCP weight directory.
- The script does not generate model configuration files automatically. If you need to load the model directly in Hugging Face, explicitly specify `--model-configs`.
- The conversion process uses shard-based loading, but each shard must still be loadable in the current environment.
