---
id: doc-baidu-baige-loongforge-f275f6f98d502980afa7
title: baidu-baige/LoongForge / docs/source_zh/llm_tutorial/llm_ckpt_convert.md
engine: loongforge
kind: source-document
review_level: source-reported
runtime_validated: false
stages:
- adapt
- optimize
- fault-tolerance
repository: baidu-baige/LoongForge
commit: 733126ddccaf49c4bfd780d384f00878c1f0a9a8
path: docs/source_zh/llm_tutorial/llm_ckpt_convert.md
raw_sha256: e76f5bc7bb8ca77e544a10fd7260a6d4346ef798fbff0cdbcdbfffc5cc867093
sources: []
generated_body_sha256: 4248f72df170ed7e3e5d5f66d9757d75fc452bae84f1192d460ca6c8ffad41f7
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source_zh/llm_tutorial/llm_ckpt_convert.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source_zh/llm_tutorial/llm_ckpt_convert.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# LLM 权重转换

## 1. 常用参数
在执行 LLM 权重转换时，建议通过命令行参数（args）传递参数。以下是常用参数：

|**参数**|**说明**|
|-|-|
|load_platform|加载权重的平台|
|save_platform|保存权重的平台|
|config_file|模型配置文件|
|convert_file|权重转换配置文件|
|tensor_model_parallel_size|目标张量并行大小|
|pipeline_model_parallel_size|目标流水线并行大小|
|expert_parallel_size|目标专家并行大小|
|expert_tensor_parallel_size|专家张量并行度|
|megatron_path|Megatron 仓库根目录|
|load_ckpt_path|加载权重路径|
|save_ckpt_path|保存权重路径|
|custom_pipeline_layers|自定义流水线层分配|
|safetensors|使用 safetensors 格式|
|max_workers|权重转换线程数|
|moe-grouped-gemm|在 MoE 中使用 grouped gemm|
|amax_epsilon|FP8 转换中 amax 计算的 Epsilon 值；用于 FP8 量化缩放因子，需与训练时设置的 FP8 EPS 环境变量对齐。适用于 `te` 和 `pt` 方法。|
|quant_method|使用的量化方法。可选值：[te, pt]，默认为 `te`。|
|force_pow_2_scales|为 True（默认）时，FP8 量化使用 2 的幂次缩放（与 DeepGEMM 的 get_e4m3_sf_and_sf_inv 匹配）。为 False 时，使用线性缩放。适用于 `te` 和 `pt` 方法。|
|fp8_force_no_requant|在 FP8 转换中跳过反量化 + 重新量化|

其他参数说明请参考 [checkpoint_convert.md](https://loongforge.readthedocs.io/en/latest/llm_tutorial/checkpoint_convert.html)。

## 2. 示例脚本
框架为每个模型提供了权重转换示例脚本。用户可在 `configs/models/{model}/ckpt_convert/` 目录下找到具体脚本。

以下是将 **DeepSeek V3.1** 模型权重从 **HuggingFace FP8** 格式转换为 **MegatronCore FP8** 格式的示例脚本。在转换 FP8 格式权重时，必须设置 `amax_epsilon` 参数。该参数需要与训练时设置的 FP8 EPS 环境变量（`export FP8_QUANT_FWD_INP_AMAX_EPS`、`export FP8_QUANT_FWD_WEIGHT_AMAX_EPS`、`export FP8_QUANT_BWD_GRAD_AMAX_EPS`）保持一致。

如果用户使用的是 **Nvidia B 系列 GPU**，则必须在转换脚本中添加 `--quant_method pt` 参数。

```bash
#! /bin/bash

export LOONGFORGE_PATH=${LOONGFORGE_PATH:-"/workspace/LoongForge"}
MEGATRON_PATH=${MEGATRON_PATH:-"/workspace/Loong-Megatron"}
CONVERT_CHECKPOINT_PATH="$LOONGFORGE_PATH/tools/mcore_checkpoint_convert"

LOAD=/path/to/hf_checkpoint  # 原始 DeepSeek-V3 权重为 FP8 格式
SAVE=/path/to/your/save  # 转换后的权重将为 MCore FP8 格式

MODEL_CONFIG_FILE=${LOONGFORGE_PATH}/configs/models/deepseek3/deepseek_v3.yaml
CONVERT_FILE=${LOONGFORGE_PATH}/configs/models/deepseek3/ckpt_convert/deepseek_v3_convert.yaml

PYTHONPATH=$MEGATRON_PATH:$PYTHONPATH \
    python $CONVERT_CHECKPOINT_PATH/module_convertor/model.py \
    --load_platform=huggingface \
    --save_platform=mcore \
    --config_file $MODEL_CONFIG_FILE \
    --convert_file $CONVERT_FILE \
    --tensor_model_parallel_size=8 \
    --pipeline_model_parallel_size=8 \
    --expert_parallel_size=32 \
    --expert_tensor_parallel_size=1 \
    --megatron_path=$MEGATRON_PATH \
    --load_ckpt_path=$LOAD \
    --save_ckpt_path=$SAVE \
    --custom_pipeline_layers 8,7,8,8,8,8,8,6 \
    --safetensors \
    --max_workers=32 \
    --moe-grouped-gemm \
    --amax_epsilon=1e-12 \
    # --quant_method pt
```

以下是将 **DeepSeek V3.1** 模型权重从 **MegatronCore FP8** 格式转换为 **HuggingFace FP8** 格式的示例脚本：

> **注意**：当从 BF16/FP32 源格式转换为 FP8 目标格式时，必须使用 `--fp8_force_no_requant` 以避免反量化 + 重新量化。在 Nvidia B 系列 GPU 上，还必须添加 `--quant_method pt`。

```bash
#! /bin/bash

export LOONGFORGE_PATH=${LOONGFORGE_PATH:-"/workspace/LoongForge"}
MEGATRON_PATH=${MEGATRON_PATH:-"/workspace/Loong-Megatron"}
CONVERT_CHECKPOINT_PATH="$LOONGFORGE_PATH/tools/mcore_checkpoint_convert"

LOAD=/path/to/mcore_checkpoint  # MCore FP8 格式的权重
SAVE=/path/to/your/save  # 转换后的 HuggingFace FP8 格式权重

MODEL_CONFIG_FILE=${LOONGFORGE_PATH}/configs/models/deepseek3/deepseek_v3.yaml
CONVERT_FILE=${LOONGFORGE_PATH}/configs/models/deepseek3/ckpt_convert/deepseek_v3_convert.yaml

PYTHONPATH=$MEGATRON_PATH:$PYTHONPATH \
    python $CONVERT_CHECKPOINT_PATH/module_convertor/model.py \
    --load_platform=mcore \
    --save_platform=huggingface \
    --config_file $MODEL_CONFIG_FILE \
    --convert_file $CONVERT_FILE \
    --tensor_model_parallel_size=8 \
    --pipeline_model_parallel_size=8 \
    --expert_parallel_size=32 \
    --expert_tensor_parallel_size=1 \
    --megatron_path=$MEGATRON_PATH \
    --load_ckpt_path=$LOAD \
    --save_ckpt_path=$SAVE \
    --custom_pipeline_layers 8,7,8,8,8,8,8,6 \
    --safetensors \
    --max_workers=32 \
    --moe-grouped-gemm \
    --fp8_force_no_requant \
    --amax_epsilon=1e-12 \
    # --quant_method pt
```
