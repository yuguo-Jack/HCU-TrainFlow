---
id: doc-sgl-project-sglang-f735675a325797e54b9d
title: sgl-project/sglang / docs/docs/references/custom_chat_template.mdx
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
path: docs/docs/references/custom_chat_template.mdx
raw_sha256: 232c92e6325a78977496a24e5656b401ee4a7943f07867ff68f022256497a1cd
sources: []
generated_body_sha256: aafcee583f687fb770ad48585ecc2833daaa933213fff82f50af1c656a52b80c
source_state: current-scan
---

# sgl-project/sglang / docs/docs/references/custom_chat_template.mdx

[Original at fixed commit](https://github.com/sgl-project/sglang/blob/bd2d73daa5afda6bcad8d479a834f2e70bbe9569/docs/docs/references/custom_chat_template.mdx)

Upstream source document; original commands, claims and links require their stated platform/version. This is not an authored HCU recipe. Relative links should be resolved from the original file.

---

---
title: "Custom Chat Template"
metatags:
    description: "SGLang custom chat templates: JSON and Jinja formats for OpenAI-compatible API server. Override tokenizer defaults."
---
**NOTE**: There are two chat template systems in SGLang project. This document is about setting a custom chat template for the OpenAI-compatible API server (defined at [conversation.py](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/parser/conversation.py)). It is NOT related to the chat template used in the SGLang language frontend (defined at [chat_template.py](https://github.com/sgl-project/sglang/blob/main/python/sglang/lang/chat_template.py)).

By default, the server uses the chat template specified in the model tokenizer from Hugging Face.
It should just work for most official models such as Llama-2/Llama-3.

If needed, you can also override the chat template when launching the server:

```bash Command
python -m sglang.launch_server \
  --model-path meta-llama/Llama-2-7b-chat-hf \
  --port 30000 \
  --chat-template llama-2
```

If the chat template you are looking for is missing, you are welcome to contribute it or load it from a file.

## JSON Format

You can load the JSON format, which is defined by `conversation.py`.

```json Config
{
  "name": "my_model",
  "system": "<|im_start|>system",
  "user": "<|im_start|>user",
  "assistant": "<|im_start|>assistant",
  "sep_style": "CHATML",
  "sep": "<|im_end|>",
  "stop_str": ["<|im_end|>", "<|im_start|>"]
}
```

```bash Command
python -m sglang.launch_server \
  --model-path meta-llama/Llama-2-7b-chat-hf \
  --port 30000 \
  --chat-template ./my_model_template.json
```

## Jinja Format

You can also use the [Jinja template format](https://huggingface.co/docs/transformers/main/en/chat_templating) as defined by Hugging Face Transformers.

```bash Command
python -m sglang.launch_server \
  --model-path meta-llama/Llama-2-7b-chat-hf \
  --port 30000 \
  --chat-template ./my_model_template.jinja
```