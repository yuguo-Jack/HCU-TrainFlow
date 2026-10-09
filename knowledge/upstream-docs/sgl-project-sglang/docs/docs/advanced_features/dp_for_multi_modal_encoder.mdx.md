---
id: doc-sgl-project-sglang-f47402ec22cfefce835a
title: sgl-project/sglang / docs/docs/advanced_features/dp_for_multi_modal_encoder.mdx
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
path: docs/docs/advanced_features/dp_for_multi_modal_encoder.mdx
raw_sha256: b8b16b6cebc272164bfb3401a1f91605534fdf33e758ba8edd35d03248a82191
sources: []
generated_body_sha256: b897061eeaf50a967a30c4495d744316836c18eb26c4645efe3150e7354ee3a6
source_state: current-scan
---

# sgl-project/sglang / docs/docs/advanced_features/dp_for_multi_modal_encoder.mdx

[Original at fixed commit](https://github.com/sgl-project/sglang/blob/bd2d73daa5afda6bcad8d479a834f2e70bbe9569/docs/docs/advanced_features/dp_for_multi_modal_encoder.mdx)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
title: "DP for Multi-Modal Encoder in SGLang"
metatags:
    description: "Data parallelism for VLM vision encoder in SGLang: reduce TTFT, boost throughput. Supports Qwen2.5-VL, Qwen3-VL, InternVL, GLM-4.5V/4.6V."
---
A typical VLM architecture involves two main components: an multi-modal encoder and a text decoder.

Most VLMs utilize a Vision Transformer (ViT) as their multi-modal encoder, it is responsible for processing visual data, extracting features (objects, colors, textures, etc.), and transforming them into a format that can be understood by the model.

The text deocoder is based on LLM. It processes textual data and generates output based on the encoded visual features.

However, since the size of ViT is very small compared to language decoders,
there is relatively little gain from TP. On the other hand, TP incurs significant communication
overhead because of all-reduce being performed after every layer.

Placing the ViT in data parallel while keeping the LLM in tensor parallel consistently lowers TTFT and boosts end-to-end throughput. In this hybrid layout, the vision front-end becomes parallel and lightweight, while scarce interconnect bandwidth and collective ops are reserved for the LLM.

Data parallelism replicates the entire model across multiple GPU sets and processes different batches of requests in parallel.

## Command Example
You can enable batch-level DP by setting `mm-enable-dp-encoder`, for example:
```shell Command
python3 -m sglang.launch_server \
    --model-path Qwen/Qwen2.5-VL-7B-Instruct \
    --tp 2 \
    --mm-enable-dp-encoder
```

## Known supported models
- Qwen2.5-VL (&lt;https://github.com/sgl-project/sglang/pull/13126&gt;)
- Qwen3-VL (&lt;https://github.com/sgl-project/sglang/pull/13724&gt;)
- InternVL (&lt;https://github.com/sgl-project/sglang/pull/13925&gt;)
- GLM-4.5V & GLM-4.6V (&lt;https://github.com/sgl-project/sglang/pull/14097&gt;)