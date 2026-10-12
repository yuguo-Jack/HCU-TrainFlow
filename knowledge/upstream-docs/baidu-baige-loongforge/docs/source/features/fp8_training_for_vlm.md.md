---
id: doc-baidu-baige-loongforge-e02e50cad1b31706f838
title: baidu-baige/LoongForge / docs/source/features/fp8_training_for_vlm.md
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
path: docs/source/features/fp8_training_for_vlm.md
raw_sha256: 2d80fa3764a8a637706268d061608a98e7c68a44343b56dac8fe8b19294ec08e
sources: []
generated_body_sha256: a6a940a0fb4a2719fea19b3dc998a2e37305f93937de3d0d3d04268ee6d286d5
source_state: current-scan
---

# baidu-baige/LoongForge / docs/source/features/fp8_training_for_vlm.md

[Original at fixed commit](https://github.com/baidu-baige/LoongForge/blob/733126ddccaf49c4bfd780d384f00878c1f0a9a8/docs/source/features/fp8_training_for_vlm.md)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

# FP8 Training for VLM  
LoongForge provides FP8 low-precision training for various models. By editing the corresponding YAML config files you can turn FP8 on/off independently for the vision/audio **Encoder** and the language **Foundation** model, achieving the best training efficiency.

---

## 1. Supported Models  
Verified VLM models that support FP8:

| Model               | FP8 Support |
|---------------------|-------------|
| LLaVA-OneVision-1.5 | ✅           |
| Qwen2.5-VL          | –           |
| Qwen3-VL            | ✅           |
| InternVL 3.5        | –           |

---

## 2. How to Run FP8 Training  
Below we use **Qwen3-VL 30 B** as an example.

### 2.1 Turn on FP8 globally  
Add FP8-related launcher flags in  
`examples/qwen3_vl/pretrain/pretrain_qwen3_vl_30b_a3b.sh`:

```bash
TRAINING_ARGS=(
    --training-phase pretrain        # pretrain | sft
    --seq-length 32768
    --max-position-embeddings 32768
    --init-method-std 0.02
    --micro-batch-size 1
    --global-batch-size 32
    --lr 0.0002
    --min-lr 1.0e-5
    --clip-grad 1.0
    --weight-decay 0.01
    --optimizer adam
    --adam-beta1 0.9
    --adam-beta2 0.95
    --adam-eps 1e-05
    --norm-epsilon 1e-6
    --train-iters 50000
    --lr-decay-iters 50000
    --lr-decay-style cosine
    --lr-warmup-fraction 0.002
    --initial-loss-scale 65536
    --bf16
    #--load $CHECKPOINT_PATH
    #--save $CHECKPOINT_PATH
    --save-interval 10000000
    --ckpt-format torch
    --dataloader-save ${CHECKPOINT_PATH}/dataloader
    # <-- FP8 block-wise GEMM & weights -->
    --fp8-format e4m3
    --fp8-recipe blockwise
    --fp8-param-gather
)
```

With these flags the **entire** Qwen3-VL model will be trained in FP8.

---

### 2.2 Enable FP8 selectively  
If you prefer to enable FP8 only for the **Encoder** and/or **Foundation** model, edit the YAML config:

`configs/models/qwen3_vl/qwen3_vl_30b_a3b.yaml`

```yaml
# hydra:
#   searchpath:
#     - file://configs/

defaults:
  - ../../models/image_encoder@model.image_encoder: qwen3_vit
  - ../../models/image_projector@model.image_projector: qwen_mlp_adapter
  - ../../models/qwen3@model.foundation: qwen3_30b_a3b
  - _self_

model:
  model_type: qwen3_vl
  position_idx_func: ${position_func:rope_ids_qwen3vl}
  loss_func: ${loss_func:default}
  foundation:
    rotary_emb_func: "Qwen3VLRotaryEmbedding"
    mrope_section: [24, 20, 20]
    rotary_base: 1000000
    model_spec: ["loongforge.models.foundation.qwen3.qwen_layer_spec",
                 "get_qwen3_vl_layer_with_te_spec"]
    # <-- FP8 block-wise GEMM & weights -->
    fp8: "e4m3"
    fp8_recipe: "blockwise"
    fp8_param: True
  image_encoder:
    model_spec: ["loongforge.models.encoder.qwen3_vl_vision_models.qwen3_vl_layer_spec",
                 "get_qwen3_vl_vision_model_layer_with_te_spec"]
    # <-- FP8 block-wise GEMM & weights -->
    fp8: "e4m3"
    fp8_recipe: "blockwise"
    fp8_param: True
  image_projector:
    activation_func: ${act:gelu}
    normalization: "LayerNorm"
```

With the above snippet only the **Foundation** and **image_encoder** modules will run in FP8; other parts (e.g. projector, loss, etc.) remain in their original precision.
